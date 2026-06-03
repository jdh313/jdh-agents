---
name: implement
description: This skill should be used when the user runs `/spec-flow implement [name]` or otherwise signals a transition from a drafted contract to actual coding work. Trigger phrases include "spec-flow implement", "let's start coding on the X contract", "pick up the X contract", "resume the X change", "continue the okta-auth work". Accepts either a file slug or a Linear ticket ID (e.g. `TEAM-49`). Covers both first-run implementation (negotiate handoff cadence, begin work) and resumption (restore context from contract, summarize where work last left off, continue). Same flow either way — read state, summarize, confirm cadence, execute. May invoke `spec-flow:amend` mid-implementation when reality diverges from the contract.
---

# spec-flow:implement

Start or resume implementation against an active contract. Works for both file-hosted (`.docs/`) and Linear-hosted contracts; the only difference is where the body is read from. See `references/hosts.md`.

## When to invoke

- User runs `/spec-flow implement [name]`.
- User signals readiness to code on an existing contract: "let's start", "pick up the okta-auth contract", etc.
- Resumption of work on a contract from a prior session.

## Do NOT invoke for

- Drafting a new contract — that is `spec-flow:start`.
- Closing a finished change — that is `spec-flow:close`.
- Code work that has no associated contract (trivial changes are out of scope by design).

## Workflow

### 1. Identify the target contract and detect host

If a name was given as argument:

- Argument matches `^[A-Z]{2,5}-\d+$` (e.g. `TEAM-49`) → **linear** host. Use the ticket ID.
- Otherwise → **file** host. Treat the argument as a slug or filename.

If no name was given, scan `.docs/` for active file-host contracts (excluding `archive/`):

- **Single active file contract** — Use it.
- **Multiple active** — Match the user's recent prompt against contract topics. If unambiguous, use the match. If ambiguous, list active contracts and ask which.
- **None active** — Tell the user there is nothing to implement and suggest `/spec-flow start`. (Linear-host contracts are not enumerable cheaply; the user is expected to name the ticket explicitly when resuming Linear work.)

If host = linear, check that `mcp__linear-server__*` tools are loaded. If not:

> "Linear MCP server isn't connected — I can't read TEAM-49. Fall back to a `.docs/` file contract, or pause while you wire up the MCP yourself?"

Do not run `claude mcp add` or suggest a paste-and-go connect command.

### 2. Read the contract

- **File host** — `Read` the contract file.
- **Linear host** — Fetch via `mcp__linear-server__get_issue` and parse the description for the 5 sections.

Follow any linked ndr atoms (`[[ndr-...]]` references) and read them.

### 3. Assess state

Check whether implementation has already begun:

- Recent git commits referencing the contract's topic or slug.
- Uncommitted changes in working tree.
- Files modified since the contract was created.

Summarize back to the user in 2–3 lines:

- **First run:** "Contract is `<slug>`. Goal: X. Approach: Y. No implementation work yet."
- **Resumption:** "Contract is `<slug>`. Last session: A, B per git. Open questions remaining: ..."

### 4. Negotiate cadence

Ask the user briefly:

> "Implement all at once, or check in after a piece?"

If a sensible breakpoint exists, propose it:

> "I'd suggest checking in after the auth middleware is wired up, before touching the route layer. Sound good?"

Wait for the user's choice. Do not persist this — cadence is per-session.

### 5. Execute

**Linear host — move to In Progress.** Before writing any code, transition the ticket to the started state:

- Fetch the team's workflow states via `mcp__linear-server__list_issue_statuses` (the team comes from the issue read in step 2).
- Find the state named "In Progress" (case-insensitive match); if absent, fall back to the team's first `started`-type state.
- Set it via `mcp__linear-server__save_issue` (state field).
- If no started-type state exists, note it once and continue. Never block coding on a status change.

(File host has no status — skip this.)

Work according to the chosen cadence:

- **All at once** — Implement the full change; surface the diff at the end.
- **Check in after a piece** — Implement up to the agreed breakpoint; surface progress; await sanity-check; continue.

### 6. Amend when reality diverges

If implementation reveals the contract is becoming inaccurate (wrong approach, new constraint, scope shift, resolved open question), invoke `Skill(spec-flow:amend)` to propose an edit. Do NOT silently work outside the contract; do NOT silently edit it.

### 7. End

When the user signals completion (or the agreed scope has shipped), prompt:

> "Looks done from my end. Run `/spec-flow close` when ready to migrate findings to the durable layer."

Do NOT auto-close. Closing is an explicit user action.

## Notes

- "First run" and "resumption" share the same flow; behavior differs based on observed state, not on a persisted flag.
- Host is not persisted. Each invocation re-detects from the identifier shape.
- Confidence is not persisted. Each invocation re-negotiates cadence.
- Implementation must respect the contract's *Out of scope* — if a tempting addition surfaces, propose an amendment via `spec-flow:amend`. Do not just add it.
