"""BrainState: Type-safe state model for Reachy Mini LangGraph brain.

This module defines the complete state structure shared across all nodes.
All fields use Pydantic v2 for runtime validation and type safety.

Architecture:
    BrainState contains 8 top-level sections:
    - sensors: Raw sensory input (vision, audio, IMU)
    - world_model: Interpreted environment (humans, objects, pose)
    - interaction: User intent, conversation context
    - goals: List of active goals with priorities
    - current_plan: Active goal execution plan
    - emotion: Valence, arousal, personality traits
    - actuator_commands: Commands for head, antennas, voice, LEDs
    - metadata: Timestamp, mode, logs

Usage:
    >>> from brain.models.state import BrainState, create_initial_state
    >>> state = create_initial_state()
    >>> state.sensors.vision.faces  # Access nested data
    []
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================================
# Enums
# ============================================================================

class Mode(str, Enum):
    """Robot operational mode."""
    IDLE = "idle"
    ACTIVE = "active"
    SLEEPING = "sleeping"


class GoalType(str, Enum):
    """Types of goals the robot can pursue."""
    SOCIAL_INTERACTION = "social_interaction"
    IDLE_EXPLORE = "idle_explore"
    MAINTAIN_ATTENTION = "maintain_attention"


class GoalStatus(str, Enum):
    """Goal lifecycle states."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"


class IntentType(str, Enum):
    """User intent classifications."""
    GREETING = "greeting"
    QUESTION = "question"
    COMMAND = "command"
    FAREWELL = "farewell"
    SMALL_TALK = "small_talk"


# ============================================================================
# Sensor Models
# ============================================================================

class Face(BaseModel):
    """Detected face with bounding box and metadata."""
    face_id: int
    x: float  # Bounding box top-left x
    y: float  # Bounding box top-left y
    width: float
    height: float
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)


class VisionData(BaseModel):
    """Vision sensor outputs."""
    faces: list[Face] = Field(default_factory=list)
    frame_timestamp: Optional[datetime] = None
    fps: float = 0.0


class AudioData(BaseModel):
    """Audio sensor outputs."""
    wake_word_detected: bool = False
    wake_word_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    audio_buffer: Optional[bytes] = None
    timestamp: Optional[datetime] = None


class SensorData(BaseModel):
    """All sensor inputs."""
    vision: VisionData = Field(default_factory=VisionData)
    audio: AudioData = Field(default_factory=AudioData)
    # Future: proximity, IMU, etc.


# ============================================================================
# World Model
# ============================================================================

class Position3D(BaseModel):
    """3D position relative to robot."""
    x: float  # meters
    y: float  # meters
    z: float  # meters


class Human(BaseModel):
    """Tracked human in environment."""
    human_id: int
    position: Position3D
    face_id: Optional[int] = None
    persistent_id: Optional[int] = None  # Persistent tracking ID across frames
    person_id: Optional[str] = None  # From memory system
    name: Optional[str] = None
    last_seen: datetime = Field(default_factory=datetime.now)
    is_primary: bool = False  # Primary attention target
    tracking_confidence: float = Field(default=1.0, ge=0.0, le=1.0)  # Tracking stability


class Pose3D(BaseModel):
    """Robot pose (position + orientation)."""
    position: Position3D = Field(default_factory=lambda: Position3D(x=0, y=0, z=0))
    yaw: float = 0.0  # degrees
    pitch: float = 0.0  # degrees
    roll: float = 0.0  # degrees


class WorldModel(BaseModel):
    """Robot's understanding of environment."""
    humans: list[Human] = Field(default_factory=list)
    objects: list[Any] = Field(default_factory=list)  # Future: object detection
    self_pose: Pose3D = Field(default_factory=Pose3D)


# ============================================================================
# Interaction
# ============================================================================

class UserIntent(BaseModel):
    """Parsed user intent from speech."""
    intent_type: IntentType
    text: str  # Transcribed speech
    entities: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversationContext(BaseModel):
    """Context for ongoing conversation."""
    recalled_memories: list[str] = Field(default_factory=list)
    conversation_history: list[str] = Field(default_factory=list, max_length=10)
    active_person_id: Optional[str] = None


class InteractionState(BaseModel):
    """User interaction state."""
    listening_active: bool = False
    user_intent: Optional[UserIntent] = None
    user_id: Optional[str] = None
    conversation_context: ConversationContext = Field(default_factory=ConversationContext)


# ============================================================================
# Goals & Planning
# ============================================================================

class Goal(BaseModel):
    """Goal with priority and status."""
    id: str
    goal_type: GoalType
    priority: int = Field(ge=1, le=10)
    status: GoalStatus = GoalStatus.PENDING
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class Plan(BaseModel):
    """Execution plan for active goal."""
    goal_id: Optional[str] = None
    steps: list[str] = Field(default_factory=list)
    active_step: int = 0


# ============================================================================
# Emotion
# ============================================================================

class EmotionState(BaseModel):
    """Two-dimensional emotion model: valence (positive/negative) + arousal (energy)."""
    valence: float = Field(default=0.0, ge=-1.0, le=1.0)  # -1 (sad) to +1 (happy)
    arousal: float = Field(default=0.5, ge=0.0, le=1.0)  # 0 (calm) to 1 (excited)
    traits: dict[str, float] = Field(
        default_factory=lambda: {
            "curiosity": 0.8,
            "friendliness": 0.9,
            "playfulness": 0.7,
        }
    )


