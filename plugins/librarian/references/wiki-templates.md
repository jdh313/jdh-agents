# Wiki page templates

Page-type skeletons for the Knowledge Wiki. Loaded by `@note-editor`
when writing or restructuring wiki pages. The vault's canonical schema
lives in `~/Loose Ends/.claude/rules/wiki.md`; this file is the
write-side distillation.

Every wiki page declares `page_type` in frontmatter. Three types:
`concept`, `how-to`, `evaluation`. The `concept` type also has two
gist-hub variants used when the page sits at the top of an altitude
descent.

## Shared frontmatter (all wiki pages)

```yaml
---
owner: ai
type: wiki
page_type: concept       # concept | how-to | evaluation
up:                      # topic specialization — for sub-topics of a broader area
  - "[[Parent Page]]"
expands:                 # altitude descent — only on children of a gist hub
  - "[[Gist Page]]"
sources: []              # [[Sources/...]] wikilinks; empty for stub pages
date_created: YYYY-MM-DD
date_updated: YYYY-MM-DD
tags: []
---
```

Use the underscored date form (`date_created`, `date_updated`). Migrate
legacy `date created` / `date modified` (spaces) when touching a page.

Top-level topic pages omit both `up:` and `expands:`. A page can carry
both `up:` and `expands:` (rare but valid).

## `page_type: concept` — general

Default type. Definitions, patterns, architectures, topic-area landing
pages.

Skeleton (omit sections that don't apply; never reorder):

1. *Neutral 1-2 sentence definition* (first line after frontmatter, no heading)
2. `## Overview` — why it matters here / how it fits (optional)
3. `## How it works` or `## Key concepts` — the generic explanation
4. `## In this vault` or `## My use` — personal context (optional)
5. `## Gotchas` or `## Known issues` — specific to our usage (optional)
6. `## Pages in this area` — Breadcrumbs codeblock (only on topic-area pages with children)
7. `## See also` — external links with commentary

Topic-area landing pages include a `## Pages in this area` Breadcrumbs
codeblock with `field-groups: [downs]`. See "Breadcrumbs codeblocks" below.

## `page_type: concept` — gist hub variants

When a `concept` page sits at the top of an altitude descent (one or
more child pages declare `expands: [[This Page]]`), use a slimmer
skeleton. The gist hub orients across the topic; deeper layers live in
the children. Body stays small (target: under ~60 lines).

### Catalog gist hub

For Software Catalog top-level pages. Pairs with a `<Tool> Decision`
child carrying the eval prose. Schema details in
`~/Loose Ends/.claude/rules/catalog.md`.

1. *Neutral 1-2 sentence definition* — what the tool is, no first-person, no opinion. May end with a one-clause adoption note: "Adopted for personal projects."
2. `## Advantages` — descriptive bullets. End with `Full reasoning: [[<Tool> Decision]]` when a Decision child exists.
3. `## Going deeper` — Breadcrumbs codeblock, `field-groups: [expansions]`.
4. `## Related topics` — Breadcrumbs codeblock, `field-groups: [downs]`.
5. `## See also` — only if external links not auto-rendered above.

For `assess`/`dropped` without a Decision child, drop the `Full
reasoning:` pointer and put a 1-2 sentence verdict on the gist body
(`## Decision` H2 acceptable as a deferred placeholder).

### Non-catalog gist hub

For patterns, frameworks, architectures that have enough material to
warrant altitude descents but aren't Software Catalog entries (no
`<Tool> Decision` page).

1. *Neutral 1-2 sentence definition* — what the thing is, no first-person, no opinion.
2. `## Overview` (optional) — short contextual paragraph(s); narrative, not bullets. Replaces the catalog gist's `## Advantages` — there's no Decision page to point to.
3. `## Going deeper` — Breadcrumbs codeblock, `field-groups: [expansions]`.
4. `## Related topics` — Breadcrumbs codeblock, `field-groups: [downs]`.
5. `## See also` — only if external links not auto-rendered above.

Children of a non-catalog gist hub use `expands: [[<Gist>]]` and are
themselves regular `concept` or `how-to` pages.

## `page_type: how-to`

Procedure with one canonical path. Calibrations, installations,
recipes.

