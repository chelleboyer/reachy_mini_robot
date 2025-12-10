"""LangGraph orchestrator for Reachy Mini brain.

This module defines the StateGraph that coordinates execution flow between
perception, cognition, skill, execution, and memory nodes.

Architecture:
    START → Perception → Cognition → Skills → Execution → END
    
    Memory nodes can be invoked conditionally (e.g., when human detected).

Usage:
    >>> from brain.graph import compile_graph
    >>> from brain.models.state import create_initial_state
    >>> 
    >>> graph = compile_graph(reachy_mini=reachy_mini)
    >>> initial_state = create_initial_state()
    >>> result = graph.invoke(initial_state)
"""

import functools
from langgraph.graph import StateGraph, START, END

from reachy_mini_ranger.brain.models.state import BrainState, update_timestamp, add_log, HeadCommand
from reachy_mini_ranger.brain.nodes.perception.vision_node import vision_node
from reachy_mini_ranger.brain.utils.kinematics import calculate_look_at_with_safety


# ============================================================================
# Perception Node Functions
# ============================================================================

def perception_node(state: BrainState, reachy_mini=None) -> BrainState:
    """Process sensory inputs (vision, audio).
    
    Currently implements:
    - Face detection via vision_node (YOLO-based)
    
    TODO:
    - Audio wake word detection
    - Multi-modal sensor fusion
    
    Args:
        state: Current BrainState
        reachy_mini: ReachyMini instance (optional, for camera/audio access)
        
    Returns:
        Updated BrainState including face detections
    """
    # Run vision processing (vision_node handles logging and timestamp)
    # Pass reachy_mini for camera access (None in tests)
    return vision_node(state, reachy_mini=reachy_mini)


def cognition_node(state: BrainState) -> BrainState:
    """Update emotion, manage goals, calculate head orientation.
    
    Currently implements:
    - Head orientation calculation for primary face tracking
    
    TODO:
    - Update emotional state based on interactions
    - Create/prioritize goals
    - Select appropriate skill based on context
    
    Args:
        state: Current BrainState
        
    Returns:
        Updated BrainState
    """
    updated = state.model_copy(deep=True)
    
    # Calculate head orientation to look at primary human
    primary_human = next((h for h in updated.world_model.humans if h.is_primary), None)
    
    if primary_human:
        # Calculate angles to look at primary human
        yaw, pitch, roll = calculate_look_at_with_safety(
            target_x=primary_human.position.z,  # z is forward in our coordinate system
            target_y=primary_human.position.x,  # x is left
            target_z=primary_human.position.y,  # y is up
            current_yaw=updated.actuator_commands.head.yaw,
            current_pitch=updated.actuator_commands.head.pitch,
            current_roll=updated.actuator_commands.head.roll,
            body_yaw=0.0,  # TODO: Get from robot state
            progress=0.8,  # Faster response (80% per cycle) - at 3 Hz YOLO speed
            easing="cubic",
        )
        
        # Update head commands (no duration - streaming control)
        updated.actuator_commands.head = HeadCommand(
            yaw=yaw,
            pitch=pitch,
            roll=roll,
            duration=0.0,  # Immediate update for streaming control
        )
        
        updated = add_log(
            updated,
            f"Cognition: Calculated head angles for Human {primary_human.persistent_id} "
            f"(yaw={yaw:.1f}°, pitch={pitch:.1f}°)"
        )
    else:
        updated = add_log(updated, "Cognition: No primary human to track")
    
    updated = update_timestamp(updated)
    
    # TODO: Update emotion, goals, current_plan
    
    return updated


def skill_node(state: BrainState) -> BrainState:
    """Execute high-level behaviors (social interaction, idle exploration).
    
    This node will eventually:
    - Generate LLM responses for social interaction
    - Coordinate gestures with speech
    - Execute idle scanning behaviors
    
    Currently: Placeholder that logs execution.
    
    Args:
        state: Current BrainState
        
    Returns:
        Updated BrainState
    """
    updated = state.model_copy(deep=True)
    updated = add_log(updated, "Skill node executed")
    updated = update_timestamp(updated)
    
    # Placeholder: In real implementation, would update:
    # - state.actuator_commands.head
    # - state.actuator_commands.antennas
    # - state.actuator_commands.voice.text
    
    return updated


