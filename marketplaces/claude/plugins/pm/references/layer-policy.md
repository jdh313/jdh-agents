# Linear layer policy

What organizational layers the workspace uses (project, milestone, issue, subissue, cycle), what layers are deliberately off by default (initiative, epic / parent ticket), and the decision criteria for promoting work between layers. Source of truth for `pm:groom`, `pm:breakdown`, and `pm:retro` when they need to decide where a ticket sits.

Companion to `references/issue-shape.md` (per-ticket structure). This file covers the layers **around** tickets; `issue-shape.md` covers what goes **inside** a ticket.

## Load-bearing rule

**Three structural layers, one nesting level, one time-box.** Active layers:

1. **Project** — the phase (e.g. a 60-day block of scoped work). One project per phase, plus a standing **Parking Lot** project for parked tickets. Each new phase gets its own project.
2. **Milestone** — a capability slice within the project with a "done as a unit" moment (e.g. `Auth perimeter`, `CI/CD from GitHub`, `Data Model`, `CRUD UI`). Linear orders these in the UI.
3. **Issue** — the work unit, under its milestone.
4. **Subissue** — a child of an issue via Linear's native `parentId`, one level deep. Used when a ticket is split into session-sized children, and for the children of an earned parent (see below).
5. **Cycle** — weekly time-box, orthogonal to scope.

Inactive layers (default off):

- **Initiative** — deferred until there are ≥2 active projects.
- **Epic / parent ticket** — earn-it only (see promotion criterion below). Default off.

## Why so few layers

Industry consensus for small / solo teams: **too many layers create administrative bloat with no operational payoff.** The natural shape for a single-developer team is Linear's intended 3-layer model (Project → Milestone → Issue) plus the cycle time-box.

Layers above issue answer the question *"what scope group does this belong to?"* You only need as many of those as you actually slice along. A solo project typically slices along capability (auth, CI/CD, data model, CRUD UI) — that's milestone. Below issue, one level of subissues buys something flat siblings do not: a change that must merge as a unit but is too big for one implementation session stays visibly one change, with Linear's own progress roll-up on the parent. Deeper nesting (sub-sub-issues) adds tree depth without that payoff, so it stays off.

## Decision criteria

### What goes in a project

One project per phase. Reasoning: stakeholders greenlight phases as units; archival on phase close keeps current views clean; phase-as-project keeps issue counts navigable.

A long-lived "whole product = one project" shape was considered and rejected — it flattens the scope grain to labels and clutters views as phases accumulate.

### What goes in a milestone

A milestone is a **capability slice with a real "done as a unit" moment**. The criterion: there's a single integration point where the milestone's tickets compose into a working capability (e.g., "auth works end-to-end in dev" for `Auth perimeter`, "CRUD screens for all core entities" for `CRUD UI`).

If the grouping is just a tag — flat classification with no shared integration moment — use a label, not a milestone. Labels are flat; milestones have ordering, progress, and target dates.

Entity slices (one milestone per domain entity) are the common alternative shape; in practice solo work tends to decompose along capabilities instead. If per-entity progress becomes a live ask, add `entity:*` labels rather than restructuring milestones.

### What goes in an issue

Per `references/issue-shape.md`. The unit of work that ships in one or a few cycles, under its milestone.

### When to split an issue into subissues

Split when the change should merge together but spans several surfaces, or will not fit one implementation session. The original ticket becomes the parent; each child is sized to one session and linked with `parentId`. No earn-it test applies: the split is justified by size, not by the parent's own weight. Children inherit the parent's milestone. Order between children is expressed with `blocks` / blocked-by, and the parent's body names the merge order.

One level only. A child that is itself too big gets split into more siblings under the same parent, or promoted to its own top-level issue when it no longer has to merge with the rest; never a grandchild. The reason is what reads the tree: Linear documents sub-issues one level deep (parent to direct children, with the parent's auto-close keyed to them), and integrations that walk sub-issues have been seen to drop grandchildren silently. A grandchild is a ticket that tooling can fail to find. Jira forbids children of sub-tasks outright, and ClickUp's own guidance is one level for most work.

### What goes in a cycle

The week's commit batch. Cycles are scope-agnostic — they pull from whichever milestones are active. A single cycle routinely spans 4–5 milestones; a single milestone routinely spans 3+ cycles. See `groom/SKILL.md` for the weekly pull/push mechanics.

### When to add a parent ticket (epic) — earn-it

**Default off.** Add a parent ticket only when an epic meets **all** of these:

1. **≥5 tickets** in the epic (small epics don't earn the overhead).
2. **Has its own design substrate** — an ndr cluster (≥2 atoms), a vault design doc, or a Linear document. The substrate is what *needs a home* on the parent's description body.
3. **Generates cross-ticket discussion** — comment threads that would otherwise be scattered across siblings or chat.

Pass all three: add a parent ticket. Its children are **native subissues** linked via `parentId`.

A parent ticket that earns its keep also serves as the **async-discussion venue** for children that span both collaborators. When children are split across people, the parent's comment thread is the canonical coordination point rather than ad-hoc chat — link the parent when handing off or requesting cross-review.

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
- **`pm:retro`** — cycle retros surface "did we honor the layer policy?" — any orphans landed, any nesting deeper than one level, any epic that earned its keep.

## See also

- **`linear`** (linear plugin) — title, labels, priority, status flow, and milestone-naming mechanics.
- **Project agent guidance** (`AGENTS.md` / `CLAUDE.md`) — when to open a ticket at all.
