# Contract Template

Used by `spec-flow:start` to scaffold a new contract in `.docs/YYYY-MM-DD-<slug>.md`. The body below is the literal scaffold the start skill produces.

## Scaffold

```markdown
---
status: active
topic: <slug>
started: YYYY-MM-DD
---

# <Goal in plain language, one line>

## What we're doing

- <one or two bullets describing the change>

## Why

- <one or two bullets — the trigger or motivation; the reason future-you cares>

## Approach

- <larger strokes only — architecture, libraries, integration points>
- <no task list, no enumeration>

## Out of scope

- <explicit non-goals — fence against the AI "helpfully" expanding>

## Open questions

- <things deferred to during implementation — these inform cadence at handoff>
```

## Conventions

- **Bullets / lists / tables over prose.** Short, scannable, retrievable. Matches the user's general reading style.
- **Approach is larger strokes only.** If a task list is emerging, it belongs in implementation, not in the contract.
- **Open questions are load-bearing.** Their presence/absence shapes the cadence conversation at implementation handoff (all-at-once vs check in after a piece).
- **State signaling:** `status: active` while the contract is in flight. On done, the file moves to `.docs/archive/`. Placement signals state; the frontmatter field is informational redundancy.
- **No amendments without sign-off.** AI proposes contract edits during implementation; user accepts before any edit lands.

## Out-of-scope sections

Things the contract deliberately does *not* include:

- **Task list / enumerated steps** — belongs in implementation, not the contract.
- **System spec / "current state of the app"** — durable layer's job (README, ndr atoms, code).
- **Cross-change roadmap** — spec-flow is single-change-scoped.
- **Test plan / acceptance criteria** — handled in implementation; can surface in Open questions if non-obvious.