1. *Neutral 1-sentence goal* (first line after frontmatter, no heading)
2. `## When to use this` — the trigger conditions
3. `## Prerequisites` — what needs to be true first
4. `## Procedure` — numbered steps
5. `## Troubleshooting` — FAQs and fixes (distinct from Known issues)
6. `## Known issues` — unsolved; link upstream bug/PR (optional)
7. `## When to redo` — signals it's time to re-run
8. `## See also`

## `page_type: evaluation`

The why-layer of a Software Catalog entry. Lives as a `<Tool> Decision`
child of the catalog gist hub, declares `expands: [[<Tool>]]`. Catalog
frontmatter (`lifecycle`, `kind`, `last_evaluated`, etc.) stays on the
gist, not here.

1. *Neutral definition* — what the tool is, one sentence, no opinion.
2. `## What it is` — generic description.
3. `## Why considered` — the problem it would solve.
4. `## Advantages` and/or `## Tradeoffs` — evaluation bullets. Both neutral; "Tradeoffs" can hold ongoing costs of adoption, not just rejection reasons.
5. `## Decision` — adopt / trial / assess / hold / dropped, with reason.
6. `## Alternatives` — markdown table `| Alternative | Verdict | Why |` for short lists; prose is fine for one or two.
7. `## Revisit triggers` — what would prompt re-evaluation.
8. `## See also`

Older eval pages may carry first-person headings (`## Why I looked at
it`, `## What I liked`, `## What didn't work`). Migrate opportunistically
when the page is next touched, not in a sweep.

## Breadcrumbs codeblocks

Two patterns compose into the gist hub shape.

**"Going deeper"** — altitude descents (children whose `expands:` points here):

````markdown
```breadcrumbs
type: tree
field-groups: [expansions]
sort: basename asc
```
````

**"Related topics"** — topic specializations (children whose `up:` points here):

````markdown
```breadcrumbs
type: tree
field-groups: [downs]
sort: basename asc
```
````

Omit `depth:` by default — let Breadcrumbs render the full tree. Add
`depth:` only with a specific reason. There is no `dir:` field —
use `field-groups: [downs]` for children, `[ups]` for ancestors.

Valid v4 codeblock fields: `type`, `title`, `start-note`, `fields`,
`field-groups`, `depth`, `flat`, `collapse`, `merge-fields`,
`dataview-from`, `content`, `sort`, `field-prefix`, `show-attributes`,
`mermaid-direction`, `mermaid-renderer`, `mermaid-curve`.

## Structure conventions (apply to every wiki page)

- **No hard-wrapped prose.** Each paragraph or list item is a single long line. Tables, code blocks, and YAML frontmatter keep natural line structure.
- **Neutral definition first.** First non-frontmatter line is a 1-2 sentence neutral "what is X". No `## Introduction` heading. No meta-descriptions ("Parent page for..."); describe the subject, not the page.
- **Avoid first-person narrative.** Prefer neutral or passive constructions. Section headings same rule.
- **Generic / personal split.** Generic facts in `## What it is`, `## How it works`, `## Key concepts`; personal in `## In this vault`, `## My use`, `## Decision`. Never blend in the same bullet list.
- **Section-level self-containment.** Each H2 should stand alone — restate critical context, front-load the claim. This is what makes wiki-query retrieval reliable.
- **Workaround provenance.** Any workaround section cites the upstream issue or PR it compensates for.
- **Anti-staleness.** No "currently", "at the time of writing", or bare inline dates. `date_updated` is the single source of truth for recency.
- **Callouts.** `> [!warning]` (severe/irreversible), `> [!note]` (caveat/surprise), `> [!tip]` (optional enhancement).
- **Linking.** Prefer topic references ("see [[systemd]]") over "click [[here]]". Use frontmatter `aliases:` for acronyms.

## Pre-write checklist

Before declaring the write complete, verify:

- [ ] `owner: ai` + `type: wiki` + `page_type` all set
- [ ] `up:` set for non-top-level pages (top-level omits both `up:` and `expands:`)
- [ ] `sources:` entries use `[[Sources/...]]` wikilinks (ingest mode); empty for stub
- [ ] `date_created` and `date_updated` use underscored form
- [ ] `tags` use `topic/*` namespace in kebab-case
- [ ] First non-frontmatter line is a neutral 1-2 sentence definition
- [ ] H2 ordering matches the canonical skeleton for the declared `page_type`
- [ ] Generic facts and personal content are in separate sections
- [ ] Wikilinks use bare names (`[[Page Name]]`)
- [ ] Page placed in correct vault folder for its topic
