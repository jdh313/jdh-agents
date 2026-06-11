# teach

A stateful, multi-session teaching workspace **routed into your Obsidian vault**. Each topic becomes a self-contained workspace folder under its best-fit context — its mission, resources, glossary, and learning records live as vault notes; its lessons and cheat sheets stay as self-contained HTML files.

> Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (`skills/productivity/teach`), MIT © 2026 Matt Pocock. The original treats the current directory as the workspace; this fork routes durable artifacts into the vault. Upstream provenance is pinned in the skill's frontmatter; divergences are tracked in `skills/teach/UPSTREAM.md` via `provenance:upstream-review`. Design spec: `.docs/2026-06-12-teach-vault-routing.md`.

> **Requires** an Obsidian vault reachable via `obsidian-cli`.

## /teach — learn something over time

```
/teach French subjunctive
/teach how Postgres MVCC works
/teach the half-moon yoga pose
```

Explicit-invocation only (`disable-model-invocation: true`) — it won't fire on its own. On invocation it:

1. **Grounds in how you learn** — reads `Personal/Manual of Me/Learning/Learning Style.md` and biases toward real-stakes practice over recall drills (no flashcard layer, by design).
2. **Resolves the context** — infers where the topic belongs (`Reference/Developer/`, `Hobbies/`, …), proposes a path, and confirms with you. The vault is context-first; there's no top-level `Learning/` folder.
3. **Builds/extends the workspace** under `<Context>/<Topic>/`:

| Artifact | Form | Role |
|---|---|---|
| `Mission.md` | `type: learning-mission` note | *Why* you're learning this + teaching prefs — grounds every lesson |
| `Resources.md` | index note → `Sources/` | High-trust sources; ingestible material goes to the vault's `Sources/` |
| `Glossary.md` | working note → `Reference/` wiki | Canonical terms; durable ones graduate to wiki concept notes |
| `Records/*.md` | `type: learning-record` notes | ADR-style insights that steer future sessions |
| `lessons/*.html` | HTML files | The primary unit of teaching — one self-contained, beautiful lesson each |
| `reference/*.html` | HTML files | Print-beautiful cheat sheets, algorithm cards, pose sequences |

A unified "all my learning" view comes from querying `type: learning-mission` across the vault (MOC/Base), not from folder colocation.

### Philosophy

Deep learning needs **knowledge** (from trusted sources), **skills** (built through effortful, real-stakes practice), and **wisdom** (from real-world communities). Lessons are short, tied to the mission, and designed for storage strength over fluency. The four FORMAT files (`MISSION-FORMAT`, `RESOURCES-FORMAT`, `LEARNING-RECORD-FORMAT`, `GLOSSARY-FORMAT`) define each artifact's shape and load on demand.
