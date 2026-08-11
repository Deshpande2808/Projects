"""
Tool Protocol: Contract for all tool implementations.

A Tool is any resource that an agent can use to perform work:
- Database queries
- File storage access
- API calls
- Vector stores
- etc.

All tools must implement this protocol.
"""

from typing import Protocol, Any, Dict, List, runtime_checkable


@runtime_checkable
class Tool(Protocol):
    """
    Protocol that all tools must implement.

    A tool is a reusable component that agents call to accomplish tasks.
    Tools are discovered and routed to agents dynamically based on capability tags.
    """

    name: str
    """Unique identifier for this tool (e.g., "database", "vector_store", "email_sender")"""

    capability_tags: List[str]
    """List of tags describing what this tool can do (e.g., ["database_query", "customer_lookup"])"""

    async def call(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with the given input.

        Args:
            input_data: Dictionary containing tool-specific parameters.
                       Structure depends on the tool type.

        Returns:
            Dictionary with the tool's output. Structure depends on the tool type.

        Raises:
            ToolError: If the tool execution fails.

        Example:
            >>> db_tool = DatabaseTool()
            >>> result = await db_tool.call({
            ...     "query": "SELECT * FROM customers WHERE id = ?",
            ...     "params": [123]
            ... })
            >>> print(result)
            {"customer_id": 123, "name": "John Doe", "status": "active"}
        """
        ...


class ToolError(Exception):
    """Raised when a tool execution fails."""
    pass


class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not registered."""
    pass
