# pm

PM helpers for solo or small-team development on a Linear workspace. Skills for the weekly grooming loop, plan-to-tickets breakdown, and end-of-cycle retro notes.

## Premise

On a solo or small-team project you act as your own project manager. The PM work splits into a few recurring shapes — weekly grooming, plan decomposition, end-of-cycle retro — each with its own cadence. This plugin gives each shape a skill so the routine is consistent and the proposals are auditable. All skills propose; transitions are applied manually via the `linear` plugin.

## Scope

- **Owns:** Grooming bucket taxonomy, retro note structure, breakdown slicing rules, ticket-body template with done-when + optional `ndr:` refs.
- **Does NOT own:** Linear ticket creation conventions (defers to the `linear` plugin), decision atoms (defers to the external `ndr` plugin), vault writes (defers to the external `librarian` setup when present).
- **Currently scoped to:** a single Linear team, written as `TEAM` throughout.

## Skills

- **`groom`** — Weekly backlog grooming sweep. Scans active cycle + backlog, optionally cross-refs ndr atoms and vault session notes, outputs a bucketed punch list and archives it to the cycle's recurring grooming child issue. Forward-looking.
- **`retro`** — End-of-cycle retro note. Pulls the just-closed cycle, classifies tickets (shipped / carried / canceled / added-mid-cycle), surfaces patterns across recent cycles, and writes a retro to a Linear document by default (shared visibility), with an optional personal vault copy. Backward-looking. Pairs with `groom` on the same weekly cadence.
- **`breakdown`** — Decompose a goal / plan / spec into independently-grabbable Linear tickets using tracer-bullet vertical slices. Grounds against current ndr heads when the ndr plugin is present, publishes in dependency order with native Linear blocks/blocked-by relations, recommends a spec-flow contract for large slices. Parent-aware. Slices land in Backlog — cycle assignment is `groom`'s job.

Planned for later versions:

- `triage` — single-issue analysis with proposed state / priority / labels / done-when
- `author` — single-ticket drafting (one-shot complement to `breakdown`'s multi-ticket case)

## References

- **`references/issue-shape.md`** — what counts as a well-formed Linear ticket (required fields + description body structure + anti-conventions). Shared across all PM skills: `groom` uses it for the Missing-fields and NDR-moot buckets; `triage` and `author` will use it for proposals and templates. Defers to `linear` for title/label/priority/status mechanics.
- **`references/layer-policy.md`** — what organizational layers the workspace uses (project / milestone / issue / cycle), what layers are deliberately off by default (epic / parent ticket, subissue, initiative), and the decision criteria for promoting work between layers. Used by `groom` to flag orphan tickets, by `breakdown` to decide milestone assignment, and by `retro` to surface layer-policy adherence.

## Composes with

- **[linear](../linear/README.md)** — `pm` skills propose; `linear` applies any approved transitions.
- **ndr** (external — ships from its own separate marketplace) — `pm:groom` calls `ndr:decisions` for supersession checks on tickets that reference ndr atoms. Optional: without it, the NDR-moot bucket and grounding passes are skipped.
- **librarian** (external — personal setup, not published) — `pm:retro`'s primary output is a Linear document; when librarian is present, an optional personal vault copy is written via its `note-editor` agent. Without librarian, that optional copy stays in chat for you to file manually.

## Assumptions

Like `linear` and `spec-flow`, this plugin assumes a particular environment and degrades gracefully without it:

- A single Linear team, written as `TEAM` in examples — substitute your team key.
- Weekly Linear cycles. Examples assume a Thu→Wed cycle with a Thursday-morning review; adjust to your workspace's cycle settings.
- An Obsidian vault (default `~/Loose Ends/`) holding per-project session notes and, if you use ndr, decision atoms under `Decisions/`. Without a vault, the vault-unfiled bucket in `groom` and the session-note passes in `retro` are skipped.

## Credits

- **`breakdown`** — Adapted from the `to-issues` skill in [`mattpocock/skills`](https://github.com/mattpocock/skills); upstream has since merged `to-issues` with `to-plan` into `to-tickets`. Adaptations applied during port: ndr grounding pre-pass, body template conforming to `references/issue-shape.md`, native Linear blocks/blocked-by relations, the parent-ticket-linking mechanic (Linear `parent` relation + confirm-before-publish), `Decision`-type slice handling with a capture-decision follow-up, and optional spec-flow handoff for contract-shaped slices. The HITL/AFK label split from the source skill was considered and deferred. Reconciled against `to-tickets` on 2026-07-09 (see `skills/breakdown/UPSTREAM.md`): adopted wide-refactor (expand-contract) sequencing and re-added a dropped prefactoring line.
