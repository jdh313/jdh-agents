---
name: catalog-evaluate
description: Add or re-evaluate a software catalog entry — a tool, service, or system with a decision attached. Use when user says "add to my tool catalog", "evaluate this tool", "catalog X", "I'm considering X", or "record my decision on X".
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(obsidian-cli *)
  - WebFetch
---

# Catalog Evaluate

Create or refresh a Software Catalog entry. The catalog is a decision
log — every entry carries a current `stance` and the reasoning for it.
An entry is a **single self-contained page** (`type: wiki` +
`page_type: concept`) in `Reference/Tools/Software Catalog/`; there is no
gist-hub-plus-Decision-child split. A tool joins one or more **category
pages** (in `Reference/Tools/Categories/`) by listing them in its
`categories:` frontmatter; each category page assembles its comparison
table from the tools' frontmatter.

This skill drafts the entry (and any new category page) interactively;
`@note-editor` executes writes. Schema lives in
`~/Loose Ends/.claude/rules/catalog.md`, `~/Loose Ends/.claude/rules/wiki.md`,
and the authoritative templates `~/Loose Ends/Templates/Software Tool.md`
and `~/Loose Ends/Templates/Software Category.md` — the agent loads them.

## When to use vs. peer skills

| Scenario | Skill |
|---|---|
| Creating a new catalog entry | `catalog-evaluate` |
| Changing the `stance` on an existing entry | `catalog-evaluate` |
| Promoting a `lead` to a full hand-written entry (on adoption) | `catalog-evaluate` |
| Updating body content from new external info (no stance change) | `wiki-refresh` |
| Answering a question using the catalog | `wiki-query` |
| Re-evaluating an existing entry against its own revisit triggers | `catalog-recheck` |

If a user says "refresh this entry" but means "I've changed my mind",
route to `catalog-evaluate`.

## The stance enum

A tool's `stance` is a DEFAULT disposition toward future-me — not a
per-project verdict (that lives on the project note; see Per-project
selection below).

- `lead` — encountered, unevaluated. The raw GitHub-star / link-saver
  pool, bulk-imported and agent-enriched. **Not** hand-written via this
  skill; promoted out of the pool on adoption.
- `assess` — actively weighing; a live contender.
- `trial` — in use, still validating.
- `adopt` — a current pick. A category MAY have more than one `adopt`
  tool, each owning a context via `best_for`.
- `hold` — settled-no but REVISITABLE (weighed-and-passed for now, or
  paused). A `## Revisit Triggers` condition could flip it.
- `dropped` — PERMANENT no (abandoned after use, or a hard
  preference-against). Not expected to revisit; no triggers.

## Vault tool usage

Use `obsidian-cli property:set` for catalog frontmatter (`stance`,
`summary`, `best_for`, `kind`, `last_evaluated`, `homepage_url`, etc.) —
one field per call with explicit typing; `categories`, `depends_on`,
`replaces`, `replaced_by` are list-typed. Use
`obsidian-cli base:query path='Bases/Software V2.base' view='...'` to
check current entries before drafting, and
`base:query path='Bases/Software Categories V2.base'` for category pages.
Use `mcp__obsidian-mcp__patch_note` for in-body content edits.

## Workflow

### 1. Check for an existing entry

Dispatch via `@vault-reader`:

```markdown
## Intent
look up catalog entry for <Tool> and the category pages it joins

## Constraints
- Search `Reference/Tools/Software Catalog/` for the tool name and close variants
  (case, space/dash/underscore, declared `aliases:`)
- Report current `stance`, `categories`, and whether it carries
  `template_version: "2.0"` (migrated) or is an un-migrated / `lead` entry
- For each declared category, check whether the page exists in
  `Reference/Tools/Categories/`

## Output shape
- entry_path: <path or null>
- stance: <value or null>
- migrated: <true | false>
- categories: <list of [[Category]] with exists: true|false>
- aliases: <list>
```

Branch:
- **No entry** → continue to step 2 to create fresh.
- **Entry is a `lead`** → this is a promotion. Load it, then step 2 to
  fill in the full hand-written entry and lift the stance.
