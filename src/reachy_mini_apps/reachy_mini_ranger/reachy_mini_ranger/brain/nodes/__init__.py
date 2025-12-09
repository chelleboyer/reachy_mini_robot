"""LangGraph node implementations.

Nodes are stateless functions that read BrainState, perform computation,
and return updated BrainState. Organized into five families:
- perception: Sensory input processing
- cognition: Decision-making and planning
- skills: High-level behaviors
- execution: Actuator control
- memory: Storage and retrieval
"""
