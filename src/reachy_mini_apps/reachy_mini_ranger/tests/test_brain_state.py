"""Unit tests for BrainState Pydantic models.

Tests cover:
- Model instantiation with defaults
- Validation rules (angle limits, field constraints)
- Nested model creation
- Factory helper functions
- Serialization/deserialization
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from reachy_mini_ranger.brain.models.state import (
    ActuatorCommands,
    BrainState,
    ConversationContext,
    EmotionState,
    Face,
    Goal,
    GoalStatus,
    GoalType,
    HeadCommand,
    Human,
    IntentType,
    InteractionState,
    Metadata,
    Mode,
    Plan,
    Position3D,
    SensorData,
    UserIntent,
    VisionData,
    WorldModel,
    add_log,
    create_initial_state,
    update_timestamp,
)


class TestBrainStateInstantiation:
    """Test BrainState creation and defaults."""

    def test_create_empty_state(self):
        """Test creating BrainState with all defaults."""
        state = BrainState()
        
        assert state.sensors is not None
        assert state.world_model is not None
        assert state.interaction is not None
        assert state.goals == []
        assert state.current_plan is not None
        assert state.emotion is not None
        assert state.actuator_commands is not None
        assert state.metadata is not None

    def test_create_initial_state_factory(self):
        """Test factory helper creates valid state."""
        state = create_initial_state()
        
        assert isinstance(state, BrainState)
        assert state.metadata.mode == Mode.IDLE
        assert state.emotion.valence == 0.0
        assert state.emotion.arousal == 0.5
        assert len(state.goals) == 0

    def test_sensors_defaults(self):
        """Test sensor data initializes correctly."""
        state = create_initial_state()
        
        assert state.sensors.vision.faces == []
        assert state.sensors.vision.fps == 0.0
        assert state.sensors.audio.wake_word_detected is False

    def test_world_model_defaults(self):
        """Test world model initializes correctly."""
        state = create_initial_state()
        
        assert state.world_model.humans == []
        assert state.world_model.objects == []
        assert state.world_model.self_pose.position.x == 0.0


class TestValidation:
    """Test Pydantic validation rules."""

    def test_head_command_angle_limits(self):
        """Test head angles are clamped to safety limits."""
        # Valid angles
        head = HeadCommand(yaw=90.0, pitch=30.0, roll=-20.0)
        assert head.yaw == 90.0
        assert head.pitch == 30.0
        assert head.roll == -20.0

        # Angles at limits
        head = HeadCommand(yaw=180.0, pitch=40.0, roll=-40.0)
        assert head.yaw == 180.0
        assert head.pitch == 40.0
        assert head.roll == -40.0

    def test_head_command_exceeds_limits_raises_error(self):
        """Test that angles exceeding limits raise validation errors."""
        # Pydantic Field constraints will raise ValidationError
        with pytest.raises(ValidationError):
            HeadCommand(yaw=200.0)  # Exceeds ±180°
        
        with pytest.raises(ValidationError):
            HeadCommand(pitch=50.0)  # Exceeds ±40°
        
        with pytest.raises(ValidationError):
            HeadCommand(roll=-45.0)  # Exceeds ±40°

    def test_emotion_valence_bounds(self):
        """Test emotion valence stays in [-1, 1]."""
        emotion = EmotionState(valence=0.8, arousal=0.5)
        assert emotion.valence == 0.8

        emotion = EmotionState(valence=-0.9, arousal=0.5)
        assert emotion.valence == -0.9

        # Out of bounds should raise error
        with pytest.raises(ValidationError):
            EmotionState(valence=1.5)

    def test_emotion_arousal_bounds(self):
        """Test emotion arousal stays in [0, 1]."""
        emotion = EmotionState(arousal=0.3)
        assert emotion.arousal == 0.3

        with pytest.raises(ValidationError):
            EmotionState(arousal=-0.1)
        
        with pytest.raises(ValidationError):
            EmotionState(arousal=1.2)

    def test_goal_priority_bounds(self):
        """Test goal priority stays in [1, 10]."""
        goal = Goal(id="g1", goal_type=GoalType.SOCIAL_INTERACTION, priority=5)
        assert goal.priority == 5

        with pytest.raises(ValidationError):
            Goal(id="g2", goal_type=GoalType.IDLE_EXPLORE, priority=0)
        
        with pytest.raises(ValidationError):
            Goal(id="g3", goal_type=GoalType.IDLE_EXPLORE, priority=11)

    def test_face_confidence_bounds(self):
        """Test face confidence stays in [0, 1]."""
        face = Face(face_id=1, x=100, y=100, width=50, height=50, confidence=0.85)
        assert face.confidence == 0.85

        with pytest.raises(ValidationError):
            Face(face_id=2, x=100, y=100, width=50, height=50, confidence=1.5)


class TestNestedModels:
    """Test nested Pydantic model creation."""

    def test_create_human_with_position(self):
        """Test creating Human with Position3D."""
        pos = Position3D(x=1.5, y=0.5, z=0.0)
        human = Human(human_id=1, position=pos, face_id=42)
        
        assert human.human_id == 1
        assert human.position.x == 1.5
        assert human.face_id == 42
        assert human.is_primary is False

    def test_create_user_intent(self):
        """Test creating UserIntent with entities."""
        intent = UserIntent(
            intent_type=IntentType.QUESTION,
            text="What time is it?",
            entities={"topic": "time"},
            confidence=0.92,
        )
        
        assert intent.intent_type == IntentType.QUESTION
        assert intent.text == "What time is it?"
        assert intent.entities["topic"] == "time"
        assert intent.confidence == 0.92

    def test_create_goal_with_details(self):
        """Test creating Goal with custom details."""
        goal = Goal(
            id="social_001",
            goal_type=GoalType.SOCIAL_INTERACTION,
            priority=10,
            status=GoalStatus.ACTIVE,
            details={"target_person_id": "person_123"},
        )
        
        assert goal.id == "social_001"
        assert goal.goal_type == GoalType.SOCIAL_INTERACTION
        assert goal.status == GoalStatus.ACTIVE
        assert goal.details["target_person_id"] == "person_123"


class TestFactoryHelpers:
    """Test factory helper functions."""

    def test_update_timestamp(self):
        """Test update_timestamp updates metadata timestamp."""
        state = create_initial_state()
        original_time = state.metadata.timestamp
        
        # Wait a tiny bit to ensure time difference
        import time
        time.sleep(0.01)
        
        updated_state = update_timestamp(state)
        
        assert updated_state.metadata.timestamp > original_time
        assert updated_state is not state  # Should be a copy

    def test_add_log(self):
        """Test add_log appends to metadata logs."""
        state = create_initial_state()
        assert len(state.metadata.logs) == 0
        
        state = add_log(state, "Test message")
        assert len(state.metadata.logs) == 1
        assert "Test message" in state.metadata.logs[0]

    def test_add_log_limits_to_100(self):
        """Test add_log keeps only last 100 entries."""
        state = create_initial_state()
        
        # Add 150 logs
        for i in range(150):
            state = add_log(state, f"Log {i}")
        
        assert len(state.metadata.logs) == 100
        # Should have logs 50-149 (last 100)
        assert "Log 149" in state.metadata.logs[-1]


class TestSerialization:
    """Test model serialization and deserialization."""

    def test_brain_state_to_dict(self):
        """Test BrainState can be serialized to dict."""
        state = create_initial_state()
        state_dict = state.model_dump()
        
        assert isinstance(state_dict, dict)
        assert "sensors" in state_dict
        assert "world_model" in state_dict
        assert "emotion" in state_dict

    def test_brain_state_from_dict(self):
        """Test BrainState can be created from dict."""
        state = create_initial_state()
        state_dict = state.model_dump()
        
        # Recreate from dict
        new_state = BrainState(**state_dict)
        
        assert new_state.metadata.mode == state.metadata.mode
        assert new_state.emotion.valence == state.emotion.valence

    def test_brain_state_to_json(self):
        """Test BrainState can be serialized to JSON."""
        state = create_initial_state()
        json_str = state.model_dump_json()
        
        assert isinstance(json_str, str)
        assert "sensors" in json_str
        assert "world_model" in json_str

    def test_immutable_pattern(self):
        """Test that model_copy creates independent copy."""
        state = create_initial_state()
        state_copy = state.model_copy(deep=True)
        
        # Modify copy
        state_copy.emotion.valence = 0.8
        
        # Original should be unchanged
        assert state.emotion.valence == 0.0
        assert state_copy.emotion.valence == 0.8


class TestComplexState:
    """Test complex state scenarios."""

    def test_state_with_multiple_humans(self):
        """Test state with multiple detected humans."""
        state = create_initial_state()
        
        # Add humans to world model
        state.world_model.humans = [
            Human(
                human_id=1,
                position=Position3D(x=1.0, y=0.0, z=0.0),
                face_id=10,
                is_primary=True,
            ),
            Human(
                human_id=2,
                position=Position3D(x=2.0, y=1.0, z=0.0),
                face_id=11,
            ),
        ]
        
        assert len(state.world_model.humans) == 2
        assert state.world_model.humans[0].is_primary is True
        assert state.world_model.humans[1].is_primary is False

    def test_state_with_active_goal_and_plan(self):
        """Test state with active goal and execution plan."""
        state = create_initial_state()
        
        # Create goal
        goal = Goal(
            id="interact_001",
            goal_type=GoalType.SOCIAL_INTERACTION,
            priority=10,
            status=GoalStatus.ACTIVE,
        )
        state.goals.append(goal)
        
        # Create plan
        state.current_plan = Plan(
            goal_id="interact_001",
            steps=["detect_face", "generate_response", "execute_gesture"],
            active_step=1,
        )
        
        assert len(state.goals) == 1
        assert state.current_plan.goal_id == "interact_001"
        assert state.current_plan.active_step == 1

    def test_state_with_conversation_context(self):
        """Test state with conversation history and recalled memories."""
        state = create_initial_state()
        
        state.interaction.conversation_context = ConversationContext(
            recalled_memories=["You mentioned liking robots yesterday"],
            conversation_history=["Hello!", "How are you?"],
            active_person_id="person_abc",
        )
        
        assert len(state.interaction.conversation_context.recalled_memories) == 1
        assert len(state.interaction.conversation_context.conversation_history) == 2
        assert state.interaction.conversation_context.active_person_id == "person_abc"
