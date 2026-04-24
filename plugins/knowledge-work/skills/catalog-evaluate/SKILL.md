---
name: catalog-evaluate
description: Add or re-evaluate a software catalog entry — a tool, service, or system with a decision attached. Use when user says "add to my tool catalog", "evaluate this tool", "catalog X", "I'm considering X", or "record my decision on X".
---

# Catalog Evaluate

Create or refresh a Software Catalog entry. The catalog is a decision log —
every entry has a current verdict (`lifecycle`) and the reasoning for it.

## Required skills
- **Skill(obsidian:obsidian-cli)** — note creation, frontmatter, search
- **Skill(obsidian:obsidian-markdown)** — wikilinks, callouts, frontmatter
- **Skill(obsidian:defuddle)** — if fetching the tool's homepage for a neutral one-liner
- **Skill(wiki-stub)** — for stubbing referenced tools that don't have entries yet (`replaces`, `alternatives`, `depends_on`)

See `~/dotfiles/claude/rules/12-software-catalog.md` for the full schema
and vocabulary this skill enforces.

## When to use vs. peer skills

| Scenario | Skill |
|---|---|
| Creating a new catalog entry | `catalog-evaluate` |
| Changing the verdict on an existing entry (lifecycle transition) | `catalog-evaluate` |
| Migrating an old-schema entry to the new schema | `catalog-evaluate` |
| Updating body content from new external info (no verdict change) | `wiki-refresh` |
| Answering a question using the catalog | `wiki-query` |

If a user says "refresh this entry" but what they mean is "I've changed
my mind about this tool," route to `catalog-evaluate`.

## Workflow

### 1. Check for an existing entry

Search `Reference/Tools/Software Catalog/` for the tool name and close
variants. "Close variants" means:

- Case-insensitive exact match (`uv` ↔ `UV`)
- Space/dash/underscore variants (`git-annex` ↔ `Git Annex`)
- Known aliases: check the `aliases:` frontmatter of candidate files

If an entry exists:

- User wants to change the verdict → load the page, jump to step 5.
- Entry is on the old schema → propose migrating while you're here
  (see rule 12 migration mapping).
- Otherwise confirm with the user whether to refresh or skip.

### 2. Gather inputs progressively

Ask one question at a time, using the user's answers to narrow the next
question. Don't fire all prompts at once. In order of importance:

1. **Lifecycle** — `adopt` | `trial` | `assess` | `hold` | `dropped`
   (this is the verdict; propose a default if the user has described the
   tool and their relationship to it).
2. **Kind** — `component` | `resource` | `system`. Default heuristic:
   local CLI/binary/library → `component`; hosted/cloud/SaaS → `resource`;
   named bundle of tools → `system`. Propose and confirm.
3. **What it solves** — one-line problem statement. Propose based on the
   user's description if possible.
4. **Replaces** (distinct from alternatives) — things it supersedes *for
   the user*, not general peers.
5. **Alternatives** — peers they genuinely considered and did not adopt.
6. **Depends on** — obvious ecosystem deps (optional; skip if none come
   to mind).
7. **Homepage URL** — required for `component` and `resource`; skip for
   `system` (systems rarely have a single homepage). Repo URL if public
   source exists.

If `kind` is ambiguous (e.g. Tailscale = a hosted service AND a local
daemon), pick the dominant shape and note the dual nature in `## What
it is`. Don't try to store two kinds.

### 3. Light external fetch (optional)

If the user hasn't described the tool and there's a homepage URL,
invoke `Skill(obsidian:defuddle)` to grab a neutral one-liner for the
definition. Don't do deep research here — `catalog-evaluate` is for
recording opinions, not producing a source summary. For deep research
first, use `wiki-ingest` then `catalog-evaluate`.

### 4. Draft the entry

Build frontmatter per rule 12 schema. Draft body per the evaluation
skeleton:

1. Neutral definition (no opinion) — first line after frontmatter
2. `## What it is`
3. `## Why I looked at it`
4. `## What I liked` / `## What didn't work` (as applicable)
5. `## Decision` — always present, includes the reasoning behind the
   `lifecycle` value
