---
name: wiki-stub
description: Quickly create a wiki page for a tool or concept encountered during work. No source required — uses common knowledge for a "what is X" baseline. Use when user says "stub this", "add a wiki page for", "create a page for", or when a tool/concept comes up that should have a wiki page but doesn't.
---

# Wiki Stub

Create a lightweight wiki page when a tool or concept comes up during work.
Faster than full ingest — no source document needed. The page can be deepened
later via `wiki-ingest` or `wiki-refresh`.

## Required skills
- **Skill(obsidian:obsidian-cli)** — for note creation, search, and frontmatter
- **Skill(obsidian:obsidian-markdown)** — for proper Obsidian-flavored markdown

## When to use

- A tool or concept comes up in conversation or work that has no wiki page
- You want to capture "what is X" quickly without finding a source first
- You're linking from a project note and the link target doesn't exist yet

## Workflow

### 1. Check if a page already exists

Search the wiki (via obsidian-cli or index) for the topic. If a page exists,
suggest `wiki-refresh` instead if it needs updating.

### 2. Determine `page_type` and location

Pick one of the three canonical page types (see
`~/dotfiles/claude/rules/11-knowledge-wiki.md` → **Page Types & Skeletons**
for full skeletons):

- **`concept`** — default. Definition + explanation of a thing or idea. Also
  covers topic-area landing pages.
- **`how-to`** — a procedure with one canonical path (calibrations,
  installations, recipes).
- **`evaluation`** — Software Catalog entries. **Do not create these via
  `wiki-stub`.** Route to `Skill(catalog-evaluate)` instead — the catalog
  has its own schema (`kind`, `lifecycle`, `replaces`, etc.) and workflow
  defined in `~/dotfiles/claude/rules/12-software-catalog.md`.

**Software tools** therefore never get stubbed through `wiki-stub`. If the
user asks to "stub" a tool, offer to route to `catalog-evaluate` instead.

**Non-software concepts** go in the standard wiki location per the rules
file topic table, usually `page_type: concept`.

**Guard:** never create a page with `page_type: concept` or `how-to` inside
`Reference/Tools/Software Catalog/`. That folder is catalog-only.

### 3. Create the page

#### Concept and how-to pages

Use the standard wiki schema:

```yaml
---
owner: ai
type: wiki
page_type: concept   # or: how-to
up:
  - "[[Parent Page]]"
sources: []
date_created: YYYY-MM-DD
date_updated: YYYY-MM-DD
tags: []
---
```

### 4. Write content using the canonical skeleton

The rules file defines the exact skeleton for each `page_type`. Emit the H2
headings in order, omit sections that don't apply, and **never** reorder them.

**Always required, regardless of type:**

- The first non-frontmatter line is a 1-2 sentence *neutral* "what is X"
  statement. Do not open with `## Introduction`, `## Overview`, meta-text
  ("Parent page for..."), or personal opinion. The neutral definition is
  non-negotiable — if you don't know what X is well enough to write one
  sentence, don't stub the page.
- Keep generic facts and personal use in *separate* sections. Do not blend
  them in one bullet list.
- Each H2 should stand on its own without earlier context (the retrieval
  self-containment rule from the rules file).

Depth follows usage — write what you know from context. Don't research
extensively; that's what `wiki-refresh` is for.

### 5. Update index and log

- Add entry to `Reference/index.md`: `- [[Page Name]] — one-line summary`
- Append to `Reference/log.md`:
  ```
  ## [YYYY-MM-DD] stub | Page Name
  - Created: [[Page Name]]
  - Context: brief note on why this was created (e.g., "encountered during K8s storage work")
  ```

### 6. Report

Tell the user:
- Page created and where it lives
- What's included vs what's thin (so they know what to deepen later)
- Suggest `wiki-refresh` or `wiki-ingest` for deeper coverage

## Quality Rules

- Common knowledge is fine without sources — this is a stub
- Don't invent specific technical claims (benchmarks, version behavior)
- If you're unsure about something, skip it rather than guessing
- Pages should be useful even in stub form — a good overview is enough
- Refuse to create a page without a neutral-definition opening sentence. If
  the stub can't start with "X is a ..." or "X is the ...", back out and ask
  the user for one sentence of context first.

## Implementation Notes

See `${CLAUDE_PLUGIN_ROOT}/references/obsidian-cli-gotchas.md` for obsidian-cli
patterns and command examples.
