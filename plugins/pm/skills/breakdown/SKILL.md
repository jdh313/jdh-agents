---
name: breakdown
description: >-
  Decompose a goal, plan, spec, or vault note into independently-grabbable
  Linear tickets using tracer-bullet vertical slices. This skill should be
  used when the user invokes `/pm:breakdown`, says "break this down", "slice
  this up", "decompose this", "convert this plan to tickets", "to issues",
  "make tickets for this", or signals that a larger goal needs to become a
  set of smaller actionable tickets. Optionally grounds against current ndr
  heads before slicing, conforms each ticket body to
  `references/issue-shape.md`, publishes in dependency order via the linear
  plugin with native Linear blocks/blocked-by relations, and optionally
  recommends a spec-flow contract for slices large enough to merit one.
  Slices land in Backlog with default priority — cycle assignment is
  `pm:groom`'s job.
argument-hint: "[source — TEAM-N ticket, vault note path, ndr:atom-id, file path; falls back to conversation]"
allowed-tools:
  # Linear — read parent + publish children + wire relations
  - mcp__linear-server__list_issues
  - mcp__linear-server__get_issue
  - mcp__linear-server__list_issue_labels
  - mcp__linear-server__list_issue_statuses
  - mcp__linear-server__list_projects
  - mcp__linear-server__save_issue
  # Obsidian — read source if it's a vault note
  - mcp__obsidian-mcp__search_notes
  - mcp__obsidian-mcp__read_multiple_notes
  # ndr atoms + codebase exploration (optional)
  - Read
  - Grep
  - Glob
  - Bash(ndr *)
  # Compose with ndr:ground, linear, spec-flow:draft
  - Skill
  - Agent
upstream:
  repo: mattpocock/skills
  path: skills/engineering/to-tickets
  reviewed_sha: d29732e49f60
  reviewed: 2026-07-09
  status: reviewed
---

# breakdown

## Overview

Decompose a goal / plan / spec / vault note into independently-grabbable Linear tickets using **vertical slices** — tracer bullets that cut through every layer end-to-end, not horizontal slices of one layer. Optionally grounds the breakdown against current ndr heads first so slices don't conflict with settled architecture. Publishes in dependency order via the linear plugin with native Linear blocks/blocked-by relations.

This is the multi-ticket-from-a-plan skill. For one-shot single-ticket drafting, use `pm:author` (when it ships).

## Inputs

- **Source (optional argument):** A `TEAM-N` ticket (parent), vault note path, `ndr:<atom-id>`, or file path. Falls back to conversation context.
- **Linear team:** `TEAM` — substitute your team key.
- **Issue shape spec:** `../../references/issue-shape.md` — body template each child ticket conforms to.
- **Layer policy:** `../../references/layer-policy.md` — decides milestone assignment for each child ticket. Defaults to an existing milestone; only proposes a new milestone if the slice is a genuinely new capability with a "done as a unit" moment. Subissue nesting and epic parents are off by default per this policy.
- **ndr atoms root:** `~/Loose Ends/Decisions/` — grounded via `ndr:ground` before slicing. Skip without the external `ndr` plugin.
- **Codebase root:** the current working repo — for optional exploration when slices touch tracked areas.

## Procedure

1. **Gather context.** Read the conversation. If an argument was passed, read the source fully:
   - `TEAM-N` — fetch via `mcp__linear-server__get_issue`. Record as the **parent ticket** for later linking.
   - Vault note path — read via `mcp__obsidian-mcp__read_multiple_notes`.
   - `ndr:<atom-id>` — dispatch `Skill(ndr:decisions)` to resolve the head.
   - File path — `Read` it.

2. **Ground against ndr heads** (skip without the external `ndr` plugin). Dispatch `Skill(ndr:ground)` against the goal's area (auth, backend framework, frontend, infra, etc.). Surface the current decision heads relevant to the breakdown. Use them to:
   - Avoid proposing slices that conflict with active decisions
   - Avoid duplicating settled choices
   - Recognize when a slice IS a decision point (gets the `Decision` type label)

3. **Explore codebase (optional).** If implementing in a tracked area and unfamiliar with the current state, dispatch the `Explore` agent with a tightly-scoped question. Skip when the source already grounds you sufficiently. Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

4. **Draft vertical slices.** Follow these rules:

   - Each slice delivers a **narrow but COMPLETE path** through every layer the change touches (schema → API → UI → tests, or whichever subset applies).
   - A completed slice is **demoable or verifiable on its own**.
   - **Many thin slices > few thick ones.** When in doubt, split.
   - **Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change — a column rename, a retyped shared symbol — whose blast radius fans across the whole codebase, so a single edit breaks call sites everywhere at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand -> migrate -> contract**: an **expand** slice adds the new form beside the old so nothing breaks yet; one or more **migrate** slices move call sites over in batches sized by blast radius (per package, per directory), each batch its own slice blocked by the expand slice via Linear's native blocks/blocked-by relation, keeping CI green batch to batch because the old form still exists; a final **contract** slice deletes the old form once no caller remains, blocked by every migrate batch. If even the batches can't stay green alone, keep the sequence but give the migrate/contract slices a shared integration branch, with all of them blocking a final integrate-and-verify slice — green is promised only there.
   - **Decision-shaped slices count as a slice.** If the breakdown requires choosing between options before implementation can proceed, that's its own slice with `Decision` type label and `Done when: decision captured (as an ndr atom if you use ndr) and linked here`.
   - **Cross-cutting concerns** (auth, observability, schema migrations) often belong inside a slice, not as separate horizontal slices.

