---
name: retro
description: >-
  End-of-cycle retro note for CartaOS Linear (team CAR). This skill should be
  used when the user invokes `/pm:retro`, says "cycle retro", "wrap up the
  cycle", "retro this cycle", "what happened this cycle", or signals the end
  of a Thu→Wed cycle. Pulls the just-closed cycle from Linear (or a
  user-specified cycle), classifies tickets into shipped / carried / canceled /
  added-mid-cycle, pulls vault session notes and NDR atoms from the cycle
  window, reads the last 2–3 prior retros to spot recurring patterns, drafts
  a retro note, and writes it to the vault via `librarian:note-editor`.
  Observational and read-only on Linear — never mutates tickets. Pairs with
  `pm:groom` (forward-looking) on the same Thursday cadence.
argument-hint: "[cycle name or any date in the cycle window]"
allowed-tools:
  # Linear — cycle + ticket history (read-only)
  - mcp__linear-server__list_cycles
  - mcp__linear-server__list_issues
  - mcp__linear-server__get_issue
  - mcp__linear-server__list_comments
  # Obsidian — read prior retros + session notes (writes go via librarian)
  - mcp__obsidian-mcp__search_notes
  - mcp__obsidian-mcp__read_multiple_notes
  # NDR atoms — find decisions captured during cycle window
  - Read
  - Grep
  - Bash
  # Compose with librarian:note-editor (vault write) and ndr:decisions
  - Skill
  - Agent
---

# retro

## Overview

End-of-cycle retro for CartaOS Linear (team `CAR`). The backward-looking counterpart to `pm:groom`: where groom plans forward, retro records backward. Pulls the just-closed cycle, classifies tickets by outcome, surfaces patterns across recent cycles, and writes a durable retro note to the vault.

Synthesis half of the Thursday rhythm — the chat output captures the story of the cycle; the vault note is the durable record that future retros read for pattern detection.

## Inputs (load-bearing constants)

- **Linear team:** `CAR` (Carta Healthcare). Single-team workspace.
- **Default target cycle:** Most recently closed cycle. Override with the argument (cycle name or any date inside the cycle window).
- **Vault project root:** `~/Loose Ends/Carta/Projects/CartaOS/`
- **Retro destination folder:** `~/Loose Ends/Carta/Projects/CartaOS/Retros/` — created by `librarian:note-editor` on first write.
- **NDR atoms root:** `~/Loose Ends/Decisions/` — filter to atoms with `project: [[CartaOS]]` AND a `date:` (or equivalent) frontmatter field inside the cycle window.
- **Pattern-detection window:** the most recent 2–3 retros in the Retros folder. On the first retro, this section is omitted.
- **Issue shape spec:** `../../references/issue-shape.md` (plugin reference). Used when characterizing carried tickets ("missing Done when:" vs. "blocked").
- **Layer policy:** `../../references/layer-policy.md` (plugin reference). Used when surfacing "did we honor the layer policy this cycle?" — any orphans landed, any subissue temptations resisted, any epic that earned its keep.

## Procedure

1. **Resolve the target cycle.** If an argument was passed, find the matching cycle via `mcp__linear-server__list_cycles` (match by name, or find the cycle whose window contains the date). Otherwise, take the most recently closed cycle. Confirm the window with the user before scanning: e.g. "Retro for Cycle 12, Thu 2026-05-28 → Wed 2026-06-03?".

2. **Pull cycle tickets.** Use `mcp__linear-server__list_issues` filtered to the resolved cycle. Capture state at cycle close, priority, `createdAt`, `updatedAt`. For tickets whose history matters (carried, mid-cycle adds), use `list_comments` to reconstruct timing.

3. **Classify each ticket** along two axes:
   - **Outcome axis:** Shipped (Done at close) / Carried (open at close, still in next cycle) / Canceled (Canceled state) — one of three.
   - **Origin axis:** Added mid-cycle (created inside cycle window) vs. planned (created before cycle start). Orthogonal to outcome — a mid-cycle add can ship or carry.

4. **Pull NDR atoms created during the cycle window.** Scan `~/Loose Ends/Decisions/` for atoms with `project: [[CartaOS]]` AND a `date:` (or equivalent) frontmatter field inside the window. These are the decisions captured during the cycle — material for the Decisions section.

5. **Pull vault session notes from the cycle window.** Search `~/Loose Ends/Carta/Projects/CartaOS/` for notes touched during the window. Use these for context on shipped/carried tickets and to surface notable moments.

6. **Read prior retros for pattern detection.** Read the most recent 2–3 retros from `~/Loose Ends/Carta/Projects/CartaOS/Retros/` (omit on first retro). Look for:
   - Tickets carried across multiple cycles (chronic friction)
   - Recurring blocker types (e.g. infra dependency, scope creep, awaiting stakeholder)
   - Mid-cycle add patterns (plan respected vs. churned)
   - Cancellation patterns (was the work duplicated by an NDR moot, or genuinely deprioritized?)

