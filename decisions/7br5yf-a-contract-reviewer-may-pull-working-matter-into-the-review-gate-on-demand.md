---
id: "7br5yf"
title: A contract reviewer may pull working-matter into the review gate on demand
status: current
decision_date: 2026-07-10
author: Jacob Hoehler
conviction: tentative
project: cc-marketplace
labels:
  - process
  - read-side
binds:
  - plugins/spec-flow/**
supersedes: []
superseded_by: []
derived_from:
  - .docs/2026-07-10-spec-flow-v2.1-rollout.md
informed_by:
  - 233ar3
  - 957bqa
---

# 7br5yf — A contract reviewer may pull working-matter into the review gate on demand

## Decision

At the pre-implementation review gate, front-matter is the reviewer's default surface, but the reviewer may pull working-matter (Approach/wiring) into review on demand. The audience reading-order sets the default reach, not a hard ceiling.

## Scope

- Binds the contract template's audience / reading-order convention at the review gate.
- Applies to both hosts; on Linear the whole contract body is one description, so nothing mechanically blocks the pull.

## Commitments

- Front-matter remains what the review gate puts up for review by default.
- A reviewer wanting to object to the integration approach may read Approach/wiring.
- Approach/wiring stays classified as working-matter — it is not promoted into front-matter.

## Revisit if

- Reviewers routinely need Approach by default, which would argue for promoting it into front-matter instead of leaving it a pull.

## Context

- 957bqa makes audience the primary axis and files Approach/wiring under working-matter.
- 233ar3 commits that front-matter is cold-legible at the review gate.
- A code review flagged that v2.1 removed the Approach-at-review visibility the old six-section-front-matter shape had, so a reviewer could no longer object to the integration approach before coding.

## Why

The audience order is a default reading reach, not an access-control ceiling, and the whole contract is a single document, so preserving the reviewer's ability to pull Approach costs nothing and keeps the pre-implementation architectural objection available. The alternative of promoting Approach back into front-matter would recover the visibility but partially revert audience-primary ordering and the drain model; leaving it hidden discards a real capability the six-section shape had.

## Alternatives

- **move Approach back into front-matter** — verdict: rejected: partially reverts 957bqa's audience-primary ordering and the working-matter drain model, since Approach still evaporates at close.
- **keep working-matter hidden from the reviewer** — verdict: rejected: foregoes a real pre-implementation objection capability the old six-section-front-matter shape provided.
