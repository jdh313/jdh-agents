---
name: wiki-create
description: Create or update a wiki page. Detects mode from input — ingest mode if the user provides a URL/file/pasted text (save to Sources/, draft wiki pages, update index and log); stub mode otherwise (lightweight "what is X" page from common knowledge, no source required). Use when user says "ingest this", "add to wiki", "process this article", "stub this", "add a wiki page for", "create a page for", or provides a source to add to the knowledge base. Merger of the former `wiki-ingest` and `wiki-stub` skills.
---

# Wiki Create

Create or update a Knowledge Wiki page. Two modes, picked by the shape of
the input:

- **Ingest mode** — the user provides a source (URL, file path, pasted text,
  or an existing file in `Sources/`). Fetch/save the source, draft wiki
  pages drawing on it, update index and log.
- **Stub mode** — no source provided. Create a lightweight "what is X" page
  from common knowledge. Faster path, no source attribution. Can be
  deepened later via `wiki-refresh` or by re-running ingest mode with a
  source.

The page can move between depths over its life: stub → ingest expansion →
refresh → graduate (split into `expands:` children). This skill only
handles initial creation; updates flow through `wiki-refresh` and
`wiki-graduate`.

## Mode detection

| Input | Mode | Notes |
|---|---|---|
| URL or "ingest <url>" | ingest | Defuddle the URL, then continue |
| Path to a local file | ingest | Read content, save copy to `Sources/` |
| Pasted text block | ingest | Save the text to `Sources/` first |
| A path already inside `Sources/` | ingest | Skip the Sources save step |
| Just a topic name ("stub Pressure Advance") | stub | Common-knowledge baseline |
| Topic + "what is X" / "add a page for" | stub | Same as above |

If the request is ambiguous, ask: "Do you have a source for this, or
should I stub it from common knowledge?"

## Canonical conventions

Read these rule files before producing output — they are the source of
truth for schema and skeletons:

- `~/Loose Ends/.claude/rules/wiki.md` — page types, skeletons, page
  structure conventions, Breadcrumbs hierarchy (`up:` vs `expands:`)
- `~/Loose Ends/.claude/rules/catalog.md` — Software Catalog schema and
  gist-hub-plus-Decision-child split

Sections this skill depends on:
- Wiki frontmatter schema → wiki.md `## Wiki Schema`
- `concept` skeleton (general) → wiki.md `### concept — explanation of a thing or idea`
- `concept` as a gist hub → wiki.md `### concept as a gist hub`
- `how-to` skeleton → wiki.md `### how-to — procedure with a single canonical path`
- `evaluation` skeleton → wiki.md `### evaluation — Decision child of a catalog gist hub`
- Page structure conventions → wiki.md `## Page Structure Conventions`
- Hierarchy fields → wiki.md `## Hierarchy via Breadcrumbs`
- Breadcrumbs codeblock patterns → wiki.md `### Codeblock patterns`
- Catalog gist hub frontmatter → catalog.md `### Gist hub`

## Required skills

- **Skill(obsidian:obsidian-cli)** — note creation, search, frontmatter
- **Skill(obsidian:obsidian-markdown)** — Obsidian-flavored markdown
- **Skill(obsidian:defuddle)** — *ingest mode only*: fetch + parse URLs
- **Skill(obsidian:obsidian-bases)** — if updating any base entries

## Guards (both modes)

- **Catalog folder is catalog-only.** Never create a page inside
  `Reference/Tools/Software Catalog/` via this skill. That folder is
  managed by `catalog-evaluate` — route there for catalog entries.
- **Neutral-definition opening is non-negotiable.** If you don't know
  what X is well enough to write one neutral sentence, back out — ask
  for context or a source first.
- **Check for an existing page before creating.** Use
  `obsidian search query="..." format=json` and `Reference/index.md`.
  If a page exists, suggest `wiki-refresh` instead.

## Workflow — ingest mode

### 1. Capture the source

- **URL**: Invoke `Skill(obsidian:defuddle)` to extract clean markdown.
  Fall back to WebFetch if defuddle fails.
- **File**: Read the file content.
- **Pasted text**: Use as-is.

Save to `Sources/YYYY-MM-DD Title.md` via `Skill(obsidian:obsidian-cli)`.
Frontmatter:

```yaml
---
owner: ai
type: source
source_url: ""
source_type: article  # article | paper | video | podcast | book | conversation
source_author: ""     # optional
date_ingested: YYYY-MM-DD
tags: []
---
```

Skip this step if the input is already a path inside `Sources/`.

### 2. Discuss with user

Before writing wiki pages, briefly surface:
- 3-5 key takeaways from the source
- Which existing wiki pages (if any) this relates to
- Any contradictions with existing wiki content

Ask: "Does this capture what matters, or should I emphasize something
different?"

