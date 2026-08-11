"""
Workflow State: The envelope that carries email data through the entire pipeline.

One WorkflowState = One Email.
As the email flows through agents (understanding → decomposition → routing → execution),
each agent updates parts of this state.

This is the single source of truth for all workflow data.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class WorkflowStatus(str, Enum):
    """All possible workflow states."""
    PENDING = "pending"
    UNDERSTANDING = "understanding"
    DECOMPOSED = "decomposed"
    ROUTING = "routing"
    EXECUTING_SUBTASKS = "executing_subtasks"
    AGGREGATING = "aggregating"
    GENERATING_DRAFT = "generating_draft"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING_ACTIONS = "executing_actions"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowState(BaseModel):
    """
    Central state object for an email workflow.

    Flows through the pipeline:
    email → understanding → decomposition → routing → execution → aggregation → draft → approval → execution

    Each node reads this state, does work, updates this state, passes to next node.
    """

    # ========================================================================
    # EMAIL INPUT
    # ========================================================================
    workflow_id: str = Field(..., description="Unique identifier for this workflow")
    email_id: str = Field(..., description="Original email ID from source")
    email_subject: str = Field(..., description="Email subject line")
    email_body: str = Field(..., description="Email body/content")
    email_from: str = Field(default="", description="Sender email address")
    email_received_at: datetime = Field(default_factory=datetime.now, description="When email was received")

    # ========================================================================
    # PHASE 1: EMAIL UNDERSTANDING
    # ========================================================================
    understanding: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Output from UnderstandingAgent: {intent, entities, urgency, confidence, ...}"
    )

    # ========================================================================
    # PHASE 2: TASK DECOMPOSITION
    # ========================================================================
    subtasks: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of subtasks to execute, each with: {id, description, required_capabilities, dependencies}"
    )

    # ========================================================================
    # PHASE 3: AGENT ROUTING & EXECUTION
    # ========================================================================
    agent_assignments: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of subtask_id → assigned_agent_name"
    )

    agent_results: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Results from each agent: {agent_name → {status, output, latency_ms, cost_usd, error}}"
    )

    # ========================================================================
    # PHASE 4: RESULT AGGREGATION
    # ========================================================================
    aggregated_findings: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Synthesized findings from all agents: {summary, key_facts, conflicts, recommendations}"
    )

    # ========================================================================
    # PHASE 5: DRAFT GENERATION
    # ========================================================================
    draft: Optional[Dict[str, Any]] = Field(
        default=None,
        description="AI-generated response: {email_body, subject, actions, confidence, reasoning}"
    )

    # ========================================================================
    # PHASE 6: HUMAN APPROVAL GATE
    # ========================================================================
    approval_status: str = Field(
        default="pending",
        description="pending | approved | rejected | requires_changes"
    )

    approval_timestamp: Optional[datetime] = Field(
        default=None,
        description="When was approval decision made"
    )

    approved_by: Optional[str] = Field(
        default=None,
        description="User who approved/rejected"
    )

    approval_notes: Optional[str] = Field(
        default=None,
        description="User's comments on approval"
    )

    # ========================================================================
    # PHASE 7: ACTION EXECUTION
    # ========================================================================
    execution_results: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Results of executing approved actions: {action_id → {status, result, error}}"
    )

    # ========================================================================
    # WORKFLOW METADATA
    # ========================================================================
    status: WorkflowStatus = Field(
        default=WorkflowStatus.PENDING,
        description="Current phase of the workflow"
    )

    error_message: Optional[str] = Field(
        default=None,
        description="Error description if workflow failed"
    )

    cost_usd: float = Field(
        default=0.0,
        description="Total cost (LLM tokens + API calls) for this workflow"
    )

    latency_ms: Optional[float] = Field(
        default=None,
        description="Total time from start to finish in milliseconds"
    )

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # ========================================================================
    # AUDIT TRAIL
    # ========================================================================
    node_logs: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Log of every node execution: {node_name, input, output, latency_ms, cost_usd, timestamp}"
    )

    # ========================================================================
    # CONTEXT / METADATA
    # ========================================================================
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context: {user_id, organization_id, tags, ...}"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "wf-12345",
                "email_id": "email-67890",
                "email_subject": "Account Locked",
                "email_body": "I can't login to my account...",
                "email_from": "customer@example.com",
                "status": "understanding",
            }
        }

    def add_node_log(
        self,
        node_name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        latency_ms: float = 0,
        cost_usd: float = 0,
        error: Optional[str] = None,
    ) -> None:
        """
        Log a node execution for audit trail.

        Args:
            node_name: Name of the node that executed
            input_data: Input to the node
            output_data: Output from the node
            latency_ms: How long the node took (milliseconds)
            cost_usd: Cost of the node execution
            error: Error message if node failed
        """
        self.node_logs.append({
            "node_name": node_name,
            "input": input_data,
            "output": output_data,
            "latency_ms": latency_ms,
            "cost_usd": cost_usd,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        })

        # Update workflow-level cost
        self.cost_usd += cost_usd
        self.updated_at = datetime.now()

    def get_subtask(self, subtask_id: str) -> Optional[Dict[str, Any]]:
        """Get a subtask by ID."""
        for subtask in self.subtasks:
            if subtask.get("id") == subtask_id:
                return subtask
        return None

    def get_agent_result(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get result from a specific agent."""
        return self.agent_results.get(agent_name)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (for JSON serialization, logging)."""
        return self.model_dump(mode='json')
