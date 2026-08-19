---
id: "233ar3"
title: Contract working-matter is cold-legible at the close gate
status: current
decision_date: 2026-07-10
author: Jacob Hoehler
conviction: tentative
project: jdh-agents
labels:
  - process
  - read-side
binds:
  - plugins/spec-flow/**
supersedes: []
superseded_by: []
derived_from:
  - .docs/model-review-2026-07-10-contract-v2.md
informed_by: []
---

# 233ar3 — Contract working-matter is cold-legible at the close gate

## Decision

The contract's audience axis applies recursively: front-matter is cold-legible at the review gate, and working-matter is cold-legible at the close gate, where the closer may not be the implementer. This restates principle #4, which had claimed working-matter can stay internal.

## Scope

- Binds: the contract template's reading-order convention and close's harvest step.
- Applies at both single-contract and nested-parent altitude.

## Commitments

- Working-matter must meet a fresh-closer legibility standard; the atom-shaped Decision-log row already encodes it.
- Neither surface is written for a mid-flight-churn reader.

## Revisit if

- spec-flow becomes single-user-only, so the closer always equals the implementer.

## Context

- v2 principle #4 claimed working-matter can stay internal because cold readers only read at the gates.
- Close is a gate, and it harvests the Decision log cold.
- The Linear host supports multiple people and resume-after-weeks, so the closer often lacks the implementer's conversational context.
- A mutable nested parent is also harvested cold at parent-close.

## Why

The "internal" claim is simply false at the close gate, and the multi-person and resume paths make closer-is-not-implementer the normal case, not an exotic one — so working-matter has to be legible to a fresh reader. The cost of admitting this is near zero, because the atom-shaped row grammar already is that legibility standard; naming it just gives the row a second reason to exist beyond promotion. Asserting the closer always equals the implementer would preserve working-matter as private shorthand but contradicts the multi-person close the skills already implement.

## Alternatives

- **declare closer equals implementer** — verdict: rejected: untenable given the multi-person Linear close already in the skills (reviewer routing, @closer attribution) and resume-after-weeks.
