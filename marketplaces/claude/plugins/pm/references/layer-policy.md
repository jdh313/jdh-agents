# Linear layer policy

What organizational layers the workspace uses (project, milestone, issue, cycle), what layers are deliberately off by default (epic / parent ticket, subissue), and the decision criteria for promoting work between layers. Source of truth for `pm:groom`, `pm:breakdown`, and `pm:retro` when they need to decide where a ticket sits.

Companion to `references/issue-shape.md` (per-ticket structure). This file covers the layers **around** tickets; `issue-shape.md` covers what goes **inside** a ticket.

## Load-bearing rule

**Three structural layers, one time-box.** Active layers:

1. **Project** — the phase (e.g. a 60-day block of scoped work). One project per phase, plus a standing **Parking Lot** project for parked tickets. Each new phase gets its own project.
2. **Milestone** — a capability slice within the project with a "done as a unit" moment (e.g. `Auth perimeter`, `CI/CD from GitHub`, `Data Model`, `CRUD UI`). Linear orders these in the UI.
3. **Issue** — the work unit. Always flat under its milestone.
4. **Cycle** — weekly time-box, orthogonal to scope.

Inactive layers (default off):

- **Initiative** — deferred until there are ≥2 active projects.
- **Epic / parent ticket** — earn-it only (see promotion criterion below). Default off.
- **Subissue** — not retired, not adopted; the default is flat siblings under a shared milestone, no nesting. Revisit only when a big milestone mid-flight makes the grouping question live.

## Why so few layers

Industry consensus for small / solo teams: **too many layers create administrative bloat with no operational payoff.** The natural shape for a single-developer team is Linear's intended 3-layer model (Project → Milestone → Issue) plus the cycle time-box.

Layers above issue answer the question *"what scope group does this belong to?"* You only need as many of those as you actually slice along. A solo project typically slices along capability (auth, CI/CD, data model, CRUD UI) — that's milestone. Below issue, nesting (subissues, sub-sub-issues) adds tree depth without buying scope clarity that flat siblings + a shared milestone don't already give.

## Decision criteria

### What goes in a project

One project per phase. Reasoning: stakeholders greenlight phases as units; archival on phase close keeps current views clean; phase-as-project keeps issue counts navigable.

A long-lived "whole product = one project" shape was considered and rejected — it flattens the scope grain to labels and clutters views as phases accumulate.

### What goes in a milestone

A milestone is a **capability slice with a real "done as a unit" moment**. The criterion: there's a single integration point where the milestone's tickets compose into a working capability (e.g., "auth works end-to-end in dev" for `Auth perimeter`, "CRUD screens for all core entities" for `CRUD UI`).

If the grouping is just a tag — flat classification with no shared integration moment — use a label, not a milestone. Labels are flat; milestones have ordering, progress, and target dates.

Entity slices (one milestone per domain entity) are the common alternative shape; in practice solo work tends to decompose along capabilities instead. If per-entity progress becomes a live ask, add `entity:*` labels rather than restructuring milestones.

### What goes in an issue

Per `references/issue-shape.md`. The unit of work that ships in one or a few cycles. Issues are always **flat siblings under their milestone** — no parent/subissue nesting.

### What goes in a cycle

The week's commit batch. Cycles are scope-agnostic — they pull from whichever milestones are active. A single cycle routinely spans 4–5 milestones; a single milestone routinely spans 3+ cycles. See `groom/SKILL.md` for the weekly pull/push mechanics.

### When to add a parent ticket (epic) — earn-it

**Default off.** Add a parent ticket only when an epic meets **all** of these:

1. **≥5 tickets** in the epic (small epics don't earn the overhead).
2. **Has its own design substrate** — an ndr cluster (≥2 atoms), a vault design doc, or a Linear document. The substrate is what *needs a home* on the parent's description body.
3. **Generates cross-ticket discussion** — comment threads that would otherwise be scattered across siblings or chat.

Pass all three: add a parent ticket. Default shape is **sibling parent** — a regular ticket linked to its children via `relatedTo` or `blocks`, not via Linear's `parentId` (which creates a subissue tree).

A parent ticket that earns its keep also serves as the **async-discussion venue** for children that span both collaborators. When children are split across people, the parent's comment thread is the canonical coordination point rather than ad-hoc chat — link the parent when handing off or requesting cross-review.

Whether to instead use Linear's native subissue nesting (`parentId`) is **deferred** — see "Subissue" in the inactive-layers list above. Until the question is live, default to the sibling-parent shape if a parent is warranted at all.

If the proposed epic fails any criterion: stay flat under the milestone, file an ndr atom or vault note for design substrate if needed, and live with the milestone's progress bar as the only grouping signal.

### Per-person capacity (lightweight)

Keep per-person WIP visible at a glance during grooming. The target is a low-overhead proxy, not a full capacity model:

- Track in-progress + todo counts per assignee (the WIP map in `pm:groom`'s output does this automatically).
- A person carrying ≥3 in-progress tickets is likely over capacity — `pm:groom` flags pull-in candidates as "ready for anyone" vs "blocked on @person" to surface this.
- Unassigned tickets in the backlog are the shared team queue; neither person is implicitly responsible until one of them accepts (see the `linear` skill's accept ritual).
- No formulas, no velocity math — the goal is to make imbalances visible so the team can redistribute voluntarily.

### When to add an initiative

When a second active project lands. Until then, deferred.

## Legal states for a ticket

The orthogonal-axes mental model:

- **Project + milestone + cycle** = actively committed (normal active state)
- **Project + milestone, no cycle** = backlog (scoped, not yet pulled)
- **Project, no milestone, no cycle** = parked in-project (explicit phase stretch / known-deferred)
- **Parking Lot project, no milestone, no cycle** = parked out-of-project (future-phase work). Bare no-project is **not** a legal parked state — the Linear MCP `save_issue` tool has no project-removal path anyway (see the `linear` plugin's `references/mcp-gotchas.md` § 6), so parked tickets are reassigned to the Parking Lot project instead.
- **No milestone, in cycle** = ❌ orphan. `pm:groom` flags these as Missing-fields.

## Composes with

- **`references/issue-shape.md`** — per-ticket structure.
- **`pm:groom`** — Missing-fields bucket uses the legal-states table above. Orphans (no milestone, in cycle) get surfaced for backfill.
- **`pm:breakdown`** — when slicing a goal into tickets, decide milestone assignment per "What goes in a milestone" above. Default to existing milestones; only propose a new one if the slice is a genuinely new capability with a "done as a unit" moment.
- **`pm:retro`** — cycle retros surface "did we honor the layer policy?" — any orphans landed, any subissue temptations resisted, any epic that earned its keep.

## See also

- **`linear`** (linear plugin) — title, labels, priority, status flow, and milestone-naming mechanics.
- **Project `CLAUDE.md`** — when to open a ticket at all.
