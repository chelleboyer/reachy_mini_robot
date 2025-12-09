"""Unit tests for face tracking with persistent IDs."""

import pytest
import numpy as np
import time
from datetime import datetime

from reachy_mini_ranger.brain.nodes.perception.face_tracker import (
    FaceTracker,
    TrackedFace,
)
from reachy_mini_ranger.brain.nodes.perception.vision_node import process_camera_frame
from reachy_mini_ranger.brain.models.state import Face, Position3D


# ============================================================================
# Helper Functions
# ============================================================================


def create_test_face(x: float, y: float, width: float, height: float, confidence: float = 0.8) -> Face:
    """Create a test Face object."""
    return Face(
        face_id=1,
        x=x,
        y=y,
        width=width,
        height=height,
        confidence=confidence,
        timestamp=datetime.now(),
    )


# ============================================================================
# FaceTracker Initialization Tests
# ============================================================================


class TestFaceTrackerInitialization:
    """Test FaceTracker initialization."""

    def test_initialization_defaults(self):
        """Test tracker initializes with default parameters."""
        tracker = FaceTracker()
        assert tracker.max_distance == 100.0
        assert tracker.track_timeout == 2.0
        assert tracker.next_id == 1
        assert len(tracker.tracks) == 0

    def test_initialization_custom_params(self):
        """Test tracker initializes with custom parameters."""
        tracker = FaceTracker(max_distance=50.0, track_timeout=3.0)
        assert tracker.max_distance == 50.0
        assert tracker.track_timeout == 3.0


# ============================================================================
# Face Tracking Tests
# ============================================================================


class TestFaceTracking:
    """Test face tracking functionality."""

    @pytest.fixture
    def tracker(self):
        """Create FaceTracker instance."""
        return FaceTracker(max_distance=100.0, track_timeout=2.0)

    def test_first_detection_creates_track(self, tracker):
        """Test first detection creates new track."""
        face = create_test_face(100, 100, 50, 50)
        tracked = tracker.update([face])
        
        assert len(tracked) == 1
        assert tracked[0].persistent_id == 1
        assert tracked[0].frames_tracked == 1

    def test_multiple_detections_create_tracks(self, tracker):
        """Test multiple faces create multiple tracks."""
        faces = [
            create_test_face(100, 100, 50, 50),
            create_test_face(300, 200, 60, 60),
            create_test_face(500, 150, 55, 55),
        ]
        tracked = tracker.update(faces)
        
        assert len(tracked) == 3
        assert set(t.persistent_id for t in tracked) == {1, 2, 3}

    def test_id_persistence_across_frames(self, tracker):
        """Test face IDs persist across frames (30+ frames)."""
        # Frame 1: Create initial track
        face1 = create_test_face(100, 100, 50, 50)
        tracked = tracker.update([face1])
        initial_id = tracked[0].persistent_id
        
        # Frames 2-31: Move face slightly, should maintain ID
        for i in range(30):
            # Simulate slight movement (within max_distance)
            face = create_test_face(100 + i, 100 + i, 50, 50)
            tracked = tracker.update([face])
            
            assert len(tracked) == 1
            assert tracked[0].persistent_id == initial_id
            assert tracked[0].frames_tracked == i + 2

    def test_similar_position_matched(self, tracker):
        """Test faces at similar positions are matched."""
        # Frame 1
        face1 = create_test_face(200, 200, 50, 50)
        tracked = tracker.update([face1])
        id1 = tracked[0].persistent_id
        
        # Frame 2: Slightly moved (within threshold)
        face2 = create_test_face(210, 205, 50, 50)
        tracked = tracker.update([face2])
        
        assert len(tracked) == 1
        assert tracked[0].persistent_id == id1

    def test_distant_position_creates_new_track(self, tracker):
        """Test faces far apart create separate tracks."""
        # Frame 1
        face1 = create_test_face(100, 100, 50, 50)
        tracker.update([face1])
        
        # Frame 2: Face at distant location (beyond max_distance)
        face2 = create_test_face(500, 500, 50, 50)
        tracked = tracker.update([face2])
        
        # Should have 2 tracks (one stale, one active in returned list)
        # But update only returns active, so we check tracker state
        assert tracker.get_track_count() == 2


# ============================================================================
# Track Expiration Tests
# ============================================================================


