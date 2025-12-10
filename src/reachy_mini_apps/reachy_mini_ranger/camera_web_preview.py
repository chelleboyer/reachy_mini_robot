#!/usr/bin/env python3
"""Web-based camera preview with face detection visualization.

Serves camera feed with YOLO detections over HTTP.
View at http://localhost:8080
"""

import cv2
import numpy as np
from flask import Flask, Response
from reachy_mini import ReachyMini

from reachy_mini_ranger.brain.nodes.perception.vision_node import process_camera_frame


app = Flask(__name__)
robot = None


def generate_frames():
    """Generate camera frames with face detection overlays."""
    global robot
    
    while True:
        # Get frame
        frame = robot.media.get_frame()
        if frame is None:
            continue
        
        h, w = frame.shape[:2]
        
        # Run face detection
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
            if human.is_primary:
                pos_text = f"PRIMARY (ID:{human.persistent_id})"
                color = (0, 255, 255)  # Yellow
            else:
                pos_text = f"Human {human.persistent_id}"
                color = (255, 0, 255)  # Magenta
            
            # Draw 3D position
            pos_3d = f"({human.position.x:.1f}, {human.position.y:.1f}, {human.position.z:.1f})m"
            cv2.putText(frame, f"{pos_text}: {pos_3d}", (10, 30 + idx * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw FPS and info
        info_text = f"Faces: {len(faces)} | Humans: {len(humans)}"
        cv2.putText(frame, info_text, (10, h - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Encode as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return '''
    <html>
      <head>
        <title>Robot Camera - Face Detection</title>
        <style>
          body { margin: 0; background: #000; display: flex; justify-content: center; align-items: center; height: 100vh; }
          img { max-width: 100%; max-height: 100%; }
        </style>
      </head>
      <body>
        <img src="/video_feed">
      </body>
    </html>
    '''


if __name__ == '__main__':
    print("Connecting to ReachyMini...")
    robot = ReachyMini()
    
    print("\n" + "="*60)
    print("Camera preview server starting...")
    print("Open browser to: http://localhost:8080")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    try:
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    finally:
        if robot:
            robot.client.disconnect()
