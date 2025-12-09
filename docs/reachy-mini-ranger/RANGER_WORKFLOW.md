# Reachy Mini Ranger - App Development Workflow

## Overview
**reachy_mini_ranger** is a custom application built on top of the Reachy Mini SDK. This app demonstrates basic robot control including head movement, antenna control, and sound playback.

## Project Location
```
src/reachy_mini_apps/reachy_mini_ranger/
├── reachy_mini_ranger/
│   ├── __init__.py
│   ├── main.py              # Main app logic
│   └── static/              # Web UI assets
├── index.html               # Web interface
├── style.css                # UI styling
├── pyproject.toml           # Dependencies & entry points
└── README.md                # App metadata
```

## Important: SDK vs App Development

### ✅ What You Can Modify
- `src/reachy_mini_apps/reachy_mini_ranger/` - **Your app code**
- `bmad-custom-src/` - Custom BMAD configurations
- `bmad-custom-modules-src/` - Custom BMAD modules
- `docs/` - Project documentation

### ❌ Do NOT Modify
- `src-refs/reachy_mini/` - Core SDK/daemon (reference only)
- `src-refs/reachy_mini_conversation_app/` - Conversation app (reference)
- `src-refs/reachy_mini_toolbox/` - Toolbox (reference)

You **use** the SDK, but don't modify it!

## Development Workflow

### 1. Setup & Installation

```bash
# Install the ranger app in development mode
cd src/reachy_mini_apps/reachy_mini_ranger
pip install -e .

# Or use uv
uv pip install -e .
```

### 2. Running the App

#### A. Start the Daemon First
```bash
# In one terminal - start hardware daemon
reachy-mini-daemon

# OR start in simulation mode
reachy-mini-daemon --sim
```

#### B. Run Your App
```bash
# In another terminal
cd src/reachy_mini_apps/reachy_mini_ranger
python -m reachy_mini_ranger.main

# The app will:
# - Connect to daemon at localhost:8000
# - Start control loop
# - Serve web UI at http://0.0.0.0:8042
```

### 3. Development Cycle

#### Making Changes
1. Edit `reachy_mini_ranger/main.py`
2. Save changes
3. Stop app (Ctrl+C)
4. Restart app
5. Test in browser at http://localhost:8042

#### Web UI Development
1. Edit `index.html` or `style.css`
2. Refresh browser (changes are immediate)
3. Use browser dev tools for debugging

### 4. Using the SDK

The ranger app inherits from `ReachyMiniApp` and gets a `reachy_mini` instance:

```python
class ReachyMiniRanger(ReachyMiniApp):
    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event):
        # Your control loop here
        while not stop_event.is_set():
            # Use reachy_mini SDK methods
            reachy_mini.set_target(head=pose, antennas=angles)
            time.sleep(0.02)
```

#### Available SDK Methods
```python
# Head control
from reachy_mini.utils import create_head_pose
pose = create_head_pose(yaw=30, pitch=10, roll=0, degrees=True)
reachy_mini.set_target(head=pose)
reachy_mini.goto_target(head=pose, duration=2.0, method="minjerk")

# Antenna control
antennas_rad = np.array([0.5, -0.5])  # radians
reachy_mini.set_target(antennas=antennas_rad)

# Audio
reachy_mini.media.play_sound("wake_up.wav")

# Get current state
current_pose = reachy_mini.get_current_head_pose()
```

#### Safety Limits (enforced by SDK)
- Head pitch/roll: ±40°
- Head yaw: ±180°
- Body-to-head yaw difference: ±65°
- Antennas: Check SDK docs for range

### 5. Adding Features to Ranger

#### Example: Add New Behavior
```python
def run(self, reachy_mini: ReachyMini, stop_event: threading.Event):
    # Add state variables
    current_behavior = "scanning"
    
    while not stop_event.is_set():
        if current_behavior == "scanning":
            # Implement scanning behavior
            pass
        elif current_behavior == "tracking":
            # Implement tracking behavior
            pass
```

#### Example: Add New Web Endpoint
```python
@self.settings_app.post("/set_behavior")
def set_behavior(behavior: str):
    nonlocal current_behavior
    current_behavior = behavior
    return {"behavior": behavior}
```

