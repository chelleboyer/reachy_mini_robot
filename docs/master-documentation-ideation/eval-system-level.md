# 1. **Evaluation Categories**

We evaluate Reachy Mini across 4 top-level dimensions:

1. **Safety**
2. **Robustness**
3. **Traceability / Observability**
4. **Governance / Compliance**

Each dimension includes **quantitative and qualitative evaluation loops**.

---

# 2. **Safety Evaluation Plan**

### **2.1 Physical Safety Tests**

Performed on every release:

* Sudden obstacle insertion test
* Human approach test (front/side/back)
* Emergency stop responsiveness
* Fall detection response
* Overcurrent and torque-limiting test
* Behavior output bounding (speed/acceleration caps)

**Metrics:**

* Reaction time (<150ms target)
* Collision probability (0% tolerance)
* Consistency across multiple runs (variance <10%)

---

### **2.2 Software Safety Evaluation**

* Validate SafetyFilterNode under:

  * malformed actuator commands
  * hallucinated movement instructions
  * unexpected LLM outputs
* Ensure “danger state” always overrides goals/plan.

**Metrics:**

* 100% command rejection for unsafe outputs
* No unsafe motor motion under stress conditions

---

# 3. **Robustness Evaluation Plan**

### **3.1 Sensor Robustness**

Evaluate behavior under:

* Frame drops
* Noisy audio
* Partial occlusions
* Lighting changes
* Missing proximity data
* IMU drift (if wheels enabled)

**Metrics:**

* System remains operational under >80% sensor degradation
* No undefined behavior allowed

---

### **3.2 Behavior Robustness**

Evaluate key loops:

* Idle → interact → idle
* Follow → stop → follow (with wheels or simulated)
* Greeting → question → memory recall
* Mismatched intent resolution

**Metrics:**

* <5% failure rate across repeated cycles
* No deadlocks or frozen nodes
* BehaviorSelectorNode never selects unavailable skills

---

### **3.3 Failure Mode Testing**

Inject synthetic failures:

* Vision offline
* Audio offline
* Memory store offline
* Graph node error
* Skill node timeout
* Hardware command rejection

**Metric:**
Robot must fall back to safe expressive mode **within 300ms**.

---

# 4. **Traceability Evaluation Plan**

Traceability ensures production debugging is possible.

### **4.1 Logging Completeness Audit**

Check that every category of event has trace logs:

* Perception update
* Goal creation/destruction
* Plan generation
* Node activation
* Actuator commands
* Safety overrides
* User interaction events

**Metrics:**

* 100% of nodes emit trace events
* No orphan state updates (changes with no source)

---

### **4.2 Replayability Test**

* Run simulation from logs and guarantee deterministic output.
* Detect divergences between real vs replay.

**Metric:**

> Replay determinism score: **>95% identical node outputs**

---

### **4.3 Brain App Observability Test**

The inspector must show:

* Active goal
* Active behavior
* Relevant sensor summaries
* Node execution order
* Reason for next action

**Metric:**

> 100% of critical fields visible in UI without cracks in the chain of reasoning.

---

# 5. **Governance Evaluation Plan**

Governance ensures responsible operation and safe iteration.

### **5.1 Versioning Governance**

* Validate that each release contains:

  * Versioned graph
  * Versioned nodes
  * Signed build
  * Changelog
* Attempt to load unsigned or mismatched graph.

**Metric:**

> Robot must reject any unapproved graph version.

---

### **5.2 Capability Governance**

Evaluate that nodes only access approved state slices:

* Perception nodes cannot write mobility commands
* Skill nodes cannot override safety flags
* Memory nodes cannot create goals
* Emotion system cannot override SafetyFilter

**Metric:**

> 100% adherence to node read/write contract.

---

### **5.3 User Governance**

Evaluate:

* Who is allowed to modify memory
* Which commands require confirmation
* Multi-user priority resolution
* Interaction logs privacy controls

**Metric:**

> No uncontrolled state changes without user identity known.

---

# 6. **Evaluation Process Structure**

### **6.1 Continuous Evaluation Loop**

Performed every development cycle:

```text
[Design] → [Sim Evaluation] → [Hardware Evaluation] → [Beta Evaluation] → [Release]
```

### **6.2 Required Before Release**

* Safety test suite pass
* Robustness suite pass
* Replay suite pass
* Governance audit pass
* No critical or high severity errors

---

# 7. **The Concise Takeaway**

This plan ensures:

* The robot **fails safely**
* Behaviors remain **predictable and explainable**
* Developers can **trace every decision** back to origin
* Governance prevents drift into unsafe territory
* MVP → Production becomes a **controlled evolution**, not a chaotic rewrite

---
