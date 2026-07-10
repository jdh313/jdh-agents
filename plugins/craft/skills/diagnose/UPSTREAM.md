# Upstream divergences — diagnose

_Upstream: `mattpocock/skills` · `skills/engineering/diagnosing-bugs` (renamed from `diagnose`) · ledger current as of `reviewed_sha: ee8bae40062c`_

Intentional divergences from upstream. Reviewed via `skillsmith:upstream-review` (2026-07-09) — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

All six diagnosis phases and the HITL loop script track upstream. The divergences are the decision-layer re-routes and wording adaptations below.

| Kind | What | Why |
|------|------|-----|
| changed | Codebase-grounding step: upstream "read `CONTEXT.md` (if it exists) ... check ADRs in the area you're touching" → "read `CONTEXT.md` (if it exists) ... invoke `/ground` to surface relevant NDR atoms in the area" | NDR ledger replaces in-repo ADRs; same intent (surface prior decisions in the touched area), different tool. The `CONTEXT.md` half now matches upstream verbatim — previously paraphrased here as "the project's domain glossary". |
| changed | Phase 6 post-mortem capture: added "or captured as an NDR atom via `/capture-decision`" alongside the upstream commit/PR-message path (additive — commit/PR path retained) | Routes the durable correct-hypothesis learning into the NDR ledger. |
| added | Phase 1 "Completion criterion — a tight loop that goes red" gate: named, already-run command + red-capable/deterministic/fast/agent-runnable checklist + explicit "stop before hypothesising" warning | Ported verbatim-in-substance from upstream's tightened Phase 1 exit gate. Forces proof (paste the invocation and its output) that a red-capable loop exists before Phase 2, closing the failure mode of jumping straight to a hypothesis. |
| added | Phase 2 renamed "Reproduce + minimise"; added "Minimise" subsection (shrink to smallest still-reproducing scenario, one cut at a time, load-bearing completion criterion) | Ported from upstream. Shrinks the Phase 3 hypothesis space and produces a cleaner Phase 5 regression-test seam. |
| added | `effort: high` frontmatter field | Six-phase diagnosis loops (feedback loop construction, bisection, instrumentation) are reasoning-intensive; high effort engages deeper model reasoning for the full skill duration. |
| added | `/goal` tip below the opening paragraph | Documents user-invoked `/goal "<symptom resolved>"` as the idiomatic way to run multi-phase diagnosis with a clear exit condition. Prose note only — no auto-behavior change. |
