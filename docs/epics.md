---
stepsCompleted: [1, 2, 3, 4]
workflowStatus: complete
lastUpdated: "2025-01-09"
implementationProgress:
  epic1: complete (3/3 stories - 100%)
  epic2: complete (3/3 stories - 100%)
  epic3: not-started (0/2 stories - 0%)
  overallProgress: 6/21 stories (29%)
inputDocuments:
  - docs/PRD.md
  - docs/master-documentation-ideation/arch-mvp-scope-epics-stories.md
  - docs/master-documentation-ideation/rmlg-ideation.md
  - docs/master-documentation-ideation/state-object-brain.md
  - docs/master-documentation-ideation/diagram-nodes-edges.md
  - docs/master-documentation-ideation/runtime-behaviors-sequencing.md
  - docs/master-documentation-ideation/production-grade-plan.md
mvpScope: social-interaction-no-wheels
hardwarePlatform: raspberry-pi-5-with-hailo-hat
computeEnvironment: offboard
---

# Reachy Mini 2.0 - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for **Reachy Mini 2.0**, an embodied LangGraph-powered autonomous AI robot focused on **social interaction** as the v1 core capability. This implementation uses the **reachy_mini_ranger** template as a foundation and extends it with intelligent perception, cognition, and expressive behaviors.

**Hardware Platform:** 
- **Current (Development):** Reachy Mini USB wired (lite) version + Raspberry Pi 5 + 26 TOPS Hailo HAT + 2TB USB SSD
- **Future (Deployment):** Reachy Mini wireless version (can also run wired) + same RPi5 setup
- Architecture must support BOTH wired and wireless modes

**Compute Strategy:** Offboard to RPi5 (daemon + brain on RPi5, motor control on robot)  
**Connection Modes:** USB wired (now) + WiFi wireless (future) - SDK handles transport layer  
**MVP Scope:** Social interaction WITHOUT wheels (head, antennas, voice, vision, memory, emotion)

**Tech Stack:**
- **LangGraph** - Multi-agent orchestration
- **Qdrant** - Vector database for semantic memory & face embeddings
- **sentence-transformers** - Text embeddings (all-MiniLM-L6-v2)
- **llama.cpp** - Local LLM inference (quantized models)
- **Hailo HAT** - Vision inference (26 TOPS)
- **Pydantic v2** - Type-safe data models

---

## Requirements Inventory

### Functional Requirements

**FR1:** Robot must detect and recognize human faces in real-time using vision  
**FR2:** Robot must extract user intent from speech input via wake word or continuous listening  
**FR3:** Robot must respond to user with coordinated speech and expressive gestures (head, antennas)  
**FR4:** Robot must maintain a BrainState data structure shared across all nodes  
**FR5:** Robot must implement a LangGraph-based multi-agent brain with perception, cognition, skill, execution, and memory nodes  
**FR6:** Robot must store memories of recognized people, interactions, and preferences  
**FR7:** Robot must recall memories during conversations to provide context-aware responses  
**FR8:** Robot must maintain an emotional state (valence + arousal) that modulates behavior  
**FR9:** Robot must display idle/exploratory behaviors when not actively engaged  
**FR10:** Robot must pass all motor commands through a safety filter before execution  
**FR11:** Robot must track user face position and orient head to maintain eye contact  
**FR12:** Robot must generate speech responses using text-to-speech  
**FR13:** Robot must coordinate multiple expressive channels (voice, head, antennas, LEDs if available)  
**FR14:** Robot must support goal-based reasoning (create, prioritize, execute goals)  
**FR15:** Robot must select appropriate behaviors based on context, emotion, and goals  

### Non-Functional Requirements

**NFR1:** Perception to motor output latency must be < 200ms  
**NFR2:** Memory recall must complete in < 50ms  
**NFR3:** Audio intent detection must process in < 200ms  
**NFR4:** All motor movements must respect safety limits (head ±40° pitch/roll, ±180° yaw, body-head yaw diff ±65°)  
**NFR5:** System must handle vision processing at minimum 10 FPS on Hailo HAT  
**NFR6:** Robot must operate reliably with onboard compute (no cloud dependency for core functions)  
**NFR7:** Code must follow existing reachy_mini SDK patterns and respect src-refs/ as read-only  
**NFR8:** Safety filter must be impossible to bypass by any node  
**NFR9:** System must gracefully handle sensor failures (vision loss, audio dropout)  
**NFR10:** Memory system must persist data to 2TB SSD with proper error handling  

### Additional Requirements from Architecture

**ARCH1:** Use `reachy_mini_ranger` template structure in `src/reachy_mini_apps/reachy_mini_ranger/` as starting point  
**ARCH2:** Implement LangGraph brain as subdirectory `brain/` within ranger app  
**ARCH3:** BrainState must use Pydantic models for type safety and validation  
**ARCH4:** Nodes must be stateless - all state lives in BrainState  
**ARCH5:** Vision processing must leverage Hailo HAT for face detection (YOLO, MediaPipe, or similar) on RPi5  
**ARCH6:** Daemon runs on RPi5, connects to robot via USB (wired/lite version) or WiFi (wireless version) - SDK handles transport transparently  
**ARCH7:** Camera/audio streams use SDK media backend (OpenCV+sounddevice for wired, GStreamer for wireless) - abstracted by SDK  
**ARCH8:** Application code must be transport-agnostic - no hardcoded wired/wireless assumptions  
**ARCH9:** LLM inference should use quantized models optimized for edge (Llama.cpp, GGUF format) on RPi5  
**ARCH10:** Memory storage should use Qdrant vector database on 2TB SSD for semantic search and face embeddings  
**ARCH11:** Each node must produce trace events for debugging and monitoring  
**ARCH12:** Safety limits must be enforced at hardware abstraction layer (SDK handles this)  
**ARCH13:** Install GStreamer dependencies on RPi5 for media streaming (see src-refs/reachy_mini/docs/RPI.md)  

