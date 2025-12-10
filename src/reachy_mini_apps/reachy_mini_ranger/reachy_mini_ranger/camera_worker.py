"""Camera worker thread with face tracking for Reachy Mini Ranger.

Ported from reachy_mini_conversation_app to provide smooth face tracking
that runs independently of the main brain loop.

Architecture:
- Runs in separate thread at ~30 Hz
- Captures frames continuously
- Detects faces using YOLO
- Calculates head pose offsets using look_at_image()
- Main loop reads offsets and applies them
"""

import time
import logging
import threading
from typing import Optional, Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.spatial.transform import Rotation as R

from reachy_mini import ReachyMini
from reachy_mini_ranger.brain.nodes.perception.vision_node import get_face_detector

logger = logging.getLogger(__name__)


class CameraWorker:
    """Thread-safe camera worker with face tracking."""

    def __init__(self, reachy_mini: ReachyMini) -> None:
        """Initialize camera worker.
        
        Args:
            reachy_mini: ReachyMini instance for camera and head control
        """
        self.reachy_mini = reachy_mini
        self.face_detector = get_face_detector()

        # Thread-safe frame storage
        self.latest_frame: Optional[NDArray[np.uint8]] = None
        self.frame_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # Face tracking state
        self.is_head_tracking_enabled = True
        self.face_tracking_offsets: Tuple[float, float, float, float, float, float] = (
            0.0, 0.0, 0.0,  # x, y, z translation (meters)
            0.0, 0.0, 0.0,  # roll, pitch, yaw rotation (radians)
        )
        self.face_tracking_lock = threading.Lock()

        # Face tracking timing (for smooth return to neutral)
        self.last_face_detected_time: Optional[float] = None
        self.interpolation_start_time: Optional[float] = None
        self.interpolation_start_pose: Optional[NDArray[np.float32]] = None
        self.face_lost_delay = 1.5  # seconds to wait before returning to neutral
        self.interpolation_duration = 2.0  # seconds to interpolate back (slower, smoother)

        # Tracking statistics
        self.frames_processed = 0
        self.faces_detected = 0

    def get_latest_frame(self) -> Optional[NDArray[np.uint8]]:
        """Get the latest camera frame (thread-safe)."""
        with self.frame_lock:
            if self.latest_frame is None:
                return None
            return self.latest_frame.copy()

    def get_face_tracking_offsets(self) -> Tuple[float, float, float, float, float, float]:
        """Get current face tracking offsets (thread-safe).
        
        Returns:
            Tuple of (x, y, z, roll, pitch, yaw) offsets
        """
        with self.face_tracking_lock:
            return self.face_tracking_offsets

    def set_head_tracking_enabled(self, enabled: bool) -> None:
        """Enable/disable head tracking."""
        self.is_head_tracking_enabled = enabled
        logger.info(f"Head tracking {'enabled' if enabled else 'disabled'}")

    def start(self) -> None:
        """Start the camera worker loop in a thread."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._working_loop, daemon=True)
        self._thread.start()
        logger.info("Camera worker started")

    def stop(self) -> None:
        """Stop the camera worker loop."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        logger.info("Camera worker stopped")

    def _working_loop(self) -> None:
        """Main camera worker loop - runs continuously in separate thread."""
        logger.info("Camera worker loop started")
        
        neutral_pose = np.eye(4, dtype=np.float32)  # Neutral pose (identity matrix)
        previous_tracking_state = self.is_head_tracking_enabled

        while not self._stop_event.is_set():
            try:
                current_time = time.time()
                
                # Get frame from robot
                frame = self.reachy_mini.media.get_frame()
                
                if frame is None:
                    time.sleep(0.01)
                    continue

                # Store frame (thread-safe)
                with self.frame_lock:
                    self.latest_frame = frame

                self.frames_processed += 1

                # Check if tracking was just disabled
                if previous_tracking_state and not self.is_head_tracking_enabled:
                    # Trigger return to neutral
                    self.last_face_detected_time = current_time
                    self.interpolation_start_time = None
                    self.interpolation_start_pose = None

                previous_tracking_state = self.is_head_tracking_enabled

                # Handle face tracking if enabled
                if self.is_head_tracking_enabled:
                    h, w = frame.shape[:2]
                    
                    # Detect faces
                    detected_faces = self.face_detector.detect_faces(frame)
                    
                    if detected_faces:
                        # Use the first face (highest confidence)
                        face = detected_faces[0]
                        self.faces_detected += 1
                        
                        # Calculate face center in pixels
                        face_center_x = face.x + face.width / 2
                        face_center_y = face.y + face.height / 2

                        # Face detected - immediately switch to tracking
                        self.last_face_detected_time = current_time
                        self.interpolation_start_time = None

                        try:
                            # Use SDK's look_at_image to calculate target pose
                            target_pose = self.reachy_mini.look_at_image(
                                int(face_center_x),
                                int(face_center_y),
                                duration=0.0,
                                perform_movement=False,  # Just calculate, don't move
                            )

                            # Extract translation and rotation from the target pose
                            translation = target_pose[:3, 3]
                            rotation = R.from_matrix(target_pose[:3, :3]).as_euler("xyz", degrees=False)

                            # Apply exponential smoothing to reduce jitter (alpha=0.7 for responsiveness)
                            alpha = 0.7
                            with self.face_tracking_lock:
                                old_offsets = self.face_tracking_offsets
                                self.face_tracking_offsets = (
                                    alpha * float(translation[0]) + (1 - alpha) * old_offsets[0],
                                    alpha * float(translation[1]) + (1 - alpha) * old_offsets[1],
                                    alpha * float(translation[2]) + (1 - alpha) * old_offsets[2],
                                    alpha * float(rotation[0]) + (1 - alpha) * old_offsets[3],
                                    alpha * float(rotation[1]) + (1 - alpha) * old_offsets[4],
                                    alpha * float(rotation[2]) + (1 - alpha) * old_offsets[5],
                                )

                        except (AssertionError, RuntimeError) as e:
                            # Pixel out of bounds or camera issue - skip this frame
                            logger.debug(f"Face tracking calculation failed: {e}")

                # Handle smooth interpolation back to neutral when face is lost
                if self.last_face_detected_time is not None:
                    time_since_face_lost = current_time - self.last_face_detected_time

                    if time_since_face_lost >= self.face_lost_delay:
                        # Start interpolation if not already started
                        if self.interpolation_start_time is None:
                            self.interpolation_start_time = current_time
                            # Capture current pose as start of interpolation
                            with self.face_tracking_lock:
                                current_translation = self.face_tracking_offsets[:3]
                                current_rotation_euler = self.face_tracking_offsets[3:]
                                # Convert to 4x4 pose matrix
                                pose_matrix = np.eye(4, dtype=np.float32)
                                pose_matrix[:3, 3] = current_translation
                                pose_matrix[:3, :3] = R.from_euler(
                                    "xyz", current_rotation_euler
                                ).as_matrix()
                                self.interpolation_start_pose = pose_matrix

                        # Calculate interpolation progress (t from 0 to 1)
                        elapsed_interpolation = current_time - self.interpolation_start_time
                        t = min(1.0, elapsed_interpolation / self.interpolation_duration)

                        # Linear interpolation between current pose and neutral pose
                        from reachy_mini.utils.interpolation import linear_pose_interpolation
                        interpolated_pose = linear_pose_interpolation(
                            self.interpolation_start_pose, neutral_pose, t
                        )

                        # Extract translation and rotation from interpolated pose
                        translation = interpolated_pose[:3, 3]
                        rotation = R.from_matrix(interpolated_pose[:3, :3]).as_euler("xyz", degrees=False)

                        # Update face tracking offsets (thread-safe)
                        with self.face_tracking_lock:
                            self.face_tracking_offsets = (
                                float(translation[0]),
                                float(translation[1]),
                                float(translation[2]),
                                float(rotation[0]),
                                float(rotation[1]),
                                float(rotation[2]),
                            )

                        # If interpolation is complete, reset timing
                        if t >= 1.0:
                            self.last_face_detected_time = None
                            self.interpolation_start_time = None
                            self.interpolation_start_pose = None

                # Small sleep to prevent excessive CPU usage (~30 Hz to feed 100 Hz control)
                time.sleep(0.033)

            except Exception as e:
                logger.error(f"Camera worker error: {e}", exc_info=True)
                time.sleep(0.1)  # Longer sleep on error

        logger.info(f"Camera worker exited. Processed {self.frames_processed} frames, detected {self.faces_detected} faces")
