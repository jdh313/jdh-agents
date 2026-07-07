# Upstream divergences — grill-with-docs

_Upstream: `mattpocock/skills` · `skills/engineering/grill-with-docs` · ledger current as of `reviewed_sha: e3b90b5238f3`_

Intentional divergences from upstream. Reviewed via `provenance:upstream-review` — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

| Kind | What | Why |
|------|------|-----|
| changed | Decision records re-routed from in-repo ADRs (`docs/adr/*.md` + `ADR-FORMAT.md`) to NDR atoms via `/capture-decision`; the skill never writes decision records directly | NDR is this ecosystem's durable decision layer. Same 3-part capture gate (hard-to-reverse / surprising / real-tradeoff) — only the destination and write-authority change. |
| changed | Multi-context `CONTEXT-MAP.md` demoted from a first-class feature to "work-only, future"; personal repos use vault wiki pages as the cross-cutting authority instead | Personal repos aren't bounded-context monorepos; CONTEXT-MAP is overhead they don't earn. |
| changed | Scenario-testing move scoped to terminology / concept-boundary finding rather than upstream's broader "domain relationships" | Keeps the move pointed at glossary governance, not a general test plan. (Was silently dropped in an earlier adaptation, re-added 2026-06-11.) |
| added | `_See_:` link conventions — vault wikilinks (`[[Page]]`) and `ndr:area/topic/NNNN-slug` refs; vault wikilinks banned in work repos | Wires CONTEXT.md into the personal vault and NDR ledger; proprietary/personal split keeps work code clear of personal vault links. |
| added | 5th CONTEXT.md rule "Flag ambiguities explicitly" + a `## Flagged ambiguities` section | Surfaces inconsistent codebase term usage instead of silently picking one reading. |
| added | "A repo earns a CONTEXT.md" worthiness gate, plus composition notes with `spec-flow:start`, `/capture-decision`, `/drift-check` | Ecosystem integration; avoids spawning glossaries for repos already covered by external sources (vault wiki / internal work docs). |

## Corrected this review

- Removed a **fabricated attribution**: the `## Explicit non-goals` entry claimed Matt's `CONTEXT-FORMAT.md` "asked for a conversation between a dev and a domain expert." The current upstream contains no such thing. Reworded to a positive rule ("Definitions only — no demonstrative dialogue") in both `SKILL.md` and `CONTEXT-FORMAT.md`.
