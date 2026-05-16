---
name: catalog-evaluate
description: Add or re-evaluate a software catalog entry — a tool, service, or system with a decision attached. Use when user says "add to my tool catalog", "evaluate this tool", "catalog X", "I'm considering X", or "record my decision on X".
---

# Catalog Evaluate

Create or refresh a Software Catalog entry. The catalog is a decision log — every entry has a current verdict (`lifecycle`) and the reasoning for it. Each entry is split across two pages: a `page_type: concept` gist hub at the catalog top level (carrying the catalog frontmatter) and an optional `<Tool> Decision` child (`page_type: evaluation`) that holds the eval prose.

## Canonical conventions

Read these rule files before producing output — they are the source of truth for schema and skeletons:

- `~/Loose Ends/.claude/rules/wiki.md` — page types, skeletons, page structure conventions, Breadcrumbs hierarchy (`up:` vs `expands:`)
- `~/Loose Ends/.claude/rules/catalog.md` — catalog schema (kind/lifecycle/relations) and gist-hub-plus-Decision-child split

Sections this skill depends on:
- Catalog frontmatter (gist hub) → catalog.md `### Gist hub`
- Decision child frontmatter → catalog.md `### Decision child`
- Gist hub skeleton → wiki.md `### concept as a gist hub`, expanded in catalog.md `### Gist hub body`
- Decision child skeleton → wiki.md `### evaluation`, expanded in catalog.md `### Decision child body`
- Hierarchy fields → wiki.md `## Hierarchy via Breadcrumbs`
- Lifecycle / kind / relations vocabulary → catalog.md `## Schema`

## Required skills
- **Skill(obsidian:obsidian-cli)** — note creation, frontmatter, search
- **Skill(obsidian:obsidian-markdown)** — wikilinks, callouts, frontmatter
- **Skill(obsidian:defuddle)** — if fetching the tool's homepage for a neutral one-liner
- **Skill(wiki-create)** — stub mode, for stubbing referenced tools that don't have entries yet (`replaces`, `alternatives`, `depends_on`)

## When to use vs. peer skills

| Scenario | Skill |
|---|---|
| Creating a new catalog entry | `catalog-evaluate` |
| Changing the verdict on an existing entry (lifecycle transition) | `catalog-evaluate` |
| Migrating an old-schema entry to the new schema (e.g. evaluation-at-top-level → gist + Decision child) | `catalog-evaluate` |
| Updating body content from new external info (no verdict change) | `wiki-refresh` |
| Answering a question using the catalog | `wiki-query` |

If a user says "refresh this entry" but what they mean is "I've changed my mind about this tool," route to `catalog-evaluate`.

## Workflow

### 1. Check for an existing entry

Search `Reference/Tools/Software Catalog/` for the tool name and close variants. "Close variants" means:

- Case-insensitive exact match (`uv` ↔ `UV`)
- Space/dash/underscore variants (`git-annex` ↔ `Git Annex`)
- Known aliases: check the `aliases:` frontmatter of candidate files

Also search for `<Tool> Decision` outside the catalog folder (typically `Reference/Developer/`) — the Decision child usually lives near the topic, not in the catalog folder.

If an entry exists:

- User wants to change the verdict → load the gist + Decision child if present, jump to step 5.
- Entry is on the old schema (single `page_type: evaluation` page at the catalog top level) → propose migrating to the gist + Decision child split (see catalog.md migration mapping).
- Otherwise confirm with the user whether to refresh or skip.

### 2. Gather inputs progressively

Ask one question at a time, using the user's answers to narrow the next question. Don't fire all prompts at once. In order of importance:

1. **Lifecycle** — `adopt` | `trial` | `assess` | `hold` | `dropped` (this is the verdict; propose a default if the user has described the tool and their relationship to it).
2. **Kind** — `component` | `resource` | `system`. Default heuristic: local CLI/binary/library → `component`; hosted/cloud/SaaS → `resource`; named bundle of tools → `system`. Propose and confirm.
3. **What it solves** — one-line problem statement. Propose based on the user's description if possible.
4. **Replaces** (distinct from alternatives) — things it supersedes *for the user*, not general peers.
5. **Alternatives** — peers they genuinely considered and did not adopt.
6. **Depends on** — obvious ecosystem deps (optional; skip if none come to mind).
7. **Homepage URL** — required for `component` and `resource`; skip for `system` (systems rarely have a single homepage). Repo URL if public source exists.

