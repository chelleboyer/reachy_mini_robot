## Core Idea: Separate **Canonical State** from **Runtime Core State**

Best-practice way to shrink this:

1. **Keep a rich, canonical model** (what we already designed) in your *internal brain implementation* / backing store.
2. Expose a **small, focused `CoreBrainState`** for:

   * LangGraph node contracts
   * Streaming to the UI
   * Debugging

And then:

* Use **IDs + references** instead of inlining big blobs.
* Use **patches/diffs** over the wire instead of full-state every tick.
* Move large/slow data (full map, memory, logs) to **separate stores/endpoints**.

Think **“blackboard”**: small, shared working memory that points to heavier stuff stored elsewhere.

---

## 1. What should be in the *small* `CoreBrainState`?

Ask: *What do most nodes need, most of the time, to decide the next action?*

You can get away with something like:

```ts
CoreBrainState {
  meta: { robot_id, session_id, tick }
  mode: "idle" | "follow" | "explore" | "interact" | "task" | "error"

  // Summaries, not full sensor data
  presence: {
    any_human: boolean
    primary_human_id?: string
    distance_to_primary?: number // m
    danger: boolean              // obstacle/cliff alarm
  }

  interaction: {
    user_id?: string
    last_user_utterance?: string
    user_intent?: { type: string, params?: Record<string, any> }
    pending_question?: string
  }

  goal: {
    id?: string
    type?: string
    status: "none" | "pending" | "in_progress" | "blocked"
  }

  plan: {
    active_step?: {
      id: string
      action: string
    } | null
  }

  emotion: {
    valence: number  // -1 .. 1
    arousal: number  // 0 .. 1
  }

  actuators: {
    drive?: { vx: number; vy: number; omega: number } | null
    head?: { pan?: number; tilt?: number; track_human_id?: string } | null
    arms?: { gesture_id?: string } | null
    voice?: { text?: string } | null
  }

  // Very light status
  status: {
    battery_level: number   // %
    is_charging: boolean
    error_severity: "ok" | "warn" | "error"
  }
}
```

That’s **an order of magnitude smaller** than the full schema and is plenty for:

* The UI to draw “what is Reachy doing right now?”
* Nodes to decide “what’s the next step?”

Everything else becomes **secondary state / services**.

---

## 2. Where does the “big stuff” go?

### A. Static + Slow-changing data → Config / separate endpoints

* `capabilities` (has wheels? arms? sensors?)
* Hardware info
* Personality traits defaults
* Map, known places

These can live in:

* `/config` endpoint
* Separate `RobotConfig` object loaded at startup
* Cached by nodes as needed

No need to shove that through every tick.

---

### B. Heavy Perception Data → Perception Store

* Full detection lists
* Bounding boxes
* Depth maps
* Raw sensor values

Access pattern:

* Perception nodes talk to camera/vision backends and **write a summary** into:

  * A `PerceptionState` service / topic
  * Or a dedicated small sub-object

From the brain’s perspective:

* `CoreBrainState.presence` just holds:

  * `any_human`
  * `primary_human_id`
  * `distance_to_primary`
  * `danger` flag

If a specific node really needs the full vision detail:

* It can call a **`getPerceptionDetails(frame_id)`** helper or subscribe to that topic, not bloat `CoreBrainState`.

---

### C. Full World Model + Map → World Model Store

Keep:

* Full occupancy grid
* Object list with rich metadata
* Historical pose traces

In a separate service / topic.

`CoreBrainState` just keeps:

* `mode`
* Active `goal` + `plan` summary
* Maybe a minimal `self_pose` if needed; or not even that if only skills care.

---

### D. Memory → Memory Service

Memories can get huge.

Pattern:

* `CoreBrainState.interaction.contextual_memory`
  → Replace with **just IDs**:

```ts
contextual_memory_ids: string[]
```

And you fetch details from a `MemoryService` as needed.

The UI can have a **“Memory” tab** that calls `/memory/:id`, instead of you trying to squeeze everything into the live state.

---

### E. Logs → Logging Infra

Logs are classic:

* Ship them to a logging system (files, Loki, Elastic, whatever).
* `CoreBrainState` can have at most:

  * `last_log_entry_id`
  * or a tiny list of last N **summaries**.

The Brain App can query `/logs?since=...` if it wants detail.

---

## 3. Use **Patch / Diff Updates** for Streaming

Even the **small** `CoreBrainState` doesn’t need full resend every frame.

Best-practice pattern:

* Brain holds the **authoritative `CoreBrainState`**.
* Every tick, compute **diff** against previous tick:

  * Only send fields that changed.
* Use a small protocol like:

```jsonc
{
  "tick": 123,
  "patch": {
    "mode": "follow",
    "presence": {
      "any_human": true,
      "primary_human_id": "user-1",
      "distance_to_primary": 0.9
    },
    "actuators": {
      "drive": { "vx": 0.1, "vy": 0.0, "omega": 0.0 }
    }
  }
}
```

The Reachy Brain App and any observers maintain their own local copy and **apply patches**.

This is **very WebSocket-friendly** and scales beautifully.

---

## 4. How LangGraph Nodes See State

You don’t have to give every node the full canonical state.

Instead:

* Most nodes:

  * Get **`CoreBrainState`** (small)
* Specialized nodes:

  * Call helper services:

    * `PerceptionAPI.get_frame_details(frame_id)`
    * `MemoryAPI.query(context)`
    * `MapAPI.get_path(start, target)`

This keeps:

* Graph simpler
* State slim
* Responsibilities separated

---

## 5. Concrete Refactor Plan

1. **Downgrade the big schema** you liked into:

   * `CanonicalBrainModel` (internal, not broadcast)
2. **Define a lean `CoreBrainState`** like the one above.
3. **Move heavy subtrees** into separate services:

   * `PerceptionState`
   * `WorldModelStore`
   * `MemoryStore`
   * `LogStore`
4. **Implement patch streaming** from `CoreBrainState` → UI.
5. **Restrict node read/write contracts**:

   * Document which fields a node can touch.
   * Prevent random bloat creeping back into core.

---