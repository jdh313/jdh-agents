# Upstream divergences — teach

_Upstream: `mattpocock/skills` · `skills/productivity/teach` · ledger current as of `reviewed_sha: 694fa30311e0`_

Intentional divergences from upstream. Reviewed via `provenance:upstream-review` intake (2026-06-12); adapted for Obsidian-vault routing the same day. Do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

This adaptation routes the skill's durable markdown artifacts into the Obsidian vault (`~/Loose Ends/`) as typed notes, while keeping lessons and HTML cheat sheets as self-contained files inside the workspace folder. Design spec: `.docs/2026-06-12-teach-vault-routing.md`.

## Kept (verbatim or substantively equivalent)
Lesson philosophy and beauty bar; fluency-vs-storage-strength; zone of proximal development; knowledge/skills/wisdom triad; community delegation for wisdom; lessons and reference cheat sheets as HTML; citation discipline. The four FORMAT files retain their templates and rules; only the host (vault note vs flat file) and a frontmatter block were added.

## Divergences

| Kind | What | Why |
|------|------|-----|
| changed | Workspace location: upstream "treat the current directory as a teaching workspace" → a self-contained workspace folder in the vault, placed under its best-fit **context** (`Reference/Developer/<Topic>/`, `Hobbies/<Area>/<Topic>/`, …). | Routes durable learning into the user's connected knowledge graph; honors the vault's context-first organization. |
| changed | `MISSION.md` → `Mission.md` vault note (`type: learning-mission`, with `status`/`up`/`tags` frontmatter). Absorbs the upstream `NOTES.md` (teaching preferences) as a body section. | Becomes a queryable typed note; folding `NOTES.md` in removes a file. |
| changed | `RESOURCES.md` → `Resources.md` index note. Ingestible material is saved to the vault's global `Sources/` namespace via `wiki-create`; the index links in by wikilink rather than inlining. | Reuses the vault's existing ingest→Sources→synthesize pipeline; sources become a shared namespace across topics. |
| changed | `learning-records/*.md` → `./Records/*.md` vault notes (`type: learning-record`). Supersession uses the vault's `status: current\|revised\|superseded` + `superseded_by` vocabulary instead of upstream's `Status: superseded by LR-NNNN`. | Reads natively next to the vault's `Decisions/` ADRs; reuses the decision-supersession primitive. |
| changed | Glossary: upstream `GLOSSARY.md` (workspace-local markdown) → `Glossary.md` working note whose durable, cross-cutting terms **graduate** to `Reference/` wiki concept notes (`type: wiki, page_type: concept`). | The vault's wiki is the long-term glossary; the workspace glossary becomes a staging area feeding it. |
| changed | "Open the lesson via a CLI command" retained but vault-path aware (lessons live in `<workspace>/lessons/`). | Lessons stay HTML inside the vault folder so their relative anchor links resolve. |
| added | Pedagogy grounding: the skill reads `Personal/Manual of Me/Learning/Learning Style.md` at session start and biases toward real-stakes practice over recall drills, and guards against being an AI-substitute crutch. | The user's own learning-style note documents retention by doing + real stakes and flags the AI-as-substitute failure mode. Notably, this is why **no spaced-repetition / flashcard layer was added** — flashcards build fluency strength, which that note treats as illusory mastery for this user. |
| added | Context-resolution step: infer best-fit context from the topic, propose a path, and confirm with the user before creating the workspace. | The vault is context-first with no top-level `Learning/` folder; placement is the user's call. |
| added | Cross-cutting "all my learning" view via querying `type: learning-mission` (MOC / Base, planned P2) instead of folder colocation. | Recovers the unified view lost by context-first placement, using the vault's tag/type tier. |
| added | `allowed-tools:` frontmatter (`obsidian-cli`, `Write`, `Read`, `patch_note`) pre-approving the vault tools the skill invokes inline. | Marketplace skill UX; the skill now performs vault writes directly. |
