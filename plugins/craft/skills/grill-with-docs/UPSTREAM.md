# Upstream divergences — grill-with-docs

_Upstream: `mattpocock/skills` · `skills/engineering/grill-with-docs` · ledger current as of `reviewed_sha: 697d4ce9742d`_

Intentional divergences from upstream. Reviewed via `skillsmith:upstream-review` — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

Upstream's `grill-with-docs` collapsed to a thin dispatcher over `/grilling` + `/domain-modeling`. This review follows that shape: all CONTEXT.md maintenance, format, and decision-capture discipline now dispatches to `craft:domain-modeling`. The CONTEXT.md/ADR->NDR divergences this file used to document directly (decision-record rerouting, CONTEXT-MAP demotion, scenario-testing scoping, `_See_:` link conventions, the "Flag ambiguities explicitly" rule, the CONTEXT.md worthiness gate) are now owned and reviewed in `domain-modeling/UPSTREAM.md` — inherited here by dispatch, not re-documented.

| Kind | What | Why |
|------|------|-----|
| changed | Interview loop extracted to `craft:grill` and dispatched, matching upstream's split into `/grilling` + `/domain-modeling`. What remains local is a two-sentence scoping delta: the subject is a plan, and facts are answered from this repo (codebase, `CONTEXT.md`, NDR heads) rather than the environment at large. **Reverses the earlier no-extract decision** — see below. | The inlined copy could not be drift-reviewed. This skill's provenance pins `skills/engineering/grill-with-docs`, so upstream `170ad48` (renaming "design tree" → "decision tree", rescoping "codebase" → "environment") was invisible here — it touched `skills/productivity/grilling`. The copy had already rotted to pre-Jul-13 vocabulary before anyone noticed. One owner, pinned to the path that governs it, is the only shape where drift review works. |
| changed | CONTEXT.md maintenance, format, and decision-capture discipline dispatched to `craft:domain-modeling` mid-interview rather than implemented inline; `CONTEXT-FORMAT.md` sibling deleted, ownership moved to `domain-modeling/CONTEXT-FORMAT.md` | Matches upstream's own consolidation (upstream's `grill-with-docs` now just dispatches to `/domain-modeling`); keeps one owner for the glossary discipline instead of two copies drifting independently. See `domain-modeling/UPSTREAM.md` provenance note for the absorption history. |
| changed | Shared-understanding gate ("do not act until the user confirms") no longer stated here — inherited from `craft:grill` by dispatch. | Previously an `added` row: the gate had been ported inline from upstream's `grilling` skill, which upstream's own `grill-with-docs` dispatches to. With the loop extracted, the gate travels with it. Still enforced, just not owned here. |

## Corrected earlier review

- Removed a **fabricated attribution**: an `## Explicit non-goals` entry (content now owned by `domain-modeling`) claimed Matt's `CONTEXT-FORMAT.md` "asked for a conversation between a dev and a domain expert." The current upstream contains no such thing. Reworded to a positive rule in the absorbed copy.

Pin advanced to `697d4ce9742d` on 2026-07-27 with no ledger change: the only upstream commit touching this path since the previous pin was `697d4ce` "add Codex `agents/openai.yaml` metadata to every skill", verified via `--name-only` to add nothing but that sidecar. No-op for this adaptation — Codex manifests here are generated from `PACKAGE.yaml`.

## Re-split, 2026-07-27

The interview loop was extracted to `craft:grill` and is now dispatched rather than inlined. This reverses the original no-extract call, whose rationale — "extracting it would leave a skill that's nothing but a dispatch" — was sound while there was no `grill` to dispatch, and overstated once there was: what remains is the scoping delta plus the `domain-modeling` pairing and the composition contract with `spec-flow:draft`.

The deciding argument was not shape but reviewability. A path-scoped `reviewed_sha` cannot see commits to a *different* upstream path, so content inlined from another skill's source is structurally invisible to drift review — and this copy had already silently rotted to pre-`170ad48` vocabulary. Extraction is what makes the loop reviewable at all. Full intake record: `../grill/UPSTREAM.md`.
