"""Unit tests for kinematics utilities."""

import pytest
import math

from reachy_mini_ranger.brain.utils.kinematics import (
    calculate_look_at_angles,
    apply_safety_limits,
    smooth_transition,
    calculate_look_at_with_safety,
    ease_in_out_cubic,
    HEAD_YAW_LIMIT,
    HEAD_PITCH_LIMIT,
    HEAD_ROLL_LIMIT,
)


# ============================================================================
# Angle Calculation Tests
# ============================================================================


class TestCalculateLookAtAngles:
    """Test 3D position to angle conversion."""

    def test_look_forward(self):
        """Test looking straight forward."""
        yaw, pitch, roll = calculate_look_at_angles(1.0, 0.0, 0.0)
        assert abs(yaw) < 0.1  # Should be ~0°
        assert abs(pitch) < 0.1  # Should be ~0°
        assert abs(roll) < 0.1  # Should be ~0°

    def test_look_left(self):
        """Test looking left (positive yaw)."""
        yaw, pitch, roll = calculate_look_at_angles(1.0, 1.0, 0.0)
        assert 40 < yaw < 50  # Should be ~45°
        assert abs(pitch) < 0.1

    def test_look_right(self):
        """Test looking right (negative yaw)."""
        yaw, pitch, roll = calculate_look_at_angles(1.0, -1.0, 0.0)
        assert -50 < yaw < -40  # Should be ~-45°
        assert abs(pitch) < 0.1

    def test_look_up(self):
        """Test looking up (positive pitch)."""
        yaw, pitch, roll = calculate_look_at_angles(1.0, 0.0, 1.0)
        assert abs(yaw) < 0.1
        assert 40 < pitch < 50  # Should be ~45°

    def test_look_down(self):
        """Test looking down (negative pitch)."""
        yaw, pitch, roll = calculate_look_at_angles(1.0, 0.0, -0.5)
        assert abs(yaw) < 0.1
        assert -30 < pitch < -20  # Should be ~-26°

    def test_look_up_and_left(self):
        """Test looking up and left (combined yaw + pitch)."""
        yaw, pitch, roll = calculate_look_at_angles(1.0, 1.0, 1.0)
        assert 40 < yaw < 50  # Yaw ~45°
        assert 30 < pitch < 40  # Pitch ~35°

    def test_look_at_origin(self):
        """Test looking at origin (edge case)."""
        # Very close to origin - should handle gracefully
        yaw, pitch, roll = calculate_look_at_angles(0.001, 0.001, 0.0)
        # Should not crash, angles defined

    def test_look_directly_above(self):
        """Test looking straight up."""
        yaw, pitch, roll = calculate_look_at_angles(0.0, 0.0, 1.0)
        assert pitch == 90.0  # Straight up

    def test_look_directly_below(self):
        """Test looking straight down."""
        yaw, pitch, roll = calculate_look_at_angles(0.0, 0.0, -1.0)
        assert pitch == -90.0  # Straight down

    def test_known_angles(self):
        """Test with known geometric positions."""
        # 45° left, eye level
        yaw, pitch, roll = calculate_look_at_angles(1.0, 1.0, 0.0)
        assert abs(yaw - 45.0) < 0.1
        assert abs(pitch) < 0.1
        
        # 30° up (tan(30°) ≈ 0.577)
        yaw, pitch, roll = calculate_look_at_angles(1.732, 0.0, 1.0)
        assert abs(pitch - 30.0) < 0.1


# ============================================================================
# Safety Limit Tests
# ============================================================================


