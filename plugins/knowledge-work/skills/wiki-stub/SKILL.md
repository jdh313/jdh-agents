---
name: wiki-stub
description: Quickly create a wiki page for a tool or concept encountered during work. No source required — uses common knowledge for a "what is X" baseline. Use when user says "stub this", "add a wiki page for", "create a page for", or when a tool/concept comes up that should have a wiki page but doesn't.
---

# Wiki Stub

Create a lightweight wiki page when a tool or concept comes up during work. Faster than full ingest — no source document needed. The page can be deepened later via `wiki-ingest` or `wiki-refresh`.

## Canonical conventions

Read these rule files before producing output — they are the source of truth for schema and skeletons:

- `~/Loose Ends/.claude/rules/wiki.md` — page types, skeletons, page structure conventions, Breadcrumbs hierarchy (`up:` vs `expands:`)
- `~/Loose Ends/.claude/rules/catalog.md` — catalog schema (kind/lifecycle/relations) and gist-hub-plus-Decision-child split

Sections this skill depends on:
- Wiki frontmatter schema → wiki.md `## Wiki Schema`
- `concept` skeleton (general) → wiki.md `### concept — explanation of a thing or idea`
- `concept` as a gist hub → wiki.md `### concept as a gist hub`
- `how-to` skeleton → wiki.md `### how-to — procedure with a single canonical path`
- Page structure conventions (no hard-wrap, neutral definition, no first-person, etc.) → wiki.md `## Page Structure Conventions`
- Hierarchy fields → wiki.md `## Hierarchy via Breadcrumbs`
- Breadcrumbs codeblock patterns → wiki.md `### Codeblock patterns`
- Catalog gist hub frontmatter → catalog.md `### Gist hub`

## Required skills
- **Skill(obsidian:obsidian-cli)** — for note creation, search, and frontmatter
- **Skill(obsidian:obsidian-markdown)** — for proper Obsidian-flavored markdown

## When to use

- A tool or concept comes up in conversation or work that has no wiki page
- You want to capture "what is X" quickly without finding a source first
- You're linking from a project note and the link target doesn't exist yet

## Workflow

### 1. Check if a page already exists

Search the wiki (via obsidian-cli or `Reference/index.md`) for the topic. If a page exists, suggest `wiki-refresh` instead if it needs updating.

### 2. Determine what to create

Pick the right page type based on the topic. Full skeletons live in wiki.md `## Page Types & Skeletons` — don't reproduce them here.

| Topic | Page type | Notes |
|---|---|---|
| Tool / service / system the user has formed an opinion on | catalog gist hub (`page_type: concept`) | Route to `Skill(catalog-evaluate)` for the full workflow — that skill handles lifecycle/kind/relations and offers to create a Decision child. Don't stub catalog entries through `wiki-stub`. |
| Tool encountered casually (no opinion yet, no decision needed) | not a catalog candidate; create as `page_type: concept` outside the catalog folder OR defer | If the user wants a verdict, route to `catalog-evaluate`. |
| Procedure with one canonical path (calibration, install, recipe) | `page_type: how-to` | |
| Definition / pattern / topic landing page | `page_type: concept` | Default. Topic-area landing pages also use `concept` and add a Breadcrumbs codeblock. |

**Guard:** never create a page inside `Reference/Tools/Software Catalog/` via `wiki-stub`. That folder is catalog-only — route to `catalog-evaluate`.

### 3. Place the page

Use the wiki location decision tree (wiki.md `### Where wiki pages live`). Common destinations: `Reference/Developer/`, `Reference/Infrastructure/`, `Reference/3D Printing/`, etc.

### 4. Create frontmatter

Use the wiki schema from wiki.md `## Wiki Schema`. The two hierarchy fields:

- **`up:`** — topic specialization. The new page is a sub-topic of a broader area (e.g. `Pressure Advance` → `up: [[3D Printing]]`).
- **`expands:`** — altitude descent. The new page is a deeper layer of an existing page (e.g. `Jujutsu Commands` → `expands: [[Jujutsu (jj)]]`). Stubs rarely use this — it usually emerges later when a topic accumulates enough material to split.

A page can carry both, but most stubs only need one. Top-level topic pages omit both. Verify the parent page exists before writing — if it doesn't, ask whether to also stub the parent or omit the field.

### 5. Write content using the canonical skeleton

Emit the H2 headings in the order defined by the relevant skeleton in wiki.md. Omit sections that don't apply. Never reorder them.

**Always required, regardless of type** (per wiki.md `## Page Structure Conventions`):

- The first non-frontmatter line is a 1-2 sentence *neutral* "what is X" statement. Do not open with `## Introduction`, `## Overview`, meta-text ("Parent page for..."), or personal opinion. The neutral definition is non-negotiable — if you don't know what X is well enough to write one sentence, don't stub the page.
- No hard-wrapped prose. Each paragraph or list item is a single long line. Tables, code blocks, and YAML frontmatter keep their natural line structure.
- Avoid first-person narrative in body and headings. Prefer `## Advantages` over `## What I liked`.
- Keep generic facts and personal use in *separate* sections.
- Each H2 should stand on its own without earlier context.

For topic-area landing pages (children expected to attach via `up:`), include a `## Pages in this area` Breadcrumbs codeblock:

````markdown
```breadcrumbs
type: tree
field-groups: [downs]
sort: basename asc
```
````

If the page is anticipated to become a gist hub later (children will declare `expands:`), see wiki.md `### concept as a gist hub` for the slimmer skeleton with both `## Going deeper` (`field-groups: [expansions]`) and `## Related topics` (`field-groups: [downs]`) blocks. Most fresh stubs aren't gist hubs yet — leave the upgrade to a later refresh once the topic accumulates expansions.

> [!note] No `depth:` by default
> Omit `depth:` from Breadcrumbs codeblocks. Unbounded trees are correct for almost every page. Add `depth:` only with a specific reason (capping a runaway tree, or flattening a deep taxonomy).

Depth follows usage — write what you know from context. Don't research extensively; that's what `wiki-refresh` is for.

### 6. Update index and log

- Add entry to `Reference/index.md`: `- [[Page Name]] — one-line summary`
- Append to `Reference/log.md`:
  ```
  ## [YYYY-MM-DD] stub | Page Name
  - Created: [[Page Name]]
  - Context: brief note on why this was created (e.g., "encountered during K8s storage work")
  ```

### 7. Report

Tell the user:
- Page created and where it lives
- What's included vs what's thin (so they know what to deepen later)
- Suggest `wiki-refresh` or `wiki-ingest` for deeper coverage

## Quality Rules

- Common knowledge is fine without sources — this is a stub
- Don't invent specific technical claims (benchmarks, version behavior)
- If you're unsure about something, skip it rather than guessing
- Pages should be useful even in stub form — a good overview is enough
- Refuse to create a page without a neutral-definition opening sentence. If the stub can't start with "X is a ..." or "X is the ...", back out and ask the user for one sentence of context first.

## Implementation Notes

See `${CLAUDE_PLUGIN_ROOT}/references/obsidian-cli-gotchas.md` for obsidian-cli patterns and command examples.
