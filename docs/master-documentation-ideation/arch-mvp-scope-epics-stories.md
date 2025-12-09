### **Reachy Mini – LangGraph Brain + App + Robot Architecture (Final Draft)**

---

## **1.1 High-Level System Architecture**

```
+---------------------------------------------------------------+
|                     Reachy Brain App (UI)                    |
|   - Real-time graph view                                     |
|   - Node inspector / state viewer                             |
|   - Memory browser                                            |
|   - Behavior overrides & debugging tools                      |
+--------------------------▲------------------------------------+
                           │ WebSocket API
                           │
+--------------------------┴------------------------------------+
|                 LangGraph Brain (Core AI System)             |
|  - Perception Nodes                                           |
|  - Cognition Nodes                                            |
|  - Skill Nodes (movement, social, idle, optional wheels)      |
|  - Execution Nodes                                             |
|  - Memory & Emotion Nodes                                     |
|  - BrainState shared model                                     |
+--------------------------▲------------------------------------+
                           │ gRPC/REST/MQTT commands
                           │ Hardware abstraction layer
+--------------------------┴------------------------------------+
|                      Robot Hardware Layer                     |
|  - Sensors: camera, mic, IMU, proximity                       |
|  - Actuators: head, arms, LEDs                                |
|  - OPTIONAL: wheels / motor drivers                           |
+---------------------------------------------------------------+
```

---

## **1.2 Subsystem Breakdown**

### **A. LangGraph Brain**

The brain is split into **five node families**:

1. **Perception Nodes**
2. **Cognition Nodes**
3. **Skill Nodes**
4. **Execution Nodes**
5. **Memory & Emotion Nodes**

Each node updates portions of `BrainState`.

---

### **A.1 Perception Nodes**

| Node               | Purpose                                                   |
| ------------------ | --------------------------------------------------------- |
| VisionNode         | Detects people/objects, updates world model               |
| AudioIntentNode    | Speech to intent, triggers conversational/cognitive paths |
| ProximityNode      | Obstacle detection, safety triggers                       |
| PoseEstimationNode | Self pose tracking (only used if wheels enabled)          |

> **Note:** Pose node becomes a no-op if wheels not installed.

---

### **A.2 Cognition Nodes**

| Node                 | Purpose                                |
| -------------------- | -------------------------------------- |
| GoalManagerNode      | Creates, prioritizes and deletes goals |
| PlannerNode          | Turns goals into steps                 |
| BehaviorSelectorNode | Chooses which skill to activate        |

---

### **A.3 Skill Nodes**

| Node                        | Purpose                          | Requires Wheels? |
| --------------------------- | -------------------------------- | ---------------- |
| FollowUserSkillNode         | Move robot to maintain distance  | Yes (optional)   |
| NavigateToLocationSkillNode | Indoor navigation                | Yes (optional)   |
| IdleExploreSkillNode        | Wandering + scanning environment | Yes (optional)   |
| SocialInteractionSkillNode  | Speech + gestures                | No               |
| DanceExpressiveSkillNode    | Gestures, animations             | No               |

If wheels are not present, fallback to:

* Head movements
* Arm animations
* Sound
* LED expressive modes
* “Virtual navigation” (pretend movement for testing)

---

### **A.4 Execution Nodes**

| Node                | Purpose                                                   |
| ------------------- | --------------------------------------------------------- |
| SafetyFilterNode    | Ensures safe output; disables movement when wheels absent |
| MotorControllerNode | Sends commands to drive + arms + head                     |
| VoiceOutputNode     | Speak via TTS                                             |

---

### **A.5 Memory & Emotion Nodes**

| Node              | Purpose                                     |
| ----------------- | ------------------------------------------- |
| MemoryWriteNode   | Store experiences                           |
| MemoryRecallNode  | Retrieve memories for conversation/behavior |
| EmotionUpdateNode | Modulates personality                       |

---

## **1.3 Data Flow**

### Without wheels:

* Perception → Cognition → Social skills → Voice/motion outputs
  Movement nodes simply skip execution or simulate.

### With wheels:

* Perception → Cognition → Movement skills → Safety → Hardware Motors
  This is an extended but optional pathway.

---

# ✅ **2. MVP SCOPE (4–6 Week Build)**

**Goal:** Deliver a working Reachy Mini with a LangGraph brain, functioning socially and perceptively, without wheels.

