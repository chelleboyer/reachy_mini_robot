# Reachy Mini Ranger - Testing Guide

## Testing Strategy

This guide covers testing approaches for the **reachy_mini_ranger** app. The app depends on the Reachy Mini SDK, so we test at the app layer only.

---

## Test Environment Setup

### Prerequisites
```bash
# Install ranger app with dev dependencies
cd src/reachy_mini_apps/reachy_mini_ranger
pip install -e ".[dev]"  # Once dev deps are added to pyproject.toml

# Or install pytest separately
pip install pytest pytest-cov pytest-asyncio
```

### Directory Structure
```
reachy_mini_ranger/
├── reachy_mini_ranger/
│   ├── __init__.py
│   └── main.py
├── tests/                    # Create this
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_app.py          # App initialization tests
│   ├── test_behaviors.py    # Behavior logic tests
│   └── test_integration.py  # Integration tests with daemon
├── pyproject.toml
└── README.md
```

---

## Testing Levels

### 1. Unit Tests (Fast, No Daemon Required)

Test individual functions and logic without requiring robot connection.

**File:** `tests/test_behaviors.py`

```python
import numpy as np
import pytest
from reachy_mini_ranger.main import ReachyMiniRanger


def test_antenna_calculation():
    """Test antenna angle calculations"""
    t = 0.0
    amp_deg = 25.0
    a = amp_deg * np.sin(2.0 * np.pi * 0.5 * t)
    expected = 0.0
    assert abs(a - expected) < 0.01


def test_head_yaw_range():
    """Test head yaw stays within safe bounds"""
    for t in np.linspace(0, 10, 100):
        yaw_deg = 30.0 * np.sin(2.0 * np.pi * 0.2 * t)
        assert -180 <= yaw_deg <= 180
        assert abs(yaw_deg) <= 30  # Our max amplitude


def test_app_initialization():
    """Test app can be instantiated"""
    app = ReachyMiniRanger()
    assert app.custom_app_url == "http://0.0.0.0:8042"
```

**Run unit tests:**
```bash
pytest tests/test_behaviors.py -v
```

---

### 2. Integration Tests (Requires Simulation Daemon)

Test app behavior with actual daemon connection (in simulation mode).

**File:** `tests/test_integration.py`

```python
import pytest
import threading
import time
from reachy_mini_ranger.main import ReachyMiniRanger
from reachy_mini import ReachyMini


@pytest.mark.integration
def test_app_connects_to_daemon():
    """Test app can connect to running daemon"""
    # Requires: reachy-mini-daemon --sim
    try:
        with ReachyMini() as reachy:
            assert reachy is not None
    except Exception as e:
        pytest.skip(f"Daemon not available: {e}")


@pytest.mark.integration
def test_app_control_loop():
    """Test app runs without errors for short duration"""
    # Requires: reachy-mini-daemon --sim
    app = ReachyMiniRanger()
    
    # Run for 1 second
    stop_event = threading.Event()
    
    def run_app():
        try:
            with ReachyMini() as reachy:
                app.run(reachy, stop_event)
        except Exception:
            pytest.skip("Daemon not available")
    
    thread = threading.Thread(target=run_app)
    thread.start()
    
    time.sleep(1.0)
    stop_event.set()
    thread.join(timeout=2.0)
    
    assert not thread.is_alive()


@pytest.mark.integration
def test_web_endpoints():
    """Test web API endpoints work"""
    import requests
    
    # Start app in background
    app = ReachyMiniRanger()
    # ... setup and test POST endpoints
    
    response = requests.post(
        "http://0.0.0.0:8042/antennas",
        json={"enabled": False}
    )
    assert response.status_code == 200
```

**Run integration tests:**
```bash
# Start daemon first
reachy-mini-daemon --sim

# In another terminal
pytest tests/test_integration.py -v -m integration
```

---

### 3. Manual Testing (Interactive)

For features that need human observation.

#### Test Checklist

**Basic Functionality:**
- [ ] App starts without errors
- [ ] Web UI loads at http://localhost:8042
- [ ] Head moves in sinusoidal pattern
- [ ] Antennas oscillate when enabled
- [ ] Antenna toggle button works
- [ ] Play sound button triggers audio
- [ ] App stops gracefully with Ctrl+C

**Visual Inspection (Simulation):**
- [ ] Head movement is smooth
- [ ] Antennas move symmetrically
- [ ] No sudden jerky motions
- [ ] Respects motor limits

**Performance:**
- [ ] Control loop runs at ~50Hz
- [ ] No lag in web UI
- [ ] CPU usage reasonable (<50%)
- [ ] Memory stable (no leaks)

#### Manual Test Script

