# Reachy Mini Ranger - Task Board

## Current Sprint: Initial Development
**Sprint Goal:** Create functional ranger app with core behaviors  
**Dates:** December 9, 2025 - December 23, 2025

---

## 🎯 Active Tasks (In Progress)

### None currently

---

## 📋 Backlog (To Do)

### High Priority

- [ ] **Task: Setup testing framework**
  - Create `tests/` directory
  - Add pytest configuration
  - Write initial smoke tests
  - Test in simulation mode
  - **Status:** Not Started
  - **Estimate:** 2h

- [ ] **Task: Improve web UI**
  - Add status indicators (connection, state)
  - Display current head/antenna positions
  - Add emergency stop button
  - Improve styling
  - **Status:** Not Started
  - **Estimate:** 3h

- [ ] **Task: Add behavior state machine**
  - Define states (idle, scanning, tracking, etc.)
  - Implement state transitions
  - Add web UI controls for state switching
  - **Status:** Not Started
  - **Estimate:** 4h

### Medium Priority

- [ ] **Task: Add configuration file**
  - Create YAML/JSON config for parameters
  - Load config on startup
  - Allow runtime config reload
  - **Status:** Not Started
  - **Estimate:** 2h

- [ ] **Task: Implement data logging**
  - Log robot state to file
  - Log events and behaviors
  - Add log rotation
  - Create log viewer endpoint
  - **Status:** Not Started
  - **Estimate:** 3h

- [ ] **Task: Add choreographed movements**
  - Define movement sequences
  - Implement sequence player
  - Create library of preset moves
  - Add web UI to trigger sequences
  - **Status:** Not Started
  - **Estimate:** 5h

- [ ] **Task: Implement person tracking**
  - Integrate vision processing
  - Detect person positions
  - Calculate head angles to look at person
  - Smooth tracking with interpolation
  - **Status:** Not Started
  - **Estimate:** 8h

### Low Priority

- [ ] **Task: Add voice feedback**
  - Text-to-speech integration
  - Voice confirmation of actions
  - Custom voice personality
  - **Status:** Not Started
  - **Estimate:** 3h

- [ ] **Task: Create mobile-friendly UI**
  - Responsive design
  - Touch controls
  - Simplified mobile view
  - **Status:** Not Started
  - **Estimate:** 4h

- [ ] **Task: Add keyboard control**
  - WASD for manual head control
  - Arrow keys for antenna control
  - Hotkeys for behaviors
  - **Status:** Not Started
  - **Estimate:** 2h

---

## ✅ Completed Tasks

- [x] **Initial app setup**
  - Created basic ReachyMiniApp structure
  - Implemented sinusoidal head movement
  - Added antenna control
  - Created web UI with basic controls
  - **Completed:** December 9, 2025

---

## 💡 Feature Ideas (Future)

### Vision & Perception
- Face detection and recognition
- Object tracking
- Gesture recognition
- QR code reading for commands

### Autonomous Behaviors
- Random exploration patterns
- Obstacle avoidance (when sensors available)
- Return to home position
- Auto-sleep when idle

### Interaction
- Sound reactive behaviors
- Multi-user tracking
- Follow-me mode
- Interactive games (Simon says, etc.)

### Advanced Features
- Record and replay movements
- Learn from demonstrations
- Personality system (moods affecting behavior)
- Integration with LangGraph brain (future)

### Developer Tools
- Performance metrics dashboard
- Real-time debugging overlay
- Movement playback/visualization
- Behavior simulation mode

---

## 🐛 Known Issues

### Critical
- None

### Major
- None

### Minor
- Web UI needs better styling
- No error handling for daemon disconnection
- Missing input validation on web endpoints

---

## 📝 Technical Debt

- [ ] Add type hints throughout codebase
- [ ] Improve error handling
- [ ] Add docstrings to all functions
- [ ] Create unit tests
- [ ] Add CI/CD pipeline
- [ ] Document all API endpoints

---

## 📊 Progress Tracking

### Current Sprint Velocity
- **Planned:** TBD story points
- **Completed:** TBD story points
- **Remaining:** TBD story points

### Feature Completion
- Core mechanics: 80%
- Web UI: 40%
- Testing: 10%
- Documentation: 60%

---

## 🎨 Design Decisions

### Architecture
- **Pattern:** Single-threaded control loop with FastAPI server
- **Rationale:** Simple, predictable, easy to debug

### Control Loop Rate
- **Choice:** 50Hz (0.02s sleep)
- **Rationale:** Balance between responsiveness and CPU usage

### State Management
- **Choice:** Nonlocal variables for simple state
- **Future:** Consider proper state machine or reactive pattern

---

## 📚 Notes

### Development Environment
- Python 3.11+
- Reachy Mini SDK
- FastAPI for web server
- Daemon required (hardware or simulation)

### Testing Strategy
1. Unit tests for individual functions
2. Integration tests with simulation
3. Hardware validation before deployment

### Deployment Checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Version bumped in pyproject.toml
- [ ] CHANGELOG updated
- [ ] Tested on actual hardware
- [ ] Performance validated

---

*Last updated: December 9, 2025*
