---
id: "v6hzfv"
title: Cap sub-issue nesting at one level
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
supersedes: []
superseded_by: []
derived_from:
  - "session research: sub-issue nesting depth across Linear, GitHub, Jira,
    ClickUp (2026-09-24)"
informed_by: []
---

# v6hzfv — Cap sub-issue nesting at one level

## Decision

A parent's children never have children of their own. A child that is still too big is split into more siblings under the same parent, or promoted to its own top-level issue when it no longer has to merge with the rest.

## Scope

- Binds: every parent-child link written by a skill or agent in this marketplace, on any tracker.
- Does not bind: hierarchies above the issue (projects, milestones, initiatives), which have their own layer rules.

## Commitments

- `linear-ops` refuses to set a parent that is itself a subissue, and says so rather than nesting further.
- The `linear` skill flattens a deeper caller tree under the top parent, or promotes a branch, and reports which.
- `pm:retro` flags nesting deeper than one level as a layer-policy violation.

## Revisit if

- Linear documents multi-level sub-issue roll-up and the integrations in use read grandchildren reliably.
- A real split repeatedly needs a grouping level between the parent and its session-sized children.

## Context

- Linear's documentation describes sub-issues only as parent to direct children, with the parent's auto-close keyed to them.
- A third-party Linear dashboard integration was reported to drop grandchildren silently.
- GitHub allows eight levels of sub-issues and gives no depth guidance.
- Jira forbids children of sub-tasks structurally; ClickUp's own guidance is one level for most work, rarely two, never three.
- Children in this workflow are sized to one agent implementation session.

## Why

What reads the tree decides the depth. Agents and integrations find work by walking sub-issues, and the evidence is that tooling built around one level can fail to see a grandchild at all; a ticket that automation cannot find is worse than a flat list. The second level also buys nothing here: children are already sized to one session, so a child that needs its own children is really more siblings.

## Alternatives

- **Allow arbitrary depth** — rejected: invites trees that roll-up and integrations misreport, with no grouping need that one level cannot meet.
- **Allow two levels** — deferred: no split so far has needed an intermediate grouping; reopen via the Revisit-if trigger.
