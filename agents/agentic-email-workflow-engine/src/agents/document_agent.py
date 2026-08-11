"""
DocumentAgent: Translates a subtask into a document_store_tool search and interprets results.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from src.llm_client import LLMClient, get_llm_client
from src.tools.registry import ToolRegistry


class DocumentSearchPlan(BaseModel):
    query: str = Field(..., description="Keyword(s) to search the knowledge base for")
    category: Optional[str] = Field(default=None, description="One of: account, billing, pricing, developer, or omit")


SYSTEM_PROMPT = """You translate a subtask description into a knowledge-base search query.
Given a subtask like "find help article about password reset", produce a short keyword query
and an optional category filter (account, billing, pricing, developer)."""


class DocumentAgent:
    name = "document_agent"
    capability_tags = ["document_search", "document_retrieval", "knowledge_base"]
    capability_description = (
        "Searches the internal knowledge base / help center for relevant articles. "
        "Use for subtasks that need documentation, policy info, or troubleshooting guides."
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
            response_schema=DocumentSearchPlan,
            system=SYSTEM_PROMPT,
        )
        plan = plan_result.output

        doc_tool = self.tools.get("document_store")
        tool_result = await doc_tool.call({
            "operation": "search",
            "query": plan.query,
            "category": plan.category,
        })

        return {
            "status": "success" if tool_result.get("success") else "failed",
            "data": tool_result.get("data"),
            "count": tool_result.get("count", 0),
            "_latency_ms": plan_result.latency_ms,
            "_cost_usd": plan_result.cost_usd,
        }
