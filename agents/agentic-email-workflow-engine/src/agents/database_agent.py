"""
DatabaseAgent: Translates a subtask into a database_tool call and interprets the result.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from src.llm_client import LLMClient, get_llm_client
from src.tools.registry import ToolRegistry


class DatabaseQueryPlan(BaseModel):
    operation: str = Field(..., description="'lookup', 'list', or 'query'")
    resource: str = Field(..., description="'customer' or 'invoice'")
    id: Optional[Any] = Field(default=None, description="ID to look up, if operation is 'lookup'")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filters, if operation is 'query'")


SYSTEM_PROMPT = """You translate a subtask description into a database query plan.
Given a subtask like "lookup customer by email alice@example.com", produce operation/resource/id.
Customer IDs in this system are integers 123, 456, 789 for known test customers.
If the subtask doesn't map cleanly, use your best guess based on the entities mentioned."""


class DatabaseAgent:
    name = "database_agent"
    capability_tags = ["database_query", "customer_lookup", "data_retrieval"]
    capability_description = (
        "Queries the customer database for customer records and invoices. "
        "Use for subtasks involving looking up customer info, account status, or billing history."
    )

    def __init__(self, tool_registry: ToolRegistry, llm_client: Optional[LLMClient] = None):
        self.tools = tool_registry
        self.llm = llm_client or get_llm_client()

    async def run(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        subtask_description = input_data.get("description", "")

        plan_result = await self.llm.call(
            prompt=f"Subtask: {subtask_description}",
            response_schema=DatabaseQueryPlan,
            system=SYSTEM_PROMPT,
        )
        plan = plan_result.output

        db_tool = self.tools.get("database")
        tool_result = await db_tool.call({
            "operation": plan.operation,
            "resource": plan.resource,
            "id": plan.id,
            "filters": plan.filters,
        })

        return {
            "status": "success" if tool_result.get("success") else "failed",
            "data": tool_result.get("data"),
            "error": tool_result.get("error"),
            "_latency_ms": plan_result.latency_ms,
            "_cost_usd": plan_result.cost_usd,
        }
