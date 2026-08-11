"""
Agent Protocol: Contract for all agent implementations.

An Agent is a specialized worker that:
1. Understands what it can do (via capability_tags and capability_description)
2. Takes input, does work (using tools), produces output
3. Is discovered dynamically based on task requirements

All agents must implement this protocol.
"""

from typing import Protocol, Any, Dict, List, Optional, runtime_checkable


@runtime_checkable
class Agent(Protocol):
    """
    Protocol that all agents must implement.

    An agent is a specialized AI worker that can:
    - Process input data
    - Call tools to accomplish tasks
    - Produce structured output

    Agents are discovered dynamically based on:
    - Capability tags (fast, tag-based matching)
    - Capability description (semantic matching via embeddings)
    """

    name: str
    """Unique identifier for this agent (e.g., "understanding_agent", "database_agent")"""

    capability_tags: List[str]
    """
    Tags describing what this agent can do (e.g., ["email_understanding", "intent_extraction"]).
    Used for fast tag-based routing. Tags should be specific and hierarchical.
    """

    capability_description: str
    """
    Natural language description of what this agent does.
    Used for semantic/vector-based routing when tag matching is ambiguous.
    Example: "Parses raw emails to extract intent, entities, and urgency level"
    """

    async def run(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute the agent with the given input.

        Args:
            input_data: Dictionary containing agent-specific input.
                       Must include all required fields for this agent.
            context: Optional dictionary with execution context
                    (e.g., workflow_id, user_id, execution_metadata).

        Returns:
            Dictionary with the agent's structured output.
            Structure depends on the agent type.

        Raises:
            AgentError: If the agent execution fails.

        Example:
            >>> understanding_agent = UnderstandingAgent(tool_registry)
            >>> result = await understanding_agent.run({
            ...     "email_subject": "Account Locked",
            ...     "email_body": "I can't log in..."
            ... }, context={"workflow_id": "123"})
            >>> print(result)
            {
                "intent": "account_access_issue",
                "urgency": "high",
                "entities": ["account", "login"],
                "confidence": 0.95
            }
        """
        ...


class AgentError(Exception):
    """Raised when an agent execution fails."""
    pass


class AgentNotFoundError(AgentError):
    """Raised when a requested agent is not registered."""
    pass
