Here’s a first cut of the **runtime behavior sequence diagram** for Reachy Mini’s LangGraph brain, with **wheels optional** baked in.

I’ll show:

* Core **“Sense → Think → Act → Learn”** loop
* A **Greeting / Social interaction** flow (no wheels needed)
* A **Follow Me** flow that **only runs movement if wheels are present**

All diagrams are in Mermaid so you can paste them into any Mermaid viewer.

---

## 1. Core Life Loop (Tick-by-Tick Sequence)

This is the generic **brain tick**: perception → cognition → skill → execution → memory/emotion.

```mermaid
sequenceDiagram
    autonumber
    participant Cam as Camera
    participant Mic as Microphone
    participant Sensors as Proximity/IMU
    participant LG as LangGraph Orchestrator
    participant V as VisionNode
    participant A as AudioIntentNode
    participant P as ProximityNode
    participant Pose as PoseEstimationNode (optional)
    participant G as GoalManagerNode
    participant Plan as PlannerNode
    participant B as BehaviorSelectorNode
    participant Skill as SelectedSkillNode
    participant Safe as SafetyFilterNode
    participant Motor as MotorControllerNode (optional wheels)
    participant Voice as VoiceOutputNode
    participant MemW as MemoryWriteNode
    participant MemR as MemoryRecallNode
    participant Emo as EmotionUpdateNode
    participant App as Reachy Brain App

    rect rgb(245,245,245)
    note over LG: One "brain tick" / event cycle
    end

    %% Perception Phase
    Cam->>V: New frame
    Mic->>A: New audio (if any)
    Sensors->>P: Proximity / cliff / bump
    Sensors->>Pose: Odometry/IMU (if wheels present)

    V->>LG: Update world_model (humans, objects)
    A->>LG: Update interaction.user_intent
    P->>LG: Update sensors.proximity
    Pose->>LG: Update world_model.self_pose (optional)

    LG->>G: Evaluate intents, safety, internal needs
    G->>LG: Updated goals, mode
    LG->>Plan: (If new/changed goal) Request plan
    Plan->>LG: current_plan.steps, active_step

    %% Behavior Selection
    LG->>B: Select behavior based on mode, active_step, emotion
    B->>MemR: (Optional) Request contextual memory
    MemR->>B: Relevant memories
    B->>Skill: Activate specific SkillNode (e.g. Social, Idle, Follow*)

    %% Skill Execution
    Skill->>LG: Proposed actuator_commands (drive/arms/head/voice)

    %% Safety + Execution
    LG->>Safe: Run SafetyFilterNode with commands + sensors
    Safe->>LG: Filtered actuator_commands, safety flags

    alt Has movement commands AND wheels installed
        LG->>Motor: Send drive/arm/head commands
        Motor->>LG: Status / telemetry
    else No wheels or movement disabled
        note over Motor: No-op (or virtual simulation only)
    end

    LG->>Voice: Send voice command (if any)
    Voice->>LG: Spoken confirmation / logs

    %% Memory & Emotion Phase
    LG->>MemW: Write episodic/semantic memories for this tick
    MemW->>Emo: Event summary for emotion update
    Emo->>LG: New emotion vector (valence, arousal, traits)

    %% App: Observability
    LG-->>App: Stream events (node states, BrainState, logs)
    App-->>LG: (Optional) Overrides / breakpoints / commands
```

Key points:

* **PoseEstimationNode** and **MotorControllerNode** only matter when wheels exist.
* Without wheels, the loop still runs; **movement commands are ignored or simulated**.
* App always sees the same stream regardless of hardware.

---

## 2. Scenario: Greeting / Social Interaction (No Wheels Required)

This is a typical “Reachy is idle → user says hello → Reachy greets back with personality.”

```mermaid
sequenceDiagram
    autonumber
    participant User as User
    participant Mic as Microphone
    participant Cam as Camera
    participant LG as LangGraph Orchestrator
    participant V as VisionNode
    participant A as AudioIntentNode
    participant G as GoalManagerNode
    participant Plan as PlannerNode
    participant B as BehaviorSelectorNode
    participant MemR as MemoryRecallNode
    participant Social as SocialInteractionSkillNode
    participant Voice as VoiceOutputNode
    participant MemW as MemoryWriteNode
    participant Emo as EmotionUpdateNode
    participant App as Reachy Brain App

    User->>Mic: "Hey Reachy!"
    Mic->>A: Audio stream
    A->>LG: last_user_utterance = "Hey Reachy", user_intent = "greet"

    Cam->>V: Frame with user face
    V->>LG: world_model.humans updated (user position, maybe identity)

    LG->>G: Evaluate greeting intent
    G->>LG: New goal: greet_user(user_id), mode = "interact"

    LG->>Plan: Plan steps for greet_user
    Plan->>LG: ["orient_to_user", "speak_greeting", "await_reply"]

    LG->>B: Select behavior for active_step="speak_greeting"
    B->>MemR: Request memories about this user
    MemR->>B: "Met yesterday; user likes robotics"

    B->>Social: Activate SocialInteractionSkillNode with context

    Social->>LG: actuator_commands.voice, arms, head (wave, head tilt)
    LG->>Voice: "Hi again! Great to see you. Want to work on robotics today?"
    Voice->>User: Speaks output

    LG->>MemW: Log greeting episode + user response
    MemW->>Emo: "Successful social interaction"
    Emo->>LG: Slight increase in positive valence

    LG-->>App: Stream nodes + BrainState
    App-->>LG: (Optional) Dev override or notes
```

