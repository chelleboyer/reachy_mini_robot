"""Kinematics utilities for head orientation calculations.

This module provides functions to convert 3D positions to head angles,
apply safety limits, and generate smooth transitions for natural motion.

Coordinate System:
    Robot frame (standard robotics convention):
    - X: forward (positive = forward)
    - Y: left (positive = left)
    - Z: up (positive = up)
    
    Head angles:
    - Yaw: rotation around Z axis (positive = look left)
    - Pitch: rotation around Y axis (positive = look up)
    - Roll: rotation around X axis (positive = tilt left)
"""

from __future__ import annotations

import logging
import math
from typing import Tuple

import numpy as np


logger = logging.getLogger(__name__)


# Robot safety limits (from Reachy Mini specifications)
# See: .github/copilot-instructions.md
HEAD_YAW_LIMIT = 180.0  # degrees, ±180°
HEAD_PITCH_LIMIT = 40.0  # degrees, ±40°
HEAD_ROLL_LIMIT = 40.0  # degrees, ±40°
BODY_HEAD_YAW_DIFF_LIMIT = 65.0  # degrees, ±65° relative to body


def calculate_look_at_angles(
    target_x: float,
    target_y: float,
    target_z: float,
    current_yaw: float = 0.0,
) -> Tuple[float, float, float]:
    """Calculate head angles to look at a 3D point.
    
    Converts a target 3D position (relative to robot) into head angles.
    Uses standard robotics conventions with atan2 for angle calculation.
    
    Args:
        target_x: Target X position in meters (forward)
        target_y: Target Y position in meters (left)
        target_z: Target Z position in meters (up)
        current_yaw: Current head yaw in degrees (for roll compensation)
        
    Returns:
        Tuple of (yaw, pitch, roll) in degrees
        
    Example:
        >>> # Person 1m forward, 0.5m left, at head height
        >>> yaw, pitch, roll = calculate_look_at_angles(1.0, 0.5, 0.0)
        >>> print(f"Yaw: {yaw:.1f}°, Pitch: {pitch:.1f}°")
        Yaw: 26.6°, Pitch: 0.0°
    """
    # Calculate yaw (rotation around Z axis)
    # atan2(y, x) gives angle from forward axis
    yaw = math.degrees(math.atan2(target_y, target_x))
    
    # Calculate pitch (rotation around Y axis)
    # atan2(z, horizontal_distance)
    # Note: Reachy Mini convention is negative pitch = look up
    horizontal_distance = math.sqrt(target_x**2 + target_y**2)
    if horizontal_distance > 0.001:  # Avoid division by zero
        pitch = -math.degrees(math.atan2(target_z, horizontal_distance))  # Inverted for Reachy convention
    else:
        # Target directly above/below
        pitch = -90.0 if target_z > 0 else 90.0
    
    # Roll calculation (optional, for natural head tilt)
    # For now, keep roll at 0 (no tilt)
    # Future: could add slight roll when looking far to sides
    roll = 0.0
    
    logger.debug(
        f"Look at ({target_x:.2f}, {target_y:.2f}, {target_z:.2f}) -> "
        f"yaw={yaw:.1f}°, pitch={pitch:.1f}°, roll={roll:.1f}°"
    )
    
    return yaw, pitch, roll


def apply_safety_limits(
    yaw: float,
    pitch: float,
    roll: float,
    body_yaw: float = 0.0,
    warn_on_clamp: bool = True,
) -> Tuple[float, float, float]:
    """Apply safety limits to head angles.
    
    Clamps angles to safe ranges based on Reachy Mini specifications.
    Optionally warns when clamping occurs to aid debugging.
    
    Args:
        yaw: Desired yaw angle in degrees
        pitch: Desired pitch angle in degrees
        roll: Desired roll angle in degrees
        body_yaw: Current body yaw for relative limit checking
        warn_on_clamp: Whether to log warnings when clamping
        
    Returns:
        Tuple of (clamped_yaw, clamped_pitch, clamped_roll) in degrees
        
    Safety Limits:
        - Yaw: ±180° absolute, ±65° relative to body
        - Pitch: ±40°
        - Roll: ±40°
    """
    clamped_yaw = yaw
    clamped_pitch = pitch
    clamped_roll = roll
    clamped = False
    
    # Clamp pitch
    if pitch > HEAD_PITCH_LIMIT:
        clamped_pitch = HEAD_PITCH_LIMIT
        clamped = True
        if warn_on_clamp:
            logger.warning(f"Pitch clamped: {pitch:.1f}° -> {clamped_pitch:.1f}°")
    elif pitch < -HEAD_PITCH_LIMIT:
        clamped_pitch = -HEAD_PITCH_LIMIT
        clamped = True
        if warn_on_clamp:
            logger.warning(f"Pitch clamped: {pitch:.1f}° -> {clamped_pitch:.1f}°")
    
    # Clamp roll
    if roll > HEAD_ROLL_LIMIT:
        clamped_roll = HEAD_ROLL_LIMIT
        clamped = True
        if warn_on_clamp:
            logger.warning(f"Roll clamped: {roll:.1f}° -> {clamped_roll:.1f}°")
    elif roll < -HEAD_ROLL_LIMIT:
        clamped_roll = -HEAD_ROLL_LIMIT
        clamped = True
        if warn_on_clamp:
            logger.warning(f"Roll clamped: {roll:.1f}° -> {clamped_roll:.1f}°")
    
    # Clamp yaw (absolute)
    if yaw > HEAD_YAW_LIMIT:
        clamped_yaw = HEAD_YAW_LIMIT
        clamped = True
        if warn_on_clamp:
            logger.warning(f"Yaw clamped: {yaw:.1f}° -> {clamped_yaw:.1f}°")
    elif yaw < -HEAD_YAW_LIMIT:
        clamped_yaw = -HEAD_YAW_LIMIT
        clamped = True
        if warn_on_clamp:
            logger.warning(f"Yaw clamped: {yaw:.1f}° -> {clamped_yaw:.1f}°")
    
    # Check body-relative yaw limit
    yaw_diff = abs(clamped_yaw - body_yaw)
    if yaw_diff > BODY_HEAD_YAW_DIFF_LIMIT:
        # Clamp to ±65° relative to body
        if clamped_yaw > body_yaw:
            clamped_yaw = body_yaw + BODY_HEAD_YAW_DIFF_LIMIT
        else:
            clamped_yaw = body_yaw - BODY_HEAD_YAW_DIFF_LIMIT
        clamped = True
        if warn_on_clamp:
            logger.warning(
                f"Yaw-body difference clamped: {yaw_diff:.1f}° > {BODY_HEAD_YAW_DIFF_LIMIT}°, "
                f"yaw adjusted to {clamped_yaw:.1f}°"
            )
    
    if not clamped:
        logger.debug("All angles within safety limits")
    
    return clamped_yaw, clamped_pitch, clamped_roll


