---
name: wiki-create
description: >-
  Create or update a wiki page. Detects mode from input — ingest mode if the
  user provides a URL/file/pasted text (save to Sources/, draft wiki pages);
  stub mode otherwise (lightweight "what is X" page from common knowledge, no
  source required). Use when user says "ingest this", "add to wiki", "process
  this article", "stub this", "add a wiki page for", "create a page for", "add a
  note about [topic]", "make a note about", "save a note about", or provides a
  source to add to the knowledge base. Merger of the former `wiki-ingest` and
  `wiki-stub` skills.
---

# Wiki Create

Create or update a Knowledge Wiki page. Two modes, picked by the shape of
the input:

- **Ingest mode** — user provides a source (URL, file, pasted text, or
  existing `Sources/` file). Fetch/save the source, draft wiki pages.
- **Stub mode** — no source provided. Create a lightweight "what is X"
  page from common knowledge. Can be deepened later via `wiki-refresh`
  or by re-running ingest mode.

This skill drafts interactively in the main session; `@note-editor`
executes all vault writes. Schema and skeleton conventions live in
`~/Loose Ends/.claude/rules/wiki.md` — the agent loads them.

## Vault tool usage

Use `obsidian-cli create name='...' content='...'` for new pages. Use `obsidian-cli property:set name=... value=... file=...` for frontmatter updates. Use `obsidian-cli read file=...` before any update. Use `mcp__obsidian-mcp__patch_note` for surgical in-body string replacement; Edit only when patch_note can't anchor.

## Mode detection

| Input | Mode | Notes |
|---|---|---|
| URL or "ingest <url>" | ingest | WebFetch the URL, then continue |
| Path to a local file | ingest | Read content, draft Sources/ entry |
| Pasted text block | ingest | Draft Sources/ entry from the paste |
| A path already inside `Sources/` | ingest | Skip the Sources draft |
| Just a topic name | stub | Common-knowledge baseline |
| "what is X" / "add a page for" | stub | Same as above |

If ambiguous: "Do you have a source for this, or should I stub it from
common knowledge?"

## Guards

- **Catalog folder is catalog-only.** Never create a page inside
  `Reference/Tools/Software Catalog/` via this skill. Route catalog work
  to `catalog-evaluate`.
- **Neutral-definition opening is non-negotiable.** If you cannot write
  a neutral 1-2 sentence "what is X" opening, back out — ask for context
  or a source.
- **Check for existing pages before creating.** Dispatch a lookup via
  `@vault-reader`; if a page exists, suggest `wiki-refresh` instead.

## Workflow — ingest mode

### 1. Capture the source

- **URL**: WebFetch to extract content
- **File**: Read the file content
- **Pasted text**: use as-is

### 2. Discuss with user

Surface 3-5 key takeaways, related existing wiki pages (if known), and
any contradictions. Ask: "Does this capture what matters, or should I
emphasize something different?"

### 3. Draft pages

For each significant concept in the source, draft the page content with
the user. Follow `~/Loose Ends/.claude/rules/wiki.md` for page_type,
skeleton, frontmatter shape, hierarchy fields. The user approves the
draft before write.

If a wiki page exists for a concept: draft the update integrating new
information; flag contradictions explicitly.

### 4. Dispatch the writes

Hand the drafted content to `@note-editor`:

```markdown
## Intent
write wiki pages from source

## Constraints
- Source: save to `Sources/YYYY-MM-DD <Title>.md` (skip if input was already a Sources/ path)
- Pages: write each drafted page to its placement path
- Schema: per `~/Loose Ends/.claude/rules/wiki.md`

## Input
<all drafted content: source frontmatter+body, each page frontmatter+body>

## Output shape
Confirm files created/modified with full paths.
```

### 5. Report

Surface the agent's `## Result` to the user (sources saved, pages
created/updated, contradictions flagged, suggested follow-ups).

## Workflow — stub mode

### 1. Check for existing page

Dispatch via `@vault-reader`:

```markdown
## Intent
check whether a wiki page exists for <topic>

## Constraints
- Search by title, aliases, and topic tags
- Restrict to `owner: ai` + `type: wiki`

## Output shape
Existing path if found, or "no match".
```

If a page exists, suggest `wiki-refresh` and stop.

### 2. Determine page type and placement

Pick page_type and placement per `~/Loose Ends/.claude/rules/wiki.md`.
Summary:

| Topic | Page type | Notes |
|---|---|---|
| Tool / service / system with a formed opinion | catalog tool entry (`concept`) | Route to `catalog-evaluate` instead |
| Tool encountered casually | `page_type: concept` outside catalog | |
| Procedure with one canonical path | `page_type: how-to` | |
| Definition / pattern / landing page | `page_type: concept` | Default |

| Topic area | Destination |
|---|---|
| Software tools (catalog) | via `catalog-evaluate` only |
| Languages, libraries, AI | `Reference/Developer/` |
| DevOps, cloud, home automation | `Reference/Infrastructure/` |
| 3D printing, Klipper | `Reference/3D Printing/` |
| Other | Follow vault Location Decision Tree |

### 3. Draft the page

Follow the canonical skeleton for the declared `page_type`. The user
approves the draft. Honor hierarchy: every non-top-level wiki page has
`up:` pointing to a parent — verify the parent exists (dispatch a quick
`@vault-reader` lookup if unsure).

### 4. Dispatch the write

```markdown
## Intent
write a stub wiki page at <path>

## Constraints
- page_type: <concept | how-to>
- Schema: per `~/Loose Ends/.claude/rules/wiki.md`
- Hierarchy: include `up:` to <parent>

## Input
<full drafted frontmatter + body>

## Output shape
Confirm file created with placement path.
```

### 5. Report

Surface the agent's `## Result`. Mention what's thin so the user knows
what to deepen later. Suggest `wiki-refresh` (or re-running ingest mode
with a source) for deeper coverage.

## Quality rules

- **Common knowledge is fine without sources** in stub mode.
- **Don't invent technical claims** (benchmarks, version-specific
  behavior). In ingest mode, cite the source for each non-trivial claim.
  In stub mode, skip the claim if unsure.
- **Flag contradictions explicitly.** Don't silently resolve them.
- **Refuse to write a page without a neutral-definition opening sentence.**
