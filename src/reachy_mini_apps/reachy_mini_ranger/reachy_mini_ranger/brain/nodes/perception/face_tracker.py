"""Face tracking with persistent IDs across frames.

This module implements centroid-based face tracking to maintain consistent
identities for detected faces across video frames. Tracks are expired after
a configurable timeout to handle faces leaving the scene.

Algorithm:
    - Centroid Tracking: Match faces based on minimum distance between centroids
    - ID Persistence: Maintain unique IDs across frames
    - Stale Track Expiration: Remove tracks not seen for N seconds
    - 3D Position Estimation: Estimate depth from bbox size
    - Primary Face Selection: Score by centrality + size + confidence
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from reachy_mini_ranger.brain.models.state import Face, Position3D


logger = logging.getLogger(__name__)


@dataclass
class TrackedFace:
    """A face with persistent tracking information.
    
    Attributes:
        persistent_id: Unique ID maintained across frames
        face: Current face detection
        centroid: Face center (x, y) in pixels
        last_seen: Timestamp of last detection
        tracking_confidence: Confidence in track (0.0-1.0)
        frames_tracked: Number of consecutive frames tracked
    """
    persistent_id: int
    face: Face
    centroid: NDArray[np.float32]
    last_seen: float
    tracking_confidence: float = 1.0
    frames_tracked: int = 1


class FaceTracker:
    """Centroid-based face tracker with persistent IDs.
    
    Maintains consistent face IDs across frames using centroid distance matching.
    Automatically expires stale tracks and estimates 3D positions.
    
    Attributes:
        max_distance: Maximum centroid distance for match (pixels)
        track_timeout: Time before track expires (seconds)
        next_id: Counter for assigning new persistent IDs
        tracks: Active tracked faces
    """

    def __init__(
        self,
        max_distance: float = 100.0,
        track_timeout: float = 2.0,
    ):
        """Initialize face tracker.
        
        Args:
            max_distance: Maximum centroid distance for matching (pixels)
            track_timeout: Time before expiring stale tracks (seconds)
        """
        self.max_distance = max_distance
        self.track_timeout = track_timeout
        self.next_id = 1
        self.tracks: dict[int, TrackedFace] = {}

    def update(self, faces: list[Face]) -> list[TrackedFace]:
        """Update tracks with new face detections.
        
        Args:
            faces: List of detected faces from current frame
            
        Returns:
            List of tracked faces with persistent IDs
        """
        current_time = time.time()
        
        # Compute centroids for new detections
        detection_centroids = []
        for face in faces:
            cx = face.x + face.width / 2
            cy = face.y + face.height / 2
            detection_centroids.append(np.array([cx, cy], dtype=np.float32))
        
        # Match detections to existing tracks
        matched_tracks = set()
        matched_detections = set()
        
        if len(self.tracks) > 0 and len(detection_centroids) > 0:
            # Build distance matrix between tracks and detections
            track_ids = list(self.tracks.keys())
            track_centroids = np.array([self.tracks[tid].centroid for tid in track_ids])
            detection_array = np.array(detection_centroids)
            
            # Compute pairwise distances
            distances = np.linalg.norm(
                track_centroids[:, np.newaxis] - detection_array[np.newaxis, :],
                axis=2
            )
            
            # Greedy matching: assign closest pairs under threshold
            while True:
                if distances.size == 0:
                    break
                    
                min_idx = np.unravel_index(distances.argmin(), distances.shape)
                min_dist = distances[min_idx]
                
                if min_dist > self.max_distance:
                    break
                
                track_idx, det_idx = min_idx
                track_id = track_ids[track_idx]
                
                # Update matched track
                self.tracks[track_id].face = faces[det_idx]
                self.tracks[track_id].centroid = detection_centroids[det_idx]
                self.tracks[track_id].last_seen = current_time
                self.tracks[track_id].frames_tracked += 1
                self.tracks[track_id].tracking_confidence = min(
                    1.0,
                    self.tracks[track_id].tracking_confidence + 0.05
                )
                
                matched_tracks.add(track_id)
                matched_detections.add(det_idx)
                
                # Remove matched pair from consideration
                distances[track_idx, :] = np.inf
                distances[:, det_idx] = np.inf
        
        # Create new tracks for unmatched detections
        for i, face in enumerate(faces):
            if i not in matched_detections:
                new_track = TrackedFace(
                    persistent_id=self.next_id,
                    face=face,
                    centroid=detection_centroids[i],
                    last_seen=current_time,
                    tracking_confidence=face.confidence,
                    frames_tracked=1,
                )
                self.tracks[self.next_id] = new_track
                matched_tracks.add(self.next_id)
                self.next_id += 1
                logger.debug(f"New track created: ID {new_track.persistent_id}")
        
        # Expire stale tracks
        stale_ids = [
            tid for tid, track in self.tracks.items()
            if current_time - track.last_seen > self.track_timeout
        ]
        for tid in stale_ids:
            logger.debug(f"Track expired: ID {tid}")
            del self.tracks[tid]
        
        # Return active tracks
        return list(self.tracks.values())

    def estimate_3d_position(
        self,
        track: TrackedFace,
        frame_width: int,
        frame_height: int,
        camera_fov_horizontal: float = 60.0,
    ) -> Position3D:
        """Estimate 3D position from bounding box and camera parameters.
        
        Uses bbox size to estimate depth (larger bbox = closer).
        Assumes typical human head size (~0.2m width).
        
        Args:
            track: Tracked face to estimate position for
            frame_width: Camera frame width in pixels
            frame_height: Camera frame height in pixels
            camera_fov_horizontal: Camera horizontal FOV in degrees
            
        Returns:
            Estimated 3D position relative to robot
        """
        face = track.face
        cx = face.x + face.width / 2
        cy = face.y + face.height / 2
        
        # Estimate depth from bbox width (simple model)
        # Assume average human head width = 0.2m
        # depth ~ (focal_length * real_width) / pixel_width
        focal_length_pixels = frame_width / (2 * np.tan(np.deg2rad(camera_fov_horizontal / 2)))
        assumed_head_width = 0.2  # meters
        estimated_depth = (focal_length_pixels * assumed_head_width) / face.width
        
        # Clamp depth to reasonable range (0.3m - 5.0m)
        estimated_depth = np.clip(estimated_depth, 0.3, 5.0)
        
        # Convert pixel coordinates to 3D position
        # x: left-right (positive = right)
        # y: vertical (positive = up)
        # z: depth (positive = forward)
        x = (cx - frame_width / 2) / focal_length_pixels * estimated_depth
        y = -(cy - frame_height / 2) / focal_length_pixels * estimated_depth  # Invert y
        z = estimated_depth
        
        return Position3D(x=float(x), y=float(y), z=float(z))

    def select_primary_face(
        self,
        tracks: list[TrackedFace],
        frame_width: int,
        frame_height: int,
    ) -> Optional[int]:
        """Select primary face for attention based on weighted scoring.
        
        Scoring factors:
        - Centrality: 40% - How close to frame center
        - Size/Proximity: 40% - Larger faces (closer) score higher
        - Tracking Confidence: 20% - More stable tracks preferred
        
        Args:
            tracks: List of active tracked faces
            frame_width: Camera frame width
            frame_height: Camera frame height
            
        Returns:
            Persistent ID of primary face, or None if no faces
        """
        if len(tracks) == 0:
            return None
        
        frame_center = np.array([frame_width / 2, frame_height / 2])
        max_distance = np.linalg.norm(frame_center)  # Max distance from center
        
        best_score = -1.0
        best_id = None
        
        for track in tracks:
            # Centrality score (0-1, higher = more central)
            distance_to_center = np.linalg.norm(track.centroid - frame_center)
            centrality_score = 1.0 - (distance_to_center / max_distance)
            
            # Size/proximity score (0-1, higher = larger bbox)
            face_area = track.face.width * track.face.height
            max_area = frame_width * frame_height
            size_score = np.sqrt(face_area / max_area)  # Sqrt to reduce dominance
            
            # Tracking confidence score (0-1, already normalized)
            confidence_score = track.tracking_confidence
            
            # Weighted combination
            total_score = (
                0.4 * centrality_score +
                0.4 * size_score +
                0.2 * confidence_score
            )
            
            if total_score > best_score:
                best_score = total_score
                best_id = track.persistent_id
                
            logger.debug(
                f"Track {track.persistent_id}: centrality={centrality_score:.2f}, "
                f"size={size_score:.2f}, confidence={confidence_score:.2f}, "
                f"total={total_score:.2f}"
            )
        
        return best_id

    def reset(self):
        """Reset tracker state (clear all tracks)."""
        self.tracks.clear()
        self.next_id = 1
        logger.info("Face tracker reset")

    def get_track_count(self) -> int:
        """Get number of active tracks."""
        return len(self.tracks)

    def get_track(self, persistent_id: int) -> Optional[TrackedFace]:
        """Get track by persistent ID."""
        return self.tracks.get(persistent_id)
