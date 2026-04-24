---
name: wiki-lint
description: Health-check the Knowledge Wiki for orphans, contradictions, stale content, and missing pages. Use when user says "lint the wiki", "wiki health check", "check knowledge base", or periodically during wiki maintenance.
---

# Wiki Lint

Health-check the Knowledge Wiki. Wiki pages are distributed across the vault,
identified by `owner: ai` + `type: wiki` frontmatter.

## Required skills
- **Skill(obsidian:obsidian-cli)** — for querying notes, properties, backlinks, and orphan detection
- **Skill(obsidian:obsidian-markdown)** — for any markdown rewrites during cleanup
- **Skill(obsidian:obsidian-bases)** — if any wiki content is exposed via a base

## Finding wiki pages

Wiki pages are no longer in a single folder. To find them:
- Read `Reference/index.md` for the catalog
- Search for `type: wiki` in frontmatter via `Skill(obsidian:obsidian-cli)`
- Sources are always in `Sources/`

## Checks

### 1. Orphan pages
Wiki pages with no inbound links from other wiki pages.
- Read all wiki pages, build a link graph
- Pages only linked from index.md are effectively orphans

### 2. Stale sources
Sources in `Sources/` that aren't referenced by any wiki page's `sources:` frontmatter.
These were ingested but their knowledge wasn't integrated.

### 3. Missing pages
Concepts referenced via wikilinks in wiki pages that don't have their own page yet.

### 4. Contradictions
Scan wiki pages for claims that conflict with each other.
Flag with the specific pages and sources involved.

### 5. Thin pages
Wiki pages with only one source. These may need enrichment or may indicate a topic worth deeper research.

### 6. Unverified claims
Scan for `[unverified]` markers left by previous ingest operations.

### 7. Cross-vault opportunities
Wiki pages that reference concepts covered elsewhere in the vault but don't link to them.

### 8. Missing `up:` field
Wiki pages without an `up:` field in frontmatter. Every page (except top-level topic pages) should have one — Breadcrumbs hierarchy depends on it. Suggest a parent. Note: top-level topic pages (e.g. `3D Printing`, `Job Search`) intentionally omit `up:`; don't flag them.

### 9. Stale MOC artifacts
Any leftover `type: moc` frontmatter, `moc` tag, or `MOC.md` filename from before MOCs were removed from the schema. Convert to regular `type: wiki` pages and rename if needed.

### 10. Source link format
Wiki pages whose `sources:` frontmatter entries don't start with `[[Sources/`. The schema requires the `Sources/` prefix on source links.

**Detection**: For each wiki page, parse the `sources:` frontmatter list. Flag any entry where the wikilink target doesn't start with `Sources/`.

**Fix**: Read the file, Edit the `sources:` block to add the `Sources/` prefix.

### 11. Tag convention
Tags that don't follow the vault's `#topic/something` namespace convention.

**Allowed top-level tags**:
- `topic/*` — for content topics (e.g., `topic/3d-printing`, `topic/career/job-search`)
- `type/*` — for note types if used
- `status/*` — for lifecycle if used

(`moc` tag is no longer allowed — flag any occurrences as stale MOC artifacts under check 9.)

### 12. Missing `owner: ai`
Wiki pages (identified via index.md or `type: wiki` frontmatter) that lack the `owner: ai` field.

### 13. Missing neutral definition
Wiki pages whose first non-frontmatter line is not a 1-2 sentence neutral
"what is X" statement.

**Detection heuristic**: read the first ~200 characters of the body
(excluding frontmatter). Flag if the first non-blank line is:
- A heading (starts with `#`) — the intro should be prose, not a section heading.
- A list item (starts with `-`, `*`, or a digit + `.`).
- Under 30 characters or over 400 characters.
- A meta-description ("Parent page for...", "This page tracks...",
  "Wiki entry on...").
- First-person opinion ("I like...", "My favorite...", "I use...").

**Fix**: propose a neutral opening sentence, ask the user to approve, then
insert before existing content.

### 14. Missing or mismatched `page_type`
Wiki pages without a `page_type` field in frontmatter, or where the declared
`page_type` doesn't match the observed skeleton.

**Detection**:
- Field absent → flag, suggest a type based on folder and structure
  (Software Catalog → `evaluation`, pages with numbered Procedure section →
  `how-to`, everything else → `concept`).
- Field present but skeleton mismatched → flag. Examples: `page_type:
  how-to` but no `## Procedure` heading; `page_type: evaluation` but no
  `## Decision` section and no `lifecycle:` frontmatter.