- **Un-migrated entry** (no `template_version: "2.0"`) → load it, map the
  old fields per `catalog.md`'s migration table, and rewrite to V2.
- **Migrated entry** → load it, jump to step 5 for the stance change.

### 2. Gather inputs progressively

Ask one question at a time, narrowing as the user answers. Order:

1. **Stance** — `assess` | `trial` | `adopt` | `hold` | `dropped`.
   Propose a default from the user's description.
2. **Kind** — `component` (local CLI/binary/library) | `resource`
   (hosted/cloud/SaaS) | `system` (named bundle). Propose and confirm.
3. **Categories** — one or more `[[Category]]` the tool competes in.
   This is what places it on a comparison surface; multi-membership is
   native. Drives the derived `alternatives` edge.
4. **Summary** — a 1-2 sentence NEUTRAL "what it is" (no opinion). This
   becomes `summary` AND echoes the body's opening definition.
5. **Best for** — routing-as-data: the situation to reach for this tool
   in. **Leave blank unless the stance is a current pick** (`adopt`, or a
   `trial` you're actively routing to).
6. **Replaces** — genuine supersession *for the user* ("jj replaces git
   for me"), not peers considered. (Peers are `alternatives` — and those
   are DERIVED, never asked for.)
7. **Depends on** — obvious ecosystem deps (optional).
8. **Homepage URL** — required for `component` / `resource`; skip for
   `system`. Also offer `repo_url` / `docs_url` if known.

Never ask for `alternatives` — they derive from shared `categories` via
Breadcrumbs. If the user volunteers a peer, capture it by ensuring both
tools share a category, or as `replaces`/`replaced_by` if it's genuine
supersession.

If `kind` is ambiguous (e.g. hosted service with a local daemon), pick
the dominant shape and note the dual nature in the body.

### 3. Light external fetch (optional)

If the user hasn't described the tool and there's a homepage URL,
WebFetch to grab a neutral one-liner for `summary`. Don't do deep
research here — `catalog-evaluate` records opinions. For deep research,
use `wiki-create` (ingest mode) first.

### 4. Resolve category pages

For each category the tool joins, confirm the page exists (from step 1).
For any that don't:

- **Offer to create the category page** from
  `~/Loose Ends/Templates/Software Category.md` — a neutral definition,
  the `## Candidates` Dataview (auto-fills as tools join), `## Key
  distinctions`, and a `## Changelog` seeded with today's "Category
  established" line.
- Default: create it (an entry referencing a non-existent category
  leaves a dead link that `vault-inspect` will flag).

If the category page exists and the tool's standing in it changed
(adopted, passed, new contender, default flips), add a dated `##
Changelog` line on the category page — this is the one manual,
event-shaped write the category keeps. The full "why" lives on the tool
entry, not the changelog.

### 5. Draft the entry

Path: `Reference/Tools/Software Catalog/{Name}.md`. Use
`~/Loose Ends/Templates/Software Tool.md` as the authoritative shape.

Frontmatter (the load-bearing fields):

```yaml
owner: ai
type: wiki
page_type: concept
template: "[[Software Tool]]"
template_version: "2.0"

stance: <enum>
summary: "<neutral 1-2 sentence what-it-is>"
best_for: "<routing situation, or blank>"

categories:
  - "[[<Category>]]"

kind: <component | resource | system>
depends_on: []
replaces: []
replaced_by: []

homepage_url: ""
repo_url: ""
docs_url: ""

last_evaluated: <YYYY-MM-DD>
```

Body skeleton (per the template):

1. *Neutral 1-2 sentence definition* (no heading) — echoes `summary`.
2. `## What it is` — generic facts + key-concept bullets. No opinion.
3. `## Stance — <Ring>` — niche + WHY it earns that stance.
   **Tool-intrinsic only** — comparative routing ("reach for X instead")
   lives on the category page, not here. Then `**Advantages**` /
   `**Caveats**` bullets, also tool-intrinsic.
4. `## Used in` — the DERIVED Dataview backlink block (copy verbatim
   from the template; reads project notes' `uses:`).
5. `## Revisit Triggers` — conditions that would FLIP the stance, NOT
   when to use it. Omit the section for a `lead` or `dropped`.
6. `## Alternatives` — the DERIVED Breadcrumbs block (copy verbatim).
   Never hand-list peers here.
7. `## Resources` — ad-hoc deep links only (homepage/repo/docs already
   in frontmatter).
8. `## Going Deeper` — the Breadcrumbs `expansions` block (copy
   verbatim). Renders only if a child page `expands:` this entry; empty
   for single-page tools.

Keep the body tight. Surface contradictions before writing: if
`stance: adopt` but the user described only concerns, flag and ask.

#### When real depth exists

If the evaluation carries genuine depth (a long tradeoff write-up, a
commands reference, a recipe), draft it as a SEPARATE `type: wiki` child
page that declares `expands: [[<Tool>]]` — it surfaces under `## Going
Deeper`. The child does NOT carry catalog frontmatter (`stance`,
`summary`, `categories`, etc.) — that stays on the single entry. Most
entries need no child; don't create one preemptively.

### 6. Dispatch the writes

```markdown
## Intent
write or update catalog entry for <Tool> (+ category page(s) if new)

## Constraints
- Schema: per `~/Loose Ends/.claude/rules/catalog.md`,
  `~/Loose Ends/Templates/Software Tool.md`,
  `~/Loose Ends/Templates/Software Category.md`
- Entry path: `Reference/Tools/Software Catalog/<Tool>.md`
- Category page(s) to create: <paths in Reference/Tools/Categories/, or none>
- Mode: <fresh | promote-lead | migrate-v1 | update>
- If migrate-v1: map old fields per catalog.md migration table; collapse any
  `<Tool> Decision` child into the single entry (keep it as a `## Going
  Deeper` `expands:` child only if it carries real depth)
- Update `date_updated` and `last_evaluated`; add category `## Changelog`
  line if standing changed
- Never hand-list `alternatives`; never set `best_for` unless a current pick

## Input
<full drafted entry content; full drafted category page content (if any)>

## Output shape
Confirm files created/modified with paths and a per-file change summary.
```

### 7. Surface missing referenced entries

After the agent reports, check every wikilink in `replaces`,
`replaced_by`, `depends_on`, and `categories` against what exists.
**Don't offer inline stubs one by one** — collect the list and present
once: "N linked entries don't exist yet: [list]. Want me to stub any,
all, or none?"

Default: leave unstubbed (category pages excepted — those are created in
step 4). `vault-inspect` (rule W-17) flags dead relation links for a
later cleanup pass.

### 8. Report

- Entry path + stance
- Categories joined (and any category page created)
- Relations recorded (`replaces` / `replaced_by` / `depends_on`)
- Changelog lines added to category pages
- Anything flagged for follow-up or stubbed

## Quality rules

- Every entry has a `stance` — never unset.
- `summary` is NEUTRAL and echoes the body's opening definition — never
  drifts from it, never carries opinion.
- `best_for` is BLANK unless the tool is a current pick. It is the
  category table's routing column — don't duplicate routing prose on the
  category page.
- If torn between `trial` and `adopt`, pick `trial` and name what would
  move it in `## Revisit Triggers`.
- `alternatives` are DERIVED from shared `categories` — never hand-listed
  in frontmatter or under `## Alternatives`.
- `replaces` / `replaced_by` are reserved for genuine supersession, not
  peers considered. `replaced_by` only makes sense on a `dropped` entry.
- Never invent technical claims not in the user's description or cited
  sources.
- Catalog frontmatter lives on the single entry only — never on an
  `expands:` child page.

## Per-project selection

A tool's `stance` is a default disposition. The actual per-project pick
lives on the **project note** via a flat `uses: [[Tool]]` field, NOT on
the tool entry. The entry's `## Used in` Dataview reverses those
backlinks. This skill never writes a per-project verdict onto the tool
entry; if the user wants to record "I picked X for project Y", add
`uses: [[X]]` to project Y's note instead.