def ease_in_out_cubic(t: float) -> float:
    """Cubic ease-in-out interpolation function.
    
    Provides smooth acceleration and deceleration for natural motion.
    
    Args:
        t: Progress from 0.0 to 1.0
        
    Returns:
        Eased progress value from 0.0 to 1.0
        
    Reference:
        https://easings.net/#easeInOutCubic
    """
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2


def smooth_transition(
    current_angle: float,
    target_angle: float,
    progress: float,
    easing: str = "cubic",
) -> float:
    """Interpolate between current and target angle with easing.
    
    Generates smooth transitions between angles using easing functions.
    Handles angle wrapping for yaw (±180°).
    
    Args:
        current_angle: Starting angle in degrees
        target_angle: Target angle in degrees
        progress: Progress from 0.0 (start) to 1.0 (end)
        easing: Easing function name ("linear", "cubic")
        
    Returns:
        Interpolated angle in degrees
        
    Example:
        >>> # Smoothly move from 0° to 45° at 50% progress
        >>> angle = smooth_transition(0.0, 45.0, 0.5, "cubic")
        >>> print(f"Angle: {angle:.1f}°")
        Angle: 22.5°
    """
    # Clamp progress
    progress = np.clip(progress, 0.0, 1.0)
    
    # Apply easing function
    if easing == "cubic":
        eased_progress = ease_in_out_cubic(progress)
    elif easing == "linear":
        eased_progress = progress
    else:
        logger.warning(f"Unknown easing '{easing}', using linear")
        eased_progress = progress
    
    # Handle angle wrapping for yaw (shortest path)
    angle_diff = target_angle - current_angle
    
    # Normalize to [-180, 180]
    while angle_diff > 180:
        angle_diff -= 360
    while angle_diff < -180:
        angle_diff += 360
    
    # Interpolate
    interpolated = current_angle + angle_diff * eased_progress
    
    # Normalize result to [-180, 180]
    while interpolated > 180:
        interpolated -= 360
    while interpolated < -180:
        interpolated += 360
    
    return interpolated


def calculate_look_at_with_safety(
    target_x: float,
    target_y: float,
    target_z: float,
    current_yaw: float = 0.0,
    current_pitch: float = 0.0,
    current_roll: float = 0.0,
    body_yaw: float = 0.0,
    progress: float = 1.0,
    easing: str = "cubic",
) -> Tuple[float, float, float]:
    """Calculate look-at angles with safety limits and smooth transitions.
    
    Convenience function combining angle calculation, safety limits, and smoothing.
    
    Args:
        target_x: Target X position in meters
        target_y: Target Y position in meters
        target_z: Target Z position in meters
        current_yaw: Current head yaw in degrees
        current_pitch: Current head pitch in degrees
        current_roll: Current head roll in degrees
        body_yaw: Current body yaw in degrees
        progress: Transition progress 0.0-1.0 (1.0 = instant)
        easing: Easing function name
        
    Returns:
        Tuple of (yaw, pitch, roll) in degrees with safety and smoothing applied
    """
    # Calculate target angles
    target_yaw, target_pitch, target_roll = calculate_look_at_angles(
        target_x, target_y, target_z, current_yaw
    )
    
    # Apply safety limits to target
    target_yaw, target_pitch, target_roll = apply_safety_limits(
        target_yaw, target_pitch, target_roll, body_yaw, warn_on_clamp=True
    )
    
    # Smooth transition
    if progress < 1.0:
        yaw = smooth_transition(current_yaw, target_yaw, progress, easing)
        pitch = smooth_transition(current_pitch, target_pitch, progress, easing)
        roll = smooth_transition(current_roll, target_roll, progress, easing)
    else:
        yaw, pitch, roll = target_yaw, target_pitch, target_roll
    
    return yaw, pitch, roll
