---
name: groom
description: >-
  Weekly Thursday-AM backlog grooming sweep for CartaOS Linear (team CAR). This
  skill should be used when the user invokes `/pm:groom`, says "groom the
  backlog", "weekly groom", "thursday grooming", "let's groom", or signals the
  start of the weekly Thu→Wed cycle grooming ritual. Scans active cycle +
  backlog, cross-refs NDR atoms and recent vault session notes, and outputs a
  punch list grouped by action bucket (pull-in, push-out, stale, missing-fields,
  NDR-moot, vault-unfiled). Writes the same punch list to this cycle's
  recurring grooming child issue as the cycle log. Proposes actions only —
  never applies state transitions, never closes tickets, never edits the bodies
  of groomed tickets. The user reviews and applies any changes manually via the
  `linear-workflow` skill.
argument-hint: "[grooming log issue ID, e.g. CAR-128]"
allowed-tools:
  # Linear — cycle + backlog scan + write the cycle log
  - mcp__linear-server__list_issues
  - mcp__linear-server__list_cycles
  - mcp__linear-server__get_issue
  - mcp__linear-server__list_comments
  - mcp__linear-server__list_issue_statuses
  - mcp__linear-server__list_issue_labels
  - mcp__linear-server__save_issue
  # Obsidian — vault session-note scan
  - mcp__obsidian-mcp__search_notes
  - mcp__obsidian-mcp__read_multiple_notes
  # NDR atom files
  - Read
  - Grep
  - Bash
  # Compose with ndr:decisions and other skills
  - Skill
---

# groom

## Overview

Run the weekly Thursday-AM grooming sweep for CartaOS Linear (team `CAR`). Read-mostly: scan the active cycle and backlog, cross-reference NDR atoms and recent vault session notes, produce a punch list grouped by action bucket. Write the punch list to this cycle's recurring grooming child issue as the cycle log. The user reviews and applies any approved transitions manually via the `linear-workflow` skill.

The bet: classification is mechanical (rule-based) and tedious, so the skill does it. Prioritization is judgment, so the user does it.

## Inputs (load-bearing constants)

- **Linear team:** `CAR` (Carta Healthcare). Single-team workspace.
- **Grooming log anchor:** `CAR-63` is the recurring-issue template. Each cycle spawns a child issue (e.g. `CAR-128`); the punch list is written to that child as the cycle log. This skill does NOT read `CAR-63`'s body — the grooming procedure is encoded in this skill, not in Linear.
- **Vault project root:** `~/Loose Ends/Carta/Projects/CartaOS/`
- **NDR atoms root:** `~/Loose Ends/Decisions/` — filter to atoms with `project: [[CartaOS]]` frontmatter.
- **Cycle cadence:** Thu→Wed, weekly. Cycle boundary aligns with the Thursday 11 AM ops review meeting — cycle closes Wed EOD; Thursday morning meeting reviews the just-closed cycle; new cycle starts Thursday.
- **Issue shape spec:** `../../references/issue-shape.md` (plugin reference). Defines what counts as a well-formed CartaOS ticket. Load when classifying for the Missing-fields or NDR-moot buckets.
- **Layer policy:** `../../references/layer-policy.md` (plugin reference). Defines the active layers (project / milestone / issue / cycle), the retired ones (epic, subissue, initiative), and the legal states for a ticket. Load when flagging orphans (no milestone, in cycle) or evaluating whether a proposed parent ticket earns its keep.

## Procedure

