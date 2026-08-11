"""
LLM Client: Thin wrapper around LiteLLM, shared by every agent.

Provides structured output (Pydantic-validated) rather than raw text, and
tracks token usage/cost per call so WorkflowState.add_node_log() can record it.
"""

from typing import Any, Dict, Optional, Type, TypeVar
import json
import logging

import litellm

from src.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T")


class LLMCallResult:
    """Result of a single LLM call: parsed output + cost/latency metadata."""

    def __init__(
        self,
        output: Any,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        latency_ms: float,
        raw_text: str,
    ):
        self.output = output
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.cost_usd = cost_usd
        self.latency_ms = latency_ms
        self.raw_text = raw_text


class LLMClient:
    """
    Wraps litellm.completion() to give agents structured, validated output.

    Every agent calls this instead of talking to litellm/the provider SDK
    directly — this is the one place that knows about models, cost tracking,
    and JSON-schema enforcement.
    """

    def __init__(self, default_model: Optional[str] = None):
        self.default_model = default_model or self._resolve_default_model()

    def _resolve_default_model(self) -> str:
        if settings.llm_provider == "anthropic":
            return "claude-sonnet-5"
        return "gpt-4o-mini"

    async def call(
        self,
        prompt: str,
        response_schema: Type[T],
        system: Optional[str] = None,
        model: Optional[str] = None,
    ) -> LLMCallResult:
        """
        Call the LLM and parse the response into response_schema.

        Args:
            prompt: The user-turn content (task-specific instructions + data).
            response_schema: A Pydantic model class describing the expected output.
            system: Optional system prompt (persona/role instructions).
            model: Override the default model for this call.

        Returns:
            LLMCallResult with a validated instance of response_schema in .output.

        Raises:
            ValueError: If the LLM response can't be parsed into response_schema.
        """
        import time

        model_id = model or self.default_model
        schema = response_schema.model_json_schema()

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({
            "role": "user",
            "content": (
                f"{prompt}\n\n"
                f"Respond with ONLY a JSON object matching this schema, no other text:\n"
                f"{json.dumps(schema, indent=2)}"
            ),
        })

        start = time.monotonic()
        response = await litellm.acompletion(
            model=model_id,
            messages=messages,
        )
        latency_ms = (time.monotonic() - start) * 1000

        raw_text = response.choices[0].message.content
        usage = response.usage

        try:
            parsed_json = json.loads(_extract_json(raw_text))
            output = response_schema.model_validate(parsed_json)
        except Exception as e:
            raise ValueError(
                f"Failed to parse LLM response into {response_schema.__name__}: {e}\n"
                f"Raw response: {raw_text}"
            )

        cost_usd = litellm.completion_cost(completion_response=response) or 0.0

        return LLMCallResult(
            output=output,
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            raw_text=raw_text,
        )


def _extract_json(text: str) -> str:
    """Strip markdown code fences if the model wrapped the JSON in ```json ... ```."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:] if lines[0].startswith("```") else lines
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


_default_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create the global LLMClient instance."""
    global _default_client
    if _default_client is None:
        _default_client = LLMClient()
    return _default_client
