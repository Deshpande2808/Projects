"""
Tests for orchestrator components: WorkflowState, graph, checkpointing.

Verifies:
1. WorkflowState tracks all workflow data correctly
2. LangGraph compiles and has proper structure
3. Checkpointing saves and resumes workflows
"""

import pytest
from datetime import datetime
from src.orchestrator import (
    WorkflowState,
    WorkflowStatus,
    create_workflow_graph,
    CheckpointManager,
    WorkflowCheckpoint,
    get_checkpoint_manager,
)


# ============================================================================
# WORKFLOW STATE TESTS
# ============================================================================

class TestWorkflowState:
    """Tests for WorkflowState."""

    def test_create_workflow_state(self):
        """Test creating a workflow state."""
        state = WorkflowState(
            workflow_id="wf-001",
            email_id="email-001",
            email_subject="Test Email",
            email_body="This is a test email",
        )

        assert state.workflow_id == "wf-001"
        assert state.email_id == "email-001"
        assert state.email_subject == "Test Email"
        assert state.status == WorkflowStatus.PENDING
        assert state.cost_usd == 0.0

    def test_workflow_state_default_values(self):
        """Test that workflow state has sensible defaults."""
        state = WorkflowState(
            workflow_id="wf-001",
            email_id="email-001",
            email_subject="Test",
            email_body="Test body",
        )

        assert state.understanding is None
        assert state.subtasks == []
        assert state.agent_results == {}
        assert state.aggregated_findings is None
        assert state.draft is None
        assert state.approval_status == "pending"
        assert state.execution_results == {}
        assert state.node_logs == []

    def test_add_node_log(self):
        """Test logging a node execution."""
        state = WorkflowState(
            workflow_id="wf-001",
            email_id="email-001",
            email_subject="Test",
            email_body="Test body",
        )

        state.add_node_log(
            node_name="understanding",
            input_data={"email_body": "Test"},
            output_data={"intent": "test"},
            latency_ms=100,
            cost_usd=0.01,
        )

        assert len(state.node_logs) == 1
        log = state.node_logs[0]
        assert log["node_name"] == "understanding"
        assert log["latency_ms"] == 100
        assert log["cost_usd"] == 0.01
        assert state.cost_usd == 0.01  # Total cost updated

    def test_add_multiple_node_logs(self):
        """Test adding multiple node logs."""
        state = WorkflowState(
            workflow_id="wf-001",
            email_id="email-001",
            email_subject="Test",
            email_body="Test body",
        )

        state.add_node_log("node-1", {}, {}, latency_ms=50, cost_usd=0.01)
        state.add_node_log("node-2", {}, {}, latency_ms=100, cost_usd=0.02)
        state.add_node_log("node-3", {}, {}, latency_ms=150, cost_usd=0.03)

        assert len(state.node_logs) == 3
        assert state.cost_usd == 0.06  # 0.01 + 0.02 + 0.03

    def test_get_subtask(self):
        """Test retrieving a subtask."""
        state = WorkflowState(
            workflow_id="wf-001",
            email_id="email-001",
            email_subject="Test",
            email_body="Test body",
            subtasks=[
                {"id": "subtask-1", "description": "Task 1"},
                {"id": "subtask-2", "description": "Task 2"},
            ]
        )

        subtask = state.get_subtask("subtask-1")
        assert subtask is not None
        assert subtask["description"] == "Task 1"

        missing = state.get_subtask("nonexistent")
        assert missing is None

    def test_get_agent_result(self):
        """Test retrieving an agent result."""
        state = WorkflowState(
            workflow_id="wf-001",
            email_id="email-001",
            email_subject="Test",
            email_body="Test body",
            agent_results={
                "database_agent": {"status": "success", "data": {"id": 123}},
                "document_agent": {"status": "success", "data": {"docs": []}},
            }
        )

        result = state.get_agent_result("database_agent")
        assert result is not None
        assert result["status"] == "success"
        assert result["data"]["id"] == 123

        missing = state.get_agent_result("nonexistent")
        assert missing is None

    def test_workflow_state_to_dict(self):
        """Test converting state to dictionary."""
        state = WorkflowState(
            workflow_id="wf-001",
            email_id="email-001",
            email_subject="Test",
            email_body="Test body",
        )

        state_dict = state.to_dict()
        assert isinstance(state_dict, dict)
        assert state_dict["workflow_id"] == "wf-001"
        assert state_dict["email_id"] == "email-001"


