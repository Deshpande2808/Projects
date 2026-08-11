"""
AggregationAgent: Synthesizes results from all worker agents into coherent findings.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.llm_client import LLMClient, get_llm_client


class AggregationOutput(BaseModel):
    summary: str = Field(..., description="One-paragraph synthesis of what was found")
    key_facts: List[str] = Field(default_factory=list, description="Bullet-point facts gathered from agent results")
    conflicts: List[str] = Field(default_factory=list, description="Any contradictions found between agent results")
    recommendations: List[str] = Field(default_factory=list, description="Suggested next actions")


SYSTEM_PROMPT = """You are an aggregation agent. Given the original email understanding and the
results from several specialist agents (database lookups, document searches, etc.), synthesize
a coherent picture: what did we learn, are there any conflicts between sources, and what should
happen next. Be factual — don't invent data not present in the agent results."""


class AggregationAgent:
    name = "aggregation_agent"
    capability_tags = ["result_aggregation"]
    capability_description = (
        "Synthesizes results from multiple specialist agents into one coherent set of findings, "
        "flagging conflicts and recommending next steps."
    )

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or get_llm_client()

    async def run(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        understanding = input_data.get("understanding", {})
        agent_results = input_data.get("agent_results", {})

        results_text = "\n".join(
            f"- {agent_name}: {result}" for agent_name, result in agent_results.items()
        )

        prompt = (
            f"Original request summary: {understanding.get('summary')}\n\n"
            f"Agent results:\n{results_text}\n\n"
            f"Synthesize these into a coherent set of findings."
        )

        result = await self.llm.call(
            prompt=prompt,
            response_schema=AggregationOutput,
            system=SYSTEM_PROMPT,
        )

        output = result.output
        return {
            "summary": output.summary,
            "key_facts": output.key_facts,
            "conflicts": output.conflicts,
            "recommendations": output.recommendations,
            "_latency_ms": result.latency_ms,
            "_cost_usd": result.cost_usd,
        }
