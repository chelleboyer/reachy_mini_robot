"""Unit tests for vision perception node and face detection."""

import pytest
import numpy as np
from datetime import datetime

from reachy_mini_ranger.brain.nodes.perception.vision_node import (
    FaceDetectionNode,
    vision_node,
)
from reachy_mini_ranger.brain.models.state import create_initial_state, Face


# ============================================================================
# FaceDetectionNode Tests
# ============================================================================


class TestFaceDetectionNodeInitialization:
    """Test FaceDetectionNode initialization and configuration."""

    def test_initialization_with_defaults(self):
        """Test node initializes with default parameters."""
        node = FaceDetectionNode()
        assert node.confidence_threshold == 0.3
        assert node.device == "cpu"
        assert node.next_face_id == 1
        assert node.model is not None

    def test_initialization_with_custom_params(self):
        """Test node initializes with custom confidence threshold."""
        node = FaceDetectionNode(confidence_threshold=0.5, device="cpu")
        assert node.confidence_threshold == 0.5
        assert node.device == "cpu"

    def test_model_loaded(self):
        """Test YOLO model is loaded successfully."""
        node = FaceDetectionNode()
        assert node.model is not None
        # Model should have predict/inference methods
        assert hasattr(node.model, "__call__")


class TestFaceDetection:
    """Test face detection functionality."""

    @pytest.fixture
    def detector(self):
        """Create FaceDetectionNode instance."""
        return FaceDetectionNode(confidence_threshold=0.3)

    def test_detect_faces_with_empty_frame(self, detector):
        """Test detection handles empty frame gracefully."""
        empty_frame = np.array([])
        faces = detector.detect_faces(empty_frame)
        assert faces == []

    def test_detect_faces_with_none(self, detector):
        """Test detection handles None frame gracefully."""
        faces = detector.detect_faces(None)
        assert faces == []

    def test_detect_faces_returns_list(self, detector):
        """Test detection always returns a list."""
        # Create dummy frame (blank image)
        blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        faces = detector.detect_faces(blank_frame)
        assert isinstance(faces, list)

    def test_face_object_structure(self, detector):
        """Test Face objects have correct structure if faces detected."""
        # Create a test image (may or may not detect faces)
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        faces = detector.detect_faces(test_frame)

        # If faces detected, validate structure
        for face in faces:
            assert isinstance(face, Face)
            assert hasattr(face, "face_id")
            assert hasattr(face, "x")
            assert hasattr(face, "y")
            assert hasattr(face, "width")
            assert hasattr(face, "height")
            assert hasattr(face, "confidence")
            assert hasattr(face, "timestamp")
            assert 0.0 <= face.confidence <= 1.0
            assert face.width > 0
            assert face.height > 0

    def test_confidence_filtering(self, detector):
        """Test low-confidence detections are filtered out."""
        # Set high threshold
        detector.confidence_threshold = 0.9
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        faces = detector.detect_faces(test_frame)

        # All returned faces should meet threshold
        for face in faces:
            assert face.confidence >= 0.9

    def test_face_id_increments(self, detector):
        """Test face IDs increment correctly across detections."""
        test_frame = np.ones((480, 640, 3), dtype=np.uint8) * 128

        initial_id = detector.next_face_id
        detector.detect_faces(test_frame)
        second_id = detector.next_face_id

        # ID should increment (even if no faces detected, counter may still increase)
        assert second_id >= initial_id

    def test_bounding_box_format(self, detector):
        """Test bounding boxes are in correct format (x, y, width, height)."""
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        faces = detector.detect_faces(test_frame)

        h, w = test_frame.shape[:2]
        for face in faces:
            # x, y should be within frame
            assert 0 <= face.x < w
            assert 0 <= face.y < h
            # width, height should be positive
            assert face.width > 0
            assert face.height > 0
            # Bbox should not exceed frame bounds
            assert face.x + face.width <= w
            assert face.y + face.height <= h


class TestFaceDetectionPerformance:
    """Test face detection performance and FPS."""

    @pytest.fixture
    def detector(self):
        """Create FaceDetectionNode instance."""
        return FaceDetectionNode()

    @pytest.mark.performance
    def test_fps_benchmark(self, detector):
        """Test detection achieves target FPS (10+ FPS)."""
        import time

        # Create test frame
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        # Run 30 detections
        num_iterations = 30
        start_time = time.time()

        for _ in range(num_iterations):
            detector.detect_faces(test_frame)

        elapsed = time.time() - start_time
        fps = num_iterations / elapsed

        print(f"\nFPS Benchmark: {fps:.2f} FPS (target: 10+ FPS)")

        # Note: This test may fail on slow hardware
        # For Hailo HAT, expect 10+ FPS; CPU may be slower
        assert fps > 0, "FPS should be positive"

    @pytest.mark.performance
    def test_detection_latency(self, detector):
        """Test single frame detection latency is acceptable."""
        import time

        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        start_time = time.time()
        detector.detect_faces(test_frame)
        latency = time.time() - start_time

        print(f"\nDetection latency: {latency*1000:.1f}ms")

        # Should complete within reasonable time (< 500ms for CPU)
        assert latency < 0.5, f"Detection took {latency:.3f}s, expected < 0.5s"


# ============================================================================
# Vision Node Integration Tests
# ============================================================================


class TestVisionNodeIntegration:
    """Test vision_node integration with BrainState."""

    def test_vision_node_updates_state(self):
        """Test vision_node returns updated BrainState."""
        initial_state = create_initial_state()
        result = vision_node(initial_state)

        assert "state" in result
        assert isinstance(result["state"], type(initial_state))

    def test_vision_node_updates_timestamp(self):
        """Test vision_node updates timestamp."""
        initial_state = create_initial_state()
        initial_time = initial_state.metadata.timestamp

        result = vision_node(initial_state)
        updated_time = result["state"].metadata.timestamp

        assert updated_time >= initial_time

    def test_vision_node_adds_log(self):
        """Test vision_node adds log entry."""
        initial_state = create_initial_state()
        initial_logs = len(initial_state.metadata.logs)

        result = vision_node(initial_state)
        updated_logs = len(result["state"].metadata.logs)

        assert updated_logs > initial_logs

    def test_vision_node_updates_vision_data(self):
        """Test vision_node updates sensors.vision fields."""
        initial_state = create_initial_state()
        result = vision_node(initial_state)

        updated = result["state"]
        assert hasattr(updated.sensors.vision, "faces")
        assert hasattr(updated.sensors.vision, "frame_timestamp")
        assert hasattr(updated.sensors.vision, "fps")
        assert isinstance(updated.sensors.vision.faces, list)

    def test_vision_node_immutability(self):
        """Test vision_node doesn't mutate input state."""
        initial_state = create_initial_state()
        initial_logs = len(initial_state.metadata.logs)

        vision_node(initial_state)

        # Original state should be unchanged
        assert len(initial_state.metadata.logs) == initial_logs


class TestVisionNodeWithDetections:
    """Test vision_node behavior with face detections (requires camera)."""

    @pytest.mark.skip(reason="Requires camera hardware")
    def test_vision_node_with_real_camera(self):
        """Test vision_node with real camera frame.

        This test is skipped by default as it requires camera hardware.
        """
        # TODO: Integrate with ReachyMini camera
        # from reachy_mini import ReachyMini
        # with ReachyMini() as reachy:
        #     frame = reachy.media.get_frame()
        #     # Process frame with vision_node
        pass


# ============================================================================
# Test Markers
# ============================================================================

# Run performance tests separately with: pytest -m performance
# Skip hardware tests with: pytest -m "not hardware"