class TestApplySafetyLimits:
    """Test safety limit enforcement."""

    def test_within_limits_unchanged(self):
        """Test angles within limits are not clamped."""
        yaw, pitch, roll = apply_safety_limits(30.0, 20.0, 10.0, warn_on_clamp=False)
        assert yaw == 30.0
        assert pitch == 20.0
        assert roll == 10.0

    def test_pitch_limit_positive(self):
        """Test positive pitch clamping."""
        yaw, pitch, roll = apply_safety_limits(0.0, 50.0, 0.0, warn_on_clamp=False)
        assert pitch == HEAD_PITCH_LIMIT  # 40°

    def test_pitch_limit_negative(self):
        """Test negative pitch clamping."""
        yaw, pitch, roll = apply_safety_limits(0.0, -50.0, 0.0, warn_on_clamp=False)
        assert pitch == -HEAD_PITCH_LIMIT  # -40°

    def test_roll_limit_positive(self):
        """Test positive roll clamping."""
        yaw, pitch, roll = apply_safety_limits(0.0, 0.0, 50.0, warn_on_clamp=False)
        assert roll == HEAD_ROLL_LIMIT  # 40°

    def test_roll_limit_negative(self):
        """Test negative roll clamping."""
        yaw, pitch, roll = apply_safety_limits(0.0, 0.0, -50.0, warn_on_clamp=False)
        assert roll == -HEAD_ROLL_LIMIT  # -40°

    def test_yaw_limit_positive(self):
        """Test positive yaw clamping (body-relative takes precedence)."""
        # With body_yaw=0°, yaw is clamped to ±65° (body-relative limit)
        yaw, pitch, roll = apply_safety_limits(200.0, 0.0, 0.0, body_yaw=0.0, warn_on_clamp=False)
        assert yaw == 65.0  # Body-relative limit applied

    def test_yaw_limit_negative(self):
        """Test negative yaw clamping (body-relative takes precedence)."""
        # With body_yaw=0°, yaw is clamped to ±65° (body-relative limit)
        yaw, pitch, roll = apply_safety_limits(-200.0, 0.0, 0.0, body_yaw=0.0, warn_on_clamp=False)
        assert yaw == -65.0  # Body-relative limit applied

    def test_body_relative_yaw_limit_positive(self):
        """Test body-relative yaw clamping (positive)."""
        # Head yaw 80° with body at 0° -> diff = 80° > 65°
        yaw, pitch, roll = apply_safety_limits(80.0, 0.0, 0.0, body_yaw=0.0, warn_on_clamp=False)
        assert yaw == 65.0  # Clamped to body_yaw + 65°

    def test_body_relative_yaw_limit_negative(self):
        """Test body-relative yaw clamping (negative)."""
        # Head yaw -80° with body at 0° -> diff = 80° > 65°
        yaw, pitch, roll = apply_safety_limits(-80.0, 0.0, 0.0, body_yaw=0.0, warn_on_clamp=False)
        assert yaw == -65.0  # Clamped to body_yaw - 65°

    def test_all_limits_exceed(self):
        """Test all angles exceed limits simultaneously."""
        yaw, pitch, roll = apply_safety_limits(200.0, 50.0, -50.0, body_yaw=0.0, warn_on_clamp=False)
        # Yaw clamped by body-relative limit (±65°)
        assert yaw == 65.0
        assert pitch == HEAD_PITCH_LIMIT
        assert roll == -HEAD_ROLL_LIMIT


# ============================================================================
# Smooth Transition Tests
# ============================================================================


class TestSmoothTransition:
    """Test smooth angle interpolation."""

    def test_progress_zero_returns_current(self):
        """Test progress=0 returns current angle."""
        angle = smooth_transition(10.0, 50.0, 0.0, "linear")
        assert angle == 10.0

    def test_progress_one_returns_target(self):
        """Test progress=1 returns target angle."""
        angle = smooth_transition(10.0, 50.0, 1.0, "linear")
        assert angle == 50.0

    def test_linear_midpoint(self):
        """Test linear interpolation at 50%."""
        angle = smooth_transition(0.0, 100.0, 0.5, "linear")
        assert abs(angle - 50.0) < 0.1

    def test_cubic_easing(self):
        """Test cubic easing produces smooth curve."""
        # At 50%, cubic should be close to linear
        angle = smooth_transition(0.0, 100.0, 0.5, "cubic")
        assert 45 < angle < 55  # Around midpoint

    def test_angle_wrapping_positive(self):
        """Test angle wrapping for large positive angles."""
        # From 170° to -170° should go through 180° (shortest path)
        angle = smooth_transition(170.0, -170.0, 0.5, "linear")
        assert 175 < angle < 185 or -185 < angle < -175

    def test_angle_wrapping_negative(self):
        """Test angle wrapping for large negative angles."""
        # From -170° to 170° should go through -180°
        angle = smooth_transition(-170.0, 170.0, 0.5, "linear")
        assert 175 < angle < 185 or -185 < angle < -175

    def test_clamped_progress(self):
        """Test progress values outside [0, 1] are clamped."""
        angle_negative = smooth_transition(10.0, 50.0, -0.5, "linear")
        angle_excess = smooth_transition(10.0, 50.0, 1.5, "linear")
        assert angle_negative == 10.0  # Clamped to 0
        assert angle_excess == 50.0  # Clamped to 1