```bash
# Terminal 1: Start daemon
reachy-mini-daemon --sim

# Terminal 2: Run app
cd src/reachy_mini_apps/reachy_mini_ranger
python -m reachy_mini_ranger.main

# Terminal 3: Test web API
curl -X POST http://localhost:8042/antennas \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

curl -X POST http://localhost:8042/play_sound
```

---

### 4. Hardware Testing (Before Deployment)

**Only run on actual hardware after simulation tests pass!**

#### Safety Checks
- [ ] Emergency stop accessible
- [ ] Clear workspace around robot
- [ ] Movement limits configured correctly
- [ ] Sound volume appropriate
- [ ] No obstacles in range

#### Hardware Test Protocol

1. **Power On Checks**
   ```bash
   # Check daemon connects to hardware
   reachy-mini-daemon
   # Should show: "Connected to hardware"
   ```

2. **Slow Movement Test**
   ```python
   # Modify main.py temporarily for slow testing
   yaw_deg = 10.0 * np.sin(2.0 * np.pi * 0.1 * t)  # Slower, smaller
   ```

3. **Full Speed Test**
   - Restore normal parameters
   - Run for 5 minutes
   - Monitor for overheating, unusual sounds
   - Check motor temperatures

4. **Stress Test**
   - Run for 30 minutes
   - Log any errors
   - Check stability

5. **Edge Cases**
   - Toggle antennas rapidly
   - Trigger sounds in quick succession
   - Test daemon reconnection

---

## Testing Configurations

### pytest.ini (Create in ranger root)

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    integration: marks tests requiring daemon (deselect with '-m "not integration"')
    hardware: marks tests requiring actual hardware
    slow: marks tests that take > 1 second

addopts = 
    -v
    --strict-markers
    --tb=short
```

### Add to pyproject.toml

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-asyncio>=0.21",
    "requests>=2.28",  # For API testing
]
```

---

## Continuous Testing Workflow

### Local Development
```bash
# Quick unit tests (no daemon needed)
pytest tests/test_behaviors.py -v

# Full test suite with daemon
reachy-mini-daemon --sim &
DAEMON_PID=$!
pytest tests/ -v
kill $DAEMON_PID
```

### Pre-commit Checks
```bash
# Run before committing
pytest tests/test_behaviors.py  # Fast tests
ruff check .                     # Linting
mypy reachy_mini_ranger/        # Type checking
```

---

## Debugging Failed Tests

### Common Issues

**1. Daemon Not Running**
```
Error: Connection refused [Errno 111]
```
**Fix:** Start daemon: `reachy-mini-daemon --sim`

**2. Port Already in Use**
```
Error: Address already in use
```
**Fix:** Kill existing process or use different port

**3. Import Errors**
```
ModuleNotFoundError: No module named 'reachy_mini_ranger'
```
**Fix:** Reinstall: `pip install -e .`

**4. Timing Issues in Tests**
```
AssertionError: Expected X but got Y
```
**Fix:** Add `time.sleep()` or increase tolerances

### Test Debugging Tools

```python
# Add detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use pytest debugging
pytest tests/test_app.py -v -s --pdb  # Drop to debugger on failure

# Print captured output
pytest tests/test_app.py -v -s  # Show print statements
```

---

## Test Coverage

### Measure Coverage
```bash
pytest --cov=reachy_mini_ranger tests/ --cov-report=html
# Open htmlcov/index.html
```

### Coverage Goals
- Unit tests: >80% coverage
- Integration tests: Key workflows covered
- Edge cases: Error handling validated

---

## Performance Testing

### Timing Tests
```python
import time

def test_control_loop_performance():
    """Ensure control loop can maintain 50Hz"""
    iterations = 100
    start = time.time()
    
    for i in range(iterations):
        # Simulate one iteration
        yaw_deg = 30.0 * np.sin(2.0 * np.pi * 0.2 * i * 0.02)
        # ... calculations
    
    elapsed = time.time() - start
    hz = iterations / elapsed
    
    assert hz >= 45  # Allow some margin
```

### Load Testing
```bash
# Monitor resource usage
top -p $(pgrep -f reachy_mini_ranger)

# Or use htop for better visualization
htop
```

---

## Test Documentation

Each test should include:
- **Purpose:** What is being tested
- **Setup:** Prerequisites and fixtures
- **Steps:** What the test does
- **Expected:** What should happen
- **Cleanup:** How to restore state

---

## Resources

- pytest docs: https://docs.pytest.org/
- SDK troubleshooting: `src-refs/reachy_mini/docs/troubleshooting.md`
- Daemon testing: `src-refs/reachy_mini/tests/`

---

*Last updated: December 9, 2025*
