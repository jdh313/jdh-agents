---
name: wiki-ingest
description: Process a source into the Knowledge Wiki — saves to Sources/, creates/updates wiki pages, updates index and log. Use when user says "ingest this", "add to wiki", "process this article", or provides a URL/file to add to the knowledge base.
---

# Wiki Ingest

Process a source document into the Knowledge Wiki.

## Required skills
- **Skill(obsidian:defuddle)** — for fetching and parsing URLs
- **Skill(obsidian:obsidian-markdown)** — for proper Obsidian-flavored markdown (wikilinks, callouts, frontmatter)
- **Skill(obsidian:obsidian-cli)** — for note creation, search, and frontmatter updates
- **Skill(obsidian:obsidian-bases)** — if updating any base entries

## Input

The user provides one of:
- A URL to an article/page
- A file path to a document
- Pasted text content
- A file already in `Sources/`

## Workflow

### 1. Capture the source

- **URL**: Invoke `Skill(obsidian:defuddle)` to extract clean markdown. If defuddle fails, fall back to WebFetch.
- **File**: Read the file content.
- **Pasted text**: Use as-is.

Save to `Sources/YYYY-MM-DD Title.md` using `Skill(obsidian:obsidian-cli)` to ensure proper note creation. Frontmatter:

```yaml
---
owner: ai
type: source
source_url: ""
source_type: article  # article | paper | video | podcast | book | conversation
date_ingested: YYYY-MM-DD
tags: []
---
```

### 2. Discuss with user

Before writing wiki pages, briefly surface:
- 3-5 key takeaways from the source
- Which existing wiki pages (if any) this relates to
- Any contradictions with existing wiki content

Ask: "Does this capture what matters, or should I emphasize something different?"

### 3. Create/update wiki pages

For each significant concept, entity, or topic in the source:

**If a wiki page exists**: Update it with new information, add the source to frontmatter `sources:` list, note any contradictions.

**If no wiki page exists**: Create one in the appropriate vault folder (see Location section below) with:

```yaml
---
owner: ai
type: wiki
page_type: concept     # concept | how-to | evaluation
up:
  - "[[Parent Page]]"
sources:
  - "[[Sources/YYYY-MM-DD Title]]"
date_created: YYYY-MM-DD
date_updated: YYYY-MM-DD
tags: []
---
```

Pick the `page_type` that matches the page's shape. Most source-driven
ingests produce `concept` pages. Software Catalog entries are always
`evaluation` and use the extended catalog schema (see `wiki-stub`). How-to
pages capture single-path procedures. The canonical skeleton for each type
lives in `~/dotfiles/claude/rules/11-knowledge-wiki.md` → **Page Types &
Skeletons**.

### Location for new wiki pages

Wiki pages go in the vault folder matching their topic:

| Topic area | Destination |
|---|---|
| Software tools, CLIs, apps, frameworks | `Reference/Tools/Software Catalog/` |
| Languages, libraries, patterns, AI | `Reference/Developer/` |
| DevOps, cloud, systems, home automation | `Reference/Infrastructure/` |
| 3D printing, Klipper | `Reference/3D Printing/` |
| Job search strategy | `Personal/Career/Job Search/` |
| Other topics | Follow vault Location Decision Tree in CLAUDE.md |

**Hierarchy (`up:` field)** — Every non-top-level wiki page MUST set `up:` pointing to a parent page. `up:` can point to any vault note, not just other wiki pages. Top-level topic pages omit `up:`. Breadcrumbs auto-derives `down:` — never write `down:` manually. Multi-parent uses a YAML list. See the global rule (`~/dotfiles/claude/rules/11-knowledge-wiki.md`) for full hierarchy conventions.

