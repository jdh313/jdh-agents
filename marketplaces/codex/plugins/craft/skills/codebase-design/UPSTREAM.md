# Upstream divergences — codebase-design

_Upstream: `mattpocock/skills` · `skills/engineering/codebase-design` · ledger current as of `reviewed_sha: 697d4ce9742d`_

Intentional divergences from upstream. Reviewed via `skillsmith:upstream-review` (2026-07-09) — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

The glossary (Module / Interface / Implementation / Depth / Seam / Adapter / Leverage / Locality), the "Deep vs shallow" box diagrams + 3 design questions, the Principles, the "Designing for testability" TS snippets, Relationships, Rejected framings, and the "Going deeper" live-dispatch to `DEEPENING.md` / `DESIGN-IT-TWICE.md` are upstream content, kept. `DEEPENING.md` and `DESIGN-IT-TWICE.md` are byte-identical to upstream modulo link paths (see below).

## Provenance of this skill

This skill was **created by consolidating pre-existing `craft` content** that predated the upstream restructuring, plus a backfill of two sections upstream added that our copies lacked:

| Kind | What | Why |
|------|------|-----|
| consolidated | Glossary body (Terms / Principles / Relationships / Rejected framings) lifted verbatim from the former shared `references/LANGUAGE.md` | Upstream promoted the glossary from a static reference into a model-invoked skill. Our `LANGUAGE.md` term/principle body already matched upstream's pre-restructuring glossary (confirmed at review); it now lives here as the skill's own vocabulary section. |
| consolidated | `DESIGN-IT-TWICE.md` is the former `improve-codebase-architecture/INTERFACE-DESIGN.md`, renamed to upstream's filename | Same "Design It Twice" parallel-subagent process; upstream owns it under `codebase-design` now. |
| consolidated | `DEEPENING.md` is the former `improve-codebase-architecture/DEEPENING.md`, moved here | Deepening guidance belongs with the shared vocabulary, not inside one consumer skill. |
| changed | Sibling-file links repointed from `../../references/LANGUAGE.md` → `[SKILL.md](SKILL.md)` | The glossary now lives in this skill's own `SKILL.md`, so `DEEPENING.md` / `DESIGN-IT-TWICE.md` reference it locally instead of the old shared reference file. |
| backfilled | "Deep vs shallow" section (module box diagrams + the 3 interface-design questions) | Upstream added it after our `LANGUAGE.md` was last synced; our copy lacked it. Adopted verbatim from upstream's `codebase-design/SKILL.md`. |
| backfilled | "Designing for testability" section (inject-don't-create / return-don't-mutate / small-surface, with the before/after TS snippets) | Same gap as above. Adopted verbatim from upstream; TS reads fine as-is, kept. |
| added | Attribution appended to `description`; `upstream:` provenance block; shared-vocabulary intro naming the `craft` consumer skills (`tdd`, `improve-codebase-architecture`, `grill-with-docs`) | Matches this repo's adapted-skill conventions and records the deep-module vocabulary's role across the plugin. |

## Downstream rewiring (Phase 2 — complete 2026-07-09)

All consumers were rewired to dispatch here: `tdd`, `improve-codebase-architecture`, and `grok` now point at `Skill(craft:codebase-design)` for the deep-module vocabulary. The former static `references/LANGUAGE.md` and `improve-codebase-architecture`'s own `INTERFACE-DESIGN.md` / `DEEPENING.md` copies were deleted. This skill is now the sole owner of the architecture vocabulary.

Pin advanced to `697d4ce9742d` on 2026-07-27 with no ledger change: the only upstream commit touching this path since the previous pin was `697d4ce` "add Codex `agents/openai.yaml` metadata to every skill", verified via `--name-only` to add nothing but that sidecar. No-op for this adaptation — Codex manifests here are generated from `PACKAGE.yaml`.