# ============================================================================
# Easing Function Tests
# ============================================================================


class TestEaseInOutCubic:
    """Test cubic easing function."""

    def test_starts_at_zero(self):
        """Test easing starts at 0."""
        assert ease_in_out_cubic(0.0) == 0.0

    def test_ends_at_one(self):
        """Test easing ends at 1."""
        assert abs(ease_in_out_cubic(1.0) - 1.0) < 0.001

    def test_midpoint_near_half(self):
        """Test easing passes through ~0.5 at t=0.5."""
        value = ease_in_out_cubic(0.5)
        assert 0.4 < value < 0.6

    def test_smooth_curve(self):
        """Test easing produces smooth acceleration/deceleration."""
        # Early acceleration
        early = ease_in_out_cubic(0.25)
        assert early < 0.25  # Slower than linear
        
        # Late deceleration
        late = ease_in_out_cubic(0.75)
        assert late > 0.75  # Slower than linear


# ============================================================================
# Integration Tests
# ============================================================================


class TestCalculateLookAtWithSafety:
    """Test combined calculation with safety and smoothing."""

    def test_instant_movement(self):
        """Test instant movement (progress=1.0)."""
        yaw, pitch, roll = calculate_look_at_with_safety(
            target_x=1.0,
            target_y=1.0,
            target_z=0.0,
            current_yaw=0.0,
            current_pitch=0.0,
            current_roll=0.0,
            progress=1.0,
        )
        # Should be ~45° yaw, 0° pitch
        assert 40 < yaw < 50
        assert abs(pitch) < 5

    def test_partial_movement(self):
        """Test partial movement (progress=0.5)."""
        yaw, pitch, roll = calculate_look_at_with_safety(
            target_x=1.0,
            target_y=1.0,
            target_z=0.0,
            current_yaw=0.0,
            current_pitch=0.0,
            current_roll=0.0,
            progress=0.5,
        )
        # Should be between current (0°) and target (~45°)
        assert 15 < yaw < 35

    def test_safety_limits_applied(self):
        """Test safety limits are enforced."""
        yaw, pitch, roll = calculate_look_at_with_safety(
            target_x=1.0,
            target_y=0.0,
            target_z=2.0,  # Very high up
            current_yaw=0.0,
            current_pitch=0.0,
            current_roll=0.0,
            progress=1.0,
        )
        # Pitch should be clamped to 40°
        assert pitch <= HEAD_PITCH_LIMIT

    def test_smooth_easing(self):
        """Test smooth easing is applied."""
        yaw1, _, _ = calculate_look_at_with_safety(
            target_x=1.0, target_y=1.0, target_z=0.0,
            current_yaw=0.0, current_pitch=0.0, current_roll=0.0,
            progress=0.25, easing="cubic"
        )
        yaw2, _, _ = calculate_look_at_with_safety(
            target_x=1.0, target_y=1.0, target_z=0.0,
            current_yaw=0.0, current_pitch=0.0, current_roll=0.0,
            progress=0.5, easing="cubic"
        )
        # Should show smooth progression
        assert 0 < yaw1 < yaw2


# ============================================================================
# Edge Case Tests
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_behind_robot(self):
        """Test looking behind the robot."""
        yaw, pitch, roll = calculate_look_at_angles(-1.0, 0.0, 0.0)
        # Should be ±180° yaw
        assert abs(abs(yaw) - 180.0) < 0.1

    def test_very_close_position(self):
        """Test position very close to robot."""
        yaw, pitch, roll = calculate_look_at_angles(0.1, 0.05, 0.0)
        # Should handle without errors
        assert -180 <= yaw <= 180
        assert -90 <= pitch <= 90

    def test_very_far_position(self):
        """Test position very far from robot."""
        yaw, pitch, roll = calculate_look_at_angles(100.0, 50.0, 10.0)
        # Should calculate reasonable angles
        assert -180 <= yaw <= 180
        assert -90 <= pitch <= 90

    def test_zero_position(self):
        """Test position at origin."""
        # Should handle gracefully (may return any angle)
        yaw, pitch, roll = calculate_look_at_angles(0.0, 0.0, 0.0)
        assert -180 <= yaw <= 180


# ============================================================================
# Test Markers
# ============================================================================

# Run with: pytest tests/test_kinematics.py -v
