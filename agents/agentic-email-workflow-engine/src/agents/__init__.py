"""
Agents module: All agent implementations.

Each agent implements the Agent protocol (base.py) and is registered in the
AgentRegistry at startup. Agents read from WorkflowState, optionally call
tools via ToolRegistry, and write structured output back.
"""

from src.agents.base import Agent, AgentError, AgentNotFoundError
from src.agents.understanding_agent import UnderstandingAgent
from src.agents.decomposition_agent import DecompositionAgent
from src.agents.database_agent import DatabaseAgent
from src.agents.document_agent import DocumentAgent
from src.agents.aggregation_agent import AggregationAgent
from src.agents.draft_agent import DraftAgent

__all__ = [
    "Agent",
    "AgentError",
    "AgentNotFoundError",
    "UnderstandingAgent",
    "DecompositionAgent",
    "DatabaseAgent",
    "DocumentAgent",
    "AggregationAgent",
    "DraftAgent",
]
