---
name: linear
description: This skill should be used when creating, updating, transitioning, reading, or querying Linear tickets in your Linear workspace. Trigger phrases include "open a linear ticket", "create a TEAM ticket", "add to linear", "add to backlog", "log this in linear", "move TEAM-N to", "transition TEAM-N", "promote to todo", "back to backlog", "mark TEAM-N done", "what state is TEAM-N", "set TEAM-N priority", "what's in todo", "show my linear tickets", "show unassigned tickets", "show team backlog", "assign to me", "assign to the other person", "accept this ticket", "who should own this". Supplies ticket creation defaults (team, labels, priority, assignee, milestone), status flow semantics, title and description conventions, collaboration conventions, and MCP call patterns. Does NOT cover the spec-flow contract lifecycle (use spec-flow plugin) or the decision of whether to open a ticket at all (project CLAUDE.md owns the floor rule).
---

# linear

Operational conventions for Linear work. Loads on any ticket create, transition, read, or update.

## Scope

- **Owns:** Ticket creation defaults, label set, status flow, title shape, description templates, status transitions, priority semantics.
- **Does NOT own:**
  - The decision of *whether* to open a ticket — that's the project CLAUDE.md floor rule.
  - The spec-flow contract lifecycle — that's the spec-flow plugin. When a contract is hosted in Linear, spec-flow writes the contract body; this skill governs the ticket's other fields.
- **Currently scoped to:** one Linear team, two collaborators. Each person runs their own Claude with their own Linear auth, so `assignee="me"` resolves per-person automatically.

## Conventions

### Team and project

- **Team:** Always `TEAM`. One team only.
- **Project:** Look up the active project via `mcp__linear-server__list_projects` and pick the non-completed active project. Projects are phase-scoped (one per 60-day phase) and rotate — don't hardcode the current name.

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
| Type | `Feature`, `Improvement`, `Docs`, `Chore`, `Decision`, `Spike` | Capitalized |

Rules:
- Surface labels live under a **`surface` label group** in Linear (group name `surface`, children `pipeline` / `backend` / `frontend` / `infra` / `database`). The MCP `save_issue` tool does NOT resolve colon-prefixed strings like `"surface:backend"` — pass the **bare child name** (`"backend"`). If you pass the colon form, `save_issue` returns silently with `labels: []`. Stable label IDs from `list_issue_labels` also work; bare child names are more readable. See `../../references/mcp-gotchas.md` § 2 for full details.
- `Bug` is unused — do not add tickets with it. If a defect comes up, it's a `Feature` regression or a `Chore` cleanup depending on framing.
- `Decision` is for tickets that mark a decision point (formerly written as `D# — ...` titles). The decision content itself becomes an ndr atom; the ticket tracks the work of making the call.
- `Spike` is for timeboxed empirical investigations — see "Spike vs Decision" below.

### Spike vs Decision

Both labels mark "we don't know something yet" work. The boundary test is **empirical vs judgment**: *could I answer this from my chair, or do I have to go do something first?*

- **`Spike`** — unknown resolved *empirically*. Timeboxed, throwaway code, a **finding** as output (vault note; ndr atom only if the finding itself resolves a decision).
- **`Decision`** — fork resolved by *judgment*. Tradeoffs weighed from the chair; an **ndr atom** as output.

**Embed by default; ticket only orphans.** A decision whose lifecycle fits one work item lives in that item's `Open questions` (spec-flow contract) and gets lazily resolved at point of contact by the implementing agent. A standalone ticket is earned only when the unknown is *orphaned*:

- no future work will naturally collide with it (silent-default risk), or
- its input needs lead time (stakeholder availability, external data).

TEAM-123 and TEAM-124 are the existing examples of tickets that clear the orphan bar.

The 2×2:

| | Judgment | Empirical |
|---|---|---|
| **Hosted** (fits one work item) | `Open questions` in the contract | probe mid-implementation (`craft:prototype`) |
| **Homeless** (orphaned) | `Decision` ticket | `Spike` ticket |