6. `## Alternatives` — link other catalog entries if they exist
7. `## Revisit triggers`
8. `## See also` — for ad-hoc links (articles, videos) that don't fit
   the scalar URL fields

Surface contradictions before writing: if declared `lifecycle: adopt`
but the user described only concerns, flag and ask.

### 5. Write the page

- Path: `Reference/Tools/Software Catalog/{Name}.md`
- Use `Skill(obsidian:obsidian-cli)` for note creation
- Set `up:` to the appropriate parent. Verify the parent page *exists*
  before writing (search the vault). If no suitable parent exists, ask
  the user whether to create one via `wiki-stub` or omit `up:` (only
  valid for top-level topic pages — unlikely for a tool).

For updates to an existing entry, preserve body prose that's still
accurate and update `date_updated` + `last_evaluated`.

### 6. Update index and log

- **`Reference/index.md`** — add/update the catalog entry line
- **`Reference/log.md`** — append:
  ```
  ## [YYYY-MM-DD] catalog | Tool Name
  - Entry: [[Tool Name]]
  - Kind: component | Lifecycle: adopt
  - Change: created | lifecycle: trial → adopt | dropped
  ```
- `Software.base` filter auto-picks up the file by folder, but if new
  frontmatter *columns* should appear in the table view, edit the Base
  spec at `Bases/Software.base` directly (Bases don't auto-discover
  new fields).

### 7. Note missing referenced entries

Check every wikilink in `replaces`, `replaced_by`, `alternatives`, and
`depends_on` against the vault. **Don't offer inline stubs one by one
— that explodes the session.** Instead, collect the full list of
missing targets and present them once in the final report as a single
batched offer ("N linked entries don't exist yet: [list]. Want me to
stub any, all, or none?").

Default to leaving them unstubbed. Dead relation links will be flagged
by `wiki-lint` (check #17) so the user can address them in a dedicated
pass instead of mid-evaluation.

### 8. Pre-finish checklist

- [ ] `type: wiki` + `page_type: evaluation` set
- [ ] `kind` and `lifecycle` both set with valid values
- [ ] `solves` populated with a one-line problem statement
- [ ] `replaces` and `alternatives` kept distinct (not merged)
- [ ] `replaced_by` set *only* if `lifecycle: dropped`
- [ ] `homepage_url` set if `kind` is `component` or `resource` (not
      required for `system`)
- [ ] `up:` points to a page that actually exists in the vault
- [ ] Dates use underscored form (`date_created`, `date_updated`,
      `last_evaluated`) — never hyphenated
- [ ] Neutral definition is the first line after frontmatter (no
      heading, no opinion, no meta-text)
- [ ] `## Decision` section present and articulates reasoning for the
      lifecycle value
- [ ] Missing wikilinks in relation fields collected and surfaced as
      a single batched offer (default: leave unstubbed)
- [ ] Body cites sources for specific technical claims (benchmarks,
      version behavior); common knowledge needs no citation

### 9. Report

Tell the user:

- Entry path and lifecycle verdict
- Relations recorded (replaces / depends_on / alternatives)
- Anything flagged for follow-up (missing homepage, unclear lifecycle)
- Any entries stubbed for linked relations

## Quality rules

- Every entry must have a `lifecycle` verdict — never leave it unset
- If the user is torn between `trial` and `adopt`, pick `trial` and
  note what would move it to `adopt` in `## Revisit triggers`
- Never invent technical claims not in the user's description or cited
  sources
- `replaces` is not `alternatives` — ask the user if unclear
- Reasoning for the verdict lives in `## Decision` prose, not
  frontmatter
- Don't create a `page_type: concept` page in the Software Catalog
  folder — catalog entries are always `page_type: evaluation`

## Implementation notes

See `${CLAUDE_PLUGIN_ROOT}/references/obsidian-cli-gotchas.md` for
obsidian-cli patterns shared across wiki skills.
