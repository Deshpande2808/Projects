"""
Tool Registry: Central place where all tools register themselves.

The registry is a simple dict-based lookup that allows:
1. Agents to discover tools by name
2. Agents to discover tools by capability tag
3. Tools to be swapped/upgraded without touching agent code
"""

from typing import Dict, List, Optional
from src.tools.base import Tool, ToolNotFoundError


class ToolRegistry:
    """
    Registry for all tools in the system.

    Tools register themselves at startup. Agents query the registry to get tools.
    This enables:
    - Agents don't hard-code tool implementations
    - Tools can be swapped (e.g., Postgres → MongoDB) without code changes
    - New tools can be added without modifying the orchestrator
    """

    def __init__(self):
        """Initialize an empty registry."""
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """
        Register a tool in the registry.

        Args:
            tool: An object implementing the Tool protocol.

        Raises:
            ValueError: If a tool with this name is already registered.

        Example:
            >>> registry = ToolRegistry()
            >>> db_tool = DatabaseTool()
            >>> registry.register(db_tool)
        """
        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered. "
                f"Use a different name or call unregister() first."
            )
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        """
        Get a tool by name.

        Args:
            name: The name of the tool (e.g., "database", "vector_store").

        Returns:
            The tool object.

        Raises:
            ToolNotFoundError: If no tool with this name is registered.

        Example:
            >>> registry = ToolRegistry()
            >>> registry.register(DatabaseTool())
            >>> db_tool = registry.get("database")
            >>> result = await db_tool.call({"query": "SELECT ..."})
        """
        if name not in self._tools:
            available = ", ".join(self._tools.keys())
            raise ToolNotFoundError(
                f"Tool '{name}' not found. Available tools: {available}"
            )
        return self._tools[name]

    def list_by_tag(self, tag: str) -> List[Tool]:
        """
        Find all tools that support a given capability tag.

        Args:
            tag: A capability tag (e.g., "database_query", "customer_lookup").

        Returns:
            List of tools that have this tag in their capability_tags.

        Example:
            >>> registry = ToolRegistry()
            >>> registry.register(DatabaseTool())    # has ["database_query"]
            >>> registry.register(VectorStoreT())    # has ["vector_search"]
            >>> tools = registry.list_by_tag("database_query")
            >>> len(tools)
            1
        """
        return [
            tool
            for tool in self._tools.values()
            if tag in tool.capability_tags
        ]

    def list_all(self) -> List[Tool]:
        """
        Get all registered tools.

        Returns:
            List of all Tool objects.
        """
        return list(self._tools.values())

    def unregister(self, name: str) -> None:
        """
        Unregister a tool (mainly for testing).

        Args:
            name: The name of the tool to remove.

        Raises:
            ToolNotFoundError: If no tool with this name is registered.
        """
        if name not in self._tools:
            raise ToolNotFoundError(f"Tool '{name}' not found.")
        del self._tools[name]

    def clear(self) -> None:
        """Clear all registered tools. Mainly for testing."""
        self._tools.clear()