### FR Coverage Map

| Epic | Stories | Functional Requirements Covered |
|------|---------|----------------------------------|
| Epic 1: Project Foundation | 3 stories | FR4, ARCH1, ARCH2, ARCH3 |
| Epic 2: Vision Perception Layer | 3 stories | FR1, FR11, NFR5, ARCH5 |
| Epic 3: Audio & Intent Processing | 2 stories | FR2, NFR3, ARCH7, ARCH8, ARCH9 |
| Epic 4: Social Interaction Skills | 3 stories | FR3, FR12, FR13 (uses FR1, FR2) |
| Epic 5: Memory System | 3 stories | FR6, FR7, NFR2, ARCH10, NFR10 |
| Epic 6: Emotion & Behavior | 3 stories | FR8, FR9 |
| Epic 7: Cognition & Goal Management | 2 stories | FR14, FR15 |
| Epic 8: Safety, Integration & Polish | 2 stories | FR10, NFR1, NFR4, NFR8, NFR9, ARCH12 |

---

## Epic List

**Development Strategy:** Sequential - perception foundation before social demo

**Phase 1: Foundation & Core Infrastructure (Week 1)**
1. **Epic 1: Project Foundation & LangGraph Brain Setup**

**Phase 2: Perception Layer (Weeks 2-3)**
2. **Epic 2: Vision Perception Layer**
3. **Epic 3: Audio & Intent Processing**

**Phase 3: Social Interaction (Week 4)**
4. **Epic 4: Social Interaction Skills** ← AUTONOMOUS DEMO MILESTONE

**Phase 4: Intelligence & Memory (Weeks 5-6)**
5. **Epic 5: Memory System**
6. **Epic 6: Emotion & Behavior System**
7. **Epic 7: Cognition & Goal Management**

**Phase 5: Polish & Integration (Week 7)**
8. **Epic 8: Safety, Integration & Polish**

---

## Epic 1: Project Foundation & LangGraph Brain Setup ✅ COMPLETE

**Status:** ✅ Done (3/3 stories completed - 100%)  
**Completed:** January 2025  
**Git Commit:** a4ec784

**Goal:** Establish the foundational project structure, BrainState data model, and LangGraph orchestration framework that all subsequent features will build upon.

**Value:** Without this foundation, we cannot implement the intelligent brain architecture. This epic creates the "operating system" for the robot's intelligence.

**Deliverables:**
- Brain directory structure with 9 modules (perception, cognition, skills, execution, memory, utils, models)
- BrainState Pydantic model with 8 sections (380 lines, 25 unit tests)
- LangGraph StateGraph orchestrator (214 lines, 20+ unit tests)
- Demo entry point (brain/main.py) showing graph execution
- Full test coverage (tests/test_brain_state.py, tests/test_graph.py)

### Story 1.1: Initialize Brain Directory Structure

As a **developer**,  
I want **a well-organized directory structure for the brain modules**,  
So that **I can develop nodes in isolation and maintain clean separation of concerns**.

**Acceptance Criteria:**

**Given** the reachy_mini_ranger template exists  
**When** I initialize the brain directory structure  
**Then** the following directories are created:
- `reachy_mini_ranger/brain/`
- `reachy_mini_ranger/brain/models/` (for BrainState)
- `reachy_mini_ranger/brain/nodes/perception/`
- `reachy_mini_ranger/brain/nodes/cognition/`
- `reachy_mini_ranger/brain/nodes/skills/`
- `reachy_mini_ranger/brain/nodes/execution/`
- `reachy_mini_ranger/brain/nodes/memory/`
- `reachy_mini_ranger/brain/utils/`

**And** each directory contains appropriate `__init__.py` files  
**And** a README.md exists at `brain/README.md` documenting the architecture  
**And** pyproject.toml is updated with new dependencies (langgraph, pydantic, etc.)

**Implementation Tasks:**

1. Create directory structure with all brain/ subdirectories
2. Add `__init__.py` to all directories with docstrings explaining purpose
3. Create `brain/README.md` documenting:
   - Architecture overview (5 node families: perception, cognition, skills, execution, memory)
   - BrainState flow pattern (shared state across all nodes)
   - Development guidelines (node creation, testing patterns)
4. Update `pyproject.toml` dependencies:
   - Add: `langgraph`, `langchain-core`, `pydantic>=2.0`, `qdrant-client`, `sentence-transformers`
   - Ensure existing: `reachy_mini` SDK dependency
5. Create `.gitignore` entries for brain artifacts (logs/, cache/, qdrant_storage/)

---

### Story 1.2: Implement BrainState Data Model

