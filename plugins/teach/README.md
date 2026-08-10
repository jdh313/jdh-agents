# teach

A stateful, multi-session teaching workspace **routed into your Obsidian vault**. Each topic becomes a self-contained workspace folder under its best-fit context — mission, resources, glossary, and learning records live as vault notes, and so do the lessons themselves: markdown notes that transclude prose from the wiki and add a pure-CSS self-grading quiz on top. There is no HTML anywhere in this skill.

> Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (`skills/productivity/teach`), MIT © 2026 Matt Pocock. The original treats the current directory as the workspace; this fork routes durable artifacts into the vault. Upstream provenance is pinned in the skill's frontmatter; divergences are tracked in `skills/teach/UPSTREAM.md` via `skillsmith:upstream-review`. Design spec: `.docs/2026-06-12-teach-vault-routing.md`.

> **Requires** an Obsidian vault reachable via `obsidian-cli`.
>
> **Optional:** a `devonthink` MCP server connected **at the user level** unlocks grounding lessons in textbooks you own in DEVONthink (the highest-trust, most stable source class). The server is not bundled with this plugin — connect it yourself; without it, the skill falls back to web sources. See the "Owned textbooks (DEVONthink)" section in `skills/teach/SKILL.md`.

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
| `Records/*.md` | `type: learning-record` notes | ADR-style insights that steer future sessions and gate mastery claims |
| `lessons/*.md` | `type: lesson` notes | The primary unit of teaching — transcludes the wiki's prose, adds a quiz |

Cheat sheets, algorithm cards, and syntax references are no longer workspace files — they're ordinary `Reference/` wiki pages (state, returned to), while a lesson is process (get from not-understanding to understanding, rarely revisited). The lesson transcludes the wiki page's `## Gist`; it never restates it. A unified "all my learning" view comes from querying `type: learning-mission` across the vault (MOC/Base), not from folder colocation.

### Depth without a status field

Entry altitude for a new topic comes from two signals — the question's own altitude, and the density of the surrounding graph (existing `expands:` chains). But graph density only proves the agent *taught* something, never that the user *learned* it — so `Records/` stays the only gate on mastery claims, and whenever density and records disagree, the session opens with a one-line calibration check before any lesson gets written. This is deliberately not a new `understanding:` frontmatter field; the graph's shape already carries the signal.

### Philosophy

Deep learning needs **knowledge** (from trusted sources), **skills** (built through effortful, real-stakes practice), and **wisdom** (from real-world communities). Lessons are short, tied to the mission, and designed for storage strength over fluency. The four FORMAT files (`MISSION-FORMAT`, `RESOURCES-FORMAT`, `LEARNING-RECORD-FORMAT`, `GLOSSARY-FORMAT`) define each artifact's shape and load on demand.

### Setup

Install the shipped CSS snippet once per vault: copy `skills/teach/assets/teach-lesson.css` to `.obsidian/snippets/teach-lesson.css` and enable it under Settings → Appearance → CSS snippets. It backs the quiz component every lesson uses — no plugin, no JavaScript.
