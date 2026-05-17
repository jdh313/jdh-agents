---
name: amend
description: This skill should be used when the AI realizes during implementation that the contract is becoming inaccurate — wrong approach, new constraint, scope shift, or a deferred open question now needing a decision. Typically invoked from within `spec-flow:implement` rather than directly by the user. Surfaces a proposed contract edit to the user, waits for sign-off, then applies the edit. Never edits the contract silently. The contract is an agreement; both parties must agree to changes.
---

# spec-flow:amend

Propose a contract amendment mid-implementation. Sign-off required before any edit.

## When to invoke

- During `spec-flow:implement`, when the work reveals the contract no longer matches reality:
  - Approach turned out wrong; switching to a different one.
  - A new constraint surfaced (library limitation, existing pattern conflict, performance issue).
  - An item in *Out of scope* now needs to be in scope (or vice versa).
  - An *Open question* has been resolved through implementation and should be promoted to *Approach*.
- User explicitly asks: "update the contract to reflect X".

## Do NOT invoke for

- Trivial implementation details that don't change the contract's substance (variable names, internal helper choices, file organization).
- Final state at close — that is `spec-flow:close`'s migration step, not amendment.

## Workflow

### 1. Summarize the divergence

In one short paragraph, tell the user what has drifted:

> "While wiring up the middleware, I found the existing auth helper expects a different shape. The contract's *Approach* says to use `verify_token()` directly, but that won't work — we need to wrap it. Proposing a contract amendment."

### 2. Propose the specific edit

Show before / after, scoped to the affected sections only:

```
**Approach** (current):
- Use `verify_token()` directly in the middleware.

**Approach** (proposed):
- Wrap `verify_token()` in a `TokenVerifier` adapter (follows existing pattern in `auth/adapters.py`).
```

### 3. Wait for sign-off

Ask explicitly: "Apply this amendment?"

Do NOT apply without user confirmation. Acceptable responses:

- "yes" / "apply" / "go" → apply the AI's proposed version.
- A modified edit from the user → apply the user's version instead.
- "no" / rejection → leave the contract unchanged; the AI must reconcile within the existing contract or surface a different proposal.

### 4. Apply

If approved, edit the contract file in place. Preserve every section the amendment does not target.

If the user provided a modified version, apply that, not the AI's original.

### 5. Resume

Return to `spec-flow:implement`. The amendment is now part of the agreement.

## Notes

- The contract is a *contract* — both parties must agree to changes. This is the load-bearing principle.
- Amendments should be narrow: edit only the section that is actually drifting. Don't restructure the whole contract.
- Frequent amendments on the same contract are a signal that the original drafting was thin — note this for the close step's reflection.
