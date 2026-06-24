---
name: retro
description: >-
  End-of-cycle retro for a team Linear workspace. This skill should be used
  when the user invokes `/pm:retro`, says "cycle retro", "wrap up the cycle",
  "retro this cycle", "what happened this cycle", or signals the end of a
  weekly cycle. Pulls the just-closed cycle from Linear (or a user-specified
  cycle), classifies tickets into shipped / carried / canceled / added-mid-cycle
  with assignee attribution, optionally pulls vault session notes and ndr atoms
  from the cycle window, reads the last 2–3 prior retros to spot recurring
  patterns, drafts a retro, and writes it to a Linear document by default
  (shared visibility) with an optional personal vault copy. Observational and
  read-only on Linear tickets — never mutates tickets. Pairs with `pm:groom`
  (forward-looking) on the same weekly cadence.
argument-hint: "[cycle name or any date in the cycle window]"
allowed-tools:
  # Linear — cycle + ticket history (read-only); document write for retro output
  - mcp__linear-server__list_cycles
  - mcp__linear-server__list_issues
  - mcp__linear-server__get_issue
  - mcp__linear-server__list_comments
  - mcp__linear-server__list_projects
  - mcp__linear-server__list_documents
  - mcp__linear-server__save_document
  # Obsidian — read prior retros + session notes; optional personal vault write
  - mcp__obsidian-mcp__search_notes
  - mcp__obsidian-mcp__read_multiple_notes
  # ndr atoms — find decisions captured during cycle window
  - Read
  - Grep
  - Bash
  # Compose with note-editor (vault write) and ndr:decisions
  - Skill
  - Agent
---

# retro

## Overview

End-of-cycle retro for a team Linear workspace (team `TEAM`, two collaborators). The backward-looking counterpart to `pm:groom`: where groom plans forward, retro records backward. Pulls the just-closed cycle, classifies tickets by outcome with assignee attribution, surfaces patterns across recent cycles, and writes a durable retro document.

**Output priority:** Write the retro to a Linear document by default (shared visibility for both collaborators). The personal vault copy is optional — write it on request or if Linear isn't available (graceful fallback). The team Linear document is the primary artifact; the vault copy is the personal supplement.

Synthesis half of the weekly rhythm — the chat output captures the story of the cycle; the Linear document is the shared durable record that future retros read for pattern detection.

## Inputs (load-bearing constants)

- **Linear team:** `TEAM` — substitute your team key. Single-team workspace.
- **Default target cycle:** Most recently closed cycle. Override with the argument (cycle name or any date inside the cycle window).
- **Vault project root:** `~/Loose Ends/Projects/<project>/` — adjust to your vault layout.
- **Retro destination folder:** `~/Loose Ends/Projects/<project>/Retros/` — created on first write.
- **ndr atoms root:** `~/Loose Ends/Decisions/` — filter to atoms whose `project:` frontmatter matches AND whose `date:` (or equivalent) frontmatter field falls inside the cycle window. Skip without the external `ndr` plugin.
- **Pattern-detection window:** the most recent 2–3 retros in the Retros folder. On the first retro, this section is omitted.
- **Cycle cadence:** weekly, per your Linear workspace settings. Examples assume Thu→Wed (close Wednesday EOD).
- **Issue shape spec:** `../../references/issue-shape.md` (plugin reference). Used when characterizing carried tickets ("missing Done when:" vs. "blocked").
- **Layer policy:** `../../references/layer-policy.md` (plugin reference). Used when surfacing "did we honor the layer policy this cycle?" — any orphans landed, any subissue temptations resisted, any epic that earned its keep.

## Procedure

1. **Resolve the target cycle.** If an argument was passed, find the matching cycle via `mcp__linear-server__list_cycles` (match by name, or find the cycle whose window contains the date). Otherwise, take the most recently closed cycle. Confirm the window with the user before scanning: e.g. "Retro for Cycle 12, Thu 2026-05-28 → Wed 2026-06-03?".

2. **Pull cycle tickets.** Use `mcp__linear-server__list_issues` filtered to the resolved cycle. Capture state at cycle close, priority, `createdAt`, `updatedAt`, and `assignee`. For tickets whose history matters (carried, mid-cycle adds), use `list_comments` to reconstruct timing.

3. **Classify each ticket** along two axes:
   - **Outcome axis:** Shipped (Done at close) / Carried (open at close, still in next cycle) / Canceled (Canceled state) — one of three.
   - **Origin axis:** Added mid-cycle (created inside cycle window) vs. planned (created before cycle start). Orthogonal to outcome — a mid-cycle add can ship or carry.

4. **Pull ndr atoms created during the cycle window.** Scan the ndr atoms root for atoms matching the project with a date inside the window. These are the decisions captured during the cycle — material for the Decisions section. (Skip without the ndr plugin.)

5. **Pull vault session notes from the cycle window.** Search the vault project root for notes touched during the window. Use these for context on shipped/carried tickets and to surface notable moments. (Skip without a vault.)

6. **Read prior retros for pattern detection.** Read the most recent 2–3 retros from the Retros folder (omit on first retro). Look for:
   - Tickets carried across multiple cycles (chronic friction)
   - Recurring blocker types (e.g. infra dependency, scope creep, awaiting stakeholder)
   - Mid-cycle add patterns (plan respected vs. churned)
   - Cancellation patterns (was the work duplicated by an ndr moot, or genuinely deprioritized?)

7. **Synthesize the retro.** Draft the body per the Body structure below. One-line characterization of the cycle in the Summary; specifics in sections; patterns at the end. If the first retro, omit the Patterns section.

8. **Present the draft in chat for review.** User may edit, ask for changes, or approve.

