# Upstream divergences — tdd

_Upstream: `mattpocock/skills` · `skills/engineering/tdd` · ledger current as of `reviewed_sha: 697d4ce9742d`_

Intentional divergences from upstream. Reviewed via `skillsmith:upstream-review` (2026-07-09) — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

The reference-only shape (what-a-good-test-is, seams, anti-patterns, rules-of-the-loop), the horizontal-slices anti-pattern, the tautological-test anti-pattern, and the `tests.md` / `mocking.md` siblings track upstream verbatim in intent. No fabricated attributions, no silent drops.

| Kind | What | Why |
|------|------|-----|
| changed | Planning grounding: generic "domain glossary" → **CONTEXT.md** (upstream has since converged on CONTEXT.md too); "respect ADRs in the area" → invoke **`/ground`** to surface the **NDR atoms** governing the area | Routes the upstream's grounding step into this repo's concrete NDR decision-ledger primitive instead of generic ADRs. |
| changed | Seam vocabulary is **dispatched** to the shared `craft:codebase-design` skill rather than defined inline (upstream defines seam inline) | De-dupes the shared `craft`-plugin architecture glossary (Module/Interface/Depth/Seam); one source of truth across sibling skills (grill-with-docs, improve-codebase-architecture). |
| changed | Refactor stage points at this repo's **`/code-review` + `/simplify`** tooling; upstream points at its own `code-review` skill | Names the concrete review tooling that lives in this marketplace. |
| added | `effort: high` frontmatter field | Multi-phase red → green loops are reasoning-intensive; high effort engages deeper model reasoning for the full skill duration. |
| added | `/goal` tip re-homed under "Rules of the loop" | Documents user-invoked `/goal "<completion condition>"` as the idiomatic way to run multi-behavior TDD sessions with a clear exit condition. Prose note only — no auto-behavior change. Survived the reference-only reshape (originally lived atop the retired Workflow section). |
| adopted (2026-07-09) | **Refactor stage dropped from the loop.** TDD is now red → green; refactoring is review-stage work. `refactoring.md` retired (`trash`). | Adopted upstream's reshape — the loop no longer owns refactoring. |
| adopted (2026-07-09) | **Reshaped to reference-only.** Dropped the prescriptive numbered Workflow and the per-cycle checklist; folded vertical-slices / tracer-bullets into the anti-patterns + rules-of-the-loop list. | Adopted upstream's reshape — reference the durable ideas rather than sequence a workflow. |
| adopted (2026-07-09) | **Seam concept adopted** ("test only at pre-agreed seams, confirmed with the user before any test is written"). | Adopted upstream's seam framing for where tests go; vocabulary dispatched to `codebase-design` (see divergence row above). |
| adopted (2026-07-09) | **Tautological-test anti-pattern added** in both `SKILL.md` (anti-patterns) and `tests.md` (BAD/GOOD pair). | Adopted upstream's addition — expected values must come from an independent source of truth, not a recomputation of the code. |
| adopted (2026-07-09) | **`deep-modules.md` and `interface-design.md` retired** (`trash`), superseded by dispatch to the shared `craft:codebase-design` skill. | The shared skill now owns the deep-module / interface / seam / depth vocabulary; the tdd-local copies were duplication. |

Pin advanced to `697d4ce9742d` on 2026-07-27 with no ledger change: the only upstream commit touching this path since the previous pin was `697d4ce` "add Codex `agents/openai.yaml` metadata to every skill", verified via `--name-only` to add nothing but that sidecar. No-op for this adaptation — Codex manifests here are generated from `PACKAGE.yaml`.
