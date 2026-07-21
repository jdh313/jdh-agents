---
name: interrogate-model
description: Holistic representability review of a domain model taken as a whole — an authorization scheme, permission table, state machine, data model, or tenancy model. Use when the user says "interrogate the model", "review this authz/permission model", "what can this scheme NOT express", "is this design representability-complete", "can the model represent <persona/state>", "review the model as a whole", "audit the state machine for unrepresentable states", or after a second orthogonal axis / new role / new principal type is added to an existing model. Enumerates the legitimate scenarios the model must serve, marks which are unrepresentable or only-via-overreach, surfaces emergent cross-axis conflations and latent (fused) axes, and flags silently waived departures from stated principles. STOPS for adjudication, then routes findings to /capture-decision. Distinct from structural review (improve-codebase-architecture), single-decision deliberation (interrogate-decision), and code-vs-decision drift (drift-check).
argument-hint: "[model or area to interrogate]"
effort: high
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Agent
  - AskUserQuestion
  - Write
  - TodoRead
  - TodoWrite
---

# interrogate-model

## Overview

A holistic **representability** review of a model taken *as a whole*. Where `/interrogate-decision` stress-tests a single candidate atom and the NDR ledger captures *why each piece*, this skill draws the complete model the atoms compose into and asks the question atom-by-atom capture structurally cannot: **what legitimate scenarios can this model NOT express, and where did independently-correct decisions silently fuse?**

It is the forward read of Minsky's "make illegal states unrepresentable" — not "can an illegal state be built?" but "is every *legal* state reachable?" The failure class it targets is **emergent across decisions made weeks apart**: invisible to diff-level review (it is a whole-model property, not in any one diff), to atom-by-atom capture (no atom says "here is the complete model and its limits"), and to behavioral tests (they enshrine the model's current shape rather than question it).

```
ground + reconstruct model ──► enumerate scenarios ──► representability matrix
   ──► cross-axis coupling audit ──► silently-waived-departure scan
   ──► gap report ──► STOP ──► (user adjudicates) ──► /capture-decision + follow-ups
```

## Vocabulary

This skill operates on the terms defined in [`../../CONTEXT.md`](../../CONTEXT.md). Use them exactly — they are load-bearing for every finding:

- **Model** — the holistic domain abstraction under review (its axes, roles, state spaces, and how they compose).
- **Axis** — an independently-variable dimension. Forced co-variation between two axes = a **conflation**; a concern fused into an axis that should stand alone = a **latent axis**.
- **Scenario** — the unit enumerated and tested; a legitimate thing the model must express. Verdicts: **representable / unrepresentable / only-via-overreach**.
- **Subject** *(access models only)* — the *who* of a scenario (subject–action–object–scope).
- **Departure** — divergence from a stated principle; **waive** *(v.)* — to deliberately set one aside. The finding is a **silently waived departure** (waived in code/comment, not in a named decision).

## When to use

- A model has grown across many decisions and was never reviewed as a whole (the atom-by-atom blind spot).
- A **second orthogonal axis, a new role/tier, or a new principal type** was just added to an existing model — re-audit the older axis's coupling assumptions *at the seam* where they meet (this is exactly where individually-correct decisions fuse).
- The user poses a persona/scenario and asks whether the model can represent it ("can a customer-success owner delete for one tenant?").
- Pre-design or periodic holistic audit of an authz scheme, permission table, state machine, data model, or tenancy model.

**Do NOT use** for:

- **Structural** review — module depth, coupling, testability → `improve-codebase-architecture` (the structural counterpart; this skill is the *expressibility* counterpart).
- A **single candidate decision** — is this one choice NDR-grade? → `interrogate-decision`.
- **Code-vs-decision drift** — does the code contradict an existing atom? → `drift-check` (it catches *accidental* departures; this skill catches *silently waived* ones).
- **Terminology** sharpening of a plan → `grill-with-docs`.

## Inputs

- Use the user's invocation input as the model or area to interrogate (e.g. "the authz model", a module path, "the order state machine"). If no input was supplied, infer it from the conversation / working area and confirm in one line before starting: `"Interrogating: <one-line model description>. Right model?"`