class TestTrackExpiration:
    """Test stale track expiration."""

    def test_stale_track_expires(self):
        """Test track expires after timeout."""
        tracker = FaceTracker(track_timeout=0.5)  # 0.5s timeout for faster test
        
        # Create initial track
        face = create_test_face(100, 100, 50, 50)
        tracker.update([face])
        assert tracker.get_track_count() == 1
        
        # Wait for timeout
        time.sleep(0.6)
        
        # Update with no detections
        tracker.update([])
        
        # Track should be expired
        assert tracker.get_track_count() == 0

    def test_active_track_not_expired(self):
        """Test active track is not expired."""
        tracker = FaceTracker(track_timeout=1.0)
        
        # Create track and keep updating
        for i in range(5):
            face = create_test_face(100 + i * 5, 100, 50, 50)
            tracked = tracker.update([face])
            assert len(tracked) == 1
            time.sleep(0.1)
        
        # Track should still be active
        assert tracker.get_track_count() == 1


# ============================================================================
# 3D Position Estimation Tests
# ============================================================================


class TestPositionEstimation:
    """Test 3D position estimation."""

    @pytest.fixture
    def tracker(self):
        """Create FaceTracker instance."""
        return FaceTracker()

    def test_position_estimation_returns_position3d(self, tracker):
        """Test position estimation returns Position3D."""
        face = create_test_face(320, 240, 100, 100)
        tracked = tracker.update([face])[0]
        
        position = tracker.estimate_3d_position(tracked, 640, 480)
        
        assert isinstance(position, Position3D)
        assert hasattr(position, "x")
        assert hasattr(position, "y")
        assert hasattr(position, "z")

    def test_larger_bbox_closer_depth(self, tracker):
        """Test larger bounding boxes result in closer depth estimates."""
        # Large face (closer)
        face_close = create_test_face(200, 200, 200, 200)
        tracked_close = tracker.update([face_close])[0]
        pos_close = tracker.estimate_3d_position(tracked_close, 640, 480)
        
        tracker.reset()
        
        # Small face (farther)
        face_far = create_test_face(200, 200, 50, 50)
        tracked_far = tracker.update([face_far])[0]
        pos_far = tracker.estimate_3d_position(tracked_far, 640, 480)
        
        # Closer face should have smaller z (depth)
        assert pos_close.z < pos_far.z

    def test_depth_clamping(self, tracker):
        """Test depth is clamped to reasonable range."""
        # Tiny face (would estimate very far)
        face_tiny = create_test_face(300, 200, 5, 5)
        tracked = tracker.update([face_tiny])[0]
        position = tracker.estimate_3d_position(tracked, 640, 480)
        
        # Should be clamped to max 5.0m
        assert position.z <= 5.0
        
        tracker.reset()
        
        # Huge face (would estimate very close)
        face_huge = create_test_face(100, 100, 500, 500)
        tracked = tracker.update([face_huge])[0]
        position = tracker.estimate_3d_position(tracked, 640, 480)
        
        # Should be clamped to min 0.3m
        assert position.z >= 0.3

    def test_center_face_zero_x(self, tracker):
        """Test face at frame center has approximately zero x coordinate."""
        # Face at exact center
        face = create_test_face(295, 215, 50, 50)  # Center at (320, 240)
        tracked = tracker.update([face])[0]
        position = tracker.estimate_3d_position(tracked, 640, 480)
        
        # x should be close to 0 (within tolerance)
        assert abs(position.x) < 0.1


# ============================================================================
# Primary Face Selection Tests
# ============================================================================


class TestPrimaryFaceSelection:
    """Test primary face identification."""

    @pytest.fixture
    def tracker(self):
        """Create FaceTracker instance."""
        return FaceTracker()

    def test_single_face_is_primary(self, tracker):
        """Test single face is selected as primary."""
        face = create_test_face(200, 200, 50, 50)
        tracked = tracker.update([face])
        
        primary_id = tracker.select_primary_face(tracked, 640, 480)
        
        assert primary_id is not None
        assert primary_id == tracked[0].persistent_id

    def test_central_face_preferred(self, tracker):
        """Test face closer to center is preferred."""
        faces = [
            create_test_face(50, 50, 50, 50),      # Corner
            create_test_face(295, 215, 50, 50),    # Center (320, 240)
            create_test_face(550, 400, 50, 50),    # Other corner
        ]
        tracked = tracker.update(faces)
        
        primary_id = tracker.select_primary_face(tracked, 640, 480)
        
        # Center face should be primary
        center_track = [t for t in tracked if abs(t.centroid[0] - 320) < 30][0]
        assert primary_id == center_track.persistent_id

    def test_larger_face_preferred(self, tracker):
        """Test larger face (closer) is preferred when centrality similar."""
        faces = [
            create_test_face(280, 200, 50, 50),    # Small, near center
            create_test_face(300, 220, 150, 150),  # Large, near center
        ]
        tracked = tracker.update(faces)
        
        primary_id = tracker.select_primary_face(tracked, 640, 480)
        
        # Larger face should be primary
        large_track = [t for t in tracked if t.face.width > 100][0]
        assert primary_id == large_track.persistent_id

    def test_no_faces_returns_none(self, tracker):
        """Test no faces returns None for primary."""
        primary_id = tracker.select_primary_face([], 640, 480)
        assert primary_id is None


