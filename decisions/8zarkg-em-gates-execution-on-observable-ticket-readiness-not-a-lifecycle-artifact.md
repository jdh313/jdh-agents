---
id: "8zarkg"
title: em gates execution on observable ticket readiness, not a lifecycle artifact
status: current
decision_date: 2026-09-24
author: Jacob Hoehler
conviction: strong
project: jdh-agents
labels:
  - architecture
  - process
binds:
  - plugins/em/skills/**
supersedes: []
superseded_by: []
derived_from: []
informed_by:
  - v4wn6d
---

# 8zarkg — em gates execution on observable ticket readiness, not a lifecycle artifact

## Decision

`em` has no fixed lifecycle and no draft artifact. `em:lead` treats a ticket as ready when its body observably has an aim line and a `Done when` slot with at least one bullet; a ready ticket goes straight to dispatch, and one that is not is scoped inline first. Each skill is a standalone entry point.

## Scope

- Binds: `em:start` and `em:lead`, and any skill later added to `em`.
- Does not bind: how `pm` shapes a ticket; `em` only reads the result.

## Commitments

- The readiness check reads the ticket body, never the agent's impression of how ready it is.
- `## Acceptance criteria`, or a tracker's equivalent field, counts as the `Done when` slot.
- Execution shape (inline, one worker, parallel lanes, test-first, diagnose first) is chosen per ticket from what the ticket and code show.
- No `em` skill may require another to have run first.

## Revisit if

- Shaped tickets routinely reach dispatch missing context that a scoping pass would have caught.

## Context

- `spec-flow` wrapped every change in a contract plus a companion document and a fixed draft, red phase, implement, verify, close path.
- `attention-workflow` imposed a seven-state lifecycle from Frame to Close.
- The user had stopped using both, and started tasks by pasting ad-hoc prompts for scoping, engineering-manager orchestration, and PM planning.
- Tickets written with `pm` already carry an aim line and a `Done when` slot.

## Why

A fixed lifecycle charges every change for the ceremony the largest change needs, and the user's actual practice had already abandoned it. The ticket already carries the state a lifecycle artifact would duplicate, so reading it directly removes a document without losing a gate. Keying the gate on the body's structure rather than the agent's judgment follows the rule that composition triggers must be observable.

## Alternatives

- **Keep a spec-flow-style contract as one optional shape** — rejected: the user wanted no dependency on spec-flow, which is headed for retirement.
- **Require `em:start` before `em:lead`** — rejected: forces a scoping pass on tickets that are already shaped.
- **Let the agent judge readiness** — rejected: an agent auditing its own impression is the failure `ndr:v4wn6d` rules out.
