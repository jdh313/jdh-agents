---
name: amend
description: >-
  This skill should be used when the AI realizes during implementation that the
  contract's front-matter — the target it promises (What we're doing, Why, Out
  of scope, Done when) — is becoming inaccurate: a new constraint narrows scope,
  an Out-of-scope item must move in-scope, or a resolved fork changes what
  Done-when promises. Typically invoked from within `spec-flow:implement` rather
  than directly by the user. Works for both file-hosted (`.docs/`) and
  Linear-hosted contracts. Surfaces a proposed front-matter edit to the user,
  waits for sign-off, then applies it to the right host (Edit for files,
  save_issue for Linear). Never edits front-matter silently. Not for
  Decision-log rows (that is implement's no-sign-off append) or for rewriting
  Approach / wiring (free working-matter). The contract is an agreement; both
  parties must agree to changes to the target.
---

# spec-flow:amend

Propose a contract amendment mid-implementation. Sign-off required before any edit. Amend touches the **contract doc** only — the companion doc is working-matter and is never amended. Host (file vs. Linear) is re-detected from the contract identifier; see `../../references/hosts.md`.

## When to invoke

- During `spec-flow:implement`, when the work reveals the contract's **front-matter — the target it promises** — no longer matches reality:
  - A new constraint surfaced (library limitation, existing pattern conflict, performance issue) that **narrows or shifts what the contract can deliver** — i.e. it changes *Done when* or *What we're doing*, not just how.
  - An item in *Out of scope* now needs to be in scope (or vice versa).
  - A resolved fork changes what *Done when* promises — the resolution isn't just logged, it moves the target.
- User explicitly asks: "update the contract to reflect X".

**Not an amend:** switching the *Approach / wiring* itself is a **free working-matter edit** in the companion doc — Approach is ephemeral mechanics that evaporate at close, so `implement` just rewrites it, no sign-off. The *decision* behind the switch (why this approach over the old one) is logged as a `[resolved]` Decision-log row (append). Amend fires only when the switch also moves the front-matter target.

## Do NOT invoke for

- Trivial implementation details that don't change the contract's substance (variable names, internal helper choices, file organization).
- **Appending a Decision-log row** — logging a fork's outcome (`[resolved]` / `[deferred]` / a new `[open]`) is `implement`'s routine `append`, not an amendment. It writes working-matter and logs a fact; it does not renegotiate the target, so it takes no sign-off.
- **Reconciling a drifted *Done when* at close** — correcting a bullet's wording to match shipped reality is `spec-flow:close`'s `reconcile` op, which rides close's own sign-off. Amend is only for renegotiating the target *in flight*.
- Final state at close — that is `spec-flow:close`'s migration step, not amendment.

## Amend vs. append vs. reconcile

Three ops touch the contract; only **amend** renegotiates the live agreement, so only amend gates on sign-off here:

| Op | Touches | Document | When | Renegotiates? | Owner |
|----|---------|----------|------|---------------|-------|
| **append** | Decision log | companion | in flight | no | `implement` (step 5) |
| **amend** | front-matter | contract doc | in flight | **yes** | this skill |
| **reconcile** | front-matter | contract doc | at close | no | `close` |

**The concurrency guard follows the document, not the host.** Appends land in the companion — a `.docs/` file on both hosts — so they need **no** guard anywhere. Only contract-doc writes carry one, and only on the Linear host, where a write is a whole-description overwrite (re-fetch + compare; it only bites when a concurrent edit is actually detected). Since amend is the only in-flight contract-doc write, step 4 below is now the *only* place the guard fires during implementation.

## Workflow

### 1. Summarize the divergence

In one short paragraph, tell the user what has drifted:

> "While wiring up the middleware, I found the upstream API can't issue refresh tokens on our current plan — so the contract's *Done when* bullet 'session survives a silent token refresh' can't ship in this change. Proposing an amendment to narrow the target." (Had this been a pure how-change — same target, different wiring — I'd just rewrite *Approach / wiring* and log the call as a `[resolved]` row, no amendment.)

### 2. Propose the specific edit

Show before / after, scoped to the affected **front-matter** section only:

```
**Done when** (current):
- Session survives a silent token refresh without re-login.

**Done when** (proposed):
- Session survives until access-token expiry; silent refresh deferred (logged as a [deferred] Decision-log row, tracked separately).
```

### 3. Wait for sign-off

Ask explicitly: "Apply this amendment?"

Do NOT apply without user confirmation. Acceptable responses:

- "yes" / "apply" / "go" → apply the AI's proposed version.
- A modified edit from the user → apply the user's version instead.
- "no" / rejection → leave the contract unchanged; the AI must reconcile within the existing contract or surface a different proposal.

### 4. Apply

If approved, write the amendment to the contract's host. Preserve every section the amendment does not target.

- **File host** — `Edit` the contract file in place.
- **Linear host** — Fetch current description via `mcp__linear-server__get_issue`. **Concurrent-edit guard:** compare this fresh fetch against the description you read at the start of the `implement` session (or at the start of this `amend` invocation). If they differ, warn:

  > "The ticket description changed since I started — someone may have edited concurrently. Merge my amendment over the current version, overwrite anyway, or abort?"

  Wait for the user's choice before proceeding. If they say merge/overwrite: apply the targeted section change locally to the latest-fetched description, then write the full updated description back via `mcp__linear-server__save_issue`. (Linear's API replaces the description; do not lose untouched sections.)

**Linear host — audit trail.** Overwriting the description erases the amendment history, so after the `save_issue` write, post the before/after as a ticket comment via `mcp__linear-server__save_comment`:

```markdown
**Contract amendment** — <one-line reason for the divergence>

**<Section>** before:
- <old bullet(s)>

**<Section>** after:
- <new bullet(s)>
```

One comment per amendment, scoped to the sections that changed. The description stays the single source of truth; comments are the changelog.

If the host is Linear and `mcp__linear-server__*` tools aren't loaded:

> "Linear MCP server isn't connected — I can't write the amendment to TEAM-123. Pause while you wire up the MCP, or hold the amendment in conversation until you can?"

Do not install or configure the integration without approval, and never ask the user to paste credentials into chat.

If the user provided a modified version, apply that, not the AI's original.

### 5. Resume

Return to `spec-flow:implement`. The amendment is now part of the agreement.

## Notes

- The contract is a *contract* — both parties must agree to changes. This is the load-bearing principle.
- Amendments should be narrow: edit only the section that is actually drifting. Don't restructure the whole contract.
- Frequent amendments on the same contract are a signal that the original drafting was thin — note this for the close step's reflection.
