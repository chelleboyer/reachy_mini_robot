# **PRODUCT REQUIREMENTS DOCUMENT (PRD)**

## **Reachy Mini 2.0 — An Embodied, LangGraph-Powered Autonomous AI Robot**

---

# 1. **Product Overview**

**Reachy Mini 2.0** is a **mobile, expressive, autonomous embodied AI robot** powered by a multi-agent **LangGraph Brain** that enables perception, planning, decision-making, movement, memory, and personality-driven interaction.
The system combines:

* A **rolling robot hardware platform**
* A **LangGraph-based software brain**
* A **Reachy Brain UI App** for real-time visualization, debugging, and control

Reachy Mini is designed to act as a **living agent**, capable of exploration, social interaction, autonomous decision-making, and context-aware movement in physical environments.

---

# 2. **Goals & Vision**

## 2.1 Vision Statement

> Build a robot that feels **alive**, moves with purpose, responds with personality, remembers interactions, and grows more capable over time — powered by a fully inspectable, modifiable LangGraph brain.

## 2.2 Core Goals

1. **Embodied Autonomy**
   Reachy Mini moves independently, explores rooms, follows users, navigates to places, avoids obstacles, and returns to charging.

2. **Agentic Intelligence**
   The LangGraph brain manages perception → planning → action loops, memory, emotional states, and multi-agent reasoning.

3. **Expressive Interaction**
   Reachy communicates using gestures, head movements, gaze, wheels, and voice synthesis.

4. **Transparent AI**
   The Reachy Brain App visualizes all reasoning steps, nodes, memory, and decisions in real time.

5. **Extendable & Modular**
   Users can add new behaviors, skills, or nodes using a structured LangGraph framework.

---

# 3. **User Personas**

### **Primary Users**

1. **Robotics developers** building embodied agents.
2. **AI tinkerers and hobbyists** who want a programmable physical AI companion.
3. **Researchers** studying agentic AI, memory models, human-robot interaction.

### **Secondary Users**

4. **Consumers** who want a friendly autonomous robot companion.
5. **Educators** teaching robotics + AI.
6. **Startup teams** building agentic assistants and robotic interfaces.

---

# 4. **System Architecture Overview**

The product consists of **three major subsystems**:

---

## **4.1 The Physical Robot (Reachy Mini Hardware)**

### Required Hardware:

* **Locomotion:**

  * Differential drive or mecanum wheels
  * Motor controllers
  * Wheel encoders

* **Sensors:**

  * RGB camera
  * Depth or stereo vision (optional but recommended)
  * IMU (acceleration, rotation)
  * Proximity sensors (IR, sonar, ToF)
  * Battery sensor

* **Actuators:**

  * Head tilt/pan
  * Expressive arms (optional but ideal)
  * LED eyes / light indicators

* **Compute Options:**
  (Choose one architecture)

  * Onboard compute (Jetson, Raspberry Pi 5 + NPU)
  * Offboard compute (server or laptop; robot streams sensor data)

---

## **4.2 LangGraph Brain (Software AI System)**

### Brain Responsibilities:

* **Perception:**
  Vision, audio intent, proximity interpretation, self-pose estimation.

* **Reasoning:**
  Goal management, long-term planning, behavior selection.

* **Behavior Layers:**
  Follow user, explore, navigate to targets, social interaction, dance/expressiveness.

* **Execution:**
  Safety filtering, motor outputs, voice output.

* **Memory & Emotion:**
  Episodic memory, semantic labeling, emotional state vector.

### LangGraph Node Categories:

1. **Perception Nodes**
2. **Cognition Nodes**
3. **Skill Nodes**
4. **Execution Nodes**
5. **Memory/Emotion Nodes**

(A complete list of nodes was generated in the previous step — happy to embed it here.)

---

## **4.3 Reachy Brain App (Graph UI)**

### Core Features:

* Live visualization of the LangGraph brain (nodes + edges)
* Real-time brain state viewer
* Step-through debugging (pause, resume, override outputs)
* Memory viewer and editor
* Behavior override (force skill nodes)
* Graph versioning & configuration management

This app acts as both:

* A **control tower**
* A **teaching tool**
* A **debugger**
* An **inspector** for Reachy’s brain

---

# 5. **Functional Requirements**

