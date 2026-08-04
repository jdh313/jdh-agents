---
name: breakdown
description: >-
  Decompose a goal, plan, spec, or vault note into independently-grabbable
  Linear tickets using tracer-bullet vertical slices. This skill should be used
  when the user invokes `/pm:breakdown`, says "break this down", "slice this
  up", "decompose this", "convert this plan to tickets", "to issues", "make
  tickets for this", or signals that a larger goal needs to become a set of
  smaller actionable tickets. Optionally grounds against current ndr heads
  before slicing, conforms each ticket body to `references/issue-shape.md`,
  publishes in dependency order via the linear plugin with native Linear
  blocks/blocked-by relations, and optionally recommends a spec-flow contract
  for slices large enough to merit one. Slices land in Backlog with default
  priority — cycle assignment is `pm:groom`'s job.
argument-hint: >-
  [source — TEAM-N ticket, vault note path, ndr:atom-id, file path; falls back
  to conversation]
allowed-tools:
  - mcp__linear-server__list_issues
  - mcp__linear-server__get_issue
  - mcp__linear-server__list_issue_labels
  - mcp__linear-server__list_issue_statuses
  - mcp__linear-server__list_projects
  - mcp__linear-server__save_issue
  - mcp__obsidian-mcp__search_notes
  - mcp__obsidian-mcp__read_multiple_notes
  - Read
  - Grep
  - Glob
  - Bash(ndr *)
  - Skill
  - Agent
---

# breakdown

## Overview

Decompose a goal / plan / spec / vault note into independently-grabbable Linear tickets using **vertical slices** — tracer bullets that cut through every layer end-to-end, not horizontal slices of one layer. Optionally grounds the breakdown against current ndr heads first so slices don't conflict with settled architecture. Publishes in dependency order via the linear plugin with native Linear blocks/blocked-by relations.

This is the multi-ticket-from-a-plan skill. For one-shot single-ticket drafting, use `pm:author` (when it ships).

## The parent is a mutable contract (spec-flow interop)

When the source is a spec-flow contract, breakdown grows it into a **nested contract tree** — one shape, nested (ndr `k7vepz`). The parent is a **normal contract at change altitude** (full front-matter + working-matter), **not** a read-only front-matter-only spec:

