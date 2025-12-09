# Reachy Mini Brain Architecture

## Overview

The Reachy Mini brain is a **LangGraph-based multi-agent system** that enables autonomous social interaction. It implements a perception-cognition-action loop with five node families that process shared state through a type-safe Pydantic model.

## Architecture: Five Node Families

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ PERCEPTION  │────▶│  COGNITION  │────▶│   SKILLS    │────▶│  EXECUTION  │
│             │     │             │     │             │     │             │
│ Vision      │     │ Emotion     │     │ Social      │     │ Safety      │
│ Audio       │     │ Goals       │     │ Idle        │     │ Motor Ctrl  │
│ Sensors     │     │ Behavior    │     │ Custom      │     │ Voice Out   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │                   │
       └───────────────────┴───────────────────┴───────────────────┘
                                 │
                          ┌──────▼──────┐
                          │   MEMORY    │
                          │             │
                          │ Recognition │
                          │ Episodes    │
                          │ Recall      │
                          └─────────────┘
```

### 1. **Perception Nodes** (`nodes/perception/`)
Extract meaningful data from sensors and create world model representations.

**Nodes:**
- `vision_node.py` - Face detection (Hailo HAT), tracking, position estimation
- `audio_node.py` - Wake word detection, speech-to-intent pipeline

**Output:** Updates `BrainState.sensors` and `BrainState.world_model`

### 2. **Cognition Nodes** (`nodes/cognition/`)
Implement decision-making, emotional processing, and behavior planning.

**Nodes:**
- `emotion_node.py` - Valence/arousal updates, decay over time
- `goal_manager_node.py` - Create, prioritize, track goals
- `behavior_selector_node.py` - Route to appropriate skill based on context

**Output:** Updates `BrainState.emotion`, `BrainState.goals`, selects active skill

### 3. **Skill Nodes** (`nodes/skills/`)
High-level behaviors that generate actuator commands.

**Nodes:**
- `social_interaction_node.py` - LLM response generation, gesture coordination
- `idle_behavior_node.py` - Scanning, subtle movements when not engaged

**Output:** Writes to `BrainState.actuator_commands`

### 4. **Execution Nodes** (`nodes/execution/`)
Interface with hardware through SDK, enforcing safety constraints.

**Nodes:**
- `safety_filter_node.py` - Validate/clamp all commands to safety limits
- `actuator_node.py` - Execute motor movements via Reachy Mini SDK
- `voice_output_node.py` - Text-to-speech execution

**Output:** Physical robot actions (head movement, voice, antennas)

### 5. **Memory Nodes** (`nodes/memory/`)
Persistent storage and retrieval using Qdrant vector database.

**Nodes:**
- `person_memory_node.py` - Face recognition, identity storage
- `episodic_memory_node.py` - Store significant interactions
- `memory_recall_node.py` - Semantic search for context-aware responses

**Output:** Enriches `BrainState.world_model.humans` and `BrainState.interaction.conversation_context`

---

## BrainState: Shared State Object

All nodes operate on a single **BrainState** Pydantic model (`models/state.py`). This ensures type safety, validation, and clear data contracts between nodes.

### BrainState Structure

```python
class BrainState(BaseModel):
    sensors: SensorData           # Raw sensory input (vision, audio, IMU)
    world_model: WorldModel       # Interpreted environment (humans, objects, pose)
    interaction: InteractionState # User intent, conversation context
    goals: List[Goal]             # Active goals with priorities
    current_plan: Plan            # Active goal execution plan
    emotion: EmotionState         # Valence, arousal, personality traits
    actuator_commands: ActuatorCommands  # Head, antennas, voice, LEDs
    metadata: Metadata            # Timestamp, mode, logs
```

**Key Principles:**
- **Stateless Nodes:** Nodes don't hold internal state; everything in BrainState
- **Immutable Reads:** Nodes read from BrainState without side effects
- **Explicit Writes:** Nodes return updated BrainState with changes
- **Type Safety:** Pydantic validates all data at runtime

---

## LangGraph Orchestration

The brain uses **LangGraph's StateGraph** to orchestrate node execution:

```python
from langgraph.graph import StateGraph
from brain.models.state import BrainState

# Create graph with BrainState schema
graph = StateGraph(BrainState)