As a **developer**,  
I want **a comprehensive BrainState Pydantic model**,  
So that **all nodes can read/write structured, type-safe data with validation**.

**Acceptance Criteria:**

**Given** the brain/models/ directory exists  
**When** I create the BrainState model  
**Then** the model includes these top-level sections:
- `sensors` (vision, audio, proximity, imu)
- `world_model` (objects, humans, self_pose)
- `interaction` (user_intent, user_id, conversation_context)
- `goals` (list of goal objects with id, type, priority, status)
- `current_plan` (goal_id, steps, active_step)
- `emotion` (arousal, valence, traits)
- `actuator_commands` (head, antennas, voice, leds)
- `metadata` (timestamp, mode, logs)

**And** each nested section uses Pydantic BaseModel subclasses  
**And** all fields have type hints and optional default values  
**And** the model validates on instantiation  
**And** unit tests verify model creation and validation

**Implementation Tasks:**

1. Create `brain/models/state.py` with BrainState class
2. Define nested Pydantic models: SensorData, WorldModel, InteractionState, Goal, Plan, EmotionState, ActuatorCommands, Metadata
3. Add validation rules: head angle limits (±40° pitch/roll, ±180° yaw), required fields with defaults, auto-timestamp
4. Create factory helpers: `create_initial_state()`, `update_timestamp()`
5. Write unit tests in `tests/test_brain_state.py`: instantiation, validation, serialization

---

### Story 1.3: Create LangGraph Orchestrator

As a **developer**,  
I want **a LangGraph StateGraph that orchestrates node execution**,  
So that **perception → cognition → skills → execution flows automatically**.

**Acceptance Criteria:**

**Given** BrainState model exists  
**When** I create the graph orchestrator in `brain/graph.py`  
**Then** the graph is initialized with BrainState as the state schema  
**And** placeholder node functions are defined for each node category  
**And** edges connect nodes in the correct sequence:
  - START → perception nodes → cognition nodes → skill nodes → execution nodes → END
**And** the graph compiles without errors  
**And** I can invoke the graph with initial BrainState and get updated state back  
**And** unit tests verify graph compilation and basic invocation

**Implementation Tasks:**

1. Create `brain/graph.py` with StateGraph initialization using BrainState schema
2. Define placeholder node functions for each category (perception_node, cognition_node, skill_node, execution_node) that pass state through
3. Add edges: START → perception → cognition → skills → execution → END
4. Implement `compile_graph()` function returning compiled graph
5. Create `brain/main.py` entry point that loads graph and runs test invocation
6. Write unit tests in `tests/test_graph.py`: compilation succeeds, invocation with initial state returns updated state

---

## Epic 2: Vision Perception Layer ✅ COMPLETE

**Status:** ✅ Done (3/3 stories completed - 100%)  
**Completed:** January 2025  
**Git Commits:** 8067ef1 (Story 2.1), ba2cc7a (Story 2.2), 6e8b67e (Story 2.3)

**Goal:** Enable the robot to see and understand its environment, specifically detecting and tracking human faces in real-time using the Hailo HAT accelerator.

**Value:** Vision is the primary sensory input for social interaction. Face detection enables eye contact, user tracking, and attention behaviors. Building this FIRST ensures social demo uses real data.

**Deliverables:**
- Face detection with YOLO (YOLOv11n-nano from HuggingFace, 220 lines, 25 unit tests)
- Face tracking with persistent IDs & 3D position estimation (310 lines, 30+ unit tests)
- Head orientation calculation with kinematics (330 lines, 39 unit tests)
- Cognition node integration for primary human tracking
- Full perception → cognition pipeline operational
- Total: ~860 production lines + ~900 test lines

### Story 2.1: Implement Face Detection Node (Hailo HAT)

As a **robot**,  
I want **to detect human faces in camera frames using Hailo-accelerated inference**,  
So that **I can identify when people are present and where they are located**.

**Acceptance Criteria:**

**Given** Raspberry Pi 5 with Hailo HAT is available  
**When** VisionNode processes a camera frame  
**Then** face detection runs at minimum 10 FPS  
**And** detected faces are returned with bounding boxes (x, y, width, height)  
**And** confidence scores are included for each detection  
**And** results are written to `BrainState.sensors.vision.faces`  
**And** face data includes: face_id, position, confidence, timestamp  
**And** no faces returns empty list without errors  
**And** integration test verifies detection with test images

**Implementation Tasks:**

1. Create `brain/nodes/perception/vision_node.py` with FaceDetectionNode class
2. Initialize Hailo HAT inference: load face detection model (YOLO/similar), set up camera (OpenCV/GStreamer), configure for 10+ FPS
3. Implement `detect_faces(frame)` method: run inference, parse bounding boxes/confidence, return Face objects
4. Integrate with BrainState: write to `BrainState.sensors.vision.faces`, handle empty detections
5. Add to LangGraph: register as perception node, update edges
6. Write tests in `tests/test_vision_node.py`: detection with test images, no faces case, FPS benchmark

---

### Story 2.2: Implement Face Tracking & Position Estimation

As a **robot**,  
I want **to track detected faces across frames and estimate their 3D position**,  
So that **I can maintain awareness of specific individuals and orient toward them**.

**Acceptance Criteria:**

