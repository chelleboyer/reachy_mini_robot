import threading
from reachy_mini import ReachyMini, ReachyMiniApp
from reachy_mini.utils import create_head_pose
import numpy as np
import time
from pydantic import BaseModel

from reachy_mini_ranger.brain.graph import compile_graph
from reachy_mini_ranger.brain.models.state import create_initial_state


class ReachyMiniRanger(ReachyMiniApp):
    # Optional: URL to a custom configuration page for the app
    # eg. "http://localhost:8042"
    custom_app_url: str | None = "http://0.0.0.0:8042"

    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event):
        """Brain-controlled autonomous interaction loop.
        
        Runs the LangGraph brain at 10 Hz:
        1. Perception: Vision captures camera frames, detects faces
        2. Cognition: Calculates head orientation to look at primary face
        3. Skills: (Future) Social interaction, conversation
        4. Execution: Validates safety, sends motor commands
        
        The brain outputs motor commands via actuator_commands, which are
        executed by the robot via set_target().
        """
        # Initialize brain
        graph = compile_graph()
        state = create_initial_state()
        
        # Settings for web UI
        antennas_enabled = True
        sound_play_requested = False
        brain_enabled = True  # New: Toggle brain control vs manual mode

        # Web UI endpoints
        class AntennaState(BaseModel):
            enabled: bool
        
        class BrainState(BaseModel):
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

        # Main brain control loop (10 Hz)
        loop_start = time.time()
        loop_count = 0
        
        while not stop_event.is_set():
            cycle_start = time.time()
            
            if brain_enabled:
                # Run one brain cycle
                state = graph.invoke(state)
                
                # Execute head commands from brain
                head_cmd = state.actuator_commands.head
                head_pose = create_head_pose(
                    yaw=head_cmd.yaw,
                    pitch=head_cmd.pitch,
                    roll=head_cmd.roll,
                    degrees=True
                )
                
                # Execute antenna commands (if enabled)
                if antennas_enabled:
                    antenna_cmd = state.actuator_commands.antennas
                    antennas_rad = np.array([
                        np.deg2rad(antenna_cmd.left),
                        np.deg2rad(antenna_cmd.right)
                    ])
                else:
                    antennas_rad = np.array([0.0, 0.0])
                
                # Send commands to robot
                reachy_mini.set_target(
                    head=head_pose,
                    antennas=antennas_rad,
                )
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
            
            # Log performance every 10 seconds
            loop_count += 1
            if loop_count % 100 == 0:  # Every 10 seconds at 10 Hz
                elapsed = time.time() - loop_start
                avg_fps = loop_count / elapsed
                print(f"Brain loop: {avg_fps:.1f} Hz (target: 10 Hz)")
            
            # Sleep to maintain 10 Hz loop (100ms period)
            cycle_elapsed = time.time() - cycle_start
            sleep_time = max(0.0, 0.1 - cycle_elapsed)
            time.sleep(sleep_time)


if __name__ == "__main__":
    app = ReachyMiniRanger()
    try:
        app.wrapped_run()
    except KeyboardInterrupt:
        app.stop()
