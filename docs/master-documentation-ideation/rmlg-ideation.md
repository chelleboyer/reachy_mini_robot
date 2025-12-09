## 1. High-Level Architecture

Think of the LangGraph brain as **four layers**, all inside one graph:

1. **Perception Layer** – “What’s happening?”
2. **Reasoning & Planning Layer** – “What should I do?”
3. **Behavior & Skill Layer** – “How exactly do I do it?”
4. **Execution & Safety Layer** – “Send commands safely to the hardware.”

Plus two “side systems”:

* **Memory System** – persists identity, people, places, experiences.
* **Personality / Emotion System** – modulates *how* it behaves, not just what it does.

All of these are represented as **nodes** in your LangGraph, exchanging a shared `BrainState`.

---

## 2. Core `BrainState` Schema

Everything in the graph should read/write a shared state object.
Rough sketch:

```jsonc
{
  "time": "...",
  "mode": "idle | follow | explore | interact | task",
  "sensors": {
    "vision": {/* raw or processed */},
    "audio": {/* transcripts, sound events */},
    "proximity": {/* distances, obstacles */},
    "imu": {/* orientation, motion */},
    "battery": {/* level, charging */},
    "wheel_odometry": {/* pose, speed */}
  },
  "world_model": {
    "map": {/* room layout, obstacles */},
    "objects": [/* detected objects with labels & positions */],
    "humans": [/* tracked people, identities, locations */],
    "self_pose": {/* where Reachy is in the map */}
  },
  "interaction": {
    "user_intent": null,
    "user_id": null,
    "last_user_utterance": "",
    "conversation_context": [/* short history */],
    "pending_question": null
  },
  "goals": [
    /* each: {id, type, priority, status, details} */
  ],
  "current_plan": {
    "goal_id": null,
    "steps": [/* high-level steps */],
    "active_step": null
  },
  "emotion": {
    "arousal": 0.0,
    "valence": 0.0,
    "traits": ["curious", "playful"]
  },
  "actuator_commands": {
    "drive": {/* target linear/angular velocity, etc. */},
    "arms": {/* joint goals or gesture id */},
    "head": {/* pan/tilt */},
    "voice": {/* text to say, voice settings */}
  },
  "logs": [/* debug info, last decisions, errors */]
}
```

LangGraph nodes read subsets and update subsets.

---

## 3. Major Node Groups

### A. Perception Nodes

These interpret raw sensors → structured info.

1. **VisionNode**

   * Inputs: camera frames
   * Outputs:

     * detected objects with labels + positions
     * faces / humans detected (with IDs if known)
   * Writes: `sensors.vision`, `world_model.objects`, `world_model.humans`

2. **AudioIntentNode**

   * Inputs: mic audio
   * Steps:

     * Speech-to-text
     * LLM: parse user intent (command, question, small talk)
   * Writes: `interaction.last_user_utterance`, `interaction.user_intent`, `interaction.user_id`

3. **ProximityNode**

   * Reads: proximity sensors
   * Writes: `sensors.proximity` + updates local obstacle data in `world_model.map`

4. **PoseEstimationNode**

   * Reads: wheel odometry, IMU
   * Writes: `world_model.self_pose`

These nodes can be run periodically or event-driven (e.g., new frame/audio).

---

### B. Reasoning & Planning Nodes

These decide **what Reachy should want right now** and how to achieve it.

5. **GoalManagerNode**

   * Reads:

     * `interaction.user_intent`
     * `battery`, `world_model`, `emotion`
   * Logic:

     * Turn intents into goals:

       * “Follow me” → `goal: follow_user`
       * “Go to the door” → `goal: go_to_location(door)`
     * Maintain background goals:

       * `stay_charged`, `be_near_humans`, `explore_when_idle`
   * Writes: `goals` array (create/update priorities, status)

6. **PlannerNode**

   * Reads: active goal from `goals`, `world_model`
   * Uses an LLM + some rule templates to:

     * Break goal into abstract steps, e.g.:

       * `go_to_kitchen` → [“locate kitchen”, “plan path”, “drive there”, “announce arrival”]
   * Writes: `current_plan.steps`, `current_plan.goal_id`, `current_plan.active_step`

7. **BehaviorSelectorNode**

   * Reads: `mode`, `current_plan.active_step`, `emotion`
   * Maps plan steps → concrete behaviors (skills):

     * `follow_user` → `FollowUserSkill`
     * `explore` → `RandomWalkSkill`
     * `social_greeting` → `GreetUserSkill`
   * Writes: something like `actuator_commands.behavior = "FollowUserSkill"` + extra params.

This is your **“what to do next” layer**.

---

### C. Skill / Behavior Nodes

Each skill is a node or small subgraph that translates **intent → concrete motor + speech commands**.

8. **FollowUserSkillNode**

   * Reads: user position from `world_model.humans`, `self_pose`
   * Computes: target velocity and heading
   * Writes: `actuator_commands.drive`

9. **NavigateToLocationSkillNode**

   * Reads: `target_location`, `world_model.map`, `self_pose`
   * Uses: whichever navigation stack you have ( could be a separate service )
   * Writes: `actuator_commands.drive` + path progress

10. **IdleExploreSkillNode**

    * When no goals:

      * Slowly wander
      * Look around
      * Occasionally trigger social behaviors

