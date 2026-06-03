# CartaOS Linear layer policy

What organizational layers CartaOS Linear uses (project, milestone, issue, cycle), what layers are deliberately retired (epic / parent ticket, subissue), and the decision criteria for promoting work between layers. Source of truth for `pm:groom`, `pm:breakdown`, and `pm:retro` when they need to decide where a ticket sits.

Companion to `references/issue-shape.md` (per-ticket structure). This file covers the layers **around** tickets; `issue-shape.md` covers what goes **inside** a ticket.

## Load-bearing rule

**Three structural layers, one time-box.** Active layers in CartaOS Linear:

1. **Project** — the 60-day phase. Today: `Phase 1 — Customer & Contract Modeling`. Phase 2 will get its own project.
2. **Milestone** — a capability slice within the project with a "done as a unit" moment. Today: `Demo: app running in AWS`, `CI/CD from GitHub`, `Auth perimeter`, `Data Model`, `CRUD UI`, `Customer Documentation + prototype`. Linear orders these in the UI; milestone names deliberately drop sequence prefixes (no M1/M2/…) because the work runs in parallel, not strict sequence.
3. **Issue** — the work unit. Always flat under its milestone.
4. **Cycle** — weekly time-box, orthogonal to scope. Thu→Wed cadence.

Inactive layers (committed-to in vault history but never adopted in practice):

- **Initiative** — deferred until Phase 2 lands and there are ≥2 active projects.
- **Epic / parent ticket** — earn-it only (see promotion criterion below). Default off.
- **Subissue** — deferred 2026-05-29; not retired, not adopted. The 2026-05-15 vault commitment to subissue nesting for Auth perimeter never got adopted (auth shipped as 9 flat siblings under the Auth perimeter milestone). The decision of whether to formally retire or re-adopt is parked until a future big milestone (`Data Model` or `CRUD UI` mid-flight) makes the grouping question live. Default behavior in the meantime: flat siblings, no nesting.

## Why so few layers

Industry consensus for small / solo teams: **too many layers create administrative bloat with no operational payoff.** The natural shape for a single-developer team is Linear's intended 3-layer model (Project → Milestone → Issue) plus the cycle time-box.

Layers above issue answer the question *"what scope group does this belong to?"* You only need as many of those as you actually slice along. CartaOS slices along capability (auth, CI/CD, data model, CRUD UI) — that's milestone. Below issue, nesting (subissues, sub-sub-issues) adds tree depth without buying scope clarity that flat siblings + a shared milestone don't already give.

## Decision criteria

### What goes in a project

One project per 60-day phase. Reasoning: Andrew greenlights phases as units; archival on phase close keeps current views clean; phase-as-project keeps issue counts navigable.

Long-lived `CartaOS = one project` was considered and rejected — it flattens the entity slice grain to labels and clutters views as phases accumulate. See vault note `Linear Setup — Project Granularity.md` for the full defense.

### What goes in a milestone

A milestone is a **capability slice with a real "done as a unit" moment**. The criterion: there's a single integration point where the milestone's tickets compose into a working capability (e.g., "auth works end-to-end in dev" for `Auth perimeter`, "CRUD screens for all four entities" for `CRUD UI`).

If the grouping is just a tag — flat classification with no shared integration moment — use a label, not a milestone. Labels are flat; milestones have ordering, progress, and target dates.

Entity slices (`Contracts`, `Case Counts`, `Hours`) were the original 2026-05-15 milestone shape per Andrew's build order. In practice the work decomposed along capabilities instead. The vault was updated 2026-05-29 to codify capabilities. If entity-slice progress becomes a live ask again, add `entity:*` labels rather than restructuring milestones.

### What goes in an issue

Per `references/issue-shape.md`. The unit of work that ships in one or a few cycles. Issues are always **flat siblings under their milestone** — no parent/subissue nesting.

### What goes in a cycle

The week's commit batch. Cycles are scope-agnostic — they pull from whichever milestones are active. A single cycle routinely spans 4–5 milestones; a single milestone routinely spans 3+ cycles. See `groom/SKILL.md` for the weekly pull/push mechanics.

### When to add a parent ticket (epic) — earn-it

**Default off.** Add a parent ticket only when an epic meets **all** of these:

1. **≥5 tickets** in the epic (small epics don't earn the overhead).
2. **Has its own design substrate** — an NDR cluster (≥2 atoms), a vault design doc, or a Linear document. The substrate is what *needs a home* on the parent's description body.
3. **Generates cross-ticket discussion** — comment threads that would otherwise be scattered across siblings or slack.

Pass all three: add a parent ticket. Default shape is **sibling parent** — a regular ticket linked to its children via `relatedTo` or `blocks`, not via Linear's `parentId` (which creates a subissue tree).

Whether to instead use Linear's native subissue nesting (`parentId`) is **deferred** — see "Subissue" in the inactive-layers list above. Revisit when `Data Model` or `CRUD UI` is mid-flight and the grouping question is live. Until then, default to the sibling-parent shape if a parent is warranted at all.

If the proposed epic fails any criterion: stay flat under the milestone, file an NDR atom or vault note for design substrate if needed, and live with the milestone's progress bar as the only grouping signal.

### When to add an initiative

When Phase 2 lands. Until then, deferred.

## Legal states for a ticket

The orthogonal-axes mental model:

- **Project + milestone + cycle** = actively committed (normal active state)
- **Project + milestone, no cycle** = backlog (scoped, not yet pulled)
- **Project, no milestone, no cycle** = parked in-project (explicit Phase 1 stretch / known-deferred)
- **Parking Lot project, no milestone, no cycle** = parked deliberately with no owning project (added 2026-06-05; the "Parking Lot" Linear project is a rolling holding pen following the Pipeline Cleanup pattern — exit = a real project claims the ticket; nothing executes from it)
- **No project** = ❌ unfiled. Previously a legal parked state ("no Phase 2 project exists yet"), retired 2026-06-05 once Phase 2 and Parking Lot existed — an out-of-project ticket is now indistinguishable from a forgot-to-file and gets flagged as Missing-fields.
- **No milestone, in cycle** = ❌ orphan. `pm:groom` flags these as Missing-fields.

## Composes with

- **`references/issue-shape.md`** — per-ticket structure.
- **`pm:groom`** — Missing-fields bucket uses the legal-states table above. Orphans (no milestone, in cycle) get surfaced for backfill.
- **`pm:breakdown`** — when slicing a goal into tickets, decide milestone assignment per "What goes in a milestone" above. Default to existing milestones; only propose a new one if the slice is a genuinely new capability with a "done as a unit" moment.
- **`pm:retro`** — cycle retros surface "did we honor the layer policy?" — any orphans landed, any subissue temptations resisted, any epic that earned its keep.

## See also

- **Vault: `Linear Setup.md`** — top-level decision rollup, decision #4 (project granularity), #5 (milestone semantics), #7 (cycle cadence).
- **Vault: `Linear Setup — Project Granularity.md`** — full project-vs-milestone defense.
- **Vault: `Linear Setup — Milestone Semantics.md`** — capability-slice vs entity-slice decision (revised 2026-05-29).
- **Vault: `Linear Setup — Cycles.md`** — Thu→Wed cadence (revised 2026-05-29).
- **CartaOS `CLAUDE.md`** § Linear workflow — when to open a ticket.