Note: No wheels involved. This is pure **social creature** mode.

---

## 3. Scenario: “Follow Me” with Optional Wheels

Now the “Follow me” behavior, but **gated by hardware capabilities**.
If there are no wheels, Reachy responds verbally and perhaps “pretends” (e.g., rotates head to track you) but doesn’t try to move.

```mermaid
sequenceDiagram
    autonumber
    participant User as User
    participant Mic as Microphone
    participant Cam as Camera
    participant Sensors as Proximity/IMU
    participant LG as LangGraph Orchestrator
    participant A as AudioIntentNode
    participant V as VisionNode
    participant Pose as PoseEstimationNode (optional)
    participant G as GoalManagerNode
    participant Plan as PlannerNode
    participant B as BehaviorSelectorNode
    participant Follow as FollowUserSkillNode
    participant Safe as SafetyFilterNode
    participant Motor as MotorControllerNode (optional)
    participant Social as SocialInteractionSkillNode
    participant Voice as VoiceOutputNode
    participant App as Reachy Brain App

    User->>Mic: "Reachy, follow me."
    Mic->>A: Audio stream
    A->>LG: user_intent = "follow_user", user_id

    Cam->>V: Frames with user
    V->>LG: world_model.humans[user_id].position

    LG->>G: New goal: follow_user(user_id)
    G->>LG: goals updated, mode = "follow"

    LG->>Plan: Plan for follow_user
    Plan->>LG: Steps: ["track_user", "maintain_distance"]

    LG->>B: Select behavior for follow_user
    B->>Follow: Activate FollowUserSkillNode

    loop Continuous follow loop
        Cam->>V: User + environment
        V->>LG: Updated human + object positions

        Sensors->>Pose: Odometry/IMU (if wheels)
        Pose->>LG: world_model.self_pose (if wheels)

        Follow->>LG: Proposed actuator_commands.drive (and head orientation)
        LG->>Safe: Filter motion vs obstacles

        alt Wheels present and safe
            Safe->>Motor: Drive commands (v, omega)
            Motor->>LG: Status
        else No wheels detected OR unsafe
            note over Motor: No movement
            LG->>Social: Inform user "I can't move yet, but I'm tracking you."
            Social->>Voice: Friendly response
            Voice->>User: Speaks limitation or virtual follow
        end

        LG-->>App: Stream BrainState, follow intent, safety info
        App-->>LG: (Optional) Dev override / emergency stop
    end
```

This flow ensures:

* **Same high-level intent and goal system** works with or without wheels.
* If wheels are missing, the robot still **acts meaningfully** (e.g., head tracking, explanation) instead of silently failing.

---

## 4. Scenario: Idle Life Loop (Creature Vibes)

This is the “Reachy is just vibing” loop: looking around, self-updating, occasionally initiating interaction.

```mermaid
sequenceDiagram
    autonumber
    participant LG as LangGraph Orchestrator
    participant V as VisionNode
    participant A as AudioIntentNode
    participant G as GoalManagerNode
    participant Plan as PlannerNode
    participant B as BehaviorSelectorNode
    participant Idle as IdleExploreSkillNode
    participant Social as SocialInteractionSkillNode
    participant Emo as EmotionUpdateNode
    participant MemW as MemoryWriteNode
    participant App as Reachy Brain App

    loop Every N seconds (tick)
        V->>LG: Update world_model (people present? objects?)
        A->>LG: (Often no new intent)
        LG->>G: Evaluate goals (no user input, battery ok)
        G->>LG: Maybe create low-priority goal: "explore" or "look_around"

        LG->>Plan: Plan small idle steps
        Plan->>LG: ["scan_room", "look_toward_recent_motion"]

        LG->>B: Choose behavior (often IdleExploreSkill)
        B->>Idle: Activate IdleExploreSkillNode

        Idle->>LG: Commands for head sweeps, small gestures
        LG->>MemW: Log idle behaviors (e.g., "scanned room, no humans")
        MemW->>Emo: Feed events to emotion system
        Emo->>LG: Adjust emotion (if lonely, maybe increase desire to initiate contact)

        alt User detected or time since last social > threshold
            LG->>B: Re-evaluate behavior
            B->>Social: Activate SocialInteractionSkillNode
            Social->>User: "Hi, I'm here if you want to chat."
        end

        LG-->>App: Outcome of each tick
    end
```

This is what makes Reachy **feel alive even when nobody is talking to it**.

---
