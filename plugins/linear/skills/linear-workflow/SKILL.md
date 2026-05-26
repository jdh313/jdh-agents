---
name: linear-workflow
description: This skill should be used when creating, updating, transitioning, reading, or querying Linear tickets in the CartaOS workspace. Trigger phrases include "open a linear ticket", "create a CAR ticket", "add to linear", "add to backlog", "log this in linear", "move CAR-N to", "transition CAR-N", "promote to todo", "back to backlog", "mark CAR-N done", "what state is CAR-N", "set CAR-N priority", "what's in todo", "show my linear tickets". Supplies ticket creation defaults (team, labels, priority, milestone), status flow semantics, title and description conventions, and MCP call patterns. Does NOT cover the spec-flow contract lifecycle (use spec-flow plugin) or the decision of whether to open a ticket at all (project CLAUDE.md owns the floor rule).
---

# linear-workflow

Operational conventions for CartaOS Linear work. Loads on any ticket create, transition, read, or update.

## Scope

- **Owns:** Ticket creation defaults, label set, status flow, title shape, description templates, status transitions, priority semantics.
- **Does NOT own:**
  - The decision of *whether* to open a ticket — that's the project CLAUDE.md floor rule.
  - The spec-flow contract lifecycle — that's the spec-flow plugin. When a contract is hosted in Linear, spec-flow writes the contract body; this skill governs the ticket's other fields.
- **Currently scoped to:** the `CAR` (Carta Healthcare) team. Linear is CartaOS-only — scope decision lives in `~/Loose Ends/Reference/Tools/Software Catalog/Linear.md`.

## Conventions

### Team and project

- **Team:** Always `CAR` (Carta Healthcare). One team only.
- **Project:** Look up the active project via `mcp__linear-server__list_projects` and pick the non-completed CartaOS project. Projects are phase-scoped (one per 60-day phase) and rotate — don't hardcode the current name.

### Title

`Area: noun-phrase` or bare noun-phrase. Free-text area prefix. Median ~47 characters.

Good:
- `Terraform: ALB + listeners + target groups`
- `SQLAlchemy: enum check-constraint emission fix`
- `Customer Documentation: ingest pipeline`
- `Dishka adoption`
- `Authz model`

Avoid:
- `D# — phrase` — use the `Decision` label instead; the label carries the marker.
- `feat:` / `fix:` / `chore:` conventional-commit prefixes — not used in titles.
- Verb-first imperative ("Add X", "Fix Y") — the house style is noun-phrase.

### Labels

Exactly **one surface + one type** per ticket.

| Dimension | Values | Casing |
|---|---|---|
| Surface | `backend`, `frontend`, `infra`, `database`, `pipeline` | bare lowercase |
| Type | `Feature`, `Improvement`, `Docs`, `Chore`, `Decision` | Capitalized |

Rules:
- Surface labels live under a **`surface` label group** in Linear (group name `surface`, children `pipeline` / `backend` / `frontend` / `infra` / `database`). The MCP `save_issue` tool does NOT resolve colon-prefixed strings like `"surface:backend"` — pass the **bare child name** (`"backend"`). If you pass the colon form, `save_issue` returns silently with `labels: []`. Stable label IDs from `list_issue_labels` also work; bare child names are more readable. See `../../references/mcp-gotchas.md` § 2 for full details.
- `Bug` is unused — do not add tickets with it. If a defect comes up, it's a `Feature` regression or a `Chore` cleanup depending on framing.
- `Decision` is for tickets that mark a decision point (formerly written as `D# — ...` titles). The decision content itself becomes an ndr atom; the ticket tracks the work of making the call.

### Status flow

| State | Meaning | Trigger to enter |
|---|---|---|
| **Backlog** | Added but not yet approved / not yet in-scope | Created without pre-approval; an idea or stakeholder ask awaiting sign-off |
| **Todo** | Approved or clearly in-scope; ready to be picked up | Created directly when work is obviously in scope, OR promoted from Backlog after approval |
| **In Progress** | Actively working on it right now | Manual when work starts. Typically 1–2 tickets at a time. |
| **In Review** | Work done; needs my final manual review (optional gate) | Manual when work feels done but I want one more pass before calling it shipped |
| **Done** | Reviewed, complete, shipped | Manual after self-review passes (or directly from In Progress when no review wanted) |
| **Canceled** | Won't do | Manual |

Semantics:
- **All transitions are manual judgment.** No git-event-triggered automation (no PRs yet — direct-to-main solo workflow).
- **Backlog → Todo is an authorization step.** Approval comes from Andrew (stakeholder) OR self-confirmation that the work fits an existing milestone / phase scope.
- **In Review is optional.** Skip it (In Progress → Done) when no second pass is wanted. Use it when stepping back from the work helps.
- **Cycle membership is orthogonal to status.** A Todo ticket may or may not be in the current cycle; cycle assignment is a separate axis (weekly cycles starting Tuesday).

### Priority

