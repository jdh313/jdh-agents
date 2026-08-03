# Upstream divergences — writing-great-skills

_Upstream: `mattpocock/skills` · `skills/productivity/writing-great-skills` · ledger current as of `reviewed_sha: 697d4ce9742d`_

Intentional divergences from upstream. Reviewed via `skillsmith:upstream-review` (2026-07-10) — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

`SKILL.md` body and `GLOSSARY.md` are copied **verbatim** from upstream — the content is generic skill-craft with no vault, decision, tooling, or ticket surface to adapt. Only additive changes below. No fabricated attributions, no dropped content.

| Kind | What | Why |
|------|------|-----|
| added | `upstream:` provenance block in frontmatter (pin `af6d6922c3e2`, `status: reviewed`). | This marketplace's convention for every adapted skill; upstream carries no such block. |
| added | One `ADDENDA.md` context pointer near the top of `SKILL.md`, and the `ADDENDA.md` file itself. | Bridges the generic reference to cc-marketplace's own authoring mechanics (provenance, `allowed-tools` vs agent `tools:`, auto-discovery layout, commit format) that upstream doesn't cover. Pointer wording fires only when authoring *in this repo*, so it costs nothing on other reads. |
| kept | `disable-model-invocation: true` (user-invoked). | Upstream's deliberate choice — a by-name reference, not something the agent should auto-fire; keeps context load at zero. Preserved. |
| changed | `GLOSSARY.md` and `ADDENDA.md` moved from the skill root into `references/`, with the two `SKILL.md` links repointed. | The compiler publishes `SKILL.md` plus the recognized resource subdirs (`references/`, `scripts/`, `assets/`); a sibling `.md` at the skill root is not copied. At the skill root both files were linked from `SKILL.md` but absent from the compiled publication, so the installed skill carried two dead links. Content is unchanged and still verbatim from upstream. |

Pin advanced to `697d4ce9742d` on 2026-07-27 with no ledger change: the only upstream commit touching this path since the previous pin was `697d4ce` "add Codex `agents/openai.yaml` metadata to every skill", verified via `--name-only` to add nothing but that sidecar. No-op for this adaptation — Codex manifests here are generated from `PACKAGE.yaml`.
