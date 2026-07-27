# Upstream divergences — prototype

_Upstream: `mattpocock/skills` · `skills/engineering/prototype` · ledger current as of `reviewed_sha: 697d4ce9742d`_

Intentional divergences from upstream. Reviewed via `skillsmith:upstream-review` (2026-07-27) — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

The LOGIC/UI branch routing, the six shared rules, `LOGIC.md`, and `UI.md` are kept verbatim (modulo the capture lines below). No fabricated attributions, no silent drops.

Adopted from upstream at `697d4ce9742d` (2026-07-27), now equivalent and needing no divergence row: the **primary-source reframing** of rule 6 (`d627460`, `cdec9f6`, `371b9c9`, `0375c88`, `fa460cb`) — the prototype is committed to a throwaway branch out of main rather than deleted, with only the validated decision landing in main. This replaced our previous "Delete or absorb when done" text, which was itself inherited upstream text with no local intent behind it. `LOGIC.md` §3/§7 and `UI.md` §6 were rewritten to match.

| Kind | What | Why |
|------|------|-----|
| changed | Answer capture (SKILL.md "Capturing the answer" + `LOGIC.md` §7 + `UI.md` §6) routes load-bearing answers to an NDR atom via `/capture-decision`, with commit message / tracking ticket / `NOTES.md` as fallback. Upstream listed commit / ADR / issue / `NOTES.md`, and at `697d4ce9742d` lists only "the issue or a commit". | NDR is this ecosystem's durable-decision home; `ADR` is a non-concept here. The `NOTES.md`-for-AFK affordance is deliberately preserved even though upstream dropped it in the primary-source rewrite — running AFK is common here and the placeholder is the only thing that survives an unattended session. |
| changed | Rule 6's context pointer targets "the tracking ticket or spec-flow contract"; upstream says "the implementation issue". | Names this ecosystem's actual hosts (Linear ticket via the `pm`/`linear` plugins, or a `spec-flow` contract) instead of a generic issue. |
| added | SKILL.md keeps a short "Capturing the answer" section; upstream collapsed its "When done" section into rule 6 (`0375c88`). | The NDR routing plus the AFK `NOTES.md` fallback are too long to read cleanly as a rule bullet. Same content, different placement. |
| changed | Frontmatter `description` retuned to upstream's model-invocation-tuned phrasing (2026-07-09, reviewed_sha `850873cd73d5`). | Ours was stale pin-era wording carried from the original adoption; no local intent behind the old text, so adopted upstream's improved phrasing wholesale (attribution clause preserved). |