7. **Synthesize the retro.** Draft the body per the Body structure below. One-line characterization of the cycle in the Summary; specifics in sections; patterns at the end. If the first retro, omit the Patterns section.

8. **Present the draft in chat for review.** User may edit, ask for changes, or approve.

9. **Write via librarian on approval.** Dispatch `librarian:note-editor` with the drafted content, target path, and frontmatter shape. The agent reads the vault `CLAUDE.md` and honors folder/frontmatter conventions; create the Retros folder on first write. Skip the write if the user declines or if a retro file already exists for the target cycle (ask before overwrite).

## Body structure

**Filename:** `YYYY-MM-DD Cycle Retro.md` where `YYYY-MM-DD` is the cycle close date (Wednesday). Defer to `librarian:note-editor` if the vault has a different convention for cycle/retro filenames.

**Frontmatter:**

```yaml
---
type: retro
project: "[[CartaOS]]"
cycle: <cycle-name-from-linear>
cycle_start: YYYY-MM-DD  # Thursday
cycle_end: YYYY-MM-DD    # Wednesday (close)
date_created: YYYY-MM-DD
---
```

**Body sections, in order:**

### `# Cycle Retro — <cycle-name>`

One-line window: `Cycle window: Thu YYYY-MM-DD → Wed YYYY-MM-DD`

### `## Summary`

- Shipped: N
- Carried: M
- Canceled: P
- Added mid-cycle: Q  *(orthogonal to outcome; overlaps with the above)*

Then one-line characterization of the cycle.

Example: *"Solid cycle — 7 shipped, 4 carried (3 on a single Aurora-budget blocker chain), 1 canceled (mooted by ndr:0091). Plan fidelity strong: 1 mid-cycle add."*

### `## Shipped`

One bullet per shipped ticket:

- **CAR-N** — title — one-line context, NDR link if relevant

### `## Carried`

For each carried ticket:

- **CAR-N** — title
  - Reason: `blocked` | `scope-grew` | `deprioritized` | `partial` | `missing-spec`
  - Going into next cycle: `continued` | `paused` | `re-scoped`

### `## Canceled` (omit if empty)

- **CAR-N** — title — reason (e.g. "mooted by ndr:0091 supersession" or "deprioritized")

### `## Added mid-cycle` (omit if empty)

Tickets created inside the cycle window — measures plan fidelity.

- **CAR-N** — title — what triggered it (link to session note if known); outcome (shipped | carried | canceled)

### `## Decisions`

NDR atoms captured during the window:

- `ndr:NNNN` — slug — one-line context

(Omit section if no NDR atoms landed in window.)

### `## Patterns` (omit on first retro)

Observations across this cycle + the last 2–3 retros:

- Chronic carries (e.g. "`Customer Documentation: ingest` carried 3 consecutive cycles — consider scope split")
- Recurring blocker types
- Scope-creep instances
- Plan fidelity trend (e.g. "mid-cycle adds: 1, 0, 1 across last 3 cycles — plan is holding")

### `## Notable session moments` (optional)

Links to session notes worth re-reading:

- `[[YYYY-MM-DD Working Session]]` — one-line summary of why it matters

### `## Open questions / followups`

Things flagged in chat or session notes that need an owner:

- *Question / followup phrase* — proposed action (e.g. "open ticket via `pm:author`", "discuss with Andrew next planning meeting")

## Rules

- **Read-only on Linear.** Retro never edits tickets, never transitions states, never changes priorities.
- **Confirm cycle window with the user** before scanning — wrong cycle = wasted scan, and Linear cycle naming can drift.
- **Show the full draft in chat** before writing to vault. The user reviews and approves before any file lands.
- **Use librarian for the write.** Do not call `mcp__obsidian-mcp__*` create/update tools directly. Dispatch `librarian:note-editor` with the drafted content; the agent owns vault conventions.
- **One retro per cycle.** If a retro file already exists for the target cycle, ask before overwriting.
- **Omit empty sections.** Canceled / Added mid-cycle / Decisions / Patterns / Notable moments / Open questions are omitted entirely when empty — don't write placeholder headers.

## Composes with

- **`linear-workflow`** (linear plugin) — not directly called; retro just reads Linear state.
- **`librarian:note-editor`** (librarian plugin agent) — performs the vault write. Honors frontmatter/folder conventions; creates the `Retros/` folder on first invocation.
- **`librarian:vault-reader`** (librarian plugin agent) — optional alternative to inline `mcp__obsidian-mcp__*` reads for the session-note + prior-retro pass. Useful when the read scope is large.
- **`ndr:decisions`** (ndr plugin) — optional: dispatch when the retro narrative needs the current state of a referenced decision (e.g. confirming a cancellation reason).

## See also

- **`groom`** skill in this plugin — forward-looking counterpart on the same Thursday cadence.
- **`references/issue-shape.md`** — required-field spec; useful for characterizing why a ticket was carried (missing `Done when:` vs. blocked).
- **`references/layer-policy.md`** — active-layers spec; useful for surfacing layer-policy adherence in retro narrative.
