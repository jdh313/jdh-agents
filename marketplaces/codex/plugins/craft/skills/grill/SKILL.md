---
name: grill
description: >-
  Grill the user relentlessly about a plan, decision, or idea — one question at
  a time, walking the decision tree until you reach a shared understanding. Use
  when the user says "grill me", "grill this", "grill me on this plan", or asks
  to be interviewed hard about something before acting on it. Adapted from
  mattpocock/skills (MIT, © 2026 Matt Pocock).
---

Interview the user relentlessly about every aspect of this until you reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, propose a recommended answer.

Ask one question at a time, waiting for the user's response before continuing. Asking multiple questions at once is bewildering.

If a *fact* can be found by exploring the environment (filesystem, tools, connected apps), look it up rather than asking. The *decisions* are the user's — put each one to them and wait for their answer.

Do not act on it until the user confirms a shared understanding has been reached.
