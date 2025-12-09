"""Unit tests for execution_node safety filtering.

Tests cover:
- Safety limit enforcement (±40° pitch/roll, ±180° yaw)
- Safety violation logging
- Command validation and clamping
"""
import pytest

from reachy_mini_ranger.brain.graph import execution_node
from reachy_mini_ranger.brain.models.state import create_initial_state, HeadCommand


class TestExecutionNodeSafety:
    """Test execution node safety filtering."""
    
    def test_execution_node_within_limits(self):
        """Test execution node with commands within safety limits."""
        state = create_initial_state()
        state.actuator_commands.head = HeadCommand(
            yaw=30.0,
            pitch=20.0,
            roll=10.0
        )
        
        result = execution_node(state)
        
        # Commands should be unchanged
        assert result.actuator_commands.head.yaw == 30.0
        assert result.actuator_commands.head.pitch == 20.0
        assert result.actuator_commands.head.roll == 10.0
        
        # No safety violations logged
        assert not any("Safety violations" in log for log in result.metadata.logs)
    
    def test_execution_node_clamps_yaw_above_limit(self):
        """Test yaw clamping when exceeding +180°."""
        state = create_initial_state()
        state.actuator_commands.head.yaw = 200.0  # Above limit
        
        result = execution_node(state)
        
        # Yaw should be clamped to 180°
        assert result.actuator_commands.head.yaw == 180.0
        
        # Safety violation logged
        assert any("Safety violations" in log for log in result.metadata.logs)
        assert any("yaw 200.0° > 180°" in log for log in result.metadata.logs)
    
    def test_execution_node_clamps_yaw_below_limit(self):
        """Test yaw clamping when below -180°."""
        state = create_initial_state()
        state.actuator_commands.head.yaw = -200.0  # Below limit
        
        result = execution_node(state)
        
        # Yaw should be clamped to -180°
        assert result.actuator_commands.head.yaw == -180.0
        
        # Safety violation logged
        assert any("yaw -200.0° < -180°" in log for log in result.metadata.logs)
    
    def test_execution_node_clamps_pitch_above_limit(self):
        """Test pitch clamping when exceeding +40°."""
        state = create_initial_state()
        state.actuator_commands.head.pitch = 50.0  # Above limit
        
        result = execution_node(state)
        
        # Pitch should be clamped to 40°
        assert result.actuator_commands.head.pitch == 40.0
        
        # Safety violation logged
        assert any("pitch 50.0° > 40°" in log for log in result.metadata.logs)
    
    def test_execution_node_clamps_pitch_below_limit(self):
        """Test pitch clamping when below -40°."""
        state = create_initial_state()
        state.actuator_commands.head.pitch = -50.0  # Below limit
        
        result = execution_node(state)
        
        # Pitch should be clamped to -40°
        assert result.actuator_commands.head.pitch == -40.0
        
        # Safety violation logged
        assert any("pitch -50.0° < -40°" in log for log in result.metadata.logs)
    
    def test_execution_node_clamps_roll_above_limit(self):
        """Test roll clamping when exceeding +40°."""
        state = create_initial_state()
        state.actuator_commands.head.roll = 50.0  # Above limit
        
        result = execution_node(state)
        
        # Roll should be clamped to 40°
        assert result.actuator_commands.head.roll == 40.0
        
        # Safety violation logged
        assert any("roll 50.0° > 40°" in log for log in result.metadata.logs)
    
    def test_execution_node_clamps_roll_below_limit(self):
        """Test roll clamping when below -40°."""
        state = create_initial_state()
        state.actuator_commands.head.roll = -50.0  # Below limit
        
        result = execution_node(state)
        
        # Roll should be clamped to -40°
        assert result.actuator_commands.head.roll == -40.0
        
        # Safety violation logged
        assert any("roll -50.0° < -40°" in log for log in result.metadata.logs)
    
    def test_execution_node_clamps_multiple_violations(self):
        """Test multiple safety violations at once.
        
        Note: Pydantic validators on HeadCommand already clamp values,
        so we bypass validation to test execution_node clamping logic.
        """
        state = create_initial_state()
        # Bypass Pydantic validation using model_construct
        state.actuator_commands.head = HeadCommand.model_construct(
            yaw=200.0,    # Above limit
            pitch=-50.0,  # Below limit
            roll=50.0     # Above limit
        )
        
        result = execution_node(state)
        
        # All values should be clamped
        assert result.actuator_commands.head.yaw == 180.0
        assert result.actuator_commands.head.pitch == -40.0
        assert result.actuator_commands.head.roll == 40.0
        
        # Safety violations logged
        logs = " ".join(result.metadata.logs)
        assert "yaw 200.0° > 180°" in logs
        assert "pitch -50.0° < -40°" in logs
        assert "roll 50.0° > 40°" in logs
    
    def test_execution_node_boundary_values(self):
        """Test exact boundary values (should not be clamped)."""
        state = create_initial_state()
        state.actuator_commands.head = HeadCommand(
            yaw=180.0,
            pitch=40.0,
            roll=-40.0
        )
        
        result = execution_node(state)
        
        # Boundary values should be unchanged
        assert result.actuator_commands.head.yaw == 180.0
        assert result.actuator_commands.head.pitch == 40.0
        assert result.actuator_commands.head.roll == -40.0
        
        # No safety violations at boundaries
        assert not any("Safety violations" in log for log in result.metadata.logs)
    
    def test_execution_node_logs_execution(self):
        """Test execution node logs every execution."""
        state = create_initial_state()
        initial_log_count = len(state.metadata.logs)
        
        result = execution_node(state)
        
        # Log count should increase
        assert len(result.metadata.logs) > initial_log_count
        
        # Execution log should exist
        assert any("Execution:" in log for log in result.metadata.logs)
    
    def test_execution_node_updates_timestamp(self):
        """Test execution node updates timestamp."""
        state = create_initial_state()
        initial_timestamp = state.metadata.timestamp
        
        import time
        time.sleep(0.01)  # Small delay to ensure timestamp changes
        
        result = execution_node(state)
        
        # Timestamp should be updated
        assert result.metadata.timestamp > initial_timestamp
    
    def test_execution_node_doesnt_mutate_input(self):
        """Test execution node doesn't mutate input state."""
        state = create_initial_state()
        state.actuator_commands.head.yaw = 200.0  # Will be clamped
        
        original_yaw = state.actuator_commands.head.yaw
        result = execution_node(state)
        
        # Original state should be unchanged
        assert state.actuator_commands.head.yaw == original_yaw
        
        # Result state should be clamped
        assert result.actuator_commands.head.yaw == 180.0
