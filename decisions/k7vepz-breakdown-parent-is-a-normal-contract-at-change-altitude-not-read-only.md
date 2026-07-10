---
id: "k7vepz"
title: Breakdown parent is a normal contract at change altitude, not read-only
status: current
decision_date: 2026-07-10
author: Jacob Hoehler
conviction: tentative
project: cc-marketplace
labels:
  - architecture
  - scope
binds:
  - plugins/spec-flow/**
  - plugins/pm/skills/breakdown/**
supersedes: []
superseded_by: []
derived_from:
  - .docs/model-review-2026-07-10-contract-v2.md
informed_by: []
---

# k7vepz — Breakdown parent is a normal contract at change altitude, not read-only

## Decision

In spec-flow's variable-fill model, a breakdown parent is a full contract at change altitude — front-matter plus working-matter — not a read-only front-matter-only spec. Variable-fill collapses to one shape, nested: a contract, or a tree of contracts.

## Scope

- Binds: the contract template and pm breakdown's parent/slice relation.
- Depends on the recursive-audience decision (working-matter cold-legible at close).

## Commitments

- The parent gains its own amend discipline and a parent-close that harvests integration decisions.
- Whole-change and cross-slice decisions live in the parent's Decision log; slice-local decisions stay in slice logs — a duplication rule close must enforce.

## Revisit if

- Parents in practice never accrete working-matter (would vindicate a read-only parent).

## Context

- v2's parent was read-only, front-matter only, never accreting a worksheet, closed per-slice.
- A wide refactor with a shared integration branch has slices that cannot go green alone, whose end-to-end Done-when and integration decisions had no home — neither a green-alone slice nor the read-only parent.
- The slicing strategy itself, and decisions several slices share, sit at an altitude between whole-change and slice-local.
- A read-only parent also forbids amending a breakdown's whole-change Done-when mid-flight.

## Why

Making the parent mutable homes three homeless things at once — the shared-integration state, whole-change decisions, and cross-slice decisions — and it unifies the model: a parent is just a contract at a higher altitude, so variable-fill stops being three shapes and becomes one, nested. What it trades away is the guarantee that an agreed epic spec never moves, which is worth an explicit amend discipline; read-only was too rigid regardless, since it also blocked legitimate whole-change Done-when amendments. Patching the pieces separately left two findings open and cost more machinery than dropping the constraint.

## Alternatives

- **keep read-only, patch the integration state with a super-slice, fix cross-slice decisions separately** — verdict: rejected: more machinery, two findings left unresolved.
- **a distinct fourth "integration contract" fill-depth** — verdict: rejected: converges with simply making the parent mutable.
