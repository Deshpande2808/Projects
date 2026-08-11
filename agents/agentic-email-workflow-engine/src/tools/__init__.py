"""
Tools module: All tool implementations and registry.

Tools are reusable components that agents call to accomplish tasks.
Each tool implements the Tool protocol and is registered in the ToolRegistry.
"""

from src.tools.base import Tool, ToolError, ToolNotFoundError
from src.tools.registry import ToolRegistry
from src.tools.mock_database_tool import MockDatabaseTool
from src.tools.mock_document_store_tool import MockDocumentStoreTool
from src.tools.mock_crm_tool import MockCRMTool
from src.tools.mock_email_sender_tool import MockEmailSenderTool

__all__ = [
    "Tool",
    "ToolError",
    "ToolNotFoundError",
    "ToolRegistry",
    "MockDatabaseTool",
    "MockDocumentStoreTool",
    "MockCRMTool",
    "MockEmailSenderTool",
]


def create_tool_registry() -> ToolRegistry:
    """
    Factory function to create a ToolRegistry with all mocked tools registered.

    Used for testing and Phase 1 development. In production (Phase 7+),
    this would register real tool implementations instead.

    Returns:
        ToolRegistry with all tools registered and ready to use.

    Example:
        >>> registry = create_tool_registry()
        >>> db_tool = registry.get("database")
        >>> result = await db_tool.call({"operation": "lookup", ...})
    """
    registry = ToolRegistry()

    # Register mocked tools
    registry.register(MockDatabaseTool())
    registry.register(MockDocumentStoreTool())
    registry.register(MockCRMTool())
    registry.register(MockEmailSenderTool())

    return registry
