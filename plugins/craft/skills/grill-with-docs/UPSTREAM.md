# Upstream divergences — grill-with-docs

_Upstream: `mattpocock/skills` · `skills/engineering/grill-with-docs` · ledger current as of `reviewed_sha: 658d53e6ded8`_

Intentional divergences from upstream. Reviewed via `provenance:upstream-review` — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

Upstream's `grill-with-docs` collapsed to a thin dispatcher over `/grilling` + `/domain-modeling`. This review follows that shape: all CONTEXT.md maintenance, format, and decision-capture discipline now dispatches to `craft:domain-modeling`. The CONTEXT.md/ADR->NDR divergences this file used to document directly (decision-record rerouting, CONTEXT-MAP demotion, scenario-testing scoping, `_See_:` link conventions, the "Flag ambiguities explicitly" rule, the CONTEXT.md worthiness gate) are now owned and reviewed in `domain-modeling/UPSTREAM.md` — inherited here by dispatch, not re-documented.

| Kind | What | Why |
|------|------|-----|
| changed | No standalone `grilling` skill extracted, unlike upstream's split into `/grilling` + `/domain-modeling` — the interview loop lives inline in this skill instead | The interview loop is grill-with-docs' only reason to exist as a distinct skill; extracting it would leave a skill that's nothing but a dispatch. Deliberate divergence, not an oversight. |
| changed | CONTEXT.md maintenance, format, and decision-capture discipline dispatched to `craft:domain-modeling` mid-interview rather than implemented inline; `CONTEXT-FORMAT.md` sibling deleted, ownership moved to `domain-modeling/CONTEXT-FORMAT.md` | Matches upstream's own consolidation (upstream's `grill-with-docs` now just dispatches to `/domain-modeling`); keeps one owner for the glossary discipline instead of two copies drifting independently. See `domain-modeling/UPSTREAM.md` provenance note for the absorption history. |
| added | Shared-understanding gate: "Do not enact the plan until the user confirms a shared understanding has been reached." | Ported from upstream's `grilling` skill — the skill upstream's own `grill-with-docs` now dispatches to. Closes a real gap: nothing previously stopped the agent from enacting a plan before the interview settled. |

## Corrected earlier review

- Removed a **fabricated attribution**: an `## Explicit non-goals` entry (content now owned by `domain-modeling`) claimed Matt's `CONTEXT-FORMAT.md` "asked for a conversation between a dev and a domain expert." The current upstream contains no such thing. Reworded to a positive rule in the absorbed copy.
