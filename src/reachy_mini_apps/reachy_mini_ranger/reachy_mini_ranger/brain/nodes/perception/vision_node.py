"""Vision perception node for face detection using YOLO.

This module implements face detection using YOLO model from Hugging Face.
For Hailo HAT acceleration, the model should be converted to Hailo format (.hef).

Currently implements CPU-based YOLO inference as a starting point.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Dict

import numpy as np
from numpy.typing import NDArray

from reachy_mini_ranger.brain.models.state import (
    BrainState,
    Face,
    Human,
    Position3D,
    add_log,
    update_timestamp,
)
from reachy_mini_ranger.brain.nodes.perception.face_tracker import FaceTracker

try:
    from supervision import Detections
    from ultralytics import YOLO
except ImportError as e:
    raise ImportError(
        "YOLO dependencies not installed. Install with: pip install ultralytics supervision"
    ) from e

try:
    from huggingface_hub import hf_hub_download
except ImportError as e:
    raise ImportError("Install huggingface_hub with: pip install huggingface_hub") from e


logger = logging.getLogger(__name__)


class FaceDetectionNode:
    """Face detection using YOLO model with optional Hailo HAT acceleration.

    This class handles face detection from camera frames. Initially uses CPU-based
    YOLO inference. For production deployment on Raspberry Pi 5 with Hailo HAT,
    the model can be converted to Hailo format (.hef) for hardware acceleration.

    Attributes:
        model: YOLO face detection model
        confidence_threshold: Minimum confidence for valid detections
        device: Device for inference ('cpu', 'cuda', or 'hailo')
        next_face_id: Counter for assigning unique face IDs
    """

    def __init__(
        self,
        model_repo: str = "AdamCodd/YOLOv11n-face-detection",
        model_filename: str = "model.pt",
        confidence_threshold: float = 0.3,
        device: str = "cpu",
    ):
        """Initialize face detection node.

        Args:
            model_repo: HuggingFace model repository for YOLO face detection
            model_filename: Model file name in the repository
            confidence_threshold: Minimum confidence score (0.0-1.0)
            device: Target device ('cpu', 'cuda', or 'hailo')

        Raises:
            ImportError: If required dependencies are not installed
            RuntimeError: If model loading fails
        """
        self.confidence_threshold = confidence_threshold
        self.device = device
        self.next_face_id = 1

        try:
            # Download YOLO model from Hugging Face
            logger.info(f"Downloading YOLO model from {model_repo}")
            model_path = hf_hub_download(repo_id=model_repo, filename=model_filename)

            # Load model
            self.model = YOLO(model_path).to(device)
            logger.info(f"YOLO face detection initialized on {device}")

        except Exception as e:
            logger.error(f"Failed to initialize face detection: {e}")
            raise RuntimeError(f"Face detection initialization failed: {e}") from e

    def detect_faces(self, frame: NDArray[np.uint8]) -> list[Face]:
        """Detect faces in a camera frame.

        Args:
            frame: BGR image array from camera (H, W, 3)

        Returns:
            List of Face objects with bounding boxes and confidence scores.
            Empty list if no faces detected.

        Note:
            Coordinates are in pixel space. Confidence filtering applied.
        """
        if frame is None or frame.size == 0:
            logger.warning("Empty frame provided to detect_faces")
            return []

        h, w = frame.shape[:2]

        try:
            # Run YOLO inference (verbose=False to reduce logging)
            results = self.model(frame, verbose=False)
            detections = Detections.from_ultralytics(results[0])

            # Filter by confidence threshold
            if detections.confidence is None or len(detections.xyxy) == 0:
                logger.debug("No faces detected")
                return []

            valid_mask = detections.confidence >= self.confidence_threshold
            if not np.any(valid_mask):
                logger.debug(f"No faces above confidence threshold {self.confidence_threshold}")
                return []

            # Convert detections to Face objects
            faces: list[Face] = []
            valid_indices = np.where(valid_mask)[0]

            for idx in valid_indices:
                bbox = detections.xyxy[idx]  # [x1, y1, x2, y2]
                conf = float(detections.confidence[idx])

                # Convert to (x, y, width, height) format
                x = float(bbox[0])
                y = float(bbox[1])
                width = float(bbox[2] - bbox[0])
                height = float(bbox[3] - bbox[1])

                # Create Face object
                face = Face(
                    face_id=self.next_face_id,
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    confidence=conf,
                    timestamp=datetime.now(),
                )
                faces.append(face)
                self.next_face_id += 1

                logger.debug(
                    f"Face {face.face_id}: bbox=({x:.1f},{y:.1f},{width:.1f},{height:.1f}), "
                    f"conf={conf:.2f}"
                )

            return faces

        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return []


# Module-level singletons for face detection and tracking
_face_detector: Optional[FaceDetectionNode] = None
_face_tracker: Optional[FaceTracker] = None


def get_face_detector() -> FaceDetectionNode:
    """Get or create singleton face detector."""
    global _face_detector
    if _face_detector is None:
        # Higher confidence threshold for more stable detections
        _face_detector = FaceDetectionNode(confidence_threshold=0.5)
    return _face_detector


def get_face_tracker() -> FaceTracker:
    """Get or create singleton face tracker."""
    global _face_tracker
    if _face_tracker is None:
        _face_tracker = FaceTracker(max_distance=100.0, track_timeout=2.0)
    return _face_tracker


def vision_node(state: BrainState, reachy_mini=None) -> BrainState:
    """Vision perception node - processes camera frames for face detection.
    
    Integrates with ReachyMini SDK to capture camera frames, detect faces with YOLO,
    track faces across frames, and estimate 3D positions.
    
    Args:
        state: Current brain state
        reachy_mini: ReachyMini instance (optional, for camera access)
    
    Returns:
        Updated brain state with detected faces and tracked humans
    """
    updated = state.model_copy(deep=True)
    
    # If no camera provided, return empty data (for testing without hardware)
    if reachy_mini is None:
        updated.sensors.vision.faces = []
        updated.sensors.vision.frame_timestamp = datetime.now()
        updated.sensors.vision.fps = 0.0
        updated.world_model.humans = []
        updated = add_log(updated, "Vision: no camera provided (test mode)")
        updated = update_timestamp(updated)
        return updated
    
    # Check if camera is initialized
    if reachy_mini.media.camera is None:
        updated.sensors.vision.faces = []
        updated.sensors.vision.frame_timestamp = datetime.now()
        updated.sensors.vision.fps = 0.0
        updated.world_model.humans = []
        updated = add_log(updated, "Vision: camera not initialized")
        updated = update_timestamp(updated)
        return updated
    
    # Get frame from camera via SDK
    frame = reachy_mini.media.get_frame()
    
    if frame is None:
        updated.sensors.vision.faces = []
        updated.sensors.vision.frame_timestamp = datetime.now()
        updated.sensors.vision.fps = 0.0
        updated.world_model.humans = []
        updated = add_log(updated, "Vision: failed to capture frame")
        updated = update_timestamp(updated)
        return updated
    
    # Get frame dimensions
    frame_height, frame_width = frame.shape[:2]
    
    # DEBUG: Log frame size once every 100 frames
    if not hasattr(vision_node, '_frame_count'):
        vision_node._frame_count = 0
        logger.info(f"Camera frame size: {frame_width}x{frame_height}")
    vision_node._frame_count += 1
    
    # Process frame with face detection and tracking
    start_time = time.time()
    detected_faces, tracked_humans, primary_id = process_camera_frame(
        frame, frame_width, frame_height
    )
    processing_time = time.time() - start_time
    
    # Calculate FPS (1 / processing time)
    fps = 1.0 / processing_time if processing_time > 0 else 0.0
    
    # Update state
    updated.sensors.vision.faces = detected_faces
    updated.sensors.vision.frame_timestamp = datetime.now()
    updated.sensors.vision.fps = fps
    updated.world_model.humans = tracked_humans
    
    # Log result
    num_faces = len(detected_faces)
    num_humans = len(tracked_humans)
    primary_str = f", primary={primary_id}" if primary_id is not None else ""
    updated = add_log(
        updated, 
        f"Vision: {num_faces} face(s), {num_humans} human(s){primary_str}, {fps:.1f} FPS"
    )
    updated = update_timestamp(updated)
    
    return updated


def process_camera_frame(
    frame: NDArray[np.uint8],
    frame_width: int,
    frame_height: int,
) -> tuple[list[Face], list[Human], Optional[int]]:
    """Process camera frame with face detection and tracking.
    
    This function is ready for production use when camera integration is complete.
    
    Args:
        frame: BGR image from camera
        frame_width: Frame width in pixels
        frame_height: Frame height in pixels
        
    Returns:
        Tuple of (detected_faces, tracked_humans, primary_face_id)
    """
    detector = get_face_detector()
    tracker = get_face_tracker()
    
    # Detect faces
    detected_faces = detector.detect_faces(frame)
    
    # Update tracker with detections
    tracked_faces = tracker.update(detected_faces)
    
    # Convert tracked faces to Human objects with 3D positions
    humans: list[Human] = []
    for track in tracked_faces:
        position_3d = tracker.estimate_3d_position(track, frame_width, frame_height)
        human = Human(
            human_id=track.persistent_id,
            persistent_id=track.persistent_id,
            position=position_3d,
            face_id=track.face.face_id,
            last_seen=datetime.fromtimestamp(track.last_seen),
            tracking_confidence=track.tracking_confidence,
            is_primary=False,  # Will be set below
        )
        humans.append(human)
    
    # Select primary face
    primary_id = tracker.select_primary_face(tracked_faces, frame_width, frame_height)
    
    # Mark primary human
    if primary_id is not None:
        for human in humans:
            if human.persistent_id == primary_id:
                human.is_primary = True
                break
    
    return detected_faces, humans, primary_id