> Wheels OPTIONAL and saved for **v2**.

---

## **MVP Feature Set**

### **Required**

✔ Vision detection (humans + basic object detection)
✔ Wake word + speech → intent pipeline
✔ Social interaction skill (speech, gestures)
✔ Live LangGraph brain + state viewer
✔ Memory (people + simple episodic logs)
✔ Emotion system (valence + arousal)
✔ Idle scanning / expressive behaviors
✔ Safety system (for arms/head only)

### **Optional (stubbed until wheels exist)**

◻ Follow User
◻ Navigate to Location
◻ Explore Mode
◻ Docking

### **Architecture Delivery**

* Fully documented node graph
* BrainState schema
* Plug-in architecture for adding new nodes
* Debug app (graph view + inspector)

---

## **MVP Timeline (Example)**

### **Week 1: Brain Foundation**

* LangGraph skeleton
* BrainState model
* Core nodes (AudioIntent, Vision, MemoryWrite/Recall, SocialSkill)

### **Week 2: Emotion + Behavior Selection**

* EmotionUpdateNode
* BehaviorSelectorNode
* Idle expressive behaviors

### **Week 3: App Implementation**

* Real-time graph view
* Node inspector
* Live BrainState viewer

### **Week 4: Robot Integration**

* TTS
* Head/arm animations
* Vision → interaction mapping
* Safe execution layer

### **Week 5: Memory + Personality**

* Episodic memory
* User preferences
* Personalized greetings

### **Week 6: Polish + Testing**

* Stress test flows
* Fail-safe handling
* Clean architecture export

---

# ✅ **3. EPICS + USER STORIES (Engineering-Ready)**

---

## **EPIC 1 – LangGraph Brain Core**

### User Stories:

1. As a developer, I can define nodes with clear input/output contracts.
2. As a user, I want the robot to update its world understanding continuously.
3. As a researcher, I want to simulate nodes without hardware.

---

## **EPIC 2 – Perception Layer**

### Stories:

1. VisionNode detects faces and emits metadata.
2. AudioIntentNode converts speech to structured intents.
3. ProximityNode emits safety events.

---

## **EPIC 3 – Social Interaction System**

### Stories:

1. Robot responds conversationally to user intents.
2. Robot gestures while speaking.
3. Emotional state influences tone and motion.

---

## **EPIC 4 – Memory + Personality System**

### Stories:

1. Robot remembers users it has met.
2. Robot recalls past sessions to contextualize responses.
3. Robot maintains an emotional vector updated by events.

---

## **EPIC 5 – Reachy Brain App UI**

### Stories:

1. Developer can see entire graph in real time.
2. Developer can inspect BrainState and override variables.
3. Developer can pause/resume execution steps.
4. Developer can load graph versions and diff outputs.

---

## **EPIC 6 – Movement (Optional Wheels)**

### Stories:

1. With wheels installed, robot follows user.
2. Robot navigates to a designated point.
3. Robot avoids obstacles during navigation.

---

# ✅ **4. VISUAL SYSTEM DIAGRAMS (TEXT-BASED)**

---

## **4.1 System Data Flow Diagram**

```
Sensors → Perception Nodes → Cognition Nodes → Skills → Execution → Hardware
                          ↘ Memory & Emotion ↗
```

---

## **4.2 Component Diagram**

```
+------------------+        +--------------------+
|    Camera        |------->|    VisionNode      |
+------------------+        +--------------------+
                                    |
+------------------+                v
|   Microphone     |------->| AudioIntentNode    |
+------------------+                |
                                    v
+------------------+       +---------------------+
| Proximity Sensor |----->|  ProximityNode      |
+------------------+       +---------------------+

      Perception feeds into ↓↓↓

+------------------------------------------------+
|             Cognition Layer                    |
|  GoalManager → Planner → BehaviorSelector      |
+------------------------------------------------+

                ↓ Skill selection

+------------------------------------------------+
|                Skill Layer                     |
| SocialSkill | IdleExpressive | (NavSkills*)    |
+------------------------------------------------+

                ↓ Actions

+------------------------------------------------+
|             Execution Layer                    |
| SafetyFilter → MotorController → Hardware      |
+------------------------------------------------+

              (* optional wheels)
```

---

# 🎉 **ALL FOUR DELIVERABLES COMPLETE**

This is now a **full PRD + architecture + epics + MVP plan + diagrams**, ready for a real engineering team.

---
