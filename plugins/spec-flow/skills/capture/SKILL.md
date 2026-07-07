---
name: capture
description: This skill should be used when the user wants to capture a future change idea with zero ceremony — mid-session ("ticket this and keep going", "capture this before I forget"), during planning or mulling conversations ("that should be a ticket"), or explicitly via `/spec-flow capture <thought>`. Stage zero of the spec-flow lifecycle: takes a one-liner or rough paragraph and files a minimal, well-shaped artifact (Linear Backlog ticket by default; `.docs/` capture stub when Linear isn't connected) without asking questions or doing research. Does NOT draft a contract — that is `spec-flow:draft`, typically the second touch on the captured artifact. Also handles "triage my captures" — shaping raw Backlog tickets that were captured outside any session.
argument-hint: "<thought>"
allowed-tools:
  - mcp__linear-server__list_issues
  - mcp__linear-server__save_issue
  - Read
  - Glob
  - Write
---

# spec-flow:capture

Capture a future change idea as a minimal artifact, then get out of the way. The lifecycle is: **captured → drafted → implementing → closed** — this skill owns the first stage only.

The defining constraint is **zero ceremony**: no questions, no research, no context-gathering. Capture exists to not break flow; everything expensive happens at `draft`, the second touch.

## When to invoke

- User runs `/spec-flow capture <thought>`.
- Mid-session: "ticket this", "capture this before I forget", "don't lose this thought", "that's a ticket — keep going".
- During mulling/planning conversations when the user marks an idea as a future change.
- "Triage my captures" — shape raw tickets captured outside any session (see Triage mode).

## Do NOT invoke for

- Drafting a contract — that is `spec-flow:draft`.
- Work the user wants to start now — capture is for *future* changes.
- General Linear ticket operations (transitions, queries, field edits) — that is the linear plugin's `linear` skill.

## Workflow

### 1. Take the thought as-is

Use the argument text, or — when triggered mid-conversation — the idea as the user just stated it plus whatever context is already in the conversation. **Do not** run searches, read files, or fetch docs. **Do not** ask questions. (Single exception: if the thought is too vague to title at all, ask exactly one.)

### 2. Detect host

- Linear MCP tools (`mcp__linear-server__*`) loaded → **linear** host (default).
- Not loaded, or user said "as a file" → **file** host.

No prompt about MCP wiring at capture time — fall back silently to the file host and say so in the confirmation line. Capture must not stall on infrastructure.

### 3. Shape the minimal artifact

**Linear host** — create one Backlog ticket, deferring every convention to the linear plugin's `linear` skill (team, title shape, label set, priority, project lookup, MCP gotchas):

- **Title:** noun-phrase per linear conventions, derived from the thought. Don't confirm — capture trusts the derivation; the user can rename later.
- **State:** `Backlog`, priority None — per linear conventions for unapproved ideas.
- **Labels:** one surface + one type, best inference from the thought and conversation context. Never ask.
- **Description:** lightweight template, thin is fine:

```markdown
## Goal

<the thought, lightly cleaned up — one short paragraph max>

## Context

- <only breadcrumbs already in the conversation: repo, file paths, ticket refs, the triggering observation>

## Done when

- <only if an observable outcome is evident from the thought — otherwise omit the section entirely>
```

A captured ticket is **not** a contract. Do not write the six-section template; do not set Contract Review.

**File host** — write a capture stub the same way `draft` will later upgrade in place:

```markdown
---
status: captured
topic: <slug>
captured: YYYY-MM-DD
---

# <thought as a one-line title>

## Goal

<the thought>

## Context

- <breadcrumbs already in conversation>
```

Filename: `.docs/YYYY-MM-DD-<slug>.md` (same convention as contracts; the `status: captured` frontmatter is the differentiator).

### 4. Confirm in one line and return to flow

> "Captured as TEAM-456 (Backlog). Back to <what we were doing>."

or

> "Linear isn't connected — captured to `.docs/2026-06-11-<slug>.md`. Back to <what we were doing>."

Nothing else. No summary, no next-step menu. If capture happened mid-task, resume the task immediately.

## Triage mode

For raw captures that arrived outside any session (Linear mobile app, quick adds): when the user says "triage my captures" or similar —

1. List Backlog tickets via `mcp__linear-server__list_issues` (team per linear conventions) and surface the **raw** ones: empty or one-line descriptions, missing labels.
2. For each, propose the shaped version (title per conventions, lightweight template, labels) in one compact block. Batch the proposals; apply after a single user sign-off.
3. Do not promote state or set priority — shaping only. Promotion is `groom`'s lane (pm plugin) or the user's call.

## Handoff

The captured artifact's second touch is `spec-flow:draft`:

- Linear: `/spec-flow draft "the contract is TEAM-456"` — draft reads the captured Goal/Context as input and overwrites with the six-section contract.
- File: `/spec-flow draft <slug>` — draft upgrades the stub in place (`status: captured` → `active`, six sections).

Many captures never get drafted — quick tasks get done directly, dead ideas get canceled. That's fine; capture doesn't obligate a contract.

## Notes

- Ticket mechanics (team, labels, title shape, status semantics, MCP gotchas) are owned by the linear plugin — this skill defers, never restates. If the linear plugin's conventions and this file disagree, the linear plugin wins.
- Capture quality bar: good enough to re-find and re-understand in two weeks. Not good enough to implement from — that's what draft is for.
