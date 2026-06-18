# Upstream divergences — improve-codebase-architecture

_Upstream: `mattpocock/skills` · `skills/engineering/improve-codebase-architecture` · ledger current as of `reviewed_sha: a36584e09eae`_

Intentional divergences from upstream. Reviewed via `provenance:upstream-review` (2026-06-11) — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

`DEEPENING.md`, `INTERFACE-DESIGN.md`, and the `LANGUAGE.md` term/principle body are byte-identical to upstream (modulo link paths). The grilling-loop structure and CONTEXT.md side-effects are upstream behavior, kept. No fabricated attributions, no silent drops.

| Kind | What | Why |
|------|------|-----|
| changed | Report format: upstream self-contained HTML (Tailwind + Mermaid via CDN, written to `$TMPDIR`) → markdown + Mermaid fences + ASCII, written to gitignored `<repo>/.docs/architecture-review-<ts>.md`. Sibling `HTML-REPORT.md` → `MARKDOWN-REPORT.md`. | No CDN; renders natively in GitHub / Obsidian / VS Code. `.docs/` is the ecosystem's standard scratch space, kept out of the tracked tree. |
| changed | Decision layer: in-repo ADRs (`docs/adr/`, `ADR-FORMAT.md`, "ADR conflicts" callout, "Offer an ADR" on rejection) → NDR atoms — `/ground` surfaces them in Explore, conflicts use `ndr:area/topic/NNNN-slug` refs, rejection rationale captured via `/capture-decision`. | NDR is this ecosystem's durable decision layer; same don't-re-litigate / capture-on-rejection discipline, only destination + write-authority change. |
| changed | `LANGUAGE.md` promoted from skill-local (`./LANGUAGE.md`) to shared `../../references/LANGUAGE.md` (canonical glossary shared with `craft:tdd`); intro reworded, cross-ref + MIT attribution added. Terms/principles unchanged. | One glossary for all `craft` architectural skills; new terms added centrally rather than per-skill. |
| added | `effort: high` frontmatter field | Codebase exploration + grilling loop are reasoning-intensive; high effort engages deeper model reasoning for the full skill duration. |
| changed | Explore subagent dispatch: `subagent_type=Explore` → `subagent_type=Explore, name="arch-explorer"` | Names the agent so it stays addressable via SendMessage during the grilling loop; unnamed agents cannot be continued without full re-dispatch. |
| not-added | `disallowed-tools:` for source-editing restriction | Considered but skipped: skill legitimately writes to gitignored `.docs/` (report) and `CONTEXT.md` (grilling-loop inline updates). Blocking `Edit`/`Write` would break both. No tool-level carve-out available for "tracked source only." |