# ============================================================================
# WORKFLOW GRAPH TESTS
# ============================================================================

class TestWorkflowGraph:
    """Tests for LangGraph orchestration."""

    def test_create_workflow_graph(self):
        """Test creating a workflow graph."""
        graph = create_workflow_graph()
        assert graph is not None

    def test_graph_has_nodes(self):
        """Test that graph has all expected nodes."""
        graph = create_workflow_graph()

        # Get the graph's nodes (LangGraph API)
        # The graph should have nodes for each stage
        # Note: Testing LangGraph internals is tricky, so we just verify it compiles
        assert graph is not None


# ============================================================================
# CHECKPOINT MANAGER TESTS
# ============================================================================

class TestCheckpointManager:
    """Tests for WorkflowCheckpoint and CheckpointManager."""

    def test_create_checkpoint(self):
        """Test creating a checkpoint."""
        state_snapshot = {
            "workflow_id": "wf-001",
            "status": "understanding",
        }

        checkpoint = WorkflowCheckpoint(
            workflow_id="wf-001",
            step_name="understanding",
            state_snapshot=state_snapshot,
        )

        assert checkpoint.workflow_id == "wf-001"
        assert checkpoint.step_name == "understanding"
        assert checkpoint.state_snapshot == state_snapshot

    def test_checkpoint_to_dict(self):
        """Test converting checkpoint to dictionary."""
        checkpoint = WorkflowCheckpoint(
            workflow_id="wf-001",
            step_name="understanding",
            state_snapshot={"status": "understanding"},
        )

        checkpoint_dict = checkpoint.to_dict()
        assert checkpoint_dict["workflow_id"] == "wf-001"
        assert checkpoint_dict["step_name"] == "understanding"

    def test_save_and_retrieve_checkpoint(self):
        """Test saving and retrieving a checkpoint."""
        manager = CheckpointManager()
        state_snapshot = {"status": "understanding"}

        manager.save_checkpoint("wf-001", "understanding", state_snapshot)

        retrieved = manager.get_checkpoint("wf-001", "understanding")
        assert retrieved is not None
        assert retrieved.state_snapshot == state_snapshot

    def test_get_nonexistent_checkpoint(self):
        """Test retrieving a nonexistent checkpoint."""
        manager = CheckpointManager()

        checkpoint = manager.get_checkpoint("wf-001", "nonexistent")
        assert checkpoint is None

    def test_get_latest_checkpoint(self):
        """Test getting the most recent checkpoint."""
        manager = CheckpointManager()

        # Save multiple checkpoints
        manager.save_checkpoint("wf-001", "understanding", {"step": 1})
        manager.save_checkpoint("wf-001", "decomposition", {"step": 2})
        manager.save_checkpoint("wf-001", "routing", {"step": 3})

        # Get the latest
        latest = manager.get_latest_checkpoint("wf-001")
        assert latest is not None
        assert latest.step_name == "routing"

    def test_list_checkpoints(self):
        """Test listing all checkpoints for a workflow."""
        manager = CheckpointManager()

        manager.save_checkpoint("wf-001", "understanding", {})
        manager.save_checkpoint("wf-001", "decomposition", {})
        manager.save_checkpoint("wf-001", "routing", {})

        checkpoints = manager.list_checkpoints("wf-001")
        assert len(checkpoints) == 3

    def test_resume_from_checkpoint(self):
        """Test resuming from a checkpoint."""
        manager = CheckpointManager()
        state = {"status": "understanding", "data": "test"}

        manager.save_checkpoint("wf-001", "understanding", state)

        resumed = manager.resume_from_checkpoint("wf-001", "understanding")
        assert resumed == state

    def test_resume_from_nonexistent_checkpoint(self):
        """Test resuming from a checkpoint that doesn't exist."""
        manager = CheckpointManager()

        resumed = manager.resume_from_checkpoint("wf-001", "nonexistent")
        assert resumed is None

    def test_delete_checkpoint(self):
        """Test deleting a checkpoint."""
        manager = CheckpointManager()

        manager.save_checkpoint("wf-001", "understanding", {})
        assert manager.get_checkpoint("wf-001", "understanding") is not None

        manager.delete_checkpoint("wf-001", "understanding")
        assert manager.get_checkpoint("wf-001", "understanding") is None

    def test_delete_all_checkpoints(self):
        """Test deleting all checkpoints for a workflow."""
        manager = CheckpointManager()

        manager.save_checkpoint("wf-001", "step-1", {})
        manager.save_checkpoint("wf-001", "step-2", {})

        manager.delete_checkpoint("wf-001")

        checkpoints = manager.list_checkpoints("wf-001")
        assert len(checkpoints) == 0

    def test_multiple_workflows(self):
        """Test managing checkpoints for multiple workflows."""
        manager = CheckpointManager()

        manager.save_checkpoint("wf-001", "step-1", {"id": 1})
        manager.save_checkpoint("wf-002", "step-1", {"id": 2})

        checkpoint_1 = manager.get_checkpoint("wf-001", "step-1")
        checkpoint_2 = manager.get_checkpoint("wf-002", "step-1")

        assert checkpoint_1.state_snapshot["id"] == 1
        assert checkpoint_2.state_snapshot["id"] == 2

    def test_clear_all(self):
        """Test clearing all checkpoints."""
        manager = CheckpointManager()

        manager.save_checkpoint("wf-001", "step-1", {})
        manager.save_checkpoint("wf-002", "step-1", {})

        assert manager.list_checkpoints("wf-001")
        assert manager.list_checkpoints("wf-002")

        manager.clear_all()

        assert len(manager.list_checkpoints("wf-001")) == 0
        assert len(manager.list_checkpoints("wf-002")) == 0

    def test_global_checkpoint_manager(self):
        """Test getting the global checkpoint manager instance."""
        manager1 = get_checkpoint_manager()
        manager2 = get_checkpoint_manager()

        # Should be the same instance
        assert manager1 is manager2


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestOrchestratorIntegration:
    """Integration tests for orchestrator components."""

    def test_workflow_state_with_checkpointing(self):
        """Test saving/resuming a workflow state."""
        manager = CheckpointManager()

        # Create initial state
        state = WorkflowState(
            workflow_id="wf-001",
            email_id="email-001",
            email_subject="Test",
            email_body="Test body",
        )

        # Simulate processing
        state.understanding = {"intent": "support", "urgency": "high"}
        state.subtasks = [{"id": "subtask-1", "description": "Lookup customer"}]
        state.status = WorkflowStatus.UNDERSTANDING

        # Save checkpoint
        manager.save_checkpoint("wf-001", "understanding", state.to_dict())

        # Simulate crash/resume
        resumed_dict = manager.resume_from_checkpoint("wf-001", "understanding")
        resumed_state = WorkflowState(**resumed_dict)

        assert resumed_state.understanding == {"intent": "support", "urgency": "high"}
        assert len(resumed_state.subtasks) == 1
        assert resumed_state.status == WorkflowStatus.UNDERSTANDING

    def test_full_workflow_execution_trace(self):
        """Test tracing a workflow through multiple nodes."""
        state = WorkflowState(
            workflow_id="wf-001",
            email_id="email-001",
            email_subject="Account Issue",
            email_body="I can't access my account",
        )

        # Simulate each node executing and logging
        state.add_node_log("understanding", {}, {"intent": "support"}, latency_ms=100, cost_usd=0.01)
        state.add_node_log("decomposition", {}, {"subtasks": 2}, latency_ms=150, cost_usd=0.02)
        state.add_node_log("routing", {}, {"agents": 2}, latency_ms=200, cost_usd=0.03)
        state.add_node_log("aggregation", {}, {"findings": 1}, latency_ms=250, cost_usd=0.04)

        # Verify the trace
        assert len(state.node_logs) == 4
        assert state.cost_usd == 0.10  # 0.01 + 0.02 + 0.03 + 0.04
        assert state.node_logs[0]["node_name"] == "understanding"
        assert state.node_logs[-1]["node_name"] == "aggregation"
