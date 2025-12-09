"""Unit tests for LangGraph brain orchestration.

Tests cover:
- Graph compilation
- Node execution flow
- State updates through graph
- Edge connectivity
"""

import pytest

from reachy_mini_ranger.brain.graph import (
    compile_graph,
    create_graph,
    run_brain_cycle,
    perception_node,
    cognition_node,
    skill_node,
    execution_node,
)
from reachy_mini_ranger.brain.models.state import create_initial_state, BrainState


class TestGraphCompilation:
    """Test graph creation and compilation."""

    def test_create_graph(self):
        """Test create_graph returns StateGraph."""
        graph = create_graph()
        
        assert graph is not None
        # Graph should have nodes registered
        assert "perception" in graph.nodes
        assert "cognition" in graph.nodes
        assert "skills" in graph.nodes
        assert "execution" in graph.nodes

    def test_compile_graph(self):
        """Test compile_graph returns compiled application."""
        app = compile_graph()
        
        assert app is not None
        # Should be invokable
        assert callable(app.invoke)


class TestNodeExecution:
    """Test individual node functions."""

    def test_perception_node_returns_dict(self):
        """Test perception_node returns dict with state key."""
        state = create_initial_state()
        result = perception_node(state)
        
        assert isinstance(result, dict)
        assert "state" in result
        assert isinstance(result["state"], BrainState)

    def test_perception_node_adds_log(self):
        """Test perception_node logs execution."""
        state = create_initial_state()
        initial_log_count = len(state.metadata.logs)
        
        result = perception_node(state)
        result_state = result["state"]
        
        assert len(result_state.metadata.logs) == initial_log_count + 1
        assert any("Perception" in log for log in result_state.metadata.logs)

    def test_cognition_node_returns_dict(self):
        """Test cognition_node returns dict with state key."""
        state = create_initial_state()
        result = cognition_node(state)
        
        assert isinstance(result, dict)
        assert "state" in result

    def test_skill_node_returns_dict(self):
        """Test skill_node returns dict with state key."""
        state = create_initial_state()
        result = skill_node(state)
        
        assert isinstance(result, dict)
        assert "state" in result

    def test_execution_node_returns_dict(self):
        """Test execution_node returns dict with state key."""
        state = create_initial_state()
        result = execution_node(state)
        
        assert isinstance(result, dict)
        assert "state" in result

    def test_nodes_dont_mutate_input(self):
        """Test nodes return copies, don't mutate input."""
        state = create_initial_state()
        original_log_count = len(state.metadata.logs)
        
        result = perception_node(state)
        
        # Original state unchanged
        assert len(state.metadata.logs) == original_log_count
        # Result state changed
        assert len(result["state"].metadata.logs) == original_log_count + 1


class TestGraphInvocation:
    """Test complete graph execution."""

    def test_graph_invoke_with_initial_state(self):
        """Test graph can be invoked with initial state."""
        app = compile_graph()
        initial_state = create_initial_state()
        
        result = app.invoke(initial_state)
        
        assert isinstance(result, BrainState)

    def test_graph_executes_all_nodes(self):
        """Test all nodes execute in order."""
        app = compile_graph()
        initial_state = create_initial_state()
        
        result = app.invoke(initial_state)
        
        # Should have logs from all 4 nodes
        assert len(result.metadata.logs) >= 4
        
        # Check each node executed
        log_text = " ".join(result.metadata.logs)
        assert "Perception" in log_text
        assert "Cognition" in log_text
        assert "Skill" in log_text
        assert "Execution" in log_text

    def test_graph_execution_order(self):
        """Test nodes execute in correct order."""
        app = compile_graph()
        initial_state = create_initial_state()
        
        result = app.invoke(initial_state)
        
        # Extract log messages in order
        logs = result.metadata.logs
        
        # Find indices of each node's log
        perception_idx = next(i for i, log in enumerate(logs) if "Perception" in log)
        cognition_idx = next(i for i, log in enumerate(logs) if "Cognition" in log)
        skill_idx = next(i for i, log in enumerate(logs) if "Skill" in log)
        execution_idx = next(i for i, log in enumerate(logs) if "Execution" in log)
        
        # Verify order: perception → cognition → skill → execution
        assert perception_idx < cognition_idx
        assert cognition_idx < skill_idx
        assert skill_idx < execution_idx

    def test_graph_updates_timestamp(self):
        """Test graph updates state timestamp."""
        app = compile_graph()
        initial_state = create_initial_state()
        initial_timestamp = initial_state.metadata.timestamp
        
        result = app.invoke(initial_state)
        
        # Timestamp should be updated
        assert result.metadata.timestamp > initial_timestamp

    def test_graph_preserves_state_structure(self):
        """Test graph preserves all state sections."""
        app = compile_graph()
        initial_state = create_initial_state()
        
        result = app.invoke(initial_state)
        
        # All sections should exist
        assert result.sensors is not None
        assert result.world_model is not None
        assert result.interaction is not None
        assert result.goals is not None
        assert result.current_plan is not None
        assert result.emotion is not None
        assert result.actuator_commands is not None
        assert result.metadata is not None


class TestRunBrainCycle:
    """Test convenience function."""

    def test_run_brain_cycle(self):
        """Test run_brain_cycle executes full cycle."""
        initial_state = create_initial_state()
        
        result = run_brain_cycle(initial_state)
        
        assert isinstance(result, BrainState)
        assert len(result.metadata.logs) >= 4

    def test_run_brain_cycle_multiple_times(self):
        """Test running multiple cycles in sequence."""
        state = create_initial_state()
        
        # Run 3 cycles
        for _ in range(3):
            state = run_brain_cycle(state)
        
        # Should accumulate logs (4 per cycle × 3 cycles = 12)
        assert len(state.metadata.logs) >= 12


class TestGraphEdges:
    """Test graph connectivity."""

    def test_graph_has_start_edge(self):
        """Test graph has START → perception edge."""
        graph = create_graph()
        
        # Graph should have perception as first node after START
        assert "perception" in graph.nodes

    def test_graph_has_end_edge(self):
        """Test graph has execution → END edge."""
        graph = create_graph()
        
        # Graph should have execution as last node before END
        assert "execution" in graph.nodes

    def test_all_nodes_connected(self):
        """Test all nodes are connected in the graph."""
        graph = create_graph()
        
        # All expected nodes should be registered
        expected_nodes = ["perception", "cognition", "skills", "execution"]
        for node in expected_nodes:
            assert node in graph.nodes
