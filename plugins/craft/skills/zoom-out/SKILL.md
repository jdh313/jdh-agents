---
name: zoom-out
description: Explicit invocation only. Give broader context or a higher-level perspective when the user asks to zoom out or map how code fits into the bigger picture. Never invoke implicitly. Adapted from mattpocock/skills (MIT, © 2026 Matt Pocock).
upstream:
  repo: mattpocock/skills
  path: skills/engineering/zoom-out
  reviewed_sha: 7afa86d3a5dd
  reviewed: 2026-07-27
  status: upstream-removed
  removed_sha: e112a6b03cd7
allowed-tools:
  - Read
  - Grep
  - Glob
---

Claude Code should invoke this skill only on the explicit trigger phrases in
the description. Codex enforces the same behavior through
[`agents/openai.yaml`](agents/openai.yaml).

I don't know this area of code well. Go up a layer of abstraction. Give me a map of all the relevant modules and callers, using the project's domain glossary vocabulary.