1. **Locate the log issue.** If an argument was passed (e.g. `CAR-128`), use that. Otherwise, query `mcp__linear-server__list_issues` for the most recently updated open issue in team `CAR` matching the grooming-recurrence pattern (title contains "groom" OR label `grooming`). Confirm with the user before writing — one-line prompt, e.g. "Write log to CAR-128?".
2. Pull active cycle issues via `mcp__linear-server__list_cycles` + `list_issues` filtered by the current cycle. **Resolve the current cycle's numeric name (e.g. `"2"`) via `list_cycles({type: "current"})` first, then pass that to `list_issues({cycle: "2"})` — `cycle: "current"` silently returns `[]`.** See `~/cc-marketplace/plugins/linear/references/mcp-gotchas.md` § 1 for the failure mode and other Linear MCP gotchas. Capture state, priority, `updatedAt`, blocker links.
3. Pull backlog issues filtered to the active CartaOS project. Sort by `updatedAt` descending.
4. Classify each ticket into exactly ONE bucket per the taxonomy below. Precedence when multiple criteria match: **NDR-moot > Missing fields > Stale > Push-out > Pull-in**.
5. For tickets whose body or title references `ndr:<atom-id>`, `ndr:#<slug>`, or `ndr:<area/topic>`, dispatch `Skill(ndr:decisions)` to resolve the supersession head. Flag any whose referenced atom has been superseded as `NDR-moot`.
6. Search vault `~/Loose Ends/Carta/Projects/CartaOS/` for working-session notes touched in the last 7 days. Surface any work items mentioned in those notes but not represented by a Linear ticket as `Vault-unfiled` candidates.
7. **Smell check — Decision proliferation.** Count open `Decision`-labeled tickets across cycle + backlog. If ≥3, append a smell line to the punch list: decisions are not being resolved inside spec-flow contracts (embed-by-default — a standalone ticket is earned only by the orphan bar; see `linear-workflow`'s "Spike vs Decision" section). For each, propose checking it against the orphan bar — non-orphans should fold into the `Open questions` of the work item that will collide with them.
8. Format the punch list per the output format below. Emit to chat.
9. **Write the cycle log.** Replace the log issue's body with the formatted punch list (cycle header + buckets). Skip this step if step 1 found no candidate — warn the user instead.

## Buckets (load-bearing taxonomy)

A ticket lands in exactly one bucket per session. Precedence when multiple match: **NDR-moot > Missing fields > Stale > Push-out > Pull-in**.

| Bucket | Criteria |
|---|---|
| **Pull-in** | Not in active cycle, no blockers, has done-when in description, priority ∈ {urgent, high} |
| **Push-out** | In active cycle, blocked OR needs spec OR missing done-when |
| **Stale** | Backlog, no updates in >14 days, priority ∈ {low, none} |
| **Missing fields** | Per `references/issue-shape.md` #1–6: any required field absent (no priority, no project, no surface label, no type label, or — for status ≥ Todo — no `## Done when:` section in description) |
| **NDR-moot** | References a superseded NDR atom (confirmed via `Skill(ndr:decisions)`) |
| **Vault-unfiled** | Work named in vault session notes (last 7 days) with no corresponding ticket |

## Output format

Emit one markdown section per bucket. Skip empty buckets. Each row:

```
- **CAR-N** — <title>
  - Proposed: <action>
  - Why: <one-line rationale>
```

For `Vault-unfiled`, substitute the note name for `CAR-N`:

```
- **<vault-note-name>** — <work item phrase>
  - Proposed: open ticket via `linear-workflow` with done-when criterion
  - Why: <one-line rationale>
```

End with a one-line load summary:

```
Current cycle: N tickets total, M in progress.
```

If the Decision-proliferation smell triggered (step 7), append one line:

```
Smell: N open Decision tickets — decisions may not be resolving inside contracts. Check each against the orphan bar; fold non-orphans into the colliding work item's Open questions.
```

## Cycle log body (written to Linear in step 9)

The log body written to the recurring grooming child issue mirrors the chat output, prefixed with a cycle header:

```markdown
# Grooming — cycle YYYY-MM-DD → YYYY-MM-DD

Reviewed N tickets (C in cycle, B in backlog). Current load: N tickets, M in progress.

## Pull-in candidates

- ...

## Push-out candidates

- ...

(empty buckets omitted)
```

Replace-on-write each run. Rerunning the same week overwrites with the latest sweep.

## Rules

- **Never apply state transitions, never close tickets.**
- **Never edit groomed ticket bodies.** The grooming log issue (located in step 1) is the one exception — its body IS this skill's output destination.
- **Skip urgent-priority tickets** — those are handled live, not in weekly grooming.
- **Skip sub-projects of CAR not assigned to the user.**
- **Always flag the current cycle load** before proposing pull-ins.
- **Do not re-classify a ticket the user moved during the session** — assume the move was deliberate.
- **Confirm the log issue ID with the user** before writing in step 9.

## Composes with

- **`linear-workflow`** (linear plugin) — the user applies any approved transitions via this skill after reviewing the punch list. Do not call it from within `groom`.
- **`ndr:decisions`** (ndr plugin) — supersession-aware lookup. Dispatch when a ticket body or title contains an `ndr:` reference, to decide if the ticket belongs in the NDR-moot bucket.
- **`librarian:vault-reader`** (librarian plugin agent) — optional in v1 for the vault-unfiled pass. Inline `mcp__obsidian-mcp__search_notes` is sufficient at this version.
