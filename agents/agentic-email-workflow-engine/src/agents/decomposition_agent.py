"""
DecompositionAgent: Breaks understood email intent into a list of subtasks.

Each subtask declares required_capabilities, which the router (Phase 3) will
match against registered agents' capability_tags.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.llm_client import LLMClient, get_llm_client


class Subtask(BaseModel):
    id: str = Field(..., description="Short unique id, e.g. 'subtask-1'")
    description: str = Field(..., description="What needs to be done, in plain language")
    required_capabilities: List[str] = Field(
        ..., description="Capability tags needed, e.g. ['database_query', 'customer_lookup']"
    )
    depends_on: List[str] = Field(default_factory=list, description="IDs of subtasks that must complete first")


class DecompositionOutput(BaseModel):
    subtasks: List[Subtask]


SYSTEM_PROMPT = """You are a task decomposition agent. Given an understood customer email
(intent, entities, urgency), break the work needed to resolve it into concrete subtasks.

Available capability tags to choose from when setting required_capabilities:
- database_query, customer_lookup, data_retrieval  (customer/invoice data)
- document_search, document_retrieval, knowledge_base  (help articles, docs)
- crm_lookup, lead_management, customer_update  (CRM accounts/opportunities)

Keep subtasks minimal — only what's needed to gather facts for a response. Most emails need
1-3 subtasks. Use depends_on only when one subtask's output is genuinely required as input
to another."""


class DecompositionAgent:
    name = "decomposition_agent"
    capability_tags = ["task_decomposition"]
    capability_description = (
        "Breaks an understood email into a list of concrete subtasks, each tagged with "
        "the capabilities needed to complete it, so they can be routed to specialist agents."
    )

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or get_llm_client()

    async def run(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        understanding = input_data.get("understanding", {})

        prompt = (
            f"Intent: {understanding.get('intent')}\n"
            f"Entities: {understanding.get('entities')}\n"
            f"Urgency: {understanding.get('urgency')}\n"
            f"Summary: {understanding.get('summary')}\n\n"
            f"Decompose this into subtasks."
        )

        result = await self.llm.call(
            prompt=prompt,
            response_schema=DecompositionOutput,
            system=SYSTEM_PROMPT,
        )

        subtasks = [s.model_dump() for s in result.output.subtasks]
        return {
            "subtasks": subtasks,
            "_latency_ms": result.latency_ms,
            "_cost_usd": result.cost_usd,
        }