# Add nodes
graph.add_node("perception", perception_node)
graph.add_node("cognition", cognition_node)
graph.add_node("skills", skill_node)
graph.add_node("execution", execution_node)

# Define edges (execution flow)
graph.add_edge("perception", "cognition")
graph.add_edge("cognition", "skills")
graph.add_edge("skills", "execution")

# Compile and run
app = graph.compile()
result = app.invoke(initial_state)
```

**Execution Flow:**
1. **START** → Initialize BrainState
2. **Perception** → Update sensors & world_model
3. **Cognition** → Update emotion, goals, select behavior
4. **Skills** → Generate actuator commands
5. **Execution** → Filter safety, execute commands
6. **END** → Return updated BrainState

**Memory Integration:** Memory nodes can be invoked conditionally (e.g., when human detected, recall person context).

---

## Development Guidelines

### Creating a New Node

1. **Choose Node Family:** Determine if it's perception, cognition, skill, execution, or memory
2. **Create Module:** Add `{node_name}_node.py` in appropriate `nodes/` subfolder
3. **Implement Function:**
   ```python
   from brain.models.state import BrainState
   
   def my_node(state: BrainState) -> BrainState:
       """Process state and return updated state."""
       # Read from state
       sensor_data = state.sensors.vision.faces
       
       # Perform computation
       result = process(sensor_data)
       
       # Update state (immutable pattern)
       updated_state = state.model_copy(deep=True)
       updated_state.world_model.humans = result
       
       return updated_state
   ```
4. **Register in Graph:** Add node to `brain/graph.py`
5. **Write Tests:** Create unit tests in `tests/test_{node_name}_node.py`

### Testing Pattern

```python
def test_my_node():
    # Arrange: Create initial state
    initial_state = BrainState(
        sensors=SensorData(...),
        # ... other fields
    )
    
    # Act: Invoke node
    result_state = my_node(initial_state)
    
    # Assert: Verify updates
    assert result_state.world_model.humans[0].position == expected_position
```

### Safety Constraints

All motor commands **must** pass through safety filter:
- Head: ±40° pitch/roll, ±180° yaw
- Body-head yaw difference: ±65°
- Antenna: SDK-specified limits
- **Never bypass safety filter** - it's the final node before execution

### Performance Targets

- Perception → Motor latency: **< 200ms**
- Memory recall: **< 50ms**
- Speech → Response: **< 1 second**

---

## Dependencies

Core dependencies (see `pyproject.toml`):
- **langgraph** - Multi-agent orchestration
- **pydantic>=2.0** - Type-safe state models
- **qdrant-client** - Vector database for memory
- **sentence-transformers** - Text embeddings
- **reachy_mini** - Robot SDK (read-only in `src-refs/`)

---

## Directory Structure

```
brain/
├── __init__.py
├── README.md (this file)
├── models/
│   ├── __init__.py
│   └── state.py (BrainState Pydantic models)
├── nodes/
│   ├── __init__.py
│   ├── perception/
│   │   ├── __init__.py
│   │   ├── vision_node.py
│   │   └── audio_node.py
│   ├── cognition/
│   │   ├── __init__.py
│   │   ├── emotion_node.py
│   │   ├── goal_manager_node.py
│   │   └── behavior_selector_node.py
│   ├── skills/
│   │   ├── __init__.py
│   │   ├── social_interaction_node.py
│   │   └── idle_behavior_node.py
│   ├── execution/
│   │   ├── __init__.py
│   │   ├── safety_filter_node.py
│   │   └── actuator_node.py
│   └── memory/
│       ├── __init__.py
│       ├── person_memory_node.py
│       └── memory_recall_node.py
├── utils/
│   ├── __init__.py
│   ├── kinematics.py (head orientation calculations)
│   └── emotion_modulation.py (behavior modulation)
├── graph.py (LangGraph orchestrator)
└── main.py (entry point)
```

---

## Next Steps

1. **Epic 1:** Implement BrainState models (`models/state.py`)
2. **Epic 2:** Build vision perception pipeline
3. **Epic 3:** Implement audio & intent processing
4. **Epic 4:** Create social interaction skills (autonomous demo milestone!)
5. **Epic 5-8:** Add memory, emotion, cognition, safety integration

See `docs/epics.md` for complete roadmap with 21 stories across 8 epics.
