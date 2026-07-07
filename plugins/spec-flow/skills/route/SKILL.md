---
name: route
description: This skill should be used when the user hands spec-flow a ticket without saying which phase it's in and wants spec-flow to figure out where the change stands and continue. Trigger phrases include "/spec-flow route TEAM-123", "/spec-flow TEAM-123" (bare ticket), "where is TEAM-123", "what phase is TEAM-123 in", "continue TEAM-123", "pick up where TEAM-123 left off", "what's next on this ticket". Reads the contract's current state, maps it to the lifecycle phase (draft / implement / close / done), and hands off to the matching skill. Does NOT itself draft, implement, or close — it only detects the phase and dispatches.
argument-hint: "<TEAM-N or contract slug>"
allowed-tools:
  - mcp__linear-server__get_issue
  - mcp__linear-server__list_issue_statuses
  - Read
  - Glob
---

# spec-flow:route

Given a ticket (or file slug) and nothing else, figure out where the change sits in the lifecycle and hand off to the right skill. The phase→skill mapping is the inverse of the state transitions spec-flow drives (`../../references/hosts.md`): `draft` → Contract Review, `implement` → In Progress, `close` → a review state.

## When to invoke

- User passes a bare ticket to the dispatcher: `/spec-flow TEAM-123`.
- User runs `/spec-flow route <id>` explicitly.
- User asks "where is TEAM-123 / what phase is it in / just continue this ticket".

## Do NOT invoke for

- A known phase — if the user said "implement TEAM-123" or "close TEAM-123", call that skill directly. Route is for *unknown* phase.
- Opening a brand-new change with no ticket yet — that's `spec-flow:draft` (or `capture`).

## Workflow

### 1. Detect host

- Identifier matches `^[A-Z]{2,5}-\d+$` (e.g. `TEAM-123`) → **linear** host. State lives in Linear — this is the primary path.
- Anything else (kebab slug, filename) → **file** host. Phase comes from `.docs/` placement + frontmatter (see step 4).

If host = linear, check that `mcp__linear-server__*` tools are loaded. If not, use the standard fallback wording (`../../references/hosts.md` — *"Linear MCP server isn't connected …"*). Do not run `claude mcp add`.

### 2. Read state (linear host)

- Fetch the ticket via `mcp__linear-server__get_issue`.
- Determine two signals:
  - **`has_contract`** — does the description carry the six-section shape? Cheap test: a `## What we're doing` heading is present.
  - **state type + name** — read the ticket's workflow state (`get_issue` exposes it; `get_issue_status` for the type). Types are `triage | backlog | unstarted | started | completed | canceled`.

### 3. Map to a phase and hand off (linear host)

Evaluate top to bottom — first match wins:

| Condition | Phase | Action |
|---|---|---|
| state type `completed` or `canceled` | **done** | Report terminal; nothing to route. Don't reopen. |
| state name matches a review state (In Review / Code Review / Ready for Review / Review) | **closed** | `close` already advanced it. Report done; offer to re-run `Skill(spec-flow:close)` only if the user wants to re-migrate findings. |
| state type `started` (e.g. In Progress) | **implement** | Resume — invoke `Skill(spec-flow:implement)` with the ticket ID. If `has_contract` is false, flag the anomaly (started but no contract body) and offer `draft` instead. |
| state name "Contract Review", or any `unstarted` state with `has_contract` true | **implement** | Ready to start — invoke `Skill(spec-flow:implement)`. |
| otherwise (Backlog / Triage / unstarted, `has_contract` false) | **draft** | It's a capture stub or raw ticket — invoke `Skill(spec-flow:draft)` with the ticket ID so `draft` upgrades it. |

**Announce before handing off** — one line so the user sees the detection: *"TEAM-123 is In Progress with a contract — resuming implement."* / *"TEAM-123 is in Backlog with no contract body yet — drafting one."* Then invoke the mapped skill; do not do its work here.

### 4. File host (fallback)

File contracts have no queryable Linear state — derive the phase from placement + frontmatter:

| Where / status | Phase | Action |
|---|---|---|
| `status: captured` stub in `.docs/` | **draft** | Invoke `Skill(spec-flow:draft)` to upgrade the stub. |
| active contract in `.docs/` (not `archive/`, not captured) | **implement** | Invoke `Skill(spec-flow:implement)` with the slug. |
| in `.docs/archive/` or `status: archived` | **done** | Report already closed; nothing to route. |

Announce the detected phase the same way before handing off.

## Notes

- Route never drafts, implements, or closes — it detects and dispatches. The downstream skill re-reads the contract; route's only job is picking the right one.
- Phase is derived live each invocation from state, never persisted — same model as host and cadence.
- A bare review-state ticket is the one ambiguous case (closed vs. wants-re-close); route reports done and lets the user opt into a `close` re-run rather than guessing.
