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
log — every entry has a current verdict (`lifecycle`) and the reasoning
for it. Each entry is split across two pages:

- A `page_type: concept` **gist hub** at the catalog top level, carrying
  the catalog frontmatter (`lifecycle`, `kind`, relations).
- An optional **`<Tool> Decision`** child (`page_type: evaluation`)
  holding the eval prose.

This skill drafts both pages interactively; `@note-editor` executes
writes. Schema lives in `~/Loose Ends/.claude/rules/catalog.md` and
`~/Loose Ends/.claude/rules/wiki.md` — the agent loads them.

## When to use vs. peer skills

| Scenario | Skill |
|---|---|
| Creating a new catalog entry | `catalog-evaluate` |
| Changing the verdict on an existing entry | `catalog-evaluate` |
| Migrating an old-schema entry to gist + Decision child split | `catalog-evaluate` |
| Updating body content from new external info (no verdict change) | `wiki-refresh` |
| Answering a question using the catalog | `wiki-query` |

If a user says "refresh this entry" but means "I've changed my mind",
route to `catalog-evaluate`.

## Vault tool usage

Use `obsidian-cli property:set` for catalog frontmatter (`lifecycle`, `last_evaluated`, `kind`, `solves`, `homepage_url`, etc.) — one field per call with explicit typing. Use `obsidian-cli base:query path='Bases/Software.base' view='...'` to check current catalog entries before drafting. Use `mcp__obsidian-mcp__patch_note` for in-body content edits on Decision children.

## Workflow

### 1. Check for an existing entry

Dispatch via `@vault-reader`:

```markdown
## Intent
look up catalog entry for <Tool> and its Decision child

## Constraints
- Search `Reference/Tools/Software Catalog/` for the tool name and close variants
  (case, space/dash/underscore, declared `aliases:`)
- Also search vault-wide for `<Tool> Decision` (typically `Reference/Developer/`)
- Identify schema: gist+Decision split, or legacy single-page evaluation

## Output shape
- gist_path: <path or null>
- decision_path: <path or null>
- schema: <split | legacy | none>
- aliases: <list>
```

Branch:
- **Schema is `none`** → continue to step 2 to create fresh.
- **Schema is `legacy`** → propose migration to the gist + Decision child split.
- **Schema is `split`** → load existing pages, jump to step 5 for verdict change.
- **Otherwise** → confirm with the user whether to refresh or skip.

### 2. Gather inputs progressively

Ask one question at a time, narrowing as the user answers. Order:

1. **Lifecycle** — `adopt` | `trial` | `assess` | `hold` | `dropped`. Propose a default based on the user's description.
2. **Kind** — `component` (local CLI/binary/library) | `resource` (hosted/cloud/SaaS) | `system` (named bundle). Propose and confirm.
3. **What it solves** — one-line problem statement.
4. **Replaces** — supersedes *for the user*, not general peers.
5. **Alternatives** — peers genuinely considered, not adopted.
6. **Depends on** — obvious ecosystem deps (optional).
7. **Homepage URL** — required for `component` / `resource`; skip for `system`.

If `kind` is ambiguous (e.g. hosted service with a local daemon), pick
the dominant shape and note the dual nature in the gist body.

### 3. Light external fetch (optional)

If the user hasn't described the tool and there's a homepage URL,
WebFetch to grab a neutral one-liner. Don't do deep research here —
`catalog-evaluate` records opinions. For deep research, use
`wiki-create` (ingest mode) first.

### 4. Decide which pages to write

| Lifecycle | Gist hub | Decision child |
|---|---|---|
| `adopt` | required | required (or offered if deferred) |
| `trial` | required | required (or offered if deferred) |
| `assess` | required | optional — short blurb on gist OK |
| `hold` | required | optional |
| `dropped` | required | optional — `replaced_by` + brief gist blurb may suffice |

### 5. Draft the gist hub

