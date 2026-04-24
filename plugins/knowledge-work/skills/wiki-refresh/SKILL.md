---
name: wiki-refresh
description: Update an existing wiki page with current information from external sources. Use when user says "refresh this page", "update the wiki on", "this page is stale", "wiki-refresh", or when a wiki page needs updating with newer information.
---

# Wiki Refresh

Update an existing wiki page by going external for current information and
folding it back in. Different from ingest (which starts from a source) — this
starts from an existing page and fills gaps or updates stale content.

## Required skills
- **Skill(obsidian:defuddle)** — for fetching and parsing URLs
- **Skill(obsidian:obsidian-cli)** — for reading/updating notes and frontmatter
- **Skill(obsidian:obsidian-markdown)** — for proper Obsidian-flavored markdown

## When to use

- A wiki page exists but feels thin or outdated
- The user asks to update coverage on a topic
- A `wiki-query` reveals gaps that should be filled
- A Software Catalog entry has `lifecycle: assess` or a stale `last_evaluated` date (for verdict changes, route to `catalog-evaluate` instead)

## Workflow

### 1. Read the existing page

Read the wiki page via obsidian-cli. Note:
- Current content and structure
- What's covered vs what's thin
- Frontmatter fields (especially `sources`, `date_updated`, `last_evaluated`)
- Any `[unverified]` markers or gaps flagged in previous edits

### 2. Identify what needs updating

Surface to the user:
- Sections that are thin or missing
- Content that may be outdated (check dates, version references)
- Specific questions worth answering
- **Skeleton drift**: compare the page's H2 structure against the canonical
  skeleton for its declared `page_type` (see
  `~/dotfiles/claude/rules/11-knowledge-wiki.md` → **Page Types &
  Skeletons**). Flag missing required sections, out-of-order headings, or
  missing neutral-definition opener. Also flag dialect drift (old `date
  created` / `date modified` with spaces vs. canonical `date_created` /
  `date_updated`), missing `page_type` field.
- **Workaround provenance gap**: any `Workaround` / `Gotcha` section without
  a link to an upstream issue or PR.

Ask: "What should I focus on, or should I do a general refresh?" If skeleton
drift is significant, propose restructuring alongside content updates — but
never auto-restructure silently.

### 3. Research externally

Use web search and/or `Skill(obsidian:defuddle)` to gather current information.
Focus on:
- What's changed since the page was last updated
- Filling identified gaps
- Verifying existing claims that may be stale

### 4. Optionally save source

If the external research produced a substantial source worth keeping:
- Save it to `Sources/YYYY-MM-DD Title.md` with standard source frontmatter
- Add it to the wiki page's `sources:` list

For quick refreshes from multiple small sources (docs pages, changelogs),
saving individual sources is optional — update the page directly.

### 5. Update the page

- Integrate new information into the existing structure
- Update `date_updated` (underscored form, for all page types including
  Software Catalog — migrate any older `date modified` to `date_updated`
  while you're here)
- Update `last_evaluated` for Software Catalog pages (underscored; migrate any `last-evaluated` with hyphen you encounter — see rule 12)
- Add any new sources to the `sources:` list
- Preserve existing content that's still accurate
- Flag contradictions between old and new information
- If restructuring toward the canonical skeleton was agreed in step 2,
  reorder sections, add the neutral-definition opener, and split blended
  generic/personal content into the appropriate sections

**Depth follows usage** — don't pad the page with exhaustive coverage. Add
what's useful for our working knowledge.

### 6. Update index and log

- Update entry in `Reference/index.md` if the summary changed
- Append to `Reference/log.md`:
  ```
  ## [YYYY-MM-DD] refresh | Page Name
  - Updated: [[Page Name]]
  - Changes: brief description of what was added/updated
  - Sources consulted: list URLs or source names
  ```

### 7. Report

Tell the user:
- What was updated and what changed
- Any contradictions found between old and new information
- Sections that are still thin (if any)
- Related pages that might also need refreshing

## Fold-back reflex

If, while working on something else in a session, you end up consulting
external documentation on a topic the wiki already covers, surface: "We hit
external docs for X — should we fold the new info back into [[X]]?" The wiki
is meant to compound; external detours without fold-back leak value.

## Quality Rules

- Preserve accurate existing content — don't rewrite what's fine
- New specific claims (benchmarks, version behavior) should cite their source
- Common knowledge updates don't need formal source documents
- Flag when existing content contradicts new findings rather than silently replacing
- Never silently auto-restructure a page. Skeleton changes must be proposed and
  approved first, then applied alongside content updates.

## Implementation Notes

See `${CLAUDE_PLUGIN_ROOT}/references/obsidian-cli-gotchas.md` for obsidian-cli
patterns and command examples.
