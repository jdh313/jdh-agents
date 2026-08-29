---
name: grill
description: >-
  Grill the user relentlessly about a plan, decision, or idea — one question at
  a time, walking the design tree until you reach a shared understanding. Use
  when the user says "grill me", "grill this", "grill me on this plan", or asks
  to be interviewed hard about something before acting on it. Adapted from
  mattpocock/skills (MIT, © 2026 Matt Pocock).
allowed-tools:
  - Read
  - Grep
  - Glob
  - Agent
---

Interview the user relentlessly about every aspect of this until you reach a shared understanding.

Map the problem as a **design tree**: every decision branches into the decisions that hang off it. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask *now* without guessing at answers you haven't heard yet. A question whose answer depends on another still-open question is not on the frontier; it belongs later.

Track the frontier, but **ask one question from it at a time**, waiting for the user's answer before asking the next. Asking multiple questions at once is bewildering. Each answer reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and pick the next question from it.

Format each question like so:

```
❓ **Q1** - **<question title>**: <question body, may be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Always give your recommended answer. Number questions in sequence across the whole session, not per branch.

Finding *facts* is your job, never the user's. When a question needs a fact from the environment (filesystem, tools, connected apps), dispatch a subagent to find it rather than asking. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the subagent to report. Ask the next question the frontier already offers while it runs. The *decisions* are the user's — put each one to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms a shared understanding has been reached.
