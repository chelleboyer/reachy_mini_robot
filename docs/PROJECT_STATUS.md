# Reachy Mini 2.0 - Project Status

**Last Updated:** January 9, 2025  
**Repository:** https://github.com/chelleboyer/reachy_mini_robot.git  
**Branch:** main

---

## 🎯 Current Status

**Phase:** Foundation & Perception (Weeks 1-3)  
**Overall Progress:** 6/21 stories (29%)  
**Latest Milestone:** ✅ Epic 2 (Vision Perception Layer) Complete

---

## 📊 Epic Progress

| Epic | Status | Stories | Completion | Git Commits |
|------|--------|---------|------------|-------------|
| **Epic 1: Foundation & LangGraph Brain** | ✅ Done | 3/3 | 100% | a4ec784 |
| **Epic 2: Vision Perception Layer** | ✅ Done | 3/3 | 100% | 8067ef1, ba2cc7a, 6e8b67e |
| **Epic 3: Audio & Intent Processing** | ⏳ Next | 0/2 | 0% | - |
| Epic 4: Social Interaction Skills | 📋 Planned | 0/3 | 0% | - |
| Epic 5: Memory System | 📋 Planned | 0/3 | 0% | - |
| Epic 6: Emotion & Behavior | 📋 Planned | 0/3 | 0% | - |
| Epic 7: Cognition & Goals | 📋 Planned | 0/2 | 0% | - |
| Epic 8: Safety & Polish | 📋 Planned | 0/2 | 0% | - |

---

## ✅ Completed Work

### Epic 1: Project Foundation & LangGraph Brain Setup (100%)

**Completed:** January 2025  
**Commit:** a4ec784

**Stories:**
- ✅ 1.1: Initialize brain directory structure
- ✅ 1.2: Implement BrainState data model
- ✅ 1.3: Create LangGraph orchestrator

**Key Deliverables:**
- Brain architecture with 9 modules (perception, cognition, skills, execution, memory, utils, models)
- BrainState Pydantic model (380 lines, 8 sections, 25 unit tests)
- LangGraph StateGraph orchestrator (214 lines, 20+ unit tests)
- Demo entry point showing graph execution
- Full dependency setup (langgraph, pydantic, qdrant-client, etc.)

**Files Created:**
```
brain/
├── __init__.py
├── README.md
├── main.py (90 lines)
├── graph.py (214 lines)
├── models/
│   ├── __init__.py
│   └── state.py (380 lines)
├── nodes/
│   ├── perception/
│   ├── cognition/
│   ├── skills/
│   ├── execution/
│   └── memory/
└── utils/
tests/
├── test_brain_state.py (350 lines, 25 tests)
└── test_graph.py (230 lines, 20+ tests)
```

---

### Epic 2: Vision Perception Layer (100%)

**Completed:** January 9, 2025  
**Commits:** 8067ef1, ba2cc7a, 6e8b67e

**Stories:**
- ✅ 2.1: Implement face detection node (YOLO)
- ✅ 2.2: Implement face tracking & position estimation
- ✅ 2.3: Implement head orientation calculation

**Key Deliverables:**
- Face detection with YOLOv11n-nano from HuggingFace (220 lines, 25 tests)
- Face tracking with persistent IDs & centroid matching (310 lines, 30+ tests)
- 3D position estimation from bounding boxes (pinhole camera model)
- Primary face selection with weighted scoring (centrality + size + confidence)
- Head orientation kinematics (330 lines, 39 tests)
  - calculate_look_at_angles() - atan2-based angle calculation
  - apply_safety_limits() - ±40° pitch/roll, ±65° body-relative yaw
  - smooth_transition() - ease-in-out cubic interpolation
- Cognition node integration for primary human tracking
- Full perception → cognition pipeline operational

**Files Created:**
```
brain/nodes/perception/
├── vision_node.py (220 lines)
└── face_tracker.py (310 lines)
brain/utils/
└── kinematics.py (330 lines)
tests/
├── test_vision_node.py (225 lines, 25 tests)
├── test_face_tracker.py (380 lines, 30+ tests)
└── test_kinematics.py (280 lines, 39 tests)
```

**Files Modified:**
```
brain/graph.py - cognition_node with head orientation
brain/utils/__init__.py - kinematics exports
brain/models/state.py - Human.persistent_id, tracking_confidence
```