Then call from browser:
```javascript
fetch('/set_behavior', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify('tracking')
})
```

### 6. Testing Your App

#### Manual Testing
1. Start daemon in simulation: `reachy-mini-daemon --sim`
2. Run your app
3. Open web UI
4. Test each feature
5. Check console output for errors

#### Integration Testing
```python
# Add tests in tests/ directory (create if needed)
import pytest
from reachy_mini_ranger.main import ReachyMiniRanger

def test_app_initialization():
    app = ReachyMiniRanger()
    assert app.custom_app_url is not None
```

#### Visual Testing with Rerun
```bash
# Use rerun for visualization
reachy-mini-daemon --sim
# In another terminal
python examples/rerun_viewer.py  # from src-refs/reachy_mini/
```

### 7. Common Development Tasks

#### Add Vision Processing
```python
# Install opencv if needed
# pip install opencv-python

import cv2

def run(self, reachy_mini: ReachyMini, stop_event: threading.Event):
    while not stop_event.is_set():
        # Get camera feed (if available)
        # Process with OpenCV
        # React with head movements
        pass
```

#### Add State Machine
```python
from enum import Enum

class State(Enum):
    IDLE = "idle"
    SCANNING = "scanning"
    FOLLOWING = "following"

state = State.IDLE
```

#### Add Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run(self, reachy_mini: ReachyMini, stop_event: threading.Event):
    logger.info("Starting ranger app")
    while not stop_event.is_set():
        logger.debug(f"Current state: {state}")
```

### 8. Debugging

#### Common Issues
1. **App won't connect to daemon**
   - Check daemon is running: `curl http://localhost:8000/api/health`
   - Check correct port (default 8000)

2. **Web UI not loading**
   - Check port 8042 is not in use
   - Check firewall settings
   - Try different port in custom_app_url

3. **Movements not smooth**
   - Reduce sleep time in control loop
   - Use `goto_target()` with interpolation instead of `set_target()`
   - Check if hitting motor limits

4. **Import errors**
   - Reinstall: `pip install -e .`
   - Check virtual environment is activated

### 9. Git Workflow for Ranger App

```bash
# Create feature branch
git checkout -b feature/ranger-new-behavior

# Make changes in src/reachy_mini_apps/reachy_mini_ranger/
# Commit frequently
git add src/reachy_mini_apps/reachy_mini_ranger/
git commit -m "Add new scanning behavior to ranger"

# Push and create PR
git push origin feature/ranger-new-behavior
```

### 10. Deployment

#### Package Your App
```bash
cd src/reachy_mini_apps/reachy_mini_ranger
python -m build
# Creates dist/ with wheel
```

#### Install on Robot
```bash
# On robot hardware
pip install reachy_mini_ranger-0.1.0-py3-none-any.whl
reachy-mini-app-assistant  # Select ranger from menu
```

## Current Features

- ✅ Sinusoidal head yaw movement
- ✅ Synchronized antenna oscillation
- ✅ Web UI with antenna enable/disable
- ✅ Sound playback trigger
- ✅ FastAPI settings endpoint

## Planned Features

Track your planned features here:

- [ ] Add vision-based person tracking
- [ ] Implement multiple behavior modes
- [ ] Add joystick control via web UI
- [ ] Create choreographed movement sequences
- [ ] Add autonomous exploration behavior

## Resources

### SDK Documentation
- Python SDK: `src-refs/reachy_mini/docs/python-sdk.md`
- REST API: `src-refs/reachy_mini/docs/rest-api.md`
- Examples: `src-refs/reachy_mini/examples/`

### Your App Structure
- Entry point: `reachy_mini_ranger/main.py`
- Web UI: `index.html`, `style.css`
- Config: `pyproject.toml`

### BMAD Tools
- Workflows: `.bmad/bmb/workflows/`
- Custom config: `bmad-custom-src/custom.yaml`

## Support

- Check troubleshooting: `src-refs/reachy_mini/docs/troubleshooting.md`
- Test in simulation first before hardware
- Use examples as templates

---

*Last updated: December 9, 2025*
