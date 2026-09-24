---
id: "eg80p2"
title: Use the tracker's native parent/child relation for parent links
status: current
decision_date: 2026-09-24
author: Jacob Hoehler
conviction: strong
project: jdh-agents
labels:
  - architecture
  - scope
binds:
  - plugins/pm/references/layer-policy.md
  - plugins/linear/skills/linear/SKILL.md
  - plugins/linear/agents/linear-ops.md
  - plugins/pm/skills/**
supersedes: []
superseded_by: []
derived_from: []
informed_by: []
---

# eg80p2 — Use the tracker's native parent/child relation for parent links

## Decision

When a tracker has a native parent/child relation (Linear `parentId`, GitHub sub-issues, a Fibery parent relation), every declared parent link is written with it. Sibling links (`relatedTo` / `blocks`) stand in for a parent only on a tracker that has no native relation.

## Scope

- Binds: any skill or agent in this marketplace that writes a parent-child link between tickets, on any tracker.
- Does not bind: ordering between siblings, which stays a `blocks` relation.

## Commitments

- The `linear` skill and `linear-ops` write `parentId` for a declared parent and no longer refuse it.
- Callers keep declaring only *that* a ticket has a parent; the tracker-owning skill decides the mechanism.
- A new tracker adapter documents its native parent relation, or states that it has none.

## Revisit if

- A tracker's native relation turns out to break automation this marketplace relies on (roll-up, auto-close, integration sync).

## Context

- `pm`'s layer policy listed subissues as an inactive layer, "not retired, not adopted", with the question deferred.
- The default parent shape was a regular ticket linked to its children by `relatedTo` or `blocks`.
- `linear-ops` carried a hard rule never to promote a link to `parentId`, and stopped when a caller's intent could not be expressed as a sibling link.
- Work that must merge as one change was being split into session-sized tickets with nothing in the tracker tying them together as one unit.
- `pm:chart`'s map diverged from upstream, which makes every map ticket a child issue, solely because of that deferral.

## Why

The native relation is what the tracker's own features read: parent progress, auto-close when every child is done, and nested display in list views. A sibling link carries none of that, so a split change looked like unrelated tickets and its completion had to be tracked by hand. The deferral was protecting a question that had become live, and holding it open was costing a workaround in every caller.

Stating the rule tracker-agnostically costs nothing today, since only Linear writes parent links here, and it keeps a future Fibery or GitHub path from re-litigating the same question.

## Alternatives

- **Keep the sibling-parent shape** — rejected: forfeits the tracker's roll-up and auto-close, which is the reason to group the children at all.
- **Native relation only for splits, sibling links for epics** — rejected: two shapes for one concept, and callers would need to know which one applies.
- **Linear-only rule** — rejected: the same question would reopen on the first non-Linear tracker.