**Given** faces are detected in multiple sequential frames  
**When** VisionNode processes the tracking logic  
**Then** faces are assigned persistent IDs across frames  
**And** 3D position (x, y, z relative to robot) is estimated using camera intrinsics  
**And** primary face (closest or most central) is identified  
**And** tracking data is written to `BrainState.world_model.humans`  
**And** each human entry includes: human_id, position, face_id, last_seen_timestamp  
**And** faces disappearing for > 2 seconds are marked as inactive  
**And** unit tests verify tracking persistence and position calculation

**Implementation Tasks:**

1. Extend `vision_node.py` with tracking logic using centroid-based algorithm or SORT tracker
2. Implement `track_faces(current_faces, previous_humans)` method: assign persistent IDs, update existing tracks, expire stale tracks (>2s)
3. Add 3D position estimation: use camera intrinsics + bounding box size to estimate (x, y, z) relative to robot
4. Implement `identify_primary_human()` method: select closest or most central face
5. Update BrainState: write to `BrainState.world_model.humans` with full human data structure
6. Write tests: ID persistence across frames, position calculation accuracy, stale track expiration

---

### Story 2.3: Implement Head Orientation Calculation

As a **robot**,  
I want **to calculate head angles needed to look at detected faces**,  
So that **I can maintain eye contact during social interactions**.

**Acceptance Criteria:**

**Given** a human position exists in world_model  
**When** VisionNode calculates head orientation  
**Then** yaw, pitch, roll angles are computed to orient head toward human  
**And** angles respect safety limits (±40° pitch/roll, ±180° yaw)  
**And** angles are written to `BrainState.actuator_commands.head`  
**And** calculation accounts for current head position (smooth transitions)  
**And** if no humans detected, head returns to neutral or idle position  
**And** unit tests verify angle calculation with various positions  
**And** integration test shows head actually moves toward detected face

**Implementation Tasks:**

1. Create `brain/utils/kinematics.py` with head orientation calculation functions
2. Implement `calculate_look_at_angles(human_position, current_head_pose)` method: compute yaw/pitch/roll to orient toward target
3. Add safety clamping: enforce ±40° pitch/roll, ±180° yaw limits
4. Implement smooth transition logic: calculate delta from current position, apply easing for natural motion
5. Update vision_node to call kinematics and write angles to `BrainState.actuator_commands.head`
6. Add idle behavior: return to neutral (0, 0, 0) or scanning pattern when no humans present
7. Write tests: angle calculation correctness, safety limits enforced, smooth transitions
8. Integration test: spawn vision node, inject test face position, verify head moves correctly

---

## Epic 3: Audio & Intent Processing

**Goal:** Enable the robot to listen to speech, understand user intent, and trigger appropriate responses.

**Value:** Speech is the primary input channel for commands and conversation. Intent extraction enables context-aware responses. Built on real vision data from Epic 2.

### Story 3.1: Implement Wake Word Detection

As a **user**,  
I want **to wake the robot with a specific phrase**,  
So that **it only listens when I'm addressing it directly**.

**Acceptance Criteria:**

**Given** microphone is active  
**When** user says the wake word (e.g., "Hey Reachy")  
**Then** wake word is detected within 200ms  
**And** robot transitions to active listening mode  
**And** visual/audio feedback confirms activation (LED, tone, or head gesture)  
**And** `BrainState.interaction.listening_active` is set to True  
**And** false positive rate is < 5% in normal household noise  
**And** detection works with various accents and volumes  
**And** unit test verifies detection with audio samples

**Implementation Tasks:**

1. Create `brain/nodes/perception/audio_node.py` with WakeWordDetector class
2. Initialize wake word engine: Porcupine/Snowboy/openWakeWord, load "Hey Reachy" model, set up microphone stream
3. Implement `detect_wake_word(audio_stream)` method: monitor for wake word, return confidence, <200ms latency
4. Integrate with BrainState: set `listening_active = True`, trigger feedback (LED/tone) in actuator_commands
5. Add to LangGraph: register as perception node, add state transition logic
6. Write tests: positive detection samples, false positive rate (<5%), latency benchmark

---

### Story 3.2: Implement Speech-to-Intent Pipeline

As a **robot**,  
I want **to convert user speech to structured intent**,  
So that **I can understand commands, questions, and conversation topics**.

**Acceptance Criteria:**

**Given** audio is captured after wake word  
**When** AudioIntentNode processes the speech  
**Then** speech is transcribed to text using local STT model  
**And** text is analyzed by local LLM to extract intent  
**And** intent structure includes: intent_type, entities, confidence  
**And** common intent types recognized: command, question, greeting, farewell, small_talk  
**And** processing completes in < 200ms for short phrases  
**And** integration test verifies intent extraction for sample commands

**Implementation Tasks:**

1. Extend `audio_node.py` with SpeechToIntentNode class
2. Initialize local STT: Whisper.cpp or Vosk for on-device transcription
3. Implement `transcribe_speech(audio_buffer)` method: convert audio to text, handle silence/noise
4. Create intent extraction with local LLM (lightweight quantized model): classify intent type (greeting/question/command/farewell/small_talk)
5. Extract entities: user requests, topics, sentiment
6. Update BrainState: write to `interaction.user_intent` with full structure (type, text, entities, confidence)
7. Add audio buffer management: record after wake word, stop on silence (>1s)
8. Write tests: transcription accuracy, intent classification, latency (<200ms), edge cases
9. Integration test: wake word → transcription → intent extraction

