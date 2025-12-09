"""LangGraph-based autonomous brain for Reachy Mini social robot.

This module implements a multi-agent brain architecture with five node families:
- Perception: Vision, audio, sensor processing
- Cognition: Emotion, goals, behavior selection
- Skills: Social interaction, idle behaviors
- Execution: Motor control, voice output, safety filters
- Memory: Person recognition, episodic memory, recall

All nodes operate on shared BrainState (Pydantic model) for type-safe data flow.
"""

__version__ = "0.1.0"
