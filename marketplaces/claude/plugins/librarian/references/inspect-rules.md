# Inspect Rules

Diagnostic rule sets for the `vault-inspect` skill (and the `vault-inspector`
agent once delegation is wired up). Two scopes:

- **Structural** — vault-wide structure: orphans, dead-ends, broken links,
  frontmatter completeness, naming, stale pages, oversize pages,
  convention violations.
- **Wiki-semantic** — applies only to `owner: ai` + `type: wiki` pages:
  page_type validation, skeleton match, hierarchy completeness,
  neutral-definition opening, source-link format, anti-staleness,
  Software Catalog schema, Breadcrumbs hygiene.

Each rule has a stable ID so a report can refer back to the rule without
restating it. IDs are namespaced (`S-*` for structural, `W-*` for wiki).
The user's `~/Loose Ends/.claude/rules/wiki.md` and `catalog.md` remain
the source of truth for the *content* of conventions; rules here describe
how to *detect* violations.

## Scope flags

| Flag | Runs | Notes |
|---|---|---|
| `--structural` | S-* rules only | Whole-vault sweep |
| `--wiki` | W-* rules only | Restricted to `owner: ai` + `type: wiki` pages |
| (default) | both | Run S-* then W-* and combine the report |
| `--folder=PATH` | restricts the sweep | Applies to whichever scope was chosen |

## Structural rules (S-*)

### S-1: Orphaned notes
Notes with no incoming links and not referenced in any MOC/Dashboard.

- **Detection**: `obsidian-cli orphans` (or `obsidian-cli orphans total` for a count)
- **Severity**: medium
- **Note**: Daily notes and Sources/ are expected to have low link
  inbound — exclude or down-rank for those folders.

### S-2: Dead-end notes
Notes with no outgoing links. Isolated knowledge not connected forward.

- **Detection**: `obsidian-cli deadends` (or `obsidian-cli deadends total`)
- **Severity**: low
- **Note**: Some daily-note styles are intentionally dead-end; exclude
  `Daily Notes/` from the default sweep.

### S-3: Broken links
Internal links pointing to non-existent notes.

- **Detection**: `obsidian-cli unresolved verbose` (per-file) or
  `obsidian-cli unresolved counts` (per-file totals) or
  `obsidian-cli unresolved total` (vault total)
- **Severity**: high (blocks navigation)

### S-4: Missing required frontmatter
Notes lacking standard fields per vault conventions
(`date_created`, `date_modified`, `tags` where applicable).

- **Detection**: `obsidian-cli properties path="X"` per file, or
  `obsidian-cli properties all sort=count` to see field coverage across the
  vault and find low-coverage required fields.
- **Severity**: medium

### S-5: Stale notes
Notes whose `date_modified` is older than 6 months and which aren't
intentionally archived.

