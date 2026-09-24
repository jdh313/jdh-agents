---
id: "2qtwp6"
title: Invoking em:lead pre-authorizes moving that ticket to in-progress
status: current
decision_date: 2026-09-24
author: Jacob Hoehler
conviction: tentative
project: jdh-agents
labels:
  - process
  - write-side
binds:
  - plugins/em/skills/lead/SKILL.md
  - plugins/em/references/trackers/**
supersedes: []
superseded_by: []
derived_from: []
informed_by: []
---

# 2qtwp6 — Invoking em:lead pre-authorizes moving that ticket to in-progress

## Decision

Running `em:lead` on a ticket is consent to move that one ticket to its tracker's in-progress state, just before work on it begins. Every other tracker write (other states, bodies, comments, creates, other tickets) still needs the user's approval in the same turn.

## Scope

- Binds: `em:lead`'s own state transition for each ticket it was invoked on, including each ticket of an invoked milestone as its work begins.
- Does not bind: `em:start`, which writes no tracker state; `pm` skills, which never move a ticket to in-progress.

## Commitments

- The transition never moves a ticket backwards; a ticket already started or later is left alone and noted.
- A tracker with no in-progress state (plain GitHub Issues) reports the transition as unmapped and skips it.
- `lead` pre-approves `mcp__linear-server__save_issue` in `allowed-tools`, so its hard-boundaries list, not a permission prompt, is what stops any other Linear write.

## Revisit if

- A pre-authorized transition fires on a ticket the user did not intend to start.
- Another `save_issue` call slips through under the pre-approval.

## Context

- `em:lead`'s hard boundaries required same-turn approval for every tracker write.
- No step in `lead` moved a ticket to in-progress, so a started ticket sat in Todo until moved by hand.
- The engineering-manager working prompt asks for no interruptions for calls with a defensible default.

## Why

Naming a ticket to `lead` already expresses intent to start it, so asking again is a confirmation with only one sensible answer, and it lands exactly when the user has handed the work off. Keeping the consent to that one field on that one ticket preserves the same-turn rule for everything that actually changes what others see about the work.

## Alternatives

- **Confirm the transition each time** — rejected: a yes/no with one plausible answer, at the moment the user stepped away.
- **Leave it manual** — rejected: the tracker misreports started work until someone remembers.