## Method

Load [`references/method.md`](references/method.md) first — it holds the heuristics for each phase (how to reconstruct axes, detect conflations and latent axes, build the matrix, and distinguish a waived departure from drift). The phases below are the workflow skeleton; the doc is the how.

Surface each phase's finding as you go (list-first, terse). The phases build on each other — don't dump them all at once.

### Phase 1 — Ground and reconstruct the model

**Entry:** the model/area is identified.
**Actions:**
1. Invoke `/ground` on the area to surface governing NDR heads; read the project's `CONTEXT.md` glossary alongside them.
2. Dispatch the Agent tool with `subagent_type=Explore`, `name="model-cartographer"` to read the implementing code + grounded atoms and reconstruct the model as an explicit **axes × value-sets** table — each axis, its values, and the code site that defines it. (Naming the agent keeps it addressable for follow-ups.)
3. Have the cartographer flag **candidate latent axes**: concerns that look independently-variable but are currently fused into an axis (e.g. "system administration" riding inside a role tier).

**Exit:** an axes table exists, with code locations and a list of candidate latent axes. This table is the artifact the ledger never produces — "here is the whole model."

### Phase 2 — Enumerate scenarios

**Entry:** the axes table exists.
**Actions:**
1. List the legitimate **scenarios** the model must express. Seed from the axes (their value combinations are the candidate space), from code, and from atoms.
2. For access models, frame each as **subject–action–object–scope**.
3. Use `AskUserQuestion` to confirm and extend the list — the user knows scenarios not yet in the code (the missing-requirement case that no diff or test can surface). **Do not skip this** — an unrepresentable scenario is invisible until someone names it.

**Exit:** a confirmed scenario list, including at least the personas/states the user expects the model to serve.

### Phase 3 — Build the representability matrix

**Entry:** confirmed scenario list.
**Actions:**
1. For each scenario, assign a verdict: **representable / unrepresentable / only-via-overreach**.
2. For every non-representable scenario, name the **specific axis or coupling** that blocks it.

**Exit:** a scenario × verdict matrix, each gap traced to its cause. This is the core "what can this NOT express?" artifact.

### Phase 4 — Cross-axis coupling audit

**Entry:** the matrix exists.
**Actions:**
1. For each pair of axes, ask: *does one silently override or collapse the other?* → record **conflations**.
2. Re-audit older axes wherever a newer axis meets them (the **seam**) — this is where decisions made weeks apart fuse.
3. Confirm or reject the **candidate latent axes** from Phase 1.

**Exit:** a list of conflations and confirmed latent axes, each with its code site.

### Phase 5 — Silently-waived-departure scan

**Entry:** axes and couplings are mapped.
**Actions:**
1. Find places the model **deliberately departs** from one of its own stated principles (an NDR head, a `CONTEXT.md` invariant, an explicit commitment).
2. Cross-check each against current heads with `ndr search` / `ndr current` (never `Read` a seed atom directly).
3. Classify: an *accidental* departure is drift (note it, route to `drift-check`); a *deliberate* one waived in code/comment with no owning decision is a **silently waived departure** — the finding.

**Exit:** a list of silently waived departures, each naming the principle waived and what the waiver forecloses.

### Phase 6 — Gap report

**Entry:** Phases 3–5 complete.
**Actions:** Write the report to `<repo>/.docs/model-review-<timestamp>.md` (gitignored scratch — nothing lands in tracked source). Use the scaffold in [`references/report-template.md`](references/report-template.md), grouped by finding type. After writing, `open` it and give the user the absolute path.

**Exit:** the report file exists and is opened.

### Phase 7 — STOP and adjudicate

**Entry:** the report exists.
**Actions:** Present the finding summary and **STOP**. The user confirms, overrides, or reprioritizes. Do not route or capture autonomously — the deliberation informs a human call.

**Exit:** the user has adjudicated which findings to act on.

### Phase 8 — Route (only what the user confirmed)

