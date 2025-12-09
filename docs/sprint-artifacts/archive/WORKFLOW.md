# Reachy Mini 2.0 - Development Workflow

## Overview
This document outlines the development workflow for the Reachy Mini 2.0 project, a LangGraph-powered autonomous AI robot.

## Project Structure

```
reachy_mini_robot/
├── src/                          # Application layer (new development)
│   └── reachy_mini_apps/        # Custom applications
├── src-refs/                     # Reference implementations (SDK/daemon)
│   ├── reachy_mini/             # Core SDK and daemon
│   ├── reachy_mini_conversation_app/
│   └── reachy_mini_toolbox/
├── docs/                         # Project documentation
│   ├── PRD.md                   # Product requirements
│   ├── master-documentation/    # Architecture & design
│   └── sprint-artifacts/        # Sprint planning & tracking
├── bmad-custom-src/             # Custom BMAD configurations
└── bmad-custom-modules-src/     # Custom BMAD modules
```

## Development Phases

### Phase 1: MVP (Current - 4-6 weeks)
**Goal:** Functional robot with social interaction, no wheels

**Core Features:**
- ✅ Vision detection (humans + objects)
- ✅ Speech-to-intent pipeline
- ✅ Social interaction skill
- ✅ LangGraph brain + state viewer
- ✅ Memory system (people + episodes)
- ✅ Emotion system
- ✅ Safety system (arms/head only)

### Phase 2: Mobility (Future)
- Add wheel support
- Navigation capabilities
- Extended exploration behaviors

### Phase 3: Advanced Features (Future)
- Enhanced memory systems
- Complex multi-agent reasoning
- Advanced personality modeling

## Workflow Process

### 1. Sprint Planning
Located in: `docs/sprint-artifacts/`

Each sprint includes:
- Sprint goals aligned with MVP/roadmap
- Epic breakdown (from arch-mvp-scope-epics-stories.md)
- Story point estimation
- Task assignment
- Testing criteria

### 2. Development Cycle

#### A. Using the Daemon
```bash
# Start hardware daemon
reachy-mini-daemon

# Or start in simulation mode
reachy-mini-daemon --sim

# With specific scene
reachy-mini-daemon --sim --scene minimal
```

#### B. SDK Development
```python
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

# Always use context manager
with ReachyMini() as reachy:
    pose = create_head_pose(yaw=30, pitch=10, roll=0)
    reachy.goto_target(pose, duration=2.0, method="minjerk")
```

#### C. Testing Workflow
```bash
# Run all tests (skip hardware markers if no hardware)
pytest -m "not audio and not video and not wireless"

# Run specific test suite
pytest tests/test_daemon.py

# With coverage
pytest --cov=reachy_mini tests/
```

#### D. Linting & Type Checking
```bash
# Lint with ruff
ruff check .

# Type checking
mypy --config-file pyproject.toml src/

# Format code
ruff format .
```

### 3. LangGraph Brain Development

The brain architecture consists of five node families:

1. **Perception Nodes** - Process sensor input
   - VisionNode
   - AudioIntentNode
   - ProximityNode
   - PoseEstimationNode (optional for wheels)

2. **Cognition Nodes** - Decision making
   - GoalManagerNode
   - PlannerNode
   - BehaviorSelectorNode

3. **Skill Nodes** - Behaviors
   - SocialInteractionSkillNode
   - DanceExpressiveSkillNode
   - FollowUserSkillNode (wheels)
   - NavigateToLocationSkillNode (wheels)
   - IdleExploreSkillNode (wheels)

4. **Execution Nodes** - Hardware control
   - SafetyFilterNode
   - MotorControllerNode
   - VoiceOutputNode

5. **Memory & Emotion Nodes** - State management
   - MemoryWriteNode
   - MemoryRecallNode
   - EmotionUpdateNode

### 4. Using BMAD Workflows

BMAD (BMad Method) provides AI-assisted development tools:

```bash
# Available in .bmad/bmb/workflows/
- create-workflow/    # Generate new workflow
- create-agent/       # Generate new agent
- edit-workflow/      # Modify existing workflow
- workflow-compliance-check/  # Validate workflow
```

Custom configurations in: `bmad-custom-src/custom.yaml`

### 5. Git Workflow

```bash
# Main branches
develop    # Active development (current)
main       # Stable releases

# Feature branches
feature/node-name           # New LangGraph nodes
feature/skill-name          # New robot skills
bugfix/issue-description    # Bug fixes
docs/documentation-update   # Documentation only
```

### 6. Code Review Checklist

- [ ] Follows existing code patterns in src-refs/reachy_mini/
- [ ] Respects motor limits (head ±40° pitch/roll, ±180° yaw)
- [ ] Uses context managers for ReachyMini connections
- [ ] Includes docstrings (D203/D213 style)
- [ ] Passes ruff and mypy checks
- [ ] Has appropriate test coverage
- [ ] Updates relevant documentation
- [ ] Safety checks in place (SafetyFilterNode for motions)

### 7. Documentation Updates

When adding features:
1. Update relevant docs in `docs/master-documentation/`
2. Add examples to `src-refs/reachy_mini/examples/`
3. Update API docs if SDK changes
4. Keep architecture diagrams current

## Common Development Tasks

### Adding a New Skill Node
1. Define node class inheriting from base
2. Implement perception → action logic
3. Update BrainState schema if needed
4. Add to BehaviorSelectorNode routing
5. Write unit tests
6. Add example usage
7. Document in architecture

### Adding New Hardware Feature
1. Update daemon hardware abstraction
2. Add SDK wrapper methods
3. Implement safety limits
4. Test in simulation first
5. Validate on hardware
6. Update REST API docs

### Extending Memory System
1. Define new memory schema
2. Implement storage/retrieval nodes
3. Add to MemoryWriteNode/MemoryRecallNode
4. Test persistence
5. Document memory structure

## Troubleshooting

See: `src-refs/reachy_mini/docs/troubleshooting.md`

Common issues:
- Daemon not connecting: Check udev rules on Linux
- Motor limits: Head ±40° pitch/roll, body-to-head yaw ±65°
- WebSocket disconnects: Check daemon is running
- Simulation lag: Reduce scene complexity

## Resources

### Documentation
- PRD: `docs/PRD.md`
- Architecture: `docs/master-documentation/arch-mvp-scope-epics-stories.md`
- Python SDK: `src-refs/reachy_mini/docs/python-sdk.md`
- REST API: `src-refs/reachy_mini/docs/rest-api.md`

### Examples
- Basic motions: `src-refs/reachy_mini/examples/minimal_demo.py`
- Interpolation: `src-refs/reachy_mini/examples/goto_interpolation_playground.py`
- Vision: `src-refs/reachy_mini/examples/look_at_image.py`
- Recording: `src-refs/reachy_mini/examples/recorded_moves_example.py`

### Development Tools
- Daemon: `reachy-mini-daemon`
- Conversation app: `reachy-mini-conversation-app`
- BMAD workflows: `.bmad/bmb/workflows/`

## Support & Communication

- Repository: pollen-robotics/reachy_mini
- Branch: develop
- Questions: Check troubleshooting.md first

---

*Last updated: December 9, 2025*
