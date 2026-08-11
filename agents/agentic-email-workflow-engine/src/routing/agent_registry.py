"""
Agent Registry: Central place where all agents register themselves.

The registry allows:
1. Agents to be discovered by name
2. Agents to be discovered by capability tag
3. Agents to have their capability descriptions embedded for semantic routing
4. New agents to be added without modifying the orchestrator
"""

from typing import Dict, List, Optional
from src.agents.base import Agent, AgentNotFoundError


class AgentRegistry:
    """
    Registry for all agents in the system.

    Agents register themselves at startup. The orchestrator queries the registry
    to find agents capable of handling specific tasks. This enables:
    - Dynamic agent discovery based on task requirements
    - Tag-based routing (fast, deterministic)
    - Semantic routing fallback (using embeddings, flexible)
    - Agents can be added/updated without code changes
    """

    def __init__(self):
        """Initialize an empty registry."""
        self._agents: Dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        """
        Register an agent in the registry.

        Args:
            agent: An object implementing the Agent protocol.

        Raises:
            ValueError: If an agent with this name is already registered.

        Example:
            >>> registry = AgentRegistry()
            >>> agent = UnderstandingAgent(tool_registry)
            >>> registry.register(agent)
        """
        if agent.name in self._agents:
            raise ValueError(
                f"Agent '{agent.name}' is already registered. "
                f"Use a different name or call unregister() first."
            )
        self._agents[agent.name] = agent

    def get(self, name: str) -> Agent:
        """
        Get an agent by name.

        Args:
            name: The name of the agent (e.g., "understanding_agent", "database_agent").

        Returns:
            The agent object.

        Raises:
            AgentNotFoundError: If no agent with this name is registered.

        Example:
            >>> registry = AgentRegistry()
            >>> registry.register(UnderstandingAgent(tool_registry))
            >>> agent = registry.get("understanding_agent")
            >>> result = await agent.run({"email_body": "..."})
        """
        if name not in self._agents:
            available = ", ".join(self._agents.keys())
            raise AgentNotFoundError(
                f"Agent '{name}' not found. Available agents: {available}"
            )
        return self._agents[name]

    def list_by_tag(self, tag: str) -> List[Agent]:
        """
        Find all agents that support a given capability tag.

        Used for fast tag-based routing.

        Args:
            tag: A capability tag (e.g., "email_understanding", "database_query").

        Returns:
            List of agents that have this tag in their capability_tags.

        Example:
            >>> registry = AgentRegistry()
            >>> registry.register(UnderstandingAgent())    # has ["email_understanding"]
            >>> registry.register(DatabaseAgent())         # has ["database_query"]
            >>> agents = registry.list_by_tag("email_understanding")
            >>> len(agents)
            1
        """
        return [
            agent
            for agent in self._agents.values()
            if tag in agent.capability_tags
        ]

    def list_all(self) -> List[Agent]:
        """
        Get all registered agents.

        Returns:
            List of all Agent objects.
        """
        return list(self._agents.values())

    def get_agent_descriptions(self) -> Dict[str, str]:
        """
        Get all agent names and their capability descriptions.

        Used for building the vector embeddings for semantic routing in Phase 3.

        Returns:
            Dictionary mapping agent names to their capability descriptions.

        Example:
            >>> registry = AgentRegistry()
            >>> registry.register(UnderstandingAgent())
            >>> descriptions = registry.get_agent_descriptions()
            >>> print(descriptions)
            {
                "understanding_agent": "Parses raw emails to extract intent, entities, and urgency",
                ...
            }
        """
        return {
            agent.name: agent.capability_description
            for agent in self._agents.values()
        }

    def unregister(self, name: str) -> None:
        """
        Unregister an agent (mainly for testing).

        Args:
            name: The name of the agent to remove.

        Raises:
            AgentNotFoundError: If no agent with this name is registered.
        """
        if name not in self._agents:
            raise AgentNotFoundError(f"Agent '{name}' not found.")
        del self._agents[name]

    def clear(self) -> None:
        """Clear all registered agents. Mainly for testing."""
        self._agents.clear()