## **5.1 Robot Mobility & Autonomy**

### Movement:

* Robot must navigate indoors with stable velocity control.
* Must follow user reliably within 0.5–2 meters.
* Must avoid collisions using real-time proximity sensors.
* Must return to a charging dock automatically.

### Localization & Mapping:

* Robot must maintain a rough internal map of the environment.
* Must be able to label key locations (“kitchen”, “desk”).

---

## **5.2 Social Interaction**

### Spoken Interaction:

* Robot must recognize wake words / speech input.
* Must extract user intents via LLM.
* Must respond with speech + gesture.

### Nonverbal:

* Must track user faces & gaze direction.
* Must express emotions via animations, gestures, or LEDs.

---

## **5.3 Agentic Reasoning**

### Goals System:

* Must maintain prioritized list of active goals.
* Must create goals from:

  * user commands
  * environmental cues
  * emotional states
  * internal needs (battery low)

### Planning:

* Must break goals into discrete steps.
* Must update plans when conditions change.

### Behavior Selection:

* Must choose appropriate skills based on:

  * current goal
  * emotional state
  * context
  * safety

---

## **5.4 Memory System**

### Memory Creation:

* Robot must store:

  * Recognized people
  * Places
  * Sessions
  * Preferences
  * Significant events

### Memory Recall:

* Robot must pull memories into conversation:
  “Last time we talked you mentioned robotics.”

---

## **5.5 Emotion System**

### Emotional Dynamics:

* Must maintain valence + arousal state.
* Must reflect emotion in behavior:

  * High arousal = energetic movements
  * Low valence = subdued tone

---

## **5.6 Reachy Brain App Requirements**

### Visualization:

* Must show:

  * All nodes
  * Active edges
  * Current node output
  * BrainState in real-time

### Controls:

* Step-through mode
* Runtime overrides
* Live memory editing
* Behavior force-activation

### Development Tools:

* Export logs
* Compare runs
* Version control

---

# 6. **Non-Functional Requirements**

### Safety:

* Max movement speed must be capped.
* Robot must emergency-stop when obstacles < X cm.
* Cannot move toward humans at unsafe speed.
* All motor commands must pass through safety filter.

### Performance:

* Latency < 200ms from perception → motor output.
* Memory recall < 50ms.
* Audio detection < 200ms processing.

### Reliability:

* Robot must operate for 1–2 hours on battery.
* Must withstand WiFi drops if brain is remote.

### Security:

* Local authentication to control app.
* Permissions for editing memories.

---

# 7. **Product Scope**

### **In Scope for v1:**

* Wheels + locomotion
* Basic perception
* Follow user
* Explore mode
* Social interaction
* LangGraph brain
* App: live graph + state viewer

### **In Scope for v2:**

* Emotional modeling
* Long-term episodic memory
* Map labeling
* Charging dock navigation
* Personality systems

### **In Scope for v3:**

* Multi-room navigation
* Advanced autonomy
* Multi-agent collaboration
* App marketplace for skills

---

# 8. **Success Metrics**

### Qualitative Metrics

* Robot feels “alive” to most users.
* Smoothness of follow behavior.
* Natural social interactions.

### Quantitative Metrics

* 95% success rate for follow behavior.
* 90% successful docking attempts.
* Latency < 200ms perception→action.
* App must handle 30 fps event updates.

---

# 9. **Risks & Mitigations**

### Risk: Perception complexity

**Mitigation:** Progressive rollout; fallback modes when vision fails.

### Risk: Overwhelming AI autonomy

**Mitigation:** Strong safety filters + overrides in Brain App.

### Risk: Emotional models cause unpredictable behavior

**Mitigation:** Emotion bounded by safety and mode constraints.

### Risk: Battery limits mobility

**Mitigation:** Smart charging routines integrated in planning.

---

# 10. **Open Questions**

1. Should emotional state influence navigation?
2. Should user be allowed to rewrite memories?
3. Should the robot operate offline or require cloud inference?
4. Which hardware platform do you prefer (Jetson, Pi 5, remote server)?
5. Should the robot have a wake word or use continuous audio polling?

---

# 11. **Appendix: Full LangGraph Node Architecture Diagram**

(We can embed the full diagram created earlier.)

---
