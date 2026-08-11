"""
Tests for Tool and Agent protocols, registries.

Verifies:
1. Protocol implementations work correctly
2. Registries can register/retrieve/filter tools and agents
3. Error handling for missing/duplicate registrations
"""

import pytest
from typing import Any, Dict, List
from src.tools.base import Tool, ToolNotFoundError
from src.tools.registry import ToolRegistry
from src.agents.base import Agent, AgentNotFoundError
from src.routing.agent_registry import AgentRegistry


# ============================================================================
# MOCK IMPLEMENTATIONS FOR TESTING
# ============================================================================

class MockDatabaseTool:
    """Mock tool for database queries."""

    name = "database"
    capability_tags = ["database_query", "customer_lookup"]

    async def call(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "data": []}


class MockVectorStoreTool:
    """Mock tool for vector operations."""

    name = "vector_store"
    capability_tags = ["vector_search", "embedding"]

    async def call(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"matches": [], "scores": []}


class MockUnderstandingAgent:
    """Mock agent for understanding emails."""

    name = "understanding_agent"
    capability_tags = ["email_understanding", "intent_extraction"]
    capability_description = "Parses raw emails to extract intent, entities, and urgency"

    async def run(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return {
            "intent": "test_intent",
            "urgency": "normal",
            "entities": [],
            "confidence": 0.95,
        }


class MockDatabaseAgent:
    """Mock agent for database queries."""

    name = "database_agent"
    capability_tags = ["database_query", "customer_lookup"]
    capability_description = "Executes database queries and retrieves customer information"

    async def run(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return {"customer_id": 123, "name": "Test Customer"}


# ============================================================================
# TOOL REGISTRY TESTS
# ============================================================================

class TestToolRegistry:
    """Tests for the ToolRegistry."""

    def test_register_and_get_tool(self):
        """Test registering and retrieving a tool."""
        registry = ToolRegistry()
        tool = MockDatabaseTool()
        registry.register(tool)

        retrieved_tool = registry.get("database")
        assert retrieved_tool.name == "database"

    def test_get_nonexistent_tool_raises_error(self):
        """Test that getting a nonexistent tool raises ToolNotFoundError."""
        registry = ToolRegistry()

        with pytest.raises(ToolNotFoundError):
            registry.get("nonexistent")

    def test_register_duplicate_tool_raises_error(self):
        """Test that registering a tool with duplicate name raises error."""
        registry = ToolRegistry()
        tool1 = MockDatabaseTool()
        tool2 = MockDatabaseTool()

        registry.register(tool1)
        with pytest.raises(ValueError):
            registry.register(tool2)

    def test_list_by_tag(self):
        """Test finding tools by capability tag."""
        registry = ToolRegistry()
        db_tool = MockDatabaseTool()
        vector_tool = MockVectorStoreTool()

        registry.register(db_tool)
        registry.register(vector_tool)

        # Find tools with "database_query" tag
        db_tools = registry.list_by_tag("database_query")
        assert len(db_tools) == 1
        assert db_tools[0].name == "database"

        # Find tools with "vector_search" tag
        vector_tools = registry.list_by_tag("vector_search")
        assert len(vector_tools) == 1
        assert vector_tools[0].name == "vector_store"

    def test_list_all_tools(self):
        """Test listing all registered tools."""
        registry = ToolRegistry()
        tool1 = MockDatabaseTool()
        tool2 = MockVectorStoreTool()

        registry.register(tool1)
        registry.register(tool2)

        all_tools = registry.list_all()
        assert len(all_tools) == 2
        names = {tool.name for tool in all_tools}
        assert names == {"database", "vector_store"}

    def test_unregister_tool(self):
        """Test unregistering a tool."""
        registry = ToolRegistry()
        tool = MockDatabaseTool()
        registry.register(tool)

        assert len(registry.list_all()) == 1
        registry.unregister("database")
        assert len(registry.list_all()) == 0

    def test_unregister_nonexistent_tool_raises_error(self):
        """Test that unregistering a nonexistent tool raises error."""
        registry = ToolRegistry()

        with pytest.raises(ToolNotFoundError):
            registry.unregister("nonexistent")

    def test_clear_registry(self):
        """Test clearing all tools from registry."""
        registry = ToolRegistry()
        registry.register(MockDatabaseTool())
        registry.register(MockVectorStoreTool())

        assert len(registry.list_all()) == 2
        registry.clear()
        assert len(registry.list_all()) == 0


# ============================================================================
# AGENT REGISTRY TESTS
# ============================================================================

class TestAgentRegistry:
    """Tests for the AgentRegistry."""

    def test_register_and_get_agent(self):
        """Test registering and retrieving an agent."""
        registry = AgentRegistry()
        agent = MockUnderstandingAgent()
        registry.register(agent)

        retrieved_agent = registry.get("understanding_agent")
        assert retrieved_agent.name == "understanding_agent"

    def test_get_nonexistent_agent_raises_error(self):
        """Test that getting a nonexistent agent raises AgentNotFoundError."""
        registry = AgentRegistry()

        with pytest.raises(AgentNotFoundError):
            registry.get("nonexistent")

    def test_register_duplicate_agent_raises_error(self):
        """Test that registering an agent with duplicate name raises error."""
        registry = AgentRegistry()
        agent1 = MockUnderstandingAgent()
        agent2 = MockUnderstandingAgent()

        registry.register(agent1)
        with pytest.raises(ValueError):
            registry.register(agent2)

    def test_list_by_tag(self):
        """Test finding agents by capability tag."""
        registry = AgentRegistry()
        understanding_agent = MockUnderstandingAgent()
        database_agent = MockDatabaseAgent()

        registry.register(understanding_agent)
        registry.register(database_agent)

        # Find agents with "email_understanding" tag
        agents = registry.list_by_tag("email_understanding")
        assert len(agents) == 1
        assert agents[0].name == "understanding_agent"

        # Find agents with "database_query" tag
        db_agents = registry.list_by_tag("database_query")
        assert len(db_agents) == 1
        assert db_agents[0].name == "database_agent"

    def test_list_all_agents(self):
        """Test listing all registered agents."""
        registry = AgentRegistry()
        agent1 = MockUnderstandingAgent()
        agent2 = MockDatabaseAgent()

        registry.register(agent1)
        registry.register(agent2)

        all_agents = registry.list_all()
        assert len(all_agents) == 2
        names = {agent.name for agent in all_agents}
        assert names == {"understanding_agent", "database_agent"}

    def test_get_agent_descriptions(self):
        """Test getting all agent descriptions for semantic routing."""
        registry = AgentRegistry()
        understanding_agent = MockUnderstandingAgent()
        database_agent = MockDatabaseAgent()

        registry.register(understanding_agent)
        registry.register(database_agent)

        descriptions = registry.get_agent_descriptions()
        assert len(descriptions) == 2
        assert "understanding_agent" in descriptions
        assert "database_agent" in descriptions
        assert "Parses raw emails" in descriptions["understanding_agent"]

    def test_unregister_agent(self):
        """Test unregistering an agent."""
        registry = AgentRegistry()
        agent = MockUnderstandingAgent()
        registry.register(agent)

        assert len(registry.list_all()) == 1
        registry.unregister("understanding_agent")
        assert len(registry.list_all()) == 0

    def test_unregister_nonexistent_agent_raises_error(self):
        """Test that unregistering a nonexistent agent raises error."""
        registry = AgentRegistry()

        with pytest.raises(AgentNotFoundError):
            registry.unregister("nonexistent")

    def test_clear_registry(self):
        """Test clearing all agents from registry."""
        registry = AgentRegistry()
        registry.register(MockUnderstandingAgent())
        registry.register(MockDatabaseAgent())

        assert len(registry.list_all()) == 2
        registry.clear()
        assert len(registry.list_all()) == 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestProtocolIntegration:
    """Integration tests for protocols working together."""

    @pytest.mark.asyncio
    async def test_agent_and_tool_registry_together(self):
        """Test agents and tools working together via registries."""
        tool_registry = ToolRegistry()
        agent_registry = AgentRegistry()

        # Register tools
        tool_registry.register(MockDatabaseTool())

        # Register agents
        agent_registry.register(MockDatabaseAgent())

        # Verify both are discoverable
        db_tool = tool_registry.get("database")
        db_agent = agent_registry.get("database_agent")

        assert db_tool.name == "database"
        assert db_agent.name == "database_agent"

    def test_tag_based_routing(self):
        """Test tag-based routing scenario."""
        agent_registry = AgentRegistry()
        agent_registry.register(MockUnderstandingAgent())
        agent_registry.register(MockDatabaseAgent())

        # Scenario: We need to handle "database_query"
        # Find agents that can do it
        capable_agents = agent_registry.list_by_tag("database_query")
        assert len(capable_agents) == 1
        assert capable_agents[0].name == "database_agent"
