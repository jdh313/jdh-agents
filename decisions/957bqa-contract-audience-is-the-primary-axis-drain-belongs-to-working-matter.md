---
id: "957bqa"
title: Contract audience is the primary axis; drain belongs to working-matter
status: current
decision_date: 2026-07-10
author: Jacob Hoehler
conviction: tentative
project: agent-marketplace
labels:
  - architecture
  - process
binds:
  - plugins/spec-flow/**
supersedes: []
superseded_by: []
derived_from:
  - .docs/model-review-2026-07-10-contract-v2.md
informed_by: []
---

# 957bqa — Contract audience is the primary axis; drain belongs to working-matter

## Decision

In the contract shape, audience is the primary organizing axis and drain-target is a property of working-matter only: the Decision log promotes via the canonical ndr worthiness rubric, Approach/wiring evaporates, and front-matter has no structural drain. This retires the framing of audience and drain as two co-equal orthogonal axes.

## Scope

- Binds: the contract template's section organization and close's migration step.

## Commitments

- Close harvests only working-matter — the Decision log to ndr.
- Front-matter rests in the archived contract; a durable change-level rationale reaches ndr only as a promoted decision's Context, never via a front-matter drain.

## Revisit if

- A front-matter section acquires durable content that no promoted decision or README already carries.

## Context

- v2 presented audience (front/working) and drain (sink/evaporate) as two co-organizing axes, but only three of four quadrants were named.
- The unnamed front-matter-that-promotes cell — the change-level Why — made audience appear to determine drain.
- Neither host deletes at close: the file archives, the Linear body persists.
- Decision-level whys already flow to ndr through the Decision log.
- A change-level Why is either absorbed into a promoted atom's Context or rests in the archive.

## Why

The durable whys that matter are decision-whys, and those already sink to ndr through the Decision log, so front-matter needs no drain of its own — which means drain is genuinely a working-matter concern and the two-co-equal-axes geometry was overstatement. Naming that keeps the model honest and matches how close already behaves: it harvests the Decision log and never structurally drains Goal or Why. Giving front-matter Why its own conditional drain would add machinery the decision-why path makes unnecessary.

## Alternatives

- **force-populate the front-matter-promote quadrant by giving Why a structural drain** — verdict: rejected: unnecessary machinery, since decision-whys already reach ndr and the archive backstops the rest.
