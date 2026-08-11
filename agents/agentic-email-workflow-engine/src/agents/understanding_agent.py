"""
UnderstandingAgent: Parses a raw email into structured intent/entities/urgency.

First node in the pipeline. Pure LLM reasoning, no tool calls.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.llm_client import LLMClient, get_llm_client


class UnderstandingOutput(BaseModel):
    intent: str = Field(..., description="Short label for what the customer wants, e.g. 'account_access_issue'")
    entities: List[str] = Field(default_factory=list, description="Key entities mentioned: account, product, order ID, etc.")
    urgency: str = Field(..., description="One of: low, normal, high, critical")
    confidence: float = Field(..., ge=0.0, le=1.0)
    summary: str = Field(..., description="One-sentence summary of the request")


SYSTEM_PROMPT = """You are an email understanding agent for a customer support/sales/billing system.
Given a raw customer email, extract the intent, key entities, urgency, and a one-sentence summary.
Urgency should be "critical" only for account lockouts, security issues, or active service outages.
Be precise and concise."""


class UnderstandingAgent:
    name = "understanding_agent"
    capability_tags = ["email_understanding", "intent_extraction"]
    capability_description = (
        "Parses a raw customer email to extract intent, key entities, urgency level, "
        "and a short summary. Always the first step in processing an email."
    )

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or get_llm_client()

    async def run(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        subject = input_data.get("email_subject", "")
        body = input_data.get("email_body", "")

        prompt = f"Email subject: {subject}\n\nEmail body:\n{body}"

        result = await self.llm.call(
            prompt=prompt,
            response_schema=UnderstandingOutput,
            system=SYSTEM_PROMPT,
        )

        output = result.output
        return {
            "intent": output.intent,
            "entities": output.entities,
            "urgency": output.urgency,
            "confidence": output.confidence,
            "summary": output.summary,
            "_latency_ms": result.latency_ms,
            "_cost_usd": result.cost_usd,
        }