If `kind` is ambiguous (e.g. Tailscale = a hosted service AND a local daemon), pick the dominant shape and note the dual nature on the gist body. Don't try to store two kinds.

### 3. Light external fetch (optional)

If the user hasn't described the tool and there's a homepage URL, invoke `Skill(obsidian:defuddle)` to grab a neutral one-liner for the definition. Don't do deep research here — `catalog-evaluate` is for recording opinions, not producing a source summary. For deep research first, use `wiki-create` (ingest mode) then `catalog-evaluate`.

### 4. Decide which pages to write

| Lifecycle | Gist hub | Decision child |
|---|---|---|
| `adopt` | required | required (or offered if user wants to defer) |
| `trial` | required | required (or offered if user wants to defer) |
| `assess` | required | optional — short blurb on gist body acceptable until reasoning is ready |
| `hold` | required | optional |
| `dropped` | required | optional — `replaced_by` and a brief `## Decision` blurb on the gist may be enough |

Confirm with the user before creating a Decision child for `assess`/`dropped`. Default for `adopt`/`trial`: create both unless told otherwise.

### 5. Draft the gist hub

Path: `Reference/Tools/Software Catalog/{Name}.md`. Use the `concept` gist-hub skeleton from wiki.md / catalog.md. Concrete shape:

1. *Neutral 1-2 sentence definition* — what the tool is. May end with a one-clause adoption note ("Adopted for personal projects.") so the verdict shows without leaving the page.
2. `## Advantages` — descriptive bullets. End with `Full reasoning: [[<Tool> Decision]]` when a Decision child exists.
3. `## Going deeper` — Breadcrumbs codeblock with `field-groups: [expansions]`.
4. `## Related topics` — Breadcrumbs codeblock with `field-groups: [downs]`.
5. `## See also` — only if there are external links not auto-rendered above.

Keep the body small (target: under ~60 lines). New material lands in expansions, not by growing the gist.

Frontmatter is `type: wiki` + `page_type: concept` plus all catalog fields per catalog.md `### Gist hub`. The gist hub does **not** declare `expands:` — it's the top of the descent. Use `up:` if the gist sits under a broader wiki topic; verify that parent exists before writing.

For `assess`/`dropped` without a Decision child, drop the `Full reasoning:` pointer and put a 1-2 sentence verdict-with-reason on the gist body (`## Decision` H2 acceptable here as a deferred placeholder).

### 6. Draft the Decision child (when applicable)

Path: typically `Reference/Developer/{Name} Decision.md`, or wherever the topic lives. Frontmatter: `type: wiki` + `page_type: evaluation` + `expands: [[<Tool>]]`. Catalog frontmatter (`lifecycle`, `kind`, `last_evaluated`, etc.) does **not** repeat here — it stays on the gist as the single source of truth for `Software.base`.

Use the `evaluation` skeleton from wiki.md with neutral framings (catalog.md `### Decision child body` for the catalog-specific shape):

1. *Neutral one-sentence preamble* — what the page answers (e.g. "Why this tool, what tradeoffs, and what would move me off it").
2. `## What it is` — generic description. May repeat from the gist; the page is read independently.
3. `## Why considered` — the problem it would solve.
4. `## Advantages` — what works well in adoption.
5. `## Tradeoffs` — what didn't work, ongoing costs of adoption, or known friction.
6. `## Decision` — the verdict with reasoning, tied to the lifecycle ring.
7. `## Alternatives` — comparison table preferred when listing more than two:

   ```markdown
   | Alternative | Verdict | Why |
   ```

   Link to peer catalog entries if they exist.
8. `## Revisit triggers` — what would move the lifecycle to a different ring.
9. `## See also` — gist hub plus sibling expansions (Commands, Configuration, etc.).

Surface contradictions before writing: if the declared `lifecycle: adopt` but the user described only concerns, flag and ask.

### 7. Write the pages