Labels are not static:

- A `Decision` may convert to `Spike` on pickup, when making the call turns out to need evidence first (TEAM-124 is the live example of this pressure).
- A `Spike`'s finding often feeds a `Decision` — wire a blocks relation (Spike blocks Decision).

### Status flow

| State | Meaning | Trigger to enter |
|---|---|---|
| **Backlog** | Added but not yet approved / not yet in-scope | Created without pre-approval; an idea or stakeholder ask awaiting sign-off |
| **Todo** | Approved or clearly in-scope; ready to be picked up | Created directly when work is obviously in scope, OR promoted from Backlog after approval |
| **In Progress** | Actively working on it right now | Manual when work starts. Typically 1–2 tickets at a time. |
| **In Review** | Work done; needs a final review pass (optional gate) — self or cross-review | Manual when work feels done but a second look is wanted before calling it shipped |
| **Done** | Reviewed, complete, shipped | Manual after self-review passes (or directly from In Progress when no review wanted) |
| **Canceled** | Won't do | Manual |

Semantics:
- **All transitions are manual judgment.** No git-event-triggered automation (no PRs yet — direct-to-main workflow).
- **Backlog → Todo is an authorization step.** Approval comes from the stakeholder OR self-confirmation that the work fits an existing milestone / phase scope.
- **Unassigned = shared team queue.** An unassigned ticket sits in a pool that either person can pull from. It should NOT move to Todo or In Progress until someone explicitly accepts it (reads it, confirms scope, self-assigns). This prevents silent plate-landing.
- **In Review is flexible.** Self-review (step back, re-read) OR route to the other person for a cross-review pass. When routing to the other person, @-mention them in a comment at the point of transition.
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

**Spike template (for `Spike`-labeled tickets):**

```markdown
## Question

<the unknown, stated as a question>

Timebox: <e.g. 2h, half a day>

## Done when

- Question answered; finding written up (vault note; ndr atom only if it resolves a decision)
```

`## Question` replaces `## Goal` — a spike exists to answer something, not to ship something. State the timebox in the description. "Done when" is always the finding, never "code merged" — spike code is throwaway by definition.

**Full spec-flow contract template (when the ticket *is* the contract):**

The six-section template from `spec-flow:draft` (`What we're doing` / `Why` / `Approach` / `Out of scope` / `Done when` / `Open questions`). Used when the ticket is being created or written by `spec-flow:draft` against a Linear host. spec-flow handles writing this — this skill governs the surrounding fields (labels, priority, state, milestone).

## MCP gotchas

The Linear MCP tool surface has several silent-failure modes — empty responses, dropped fields, no errors. **Read `../../references/mcp-gotchas.md` before calling any `mcp__linear-server__*` tool, especially when filtering by cycle, setting grouped labels, or working with estimates.** Universal to all Linear MCP callers, not just this skill.

## Operations

### Create a ticket

```python
mcp__linear-server__save_issue(
    team="TEAM",
    project="<active project>",               # look up via list_projects; phase-scoped, rotates
    title="Area: noun-phrase",
    state="Backlog",                          # or "Todo" if pre-approved/in-scope
    labels=["<surface>", "<Type>"],           # exactly one of each (e.g. ["backend", "Feature"])
    priority=0,                               # 0=None default; 2=High when promoted to Todo
    assignee="me",                            # DEFAULT: self-assign. Override explicitly if needed (see below)
    description="## Goal\n\n<para>\n\n## Done when\n\n- <outcome>\n- <outcome>",
    # milestone: only if obvious — look up via list_milestones; omit otherwise
)
```

