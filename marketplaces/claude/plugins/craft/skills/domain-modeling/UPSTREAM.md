# Upstream divergences — domain-modeling

_Upstream: `mattpocock/skills` · `skills/engineering/domain-modeling` · ledger current as of `reviewed_sha: 321658273cb1`_

Intentional divergences from upstream. Reviewed via `skillsmith:upstream-review` (2026-07-09; drift review 2026-08-29) — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

The active-discipline framing, the four conversation moves (challenge against the glossary / sharpen fuzzy language / discuss concrete scenarios / cross-reference with code), the update-inline / don't-batch rule, the "CONTEXT.md is a glossary and nothing else" constraint, and the 3-part decision-worthiness gate (hard-to-reverse / surprising-without-context / real-trade-off) are upstream discipline, kept. Only the decision *destination* and the CONTEXT.md format details diverge.

| Kind | What | Why |
|------|------|-----|
| adopted | Description retriggering from `bd8e81baafe4` / `e12e7ec6a749` / `54bc6b604075`: dropped the "or when another craft skill needs to maintain the domain model" caveat, took upstream's plainer "discussing codebase terminology" wording, and added the explicit write trigger. **Applied 2026-08-29.** | Recorded because the caveat's retention was *accidental*, not intentional — drift review confirmed upstream's stated rationale holds here verbatim: `craft:grill-with-docs` and `craft:improve-codebase-architecture` both already name-invoke this skill directly, so the caveat bought nothing. Upstream's write trigger is `recording or editing an ADR`; ours says NDR decision, per the ADR→NDR swap already rowed below. |
| changed | Decision records re-routed from in-repo ADRs (`docs/adr/*.md` + `ADR-FORMAT.md`) to NDR atoms via `/capture-decision`; the skill never writes decision records directly. Upstream's "Offer ADRs sparingly" section became "Route capture-worthy decisions"; `docs/adr/` dropped from the file-structure diagram. | NDR is this ecosystem's durable decision layer. Same 3-part capture gate — only the destination and write-authority change. Mirrors the identical swap already documented in `grill-with-docs/UPSTREAM.md`; kept consistent with it. |
| changed | `ADR-FORMAT.md` sibling not carried over | Its role (how to write the decision record) belongs to the NDR ledger and `/capture-decision`, not this skill. The 3-part *gate* survives inline; the ADR *template* does not. |
| changed | Multi-context `CONTEXT-MAP.md` demoted from a first-class feature to "work-only, future"; personal repos use vault wiki pages as the cross-cutting authority instead | Personal repos aren't bounded-context monorepos; CONTEXT-MAP is overhead they don't earn. Consistent with `grill-with-docs`. |
| changed | Scenario-testing move scoped to terminology / concept-boundary finding rather than upstream's broader "domain relationships" | Keeps the move pointed at glossary governance, not a general test plan. Consistent with `grill-with-docs`. |
| added | `CONTEXT-FORMAT.md` sibling absorbed from `grill-with-docs/CONTEXT-FORMAT.md` (the more-evolved copy: `_See_:` link conventions, the "Flag ambiguities explicitly" rule + `## Flagged ambiguities` section, the "a repo earns a CONTEXT.md" worthiness gate). Content unchanged — ownership moves to `domain-modeling`. | Upstream's restructuring makes `domain-modeling` the owner of the CONTEXT.md format; `grill-with-docs` becomes a consumer of that format rather than its definer. |
| added | Attribution appended to `description`; `upstream:` provenance block; composition notes with `/capture-decision`, `craft:grill-with-docs`, `/drift-check` | Matches this repo's adapted-skill conventions and records ecosystem integration. |

## Provenance / absorption note

`CONTEXT-FORMAT.md` here is the canonical copy, absorbed from the former `grill-with-docs/CONTEXT-FORMAT.md`. As of Phase 2 (2026-07-09) the `grill-with-docs` copy was deleted and `grill-with-docs/SKILL.md` now dispatches to this skill for CONTEXT.md maintenance — `domain-modeling` is the sole owner of the format.

Pin advanced to `697d4ce9742d` on 2026-07-27 with no ledger change: the only upstream commit touching this path since the previous pin was `697d4ce` "add Codex `agents/openai.yaml` metadata to every skill", verified via `--name-only` to add nothing but that sidecar. No-op for this adaptation — Codex manifests here are generated from `PACKAGE.yaml`.