---

## Epic 4: Social Interaction Skills

**Goal:** Enable the robot to respond to users with coordinated speech, gestures, and expressive movements using REAL vision and audio data from Epics 2-3.

**Value:** This is the CORE v1 capability. Combines real perception with engaging responses. First fully autonomous interaction demo.

### Story 4.1: Implement Social Response Generation

As a **robot**,  
I want **to generate contextually appropriate responses to user intents**,  
So that **conversations feel natural and engaging**.

**Acceptance Criteria:**

**Given** user_intent exists in BrainState (from real audio - Epic 3)  
**And** human_id exists in world_model (from real vision - Epic 2)  
**When** SocialInteractionSkillNode processes the intent  
**Then** appropriate response text is generated using LLM  
**And** response considers: conversation_context, user_id (if known), detected human position  
**And** response text is written to `BrainState.actuator_commands.voice.text`  
**And** response generation completes in < 500ms  
**And** unit tests verify response generation for various intents

**Implementation Tasks:**

1. Create `brain/nodes/skills/social_interaction_node.py` with ResponseGenerator class
2. Initialize local LLM: load quantized model (Llama 3B/Phi-3 Mini) via llama.cpp
3. Implement `generate_response(intent, context)` method: build prompt with user_intent, conversation_context, human info
4. Add personality to system prompt: friendly, curious, helpful, concise
5. Handle intent types: greetings, questions, commands, farewells
6. Update BrainState: write to `actuator_commands.voice.text`
7. Add response caching for common intents
8. Write tests: response quality, latency (<500ms), various intent types

---

### Story 4.2: Implement Gesture Coordination

As a **robot**,  
I want **to coordinate head and antenna movements with speech**,  
So that **my physical expressions reinforce verbal communication**.

**Acceptance Criteria:**

**Given** a speech response is being generated  
**And** human position is known from vision  
**When** SocialInteractionSkillNode selects gestures  
**Then** appropriate gestures are chosen based on intent:  
  - Greeting → head nod + look at person
  - Question → head tilt + look at person
  - Affirmation → head nod while maintaining eye contact
  - Surprise → antennas raise + head back
**And** head orientation uses real face position from Epic 2  
**And** gesture timing is synchronized with speech  
**And** gesture commands are written to `BrainState.actuator_commands.head` and `antennas`  
**And** gestures respect safety limits  
**And** integration test shows coordinated speech + gesture + eye contact

**Implementation Tasks:**

1. Extend `social_interaction_node.py` with GestureCoordinator class
2. Create gesture library: map intent types to movements (greeting, question, affirmation, surprise)
3. Implement `select_gesture(intent_type, human_position)` method: choose gesture, incorporate face position
4. Add timing synchronization: start before speech, hold during, return after
5. Update BrainState: write to `actuator_commands.head` and `antennas` with timing
6. Ensure safety: clamp angles within limits
7. Write tests: gesture selection, timing, safety, coordination

---

### Story 4.3: Implement End-to-End Autonomous Interaction

As a **user**,  
I want **the robot to see me, hear me, and respond naturally**,  
So that **I experience a complete autonomous social interaction**.

**Acceptance Criteria:**

**Given** the complete system is running with Epics 1-3 integrated  
**When** user approaches the robot  
**Then** robot detects face and looks at user (Epic 2)  
**And** user says wake word + command  
**And** robot recognizes speech and extracts intent (Epic 3)  
**And** robot generates appropriate response (Epic 4)  
**And** robot speaks with synchronized gestures while maintaining eye contact  
**And** complete interaction loop completes in < 2 seconds from speech to response  
**And** integration test validates full autonomous flow:  
  1. Person walks into view → robot looks at them
  2. Person says "Hey Reachy, how are you?" → robot responds "I'm doing great! Nice to see you!"
  3. Robot maintains eye contact during speech
  4. Robot returns to idle scanning when person leaves
**And** README includes demonstration video and setup instructions

**Implementation Tasks:**

1. Create `brain/nodes/execution/actuator_node.py` with VoiceOutputNode and MotorControllerNode
2. Implement VoiceOutputNode: TTS engine (piper/espeak), `speak(text)` method, timing metadata
3. Implement MotorControllerNode: ReachyMini SDK connection, `execute_head_motion()`, `execute_antenna_motion()` with interpolation
4. Create orchestration: coordinate timing (gesture → 200ms → speech)
5. Add execution nodes to LangGraph
6. Write full_autonomous_interaction integration test: person approaches → vision → audio → response → execution (measure <2s latency)
7. Create demo script and record video for README

---

## Epic 5: Memory System

**Goal:** Enable the robot to remember people, past interactions, and preferences, creating continuity across sessions.

**Value:** Memory is what makes the robot feel like it knows you. It's the foundation for long-term relationships.

### Story 5.1: Implement Person Recognition & Storage

As a **robot**,  
I want **to recognize individuals and store their identity**,  
So that **I can greet them by name in future interactions**.

**Acceptance Criteria:**

