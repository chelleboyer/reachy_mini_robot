# Camera Worker Refactor - Option A Implementation

**Date**: December 10, 2025  
**Status**: ✅ Complete - Ready for Testing

## What Changed

Refactored face tracking from single-threaded 2.5 Hz brain loop to match the conversation app's multi-threaded architecture with 30 Hz camera worker.

## Architecture Overview

### Before (Single-threaded)
```
Main Loop (2.5 Hz actual, limited by vision processing)
├─ Brain: perception → cognition → execution
├─ Vision: YOLO face detection (slow)
├─ Cognition: Calculate pixel coords
└─ Main: look_at_image() + goto_target()
```

### After (Multi-threaded, matching conversation app)
```
Camera Worker Thread (30 Hz)
├─ Continuous frame capture
├─ Face detection (YOLO)
├─ look_at_image() offset calculation
└─ Thread-safe offset storage

Brain Loop (10 Hz)
├─ High-level behavior (scanning, interaction planning)
└─ Provides base head pose

Main Loop (10 Hz)
├─ Read offsets from camera worker
├─ Compose: base_pose + face_tracking_offsets
└─ set_target() to robot
```

## New Files

### `reachy_mini_ranger/camera_worker.py`
- `CameraWorker` class: Thread-safe camera + face tracking
- Runs at ~30 Hz in dedicated thread
- Calculates face tracking offsets using `look_at_image()`
- Smooth interpolation back to neutral when face lost
- Thread-safe locks for frame storage and offset access

## Modified Files

### `reachy_mini_ranger/main.py`
**Key changes:**
1. Import `CameraWorker` and `compose_world_offset`
2. Start camera worker thread on app start
3. Simplified main loop:
   - Get base pose from brain (scanning or neutral)
   - Get face tracking offsets from camera worker
   - Compose final pose with `compose_world_offset()`
   - Use `set_target()` instead of `goto_target()`
4. New web UI endpoint: `/face_tracking` to toggle tracking on/off
5. Enhanced logging showing offsets and camera stats
6. Clean shutdown of camera worker thread

### `reachy_mini_ranger/brain/graph.py`
**Simplified `cognition_node()`:**
- Face tracking logic **removed** (now in camera worker)
- Provides base poses only:
  - Neutral (0°, 0°, 0°) when human detected
  - Scanning (sinusoidal yaw sweep) when idle
- Face tracking offsets applied externally in main loop

## How It Works

1. **Camera Worker** (separate thread, 30 Hz):
   - Captures frames continuously
   - Detects faces with YOLO
   - For each face: calls `look_at_image()` to calculate target pose
   - Extracts translation (x,y,z) and rotation (roll,pitch,yaw) from pose matrix
   - Stores offsets in thread-safe variables
   - When face lost: smoothly interpolates back to neutral over 1 second

2. **Brain** (10 Hz):
   - Detects presence of humans (world model)
   - Decides behavior: scanning vs neutral
   - Outputs base head pose (scanning angles or neutral)

3. **Main Loop** (10 Hz):
   - Gets base pose from brain
   - Reads offsets from camera worker (thread-safe)
   - Composes final pose: `compose_world_offset(base, x, y, z, roll, pitch, yaw)`
   - Sends to robot with `set_target()`

## Benefits

✅ **Smooth tracking**: 30 Hz face detection vs 2.5 Hz before  
✅ **Decoupled**: Brain can think independently of camera processing  
✅ **Responsive**: Camera worker doesn't block brain decisions  
✅ **Matches reference**: Same architecture as Pollen Robotics conversation app  
✅ **Composable**: Face tracking as additive offset on any base behavior  

## Testing

### Commands to Run
```bash
# Terminal 1: Start daemon
source .venv/bin/activate
reachy-mini-daemon

# Terminal 2: Run app
cd src/reachy_mini_apps/reachy_mini_ranger
python -m reachy_mini_ranger.main
```

### Expected Behavior
- **No face**: Robot scans left-right (±60° sinusoidal)
- **Face detected**: Smooth tracking, head follows face center
- **Face moves**: Camera worker updates offsets 30x/second
- **Face lost**: Smoothly returns to base pose over 1 second

### Web UI
- Open `http://localhost:8042` (or robot IP:8042)
- Toggle face tracking on/off
- Toggle brain on/off (manual control)
- Toggle antennas

### Logs to Expect
```
Camera worker started (30 Hz face tracking)
Starting brain loop at 10 Hz...
🎯 TRACKING | Offsets: yaw=12.3° pitch=-5.7° | Head: yaw=12.5° pitch=-5.8° | Camera: 152 frames, 48 faces
🔍 SCANNING | Base: yaw=45.2° pitch=0.0° | Head: yaw=45.3° pitch=0.1° | Camera: 312 frames
```

## Tuning Parameters

### In `camera_worker.py`:
- `time.sleep(0.033)` → Controls camera worker frequency (~30 Hz)
- `face_lost_delay = 2.0` → How long to wait before returning to neutral
- `interpolation_duration = 1.0` → Smoothness of return to neutral

### In `brain/graph.py`:
- `scan_period = 4.0` → Speed of idle scanning
- `scan_amplitude = 60.0` → Range of idle scanning (degrees)

### In `main.py`:
- `time.sleep(0.1)` → Brain loop frequency (10 Hz)

## Troubleshooting

### Camera worker not starting
- Check `reachy_mini.media.get_frame()` works
- Verify YOLO model loads: `get_face_detector()`

### Face tracking not smooth
- Increase camera worker frequency (decrease sleep time)
- Check camera FPS in logs
- Verify `look_at_image()` not throwing exceptions

### Robot jerky movement
- Face tracking offsets may be too large
- Check `compose_world_offset()` parameters
- Verify safety limits in SDK

### Face tracking stuck
- Check thread locks not deadlocking
- Verify `get_face_tracking_offsets()` returns fresh data
- Look for exceptions in camera worker loop

## Next Steps

1. **Test on real hardware** - Current implementation ready to run
2. **Tune parameters** - Adjust tracking responsiveness, scan speed
3. **Add breathing** - Replace scanning with BreathingMove idle behavior
4. **Speech sway** - Add second secondary move for speech animations
5. **Conversation** - Integrate LLM responses with face tracking

## References

- Conversation app architecture: `src-refs/reachy_mini_conversation_app/src/reachy_mini_conversation_app/moves.py`
- Camera worker reference: `src-refs/reachy_mini_conversation_app/src/reachy_mini_conversation_app/camera_worker.py`
- SDK utilities: `reachy_mini.utils.interpolation.compose_world_offset()`