Notes:
- Pass real newlines in `description`, not literal `\n` escapes.
- Omit `milestone` unless the ticket obviously fits one.
- `state` accepts state names (not IDs) when team is specified.
- **Assignee is a conscious choice.** Default is self (`"me"`). Overrides:
  - *Shared team queue* — omit `assignee` entirely when the work is unowned and either person could pick it up.
  - *Route to the other person* — pass their Linear username when asked; @-mention them in a comment after creation so they see it.

### Transition state

```python
mcp__linear-server__save_issue(id="TEAM-N", state="In Progress")
```

State names per the table above. If unsure of the current state, read first:

```python
mcp__linear-server__get_issue(id="TEAM-N")
```

### Promote Backlog → Todo

Two-step ritual reflecting the authorization semantics:

1. Confirm with the user that the ticket has been approved (stakeholder sign-off OR clear scope justification). Don't promote silently.
2. Transition + set priority:

```python
mcp__linear-server__save_issue(id="TEAM-N", state="Todo", priority=2)
```

### Read a ticket

```python
mcp__linear-server__get_issue(id="TEAM-N")
```

Use to inspect state, description, labels, milestone before taking action.

### List tickets in a state

```python
# My tickets (default)
mcp__linear-server__list_issues(team="TEAM", state="Todo", assignee="me", limit=50)

# Unassigned / shared team queue — "show unassigned", "show team backlog"
mcp__linear-server__list_issues(team="TEAM", state="Backlog", assignee=None, limit=50)

# All team tickets regardless of assignee — "what's in todo for the team"
mcp__linear-server__list_issues(team="TEAM", state="Todo", limit=50)
```

Useful for "what's in todo", "show my backlog", "show unassigned tickets", "show team backlog", weekly review.

### Accept an unassigned ticket

When picking up a ticket from the shared team queue:

1. Read the ticket (`get_issue`) — confirm scope and done criteria make sense.
2. Confirm with the user this is the ticket to take.
3. Self-assign and move to Todo (or In Progress if starting immediately):

```python
mcp__linear-server__save_issue(id="TEAM-N", assignee="me", state="Todo")
```

4. Optionally leave a comment to signal acceptance (useful when the other person might also be considering it).

### Collaboration conventions

- **Reassigning to the other person:** @-mention them in a comment immediately after `save_issue` so they see the handoff. Don't just flip `assignee` silently.
- **Routing to the other person for cross-review:** when transitioning to `In Review` with the intent of cross-review (not self-review), @-mention the reviewer in a comment at that moment. The ticket state alone doesn't communicate who the reviewer is.
- **Unassigned tickets:** treat them as up for grabs. Neither person is implicitly responsible until one of them runs the accept ritual above.

## Composition

- **spec-flow** — When a contract is hosted in Linear (e.g. `/spec-flow draft TEAM-123`), spec-flow writes the contract body to the ticket description using the full six-section template. This skill governs the surrounding ticket fields. spec-flow does not set labels, priority, or milestone — those follow the conventions here. `spec-flow:capture` and Linear-new `spec-flow:draft` also *create* tickets — title shape, team, labels, priority, and state defaults all come from this skill.
- **ndr** — Tickets carrying the `Decision` label correspond to ndr atoms. The ticket tracks the work of making the decision; the atom holds the captured decision content. Reference atoms from ticket descriptions via `ndr:<atom-id>` or `ndr:<area>/<topic>`.
- **Project CLAUDE.md** — Owns the floor rule: "can't do now, or has dependencies to sequence" → open a ticket. This skill takes over once the decision to open has been made.

## Not covered (deferred)

| Item | Stance | Revisit when |
|---|---|---|
| PR-to-ticket linking (branch naming, auto-close, commit references) | Default-off by prior decision | PRs are introduced (team grows beyond solo) |
| Close-time state on PR push | Manual judgment; no convention | Same as above |
| Cycle assignment rules | Linear defaults; no custom logic | When weekly review starts feeling under-served by defaults |
| Stakeholder views (`stakeholder:*` labels, per-stakeholder views) | Declined by prior decision | Only if/when a stakeholder gets direct Linear access |
