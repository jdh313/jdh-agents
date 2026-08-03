---
name: zoom-out
description: >-
  Explicit invocation only. Give broader context or a higher-level perspective
  when the user asks to zoom out or map how code fits into the bigger picture.
  Never invoke implicitly. Adapted from mattpocock/skills (MIT, © 2026 Matt
  Pocock).
allowed-tools:
  - Read
  - Grep
  - Glob
---

Claude Code should invoke this skill only on the explicit trigger phrases in
the description. Codex enforces the same behavior through
[`agents/openai.yaml`](agents/openai.yaml).

I don't know this area of code well. Go up a layer of abstraction. Give me a map of all the relevant modules and callers, using the project's domain glossary vocabulary.