Use `Skill(obsidian:obsidian-cli)` for note creation. For migrations from old single-page entries, preserve body prose that's still accurate, redistribute it across gist + Decision child, and update `date_updated` + `last_evaluated` on the gist.

### 8. Update index and log

- **`Reference/index.md`** — add/update the catalog entry line. Reference the gist hub; the Decision child does not need its own index line.
- **`Reference/log.md`** — append:
  ```
  ## [YYYY-MM-DD] catalog | Tool Name
  - Gist: [[Tool Name]]
  - Decision: [[Tool Name Decision]]   # omit if not created
  - Kind: component | Lifecycle: adopt
  - Change: created | lifecycle: trial → adopt | dropped | migrated to gist+decision split
  ```
- `Software.base` filter auto-picks up the gist by folder, but if new frontmatter *columns* should appear in the table view, edit the Base spec at `Bases/Software.base` directly (Bases don't auto-discover new fields).

### 9. Note missing referenced entries

Check every wikilink in `replaces`, `replaced_by`, `alternatives`, and `depends_on` against the vault. **Don't offer inline stubs one by one — that explodes the session.** Collect the full list of missing targets and present them once in the final report as a single batched offer ("N linked entries don't exist yet: [list]. Want me to stub any, all, or none?").

Default to leaving them unstubbed. Dead relation links will be flagged by `vault-inspect` (rule W-17 — catalog-schema check) so the user can address them in a dedicated pass instead of mid-evaluation.

### 10. Pre-finish checklist

Gist hub:
- [ ] `type: wiki` + `page_type: concept` set
- [ ] `kind` and `lifecycle` both set with valid values per catalog.md
- [ ] `solves` populated with a one-line problem statement
- [ ] `replaces` and `alternatives` kept distinct (not merged)
- [ ] `replaced_by` set *only* if `lifecycle: dropped`
- [ ] `homepage_url` set if `kind` is `component` or `resource`
- [ ] `up:` (if present) points to a page that actually exists; `expands:` is **not** present
- [ ] Dates use underscored form (`date_created`, `date_updated`, `last_evaluated`)
- [ ] Neutral definition is the first line after frontmatter (no heading, no opinion, no meta-text)
- [ ] Body stays short (~60 lines target); deeper material is in expansions
- [ ] Both Breadcrumbs codeblocks present (`expansions` and `downs`); no `depth:` unless justified

Decision child (when created):
- [ ] `type: wiki` + `page_type: evaluation` set
- [ ] `expands: [[<Tool>]]` points to the gist
- [ ] No catalog frontmatter (`lifecycle`, `kind`, `last_evaluated`, etc. live on the gist only)
- [ ] Section headings use neutral framings (`## Why considered`, `## Advantages`, `## Tradeoffs`) — not first-person (`## Why I looked at it`, `## What I liked`, `## What didn't work`)
- [ ] `## Decision` section present and articulates reasoning for the lifecycle value
- [ ] `## Alternatives` uses comparison table when more than two alternatives

Cross-cutting:
- [ ] Missing wikilinks in relation fields collected and surfaced as a single batched offer (default: leave unstubbed)
- [ ] Body cites sources for specific technical claims (benchmarks, version behavior); common knowledge needs no citation

### 11. Report

Tell the user:

- Gist hub path and lifecycle verdict
- Decision child path (or note that it was deferred)
- Relations recorded (replaces / depends_on / alternatives)
- Anything flagged for follow-up (missing homepage, unclear lifecycle)
- Any entries stubbed for linked relations

## Quality rules

- Every entry must have a `lifecycle` verdict — never leave it unset
- If the user is torn between `trial` and `adopt`, pick `trial` and note what would move it to `adopt` in `## Revisit triggers`
- Never invent technical claims not in the user's description or cited sources
- `replaces` is not `alternatives` — ask the user if unclear
- Reasoning for the verdict lives in `## Decision` prose on the Decision child (or as a deferred blurb on the gist for `assess`/`dropped`), not in frontmatter
- Catalog frontmatter lives on the gist hub only — never duplicate `lifecycle` / `kind` / `last_evaluated` on the Decision child

## Implementation notes

See `${CLAUDE_PLUGIN_ROOT}/references/obsidian-cli-gotchas.md` for obsidian-cli patterns shared across wiki skills.
