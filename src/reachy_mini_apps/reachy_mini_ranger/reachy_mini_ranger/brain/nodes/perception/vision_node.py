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

from reachy_mini_ranger.brain.models.state import BrainState, Face, add_log, update_timestamp

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


def vision_node(state: BrainState) -> Dict[str, BrainState]:
    """Vision perception node for LangGraph.

    Processes camera frames to detect faces and updates BrainState.sensors.vision.

    Note:
        This is a placeholder implementation. In production:
        - Camera frames should come from ReachyMini media interface
        - FaceDetectionNode should be initialized once and reused
        - Frame acquisition should be optimized for real-time performance

    Args:
        state: Current BrainState

    Returns:
        Dictionary with updated BrainState containing face detections
    """
    updated = state.model_copy(deep=True)
    updated = add_log(updated, "Vision perception node executed (placeholder)")
    updated = update_timestamp(updated)

    # TODO: Integrate with ReachyMini camera
    # TODO: Initialize FaceDetectionNode as singleton
    # TODO: Process frame and update state.sensors.vision.faces
    # TODO: Calculate FPS and update state.sensors.vision.fps

    # Placeholder: Clear faces since we have no camera yet
    updated.sensors.vision.faces = []
    updated.sensors.vision.frame_timestamp = datetime.now()
    updated.sensors.vision.fps = 0.0

    return {"state": updated}
