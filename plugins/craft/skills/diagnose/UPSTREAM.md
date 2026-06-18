# Upstream divergences — diagnose

_Upstream: `mattpocock/skills` · `skills/engineering/diagnose` · ledger current as of `reviewed_sha: 7afa86d3a5dd`_

Intentional divergences from upstream. Reviewed via `provenance:upstream-review` (2026-06-11) — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

All six diagnosis phases and the HITL loop script are kept verbatim. The only divergences are the decision-layer re-routes below.

| Kind | What | Why |
|------|------|-----|
| changed | Codebase-grounding step: upstream "check ADRs in the area you're touching" → "invoke `/ground` to surface relevant NDR atoms in the area" | NDR ledger replaces in-repo ADRs; same intent (surface prior decisions in the touched area), different tool. |
| changed | Phase 6 post-mortem capture: added "or captured as an NDR atom via `/capture-decision`" alongside the upstream commit/PR-message path (additive — commit/PR path retained) | Routes the durable correct-hypothesis learning into the NDR ledger. |
| added | `effort: high` frontmatter field | Six-phase diagnosis loops (feedback loop construction, bisection, instrumentation) are reasoning-intensive; high effort engages deeper model reasoning for the full skill duration. |
| added | `/goal` tip below the opening paragraph | Documents user-invoked `/goal "<symptom resolved>"` as the idiomatic way to run multi-phase diagnosis with a clear exit condition. Prose note only — no auto-behavior change. |