# ============================================================================
# Multi-Face Tracking Tests
# ============================================================================


class TestMultiFaceTracking:
    """Test tracking multiple faces simultaneously."""

    def test_track_multiple_faces(self):
        """Test tracking 3 faces simultaneously."""
        tracker = FaceTracker()
        
        faces = [
            create_test_face(100, 100, 50, 50),
            create_test_face(300, 200, 60, 60),
            create_test_face(500, 150, 55, 55),
        ]
        
        # Update for 10 frames
        for _ in range(10):
            tracked = tracker.update(faces)
            assert len(tracked) == 3
            
            # Move faces slightly
            for face in faces:
                face.x += 2
                face.y += 1

    def test_face_appearance_and_disappearance(self):
        """Test faces appearing and disappearing."""
        tracker = FaceTracker(track_timeout=0.5)
        
        # Frame 1: 2 faces
        faces1 = [
            create_test_face(100, 100, 50, 50),
            create_test_face(300, 200, 60, 60),
        ]
        tracked = tracker.update(faces1)
        assert len(tracked) == 2
        ids1 = {t.persistent_id for t in tracked}
        
        # Frame 2: 1 face disappears, 1 new appears
        faces2 = [
            create_test_face(105, 105, 50, 50),  # Same as first
            create_test_face(500, 150, 55, 55),  # New face
        ]
        tracked = tracker.update(faces2)
        assert len(tracked) == 3  # 2 active + 1 stale
        
        # Wait for timeout
        time.sleep(0.6)
        
        # Frame 3: Stale track should expire
        tracked = tracker.update([faces2[0]])
        assert len(tracked) <= 2  # Stale expired


# ============================================================================
# Tracker Reset Tests
# ============================================================================


class TestTrackerReset:
    """Test tracker reset functionality."""

    def test_reset_clears_tracks(self):
        """Test reset clears all tracks."""
        tracker = FaceTracker()
        
        # Create multiple tracks
        faces = [
            create_test_face(100, 100, 50, 50),
            create_test_face(300, 200, 60, 60),
        ]
        tracker.update(faces)
        assert tracker.get_track_count() == 2
        
        # Reset
        tracker.reset()
        
        assert tracker.get_track_count() == 0
        assert tracker.next_id == 1

    def test_reset_allows_fresh_start(self):
        """Test tracking works after reset."""
        tracker = FaceTracker()
        
        # Create and reset
        face1 = create_test_face(100, 100, 50, 50)
        tracker.update([face1])
        tracker.reset()
        
        # New face after reset should get ID 1
        face2 = create_test_face(200, 200, 50, 50)
        tracked = tracker.update([face2])
        
        assert len(tracked) == 1
        assert tracked[0].persistent_id == 1


# ============================================================================
# Integration Tests
# ============================================================================


class TestProcessCameraFrame:
    """Test process_camera_frame integration function."""

    def test_process_frame_returns_tuple(self):
        """Test process_camera_frame returns expected tuple."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        result = process_camera_frame(frame, 640, 480)
        
        assert isinstance(result, tuple)
        assert len(result) == 3
        detected_faces, humans, primary_id = result
        assert isinstance(detected_faces, list)
        assert isinstance(humans, list)

    @pytest.mark.skip(reason="Requires YOLO model download")
    def test_process_frame_with_mock_detections(self):
        """Test process_camera_frame with simulated detections."""
        # This test would require mocking the face detector
        # Skipped for now as it requires model download
        pass


# ============================================================================
# Test Markers
# ============================================================================

# Run with: pytest tests/test_face_tracker.py -v