### 15. Frontmatter dialect drift
Wiki pages using the legacy spaced date fields (`date created`, `date
modified`) instead of the canonical underscored form (`date_created`,
`date_updated`). Primarily affects older Software Catalog pages.

**Detection**: parse YAML frontmatter. Flag any key exactly matching `date
created`, `date modified`, or `date created/modified` present alongside or
instead of the underscored equivalents.

**Fix**: on user approval, rename fields to the underscored form,
preserving values.

### 16. Stale pages
Wiki pages where `date_updated` is older than a threshold. Default:
365 days. Overridable per-page via a `velocity:` frontmatter field:

- `velocity: fast` → 90-day threshold (fast-moving topics)
- `velocity: stable` → no check (reference material that doesn't decay)
- unset → default 365 days

Skip pages marked `velocity: stable`. Flag others over threshold with their
last-updated date and suggest `wiki-refresh`.

### 17. Software Catalog schema (catalog-specific)

Only applies to pages in `Reference/Tools/Software Catalog/` or with
`page_type: evaluation`. Schema lives in
`~/dotfiles/claude/rules/12-software-catalog.md`.

**Detection (flag each independently):**

- **Old schema fields present** — `status:` (should be `lifecycle:`),
  `url:` (should be `homepage_url:`), `last-evaluated:` (hyphen; should
  be `last_evaluated:` underscore).
- **Missing `kind`** — catalog entries require `kind: component | resource | system`.
- **Missing `lifecycle`** — catalog entries require a verdict.
- **Invalid `lifecycle` value** — must be one of `adopt`, `trial`,
  `assess`, `hold`, `dropped`.
- **Missing `homepage_url`** — required when `kind: component` or
  `kind: resource`. Not required for `kind: system`.
- **`replaced_by` set on non-dropped entry** — `replaced_by` only makes
  sense when `lifecycle: dropped`.
- **Dead relation links** — wikilinks in `replaces`, `replaced_by`,
  `alternatives`, or `depends_on` that point to non-existent pages.
- **Non-evaluation page in Software Catalog folder** — any file in
  `Reference/Tools/Software Catalog/` with `page_type` other than
  `evaluation` is misplaced.

**Fix**: report findings; route fixes through `catalog-evaluate`
(migration) or `wiki-stub` (missing relation targets). Don't
auto-migrate silently.

## Output

Present findings as a structured report:

```
## Wiki Health Report — YYYY-MM-DD

### Orphan Pages (N)
- [[Page]] — no inbound links

### Stale Sources (N)
- [[Sources/Source]] — not referenced by any wiki page

### Missing Pages (N)
- [[Concept]] — referenced but doesn't exist

### Contradictions (N)
- Page A claims X; Page B claims Y (sources: ...)

### Thin Pages (N)
- [[Page]] — only 1 source

### Unverified Claims (N)
- [[Page#section]] — marked [unverified]

### Cross-Vault Links (N)
- [[Page]] could link to [[Related Note]]

### Missing Neutral Definition (N)
- [[Page]] — opens with heading/list/meta-text/opinion instead of a neutral "what is X"

### Missing or Mismatched `page_type` (N)
- [[Page]] — no `page_type`; suggest: concept
- [[Page]] — declares `page_type: how-to` but has no `## Procedure` section

### Frontmatter Dialect Drift (N)
- [[Page]] — uses `date created` / `date modified`; should be `date_created` / `date_updated`

### Stale Pages (N)
- [[Page]] — last updated YYYY-MM-DD (N days ago, threshold N)

### Software Catalog Schema (N)
- [[Page]] — old schema (`status:` / `url:` / `last-evaluated`); migrate via `catalog-evaluate`
- [[Page]] — missing `kind` / `lifecycle`
- [[Page]] — `kind: component` but no `homepage_url`
- [[Page]] — `replaced_by` set but `lifecycle` is not `dropped`
- [[Page]] — dead relation link: `replaces: [[Missing Tool]]`

### Suggested Actions
- [ ] Create page for X (referenced 3 times)
- [ ] Find additional sources for Y (thin page)
- [ ] Resolve contradiction between A and B
```

## After reporting

Ask the user which actions to take. Execute approved actions, then:
- Update `Reference/index.md`
- Append lint results to `Reference/log.md`

## Implementation Notes

See `${CLAUDE_PLUGIN_ROOT}/references/obsidian-cli-gotchas.md` for obsidian-cli patterns and command examples (search, backlinks, property:set).

## Quality Rules

- Report findings, don't auto-fix without approval
- Contradictions require source-level investigation, not guessing
- Suggest new sources to seek out for gap-filling