- **Silently waived departure** → `/capture-decision` to record the waiver as a decision that *names what it forecloses* — own the cost forward rather than leaving it an inline convenience. For an access-model waiver, this is also where a deliberate "we accept scoped-X is unrepresentable for now" gets captured.
- **Unrepresentable / only-via-overreach scenario, conflation, latent axis** → a follow-up change (a Linear ticket via the `linear` skill, or a `spec-flow` contract if it is a real change) **or** an explicit decision to accept the limitation, captured via `/capture-decision` so the foreclosure is owned rather than rediscovered.

Never write to the ledger directly — capture is `/capture-decision`'s job. This skill produces the report and hands off.

## Output example

Condensed summary presented at the Phase 7 STOP (full report lives in `.docs/`). Synthetic generic-authz illustration:

```markdown
**interrogate-model — <project> authz model**

Axes: role/action (viewer/editor/admin) × tenant-scope (specific tenants / all-tenants).

Unrepresentable / overreach scenarios:
- "scoped owner deletes within ONE tenant" — ONLY-VIA-OVERREACH. delete is admin-only (role
  axis), and admin is hard-wired to all-tenants (authz/policy.py:NN), so the only way to grant
  delete-on-one is to mint a global superuser. Scoped-owner is unrepresentable.

Conflations:
- role-axis admin silently overrides the tenant-scope axis → the two intended-orthogonal axes
  are fused (contradicts <ndr:ref stating orthogonality>).

Latent axes:
- "system administration" (grant-management) is fused into the role axis — should be its
  own axis (you cannot be a system admin without also being a top-tier deleter).

Silently waived departures:
- authz/policy.py:NN deliberately waives the stated orthogonality principle (comment: "admins
  see all tenants regardless of recorded scope") with no owning decision. → /capture-decision,
  naming that it forecloses scoped-admin.

— Stopping for your call. Capture the waiver + open a follow-up to decouple the axes? (confirm / adjust / skip)
```

## Rationalizations to reject

| Rationalization | Why it's wrong |
|-----------------|----------------|
| "The tests pass, so the model is fine." | Tests assert the model does what it *says*; they enshrine the current shape. Only "what can't this express?" asks whether it says the *right* thing. |
| "Every decision was reviewed when it landed." | The conflation is emergent across decisions; no single diff or atom contains it. Whole-model review is the *only* place it appears. |
| "Admin = full power is the standard shape." | Standard ≠ correct. Review catches deviations; the default is invisible. Name the scenario (scoped owner) and the gap appears. |
| "The short-circuit is documented in the docstring." | A docstring is not a decision. A deliberate departure that forecloses future scenarios must be a named decision that owns its cost — not an inline comment. |
| "No one asked for scoped-admin." | A missing capability is invisible until the scenario is named — that is *why* Phase 2 enumerates scenarios with the user rather than reading them off the code. |

## Hard rules

1. **Reconstruct the whole model before judging it.** The axes table (Phase 1) is the point — never review a model you have only seen atom-by-atom.
2. **Enumerate scenarios *with the user* (Phase 2).** The load-bearing gaps are the ones not yet in the code; you cannot read them off the implementation.
3. **Run 1–6, then STOP (Phase 7).** Adjudication is the user's. Never capture or open tickets autonomously.
4. **Never write to the ledger.** Routing is a handoff to `/capture-decision`; this skill writes only the `.docs/` report.
5. **The CLI owns supersession.** In Phase 5 use `ndr search` / `ndr current` / `ndr resolve` — never `Read` a seed atom to judge a principle.

## Related

- `improve-codebase-architecture` — the **structural** counterpart (depth/coupling). interrogate-model is the **expressibility** counterpart. Run both for a full design review.
- `interrogate-decision` — single-candidate deliberation. interrogate-model reviews the whole model those decisions compose into.
- `drift-check` (ndr) — catches *accidental* departures; interrogate-model catches *silently waived* ones.
- `/capture-decision` (ndr) — the Phase 8 handoff target for waivers and accepted-limitation decisions.
- `/ground` (ndr) — Phase 1 grounding in governing heads.
- [`references/method.md`](references/method.md) — per-phase heuristics.
- [`references/report-template.md`](references/report-template.md) — gap-report scaffold.