- **Transition (single → breakdown).** When a lean contract outgrows single scope, running `/pm:breakdown` on it makes the contract *become* the parent — it keeps its front-matter and its change-altitude Decision log; breakdown only spawns the slices. No worksheet is shed, no host teardown. Each substantial slice is its own contract with a pointer back to the parent.
- **Decision altitude (duplication rule).** Whole-change and cross-slice decisions live in the **parent's** Decision log; slice-local decisions live in the **slice's**. A decision belongs to exactly one log — placement is author judgment as slices are drafted; `spec-flow:close` flags only literal cross-log duplication at parent-close.
- **Parent stays live.** The parent has its own amend discipline (a breakdown's whole-change *Done when* can legitimately change mid-flight) and is **closed last** — after every child slice — so `spec-flow:close` can harvest its integration / whole-change decisions. breakdown itself does not close or transition it; it just publishes the children and (for a `TEAM-N` source) wires the parent relations.
- **Host follows fill.** The parent may **stay a Linear issue with child issues** (a Linear Document is an optional static-home preference, not required), or be a `.docs/` parent file with Linear child issues. **Boundary:** an all-`.docs` breakdown (file parent + file children) has no skill — breakdown always publishes **Linear** children. A `.docs/` parent is fine; its slices land as Linear tickets.
- **Fog is the parent's, and this skill owns it.** A breakdown charts what you can see now; `## Not yet specified` on the parent holds what you can't (contract template v2.2). breakdown writes it while slicing and graduates it on re-entry (see *Graduating fog* below). `spec-flow:close` drains whatever never graduated, at parent-close.

## Inputs

- **Source (optional argument):** A `TEAM-N` ticket (parent), vault note path, `ndr:<atom-id>`, or file path. Falls back to conversation context.
- **Linear team:** `TEAM` — substitute your team key.
- **Issue shape spec:** `../../references/issue-shape.md` — body template each child ticket conforms to.
- **Layer policy:** `../../references/layer-policy.md` — decides milestone assignment for each child ticket. Defaults to an existing milestone; only proposes a new milestone if the slice is a genuinely new capability with a "done as a unit" moment. Subissue nesting and epic parents are off by default per this policy.
- **ndr atoms root:** `~/Loose Ends/Decisions/` — grounded via `ndr:ground` before slicing. Skip without the external `ndr` plugin.
- **Codebase root:** the current working repo — for optional exploration when slices touch tracked areas.

## Procedure

1. **Gather context.** Read the conversation. If an argument was passed, read the source fully:
   - `TEAM-N` — fetch it from Linear. Record as the **parent ticket** for later linking.
   - Vault note path — read it from the vault.
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
   - **Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change — a column rename, a retyped shared symbol — whose blast radius fans across the whole codebase, so a single edit breaks call sites everywhere at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand -> migrate -> contract**: an **expand** slice adds the new form beside the old so nothing breaks yet; one or more **migrate** slices move call sites over in batches sized by blast radius (per package, per directory), each batch its own slice blocked by the expand slice via Linear's native blocks/blocked-by relation, keeping CI green batch to batch because the old form still exists; a final **contract** slice deletes the old form once no caller remains, blocked by every migrate batch. If even the batches can't stay green alone, keep the sequence but give the migrate/contract slices a shared integration branch, with all of them blocking a final integrate-and-verify slice — green is promised only there. Each such migrate slice carries a **relative *Done when***: "call sites moved; end-to-end green promised at `<final slice>`". `spec-flow:close` honors this as **met-with-deferral**, not not-met; the final integrate-and-verify slice owns the cross-batch *Done when* and the integration Decision log.
   - **Decision-shaped slices count as a slice.** If the breakdown requires choosing between options before implementation can proceed, that's its own slice with `Decision` type label and `Done when: decision captured (as an ndr atom if you use ndr) and linked here`.
   - **Cross-cutting concerns** (auth, observability, schema migrations) often belong inside a slice, not as separate horizontal slices.
   - **Don't pre-slice what you can't yet phrase.** A slice needs a stateable question; the test is whether you can *phrase* it now, not whether you can *answer* it now — a sharp slice you can't start yet is still a slice, just a blocked one. What fails that test is fog, and it goes to the parent's `## Not yet specified` instead (step 7a). Forcing fog into ticket-shaped pieces is the failure this separation exists to prevent: a fog patch is coarser than a slice and may later become several, or none.

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
   - Set project: the active phase project (lookup in Linear, take the non-completed one).
   - Set parent relation if applicable.
   - **Assignee:** Omit `assignee` by default — breakdown produces independently-grabbable slices that either person can pull from the shared team queue. Set `assignee` only for slices the user explicitly pre-assigned during the quiz. (See the `linear` skill's collaboration conventions for the accept ritual.)
   - After save, capture the returned `TEAM-N` for downstream blocks/blocked-by references.

7a. **Write the fog to the parent** (parent-hosted breakdowns only). Anything the quiz surfaced that failed the phrase-it-now test goes to the parent's `## Not yet specified` — one line per patch, as loose as the view allows. Write it in the parent's own words, not sharpened; sharpening it here is the same mistake as ticketing it.

   Skip when there is no parent (vault / ndr / conversation source) — fog needs a home that outlives the session, and a parentless breakdown has none. Say so rather than inventing one: *"No parent to hold the fog — want me to make this a contract first?"*

   **If nothing is foggy, write nothing.** An effort whose way is fully visible doesn't need the section, and an empty one is noise at close.

8. **Flag spec-flow candidates.** After publishing, scan the published slices for ones that warrant a spec-flow contract — multi-day work, architectural negotiation needed, or contract-shaped (clear handoff between user and AI). For each candidate, recommend `/spec-flow draft` with the slice's `TEAM-N` as the contract host.

## Graduating fog (re-entry on an existing parent)

Running `/pm:breakdown` on a parent that **already has slices** is the graduation pass, not a re-slice. `spec-flow:close` recommends it after a slice closes that appears to have sharpened something.

1. **Read the parent**, including `## Not yet specified` and the closed slices' resolutions.
2. **Test each patch against the frontier.** A patch graduates when its question can now be *stated* — not when it can be answered. Report which patches moved and which are still fogged; don't force one.
3. **Slice the graduated patches only.** Run steps 4–7 against those patches alone. Leave the rest of the map untouched: existing slices are not re-cut, and their relations are not rewired.
4. **Clear each graduated patch** from the parent's `## Not yet specified` as its slices publish, so the patch lives in exactly one place — its slices. A patch that graduated into nothing (the resolution dissolved it) is cleared too, with a one-line note on why.
5. **New fog is allowed.** A resolution often reveals fog that wasn't visible before; append it in the same pass.

If no patch graduated, say so and change nothing. A pass that moves nothing is a normal outcome, not a failure.

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

- **Creating-only during the breakdown operation.** breakdown spawns child slices; it does not close, transition, or rewrite existing tickets as it runs. This is a rule about *this operation*, not a claim that the parent is a frozen artifact — see *The parent is a mutable contract* above (just under the Overview).
- **Never mutate existing tickets' content** — only create new ones and (when the source is a spec-flow parent) attach child relations. **One carve-out: the parent's `## Not yet specified` section**, which this skill owns end-to-end — writing patches while charting, clearing them as they graduate. Nothing else in the parent body is breakdown's to touch, and no *slice* body ever is.
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
- **`spec-flow:close`** (spec-flow plugin) — the other half of the fog loop. On a slice close it notices sharpened fog and recommends the graduation pass back here; at parent-close it drains whatever never graduated. This skill never closes anything.
- **`Explore` agent** (built-in) — optional codebase exploration in step 3.

## See also

- **`references/issue-shape.md`** — body template each published ticket conforms to.
- **`references/layer-policy.md`** — milestone-assignment criteria; epic-parent earn-it rule; subissue default-off stance.
- **`groom`** skill in this plugin — pulls breakdown's Backlog output into the cycle later.
- **Project `CLAUDE.md`** — repo conventions; the codebase shape that informs which layers a vertical slice touches.
