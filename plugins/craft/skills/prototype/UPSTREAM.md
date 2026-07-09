# Upstream divergences — prototype

_Upstream: `mattpocock/skills` · `skills/engineering/prototype` · ledger current as of `reviewed_sha: 850873cd73d5`_

Intentional divergences from upstream. Reviewed via `provenance:upstream-review` (2026-06-11) — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

The LOGIC/UI branch routing, the six shared rules, `LOGIC.md`, and `UI.md` are kept verbatim (modulo the one capture line below). No fabricated attributions, no silent drops.

| Kind | What | Why |
|------|------|-----|
| changed | "Capture the answer" (SKILL.md "When done" + UI.md step 6) routes load-bearing answers to an NDR atom via `/capture-decision`, with commit message / `NOTES.md` as fallback. Upstream listed commit / ADR / issue / `NOTES.md`. | NDR is this ecosystem's durable-decision home; `ADR` and `issue` are non-concepts here. The `NOTES.md`-for-AFK affordance is preserved. |
| changed | Frontmatter `description` retuned to upstream's model-invocation-tuned phrasing (2026-07-09, reviewed_sha `850873cd73d5`). | Ours was stale pin-era wording carried from the original adoption; no local intent behind the old text, so adopted upstream's improved phrasing wholesale (attribution clause preserved). |
