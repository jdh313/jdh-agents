# pm

Self-PM helpers for CartaOS (Linear team CAR). Skills for the weekly grooming loop, single-issue triage, ticket authoring with NDR refs, and end-of-cycle retro notes.

## Premise

Solo development on CartaOS means acting as my own project manager. The PM work splits into a few recurring shapes — weekly grooming, ad-hoc triage, ticket authoring, end-of-cycle retro — each with its own cadence. This plugin gives each shape a skill so the routine is consistent and the proposals are auditable. All skills propose; transitions are applied manually via the `linear` plugin.

## Scope

- **Owns:** Grooming bucket taxonomy, triage proposal shape, retro note structure, ticket-authoring template with done-when + `ndr:` refs.
- **Does NOT own:** Linear ticket creation conventions (defers to `linear` plugin), decision atoms (defers to `ndr` plugin), vault writes (defers to `librarian` plugin).
- **Currently scoped to:** the `CAR` (Carta Healthcare) team.

## Skills

- **`groom`** — Weekly Tuesday-AM backlog grooming sweep. Scans active cycle + backlog, cross-refs NDR atoms and vault session notes, outputs a bucketed punch list and archives it to the week's recurring grooming child issue. Forward-looking.
- **`retro`** — End-of-cycle retro note. Pulls the just-closed cycle, classifies tickets (shipped / carried / canceled / added-mid-cycle), surfaces patterns across recent cycles, and writes a durable retro to `~/Loose Ends/Carta/Projects/CartaOS/Retros/` via `librarian:note-editor`. Backward-looking. Pairs with `groom` on the same Tuesday cadence.
- **`breakdown`** — Decompose a goal / plan / spec into independently-grabbable Linear tickets using tracer-bullet vertical slices. Grounds against current NDR heads, publishes in dependency order with native Linear blocks/blocked-by relations, recommends a spec-flow contract for large slices. Parent-aware. Slices land in Backlog — cycle assignment is `groom`'s job.

Planned for later versions:

- `triage` — single-issue analysis with proposed state / priority / labels / done-when
- `author` — single-ticket drafting (one-shot complement to `breakdown`'s multi-ticket case)

## References

- **`references/issue-shape.md`** — what counts as a well-formed CartaOS Linear ticket (required fields + description body structure + anti-conventions). Shared across all PM skills: `groom` uses it for the Missing-fields and NDR-moot buckets; `triage` and `author` will use it for proposals and templates. Defers to `linear-workflow` for title/label/priority/status mechanics.

## Composes with

- **[linear](../linear/README.md)** — `pm` skills propose; `linear-workflow` applies any approved transitions.
- **[ndr](../ndr/README.md)** — `pm:groom` calls `ndr:decisions` for supersession checks on tickets that reference NDR atoms.
- **[librarian](../librarian/README.md)** — `pm:retro` will (later) write retro notes via librarian patterns.

## Vault context

PM cadence and grooming setup:

- `Carta/Projects/CartaOS/` — project root, working-session notes
- `Carta/Projects/CartaOS/Linear Setup.md` — workspace shape (cycles, milestones, labels)

The `linear` plugin's catalog entry at `Reference/Tools/Software Catalog/Linear.md` covers the broader Linear adoption decision.

## Credits

- **`breakdown`** — Adapted from the `to-issues` skill in [`mattpocock/skills`](https://github.com/mattpocock/skills). CartaOS-specific adaptations applied during port: NDR grounding pre-pass, body template conforming to `references/issue-shape.md`, native Linear blocks/blocked-by relations, parent-ticket linking, `Decision`-type slice handling with `ndr:capture-decision` follow-up, and optional `spec-flow:start` handoff for contract-shaped slices. The HITL/AFK label split from the source skill was considered and deferred.