9. **Write the retro on approval.** Two outputs; Linear is primary:

   - **Linear document (default — shared visibility):** Look up the active project via `mcp__linear-server__list_projects`. Create or replace a document in that project titled `Cycle Retro — <cycle-name>` using `mcp__linear-server__save_document`. This is the shared team artifact; both collaborators can read and comment here.
   - **Personal vault copy (optional):** Write to `~/Loose Ends/Projects/<project>/Retros/YYYY-MM-DD Cycle Retro.md` only if the user requests it OR if Linear is unavailable. If the external `librarian` setup is present, dispatch its `note-editor` agent with the drafted content, target path, and frontmatter shape — it reads the vault `CLAUDE.md` and honors folder/frontmatter conventions. Without librarian, write the note directly (create the Retros folder on first write).

   Ask once: "Write to Linear and optionally the vault?" Let the user choose. Skip the write entirely if the user declines. If a retro document/note already exists for the target cycle, ask before overwriting.

## Body structure

**Filename:** `YYYY-MM-DD Cycle Retro.md` where `YYYY-MM-DD` is the cycle close date. Defer to your vault's conventions if it has a different shape for cycle/retro filenames.

**Frontmatter:**

```yaml
---
type: retro
project: "[[<project>]]"
cycle: <cycle-name-from-linear>
cycle_start: YYYY-MM-DD  # e.g. Thursday
cycle_end: YYYY-MM-DD    # e.g. Wednesday (close)
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

Example: *"Solid cycle — 7 shipped, 4 carried (3 on a single infra-budget blocker chain), 1 canceled (mooted by ndr:0091). Plan fidelity strong: 1 mid-cycle add."*

### `## Shipped`

One bullet per shipped ticket, with assignee attribution:

- **TEAM-N** — title [@assignee] — one-line context, ndr link if relevant

Attribution enables pattern detection across retros (e.g. "carried 3 cycles" names who). Use the Linear `assignee` field captured in step 2; write `[unassigned]` if none.

### `## Carried`

For each carried ticket, with assignee attribution:

- **TEAM-N** — title [@assignee]
  - Reason: `blocked` | `scope-grew` | `deprioritized` | `partial` | `missing-spec`
  - Going into next cycle: `continued` | `paused` | `re-scoped`

### `## Canceled` (omit if empty)

- **TEAM-N** — title [@assignee] — reason (e.g. "mooted by ndr:0091 supersession" or "deprioritized")

### `## Added mid-cycle` (omit if empty)

Tickets created inside the cycle window — measures plan fidelity.

- **TEAM-N** — title [@assignee] — what triggered it (link to session note if known); outcome (shipped | carried | canceled)

### `## Decisions`

ndr atoms captured during the window:

- `ndr:NNNN` — slug — one-line context

(Omit section if no ndr atoms landed in window, or if you don't use ndr.)

### `## Patterns` (omit on first retro)

Observations across this cycle + the last 2–3 retros:

- Chronic carries, named by assignee (e.g. "`Docs ingest` [@you] carried 3 consecutive cycles — consider scope split")
- Recurring blocker types, and whose work they block
- Scope-creep instances
- Plan fidelity trend (e.g. "mid-cycle adds: 1, 0, 1 across last 3 cycles — plan is holding")

### `## Notable session moments` (optional)

Links to session notes worth re-reading:

- `[[YYYY-MM-DD Working Session]]` — one-line summary of why it matters

### `## Open questions / followups`

Things flagged in chat or session notes that need an owner:

- *Question / followup phrase* — proposed action (e.g. "open ticket via `pm:author`", "raise with stakeholder at next planning meeting")

## Rules

- **Read-only on Linear tickets.** Retro never edits tickets, never transitions states, never changes priorities. Writing the Linear retro document is write-to-doc, not write-to-ticket.
- **Confirm cycle window with the user** before scanning — wrong cycle = wasted scan, and Linear cycle naming can drift.
- **Show the full draft in chat** before writing anywhere. The user reviews and approves before any artifact lands.
- **Linear document is the primary output.** Write there first. If Linear is unavailable, fall back to the vault — do not hard-depend on either.
- **Personal vault copy is optional.** Write it only when the user requests it or when Linear is unavailable.
- **Prefer librarian for the vault write when present.** Do not call `mcp__obsidian-mcp__*` create/update tools directly when a vault-convention-aware writer exists; dispatch it with the drafted content instead.
- **One retro per cycle.** If a retro document/note already exists for the target cycle, ask before overwriting.
- **Omit empty sections.** Canceled / Added mid-cycle / Decisions / Patterns / Notable moments / Open questions are omitted entirely when empty — don't write placeholder headers.

## Composes with

- **`linear`** (linear plugin) — retro reads Linear state (tickets, cycles) and writes the retro output to a Linear document via `mcp__linear-server__save_document`.
- **`note-editor`** (external librarian setup) — performs the optional vault write when present. Honors frontmatter/folder conventions; creates the `Retros/` folder on first invocation.
- **`vault-reader`** (external librarian setup) — optional alternative to inline `mcp__obsidian-mcp__*` reads for the session-note + prior-retro pass. Useful when the read scope is large.
- **`ndr:decisions`** (external ndr plugin) — optional: dispatch when the retro narrative needs the current state of a referenced decision (e.g. confirming a cancellation reason).

## See also

- **`groom`** skill in this plugin — forward-looking counterpart on the same weekly cadence.
- **`references/issue-shape.md`** — required-field spec; useful for characterizing why a ticket was carried (missing `Done when:` vs. blocked).
- **`references/layer-policy.md`** — active-layers spec; useful for surfacing layer-policy adherence in retro narrative.
