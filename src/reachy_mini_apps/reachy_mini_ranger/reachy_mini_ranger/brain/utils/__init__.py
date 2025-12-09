"""Utility functions for the brain (kinematics, emotion modulation, helpers).

Shared utilities used across multiple nodes:
- kinematics.py: Head orientation calculations, IK helpers
- emotion_modulation.py: Emotion-based behavior modification
"""

from reachy_mini_ranger.brain.utils.kinematics import (
    calculate_look_at_angles,
    apply_safety_limits,
    smooth_transition,
    calculate_look_at_with_safety,
    ease_in_out_cubic,
)

__all__ = [
    "calculate_look_at_angles",
    "apply_safety_limits",
    "smooth_transition",
    "calculate_look_at_with_safety",
    "ease_in_out_cubic",
]
