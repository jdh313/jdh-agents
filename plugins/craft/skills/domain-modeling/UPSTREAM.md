# Upstream divergences — domain-modeling

_Upstream: `mattpocock/skills` · `skills/engineering/domain-modeling` · ledger current as of `reviewed_sha: ee8bae40062c`_

Intentional divergences from upstream. Reviewed via `skillsmith:upstream-review` (2026-07-09) — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

The active-discipline framing, the four conversation moves (challenge against the glossary / sharpen fuzzy language / discuss concrete scenarios / cross-reference with code), the update-inline / don't-batch rule, the "CONTEXT.md is a glossary and nothing else" constraint, and the 3-part decision-worthiness gate (hard-to-reverse / surprising-without-context / real-trade-off) are upstream discipline, kept. Only the decision *destination* and the CONTEXT.md format details diverge.

| Kind | What | Why |
|------|------|-----|
| changed | Decision records re-routed from in-repo ADRs (`docs/adr/*.md` + `ADR-FORMAT.md`) to NDR atoms via `/capture-decision`; the skill never writes decision records directly. Upstream's "Offer ADRs sparingly" section became "Route capture-worthy decisions"; `docs/adr/` dropped from the file-structure diagram. | NDR is this ecosystem's durable decision layer. Same 3-part capture gate — only the destination and write-authority change. Mirrors the identical swap already documented in `grill-with-docs/UPSTREAM.md`; kept consistent with it. |
| changed | `ADR-FORMAT.md` sibling not carried over | Its role (how to write the decision record) belongs to the NDR ledger and `/capture-decision`, not this skill. The 3-part *gate* survives inline; the ADR *template* does not. |
| changed | Multi-context `CONTEXT-MAP.md` demoted from a first-class feature to "work-only, future"; personal repos use vault wiki pages as the cross-cutting authority instead | Personal repos aren't bounded-context monorepos; CONTEXT-MAP is overhead they don't earn. Consistent with `grill-with-docs`. |
| changed | Scenario-testing move scoped to terminology / concept-boundary finding rather than upstream's broader "domain relationships" | Keeps the move pointed at glossary governance, not a general test plan. Consistent with `grill-with-docs`. |
| added | `CONTEXT-FORMAT.md` sibling absorbed from `grill-with-docs/CONTEXT-FORMAT.md` (the more-evolved copy: `_See_:` link conventions, the "Flag ambiguities explicitly" rule + `## Flagged ambiguities` section, the "a repo earns a CONTEXT.md" worthiness gate). Content unchanged — ownership moves to `domain-modeling`. | Upstream's restructuring makes `domain-modeling` the owner of the CONTEXT.md format; `grill-with-docs` becomes a consumer of that format rather than its definer. |
| added | Attribution appended to `description`; `upstream:` provenance block; composition notes with `/capture-decision`, `craft:grill-with-docs`, `/drift-check` | Matches this repo's adapted-skill conventions and records ecosystem integration. |

## Provenance / absorption note

`CONTEXT-FORMAT.md` here is the canonical copy, absorbed from the former `grill-with-docs/CONTEXT-FORMAT.md`. As of Phase 2 (2026-07-09) the `grill-with-docs` copy was deleted and `grill-with-docs/SKILL.md` now dispatches to this skill for CONTEXT.md maintenance — `domain-modeling` is the sole owner of the format.
