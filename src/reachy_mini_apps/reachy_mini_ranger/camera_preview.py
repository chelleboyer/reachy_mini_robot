#!/usr/bin/env python3
"""Camera preview with face detection visualization.

Shows what the robot sees with YOLO face detection overlays.
Press 'q' to quit.
"""

import cv2
import numpy as np
from reachy_mini import ReachyMini

from reachy_mini_ranger.brain.nodes.perception.vision_node import process_camera_frame


def main():
    """Run camera preview with face detection."""
    print("Connecting to ReachyMini...")
    with ReachyMini() as robot:
        print("Camera preview starting. Press 'q' to quit.")
        
        # Check camera
        if robot.media.camera is None:
            print("ERROR: Camera not initialized!")
            return
        
        frame_count = 0
        
        while True:
            # Get frame
            frame = robot.media.get_frame()
            if frame is None:
                print("WARNING: Failed to get frame")
                continue
            
            frame_count += 1
            h, w = frame.shape[:2]
            
            # Run face detection every frame
            faces, humans, primary_id = process_camera_frame(frame, w, h)
            
            # Draw detections
            for face in faces:
                # Draw bounding box
                x1, y1 = int(face.x), int(face.y)
                x2, y2 = int(face.x + face.width), int(face.y + face.height)
                color = (0, 255, 0)  # Green
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw confidence
                conf_text = f"{face.confidence:.2f}"
                cv2.putText(frame, conf_text, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw human tracking info
            for idx, human in enumerate(humans):
                # Draw position info
                if human.is_primary:
                    pos_text = f"PRIMARY (ID:{human.persistent_id})"
                    color = (0, 255, 255)  # Yellow for primary
                else:
                    pos_text = f"Human {human.persistent_id}"
                    color = (255, 0, 255)  # Magenta for others
                
                # Draw 3D position
                pos_3d = f"({human.position.x:.1f}, {human.position.y:.1f}, {human.position.z:.1f})m"
                cv2.putText(frame, f"{pos_text}: {pos_3d}", (10, 30 + idx * 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw FPS and info
            info_text = f"Frame: {frame_count} | Faces: {len(faces)} | Humans: {len(humans)}"
            cv2.putText(frame, info_text, (10, h - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Display
            cv2.imshow('Robot Camera - Press Q to quit', frame)
            
            # Check for quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        cv2.destroyAllWindows()
        print("Camera preview stopped.")


if __name__ == "__main__":
    main()