**Given** a face is detected and tracked  
**When** MemoryWriteNode processes the person  
**Then** face embeddings are generated for recognition  
**And** person record is created in Qdrant collection `people` with: person_id, name, face_embedding, first_seen, last_seen  
**And** if person is recognized (embedding match via cosine similarity), existing record is updated  
**And** if person is new, they are stored with temporary ID until named  
**And** `BrainState.world_model.humans` is enriched with person_id  
**And** vector search operations complete in < 50ms  
**And** unit tests verify storage and retrieval

**Implementation Tasks:**

1. Create `brain/nodes/memory/person_memory_node.py` with PersonRecognitionNode class
2. Initialize Qdrant: create local client with storage path on 2TB SSD, create collection `people` with vector config (size=128/512, distance=Cosine)
3. Add face recognition model: use dlib/face_recognition library or Hailo-compatible model for face embedding extraction
4. Implement `generate_embedding(face_image)` method: extract 128/512-dim face embedding vector
5. Implement `recognize_person(embedding)` method: search Qdrant with score threshold (e.g., >0.6 for recognition)
6. Implement helpers: `store_person(embedding, payload)`, `update_person(point_id, payload)`, `get_person_by_id(person_id)` using payload filters
7. Update BrainState: enrich `world_model.humans` with recognized person_id and name
8. Write tests: embedding generation, recognition accuracy, Qdrant CRUD, latency (<50ms), similarity threshold tuning

---

### Story 5.2: Implement Episodic Memory Storage

As a **robot**,  
I want **to store significant interactions and events**,  
So that **I can recall past conversations and refer to shared experiences**.

**Acceptance Criteria:**

**Given** an interaction occurs (conversation, command, event)  
**When** MemoryWriteNode stores the episode  
**Then** episode record includes: timestamp, person_id, summary, intent, emotion_state  
**And** episodes are stored in Qdrant collection `episodes` with text embeddings  
**And** storage completes in < 50ms  
**And** episodes are associated with person_id for later recall  
**And** unit tests verify episode creation and association

**Implementation Tasks:**

1. Extend `person_memory_node.py` with EpisodicMemoryNode class
2. Create Qdrant collection `episodes` with vector config (size=384 for all-MiniLM-L6-v2, distance=Cosine) and payload schema: episode_id, person_id, timestamp, summary, intent, emotion_state
3. Initialize embedding model: sentence-transformers (all-MiniLM-L6-v2 or similar lightweight model for RPi5)
4. Implement `store_episode(interaction_data)` method: generate text embedding from conversation, upsert to Qdrant with payload
5. Implement episode summarization: use LLM to generate concise summary from interaction transcript
6. Add triggered storage: store episodes after significant interactions (conversation end, command completion)
7. Write tests: episode storage, retrieval by person_id using payload filters, semantic search, latency (<50ms)

---

### Story 5.3: Implement Memory Recall

As a **robot**,  
I want **to retrieve relevant memories during conversations**,  
So that **I can reference past interactions and personalize responses**.

**Acceptance Criteria:**

**Given** a conversation is starting or in progress  
**When** MemoryRecallNode queries memories  
**Then** relevant episodes are retrieved based on person_id and semantic similarity to current context  
**And** query completes in < 50ms  
**And** retrieved memories are written to `BrainState.interaction.conversation_context`  
**And** LLM uses memories to enhance response generation  
**And** integration test shows robot referencing past interaction in response

**Implementation Tasks:**