Path: `Reference/Tools/Software Catalog/{Name}.md`. Skeleton (per
catalog.md `### Gist hub body`):

1. *Neutral 1-2 sentence definition* (may end with one-clause adoption note: "Adopted for personal projects.")
2. `## Advantages` — descriptive bullets; end with `Full reasoning: [[<Tool> Decision]]` when a Decision child exists
3. `## Going deeper` — Breadcrumbs codeblock, `field-groups: [expansions]`
4. `## Related topics` — Breadcrumbs codeblock, `field-groups: [downs]`
5. `## See also` — only if external links not auto-rendered

Keep the body under ~60 lines. Body declares `type: wiki` +
`page_type: concept` plus catalog fields. **Does not** declare `expands:`
(top of descent). Use `up:` only if the gist sits under a broader topic.

For `assess`/`dropped` without a Decision child, replace the
`Full reasoning:` pointer with a 1-2 sentence verdict on the gist body
(`## Decision` H2 OK as a deferred placeholder).

### 6. Draft the Decision child (when applicable)

Path: typically `Reference/Developer/{Name} Decision.md` (or wherever
the topic lives). Frontmatter: `type: wiki` + `page_type: evaluation` +
`expands: [[<Tool>]]`. Catalog frontmatter (`lifecycle`, `kind`,
`last_evaluated`) **does not** repeat here — stays on the gist only.

Skeleton (per catalog.md `### Decision child body`):

1. *Neutral one-sentence preamble*
2. `## What it is`
3. `## Why considered`
4. `## Advantages`
5. `## Tradeoffs`
6. `## Decision` — verdict + reasoning tied to lifecycle
7. `## Alternatives` — comparison table when listing >2
8. `## Revisit triggers` — what moves the lifecycle to a different ring
9. `## See also`

Surface contradictions before writing: if `lifecycle: adopt` but the
user described only concerns, flag and ask.

### 7. Dispatch the writes

```markdown
## Intent
write or update catalog entry for <Tool>

## Constraints
- Schema: per `~/Loose Ends/.claude/rules/catalog.md` and `~/Loose Ends/.claude/rules/wiki.md`
- Gist path: `Reference/Tools/Software Catalog/<Tool>.md`
- Decision path: <path or omitted>
- Migration: <fresh | legacy-to-split | update> — if legacy-to-split, preserve accurate body content and redistribute across gist + Decision child
- Update `Reference/index.md` with the gist (Decision child does not need its own line)
- Append to `Reference/log.md` with the catalog entry
- Update gist `date_updated` and `last_evaluated`

## Input
<full drafted gist content, full drafted Decision child content (if any), index entry, log entry>

## Output shape
Confirm files created/modified with paths and a per-file change summary.
```

### 8. Surface missing referenced entries

After the agent reports, check every wikilink in `replaces`,
`replaced_by`, `alternatives`, `depends_on` against what exists.
**Don't offer inline stubs one by one** — collect the list and present
once: "N linked entries don't exist yet: [list]. Want me to stub any,
all, or none?"

Default: leave unstubbed. `vault-inspect` (rule W-17) flags dead
relation links for a later cleanup pass.

### 9. Report

- Gist hub path + lifecycle verdict
- Decision child path (or noted deferred)
- Relations recorded (replaces / depends_on / alternatives)
- Anything flagged for follow-up
- Any entries stubbed for linked relations (after the batched offer)

## Quality rules

- Every entry must have a `lifecycle` verdict — never unset
- If torn between `trial` and `adopt`, pick `trial` and name what would move it in `## Revisit triggers`
- Never invent technical claims not in the user's description or cited sources
- `replaces` ≠ `alternatives` — ask if unclear
- Reasoning lives in `## Decision` prose (Decision child, or a deferred blurb on the gist for `assess`/`dropped`), not in frontmatter
- Catalog frontmatter lives on the gist only — never duplicate `lifecycle` / `kind` / `last_evaluated` on the Decision child
