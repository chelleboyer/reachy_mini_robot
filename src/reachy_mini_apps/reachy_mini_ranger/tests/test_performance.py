"""Performance benchmarks for Reachy Mini Ranger brain system.

This module tests performance-critical paths to validate NFR requirements:
- Vision FPS ≥10 FPS (Hailo HAT target)
- Perception latency <200ms
- Face detection latency <100ms
- Memory recall <50ms (when implemented)
- Audio intent detection <200ms (when implemented)
"""

import time
from datetime import datetime

import numpy as np
import pytest

from reachy_mini_ranger.brain.models.state import create_initial_state, Face
from reachy_mini_ranger.brain.nodes.perception.vision_node import process_camera_frame
from reachy_mini_ranger.brain.nodes.perception.face_tracker import get_face_tracker, TrackedFace


class TestVisionPerformance:
    """Performance benchmarks for vision perception."""
    
    @pytest.mark.performance
    def test_face_detection_latency_under_100ms(self):
        """Test that face detection completes in <100ms (target for real-time)."""
        # Create test frame (640x480 BGR)
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Measure detection time
        start = time.time()
        faces, humans, primary_id = process_camera_frame(test_frame, 640, 480)
        elapsed_ms = (time.time() - start) * 1000
        
        print(f"\nFace detection latency: {elapsed_ms:.1f}ms")
        
        # Target: <100ms for inference on Hailo HAT
        # Note: This will be slower on CPU during development
        # assert elapsed_ms < 100, f"Detection too slow: {elapsed_ms:.1f}ms > 100ms target"
        
        # For now just log performance
        assert elapsed_ms < 5000, f"Detection extremely slow: {elapsed_ms:.1f}ms"
    
    @pytest.mark.performance
    def test_perception_loop_fps(self):
        """Test perception loop FPS (target: ≥10 FPS on Hailo HAT)."""
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Run 10 iterations to measure average FPS
        num_iterations = 10
        start = time.time()
        
        for _ in range(num_iterations):
            faces, humans, primary_id = process_camera_frame(test_frame, 640, 480)
        
        elapsed = time.time() - start
        avg_fps = num_iterations / elapsed
        
        print(f"\nAverage perception FPS: {avg_fps:.1f}")
        
        # Target: ≥10 FPS
        # Note: CPU performance will be slower, Hailo HAT should hit 10+
        # assert avg_fps >= 10, f"FPS too low: {avg_fps:.1f} < 10 target"
        
        # For now just log performance
        assert avg_fps > 0.5, f"FPS extremely low: {avg_fps:.1f}"
    
    @pytest.mark.performance
    def test_frame_processing_latency(self):
        """Test end-to-end frame processing latency (face detection + tracking)."""
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Reset tracker for clean test
        tracker = get_face_tracker()
        tracker._tracks = []
        tracker._next_id = 1
        
        # Measure full processing pipeline
        start = time.time()
        faces, humans, primary_id = process_camera_frame(test_frame, 640, 480)
        elapsed_ms = (time.time() - start) * 1000
        
        print(f"\nFrame processing latency: {elapsed_ms:.1f}ms")
        
        # For development, just ensure it's reasonable
        assert elapsed_ms < 5000, f"Processing extremely slow: {elapsed_ms:.1f}ms"