### 3. Create/update wiki pages

For each significant concept, entity, or topic in the source:

**If a wiki page exists**: update it — add the source to frontmatter
`sources:` list, integrate new information, note any contradictions.

**If no wiki page exists**: create one. See the page-type table and
placement section below.

### 4. Update index

Read `Reference/index.md`. Add/update entries for every page touched.
Each entry: `- [[Page Name]] — one-line summary (N sources)`.

### 5. Update log

Append to `Reference/log.md`:

```
## [YYYY-MM-DD] ingest | Source Title
- Source: [[Sources/YYYY-MM-DD Title]]
- Pages created: [[Page1]], [[Page2]]
- Pages updated: [[Page3]]
- Key insight: one-sentence summary
```

### 6. Report

Tell the user:
- What was ingested
- Pages created/updated (with counts)
- Any contradictions flagged
- Suggested follow-up sources or questions

## Workflow — stub mode

### 1. Check if a page already exists

Search the wiki (via obsidian-cli or `Reference/index.md`) for the topic.
If a page exists, suggest `wiki-refresh` instead.

### 2. Determine what to create

Pick the right page type. Full skeletons live in wiki.md
`## Page Types & Skeletons` — don't reproduce them here.

| Topic | Page type | Notes |
|---|---|---|
| Tool / service / system the user has formed an opinion on | catalog gist hub (`page_type: concept`) | Route to `Skill(catalog-evaluate)` — it handles lifecycle/kind/relations and offers to create a Decision child. Don't stub catalog entries from here. |
| Tool encountered casually (no opinion yet) | `page_type: concept` outside catalog folder, or defer | If user wants a verdict, route to `catalog-evaluate`. |
| Procedure with one canonical path | `page_type: how-to` | |
| Definition / pattern / topic landing page | `page_type: concept` | Default. Topic landing pages add a Breadcrumbs codeblock. |

### 3. Place the page

Use the wiki location decision tree (wiki.md `### Where wiki pages live`):

| Topic area | Destination |
|---|---|
| Software tools, CLIs, apps, frameworks | `Reference/Tools/Software Catalog/` (only via `catalog-evaluate`) |
| Languages, libraries, patterns, AI | `Reference/Developer/` |
| DevOps, cloud, systems, home automation | `Reference/Infrastructure/` |
| 3D printing, Klipper | `Reference/3D Printing/` |
| Job search strategy | `Personal/Career/Job Search/` |
| Other topics | Follow vault Location Decision Tree in CLAUDE.md |

### 4. Create frontmatter

Use the wiki schema from wiki.md `## Wiki Schema`. Hierarchy fields:

- **`up:`** — topic specialization (e.g. `Pressure Advance` →
  `up: [[3D Printing]]`).
- **`expands:`** — altitude descent (e.g. `Jujutsu Commands` →
  `expands: [[Jujutsu (jj)]]`). Stubs rarely use this — it usually
  emerges later when a topic accumulates enough to split.

A page can carry both, but most stubs only need one. Top-level topic
pages omit both. Verify the parent page exists before writing — if it
doesn't, ask whether to also stub the parent or omit the field.

### 5. Write content using the canonical skeleton

Emit the H2 headings in the order defined by the relevant skeleton in
wiki.md. Omit sections that don't apply. Never reorder.

For topic-area landing pages (children expected to attach via `up:`),
include a `## Pages in this area` Breadcrumbs codeblock:

````markdown
```breadcrumbs
type: tree
field-groups: [downs]
sort: basename asc
```
````

If the page is anticipated to become a gist hub later (children will
declare `expands:`), see wiki.md `### concept as a gist hub` for the
slimmer skeleton. Most fresh stubs aren't gist hubs yet — leave the
upgrade to `wiki-graduate` once accumulation demands it.

> [!note] No `depth:` by default
> Omit `depth:` from Breadcrumbs codeblocks. Unbounded trees are correct
> for almost every page. Add `depth:` only with a specific reason.

Depth follows usage — write what you know from context. Don't research
extensively; that's what ingest mode is for.

### 6. Update index and log

- Add entry to `Reference/index.md`: `- [[Page Name]] — one-line summary`
- Append to `Reference/log.md`:
  ```
  ## [YYYY-MM-DD] stub | Page Name
  - Created: [[Page Name]]
  - Context: brief note on why this was created
  ```

### 7. Report

Tell the user:
- Page created and where it lives
- What's included vs what's thin (so they know what to deepen later)
- Suggest `wiki-refresh` or re-running this skill with a source for deeper
  coverage

## Page placement (both modes)

Wiki pages go in the vault folder matching their topic — see the table
in stub mode step 3. Mode-specific notes:

- **Ingest mode** can create multiple pages per session (one per
  concept in the source). Stub mode creates one page per invocation.