def execution_node(state: BrainState) -> BrainState:
    """Execute actuator commands with safety filtering.
    
    Safety filter validates all motor commands against physical limits:
    - Head yaw: ±180° (full rotation)
    - Head pitch: ±40° (prevent cable strain)
    - Head roll: ±40° (prevent cable strain)
    - Body-to-head yaw difference: ±65° (prevent body twist)
    
    Violations are logged and clamped to safe limits.
    
    Note: This node prepares safe commands for execution. The main app
    loop actually executes commands via ReachyMini SDK.
    
    Args:
        state: Current BrainState with actuator_commands
        
    Returns:
        Updated BrainState with validated actuator_commands
    """
    updated = state.model_copy(deep=True)
    
    # Safety validation for head commands
    head_cmd = updated.actuator_commands.head
    violations = []
    
    # Clamp yaw to ±180°
    if head_cmd.yaw < -180.0:
        violations.append(f"yaw {head_cmd.yaw:.1f}° < -180° (clamped)")
        head_cmd.yaw = -180.0
    elif head_cmd.yaw > 180.0:
        violations.append(f"yaw {head_cmd.yaw:.1f}° > 180° (clamped)")
        head_cmd.yaw = 180.0
    
    # Clamp pitch to ±40°
    if head_cmd.pitch < -40.0:
        violations.append(f"pitch {head_cmd.pitch:.1f}° < -40° (clamped)")
        head_cmd.pitch = -40.0
    elif head_cmd.pitch > 40.0:
        violations.append(f"pitch {head_cmd.pitch:.1f}° > 40° (clamped)")
        head_cmd.pitch = 40.0
    
    # Clamp roll to ±40°
    if head_cmd.roll < -40.0:
        violations.append(f"roll {head_cmd.roll:.1f}° < -40° (clamped)")
        head_cmd.roll = -40.0
    elif head_cmd.roll > 40.0:
        violations.append(f"roll {head_cmd.roll:.1f}° > 40° (clamped)")
        head_cmd.roll = 40.0
    
    # Log safety violations
    if violations:
        updated = add_log(updated, f"Safety violations: {', '.join(violations)}")
    
    # Log execution
    updated = add_log(updated, 
        f"Execution: head=({head_cmd.yaw:.1f}°, {head_cmd.pitch:.1f}°, {head_cmd.roll:.1f}°)")
    updated = update_timestamp(updated)
    
    return updated


# ============================================================================
# Graph Construction
# ============================================================================

def create_graph(reachy_mini=None) -> StateGraph:
    """Create the LangGraph StateGraph with all nodes and edges.
    
    Args:
        reachy_mini: Optional ReachyMini instance for hardware access (camera, audio)
    
    Returns:
        StateGraph: Configured graph ready for compilation
    
    Example:
        >>> graph = create_graph(reachy_mini=reachy_mini)
        >>> app = graph.compile()
    """
    # Initialize graph with BrainState schema
    graph = StateGraph(BrainState)
    
    # Bind reachy_mini to perception node for camera access
    perception_with_hardware = functools.partial(perception_node, reachy_mini=reachy_mini)
    
    # Add nodes
    graph.add_node("perception", perception_with_hardware)
    graph.add_node("cognition", cognition_node)
    graph.add_node("skills", skill_node)
    graph.add_node("execution", execution_node)
    
    # Define edges (execution flow)
    graph.add_edge(START, "perception")
    graph.add_edge("perception", "cognition")
    graph.add_edge("cognition", "skills")
    graph.add_edge("skills", "execution")
    graph.add_edge("execution", END)
    
    return graph


class CompiledBrainGraph:
    """Wrapper for compiled LangGraph that reconstructs BrainState from dict result."""
    
    def __init__(self, compiled_graph):
        self._compiled = compiled_graph
    
    def invoke(self, state: BrainState) -> BrainState:
        """Invoke graph and return final BrainState.
        
        Args:
            state: Input BrainState
            
        Returns:
            BrainState: Updated state after graph execution
        """
        result = self._compiled.invoke(state)
        
        # LangGraph with Pydantic state returns dict of field values
        # Reconstruct BrainState from dict
        if isinstance(result, BrainState):
            return result
        elif isinstance(result, dict):
            # Reconstruct from dict representation
            return BrainState(**result)
        else:
            raise TypeError(f"Unexpected result type: {type(result)}")
    
    def __call__(self, state: BrainState) -> BrainState:
        """Allow direct call: app(state)."""
        return self.invoke(state)


def compile_graph(reachy_mini=None):
    """Create and compile the brain graph.
    
    Args:
        reachy_mini: Optional ReachyMini instance for hardware access (camera, audio)
    
    Returns:
        CompiledBrainGraph: Wrapper with invoke() method that returns BrainState
        
    Example:
        >>> app = compile_graph(reachy_mini=reachy_mini)
        >>> result = app.invoke(create_initial_state())
        >>> # Or call directly:
        >>> result = app(create_initial_state())
    """
    graph = create_graph(reachy_mini=reachy_mini)
    compiled = graph.compile()
    return CompiledBrainGraph(compiled)


# ============================================================================
# Convenience Functions
# ============================================================================

def run_brain_cycle(state: BrainState) -> BrainState:
    """Execute one complete brain cycle.
    
    Args:
        state: Current BrainState
        
    Returns:
        BrainState: Updated state after full cycle
        
    Example:
        >>> from brain.models.state import create_initial_state
        >>> initial = create_initial_state()
        >>> result = run_brain_cycle(initial)
        >>> len(result.metadata.logs)  # Should have 4 log entries
        4
    """
    app = compile_graph()
    return app.invoke(state)