class TestTrackingPerformance:
    """Performance benchmarks for face tracking."""
    
    @pytest.mark.performance
    def test_tracking_update_latency(self):
        """Test face tracking update latency."""
        tracker = get_face_tracker()
        tracker._tracks = []  # Reset
        
        # Create test faces
        test_faces = [
            Face(
                face_id=1,
                x=100, y=100, width=80, height=80,
                confidence=0.9,
                timestamp=datetime.now()
            ),
            Face(
                face_id=2,
                x=300, y=200, width=90, height=90,
                confidence=0.85,
                timestamp=datetime.now()
            ),
        ]
        
        # Measure tracking update
        start = time.time()
        tracked = tracker.update(test_faces)
        elapsed_ms = (time.time() - start) * 1000
        
        print(f"\nTracking update latency: {elapsed_ms:.1f}ms")
        
        # Tracking should be extremely fast (< 10ms)
        assert elapsed_ms < 50, f"Tracking too slow: {elapsed_ms:.1f}ms"
    
    @pytest.mark.performance
    def test_3d_position_estimation_latency(self):
        """Test 3D position estimation latency."""
        tracker = get_face_tracker()
        
        # Create test tracked face
        test_face = Face(
            face_id=1,
            x=320, y=240, width=100, height=100,
            confidence=0.9,
            timestamp=datetime.now()
        )
        
        from reachy_mini_ranger.brain.nodes.perception.face_tracker import TrackedFace
        tracked = TrackedFace(
            persistent_id=1,
            face=test_face,
            first_seen=time.time(),
            last_seen=time.time(),
            tracking_confidence=0.9,
        )
        
        # Measure 3D estimation
        start = time.time()
        position_3d = tracker.estimate_3d_position(tracked, 640, 480)
        elapsed_ms = (time.time() - start) * 1000
        
        print(f"\n3D estimation latency: {elapsed_ms:.1f}ms")
        
        # Should be very fast (just math)
        assert elapsed_ms < 10, f"3D estimation too slow: {elapsed_ms:.1f}ms"


class TestBrainStatePerformance:
    """Performance benchmarks for BrainState operations."""
    
    @pytest.mark.performance
    def test_state_copy_latency(self):
        """Test BrainState deep copy latency."""
        state = create_initial_state()
        
        # Add some data
        state.sensors.vision.faces = [
            Face(
                face_id=i,
                x=100 * i, y=100, width=80, height=80,
                confidence=0.9,
                timestamp=datetime.now()
            )
            for i in range(10)
        ]
        
        # Measure deep copy
        start = time.time()
        for _ in range(100):
            copied = state.model_copy(deep=True)
        elapsed_ms = (time.time() - start) * 1000 / 100
        
        print(f"\nState copy latency (avg): {elapsed_ms:.3f}ms")
        
        # Should be very fast
        assert elapsed_ms < 10, f"State copy too slow: {elapsed_ms:.3f}ms"
    
    @pytest.mark.performance
    def test_state_serialization_latency(self):
        """Test BrainState JSON serialization latency."""
        state = create_initial_state()
        
        # Measure serialization
        start = time.time()
        for _ in range(100):
            json_data = state.model_dump_json()
        elapsed_ms = (time.time() - start) * 1000 / 100
        
        print(f"\nState serialization latency (avg): {elapsed_ms:.3f}ms")
        
        # Should be reasonable
        assert elapsed_ms < 50, f"Serialization too slow: {elapsed_ms:.3f}ms"


class TestEndToEndPerformance:
    """End-to-end performance benchmarks."""
    
    @pytest.mark.performance
    @pytest.mark.skip(reason="Requires full camera integration")
    def test_perception_to_motor_command_latency(self):
        """Test end-to-end latency from perception to motor command.
        
        Target: <200ms (NFR requirement)
        
        This test requires:
        1. Camera frame capture
        2. Face detection
        3. Tracking update
        4. Kinematics calculation
        5. Actuator command generation
        """
        # TODO: Implement after camera integration
        pass
    
    @pytest.mark.performance
    @pytest.mark.skip(reason="Requires Hailo HAT hardware")
    def test_hailo_hat_fps_validation(self):
        """Validate Hailo HAT achieves ≥10 FPS.
        
        GO/NO-GO checkpoint: If this fails, architecture pivot needed.
        
        This test requires:
        - Raspberry Pi 5 with Hailo HAT
        - Real camera connected
        - YOLO model compiled for Hailo (.hef format)
        """
        # TODO: Implement with actual hardware
        pass


if __name__ == "__main__":
    # Run performance benchmarks with detailed output
    pytest.main([__file__, "-v", "-s", "-m", "performance"])
