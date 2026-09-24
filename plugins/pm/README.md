# pm

> **Requires an Obsidian vault.** Skills in this plugin read and write notes in an
> Obsidian vault, defaulting to `~/Loose Ends/`. That default is an example, not a
> requirement — point it at your own vault by editing the paths in the skill bodies
> (search for `Loose Ends`). Without a vault, the vault-writing skills will not work.

PM helpers for solo or small-team development on a Linear workspace. Skills for the weekly grooming loop, charting an effort you cannot yet see the end of, plan-to-tickets breakdown, pulling a blocking decision out of someone else's head, and end-of-cycle retro notes.

## Premise

On a solo or small-team project you act as your own project manager. The PM work splits into a few recurring shapes — weekly grooming, charting, plan decomposition, end-of-cycle retro — each with its own cadence. This plugin gives each shape a skill so the routine is consistent and the proposals are auditable. All skills propose; transitions are applied manually via the `linear` plugin.

## Scope

- **Owns:** Grooming bucket taxonomy, retro note structure, breakdown slicing rules, the chart map shape and its charting/working loop, the discovery-questionnaire document shape, ticket-body template with done-when + optional `ndr:` refs.
- **Does NOT own:** Linear ticket creation conventions (defers to the `linear` plugin), decision atoms (defers to the external `ndr` plugin), vault writes (defers to the external `librarian` setup when present).
- **Currently scoped to:** a single Linear team, written as `TEAM` throughout.

## Skills

- **`lead`** — PM mode for a whole planning session. Reads the real state (project, open tickets, cited docs), measures before asserting, pushes back with evidence, and slices work into tickets good enough to hand off cold. Confirms every Linear write and routes it through `linear-ops`. Never codes, dispatches, or moves a ticket to In Progress — the `em` plugin's `em:lead` executes what it produces. Splits a merge-together change too big for one session into subissues, per `references/layer-policy.md`.
- **`groom`** — Weekly backlog grooming sweep. Scans active cycle + backlog, optionally cross-refs ndr atoms and vault session notes, outputs a bucketed punch list and archives it to the cycle's recurring grooming child issue. Forward-looking.
- **`retro`** — End-of-cycle retro note. Pulls the just-closed cycle, classifies tickets (shipped / carried / canceled / added-mid-cycle), surfaces patterns across recent cycles, and writes a retro to a Linear document by default (shared visibility), with an optional personal vault copy. Backward-looking. Pairs with `groom` on the same weekly cadence.
- **`breakdown`** — Decompose a goal / plan / spec into independently-grabbable Linear tickets using tracer-bullet vertical slices. Grounds against current ndr heads when the ndr plugin is present, publishes in dependency order with native Linear blocks/blocked-by relations, recommends a spec-flow contract for large slices. Parent-aware. Slices land in Backlog — cycle assignment is `groom`'s job.
- **`chart`** — Chart an effort too large to see the end of as a map ticket plus `Decision` / `Spike` / `Chore` question tickets in Linear, then resolve them one per session until the route is clear. Names the destination first, wires native blocks/blocked-by so the frontier renders in Linear's UI, and routes each resolution to an ndr atom. Charts *questions*; `breakdown` slices *work*.
- **`to-questionnaire`** — Turn a decision you cannot answer alone into a Markdown questionnaire for one person to fill in async. Interviews you only about the send — who it goes to, what you need back — then writes questions aimed at the gap, and routes the answers back to a decision atom, a ticket, or the `chart` ticket they unblocked.

### How they chain

```
chart  →  breakdown  →  spec-flow / clearance
 charts        slices          implements
```

`chart` handles a goal whose shape is still fogged; `breakdown` handles one you can already name the parts of. The boundary test is whether you can list the work, or only the questions. `to-questionnaire` sits off to the side of both: it is what you reach for when the blocker is another person's knowledge.

Planned for later versions:

