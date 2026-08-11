"""
LangGraph Orchestrator: The workflow engine that coordinates agents.

A StateGraph that:
1. Defines nodes (agents, handlers)
2. Defines edges (connections, routing logic)
3. Manages state transitions
4. Handles checkpointing (persistence)
5. Supports human interrupts (approval gates)

One graph per workflow. Each workflow is one email flowing through the pipeline.
"""

from typing import Callable, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from src.orchestrator.state import WorkflowState, WorkflowStatus
import logging

logger = logging.getLogger(__name__)

# Maps graph node names to WorkflowStatus — not a 1:1 string match
# (e.g. node "decomposition" -> status DECOMPOSED), so it's an explicit table.
_NODE_TO_STATUS = {
    "understanding": WorkflowStatus.UNDERSTANDING,
    "decomposition": WorkflowStatus.DECOMPOSED,
    "routing": WorkflowStatus.ROUTING,
    "aggregation": WorkflowStatus.AGGREGATING,
    "draft_generation": WorkflowStatus.GENERATING_DRAFT,
    "approval_gate": WorkflowStatus.AWAITING_APPROVAL,
    "execution_actions": WorkflowStatus.EXECUTING_SUBTASKS,
}


class EmailWorkflowGraph:
    """
    Orchestrates an email workflow using LangGraph.

    Nodes:
    - understanding: Parse email intent/entities
    - decomposition: Break into subtasks
    - routing: Find agents for each subtask
    - execution: Run agents in parallel
    - aggregation: Synthesize results
    - draft_generation: Generate response
    - approval_gate: PAUSE for human approval
    - execution_actions: Execute approved actions
    - end: Workflow complete

    Edges define the flow between nodes.
    """

    def __init__(
        self,
        understanding_node: Callable,
        decomposition_node: Callable,
        router_node: Callable,
        aggregation_node: Callable,
        draft_node: Callable,
        approval_gate_node: Callable,
        execution_node: Callable,
    ):
        """
        Initialize the graph with node handlers.

        Args:
            understanding_node: async def (state) -> state
            decomposition_node: async def (state) -> state
            router_node: async def (state) -> state (routes to agents)
            aggregation_node: async def (state) -> state
            draft_node: async def (state) -> state
            approval_gate_node: async def (state) -> state (pauses for approval)
            execution_node: async def (state) -> state (executes actions)
        """
        self.understanding_node = understanding_node
        self.decomposition_node = decomposition_node
        self.router_node = router_node
        self.aggregation_node = aggregation_node
        self.draft_node = draft_node
        self.approval_gate_node = approval_gate_node
        self.execution_node = execution_node

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph StateGraph."""
        graph = StateGraph(WorkflowState)

        # Add nodes
        graph.add_node("understanding", self._wrap_node("understanding", self.understanding_node))
        graph.add_node("decomposition", self._wrap_node("decomposition", self.decomposition_node))
        graph.add_node("routing", self._wrap_node("routing", self.router_node))
        graph.add_node("aggregation", self._wrap_node("aggregation", self.aggregation_node))
        graph.add_node("draft_generation", self._wrap_node("draft_generation", self.draft_node))
        graph.add_node("approval_gate", self._wrap_node("approval_gate", self.approval_gate_node))
        graph.add_node("execution_actions", self._wrap_node("execution_actions", self.execution_node))

        # Add edges (workflow flow)
        graph.add_edge("__start__", "understanding")
        graph.add_edge("understanding", "decomposition")
        graph.add_edge("decomposition", "routing")
        graph.add_edge("routing", "aggregation")
        graph.add_edge("aggregation", "draft_generation")
        graph.add_edge("draft_generation", "approval_gate")

        # Conditional edge from approval_gate
        graph.add_conditional_edges(
            "approval_gate",
            self._approval_router,
            {
                "approved": "execution_actions",
                "rejected": END,
            }
        )

        graph.add_edge("execution_actions", END)

        return graph

    def _wrap_node(self, node_name: str, node_fn: Callable) -> Callable:
        """
        Wrap a node function to add logging and error handling.

        Args:
            node_name: Name of the node
            node_fn: The actual node function

        Returns:
            Wrapped function that handles logging and state updates
        """
        async def wrapped(state: WorkflowState) -> WorkflowState:
            try:
                logger.info(f"→ Entering node: {node_name}")

                # Update status
                if node_name in _NODE_TO_STATUS:
                    state.status = _NODE_TO_STATUS[node_name]

                # Call the actual node
                result_state = await node_fn(state)

                logger.info(f"✓ Completed node: {node_name}")
                return result_state

            except Exception as e:
                logger.error(f"✗ Error in node {node_name}: {str(e)}")
                state.status = WorkflowStatus.FAILED
                state.error_message = f"Error in {node_name}: {str(e)}"
                raise

        return wrapped

    def _approval_router(self, state: WorkflowState) -> str:
        """
        Route based on approval status.

        Returns:
            "approved" if draft was approved, "rejected" otherwise
        """
        if state.approval_status == "approved":
            return "approved"
        else:
            return "rejected"

    def compile(self):
        """
        Compile the graph into a runnable workflow.

        Returns:
            Compiled graph ready to execute
        """
        return self.graph.compile()


# ============================================================================
# MINIMAL NODE IMPLEMENTATIONS (Placeholders for Phase 2+)
# ============================================================================

async def placeholder_understanding_node(state: WorkflowState) -> WorkflowState:
    """Placeholder: Will be replaced by actual UnderstandingAgent."""
    logger.info("Understanding node executing...")
    state.understanding = {
        "intent": "unknown",
        "entities": [],
        "urgency": "normal",
    }
    return state


async def placeholder_decomposition_node(state: WorkflowState) -> WorkflowState:
    """Placeholder: Will be replaced by actual DecompositionAgent."""
    logger.info("Decomposition node executing...")
    state.subtasks = [
        {"id": "subtask-1", "description": "Lookup customer", "required_capabilities": ["database_query"]},
    ]
    return state


async def placeholder_router_node(state: WorkflowState) -> WorkflowState:
    """Placeholder: Will be replaced by actual routing logic."""
    logger.info("Router node executing...")
    # Would normally call agents here
    state.agent_results = {
        "database_agent": {"status": "success", "data": {}},
    }
    return state


async def placeholder_aggregation_node(state: WorkflowState) -> WorkflowState:
    """Placeholder: Will be replaced by actual AggregationAgent."""
    logger.info("Aggregation node executing...")
    state.aggregated_findings = {
        "summary": "Customer found",
        "key_facts": [],
    }
    return state


async def placeholder_draft_node(state: WorkflowState) -> WorkflowState:
    """Placeholder: Will be replaced by actual DraftAgent."""
    logger.info("Draft node executing...")
    state.draft = {
        "email_body": "Thank you for reaching out...",
        "actions": [],
        "confidence": 0.9,
    }
    return state


async def placeholder_approval_gate_node(state: WorkflowState) -> WorkflowState:
    """
    Approval gate: Pauses workflow here.

    In Phase 5, this will be an interrupt that:
    1. Pauses the graph
    2. Returns to API
    3. API shows user the draft
    4. User approves/rejects
    5. API resumes graph with approval_status set
    """
    logger.info("Approval gate: Workflow paused for human review")
    # In real implementation, this would interrupt and return to user
    # For now, auto-approve for testing
    state.approval_status = "approved"
    state.approved_by = "system_test"
    return state


async def placeholder_execution_node(state: WorkflowState) -> WorkflowState:
    """Placeholder: Will be replaced by actual execution handler."""
    logger.info("Execution node executing...")
    state.execution_results = {
        "send_email": {"status": "success", "email_id": "mock-email-123"},
    }
    state.status = WorkflowStatus.COMPLETED
    return state


def create_workflow_graph() -> StateGraph:
    """
    Factory function to create a workflow graph using placeholder nodes.

    Useful for testing orchestration mechanics (state flow, checkpointing,
    approval routing) without incurring LLM cost. For the real pipeline,
    use create_workflow_graph_with_agents().

    Returns:
        Compiled LangGraph StateGraph ready to execute
    """
    orchestrator = EmailWorkflowGraph(
        understanding_node=placeholder_understanding_node,
        decomposition_node=placeholder_decomposition_node,
        router_node=placeholder_router_node,
        aggregation_node=placeholder_aggregation_node,
        draft_node=placeholder_draft_node,
        approval_gate_node=placeholder_approval_gate_node,
        execution_node=placeholder_execution_node,
    )

    return orchestrator.compile()


# ============================================================================
# REAL NODE IMPLEMENTATIONS (Phase 2 — backed by actual agents)
# ============================================================================
#
# Routing here is intentionally simple (not the Phase 3 tag/semantic router):
# for each subtask, run every worker agent whose capability_tags overlap
# the subtask's required_capabilities. Phase 3 replaces this with
# src/routing/tag_router.py + semantic_router.py without touching these
# node functions' call sites in the graph.

def _make_understanding_node(agent) -> Callable:
    async def node(state: WorkflowState) -> WorkflowState:
        input_data = {"email_subject": state.email_subject, "email_body": state.email_body}
        output = await agent.run(input_data)
        state.understanding = {k: v for k, v in output.items() if not k.startswith("_")}
        state.add_node_log(
            "understanding", input_data, output,
            latency_ms=output.get("_latency_ms", 0), cost_usd=output.get("_cost_usd", 0),
        )
        return state
    return node


def _make_decomposition_node(agent) -> Callable:
    async def node(state: WorkflowState) -> WorkflowState:
        input_data = {"understanding": state.understanding}
        output = await agent.run(input_data)
        state.subtasks = output["subtasks"]
        state.add_node_log(
            "decomposition", input_data, output,
            latency_ms=output.get("_latency_ms", 0), cost_usd=output.get("_cost_usd", 0),
        )
        return state
    return node


def _make_router_node(worker_agents: list) -> Callable:
    """
    worker_agents: list of agent instances (e.g. [database_agent, document_agent]),
    each with .capability_tags. For each subtask, runs every agent whose tags
    overlap the subtask's required_capabilities.
    """
    async def node(state: WorkflowState) -> WorkflowState:
        for subtask in state.subtasks:
            required = set(subtask.get("required_capabilities", []))
            for agent in worker_agents:
                if required & set(agent.capability_tags):
                    result = await agent.run({"description": subtask["description"]})
                    state.agent_assignments[subtask["id"]] = agent.name
                    state.agent_results[agent.name] = {
                        k: v for k, v in result.items() if not k.startswith("_")
                    }
                    state.add_node_log(
                        f"routing:{agent.name}", subtask, result,
                        latency_ms=result.get("_latency_ms", 0), cost_usd=result.get("_cost_usd", 0),
                    )
        return state
    return node


def _make_aggregation_node(agent) -> Callable:
    async def node(state: WorkflowState) -> WorkflowState:
        input_data = {"understanding": state.understanding, "agent_results": state.agent_results}
        output = await agent.run(input_data)
        state.aggregated_findings = {k: v for k, v in output.items() if not k.startswith("_")}
        state.add_node_log(
            "aggregation", input_data, output,
            latency_ms=output.get("_latency_ms", 0), cost_usd=output.get("_cost_usd", 0),
        )
        return state
    return node


def _make_draft_node(agent) -> Callable:
    async def node(state: WorkflowState) -> WorkflowState:
        input_data = {
            "email_subject": state.email_subject,
            "email_body": state.email_body,
            "aggregated_findings": state.aggregated_findings,
        }
        output = await agent.run(input_data)
        state.draft = {k: v for k, v in output.items() if not k.startswith("_")}
        state.add_node_log(
            "draft_generation", input_data, output,
            latency_ms=output.get("_latency_ms", 0), cost_usd=output.get("_cost_usd", 0),
        )
        return state
    return node


def create_workflow_graph_with_agents(tool_registry, llm_client=None) -> StateGraph:
    """
    Factory function to create the real workflow graph, backed by actual agents.

    Args:
        tool_registry: ToolRegistry with tools registered (e.g. from create_tool_registry())
        llm_client: Optional shared LLMClient; defaults to get_llm_client() per agent

    Returns:
        Compiled LangGraph StateGraph ready to execute against a real email
    """
    from src.agents import (
        UnderstandingAgent,
        DecompositionAgent,
        DatabaseAgent,
        DocumentAgent,
        AggregationAgent,
        DraftAgent,
    )

    understanding_agent = UnderstandingAgent(llm_client)
    decomposition_agent = DecompositionAgent(llm_client)
    database_agent = DatabaseAgent(tool_registry, llm_client)
    document_agent = DocumentAgent(tool_registry, llm_client)
    aggregation_agent = AggregationAgent(llm_client)
    draft_agent = DraftAgent(llm_client)

    orchestrator = EmailWorkflowGraph(
        understanding_node=_make_understanding_node(understanding_agent),
        decomposition_node=_make_decomposition_node(decomposition_agent),
        router_node=_make_router_node([database_agent, document_agent]),
        aggregation_node=_make_aggregation_node(aggregation_agent),
        draft_node=_make_draft_node(draft_agent),
        approval_gate_node=placeholder_approval_gate_node,  # real approval gate arrives in Phase 5
        execution_node=placeholder_execution_node,  # real execution arrives in Phase 5
    )

    return orchestrator.compile()