11. **SocialInteractionSkillNode**

    * Reads: `interaction.user_intent`, `emotion`, `conversation_context`
    * Uses LLM to pick:

      * Response text
      * Gesture (“wave”, “tilt head”, “nod”, “shrug”)
    * Writes: `actuator_commands.voice`, `actuator_commands.arms`, `actuator_commands.head`

12. **DanceOrExpressiveSkillNode**

    * Ex: triggered when user says “Dance!” or when “happy”:
    * Writes: pre-defined gesture sequences to motors.

These are “leaf nodes” that actually **decide robot behavior in the moment**.

---

### D. Execution & Safety Nodes

These are closest to hardware.

13. **SafetyFilterNode**

* Reads: `actuator_commands`, `sensors.proximity`, `battery`, `world_model`
* Enforces:

  * Speed caps
  * Emergency stops if obstacle or cliff detected
  * No movement when human too close (configurable)
* Writes: sanitized `actuator_commands` + safety logs.

14. **MotorControllerNode**

* Reads: filtered `actuator_commands.drive`, `actuator_commands.arms`, `…`
* Sends: actual commands to robot SDK / microcontrollers.
* Writes back:

  * Confirmation
  * Error states into `logs`.

15. **VoiceOutputNode**

* Reads: `actuator_commands.voice`
* Sends text to TTS
* Optionally logs prompts & outputs.

---

### E. Memory & Personality Nodes

These make Reachy feel persistent and alive.

16. **MemoryWriteNode**

* Triggered when:

  * New user appears
  * New object labeled
  * Important event completes
* Writes to external memory store:

  * `people` (names, faces, preferences)
  * `places` (map, semantic labels: “couch”, “door”, “desk”)
  * `episodes` (short natural-language summaries of interactions)

17. **MemoryRecallNode**

* When interacting:

  * Pulls relevant memories:

    * “This is Alex, you often talk about robotics.”
* Writes: `interaction.contextual_memory`

18. **EmotionUpdateNode**

* Reads:

  * Recent events (success/failure of tasks)
  * Social feedback
  * Time since last interaction
* Updates: `emotion` vector and tags
* Influences other nodes:

  * BehaviorSelectorNode (more playful, more talkative, quieter, more cautious)
  * SocialInteractionSkillNode word choice + gestures

---

## 4. Graph Topology: How It All Flows

At a high level, you can think of each **tick** (or event burst) like:

1. **Perception phase**

   * VisionNode
   * AudioIntentNode
   * ProximityNode
   * PoseEstimationNode

2. **Cognition phase**

   * GoalManagerNode (update goals)
   * PlannerNode (if goal changed or plan finished)
   * BehaviorSelectorNode (decide which skill runs)

3. **Skill phase**

   * Appropriate SkillNode runs:

     * FollowUserSkill / NavigateToLocationSkill / SocialInteractionSkill / etc.

4. **Execution phase**

   * SafetyFilterNode
   * MotorControllerNode
   * VoiceOutputNode

5. **Memory/Emotion phase**

   * MemoryWriteNode (for notable events)
   * MemoryRecallNode (if social context needed)
   * EmotionUpdateNode

LangGraph is good at **branching and conditionally calling nodes**, so you can:

* Only run PlannerNode when:

  * `current_plan` is empty
  * or current goal changed
* Only run MemoryWriteNode when:

  * `goal.status == completed`
  * or new human detected

Your “root” or supervisor node can orchestrate which nodes are called given the current `BrainState`.

---

## 5. Example Concrete Loops

### A. Idle → Human Appears → Interaction

1. IdleExploreSkillNode runs (slow patrol).
2. VisionNode sees a person; AudioIntentNode hears “Hey Reachy”.
3. GoalManagerNode creates `greet_human` goal and raises its priority.
4. PlannerNode sets steps: `orient_to_human → greet → wait_for_reply`.
5. BehaviorSelectorNode activates SocialInteractionSkillNode.
6. SocialInteractionSkillNode:

   * Speaks: “Hi! Good to see you again.”
   * Moves head + arms.
7. MemoryWriteNode logs the encounter.

### B. “Follow me” Scenario

1. User: “Reachy, follow me.”
2. AudioIntentNode → `user_intent = follow_user`.
3. GoalManagerNode:

   * Creates `follow_user` goal, mode = `follow`.
4. PlannerNode:

   * Steps: [“locate user”, “maintain distance”, “stop if too close or user stops”].
5. BehaviorSelectorNode → FollowUserSkillNode.
6. FollowUserSkillNode:

   * Uses human position + self pose to set drive commands.
7. SafetyFilterNode:

   * Ensures no collisions.
8. If user says “Stop following.” → new intent cancels goal.

---

## 6. Design Principles for This Brain

* **State-first design**
  Clearly define what lives in `BrainState`; nodes should be **pure-ish functions of state** + possibly LLM calls, not random side-effect machines.

* **Narrow nodes**
  Each node does one clear responsibility: perception, goal management, planning, behavior, execution.

* **Human-in-the-loop hooks**
  You can pause the graph at certain nodes (e.g. SafetyFilterNode or PlannerNode) to:

  * Inspect decisions
  * Override
  * Adjust parameters

* **Configurable modes**
  `mode` in `BrainState` decides:

  * Which goals are allowed
  * Which skills are available
  * How exploratory vs cautious the robot is

---

