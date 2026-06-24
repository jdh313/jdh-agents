---
name: wiki-graduate
description: Split a fat wiki gist into an `expands:` child page cleanly. Use when a wiki page has accumulated enough material that a section deserves its own deeper layer — user says "this page is getting too long", "split off the X section", "graduate this", "move this to a child page", "promote this section", or when `vault-inspect` flags a page as oversized.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(obsidian-cli *)
---

# Wiki Graduate

Split a fat gist hub into an `expands:` child page. The child takes
selected sections; the gist retains a short pointer (or relies on the
Breadcrumbs `## Going deeper` block to surface the child automatically).

Drafts the split interactively with the user; `@vault-reader` pulls the
source page and incoming-link map; `@note-editor` executes the
multi-file edit.

Schema and skeletons live in the vault Templates folder:

- `~/Loose Ends/Templates/Wiki Concept.md`
- `~/Loose Ends/Templates/Wiki Concept - Gist Hub (Non-Catalog).md`
- `~/Loose Ends/Templates/Wiki How-to.md`
- `~/Loose Ends/Templates/Wiki Evaluation.md`
- `~/Loose Ends/Templates/Software Tool.md` (catalog tool entry — a single self-contained page; graduate depth into a `## Going Deeper` `expands:` child)

Hierarchy mechanics (`expands:` vs `up:`) live in
`~/Loose Ends/.claude/rules/wiki.md`.

## When to use

- A wiki page has grown past ~150-200 lines and a section (or two)
  could stand alone as a deeper layer
- `vault-inspect` flags a page as oversized (rule `S-6`)
- The user describes the page as "doing too much" or wants drill-down
- A topic has accumulated practical detail (commands, configuration,
  troubleshooting) that's drowning the conceptual gist

Do NOT use for:

- Moving a page to a different parent (that's an `up:` change, edit the frontmatter directly)
- Renaming a page (use Obsidian rename or `@note-editor`)
- Splitting a page into two peers (no `expands:` relationship — use `wiki-create` for the new page)

## Workflow

### 1. Pull the source page + incoming links

Dispatch via `@vault-reader`:

```markdown
## Intent
pull wiki page and its incoming-link map for graduation

## Constraints
- Read the source page in full
- List all incoming links (backlinks) with the line context where they appear
- Note any links that point at section anchors (`[[Page#Section]]`) — those break if the section moves

## Input
page: <path>

## Output shape
- page_content: <full content>
- frontmatter: <parsed>
- sections: [<list of H2s with line ranges>]
- incoming_links: [{source_path, line, link_text, points_at_section: <section name or null>}]
```

### 2. Decide what graduates

With the user:

- **Which section(s)?** Usually one section becomes one child page. Occasionally two related sections merge into one child.
- **Child page title?** Should reflect the topic of the moved content, not "Section X of Page Y". E.g. `Jujutsu Commands` (not "jj — Commands").
- **Page type?** Usually `concept` (or `concept` as a gist hub if the child will itself accumulate descents). `how-to` if the moved content is a procedure.
- **Should the gist keep a pointer?** Default: no — Breadcrumbs `## Going deeper` auto-renders the child. Add a one-line pointer in the gist body only if the content above the graduated section references it.

### 3. Plan the link rewrites

For each incoming link that targets a section being moved:

- `[[Page#MovedSection]]` → `[[Child Page]]` (or `[[Child Page#NewSection]]` if the section becomes an H2 inside the child)
- `[[Page]]` references stay as-is — they still point at the gist, which still exists

Surface the rewrite plan as a table for user approval:

```markdown
| Source | Current link | New link |
|---|---|---|
| `Project A.md:42` | `[[Jujutsu#Commands]]` | `[[Jujutsu Commands]]` |
```

### 4. Draft the child page

Compose:

- **Frontmatter** — copy from the parent's frontmatter, then:
  - Set `expands: [[<Gist>]]`
  - Remove `up:` (the gist holds the `up:`; the child gets its taxonomy via `expands:`)
  - Reset `date_created` to today; `date_updated` to today
  - Keep `sources:` for any sources cited in the moved content
- **Neutral 1-2 sentence definition** at top — what this deeper layer covers
- **Moved sections** — copy verbatim. If a section was at H3 in the gist (subordinate to a moving H2), promote to H2 in the child.
- **`## See also`** — link back to the gist (`[[<Gist>]]`) at minimum.

### 5. Draft the gist update

- Remove the moved sections from the gist body.
- If the gist now lacks a `## Going deeper` Breadcrumbs codeblock, add one (per `~/Loose Ends/Templates/Wiki Concept.md`):

  ````markdown
  ```breadcrumbs
  type: tree
  field-groups: [expansions]
  sort: basename asc
  ```
  ````

- If the gist was a non-catalog `concept` page and now sits at the top of a descent, the body shape shifts to the gist-hub skeleton — verify it still satisfies that shape after the section removal.
- Update `date_updated` to today.

### 6. Dispatch the writes

```markdown
## Intent
graduate sections from <gist-path> into a new <expands:> child

## Constraints
- Order: write child first, then update gist, then rewrite incoming links
- Child path: <path>
- Child frontmatter: `expands: [[<Gist>]]`, no `up:`
- Schema: per the matching template in `~/Loose Ends/Templates/` (`Wiki Concept.md`, the gist-hub variant, `Wiki How-to.md`, or `Wiki Evaluation.md`)
- Link rewrites: list provided in Input

## Input
- child_page: <full drafted frontmatter + body>
- gist_update: <full updated gist content>
- link_rewrites: [{source_path, old_link, new_link}]

## Output shape
Per file: action (write/edit), path, sections touched. Confirm Breadcrumbs codeblock present on gist if it was missing.
```

### 7. Report

Surface the agent's `## Result`:

- Child page created (path)
- Gist updated (sections removed, Breadcrumbs codeblock state)
- Incoming-link rewrites applied (count)
- Anything to verify in Obsidian (`## Going deeper` block renders the new child; backlinks resolve)

If the gist now feels lean enough, suggest stopping. If multiple
sections still feel like candidates, offer to graduate another.

## Quality rules

- **One graduation at a time.** Don't move three unrelated sections into three children in one shot. The user reviews each split.
- **Preserve content verbatim** when moving — don't restructure or rewrite during the move. Restructure as a follow-up via `wiki-refresh` if needed.
- **`expands:` not `up:`** for the child. If you're tempted to use `up:`, the section isn't really a deeper layer — consider `wiki-create` for a peer page instead.
- **Don't graduate a section that's only there for SEO/context.** If the section's value is mostly in pointing to other pages (a thin `## See also`-style section), leave it on the gist.
- **No silent rewrites.** Every incoming-link change goes through the approval table in step 3.