- **Detection**: `obsidian-cli history path="X"` for last-modified date.
- **Severity**: low (surface for review; don't auto-fix)

### S-6: Oversized notes
Single notes that have grown too large or cover multiple distinct
topics (candidates for splitting).

- **Detection**: `obsidian-cli wordcount path="X"` (over 500 words triggers
  a closer look) combined with `obsidian-cli outline path="X" format=tree`
  (multiple H1 headers, or several large H2 sections, suggests a split).
- **Severity**: low

### S-7: Convention violations
Notes that don't follow vault patterns documented in
`~/Loose Ends/.claude/CLAUDE.md`:

- Wrong folder location for content type
- Inconsistent naming (spaces vs hyphens, case)
- Missing `up:` field for hierarchical notes
- Missing tags for categorization

Detection is heuristic — compare folder + frontmatter against the
location decision tree and template inventory in vault CLAUDE.md.

- **Severity**: low

## Wiki-semantic rules (W-*)

Wiki pages are identified by `owner: ai` + `type: wiki` frontmatter.
All W-* rules restrict to that set.

### W-1: Orphan wiki pages
Wiki pages with no inbound links from other wiki pages.

- **Detection**: build a link graph from wiki pages only.
- **Severity**: medium

### W-2: Stale sources
Sources in `Sources/` that aren't referenced by any wiki page's
`sources:` frontmatter — ingested but their knowledge wasn't integrated.

- **Detection**: list `Sources/`; for each source, search wiki pages'
  `sources:` frontmatter for a wikilink to it.
- **Severity**: low

### W-3: Missing pages
Concepts referenced via wikilinks in wiki pages that don't have their
own page yet.

- **Detection**: scan wiki page bodies for `[[Target]]` where `Target`
  resolves to nothing.
- **Severity**: medium (informational — most are intentional)

### W-4: Contradictions
Wiki pages making claims that conflict with each other.

- **Detection**: requires reading bodies and reasoning; flag with the
  specific pages and sources involved.
- **Severity**: high (but rare; investigate, don't auto-fix)

### W-5: Thin pages
Wiki pages with only one source. May need enrichment, or may indicate a
topic worth deeper research.

- **Detection**: count `sources:` entries on each wiki page.
- **Severity**: low

### W-6: Unverified claims
Wiki pages containing `[unverified]` markers left by previous ingest
operations.

- **Detection**: grep for `[unverified]` in wiki page bodies.
- **Severity**: low

### W-7: Cross-vault opportunities
Wiki pages that reference concepts covered elsewhere in the vault but
don't link to them.

- **Detection**: extract noun phrases; search vault for matching note
  titles; flag missed link opportunities.
- **Severity**: low (suggestion only)

### W-8: Missing parent (`up:` or `expands:`)
Wiki pages without either an `up:` or `expands:` field. Every non-top-level
page needs one — Breadcrumbs hierarchy depends on it.

- `up:` covers topic specialization
- `expands:` covers altitude descent
- A page can carry both

**Don't flag**:
- Top-level topic pages (e.g. `3D Printing`, `Job Search`) — intentionally
  omit both
- Catalog tool entries in `Reference/Tools/Software Catalog/` — `up:` is
  optional per catalog.md; only flag if the page sits under a clear
  broader topic and has no `up:`. A catalog tool entry is a single
  self-contained `concept` page; it never declares `expands:` (it's the
  top of any descent — depth splits into `## Going Deeper` children that
  expand IT).
- Catalog category pages in `Reference/Tools/Categories/` — aggregation
  surfaces; they omit both `up:` and `expands:`.

- **Severity**: medium

### W-9: Stale MOC artifacts
Leftover `type: moc` frontmatter, `moc` tag, or `MOC.md` filename from
before MOCs were removed from the schema. Convert to regular `type: wiki`
pages and rename if needed.

- **Severity**: medium (schema drift)

### W-10: Source link format
Wiki pages whose `sources:` entries don't start with `[[Sources/`. The
schema requires the `Sources/` prefix on source links.

- **Detection**: parse `sources:` frontmatter; flag entries where the
  wikilink target doesn't start with `Sources/`.
- **Fix**: Edit the `sources:` block to add the `Sources/` prefix (on
  user approval).
- **Severity**: medium

### W-11: Tag convention
Tags that don't follow the vault's `#topic/something` namespace.

- **Allowed top-level tags**:
  - `topic/*` — content topics (e.g., `topic/3d-printing`)
  - `type/*` — note types if used
  - `status/*` — lifecycle if used
- `moc` tag is no longer allowed — flag occurrences under W-9.

- **Severity**: low

### W-12: Missing `owner: ai`
Wiki pages (identified via `type: wiki` frontmatter) that lack the
`owner: ai` field.

- **Severity**: medium

### W-13: Missing neutral definition
Wiki pages whose first non-frontmatter line is not a 1-2 sentence neutral
"what is X" statement.

**Detection heuristic** — read the first ~200 characters of the body
(excluding frontmatter). Flag if the first non-blank line is:

- A heading (starts with `#`)
- A list item (starts with `-`, `*`, or a digit + `.`)
- Under 30 characters or over 400 characters
- A meta-description ("Parent page for...", "This page tracks...")
- First-person opinion ("I like...", "My favorite...", "I use...")

- **Fix**: propose a neutral opening sentence; insert on approval.
- **Severity**: medium

### W-14: Missing or mismatched `page_type`
Wiki pages without a `page_type` field, or where the declared `page_type`
doesn't match the observed skeleton.

**Detection**:
- Field absent → flag, suggest a type based on folder + structure
  (Software Catalog or Categories folder → `concept`; pages with numbered
  Procedure section → `how-to`; everything else → `concept`).
- Field present but skeleton mismatched → flag. Examples:
  - `page_type: how-to` but no `## Procedure` heading
  - `page_type: evaluation` but no `## Decision` section (standalone
    evaluation pages only; the V2 catalog does not use `evaluation`)
  - A catalog tool entry (in `Reference/Tools/Software Catalog/`) missing
    the `## Stance` section or the derived `## Used in` / `## Alternatives`
    Breadcrumbs/Dataview blocks

- **Severity**: medium

### W-15: Frontmatter dialect drift
Wiki pages using legacy spaced date fields (`date created`,
`date modified`) instead of the canonical underscored form. Primarily
affects older Software Catalog pages. Also flag `last-evaluated` (hyphen)
— should be `last_evaluated` (underscore).

- **Detection**: parse YAML frontmatter; flag any key exactly matching
  `date created`, `date modified`, or `last-evaluated`.
- **Fix**: on approval, rename fields to the underscored form,
  preserving values.
- **Severity**: medium

### W-16: Stale wiki pages
Wiki pages where `date_updated` is older than a threshold. Default 365
days. Overridable per-page via a `velocity:` frontmatter field:

- `velocity: fast` → 90-day threshold (fast-moving topics)
- `velocity: stable` → no check (reference material that doesn't decay)
- unset → default 365 days

Skip pages marked `velocity: stable`. Flag others over threshold with
their last-updated date and suggest `wiki-refresh`.

- **Severity**: low (review recommended)

### W-17: Software Catalog schema (V2)
Applies to tool entries in `Reference/Tools/Software Catalog/`. See
`~/Loose Ends/.claude/rules/catalog.md` and
`~/Loose Ends/Templates/Software Tool.md` for the full V2 schema. A
catalog tool entry is a single self-contained `concept` page — there is
no gist-hub + `<Tool> Decision` child split.

**Flag each independently**:

- V1 schema fields present — `lifecycle:` or `status:` (should be
  `stance:`), `solves:` (split into `categories` + `summary`), `url:`
  (should be `homepage_url:`), `last-evaluated:` (hyphen, should be
  `last_evaluated`).
- Missing `template_version: "2.0"` — un-migrated entry. Surface for a
  migration pass via `catalog-evaluate`.
- Missing `stance` — every entry requires one.
- Invalid `stance` value — must be one of `lead`, `assess`, `trial`,
  `adopt`, `hold`, `dropped`.
- Missing `kind` — entries require `kind: component | resource | system`.
- Missing `summary` — entries require a neutral 1-2 sentence what-it-is.
- Missing `categories` — a tool with no `categories` appears on no
  comparison surface. Warn (a raw `stance: lead` may legitimately defer
  categorization until promotion).
- `best_for` set on a non-pick entry — `best_for` should be blank unless
  the tool is a current pick (`adopt`, or a `trial` being routed to). A
  `lead` / `assess` / `hold` / `dropped` entry with a non-empty
  `best_for` is suspect.
- Hand-listed `alternatives` in frontmatter — `alternatives` are DERIVED
  from shared `categories` via Breadcrumbs. A literal `alternatives:`
  field is a V1 leftover; reclassify genuine supersession as `replaces` /
  `replaced_by`, otherwise drop it (membership in the shared category
  produces the edge).
- Missing `homepage_url` — required when `kind: component` or
  `kind: resource`.
- `replaced_by` set on non-dropped entry — only makes sense when
  `stance: dropped`.
- Dead relation links — wikilinks in `replaces`, `replaced_by`,
  `depends_on`, or `categories` pointing to non-existent pages. A dead
  `categories` link means the category page hasn't been created.

- **Fix**: don't auto-migrate; route through `catalog-evaluate` (entry
  rewrite / category-page creation) or `wiki-create` (stub mode) for
  relation targets.
- **Severity**: medium

### W-18: Un-collapsed V1 catalog split
A leftover from the V1 gist-hub + `<Tool> Decision` child split that the
V2 single-entry schema replaced. Two shapes to flag:

- A `<Tool> Decision` page (`page_type: evaluation`) that `expands:` a
  catalog tool entry — the eval prose should be collapsed back into the
  single entry's `## Stance` section (or kept as a `## Going Deeper`
  child ONLY if it carries real depth, in which case it must NOT carry
  catalog frontmatter).
- Catalog frontmatter (`stance`, `summary`, `categories`, `kind`,
  `best_for`, `last_evaluated`) on a `page_type: evaluation` page or any
  `expands:` child — those fields belong on the single tool entry only.

- **Fix**: route through `catalog-evaluate` (migrate-v1 mode).
- **Severity**: medium

### W-19: First-person or V1 section headings on catalog entries
Catalog tool entries (or standalone evaluation pages) using older
first-person framings instead of the neutral V2 ones in wiki.md /
catalog.md / `Templates/Software Tool.md`:

- `## Why I'm on it` / `## Why I looked at it` → suggest `## Stance`
- `## What I liked` → fold into the `## Stance` `**Advantages**` bullets
- `## What didn't work` → fold into the `## Stance` `**Caveats**` bullets
- A literal `## Decision` heading on a catalog entry → the verdict lives
  in `## Stance` now (no separate Decision section on the single entry).

Surface as migration suggestions; don't bulk-rewrite (per wiki.md note).
The user migrates each page when next touching it.

- **Severity**: low

### W-20: Gratuitous `depth:` on Breadcrumbs codeblocks
Breadcrumbs codeblocks (` ```breadcrumbs `) that set `depth:` without
obvious reason. Default is unbounded — multi-level drill-down should be
visible from a hub.

- **Detection**: parse code fences with the `breadcrumbs` info string;
  check for a `depth:` line.
- **Fix**: report; user keeps or drops case-by-case.
- **Severity**: low

### W-21: Software Category page schema (V2)
Applies to category pages in `Reference/Tools/Categories/`. See
`~/Loose Ends/.claude/rules/catalog.md` and
`~/Loose Ends/Templates/Software Category.md`. A category page is an
ordinary `type: wiki`, `page_type: concept` page that aggregates tools
into one comparison surface.

**Flag each independently**:

- Missing `template_version: "2.0"` (with `template: "[[Software Category]]"`)
  — un-migrated or hand-built category page.
- Missing `## Candidates` Dataview block — the auto comparison table is
  the page's reason to exist. The block filters
  `contains(categories, this.file.link)`; nothing in it is hand-typed.
- Hand-typed candidate rows / a manual "reach for X when Y" routing list
  under `## Candidates` — routing is data (`best_for` on each tool); the
  table assembles it. Flag any prose comparison table.
- Missing `## Changelog` — the one hand-kept, event-shaped section
  (dated lines, newest first).
- No tool joins it — a category page that no tool lists in its
  `categories:` is an empty surface. Warn (may be newly established).
- A `category-hub` page_type or separate category base block — V2
  category pages are plain `concept` pages, not a distinct type.

- **Fix**: route through `catalog-evaluate` (which owns category-page
  creation when a tool joins a missing category).
- **Severity**: medium

## Event rules (W-EVENT-*)

Apply to `type: event` pages (schemas: `~/Loose Ends/Templates/Event
Incident.md` and `~/Loose Ends/Templates/Event Appointment.md`).
Events sit parallel to wiki pages — these rules validate shape but do
not run as part of the structural sweep. Default `--wiki` scope
includes them; an `--events` scope flag is reserved if differentiation
becomes useful.

### W-EVENT-1: Missing or invalid `page_type` on `type: event`
Event pages must declare a `page_type` from the enumerated list
(currently `incident`, `appointment`). Pages with `type: event` and
either no `page_type` or an unknown value are misshapen.

- **Detection**: `obsidian-cli properties path="<event-page>"` — check `type: event` plus `page_type` set to a known value
- **Severity**: high

### W-EVENT-2: Incident missing `expands:`
Every `page_type: incident` must declare `expands:` pointing at the
affected entity (device, system, condition). Incidents without an
entity link don't compose into entity dashboards.

- **Detection**: parse frontmatter; check `expands:` is non-empty when `page_type: incident`
- **Severity**: high

### W-EVENT-3: Appointment missing required fields
Every `page_type: appointment` must declare `expands:` (subject),
`specialty`, `date`, and `status`. Subjects are people or pets;
appointments without a subject don't compose.

- **Detection**: parse frontmatter; verify each required field is present and non-empty
- **Severity**: high

### W-EVENT-4: Missing `date` or `status`
Any `type: event` page without both `date` and `status` is incomplete.
These drive sort, filter, and follow-up reachability.

- **Detection**: parse frontmatter; check both fields present
- **Severity**: medium

### W-EVENT-5: `follow_up_by:` overdue with open status
`type: event` page with `follow_up_by:` in the past *and* `status:
open` (incident) or `status: scheduled` (appointment) indicates a
missed follow-up.

- **Detection**: parse frontmatter; compare `follow_up_by` to today; check `status`
- **Severity**: medium
- **Fix**: report; user resolves by updating status, rescheduling, or noting the slip

### W-EVENT-6: Incident with empty `## Diagnosis`
Incidents with a `## Diagnosis` heading whose body is empty, a single
short phrase (under ~10 words), or restates the `## Symptoms`. The
diagnosis is the load-bearing section — a page without one is worth
keeping only as a chronological record.

- **Detection**: read the section under `## Diagnosis`; flag if empty or trivial
- **Severity**: low
- **Note**: don't flag if `status: open` — the diagnosis may legitimately be unknown

## Report shape

Group findings by rule ID; within each rule, list affected pages.
Severity drives sort order (high → low). The full output template
lives in `vault-inspect`'s SKILL.md; this reference holds only the
rule definitions.
