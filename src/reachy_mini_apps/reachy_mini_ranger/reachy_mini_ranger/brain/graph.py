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
    >>> graph = compile_graph()
    >>> initial_state = create_initial_state()
    >>> result = graph.invoke(initial_state)
"""

from typing import Dict

from langgraph.graph import StateGraph, START, END

from brain.models.state import BrainState, update_timestamp, add_log
from brain.nodes.perception.vision_node import vision_node


# ============================================================================
# Perception Node Functions
# ============================================================================

def perception_node(state: BrainState) -> Dict[str, BrainState]:
    """Process sensory inputs (vision, audio).
    
    Currently implements:
    - Face detection via vision_node (YOLO-based)
    
    TODO:
    - Audio wake word detection
    - Multi-modal sensor fusion
    
    Args:
        state: Current BrainState
        
    Returns:
        Dict with updated BrainState including face detections
    """
    # Run vision processing
    updated_state = vision_node(state)
    state = updated_state["state"]
    
    # Add perception summary log
    updated = state.model_copy(deep=True)
    num_faces = len(updated.sensors.vision.faces)
    updated = add_log(updated, f"Perception node: {num_faces} face(s) detected")
    updated = update_timestamp(updated)
    return {"state": updated}


def cognition_node(state: BrainState) -> Dict[str, BrainState]:
    """Update emotion, manage goals, select behaviors.
    
    This node will eventually:
    - Update emotional state based on interactions
    - Create/prioritize goals
    - Select appropriate skill based on context
    
    Currently: Placeholder that logs execution.
    
    Args:
        state: Current BrainState
        
    Returns:
        Dict with updated BrainState
    """
    updated = state.model_copy(deep=True)
    updated = add_log(updated, "Cognition node executed")
    updated = update_timestamp(updated)
    
    # Placeholder: In real implementation, would update:
    # - state.emotion
    # - state.goals
    # - state.current_plan
    
    return {"state": updated}


def skill_node(state: BrainState) -> Dict[str, BrainState]:
    """Execute high-level behaviors (social interaction, idle exploration).
    
    This node will eventually:
    - Generate LLM responses for social interaction
    - Coordinate gestures with speech
    - Execute idle scanning behaviors
    
    Currently: Placeholder that logs execution.
    
    Args:
        state: Current BrainState
        
    Returns:
        Dict with updated BrainState
    """
    updated = state.model_copy(deep=True)
    updated = add_log(updated, "Skill node executed")
    updated = update_timestamp(updated)
    
    # Placeholder: In real implementation, would update:
    # - state.actuator_commands.head
    # - state.actuator_commands.antennas
    # - state.actuator_commands.voice.text
    
    return {"state": updated}


def execution_node(state: BrainState) -> Dict[str, BrainState]:
    """Execute actuator commands with safety filtering.
    
    This node will eventually:
    - Validate commands against safety limits
    - Execute motor movements via Reachy Mini SDK
    - Execute TTS voice output
    
    Currently: Placeholder that logs execution.
    
    Args:
        state: Current BrainState
        
    Returns:
        Dict with updated BrainState
    """
    updated = state.model_copy(deep=True)
    updated = add_log(updated, "Execution node executed")
    updated = update_timestamp(updated)
    
    # Placeholder: In real implementation, would:
    # - Validate state.actuator_commands (safety filter)
    # - Execute via ReachyMini SDK
    # - Execute TTS
    
    return {"state": updated}


# ============================================================================
# Graph Construction
# ============================================================================

def create_graph() -> StateGraph:
    """Create the LangGraph StateGraph with all nodes and edges.
    
    Returns:
        StateGraph: Configured graph ready for compilation
    
    Example:
        >>> graph = create_graph()
        >>> app = graph.compile()
    """
    # Initialize graph with BrainState schema
    graph = StateGraph(BrainState)
    
    # Add nodes
    graph.add_node("perception", perception_node)
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


def compile_graph():
    """Create and compile the brain graph.
    
    Returns:
        CompiledGraph: Ready-to-invoke graph application
        
    Example:
        >>> app = compile_graph()
        >>> result = app.invoke(create_initial_state())
    """
    graph = create_graph()
    return graph.compile()


# ============================================================================
# Convenience Functions
# ============================================================================

def run_brain_cycle(state: BrainState):
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
    result = app.invoke(state)
    return result
