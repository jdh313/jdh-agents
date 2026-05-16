---
name: vault-inspect
description: Run a diagnostic sweep on the Obsidian vault. Reports structural issues (orphans, dead-ends, broken links, frontmatter, stale pages) and/or wiki-semantic issues (page_type validation, neutral-definition opening, source-link format, Software Catalog schema, anti-staleness). Use when user says "lint the wiki", "wiki health check", "check knowledge base", "vault health check", "note health", or invokes `/vault-inspect`. Merger of the former `note-health` and `wiki-lint` skills.
disable-model-invocation: true
allowed-tools:
  - Bash(obsidian orphans *)
  - Bash(obsidian deadends *)
  - Bash(obsidian unresolved *)
  - Bash(obsidian read *)
  - Bash(obsidian search *)
  - Bash(obsidian files *)
  - Bash(obsidian folders *)
  - Bash(obsidian properties *)
  - Bash(obsidian wordcount *)
  - Bash(obsidian backlinks *)
  - Bash(obsidian links *)
  - Bash(obsidian outline *)
  - Bash(obsidian history *)
  - Read
  - Glob
  - Grep
---

# Vault Inspect

Diagnostic sweep on the Obsidian vault "Loose Ends". Two rule families:

- **Structural** — vault-wide: orphans, dead-ends, broken links, missing
  frontmatter, stale, oversized, convention violations.
- **Wiki-semantic** — `owner: ai` + `type: wiki` pages only: page_type
  validation, hierarchy, neutral-definition opening, source-link format,
  Software Catalog schema, anti-staleness, Breadcrumbs hygiene.

The rule definitions and detection methods live in
`${CLAUDE_PLUGIN_ROOT}/references/inspect-rules.md`. Read that file
before running the sweep — it is the source of truth for what to check
and how.

## Usage

```
/vault-inspect                       # both scopes (default)
/vault-inspect --structural          # S-* rules only
/vault-inspect --wiki                # W-* rules only
/vault-inspect --folder="path/to/x"  # restrict to a folder
/vault-inspect --focus=orphans       # one rule category (structural)
```

## Canonical conventions

Read these for the *content* of conventions (the rule reference describes
how to *detect* violations):

- `${CLAUDE_PLUGIN_ROOT}/references/inspect-rules.md` — rule set with IDs
- `${CLAUDE_PLUGIN_ROOT}/references/vault-conventions.md` — folder
  structure, frontmatter, naming
- `~/Loose Ends/.claude/rules/wiki.md` — wiki schema and skeletons
- `~/Loose Ends/.claude/rules/catalog.md` — Software Catalog schema

## Required skills

- **Skill(obsidian:obsidian-cli)** — for diagnostic commands (`orphans`,
  `deadends`, `unresolved`, `properties`, etc.)

## Workflow

### 1. Resolve scope

- No flags → run both `--structural` and `--wiki`.
- `--structural` → S-* rules only.
- `--wiki` → W-* rules only (restrict to wiki pages).
- `--folder=PATH` → restrict whichever scope was chosen to that folder.
- `--focus=CATEGORY` → run one rule category (structural):
  - `orphans` (S-1), `deadends` (S-2), `broken` (S-3),
    `frontmatter` (S-4), `stale` (S-5), `oversized` (S-6),
    `conventions` (S-7).

### 2. Run the rule set

Apply rules in ID order (S-1, S-2, … then W-1, W-2, …). For each rule:

1. Read its detection method from `inspect-rules.md`.
2. Run the obsidian-cli command(s) it specifies.
3. Collect violating files into the report bucket for that rule.

The default sweep samples; pass `--full` to check every note.

### 3. Score and report

Aggregate findings, then emit a scannable structured report.

```markdown
## Vault Inspect Report — YYYY-MM-DD

### Summary
| Scope | Rule | Issues | Severity |
|---|---|---|---|
| S | Orphaned notes (S-1) | 7 | medium |
| S | Broken links (S-3) | 2 | high |
| S | Missing frontmatter (S-4) | 12 | medium |
| W | Missing parent (W-8) | 3 | medium |
| W | Catalog schema drift (W-17) | 4 | medium |
| W | Stale wiki pages (W-16) | 6 | low |

### Top issues by rule

#### S-1 Orphaned Notes (7)
1. `Python Decorators.md` — no incoming links
2. `Old Meeting.md` — no incoming links
…

#### S-3 Broken Links (2)
1. `[[Missing Note]]` in `Developer Notes.md:42`
…

#### W-13 Missing Neutral Definition (3)
- [[Jujutsu (jj)]] — opens with `## Overview` heading
…

### Recommendations
1. **High priority:** Fix 2 broken links (blocks navigation)
2. **Medium priority:** Add frontmatter to 12 notes
3. **Low priority:** Review 4 stale notes

Run `/note-cleanup` to start fixing these, or `@note-editor` for
targeted rewrites.
```

### 4. After reporting

Ask the user which actions to take. Don't auto-fix — surface findings,
suggest a next skill or agent. Common follow-ups:

- Structural fixes → `/note-cleanup` (forks to `vault-curator`)
- Wiki schema migration → `Skill(catalog-evaluate)` for catalog drift,
  `Skill(wiki-create)` (stub mode) for missing-page relation targets
- Specific page rewrites → `@note-editor`

If the user approves fixes, run them, then:
- Update `Reference/index.md` if wiki pages were touched.
- Append a lint entry to `Reference/log.md`:
  ```
  ## [YYYY-MM-DD] inspect | scope
  - Rules run: S-*, W-* (or subset)
  - Issues found: N
  - Issues fixed: M
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

- **Report findings; don't auto-fix without approval.** Contradictions
  (W-4) require source-level investigation, not guessing.
- **Don't bulk-rewrite** first-person eval headings (W-19) — surface as
  migration suggestions; the user migrates each page when next touching it.
- **Suggest sources to seek out** for gap-filling on thin pages (W-5).
- **Respect velocity overrides** (W-16) — `velocity: stable` pages are
  intentionally not anti-stale-checked.

## Implementation notes

See `${CLAUDE_PLUGIN_ROOT}/references/obsidian-cli-gotchas.md` for
obsidian-cli patterns and command examples (search, backlinks,
property:set).

## Follow-up

- `/note-cleanup` — interactive cleanup session (forks to `vault-curator`)
- `Skill(wiki-create)` — create missing pages flagged by W-3
- `Skill(catalog-evaluate)` — fix Software Catalog drift flagged by W-17
- Re-run `/vault-inspect` to confirm fixes
