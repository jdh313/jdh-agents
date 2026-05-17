---
name: implement
description: This skill should be used when the user runs `/spec-flow implement [name]` or otherwise signals a transition from a drafted contract to actual coding work. Trigger phrases include "spec-flow implement", "let's start coding on the X contract", "pick up the X contract", "resume the X change", "continue the okta-auth work". Covers both first-run implementation (negotiate handoff cadence, begin work) and resumption (restore context from contract, summarize where work last left off, continue). Same flow either way — read state, summarize, confirm cadence, execute. May invoke `spec-flow:amend` mid-implementation when reality diverges from the contract.
---

# spec-flow:implement

Start or resume implementation against an active contract.

## When to invoke

- User runs `/spec-flow implement [name]`.
- User signals readiness to code on an existing contract: "let's start", "pick up the okta-auth contract", etc.
- Resumption of work on a contract from a prior session.

## Do NOT invoke for

- Drafting a new contract — that is `spec-flow:start`.
- Closing a finished change — that is `spec-flow:close`.
- Code work that has no associated contract (trivial changes are out of scope by design).

## Workflow

### 1. Identify the target contract

If a name was given as argument, use it. Otherwise, scan `.docs/` for active contracts (excluding `archive/`):

- **Single active contract** — Use it.
- **Multiple active** — Match the user's recent prompt against contract topics. If unambiguous, use the match. If ambiguous, list active contracts and ask which.
- **None active** — Tell the user there is nothing to implement and suggest `/spec-flow start`.

### 2. Read the contract

Read the full contract file. Follow any linked ndr atoms (`[[ndr-...]]` references) and read them.

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
- Confidence is not persisted. Each invocation re-negotiates cadence.
- Implementation must respect the contract's *Out of scope* — if a tempting addition surfaces, propose an amendment via `spec-flow:amend`. Do not just add it.
