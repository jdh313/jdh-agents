---
name: vault-inspect
description: Run a diagnostic sweep on the Obsidian vault. Reports structural issues (orphans, dead-ends, broken links, frontmatter, stale pages) and/or wiki-semantic issues (page_type validation, neutral-definition opening, source-link format, Software Catalog schema, anti-staleness). Use when user says "lint the wiki", "wiki health check", "check knowledge base", "vault health check", "note health", or invokes `/vault-inspect`. Merger of the former `note-health` and `wiki-lint` skills.
disable-model-invocation: true
context: fork
agent: vault-inspector
---

# Vault Inspect

Diagnostic sweep on the Obsidian vault "Loose Ends". The slash command
forks to `@vault-inspector`, which runs the rule set from
`${CLAUDE_PLUGIN_ROOT}/references/inspect-rules.md` and returns a
structured report.

Two rule families:

- **Structural** (`S-*`) — vault-wide: orphans, dead-ends, broken links,
  missing frontmatter, stale, oversized, convention violations.
- **Wiki-semantic** (`W-*`) — `owner: ai` + `type: wiki` pages only:
  page_type validation, hierarchy, neutral-definition opening,
  source-link format, Software Catalog schema, anti-staleness,
  Breadcrumbs hygiene.

## Usage

```
/vault-inspect                       # both scopes (default)
/vault-inspect --structural          # S-* rules only
/vault-inspect --wiki                # W-* rules only
/vault-inspect --folder="path/to/x"  # restrict to a folder
/vault-inspect --focus=orphans       # one rule category (structural)
/vault-inspect --full                # exhaustive scan (no sampling)
```

## Scope resolution

For the forked `@vault-inspector`:

- No flags → run both `--structural` and `--wiki`.
- `--structural` → S-* rules only.
- `--wiki` → W-* rules only (restrict to wiki pages).
- `--folder=PATH` → restrict whichever scope was chosen to that folder.
- `--focus=CATEGORY` → run one rule category (structural):
  - `orphans` (S-1), `deadends` (S-2), `broken` (S-3),
    `frontmatter` (S-4), `stale` (S-5), `oversized` (S-6),
    `conventions` (S-7).
- `--full` → no sampling; check every note.

## Report shape

Per `agents/vault-inspector.md` (`## Output shape`): one table per rule
category with columns Rule / Severity / Path / Note, plus a Summary
section with counts and highest severity. Add a Recommendations section
mapping the top issues to follow-up skills:

```markdown
### Recommendations
1. **High priority:** Fix N broken links (blocks navigation)
2. **Medium priority:** Add frontmatter to M notes
3. **Low priority:** Review P stale notes

Follow-ups:
- Structural fixes → `/note-cleanup` (forks to `vault-curator`)
- Wiki schema migration → `Skill(catalog-evaluate)` for catalog drift,
  `Skill(wiki-create)` (stub mode) for missing-page targets
- Specific page rewrites → `@note-editor`
```

## Health score (optional, structural only)

The structural sweep can produce a 0–100 score for at-a-glance vault
health:

| Factor | Weight | Deduction per Issue |
|--------|--------|---------------------|
| Broken links (S-3) | 25% | -5 per link |
| Orphaned notes (S-1) | 20% | -2 per note |
| Dead-end notes (S-2) | 10% | -1 per note |
| Missing frontmatter (S-4) | 15% | -1 per note |
| Oversized notes (S-6) | 10% | -2 per note |
| Convention violations (S-7) | 10% | -2 per violation |
| Stale notes (S-5) | 10% | -1 per note |

Cap deductions per factor at its weight so a single bad category can't
drag the score below the next factor's contribution.

## Quality rules

- **Report findings; don't auto-fix.** That's `vault-curator`'s or `note-editor`'s job, not the inspector's.
- **Don't bulk-rewrite** first-person eval headings (W-19) — surface as migration suggestions; the user migrates each page when next touching it.
- **Suggest sources to seek out** for gap-filling on thin pages (W-5).
- **Respect velocity overrides** (W-16) — `velocity: stable` pages are intentionally not anti-stale-checked.

## After reporting

The agent's report is surfaced to the user. The user decides which
follow-ups to take; this skill does not chain into them automatically.
If the user approves fixes:

- `/note-cleanup` opens an interactive cleanup session (forks to `vault-curator`)
- `Skill(wiki-create)` (stub mode) for missing-page targets
- `Skill(catalog-evaluate)` for Software Catalog schema drift
- `@note-editor` for targeted page rewrites
- Re-run `/vault-inspect` to confirm fixes

If fixes happened in the same session, append a lint entry to
`Reference/log.md` (the cleanup skill handles this).