- **Software Catalog folder** is off-limits to this skill — both modes
  route catalog work to `Skill(catalog-evaluate)`.

## Page structure (both modes)

Always required, regardless of mode or page_type (per wiki.md
`## Page Structure Conventions`):

- **Neutral definition first.** The first non-frontmatter line is a 1-2
  sentence *neutral* "what is X" statement. No heading, no meta-text
  ("Parent page for..."), no first-person opinion. If you can't write
  one such sentence, you don't know the topic well enough — back out.
- **No hard-wrapped prose.** Each paragraph or list item is a single
  long line. Tables, code blocks, and YAML frontmatter keep their
  natural line structure.
- **No first-person in body/headings.** Prefer `## Advantages` over
  `## What I liked`.
- **Generic vs personal separation.** Generic facts in `## What it is`,
  `## How it works`, `## Key concepts`; personal content in
  `## In this vault`, `## My use`, or `## Decision`. Never blend.
- **Section-level self-containment.** Each H2 stands alone —
  `wiki-query` retrieval loses surrounding context, so restate critical
  details inside the section.
- **Contradictions/open questions in callouts** (`> [!note]` or
  `> [!warning]` per the semantics in wiki.md).

Hierarchy rules:

- Every non-top-level wiki page MUST set `up:` pointing to a parent
  page. `up:` can point to any vault note, not just other wiki pages.
- Top-level topic pages omit `up:`.
- Breadcrumbs auto-derives `down:` — never write `down:` manually.
- Multi-parent uses a YAML list.

**No MOCs** — this wiki does not use dedicated `type: moc` pages. New
topic landing pages are regular `type: wiki` pages with a Breadcrumbs
codeblock to auto-list children.

**Valid Breadcrumbs v4 codeblock fields**: `type`, `title`, `start-note`,
`fields`, `field-groups`, `depth`, `flat`, `collapse`, `merge-fields`,
`dataview-from`, `content`, `sort`, `field-prefix`, `show-attributes`,
`mermaid-direction`, `mermaid-renderer`, `mermaid-curve`. **There is no
`dir:` field** — use `field-groups: [downs]` for children, `[ups]` for
ancestors.

## Pre-finish checklist

Before declaring complete, verify every new or modified file:

**Source notes (ingest mode only, in `Sources/`)**:
- [ ] `owner: ai` set
- [ ] `type: source` set
- [ ] `source_url` set if available (empty string OK)
- [ ] `source_type` set (article | paper | video | podcast | book | conversation)
- [ ] `source_author` set if known
- [ ] `date_ingested` set
- [ ] `tags` use `topic/*` namespace in kebab-case
- [ ] Filename matches `YYYY-MM-DD Title.md`

**Wiki pages (both modes)**:
- [ ] `owner: ai` set
- [ ] `type: wiki` set
- [ ] `page_type` set (`concept` | `how-to` | `evaluation`)
- [ ] `up:` set for non-top-level pages — top-level topic pages omit it
- [ ] `sources:` entries use `[[Sources/...]]` prefix (ingest mode);
      omitted or empty for stub mode
- [ ] `date_created` and `date_updated` set (underscored form only —
      never `date created` / `date modified`)
- [ ] `tags` use `topic/*` namespace in kebab-case
- [ ] Page placed in correct vault folder for its topic
- [ ] Wikilinks use bare names: `[[Page Name]]`
- [ ] First non-frontmatter line is a 1-2 sentence neutral definition
- [ ] H2 ordering matches the canonical skeleton for the declared
      `page_type` (see wiki.md)
- [ ] Generic facts and personal content are in separate sections
- [ ] Body cites which source supports each non-trivial claim
      (ingest mode)

**Index and log (both modes)**:
- [ ] `Reference/index.md` updated with new pages (and sources for
      ingest mode)
- [ ] `Reference/log.md` appended with `## [YYYY-MM-DD] ingest|stub | Title`
- [ ] Statistics section in `index.md` updated (page count, source
      count, last_updated date)

If any item fails, fix it before reporting completion. `vault-inspect`
will catch them later, but it's cheaper to get them right at write time.

## Quality rules

- **Common knowledge is fine without sources** in stub mode.
- **Don't invent specific technical claims** (benchmarks, version
  behavior, gotchas) in either mode. In ingest mode, cite which source
  supports each non-trivial claim. In stub mode, skip the claim if
  unsure.
- **Flag contradictions explicitly.** Don't silently resolve them.
- **Pages should be useful even in stub form** — a good overview is
  enough. Refuse to write a page without a neutral-definition opening
  sentence.

## Implementation notes

See `${CLAUDE_PLUGIN_ROOT}/references/obsidian-cli-gotchas.md` for
obsidian-cli patterns, gotchas, and command examples used by all wiki
skills.
