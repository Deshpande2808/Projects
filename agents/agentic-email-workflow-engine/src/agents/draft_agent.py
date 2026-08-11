"""
DraftAgent: Generates the final email reply + proposed actions, ready for human approval.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.llm_client import LLMClient, get_llm_client


class ProposedAction(BaseModel):
    action: str = Field(..., description="e.g. 'send_email', 'update_crm'")
    details: Dict[str, Any] = Field(default_factory=dict)


class DraftOutput(BaseModel):
    email_subject: str
    email_body: str = Field(..., description="The full reply text, ready to send")
    actions: List[ProposedAction] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., description="Brief note on why this response was chosen")


SYSTEM_PROMPT = """You are a customer response drafting agent. Given the original email and
the aggregated findings from research agents, write a professional, warm, and accurate reply.
Also propose any follow-up actions needed (e.g. update_crm, escalate). This draft will be
shown to a human for approval before anything is sent — write it as if it will be sent as-is,
but don't fabricate facts not present in the findings."""


class DraftAgent:
    name = "draft_agent"
    capability_tags = ["response_drafting"]
    capability_description = (
        "Generates the final customer-facing email reply and a list of proposed follow-up "
        "actions, based on aggregated findings. Output is reviewed by a human before execution."
    )

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or get_llm_client()

    async def run(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        original_subject = input_data.get("email_subject", "")
        original_body = input_data.get("email_body", "")
        aggregated_findings = input_data.get("aggregated_findings", {})

        prompt = (
            f"Original email subject: {original_subject}\n"
            f"Original email body: {original_body}\n\n"
            f"Findings summary: {aggregated_findings.get('summary')}\n"
            f"Key facts: {aggregated_findings.get('key_facts')}\n"
            f"Recommendations: {aggregated_findings.get('recommendations')}\n\n"
            f"Draft a reply and propose any follow-up actions."
        )

        result = await self.llm.call(
            prompt=prompt,
            response_schema=DraftOutput,
            system=SYSTEM_PROMPT,
        )

        output = result.output
        return {
            "email_subject": output.email_subject,
            "email_body": output.email_body,
            "actions": [a.model_dump() for a in output.actions],
            "confidence": output.confidence,
            "reasoning": output.reasoning,
            "_latency_ms": result.latency_ms,
            "_cost_usd": result.cost_usd,
        }