- `triage` — single-issue analysis with proposed state / priority / labels / done-when
- `author` — single-ticket drafting (one-shot complement to `breakdown`'s multi-ticket case)

## References

- **`references/issue-body.md`** — what goes *inside* a ticket body: five slots (a one-line aim, then `## Why now`, `## Sketch`, `## Done when`, `## Context`), with per-type fill guidance. Tracker-agnostic by construction — the same slots apply in Linear, Fibery, or anywhere else — and it is the single source of truth for ticket bodies across this marketplace. The `linear` plugin carries no template of its own.
- **`references/issue-shape.md`** — what a well-formed ticket carries *around* the body (required fields + anti-conventions). `groom` uses it for the Missing-fields and NDR-moot buckets. Defers to `linear` for title/label/priority/status mechanics.
- **`references/layer-policy.md`** — what organizational layers the workspace uses (project / milestone / issue / cycle), when to split a ticket into one level of subissues, what layers are deliberately off by default (epic / parent ticket, initiative), and the decision criteria for promoting work between layers. Used by `groom` to flag orphan tickets, by `breakdown` to decide milestone assignment, and by `retro` to surface layer-policy adherence.

## Composes with

- **[linear](../linear/README.md)** — `pm` skills propose; `linear` applies any approved transitions. `linear` also owns the Spike-vs-Decision boundary test that `chart` uses to type its map tickets.
- **craft** (`../craft/`) — `pm:chart` resolves its tickets through `craft:grill`, `craft:domain-modeling`, `craft:grill-with-docs`, and `craft:prototype`. Without craft, `chart` still charts and publishes, but each ticket is resolved by plain conversation.
- **[spec-flow](../spec-flow/README.md)** — owns the canonical fog-of-war definition (`references/contract-template.md`) that `chart` and `breakdown` both apply, and receives the handoff once a map's route is clear.
- **ndr** (external — ships from its own separate marketplace) — `pm:groom` calls `ndr:decisions` for supersession checks on tickets that reference ndr atoms. Optional: without it, the NDR-moot bucket and grounding passes are skipped.
- **librarian** (external — personal setup, not published) — `pm:retro`'s primary output is a Linear document; when librarian is present, an optional personal vault copy is written via its `note-editor` agent. Without librarian, that optional copy stays in chat for you to file manually.

## Assumptions

Like `linear` and `spec-flow`, this plugin assumes a particular environment and degrades gracefully without it:

- A single Linear team, written as `TEAM` in examples — substitute your team key.
- Weekly Linear cycles. Examples assume a Thu→Wed cycle with a Thursday-morning review; adjust to your workspace's cycle settings.
- An Obsidian vault (default `~/Loose Ends/`) holding per-project session notes and, if you use ndr, decision atoms under `Decisions/`. Without a vault, the vault-unfiled bucket in `groom` and the session-note passes in `retro` are skipped.

## Credits

- **`breakdown`** — Adapted from the `to-issues` skill in [`mattpocock/skills`](https://github.com/mattpocock/skills); upstream has since merged `to-issues` with `to-plan` into `to-tickets`. Adaptations applied during port: ndr grounding pre-pass, body template conforming to `references/issue-shape.md`, native Linear blocks/blocked-by relations, the parent-ticket-linking mechanic (Linear `parent` relation + confirm-before-publish), `Decision`-type slice handling with a capture-decision follow-up, and optional spec-flow handoff for contract-shaped slices. The HITL/AFK label split from the source skill was considered and deferred. Reconciled against `to-tickets` on 2026-07-09 (see `skills/breakdown/UPSTREAM.md`): adopted wide-refactor (expand-contract) sequencing and re-added a dropped prefactoring line.
- **`wayfinder`** — Adapted from the `wayfinder` skill in [`mattpocock/skills`](https://github.com/mattpocock/skills) (MIT, © 2026 Matt Pocock), first intake 2026-08-29. Adaptations applied: Linear as the fixed tracker (upstream is tracker-agnostic), the map as the parent of its tickets via native subissues, as upstream has it, upstream's four ticket types mapped onto the existing `Spike` / `Decision` / `Chore` label set instead of bespoke `wayfinder:*` labels, resolutions routed to ndr atoms, a confirm-before-publish gate, and an explicit map-close step that hands remaining fog to the successor contract. The fog-of-war model is **cited, not re-imported** — this marketplace already adopted it into `spec-flow`'s contract template (v2.2) ahead of the skill itself. See `skills/chart/UPSTREAM.md`.
- **`to-questionnaire`** — Adapted from the `to-questionnaire` skill in [`mattpocock/skills`](https://github.com/mattpocock/skills) (MIT, © 2026 Matt Pocock), first intake 2026-08-29. The send interview and document template are kept as upstream wrote them; adaptations are the `.docs/` output path, an optional shared Linear/vault copy, and routing of returned answers to `ndr:capture-decision`, `spec-flow:capture`, `pm:breakdown`, or the `wayfinder` ticket they unblocked. See `skills/to-questionnaire/UPSTREAM.md`.

Both new skills are **model-invocable here**, where upstream marks them explicit-invocation-only — pm skills in this marketplace are reachable by sibling skills by convention, and the restraint is carried by explicit confirm gates instead. Recorded in each skill's ledger.
