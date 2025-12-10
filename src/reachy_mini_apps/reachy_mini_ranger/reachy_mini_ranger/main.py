import threading
from reachy_mini import ReachyMini, ReachyMiniApp
from reachy_mini.utils import create_head_pose
from reachy_mini.utils.interpolation import compose_world_offset
import numpy as np
import time
from pydantic import BaseModel
from scipy.spatial.transform import Rotation as R

from reachy_mini_ranger.brain.graph import compile_graph
from reachy_mini_ranger.brain.models.state import create_initial_state
from reachy_mini_ranger.camera_worker import CameraWorker


class ReachyMiniRanger(ReachyMiniApp):
    # Optional: URL to a custom configuration page for the app
    # eg. "http://localhost:8042"
    custom_app_url: str | None = "http://0.0.0.0:8042"

    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event):
        """Brain-controlled autonomous interaction loop with camera worker.
        
        Architecture (matching conversation app):
        - Camera worker thread: ~30 Hz face detection & tracking offset calculation
        - Brain loop: 10 Hz high-level behavior (scanning, interaction)
        - Main loop: Apply face tracking offsets as secondary move on top of brain commands
        
        This gives smooth face tracking while maintaining responsive brain behavior.
        """
        # Enable motors for head movement
        print("Enabling motors...", flush=True)
        reachy_mini.enable_motors()
        
        # Start camera worker thread for face tracking
        camera_worker = CameraWorker(reachy_mini)
        camera_worker.start()
        print("Camera worker started (30 Hz face tracking)", flush=True)
        
        # Initialize brain (no longer needs reachy_mini since camera worker handles camera)
        graph = compile_graph(reachy_mini=reachy_mini)
        state = create_initial_state()
        
        # Settings for web UI
        antennas_enabled = True
        sound_play_requested = False
        brain_enabled = True  # Toggle brain control vs manual mode
        face_tracking_enabled = True  # Toggle face tracking

        # Web UI endpoints
        class AntennaState(BaseModel):
            enabled: bool
        
        class BrainState(BaseModel):
            enabled: bool
        
        class FaceTrackingState(BaseModel):
            enabled: bool

        @self.settings_app.post("/antennas")
        def update_antennas_state(antenna_state: AntennaState):
            nonlocal antennas_enabled
            antennas_enabled = antenna_state.enabled
            return {"antennas_enabled": antennas_enabled}

        @self.settings_app.post("/play_sound")
        def request_sound_play():
            nonlocal sound_play_requested
            sound_play_requested = True
        
        @self.settings_app.post("/brain")
        def update_brain_state(brain_state_update: BrainState):
            nonlocal brain_enabled
            brain_enabled = brain_state_update.enabled
            return {"brain_enabled": brain_enabled}
        
        @self.settings_app.post("/face_tracking")
        def update_face_tracking_state(tracking_state: FaceTrackingState):
            nonlocal face_tracking_enabled
            face_tracking_enabled = tracking_state.enabled
            camera_worker.set_head_tracking_enabled(face_tracking_enabled)
            return {"face_tracking_enabled": face_tracking_enabled}

        # Main brain control loop (100 Hz for perfectly fluid face tracking)
        print("Starting control loop at 100 Hz (brain at 10 Hz)...", flush=True)
        loop_start = time.time()
        loop_count = 0
        brain_cycle_counter = 0  # Run brain at 10 Hz, apply tracking at 100 Hz
        
        try:
            while not stop_event.is_set():
                cycle_start = time.time()
                
                if brain_enabled:
                    # Run brain at 10 Hz (every 10 cycles), but apply tracking at 100 Hz
                    brain_cycle_counter += 1
                    if brain_cycle_counter >= 10:
                        state = graph.invoke(state)
                        brain_cycle_counter = 0
                    
                    # Get brain's commanded head pose (scanning, looking around, etc.)
                    head_cmd = state.actuator_commands.head
                    base_head_pose = create_head_pose(
                        yaw=head_cmd.yaw,
                        pitch=head_cmd.pitch,
                        roll=head_cmd.roll,
                        degrees=True
                    )
                    
                    # Get face tracking offsets from camera worker (running at 30 Hz)
                    if face_tracking_enabled:
                        offsets = camera_worker.get_face_tracking_offsets()
                        x, y, z, roll, pitch, yaw = offsets
                        
                        # Check if we have meaningful face tracking (not all zeros)
                        has_face_tracking = any(abs(val) > 0.001 for val in offsets)
                        
                        if has_face_tracking:
                            # Build offset matrix (4x4 homogeneous transform)
                            offset_matrix = np.eye(4, dtype=np.float32)
                            offset_matrix[:3, 3] = [x, y, z]  # Translation
                            offset_matrix[:3, :3] = R.from_euler('xyz', [roll, pitch, yaw]).as_matrix()  # Rotation
                            
                            # Apply face tracking as SECONDARY move (additive offset)
                            # This matches conversation app's architecture
                            final_head_pose = compose_world_offset(
                                base_head_pose,
                                offset_matrix
                            )
                        else:
                            # No face tracking active, use base pose
                            final_head_pose = base_head_pose
                    else:
                        # Face tracking disabled, use base pose
                        final_head_pose = base_head_pose
                    
                    # Send final composed head pose to robot (continuous updates at 50 Hz)
                    reachy_mini.set_target(head=final_head_pose)
                
                # Execute antenna commands (if enabled)
                if antennas_enabled:
                    antenna_cmd = state.actuator_commands.antennas
                    antennas_rad = np.array([
                        np.deg2rad(antenna_cmd.left),
                        np.deg2rad(antenna_cmd.right)
                    ])
                else:
                    antennas_rad = np.array([0.0, 0.0])
                
                reachy_mini.set_target(antennas=antennas_rad)
            else:
                # Manual mode: Neutral pose
                head_pose = create_head_pose(yaw=0.0, pitch=0.0, roll=0.0, degrees=True)
                reachy_mini.set_target(
                    head=head_pose,
                    antennas=np.array([0.0, 0.0]),
                )
            
            # Handle sound play requests from web UI
            if sound_play_requested:
                print("Playing sound...")
                reachy_mini.media.play_sound("wake_up.wav")
                sound_play_requested = False
            
            # Log performance every second
            loop_count += 1
            if loop_count % 100 == 0:  # Every second at 100 Hz
                elapsed = time.time() - loop_start
                avg_fps = loop_count / elapsed
                
                # Get camera worker stats
                offsets = camera_worker.get_face_tracking_offsets()
                has_face = any(abs(val) > 0.001 for val in offsets)
                
                # Get actual current head pose from robot
                current_head = reachy_mini.get_current_head_pose()
                actual_yaw = current_head.yaw if hasattr(current_head, 'yaw') else 0.0
                actual_pitch = current_head.pitch if hasattr(current_head, 'pitch') else 0.0
                
                # Log with camera worker info
                if has_face:
                    x, y, z, roll, pitch, yaw = offsets
                    print(f"🎯 TRACKING | Offsets: yaw={np.rad2deg(yaw):.1f}° pitch={np.rad2deg(pitch):.1f}° | "
                          f"Head: yaw={actual_yaw:.1f}° pitch={actual_pitch:.1f}° | "
                          f"Camera: {camera_worker.frames_processed} frames, {camera_worker.faces_detected} faces", 
                          flush=True)
                else:
                    head_cmd = state.actuator_commands.head
                    print(f"🔍 SCANNING | Base: yaw={head_cmd.yaw:.1f}° pitch={head_cmd.pitch:.1f}° | "
                          f"Head: yaw={actual_yaw:.1f}° pitch={actual_pitch:.1f}° | "
                          f"Camera: {camera_worker.frames_processed} frames", 
                          flush=True)
            
            # Sleep to maintain 100 Hz loop (10ms period)
            cycle_elapsed = time.time() - cycle_start
            sleep_time = max(0.0, 0.01 - cycle_elapsed)
            time.sleep(sleep_time)
        
        finally:
            # Clean shutdown of camera worker
            print("Stopping camera worker...", flush=True)
            camera_worker.stop()


if __name__ == "__main__":
    app = ReachyMiniRanger()
    try:
        app.wrapped_run()
    except KeyboardInterrupt:
        app.stop()
