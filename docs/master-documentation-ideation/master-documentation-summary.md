# 📚 **Reachy Mini – Master Documentation Table of Contents**

---

## **1. Product & Vision**

### **1.1 Product Requirements Document (PRD)**

1. Product Overview
2. Goals & Vision
3. User Personas
4. System Architecture Overview
5. Functional Requirements

   * Mobility & Autonomy
   * Social Interaction
   * Agentic Reasoning
   * Memory System
   * Emotion System
   * Reachy Brain App
6. Non-Functional Requirements

   * Safety
   * Performance
   * Reliability
   * Security
7. Product Scope (v1–v3)
8. Success Metrics
9. Risks & Mitigations
10. Open Questions

---

## **2. System Architecture & Design**

### **2.1 Final Architecture Overview (Brain + App + Robot)**

1. High-Level System Architecture
2. Subsystem Breakdown

   * LangGraph Brain
   * Robot Hardware Layer
   * Brain App UI
3. Node Families

   * Perception
   * Cognition
   * Skills
   * Execution
   * Memory & Emotion
4. Data Flow (With Wheels / Without Wheels)
5. MVP Scope & Timeline
6. Engineering Epics & User Stories
7. Text-Based System Diagrams

---

### **2.2 High-Level LangGraph Diagram (Mermaid)**

1. Perception Layer
2. Cognition Layer
3. Skill Layer
4. Execution Layer
5. Memory & Emotion Layer
6. Inter-Node Edge Relationships
7. Conditional & Optional Wheel Paths

---

### **2.3 Node & Edge Definitions (Detailed)**

1. Perception Nodes

   * VisionNode
   * AudioIntentNode
   * ProximityNode
   * PoseEstimationNode
2. Cognition Nodes

   * GoalManagerNode
   * PlannerNode
   * BehaviorSelectorNode
3. Skill Nodes

   * FollowUserSkill
   * Navigation
   * IdleExplore
   * SocialInteraction
   * DanceExpressive
4. Execution Nodes

   * SafetyFilter
   * MotorController
   * VoiceOutput
5. Memory & Emotion Nodes

   * MemoryWrite
   * MemoryRecall
   * EmotionUpdate

---

## **3. Runtime Behavior & Sequencing**

### **3.1 Runtime Behavior Sequence Diagrams**

1. Core Life Loop (Sense → Think → Act → Learn)
2. Greeting / Social Interaction Flow
3. Follow-Me Flow (Wheels Optional)
4. Idle “Creature Mode” Loop
5. Safety-Interrupted Execution Flow
6. App-to-Brain Observability Loop

---

## **4. Brain State & Data Models**

### **4.1 Canonical BrainState & CoreBrainState Design**

1. Canonical vs Runtime Core State
2. CoreBrainState Schema
3. Presence Model
4. Interaction Model
5. Goal & Plan Model
6. Emotion Vector
7. Actuator Command Model
8. Status & Telemetry
9. Patch / Diff Streaming Design
10. External Stores

    * Perception Store
    * World Model Store
    * Memory Store
    * Log Store

---

## **5. MVP Scope & Engineering Planning**

### **5.1 MVP Architecture, Scope, Epics & Stories**

1. MVP Feature Set
2. Required vs Optional Capabilities
3. Wheel-Optional Strategy
4. Week-by-Week Delivery Plan
5. Core Engineering Epics
6. User Stories by Domain

---

## **6. Production-Grade Readiness**

### **6.1 Production Robustness & Safety Plan**

1. Physical Safety Layer
2. Software Safety Layer
3. Traceability & Deterministic Replay
4. Governance & Version Control
5. Skill Sandboxing
6. Graceful Degradation Strategy
7. Watchdog Systems
8. “Good Evil Plan” (Adversarial & Misuse Defense)
9. Chaos & Fault Injection Strategy

---

## **7. Evaluation & Governance**

### **7.1 System-Level Evaluation Plan**

1. Evaluation Categories

   * Safety
   * Robustness
   * Traceability
   * Governance
2. Physical Safety Tests
3. Software Safety Tests
4. Sensor & Behavior Robustness Testing
5. Failure Mode Injection
6. Traceability Testing
7. Replayability Validation
8. Governance Audits
9. Continuous Evaluation Loop

---

### **7.2 AI / LLM Evaluation Strategy**

1. Core AI Evaluation Questions
2. Offline vs Online Evals
3. LangSmith Integration
4. RAGAS Integration
5. Agent Behavior Evals
6. CI/CD Quality Gates
7. Shadow & Canary Evals
8. Drift Detection
9. Model Rollback Triggers

---

## **8. Ideation & Early Concept Work**

### **8.1 Reachy Mini LangGraph Ideation Notes**

1. Layered Brain Architecture Concept
2. Initial BrainState Schema
3. Perception Strategy
4. Cognition & Planning Strategy
5. Skill Decomposition
6. Execution & Safety Concepts
7. Memory & Emotion Design Foundations
8. Design Principles

---

# ✅ **How You Can Use This TOC Immediately**

* ✅ Front page for **Confluence / Notion**
* ✅ Root `README.md` for your **Git repo**
* ✅ Printable **design review binder**
* ✅ Index for **investor / stakeholder packets**
* ✅ Anchor structure for **future ISO / safety audits**

---
