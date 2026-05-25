---
name: wiki-refresh
description: Update an existing wiki page with current information from external sources. Use when user says "refresh this page", "update the wiki on", "this page is stale", "wiki-refresh", or when a wiki page needs updating with newer information.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(obsidian-cli *)
  - WebFetch
  - WebSearch
---

# Wiki Refresh

Update an existing wiki page by going external for current information
and folding it back in. Different from `wiki-create` (which starts from
a source) — this starts from an existing page and fills gaps or updates
stale content.

This skill drafts updates interactively; `@vault-reader` reads the
existing page and `@note-editor` executes the write.

## When to use

- A wiki page exists but feels thin or outdated
- User asks to update coverage on a topic
- A `wiki-query` reveals gaps that should be filled
- A Software Catalog entry has `lifecycle: assess` or a stale
  `last_evaluated` date (for verdict changes, route to `catalog-evaluate`
  instead)

## Vault tool usage

Use `obsidian-cli read file=...` to get current state before drafting changes. Use `obsidian-cli property:set name=date_updated value=<ISO date> file=...` after the refresh. Use `mcp__obsidian-mcp__patch_note` for surgical content updates within the page body; Edit only when patch_note can't anchor.

## Workflow

### 1. Pull the existing page

Dispatch via `@vault-reader`:

```markdown
## Intent
read wiki page at <path> with skeleton-drift diagnostic

## Constraints
- Return current frontmatter and body
- Flag skeleton drift vs the canonical skeleton for the declared `page_type`
  (per `~/Loose Ends/.claude/rules/wiki.md` → Page Types & Skeletons)
- Flag dialect drift (old `date created` / `date modified` with spaces vs
  canonical `date_created` / `date_updated`)
- Flag missing `page_type` field
- Flag `Workaround` / `Gotcha` sections without upstream issue/PR links

## Output shape
Page content + bulleted drift report.
```

### 2. Identify what needs updating

Surface to the user:

- Sections that are thin or missing
- Content that may be outdated (dates, version references, `[unverified]` markers)
- Skeleton drift (from the agent's drift report)
- Specific questions worth answering

Ask: "What should I focus on, or should I do a general refresh?" If
skeleton drift is significant, propose restructuring alongside content
updates — but never auto-restructure silently.

### 3. Research externally

Use WebSearch and/or WebFetch to gather current information. Focus on:

- What's changed since the page was last updated
- Filling identified gaps
- Verifying existing claims that may be stale

### 4. Draft the update

With the user: draft the integrated content (updated sections,
contradiction-flagging callouts, any restructuring). If the research
produced a substantial source worth keeping, also draft the
`Sources/YYYY-MM-DD Title.md` entry.

For quick refreshes from multiple small sources (docs pages,
changelogs), saving individual sources is optional — update the page
directly.

**Depth follows usage** — don't pad with exhaustive coverage. Add what's
useful for our working knowledge.

### 5. Dispatch the write

```markdown
## Intent
refresh wiki page at <path>

## Constraints
- Preserve existing accurate content
- Update `date_updated` (underscored form; migrate any legacy `date modified` while editing)
- Update `last_evaluated` for Software Catalog pages
- Add new sources to the `sources:` list
- If restructuring was agreed in step 2: reorder sections, add neutral-definition opener, split blended generic/personal content
- If a new source was drafted: also write `Sources/YYYY-MM-DD <Title>.md`
- Append to `Reference/log.md` with a refresh entry
- Update `Reference/index.md` if the page summary changed

## Input
<drafted page content, drafted source content if any, drafted index/log entries>

## Output shape
Confirm files modified with paths and a one-line change summary per file.
```

### 6. Report

Surface the agent's `## Result` to the user:

- What was updated and what changed
- Any contradictions found between old and new information
- Sections that are still thin (if any)
- Related pages that might also need refreshing

## Fold-back reflex

If, while working on something else in a session, you consult external
documentation on a topic the wiki already covers, surface: "We hit
external docs for X — should we fold the new info back into [[X]]?"
The wiki is meant to compound; external detours without fold-back leak
value.

## Quality rules

- Preserve accurate existing content — don't rewrite what's fine
- New specific claims (benchmarks, version behavior) should cite their source
- Common knowledge updates don't need formal source documents
- Flag when existing content contradicts new findings rather than silently replacing
- Never silently auto-restructure. Skeleton changes must be proposed and approved first, then applied alongside content updates.