| Level | Numeric | Meaning | Default for |
|---|---|---|---|
| Urgent | 1 | Drop everything | Genuine emergency (blocking stakeholder, prod incident) |
| High | 2 | Committed work, on the active plate | Default for **Todo** tickets |
| Medium | 3 | Should do, can wait | Default for **Backlog** tickets when promoted |
| Low | 4 | Nice-to-have / cleanup | Chores, polish, low-stakes improvements |
| None | 0 | Unprioritized | Default at creation; set when status moves to Todo |

Priority and status are independent — set both consciously. Don't auto-bump priority just because status changed; treat the level as a separate signal of stakes.

### Milestone

Assign only when the ticket obviously belongs to one. Lazy by default — add when a real ticket forces the call.

Naming convention: `Mn — phrase` for sequenced phase milestones (e.g. `M3 — Auth perimeter`); `Stretch — phrase` for aspirational scope outside the sequence.

Look up the current milestone set via `mcp__linear-server__list_milestones` against the active project. Milestones are phase-scoped and rotate — don't enumerate them here.

### Description

Two templates depending on what the ticket is for.

**Lightweight template (default for most tickets):**

```markdown
## Goal

<one paragraph: what this ticket is for, why it exists>

## Done when

- <observable outcome>
- <observable outcome>
```

`Goal` + `Done when` is the de facto house template across the existing ticket corpus. The `Done when` heading matches spec-flow's contract template — same vocabulary, lower altitude.

**Full spec-flow contract template (when the ticket *is* the contract):**

The five-section template from `spec-flow:start` (`What we're doing` / `Why` / `Approach` / `Out of scope` / `Done when` / `Open questions`). Used when the ticket is being created or written by `spec-flow:start` against a Linear host. spec-flow handles writing this — this skill governs the surrounding fields (labels, priority, state, milestone).

## MCP gotchas

The Linear MCP tool surface has several silent-failure modes — empty responses, dropped fields, no errors. **Read `../../references/mcp-gotchas.md` before calling any `mcp__linear-server__*` tool, especially when filtering by cycle, setting grouped labels, or working with estimates.** Universal to all Linear MCP callers, not just this skill.

## Operations

### Create a ticket

```python
mcp__linear-server__save_issue(
    team="CAR",
    project="<active CartaOS project>",       # look up via list_projects; phase-scoped, rotates
    title="Area: noun-phrase",
    state="Backlog",                          # or "Todo" if pre-approved/in-scope
    labels=["<surface>", "<Type>"],           # exactly one of each (e.g. ["backend", "Feature"])
    priority=0,                               # 0=None default; 2=High when promoted to Todo
    description="## Goal\n\n<para>\n\n## Done when\n\n- <outcome>\n- <outcome>",
    # milestone: only if obvious — look up via list_milestones; omit otherwise
    # assignee: omit (defaults to me)
)
```

Notes:
- Pass real newlines in `description`, not literal `\n` escapes.
- Omit `milestone` unless the ticket obviously fits one.
- `state` accepts state names (not IDs) when team is specified.

### Transition state

```python
mcp__linear-server__save_issue(id="CAR-N", state="In Progress")
```

State names per the table above. If unsure of the current state, read first:

```python
mcp__linear-server__get_issue(id="CAR-N")
```

### Promote Backlog → Todo

Two-step ritual reflecting the authorization semantics:

1. Confirm with the user that the ticket has been approved (Andrew nod OR clear scope justification). Don't promote silently.
2. Transition + set priority:

```python
mcp__linear-server__save_issue(id="CAR-N", state="Todo", priority=2)
```

### Read a ticket

```python
mcp__linear-server__get_issue(id="CAR-N")
```

Use to inspect state, description, labels, milestone before taking action.

### List tickets in a state

```python
mcp__linear-server__list_issues(team="CAR", state="Todo", assignee="me", limit=50)
```

Useful for "what's in todo", "show my backlog", weekly review.

## Composition

- **spec-flow** — When a contract is hosted in Linear (e.g. `/spec-flow start CAR-49`), spec-flow writes the contract body to the ticket description using the full five-section template. This skill governs the surrounding ticket fields. spec-flow does not set labels, priority, or milestone — those follow the conventions here.
- **ndr** — Tickets carrying the `Decision` label correspond to ndr atoms. The ticket tracks the work of making the decision; the atom holds the captured decision content. Reference atoms from ticket descriptions via `ndr:<atom-id>` or `ndr:<area>/<topic>`.
- **Project CLAUDE.md (CartaOS)** — Owns the floor rule: "can't do now, or has dependencies to sequence" → open a ticket. This skill takes over once the decision to open has been made.

## Not covered (deferred)

| Item | Stance | Revisit when |
|---|---|---|
| PR-to-ticket linking (branch naming, auto-close, commit references) | Default-off per the `Linear.md` catalog decision | PRs are introduced (team grows beyond solo) |
| Close-time state on PR push | Manual judgment; no convention | Same as above |
| Cycle assignment rules | Linear defaults; no custom logic | When weekly review starts feeling under-served by defaults |
| Stakeholder views (`stakeholder:*` labels, Andrew-specific view) | Declined per `Linear Setup — Views.md` | Only if/when stakeholder gets direct Linear access |
