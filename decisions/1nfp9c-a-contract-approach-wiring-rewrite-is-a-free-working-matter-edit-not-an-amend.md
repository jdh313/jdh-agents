---
id: "1nfp9c"
title: A contract Approach/wiring rewrite is a free working-matter edit, not an amend
status: current
decision_date: 2026-07-10
author: Jacob Hoehler
conviction: tentative
project: cc-marketplace
labels:
  - process
  - write-side
binds:
  - plugins/spec-flow/**
supersedes: []
superseded_by: []
derived_from:
  - .docs/2026-07-10-spec-flow-v2.1-rollout.md
informed_by:
  - 957bqa
---

# 1nfp9c — A contract Approach/wiring rewrite is a free working-matter edit, not an amend

## Decision

A mid-flight rewrite of a contract's Approach/wiring section is a free, ceremony-free working-matter edit that implement makes with no sign-off — not an amendment, because Approach is working-matter, not the co-signed target. The decision behind an approach switch is logged separately as a [resolved] Decision-log row.

## Scope

- Binds spec-flow's amend and implement skills and the contract template's append/amend/reconcile mutation-ops model.
- Applies in flight, not at close.

## Commitments

- amend fires only when an edit changes front-matter, the co-signed target; an approach switch that also moves Done-when is therefore an amend.
- implement rewrites Approach/wiring freely, no sign-off.
- The call behind an approach switch is logged as a [resolved] Decision-log row (append), so the rationale still harvests at close.

## Revisit if

- Approach rewrites routinely change Done-when in practice, so the free-edit class rarely applies on its own and the switch is almost always already an amend.

## Context

- v2.1 files Approach/wiring under working-matter, which evaporates at close.
- The mutation-ops model has three ops: append (Decision log, no sign-off), amend (front-matter, sign-off), reconcile (front-matter at close).
- A code review found amend's op table restricted amend to front-matter while amend's own triggers and worked example still edited Approach, leaving an approach rewrite outside every op.

## Why

Approach/wiring is ephemeral mechanics that evaporate at close, so it is not the target the two parties co-signed; gating its rewrite behind amend's sign-off would force ceremony on a non-target edit and contradict its own working-matter classification. Keeping the rewrite free while routing the decision behind it to a [resolved] row preserves the rationale for harvest without freezing the mechanics.

## Alternatives

- **keep Approach under amend's sign-off gate** — verdict: rejected: contradicts Approach's working-matter classification and gates a non-target edit, forcing sign-off ceremony on ephemeral mechanics.
