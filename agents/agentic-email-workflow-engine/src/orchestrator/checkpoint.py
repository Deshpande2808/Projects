"""
Checkpointing: Persistence layer for LangGraph.

Allows workflows to survive process crashes and be resumed from last step.
Uses Postgres to store workflow state checkpoints.

In Phase 1, this is a stub (in-memory). In Phase 7, wire it to real Postgres.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class WorkflowCheckpoint:
    """
    Data structure for a checkpoint.

    Stores the complete state of a workflow at a point in time,
    allowing resumption if interrupted.
    """

    def __init__(
        self,
        workflow_id: str,
        step_name: str,
        state_snapshot: Dict[str, Any],
        timestamp: Optional[datetime] = None,
    ):
        self.workflow_id = workflow_id
        self.step_name = step_name
        self.state_snapshot = state_snapshot
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "workflow_id": self.workflow_id,
            "step_name": self.step_name,
            "state_snapshot": self.state_snapshot,
            "timestamp": self.timestamp.isoformat(),
        }


class CheckpointManager:
    """
    Manages checkpoints for workflow persistence.

    In Phase 1: In-memory storage (for testing)
    In Phase 7: Swap for PostgresCheckpointManager (real persistence)
    """

    def __init__(self):
        """Initialize checkpoint manager."""
        # In-memory storage for Phase 1
        self.checkpoints: Dict[str, Dict[str, WorkflowCheckpoint]] = {}

    def save_checkpoint(
        self,
        workflow_id: str,
        step_name: str,
        state_snapshot: Dict[str, Any],
    ) -> None:
        """
        Save a checkpoint for a workflow.

        Args:
            workflow_id: ID of the workflow
            step_name: Name of the step being checkpointed
            state_snapshot: Complete state at this point
        """
        if workflow_id not in self.checkpoints:
            self.checkpoints[workflow_id] = {}

        checkpoint = WorkflowCheckpoint(
            workflow_id=workflow_id,
            step_name=step_name,
            state_snapshot=state_snapshot,
        )

        self.checkpoints[workflow_id][step_name] = checkpoint
        logger.info(f"Checkpoint saved: {workflow_id} @ {step_name}")

    def get_checkpoint(
        self,
        workflow_id: str,
        step_name: str,
    ) -> Optional[WorkflowCheckpoint]:
        """
        Retrieve a checkpoint.

        Args:
            workflow_id: ID of the workflow
            step_name: Name of the step

        Returns:
            Checkpoint if found, None otherwise
        """
        if workflow_id not in self.checkpoints:
            return None
        return self.checkpoints[workflow_id].get(step_name)

    def get_latest_checkpoint(self, workflow_id: str) -> Optional[WorkflowCheckpoint]:
        """
        Get the most recent checkpoint for a workflow.

        Args:
            workflow_id: ID of the workflow

        Returns:
            Latest checkpoint if found, None otherwise
        """
        if workflow_id not in self.checkpoints:
            return None

        checkpoints = self.checkpoints[workflow_id]
        if not checkpoints:
            return None

        # Return the checkpoint with the latest timestamp
        return max(checkpoints.values(), key=lambda cp: cp.timestamp)

    def list_checkpoints(self, workflow_id: str) -> list:
        """
        List all checkpoints for a workflow.

        Args:
            workflow_id: ID of the workflow

        Returns:
            List of checkpoints, sorted by timestamp
        """
        if workflow_id not in self.checkpoints:
            return []

        checkpoints = list(self.checkpoints[workflow_id].values())
        return sorted(checkpoints, key=lambda cp: cp.timestamp)

    def resume_from_checkpoint(
        self,
        workflow_id: str,
        step_name: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Resume a workflow from a specific checkpoint.

        Args:
            workflow_id: ID of the workflow
            step_name: Step to resume from

        Returns:
            The saved state, or None if checkpoint not found
        """
        checkpoint = self.get_checkpoint(workflow_id, step_name)
        if checkpoint:
            logger.info(f"Resuming from checkpoint: {workflow_id} @ {step_name}")
            return checkpoint.state_snapshot
        return None

    def delete_checkpoint(self, workflow_id: str, step_name: Optional[str] = None) -> None:
        """
        Delete a checkpoint (mainly for testing/cleanup).

        Args:
            workflow_id: ID of the workflow
            step_name: Specific step to delete, or None to delete all
        """
        if workflow_id not in self.checkpoints:
            return

        if step_name:
            self.checkpoints[workflow_id].pop(step_name, None)
        else:
            self.checkpoints.pop(workflow_id, None)

        logger.info(f"Checkpoint deleted: {workflow_id} @ {step_name or 'all'}")

    def clear_all(self) -> None:
        """Clear all checkpoints (testing only)."""
        self.checkpoints.clear()


# Global checkpoint manager instance
_checkpoint_manager: Optional[CheckpointManager] = None


def get_checkpoint_manager() -> CheckpointManager:
    """
    Get or create the global checkpoint manager.

    Returns:
        CheckpointManager instance
    """
    global _checkpoint_manager
    if _checkpoint_manager is None:
        _checkpoint_manager = CheckpointManager()
    return _checkpoint_manager