**Test Results:**
- Face detection: 25/25 tests passing
- Face tracking: 30/30 tests passing
- Kinematics: 39/39 tests passing
- **Total: 94/94 vision tests passing (100%)**

---

## 🔧 Technical Stack

### Core Technologies
- **LangGraph** 0.2.0+ - Multi-agent orchestration
- **Pydantic** 2.0+ - Type-safe data models
- **Qdrant** 1.7.0+ - Vector database (ready, not yet used)
- **sentence-transformers** 2.0.0+ - Embeddings (ready, not yet used)

### Vision (Epic 2)
- **YOLO** - Face detection (YOLOv11n-nano via HuggingFace)
- **NumPy** - Position calculations & centroid tracking
- **Supervision** 0.18.0+ - Detection utilities

### Planned (Epic 3+)
- **Whisper** - Speech-to-text
- **Porcupine** - Wake word detection
- **llama.cpp** - Local LLM inference

### Hardware
- **Platform:** Raspberry Pi 5 + Hailo HAT (26 TOPS)
- **Robot:** Reachy Mini (USB wired, wireless support planned)
- **Storage:** 2TB USB SSD for memory/models

---

## 📈 Code Metrics

### Production Code
- **Epic 1:** ~670 lines
- **Epic 2:** ~860 lines
- **Total:** ~1,530 lines

### Test Code
- **Epic 1:** ~580 lines, 45+ tests
- **Epic 2:** ~885 lines, 94 tests
- **Total:** ~1,465 lines, 139+ tests

### Test Coverage
- All modules have comprehensive unit tests
- 100% pass rate across all tests
- Integration tests for graph execution

---

## 🎯 Next Steps

### Immediate (Epic 3: Audio & Intent Processing)

**Story 3.1: Implement Wake Word Detection**
- Audio capture from microphone
- Porcupine integration for wake word ("Hey Reachy")
- Trigger conversation mode
- Update BrainState.sensors.audio

**Story 3.2: Implement Speech-to-Intent Pipeline**
- Whisper integration for speech-to-text
- LLM intent classification
- Update BrainState.interaction.user_intent
- Memory context integration

**Timeline:** Week 3 (January 2025)

---

### Upcoming Milestones

**Week 4: Epic 4 - Social Interaction Skills**
- 🎯 **AUTONOMOUS DEMO MILESTONE**
- See face → hear speech → respond with gesture + voice
- Requires Epic 2 (vision) + Epic 3 (audio) complete

**Weeks 5-6: Epics 5-7 - Intelligence Layer**
- Memory system (person recognition, episodic memory)
- Emotion & behavior (idle behaviors, emotion modulation)
- Cognition & goals (goal management, behavior selection)

**Week 7: Epic 8 - Safety & Polish**
- Safety filter enforcement
- End-to-end integration
- Performance validation

---

## 📝 Documentation

### Available Documentation
- ✅ `docs/PRD.md` - Product requirements
- ✅ `docs/epics.md` - Epic & story breakdown
- ✅ `docs/README.md` - Documentation index
- ✅ `docs/sprint-artifacts/` - Sprint tracking & story completion reports
  - `sprint-status.yaml` - Current sprint status
  - `epic-1-completed.md` - Epic 1 completion report
  - `story-2.1-completed.md` - Face detection completion
  - `story-2.2-completed.md` - Face tracking completion
  - `story-2.3-completed.md` - Head orientation completion
- ✅ `docs/master-documentation-ideation/` - Architecture details

### Story Completion Reports
Each completed story has a comprehensive report:
- Acceptance criteria validation
- Implementation details
- Test results
- Performance analysis
- Files created/modified
- Next steps

---

## 🐛 Known Issues

None currently. All implemented features are tested and operational.

---

## 🔗 Resources

- **Repository:** https://github.com/chelleboyer/reachy_mini_robot.git
- **Reachy Mini SDK:** `src-refs/reachy_mini/` (read-only reference)
- **Examples:** `src-refs/reachy_mini/examples/`
- **SDK Docs:** `src-refs/reachy_mini/docs/`

---

## 👥 Contributors

- Michelle Boyer (chelleboyer) - Lead Developer
- GitHub Copilot - AI Assistant

---

*This document is automatically updated after each epic/story completion.*
