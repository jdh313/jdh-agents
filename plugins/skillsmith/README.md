# skillsmith

Craft and upkeep of skills. Two jobs: **authoring** skills well, and keeping **borrowed** skills honest against their upstream sources. Several skills in this marketplace are adapted from upstream (e.g. `mattpocock/skills`) — adaptation is fine, but every divergence should be deliberate, documented, and free of fabricated claims about what upstream actually does.

## Skills

- **writing-for-agents** — Reference for writing any document an agent consumes: a skill, an AGENTS.md/CLAUDE.md, a rules file, or a doc reached by a pointer. Carries the vocabulary (predictability, context vs cognitive load, information hierarchy, progressive disclosure, granularity, pruning) and principles that make such a document predictable. Model-invoked — fires on its own when you create or edit a skill, AGENTS.md/CLAUDE.md, or a rules file, or when asked how to make an agent-facing document more predictable; full definitions disclosed to `GLOSSARY.md`. Adapted verbatim from upstream (which made the same rename and scope broadening) with a repo-specific bridge in `ADDENDA.md`.
- **upstream-review** — Compare an adapted skill against its pinned upstream source. Classifies each behavioral unit as kept / diverged / dropped / added, hunts fabricated attributions (local claims about upstream that upstream doesn't support), proposes fixes for sign-off, and refreshes the reviewed commit SHA.

## Codex optional agent bundle

Skillsmith 2.3.0 can register `skillsmith:upstream-reviewer` in one selected
Codex user or project scope. After installing Skillsmith from the Codex
marketplace, explicitly invoke `$skillsmith:setup-codex-agents`. The active
installed setup skill derives its helper from the installed skill path; do not
guess a cache path or use an authoring checkout. In a fresh session, run the
same selected-scope check immediately before dispatching the exact
`agent_type`.

The bundled Markdown procedure remains a separately chosen generic-child
fallback. It omits `agent_type` and does not register a role. Codex does not
mechanically retain the Claude agent's tool allowlist, so its read-only,
one-comparison boundary stays advisory procedure guidance; sandbox and approval
policy remain the caller's responsibility. Source declares this bundle, but
the generated bundle does not establish installed registration or runtime
acceptance. Isolated lifecycle, installed-skill activation, and fresh-dispatch
acceptance remain pending.

## Provenance convention

Each adapted skill pins its source in its own SKILL.md frontmatter:

```yaml
upstream:
  repo: owner/name
  path: path/to/skill/dir
  reviewed_sha: <12-char sha>   # last upstream commit touching `path` that we reconciled against
  reviewed: YYYY-MM-DD
  status: reviewed | baseline   # `baseline` = pinned without a behavioral review (still owes a first review)
```

Drift = a newer commit has touched `path` since `reviewed_sha`. A `baseline` pin only catches *future* upstream commits — it does not certify that the current adaptation matches the pinned SHA, so baseline skills still owe a full `upstream-review`. A future scheduled job (GitHub Action, or a Claude Code scheduled agent / cron routine) can walk every `upstream:` block and open an issue for skills that have fallen behind; `upstream-review` does the per-skill reconciliation on demand.
