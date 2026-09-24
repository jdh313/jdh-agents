---
id: "z1yeag"
title: Splitting an oversized merge-together ticket needs no earn-it test
status: current
decision_date: 2026-09-24
author: Jacob Hoehler
conviction: tentative
project: jdh-agents
labels:
  - process
  - scope
binds:
  - plugins/pm/references/layer-policy.md
  - plugins/pm/skills/lead/SKILL.md
  - plugins/pm/skills/breakdown/SKILL.md
supersedes: []
superseded_by: []
derived_from: []
informed_by: []
---

# z1yeag — Splitting an oversized merge-together ticket needs no earn-it test

## Decision

When a ticket's change should merge as one unit but spans several surfaces or will not fit one implementation session, it is split into session-sized children with the original ticket as the parent. The epic earn-it test does not apply to this split; it still gates creating a brand-new parent.

## Scope

- Binds: splitting an existing ticket by size.
- Does not bind: creating a new epic parent to group existing or future work, which keeps the three-part earn-it test.

## Commitments

- The parent's body states that the children merge together and names the merge order.
- Each child is sized to one `haiku` or `sonnet` implementation session.
- Children inherit the parent's milestone.

## Revisit if

- Splits start producing parents with one or two children that add tracking overhead without roll-up value.

## Context

- The layer policy allowed a parent ticket only when it had five or more children, its own design substrate, and cross-ticket discussion.
- A ticket too big for one agent session had no sanctioned way to be split while staying visibly one change.
- The PM working prompt already split such tickets anyway, as a declared deviation from the pm skills.

## Why

The earn-it test asks whether a *new* grouping pays for its overhead. A size split creates no new grouping: the ticket already exists and already names the change, and its children are the same work cut to session size. Applying the test there forbade the one split that implementation needs most, which is why it was being worked around.

## Alternatives

- **Apply the earn-it test to splits too** — rejected: a two- or three-child split fails the five-child bar by construction.
- **Keep it as a pm:lead-only declared deviation** — rejected: every other slicing skill would still follow the stricter rule, so the same ticket would be split differently depending on which skill touched it.
