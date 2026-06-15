# Mission.md Format

`Mission.md` lives at the workspace-folder root, as a vault note. It captures the _reason_ the user is learning this topic. Every teaching decision — what to teach next, which resources to surface, which exercises to design — should trace back to this document.

## Frontmatter

```yaml
---
owner: ai
type: learning-mission
status: active            # active | achieved | paused | abandoned
topic: {Topic}
started: YYYY-MM-DD
up: "[[{Context parent MOC}]]"
project: "[[{Project}]]"   # OPTIONAL — only when a real project/deliverable this learning serves already exists. Omit entirely otherwise. Never invent a project to fill it.
related: ["[[Learning Style]]"]
tags: [learning, topic/{x}, context/{y}]
---
```

`date created` / `date_modified` are managed by the Linter plugin — do not set them.

## Body template

```md
# Mission: {Topic}

## Why
{1-3 sentences. The concrete real-world goal the user is chasing. What changes in their life or work when they have this skill? Avoid abstract framings like "to understand X" — push for the underlying outcome.}

## Success looks like
- {A specific, observable thing the user will be able to do}
- {Another specific thing}
- {…}

## Constraints
- {Time, budget, prior commitments, learning preferences, anything that bounds the approach}

## Out of scope
- {Adjacent topics the user explicitly does not want to chase right now — protects the zone of proximal development}

## Teaching preferences
- {How the user wants to be taught — pace, format, things to keep in mind. Folded in from the upstream NOTES.md; record preferences here as they surface.}
```

## Rules

- **One mission per workspace.** If the user wants to learn two unrelated things, that is two workspaces.
- **Tether to a real project only when one exists.** If the topic serves a concrete deliverable the user already has — a vault project page or a Linear project — set `project:` to it so the mission's "why" is anchored to real work and a query can surface "what am I learning for project X." If there is no such project, **omit the field**; never spin up a project page just to have something to link. A standalone personal interest needs no project.
- **Concrete over abstract.** "Run a half marathon by October" beats "get fitter." "Ship a Rust CLI to my team" beats "learn Rust."
- **Push back on vagueness.** If the user cannot articulate why, interview them before writing anything. A bad mission is worse than no mission.
- **Revise when reality shifts.** Missions change. When the user's goal moves, update this note (and set `status:` accordingly) — don't leave a stale mission steering future sessions. Capture the shift in a learning record too.
- **Keep it short.** If `Mission.md` runs past a screen, it has stopped being a compass and started being a plan.