# ============================================================================
# Actuator Commands
# ============================================================================

class HeadCommand(BaseModel):
    """Head motor angles in degrees."""
    yaw: float = Field(default=0.0, ge=-180.0, le=180.0)
    pitch: float = Field(default=0.0, ge=-40.0, le=40.0)
    roll: float = Field(default=0.0, ge=-40.0, le=40.0)
    duration: float = Field(default=1.0, ge=0.0)  # seconds
    interpolation: str = "linear"  # linear, minjerk, ease, cartoon

    @field_validator("yaw", "pitch", "roll")
    @classmethod
    def clamp_angles(cls, v: float, info) -> float:
        """Ensure angles stay within safety limits."""
        field_name = info.field_name
        if field_name == "yaw":
            return max(-180.0, min(180.0, v))
        else:  # pitch or roll
            return max(-40.0, min(40.0, v))


class AntennaCommand(BaseModel):
    """Antenna motor angles in degrees."""
    left: float = Field(default=0.0, ge=-90.0, le=90.0)
    right: float = Field(default=0.0, ge=-90.0, le=90.0)
    duration: float = Field(default=1.0, ge=0.0)


class VoiceCommand(BaseModel):
    """Text-to-speech output."""
    text: str = ""
    pitch: float = Field(default=1.0, ge=0.5, le=2.0)  # TTS pitch multiplier
    speed: float = Field(default=1.0, ge=0.5, le=2.0)  # TTS speed multiplier
    volume: float = Field(default=1.0, ge=0.0, le=1.0)


class ActuatorCommands(BaseModel):
    """All actuator commands (motors, voice, LEDs)."""
    head: HeadCommand = Field(default_factory=HeadCommand)
    antennas: AntennaCommand = Field(default_factory=AntennaCommand)
    voice: VoiceCommand = Field(default_factory=VoiceCommand)
    # Face tracking target (pixel coordinates for look_at_image)
    face_tracking_pixel: Optional[tuple[float, float]] = None  # (x, y) in pixels
    # Future: LEDs, etc.


# ============================================================================
# Metadata
# ============================================================================

class Metadata(BaseModel):
    """System metadata and logs."""
    timestamp: datetime = Field(default_factory=datetime.now)
    mode: Mode = Mode.IDLE
    logs: list[str] = Field(default_factory=list, max_length=100)


# ============================================================================
# BrainState - Main State Object
# ============================================================================

class BrainState(BaseModel):
    """Complete robot state shared across all LangGraph nodes.
    
    This is the single source of truth for the robot's perception,
    cognition, and planned actions. All nodes read from and write to
    this state object.
    
    Architecture Pattern:
        - Nodes are stateless functions
        - All state lives in BrainState
        - Nodes return updated BrainState copies (immutable pattern)
    
    Attributes:
        sensors: Raw sensory input (vision, audio)
        world_model: Interpreted environment (humans, objects, pose)
        interaction: User intent and conversation context
        goals: List of active goals with priorities
        current_plan: Execution plan for active goal
        emotion: Valence, arousal, personality traits
        actuator_commands: Commands for motors, voice, LEDs
        metadata: Timestamp, mode, system logs
    """
    
    sensors: SensorData = Field(default_factory=SensorData)
    world_model: WorldModel = Field(default_factory=WorldModel)
    interaction: InteractionState = Field(default_factory=InteractionState)
    goals: list[Goal] = Field(default_factory=list)
    current_plan: Plan = Field(default_factory=Plan)
    emotion: EmotionState = Field(default_factory=EmotionState)
    actuator_commands: ActuatorCommands = Field(default_factory=ActuatorCommands)
    metadata: Metadata = Field(default_factory=Metadata)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True  # Validate on field updates
    )


# ============================================================================
# Factory Helpers
# ============================================================================

def create_initial_state() -> BrainState:
    """Create initial BrainState with default values.
    
    Returns:
        BrainState: Initialized state ready for first graph invocation
    
    Example:
        >>> state = create_initial_state()
        >>> state.metadata.mode
        <Mode.IDLE: 'idle'>
    """
    return BrainState()


def update_timestamp(state: BrainState) -> BrainState:
    """Update state timestamp to current time.
    
    Args:
        state: Current BrainState
        
    Returns:
        BrainState: State with updated timestamp
    
    Example:
        >>> state = update_timestamp(state)
    """
    updated = state.model_copy(deep=True)
    updated.metadata.timestamp = datetime.now()
    return updated


def add_log(state: BrainState, message: str) -> BrainState:
    """Add log message to state metadata.
    
    Args:
        state: Current BrainState
        message: Log message to add
        
    Returns:
        BrainState: State with log appended
    
    Example:
        >>> state = add_log(state, "Face detected")
    """
    updated = state.model_copy(deep=True)
    log_entry = f"{datetime.now().isoformat()}: {message}"
    updated.metadata.logs.append(log_entry)
    # Keep only last 100 logs
    if len(updated.metadata.logs) > 100:
        updated.metadata.logs = updated.metadata.logs[-100:]
    return updated
