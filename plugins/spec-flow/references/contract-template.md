# Contract Template

Used by `spec-flow:draft` to scaffold a new contract. The body below is the literal scaffold the draft skill produces.

The contract shape is **host-agnostic** — the same six sections work whether the contract lives in `.docs/YYYY-MM-DD-<slug>.md` or in a Linear ticket description. Only frontmatter is file-only (Linear has its own metadata). See `hosts.md` (same directory) for the host-selection decision and per-host behavior.

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

## Done when

- <observable outcome — what the user/system can now do that it couldn't before>
- <visible state change — file exists, command works, endpoint returns, etc.>
- <verification gate — "tests pass", or "manual smoke: X" if non-obvious>

## Open questions

- <things deferred to during implementation — these inform cadence at handoff>
```

## Conventions

- **Bullets / lists / tables over prose.** Short, scannable, retrievable. Matches the user's general reading style.
- **Approach is larger strokes only.** If a task list is emerging, it belongs in implementation, not in the contract.
- **Done when is observable, not procedural.** 2–4 bullets describing visible outcomes — "command returns the head atom", not "implement walk function in reader.py". Bullets, not checkboxes (checkboxes invite task-list creep). Load-bearing for the close skill's review pass.
- **Open questions are load-bearing.** Their presence/absence shapes the cadence conversation at implementation handoff (all-at-once vs check in after a piece).
- **State signaling:** `status: active` while the contract is in flight. On done, the file moves to `.docs/archive/`. Placement signals state; the frontmatter field is informational redundancy.
- **No amendments without sign-off.** AI proposes contract edits during implementation; user accepts before any edit lands.

## Out-of-scope sections

Things the contract deliberately does *not* include:

- **Task list / enumerated steps** — belongs in implementation, not the contract.
- **System spec / "current state of the app"** — durable layer's job (README, ndr atoms, code).
- **Cross-change roadmap** — spec-flow is single-change-scoped.
- **Enumerated acceptance criteria / test plan** — `Done when` captures verification gates as observable outcomes; specific test cases stay in implementation.
