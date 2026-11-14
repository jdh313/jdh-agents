---
id: "81zdt0"
title: Give a Linear project only bounded-outcome work
status: current
decision_date: 2026-11-14
author: Jacob Hoehler
conviction: strong
project: jdh-agents
labels:
  - process
  - scope
binds:
  - plugins/pm/references/layer-policy.md
  - plugins/pm/references/issue-shape.md
  - plugins/pm/skills/groom/SKILL.md
  - plugins/pm/skills/breakdown/SKILL.md
  - plugins/pm/skills/retro/SKILL.md
  - plugins/linear/skills/linear/SKILL.md
  - plugins/linear/agents/linear-ops.md
  - plugins/linear/references/mcp-gotchas.md
supersedes: []
superseded_by: []
derived_from:
  - Linear ticket JUN-695 thread (2026-11-13 to 2026-11-14)
informed_by:
  - v6hzfv
  - rw9nyx
---

## Decision

A Linear project holds only work toward a bounded outcome with an end, and a ticket with no project is legal. Ongoing work (bugs, chores, maintenance) lives in the team backlog with no project, homed by a repo or area label and found by a saved view. When a skill or agent picks a project for a ticket, the first matching rule wins: (1) if the caller or user named a project, use it; (2) if the ticket advances a bounded outcome a project owns, such as a `pm:breakdown` slice of that project's goal, or it is a bug in that project's own work, such as a regression in a feature the project shipped, use that project; (3) otherwise, including unrelated bugs, chores and maintenance, set no project and add a repo or area label.

## Scope

- Binds: every project choice and project check made by the `pm` and `linear` plugins: the `linear` skill, the `linear-ops` agent, `pm:breakdown`, `pm:groom`, `pm:retro`, and the layer-policy and issue-shape references.
- Does not bind: sub-issue nesting, which `ndr:v6hzfv` governs, or the milestone, cycle and initiative layers.

## Commitments

- The `linear` skill, `linear-ops` and `pm:breakdown` pick a project by the three-step rule above, and never by "the one non-completed active project" or by asking once.
- No skill or agent creates or requires a standing Parking Lot project, and none requires one project per phase.
- `pm:groom` does not list "no project" under Missing fields. It flags only an unhomed ticket: one with neither a project nor a repo or area label, so neither a project nor the saved view that queries a repo or area label finds it.
- `pm:groom` step 3 pulls the backlog by team, not only from one active project.
- One policy applies in every repo and workspace: there is no per-repo or per-workspace setting that restores the strict one-project rule.

## Revisit if

- A workspace this marketplace serves asks for the strict rule, where every ticket must carry a project.
- Linear adds a first-class ongoing or never-ending project type that its own guidance recommends for maintenance work.
- Label-homed tickets start going unfound in practice, for example `pm:groom` keeps flagging the same unhomed tickets because callers skip the label.

## Context

- On 2026-11-12 the clr work was re-split along Linear's own guidance: three projects with an outcome and an end cover the clr work, and 9 ongoing clr tickets have no project and are found by the "clr backlog" saved view. The workspace had about 10 active projects and no Parking Lot project at the time.
- Linear's Projects FAQ ("Can I make a project for ongoing work?") and its "Managing unplanned work" guide (Triage, a Bug label and saved views, no project) recommend no project for work with no end.
- Before this decision the plugins assumed a stricter rule: `plugins/pm/references/layer-policy.md` called no-project "not a legal parked state" and prescribed a Parking Lot project and one project per phase; `plugins/pm/references/issue-shape.md` #2 required the active phase project; `plugins/pm/skills/groom/SKILL.md` flagged no project under Missing fields and filtered step 3 by "the active project"; `plugins/pm/skills/breakdown/SKILL.md` step 7 and the `linear` skill's "Team and project" section picked "the non-completed active project"; `linear-ops` stopped on `project: active` when several projects were non-completed; `pm:retro` wrote the retro into "the active project"; `plugins/linear/references/mcp-gotchas.md` §6 described an incident in terms of the Parking Lot project.
- No earlier atom backed the phase or Parking Lot rule. `ndr:v6hzfv` says in its Scope that projects "have their own layer rules"; this atom is that rule. `ndr:rw9nyx` is the per-repo tracker config precedent that this atom declines to extend.

## Why

The old picker cannot run. A picker must return exactly one project, but "the non-completed active project" is a query that returns every active project, and with about 10 active it returns about 10, so the rule has no answer and `linear-ops` stops. Requiring a project on every ticket then forces a write with no correct target, which is why a Parking Lot project existed: a dumping ground that satisfies the check and records nothing. A repo or area label plus a saved view homes ongoing work without that: a view is a query that finds a ticket by its repo or area label, so the ticket is found with no project set. The three-step rule always returns exactly one answer, either a named or owning project or none, and a ticket with no project and no repo or area label is found by neither a project nor the saved view that queries that label, which is exactly the unhomed ticket `pm:groom` flags.

## Alternatives

- **Keep the phase project plus a standing Parking Lot** — rejected: the picker still returns one project per active phase, and the Parking Lot is a project with no outcome, which Linear's guidance advises against.
- **A config knob that restores the strict rule per repo or workspace** — rejected: no workspace has asked for it, and one policy keeps every skill's behaviour predictable; reopen via the Revisit-if trigger.
- **Put every bug in the active project** — rejected: it repeats the original diagram's mistake, filing unrelated bugs under an outcome they do not advance and again needing one active project to exist.
- **Keep even project-caused bugs outside the project and link them** — rejected: the operator chose to keep a bug in a project's own work, such as a regression in a feature it shipped, inside that project.