**No MOCs** — This wiki does not use dedicated `type: moc` pages. If a new page would be the first in a topic with no existing parent, either (a) create it as top-level (no `up:`), or (b) create a regular `type: wiki` topic page to act as its parent. The topic page should include a Breadcrumbs codeblock to auto-list children:
\`\`\`breadcrumbs
type: tree
field-groups: [downs]
depth: [0, 2]
sort: basename asc
\`\`\`

**Valid Breadcrumbs v4 codeblock fields**: `type`, `title`, `start-note`, `fields`, `field-groups`, `depth`, `flat`, `collapse`, `merge-fields`, `dataview-from`, `content`, `sort`, `field-prefix`, `show-attributes`, `mermaid-direction`, `mermaid-renderer`, `mermaid-curve`. **There is no `dir:` field** — use `field-groups: [downs]` for children, `[ups]` for ancestors.

**Self-contained basics**: Every wiki page should answer "what is X" without
needing external docs. Include a clear definition/overview even for pages
created from a narrow source — the page is the reference, not just a summary
of the source.

**Depth follows usage**: Cover what we'd reasonably look up again. Document
the commands, patterns, and config we actually use. Skip deep internals or
features we haven't touched. The wiki mirrors working knowledge, not
exhaustive documentation.

Structure wiki pages using the canonical skeleton for the chosen
`page_type` — see `~/dotfiles/claude/rules/11-knowledge-wiki.md` → **Page
Types & Skeletons** for the exact H2 ordering. The shape is:

- **Neutral definition first** (first line after frontmatter, no heading): 1-2
  sentences of neutral "what is X" — no personal opinion, no `##
  Introduction`, no meta-text.
- **Generic / personal split**: generic facts in `## What it is`, `## How it
  works`, `## Key concepts`; personal content in `## In this vault`, `## My
  use`, or `## Decision`. Never blend them.
- **Section-level self-containment**: each H2 stands alone — `wiki-query`
  retrieval loses surrounding context, so restate critical details.
- Contradictions or open questions go in callouts (`> [!note]` or
  `> [!warning]` per the semantics in the rules file).

Use `Skill(obsidian:obsidian-markdown)` for proper Obsidian syntax — wikilinks, callouts, embeds, and frontmatter formatting.

### 4. Update index

Read `Reference/index.md`. Add/update entries for every page touched.
Each entry: `- [[Page Name]] — one-line summary (N sources)`

### 5. Update log

Append to `Reference/log.md`:
```
## [YYYY-MM-DD] ingest | Source Title
- Source: [[Sources/YYYY-MM-DD Title]]
- Pages created: [[Page1]], [[Page2]]
- Pages updated: [[Page3]]
- Key insight: one-sentence summary
```

### 6. Pre-finish checklist

Before declaring the ingest complete, verify EVERY new or modified file against this checklist:

**Source notes (`Sources/`)**:
- [ ] `owner: ai` set
- [ ] `type: source` set
- [ ] `source_url` set if available (empty string OK if not applicable)
- [ ] `source_type` set (article | paper | video | podcast | book | conversation)
- [ ] `source_author` set if known (skip for multi-source syntheses)
- [ ] `date_ingested` set
- [ ] `tags` use `topic/*` namespace in kebab-case
- [ ] Filename matches `YYYY-MM-DD Title.md`

**Wiki pages**:
- [ ] `owner: ai` set
- [ ] `type: wiki` set
- [ ] `page_type` set (concept | how-to | evaluation)
- [ ] `up:` set (REQUIRED for non-top-level pages — top-level topic pages omit it)
- [ ] `sources:` entries use `[[Sources/...]]` prefix
- [ ] `date_created` and `date_updated` set (underscored form only — never `date created` / `date modified`)
- [ ] `tags` use `topic/*` namespace in kebab-case
- [ ] Page placed in correct vault folder for its topic
- [ ] Wikilinks use bare names: `[[Page Name]]`
- [ ] Body cites which source supports each non-trivial claim
- [ ] First non-frontmatter line is a 1-2 sentence neutral definition (no heading, no personal opinion, no meta-text)
- [ ] H2 ordering matches the canonical skeleton for the declared `page_type` (see rules file)
- [ ] Generic facts and personal content are in separate sections, not blended

**Index and log**:
- [ ] `Reference/index.md` updated with new pages and sources
- [ ] `Reference/log.md` appended with `## [YYYY-MM-DD] ingest | Title` entry
- [ ] Statistics section in index.md updated (page count, source count, last_updated date)

If any item fails, fix it before reporting completion. Do not declare an ingest done with frontmatter convention violations — wiki-lint will catch them later, but it's cheaper to get them right at write time.

### 7. Report

Tell the user:
- What was ingested
- Pages created/updated (with counts)
- Any contradictions flagged
- Suggested follow-up sources or questions

## Quality Rules

- Never invent specific technical claims not in the source
- Common knowledge (definitions, standard descriptions) is fine without citation
- Cite which source supports specific claims (benchmarks, gotchas, version behavior) when updating existing pages
- Flag contradictions explicitly — don't silently resolve them

## Implementation Notes

See `${CLAUDE_PLUGIN_ROOT}/references/obsidian-cli-gotchas.md` for obsidian-cli patterns, gotchas, and command examples used by all wiki skills.
