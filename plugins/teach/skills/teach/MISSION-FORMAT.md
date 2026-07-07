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
stack_lens: "{e.g. Okta/OIDC, RBAC, FastAPI+Dishka}"   # OPTIONAL — when learning a concept THROUGH a specific stack. The technologies/patterns lessons teach through. Omit for stack-agnostic topics.
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

## Stack lens
- {OPTIONAL. The specific technologies/patterns this concept is being learned *through* — the productive constraint. e.g. "Auth taught through Okta/OIDC + RBAC + FastAPI/Dishka, as Meridian uses it."}
- {What this implies is *off-stack* and therefore not taught: e.g. "not SAML, not session cookies, not ABAC." Lessons bind to concept + this lens, never to exact code wiring (file/line/provider).}

## Out of scope
- {Adjacent topics the user explicitly does not want to chase right now — protects the zone of proximal development}

## Teaching preferences
- {How the user wants to be taught — pace, format, things to keep in mind. Folded in from the upstream NOTES.md; record preferences here as they surface.}
```

## Rules

- **One mission per workspace.** If the user wants to learn two unrelated things, that is two workspaces.
- **Name the stack lens when learning through a codebase.** If the goal is a durable concept learned *through* a specific stack (the common, productive case for work-tied topics), set `stack_lens:` and fill the Stack lens section. Lessons then teach concept + lens and treat exact code (file/line/provider) as illustration only. A change to the *lens* (a new auth provider, a paradigm switch) is a major change worth a freshness pass; a refactor that leaves the approach intact is not.
- **Tether to a real project only when one exists.** If the topic serves a concrete deliverable the user already has — a vault project page or a Linear project — set `project:` to it so the mission's "why" is anchored to real work and a query can surface "what am I learning for project X." If there is no such project, **omit the field**; never spin up a project page just to have something to link. A standalone personal interest needs no project.
- **Concrete over abstract.** "Run a half marathon by October" beats "get fitter." "Ship a Rust CLI to my team" beats "learn Rust."
- **Push back on vagueness.** If the user cannot articulate why, interview them before writing anything. A bad mission is worse than no mission.
- **Revise when reality shifts.** Missions change. When the user's goal moves, update this note (and set `status:` accordingly) — don't leave a stale mission steering future sessions. Capture the shift in a learning record too.
- **Keep it short.** If `Mission.md` runs past a screen, it has stopped being a compass and started being a plan.