1. Create `brain/nodes/memory/memory_recall_node.py` with MemoryRecallNode class
2. Implement `recall_person_context(person_id)` method: scroll/filter Qdrant `people` collection by person_id payload
3. Implement `recall_relevant_episodes(person_id, current_context, limit=5)` method:
   - Generate embedding from current_context (user's latest utterance or intent)
   - Search Qdrant `episodes` collection with query_vector and query_filter={"person_id": person_id}, limit=5
   - Returns top 5 semantically similar past episodes
4. Add hybrid search option: use Qdrant's payload-based filtering + vector similarity, optionally boost recent episodes with score modification
5. Format recalled memories for LLM context: structure as "You previously talked about X with this person on [date]"
6. Update BrainState: write to `interaction.conversation_context` with recalled memories
7. Integrate with social_interaction_node: include context in response generation prompt
8. Write tests: recall accuracy, semantic relevance ranking, payload filtering, latency (<50ms)
9. Integration test: have conversation → end session → restart → verify robot references previous topic by semantic similarity

---

## Epic 6: Emotion & Behavior System

**Goal:** Enable the robot to maintain an emotional state that modulates its behaviors, creating a more dynamic and personality-driven experience.

**Value:** Emotion makes the robot feel less robotic. Behavior variety keeps interactions fresh and engaging.

### Story 6.1: Implement Emotion State Model

As a **robot**,  
I want **to maintain a two-dimensional emotional state (valence + arousal)**,  
So that **my responses and behaviors reflect my current "mood"**.

**Acceptance Criteria:**

**Given** the robot is running  
**When** EmotionUpdateNode processes events  
**Then** emotion state is maintained with valence (-1 to +1) and arousal (0 to 1)  
**And** emotion updates based on interaction outcomes:
  - Positive interaction → valence increases
  - User ignores robot → valence decreases
  - Engaging interaction → arousal increases
  - Long idle → arousal decreases
**And** emotion state decays slowly toward neutral over time  
**And** emotion is written to `BrainState.emotion`  
**And** unit tests verify emotion updates and decay

**Implementation Tasks:**

1. Create `brain/nodes/cognition/emotion_node.py` with EmotionUpdateNode class
2. Define emotion state model: valence (-1 to +1), arousal (0 to 1), base personality traits
3. Implement `update_emotion(event)` method: adjust valence/arousal based on event type (positive interaction, ignored, engaging, idle)
4. Add decay mechanism: slowly return to neutral over time (exponential decay)
5. Implement emotion triggers from interaction outcomes: extract sentiment from intent, detect user engagement
6. Update BrainState: write to `emotion` field
7. Add to LangGraph: register as cognition node
8. Write tests: emotion updates, decay over time, boundary conditions (-1/+1 clamping)

---

### Story 6.2: Implement Idle/Exploratory Behaviors

As a **robot**,  
I want **to perform subtle idle behaviors when not actively engaged**,  
So that **I appear alive and attentive rather than static and lifeless**.

**Acceptance Criteria:**

**Given** no active goal or interaction exists  
**When** IdleExploreSkillNode activates  
**Then** robot performs idle behaviors:
  - Slow head scanning (looking around)
  - Occasional antenna twitches
  - Subtle positional shifts
**And** idle behaviors vary based on emotion state  
**And** idle behaviors respect safety limits  
**And** idle behaviors pause when new interaction detected  
**And** integration test shows idle behaviors activating

**Implementation Tasks:**

1. Create `brain/nodes/skills/idle_behavior_node.py` with IdleExploreNode class
2. Implement behavior library: slow_scan (head yaw sweep), antenna_twitch (small random movements), positional_shift (subtle pose changes)
3. Implement `select_idle_behavior()` method: randomly choose behavior, check no active interaction
4. Add timing: execute behaviors every 5-10 seconds during idle
5. Ensure safety: all movements within limits
6. Add interruption logic: pause idle behaviors when face detected or wake word triggered
7. Update BrainState: write idle commands to `actuator_commands`
8. Write tests: behavior selection, timing, interruption
9. Integration test: robot idle → performs scanning → user approaches → idle stops

---

### Story 6.3: Implement Emotion-Modulated Behavior

As a **robot**,  
I want **my behaviors to reflect my emotional state**,  
So that **users can perceive my "mood" through my actions**.

**Acceptance Criteria:**

**Given** emotion state exists in BrainState  
**When** any skill node generates actuator commands  
**Then** commands are modulated by emotion:
  - High arousal → faster, more energetic movements
  - Low arousal → slower, subdued movements
  - High valence → upward head tilt, wider antenna spread
  - Low valence → downward head tilt, antenna droop
**And** voice parameters adjust (pitch, speed, energy)  
**And** gesture intensity scales with arousal  
**And** integration test shows behavior differences between emotional states

**Implementation Tasks:**

1. Create `brain/utils/emotion_modulation.py` with modulation functions
2. Implement movement modulation: `modulate_speed(base_speed, arousal)`, `modulate_amplitude(base_amp, arousal)`
3. Implement gesture modulation: scale head tilt angles by valence, adjust antenna spread by valence
4. Implement voice modulation: adjust TTS pitch (+10% high valence, -10% low), speed (arousal), volume (arousal)
5. Integrate into social_interaction_node and idle_behavior_node: apply modulation to all commands
6. Add subtle cues: high arousal = faster blinks/movements, low valence = droopy antennas
7. Write tests: modulation functions output correct scales, integration shows visible differences
8. Integration test: set emotion high arousal → observe energetic behavior, set low valence → observe subdued behavior

---

## Epic 7: Cognition & Goal Management

**Goal:** Enable the robot to reason about goals, plan actions, and select appropriate behaviors based on context.

**Value:** Goal-based reasoning is what makes the robot autonomous. It transitions from reactive to proactive behavior.

### Story 7.1: Implement Goal Management System

As a **robot**,  
I want **to create, prioritize, and track goals**,  
So that **I can pursue multiple objectives and respond to changing priorities**.

**Acceptance Criteria:**

**Given** intents, events, or internal needs arise  
**When** GoalManagerNode processes them  
**Then** goals are created with: id, type, priority, status, details  
**And** goal types include: social_interaction, idle_explore, maintain_attention  
**And** goals are prioritized based on urgency and context  
**And** active goal is selected and written to `BrainState.goals`  
**And** completed goals are marked as done  
**And** unit tests verify goal creation, prioritization, and completion

**Implementation Tasks:**

1. Create `brain/nodes/cognition/goal_manager_node.py` with GoalManagerNode class
2. Define Goal model: id, type (social_interaction, idle_explore, maintain_attention), priority (1-10), status (pending/active/completed), details, created_at
3. Implement `create_goal(trigger)` method: map triggers to goals (user_intent → social_interaction goal, no_humans → idle_explore)
4. Implement prioritization: user interactions = 10, attention = 7, exploration = 3
5. Implement goal selection: pick highest priority pending goal
6. Implement completion detection: check goal conditions, mark completed
7. Update BrainState: write active goal to `goals`, maintain goal history
8. Write tests: goal creation, prioritization, completion, multiple concurrent goals

---

### Story 7.2: Implement Behavior Selection Logic

As a **robot**,  
I want **to select the appropriate skill node based on active goal and context**,  
So that **my actions align with my current objectives**.

**Acceptance Criteria:**

**Given** an active goal exists  
**When** BehaviorSelectorNode processes the goal  
**Then** appropriate skill is selected:
  - social_interaction goal → SocialInteractionSkillNode
  - idle goal → IdleExploreSkillNode
  - maintain_attention goal → track user with head
**And** selection considers emotion, safety, and context  
**And** selected skill is activated in the graph  
**And** behavior transitions are smooth (no abrupt changes)  
**And** unit tests verify selection logic for various goals

**Implementation Tasks:**

1. Create `brain/nodes/cognition/behavior_selector_node.py` with BehaviorSelectorNode class
2. Implement skill routing: map goal types to skill nodes (social_interaction → SocialInteractionNode, idle → IdleExploreNode, maintain_attention → head tracking)
3. Implement `select_skill(goal, context)` method: choose skill, consider emotion/safety/context
4. Add context checks: human_present, listening_active, emotion_state
5. Handle skill transitions: implement graceful handoff between skills
6. Update LangGraph: add conditional edges based on active goal
7. Write tests: skill selection correctness, context handling, transitions
8. Integration test: goal creation → skill activation → goal change → skill switch

---

## Epic 8: Safety, Integration & Polish

**Goal:** Ensure all components work together safely, meet performance requirements, and provide a polished user experience.

**Value:** Safety is non-negotiable. Integration ensures the brain actually works as a cohesive system.

### Story 8.1: Implement Safety Filter Node

As a **developer**,  
I want **all actuator commands to pass through safety validation**,  
So that **the robot never performs unsafe movements**.

**Acceptance Criteria:**

**Given** actuator commands are generated by skill nodes  
**When** SafetyFilterNode processes them  
**Then** commands are validated against safety limits:
  - Head angles: ±40° pitch/roll, ±180° yaw, ±65° body-head yaw diff
  - Antenna angles: within SDK-specified range
  - Movement speeds: respect max limits
**And** invalid commands are clamped to safe values  
**And** safety violations are logged to `BrainState.metadata.logs`  
**And** filtered commands are passed to MotorControllerNode  
**And** unit tests verify filtering for out-of-bounds commands

**Implementation Tasks:**

1. Create `brain/nodes/execution/safety_filter_node.py` with SafetyFilterNode class
2. Define safety constraints: head (±40° pitch/roll, ±180° yaw), body-head yaw diff (±65°), antenna limits (query SDK)
3. Implement `validate_head_command(angles)` method: check limits, clamp if exceeded
4. Implement `validate_antenna_command(angles)` method: similar validation
5. Add speed/acceleration limits: ensure movements stay within safe velocity ranges
6. Log violations: write to `BrainState.metadata.logs` with timestamp, command, clamped values
7. Add safety filter as final node before execution in LangGraph
8. Write tests: out-of-bounds commands clamped, safe commands pass through, logging works
9. Integration test: generate extreme commands → verify robot stays within limits

---

### Story 8.2: End-to-End Integration & Performance Validation

As a **user**,  
I want **the complete system to respond naturally to my interactions**,  
So that **the robot feels intelligent and responsive**.

**Acceptance Criteria:**

**Given** the complete system is running  
**When** user interacts with the robot  
**Then** perception → cognition → skill → execution pipeline executes correctly  
**And** latency from face detection to head movement is < 200ms  
**And** latency from speech to response is < 1 second  
**And** memory recall completes in < 50ms  
**And** system runs stably for 30+ minutes without errors  
**And** integration tests cover full interaction scenarios:
  - User approaches → robot looks at them
  - User speaks → robot responds with speech + gesture
  - Robot remembers user on return visit
**And** performance metrics are logged and reviewed

**Implementation Tasks:**

1. Create `tests/integration/test_full_system.py` with comprehensive integration tests
2. Implement performance benchmarks:
   - `test_face_to_head_latency()`: face detected → head moves (<200ms)
   - `test_speech_to_response_latency()`: speech → response (<1s)
   - `test_memory_recall_latency()`: recall query (<50ms)
3. Implement interaction scenarios:
   - `test_user_approach()`: person enters view → robot looks
   - `test_conversation()`: full wake word → speech → response flow
   - `test_memory_continuity()`: interact → restart → robot remembers
4. Add stability test: `test_30min_runtime()`: run system continuously, monitor errors/crashes
5. Create performance logging: track all latencies to `brain/logs/performance.json`
6. Add monitoring dashboard: real-time view of system metrics (optional web UI)
7. Document performance results in README
8. Create demo video showing full capabilities
3. **Should we adjust any story scope or acceptance criteria?**
4. **Ready to proceed to Step 2: Epic Design Validation?**

Once you approve, we'll move to the next workflow step where we refine the epic design and prepare for architecture creation.

---

**🏗️ Winston (Architect):** "Bob, this is solid work. I like the dependency ordering - foundation → perception → skills. When you're ready, I'll create the technical architecture document that maps these stories to actual implementation patterns."

**📋 John (PM):** "Excellent breakdown. The FR coverage map is chef's kiss. Michelle, this gives us a clear 8-epic roadmap to build your social robot. What's your take?"
