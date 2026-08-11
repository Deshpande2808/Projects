"""
Tests for Phase 2 agents: Understanding, Decomposition, Database, Document,
Aggregation, Draft.

Each agent is tested with a mocked LLMClient (no real API calls, no cost) so
these tests run for free and deterministically. The mock returns a fixed
response_schema instance regardless of prompt content.
"""

import pytest
from unittest.mock import AsyncMock

from src.llm_client import LLMCallResult
from src.tools import create_tool_registry
from src.agents.understanding_agent import UnderstandingAgent, UnderstandingOutput
from src.agents.decomposition_agent import DecompositionAgent, DecompositionOutput, Subtask
from src.agents.database_agent import DatabaseAgent, DatabaseQueryPlan
from src.agents.document_agent import DocumentAgent, DocumentSearchPlan
from src.agents.aggregation_agent import AggregationAgent, AggregationOutput
from src.agents.draft_agent import DraftAgent, DraftOutput, ProposedAction


def make_mock_llm(output):
    """Build a mock LLMClient whose .call() always returns `output` wrapped in LLMCallResult."""
    mock = AsyncMock()
    mock.call = AsyncMock(return_value=LLMCallResult(
        output=output, input_tokens=100, output_tokens=50,
        cost_usd=0.001, latency_ms=120, raw_text="{}",
    ))
    return mock


class TestUnderstandingAgent:
    @pytest.mark.asyncio
    async def test_run_returns_structured_understanding(self):
        mock_output = UnderstandingOutput(
            intent="account_access_issue", entities=["account", "login"],
            urgency="high", confidence=0.95, summary="Customer locked out of account",
        )
        agent = UnderstandingAgent(llm_client=make_mock_llm(mock_output))

        result = await agent.run({"email_subject": "Locked out", "email_body": "Can't log in"})

        assert result["intent"] == "account_access_issue"
        assert result["urgency"] == "high"
        assert result["confidence"] == 0.95

    def test_agent_metadata(self):
        agent = UnderstandingAgent(llm_client=make_mock_llm(None))
        assert agent.name == "understanding_agent"
        assert "email_understanding" in agent.capability_tags


class TestDecompositionAgent:
    @pytest.mark.asyncio
    async def test_run_returns_subtasks(self):
        mock_output = DecompositionOutput(subtasks=[
            Subtask(id="subtask-1", description="Lookup customer",
                    required_capabilities=["database_query"], depends_on=[]),
        ])
        agent = DecompositionAgent(llm_client=make_mock_llm(mock_output))

        result = await agent.run({"understanding": {"intent": "account_access_issue"}})

        assert len(result["subtasks"]) == 1
        assert result["subtasks"][0]["id"] == "subtask-1"
        assert "database_query" in result["subtasks"][0]["required_capabilities"]


class TestDatabaseAgent:
    @pytest.mark.asyncio
    async def test_run_looks_up_customer(self):
        mock_plan = DatabaseQueryPlan(operation="lookup", resource="customer", id=123)
        registry = create_tool_registry()
        agent = DatabaseAgent(registry, llm_client=make_mock_llm(mock_plan))

        result = await agent.run({"description": "Lookup customer 123"})

        assert result["status"] == "success"
        assert result["data"]["id"] == 123
        assert result["data"]["name"] == "Alice Johnson"

    @pytest.mark.asyncio
    async def test_run_handles_missing_customer(self):
        mock_plan = DatabaseQueryPlan(operation="lookup", resource="customer", id=999)
        registry = create_tool_registry()
        agent = DatabaseAgent(registry, llm_client=make_mock_llm(mock_plan))

        result = await agent.run({"description": "Lookup customer 999"})

        assert result["status"] == "failed"
        assert "not found" in result["error"]


class TestDocumentAgent:
    @pytest.mark.asyncio
    async def test_run_searches_knowledge_base(self):
        mock_plan = DocumentSearchPlan(query="password", category="account")
        registry = create_tool_registry()
        agent = DocumentAgent(registry, llm_client=make_mock_llm(mock_plan))

        result = await agent.run({"description": "find password reset help"})

        assert result["status"] == "success"
        assert result["count"] >= 1


class TestAggregationAgent:
    @pytest.mark.asyncio
    async def test_run_synthesizes_findings(self):
        mock_output = AggregationOutput(
            summary="Customer account was locked due to failed logins",
            key_facts=["Account locked since yesterday"],
            conflicts=[], recommendations=["Unlock account"],
        )
        agent = AggregationAgent(llm_client=make_mock_llm(mock_output))

        result = await agent.run({
            "understanding": {"summary": "Account locked"},
            "agent_results": {"database_agent": {"status": "success"}},
        })

        assert "locked" in result["summary"]
        assert len(result["recommendations"]) == 1


class TestDraftAgent:
    @pytest.mark.asyncio
    async def test_run_generates_draft(self):
        mock_output = DraftOutput(
            email_subject="Re: Account Locked",
            email_body="Your account has been unlocked.",
            actions=[ProposedAction(action="send_email", details={})],
            confidence=0.9, reasoning="Standard unlock resolution",
        )
        agent = DraftAgent(llm_client=make_mock_llm(mock_output))

        result = await agent.run({
            "email_subject": "Account Locked",
            "email_body": "I can't log in",
            "aggregated_findings": {"summary": "Account locked", "key_facts": [], "recommendations": []},
        })

        assert result["email_subject"] == "Re: Account Locked"
        assert result["confidence"] == 0.9
        assert len(result["actions"]) == 1


class TestAgentRegistryIntegration:
    def test_all_agents_have_required_protocol_fields(self):
        registry = create_tool_registry()
        agents = [
            UnderstandingAgent(llm_client=make_mock_llm(None)),
            DecompositionAgent(llm_client=make_mock_llm(None)),
            DatabaseAgent(registry, llm_client=make_mock_llm(None)),
            DocumentAgent(registry, llm_client=make_mock_llm(None)),
            AggregationAgent(llm_client=make_mock_llm(None)),
            DraftAgent(llm_client=make_mock_llm(None)),
        ]
        for agent in agents:
            assert isinstance(agent.name, str) and agent.name
            assert isinstance(agent.capability_tags, list) and agent.capability_tags
            assert isinstance(agent.capability_description, str) and agent.capability_description
