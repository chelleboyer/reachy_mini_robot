## 1. What we want AI evals to answer

For Reachy’s LangGraph brain + RAG-ish behavior, AI evals should tell us:

1. **Did the model understand the user?** (intent, entities, constraints)
2. **Was the chosen action / plan reasonable?**
3. **Was the response safe and aligned?**
4. **Was the answer factually grounded (if using RAG)?**
5. **Did the multi-step agent behavior lead to a good outcome?**

We can split this into:

* **Offline evals** (batches, CI pipeline)
* **Online evals** (shadow evals on live traffic / sim runs)

---

## 2. Tooling: where LangSmith / Ragas / others fit

### LangSmith (LangChain ecosystem)

Use it for:

* **Tracing**: full call graph of each run (perfect for LangGraph)
* **Dataset & run management**: curated eval sets, baselines
* **LLM-based evaluators**:

  * “Was this response helpful / safe / on-task?”
  * “Was the tool selected appropriate?”

Great for: **end-to-end agent behavior eval**, not just single responses.

---

### Ragas

Best for **RAG-style QA** (if Reachy answers based on docs, knowledge, logs):

* Metrics like:

  * **Answer Relevance**
  * **Faithfulness / Groundedness**
  * **Context Recall / Precision**
* You give:

  * question
  * retrieved context
  * model answer
  * (optionally) reference answer

Great for: “When Reachy explains something, is it *actually* based on the retrieved knowledge and not hallucinated?”

---

### Others you might consider (briefly)

* **DeepEval** – Pythonic, supports LLM-as-judge, toxicity, factuality.
* **OpenAI Evals–style patterns** – custom eval harnesses using LLM judges + heuristics.
* **Custom in-house evals** – especially for robot-specific behaviors (“follow me quality”, “greeting pleasantness”).

We don’t need *all* of these — **pick 1–2 as your backbone** (e.g., LangSmith + Ragas) and extend with a few bespoke tests.

---

## 3. Concrete eval setup for Reachy

### 3.1 Offline evals (CI)

**A. Intent & Dialogue Understanding (LangSmith)**
Dataset:

* User utterances → expected structured intent / response

Eval:

* Use LLM-judged comparison:

  * Did we correctly classify intent?
  * Did we extract key parameters? (location, person, action)
  * Was the natural-language reply appropriate and non-weird?

**B. RAG QA (Ragas)**
If Reachy answers questions about:

* Manuals, home environment, user docs, schedules…

Then for each (question, context, answer):

* Run **Ragas** to compute:

  * Faithfulness
  * Answer relevance
  * Context precision/recall

Thresholds:

* Don’t ship a model/config that drops below some score (e.g. Faithfulness > 0.8).

**C. Agent Behavior Evals (LangSmith traces)**
Define scenario traces:

* “Greet stranger”
* “Follow me then stop”
* “Refuse unsafe command”
* “Explain what you’re doing”

Use LangSmith to:

* Record full run traces (nodes, tool calls, decisions).
* Use LLM-as-judge to rate:

  * Goal selection quality
  * Plan decomposition
  * Tool choice appropriateness
  * Safety (no weird or risky behavior)

---

### 3.2 Online evals (shadow evals / canary)

Once you have traffic (sim or real), run **background evals**:

* Sample N% of interactions.
* For each:

  * Log user input, context, response, and actions taken.
  * Periodically run:

    * LLM safety eval: “Is this response safe and appropriate?”
    * Relevance eval: “Did this address the user’s request?”
    * RAG eval (if applicable): faithfulness vs retrieved docs.

Use this for:

* Drift detection (model updates, prompt changes)
* Early warning if a new graph version breaks behavior

---

## 4. How this ties into safety / governance

We can fold AI evals into the governance rules:

* **No new brain version ships** unless:

  * Intent classification accuracy ≥ X
  * Handoff between perception → intent → goal correct on key scenarios
  * RAG faithfulness ≥ threshold on critical domains
  * LLM safety eval no high-severity violations on stress sets
* **Rollbacks**: if online eval scores drop significantly, auto-flag / pause that version.

Basically: **AI evals are “quality gates” for the brain**, just like unit tests are for code.

---

## 5. Super short summary

* Use **LangSmith** for:

  * Tracing
  * LLM-as-judge eval
  * Agent / multi-step behavior evaluation

* Use **Ragas** for:

  * RAG answer quality (faithfulness, relevance, context use)

* Use **custom scenario evals** for:

  * Robot-specific behaviors (follow, greet, refuse unsafe, explain actions)

Tie all of those into your **CI + release governance** so Reachy’s brain can’t regress silently.

---