5. **Quiz the user.** Present the proposed slices as a numbered list. For each slice show:

   ```
   N. <Title>
      Surface:     <pipeline | backend | frontend | infra | database>
      Type:        <Feature | Improvement | Chore | Docs | Decision>
      Blocked by:  <slice #s, or "none — can start immediately">
      Assigned to: <unassigned — shared queue | @person if pre-assigned>
      Why a slice: <one line — what end-to-end path this cuts>
   ```

   Ask the user:
   - Does the granularity feel right? (Too coarse / too fine.)
   - Are the dependency relationships correct?
   - Should any slices be merged or split further?
   - Any slice that should be `Decision` type rather than `Feature`?
   - Any slice to pre-assign? (Default is unassigned — either person can pick it up.)

   Iterate until the user approves the breakdown.

6. **Confirm parent linking.** If the source was a `TEAM-N` ticket, each child will get a Linear `parent` relation pointing at it. Confirm the parent ID once before publishing. If the source was vault/ndr/conversation, no Linear parent — each child's `## Context` describes the goal directly (link to vault note or ndr atom if applicable).

7. **Publish in dependency order via `linear`.** Save blockers first so children can reference real `TEAM-N` IDs in the Linear blocks/blocked-by relation. For each slice:

   - Compose body per `references/issue-shape.md`: `## Context`, `## Done when:`, `## NDR references` (if any), `## Notes` (if any).
   - Set labels: one Surface, one Type. Defaults: `Feature` type unless decision-shaped (`Decision`). Surface comes from the slice's primary layer.
   - Set priority: `medium` (Backlog default per the `linear` skill). Bump to `high` only when the user explicitly committed to the slice this cycle.
   - Set project: the active phase project (lookup via `mcp__linear-server__list_projects`, take the non-completed one).
   - Set parent relation if applicable.
   - **Assignee:** Omit `assignee` by default — breakdown produces independently-grabbable slices that either person can pull from the shared team queue. Set `assignee` only for slices the user explicitly pre-assigned during the quiz. (See the `linear` skill's collaboration conventions for the accept ritual.)
   - After save, capture the returned `TEAM-N` for downstream blocks/blocked-by references.

8. **Flag spec-flow candidates.** After publishing, scan the published slices for ones that warrant a spec-flow contract — multi-day work, architectural negotiation needed, or contract-shaped (clear handoff between user and AI). For each candidate, recommend `/spec-flow draft` with the slice's `TEAM-N` as the contract host.

## Quiz format (worked example)

For a hypothetical "Wire up the customer search page" goal, the skill might propose:

```
1. Customer search: list endpoint + search params
   Surface:     backend
   Type:        Feature
   Blocked by:  none — can start immediately
   Assigned to: unassigned — shared queue
   Why a slice: GET /customers?q= returning a typed page model; unit tests on filter logic; no UI yet

2. Customer search: route + table component
   Surface:     frontend
   Type:        Feature
   Blocked by:  #1
   Assigned to: unassigned — shared queue
   Why a slice: TanStack Router + Table page at /customers, calls #1's endpoint via openapi-fetch

3. Customer search: empty / loading / error states
   Surface:     frontend
   Type:        Improvement
   Blocked by:  #2
   Assigned to: unassigned — shared queue
   Why a slice: thin polish slice; demoable on its own with mocked responses

Granularity right? Dependencies correct? Anything to merge or split? Anyone to pre-assign?
```

## Rules

- **Never close, modify, or transition the parent ticket.** Read-only on the source.
- **Never mutate existing tickets** — only create new ones. The skill is creating-only.
- **Confirm before publishing.** Show the user the final ordered list once more before any ticket is created. Publishing is the only destructive step in this skill.
- **Decision-type slices** get `Done when: decision captured and linked here`. After the call is made, recommend `Skill(ndr:capture-decision)` if the ndr plugin is present.
- **Cycle assignment is not breakdown's job.** Slices land in Backlog. `pm:groom` pulls them into a cycle later.
- **Skip horizontal-slice anti-patterns.** Never propose "do all schema work first, then all API work, then all UI work" as three slices — that's a layer-by-layer plan, not tracer bullets.
- **Avoid file paths or code snippets in issue bodies.** They go stale. Exception: a prototype-derived snippet that encodes a decision more precisely than prose (state machine, schema, type shape) — inline the decision-rich parts only, with a note that it came from a prototype.

## Composes with

- **`ndr:ground`** (external ndr plugin — ships from its own separate marketplace) — grounding pass before slicing. Surfaces current decision heads relevant to the goal's area. Optional: without it, slice from the source + conversation alone.
- **`ndr:decisions`** (external ndr plugin) — used when the source argument is an `ndr:` reference.
- **`ndr:capture-decision`** (external ndr plugin) — recommended after a `Decision`-type slice's call is made.
- **`linear`** (linear plugin) — performs the actual ticket saves with team conventions (labels, priority semantics, title shape).
- **`spec-flow:draft`** (spec-flow plugin) — optional handoff for slices that warrant a contract-tracked workflow, via `/spec-flow draft`.
- **`Explore` agent** (built-in) — optional codebase exploration in step 3.

## See also

- **`references/issue-shape.md`** — body template each published ticket conforms to.
- **`references/layer-policy.md`** — milestone-assignment criteria; epic-parent earn-it rule; subissue default-off stance.
- **`groom`** skill in this plugin — pulls breakdown's Backlog output into the cycle later.
- **Project `CLAUDE.md`** — repo conventions; the codebase shape that informs which layers a vertical slice touches.
