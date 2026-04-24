# knowledge-work

Personal knowledge-management workflows for an Obsidian vault. A bundle of 20
skills + 2 agents covering the full lifecycle of a personal knowledge system:
ingest, curate, review, retain, and maintain.

Coupled to the vault at `~/Loose Ends/` and governed by conventions in
`~/Loose Ends/.claude/rules/{wiki.md,catalog.md}` and
`~/dotfiles/claude/rules/11-knowledge-wiki.md`.

## Skills

### Wiki

| Skill | Purpose |
|---|---|
| `wiki-ingest` | Process a source (URL/file) → save to `Sources/`, create/update wiki pages, update index and log |
| `wiki-query` | Answer a question using the wiki as context |
| `wiki-stub` | Quickly create a new wiki page from a "what is X" baseline |
| `wiki-refresh` | Update a stale wiki page with newer information |
| `wiki-lint` | Health-check the wiki for orphans, contradictions, stale content |

### Software Catalog

| Skill | Purpose |
|---|---|
| `catalog-evaluate` | Add or re-evaluate a Software Catalog entry with a lifecycle decision |

### Meetings

| Skill | Purpose |
|---|---|
| `meeting-notes` | Format raw meeting notes (incl. Zoom/Meet/Otter transcripts) and file into the vault |
| `meeting-followup` | Surface relevant unchecked action items from recent meeting notes |
| `meeting-restructure` | Redistribute durable facts from a meeting note into canonical pages; leave the meeting as a slim log |

### Experiments

| Skill | Purpose |
|---|---|
| `experiment-start` | Scaffold a new time-bounded experiment with hypothesis + review date |
| `experiment-review` | Pulse-check mid-run or record the adopt/modify/drop verdict at review_date |

### Anki

| Skill | Purpose |
|---|---|
| `anki-cards` | Create Anki flashcards from content |
| `anki-learn` | Research a topic and generate flashcard suggestions when no source exists yet |

### Notes (vault-general)

| Skill | Purpose |
|---|---|
| `note-capture` | Quickly capture a thought to the daily note |
| `note-cleanup` | Start an interactive vault cleanup session |
| `note-health` | Run a vault health check for structural issues |
| `note-suggester` | Suggest reusable knowledge captures inline during coding sessions |

### Vault meta

| Skill | Purpose |
|---|---|
| `vault-knowledge` | Load vault conventions from `~/Loose Ends/.claude/CLAUDE.md` for folder structure, templates, and patterns |
| `bases-knowledge` | Read all `.base` files and extract filters + required properties; base-aware operations |
| `base-add` | Create a new Obsidian Base entry with correct frontmatter |

## Agents

| Agent | Purpose |
|---|---|
| `note-editor` | Complex note editing: merge, restructure, add comprehensive links, update to new templates, enrich sparse notes |
| `vault-curator` | Dedicated cleanup sessions: find orphans, identify duplicates, propose merges/splits, update to conventions |

## Shared reference

`references/obsidian-cli-gotchas.md` — obsidian-cli patterns, gotchas, and
command examples used by the wiki skills. Referenced from SKILL.md files via
`${CLAUDE_PLUGIN_ROOT}/references/obsidian-cli-gotchas.md`.

## Vault coupling

These skills are intentionally coupled to a specific vault layout at
`~/Loose Ends/`:

- Wiki pages live distributed across the vault, identified by `owner: ai` +
  `type: wiki` frontmatter
- Sources live in `Sources/`
- Index at `Reference/index.md`, log at `Reference/log.md`
- Software Catalog entries under `Reference/Tools/Software Catalog/`
- Meetings under `80 Waites/Meetings/` (per vault conventions)
- Hierarchy managed via the Breadcrumbs plugin (`up:` field)

The rule files (`wiki.md`, `catalog.md`) remain in the vault — they describe
vault conventions, not workflow logic — and are read by these skills as
context.

## Companion plugins

`obsidian@obsidian-skills` is required for wiki operations:
- `obsidian:defuddle` — fetch/parse URLs for ingestion
- `obsidian:obsidian-markdown` — Obsidian-flavored markdown
- `obsidian:obsidian-cli` — note CRUD, search, frontmatter updates
- `obsidian:obsidian-bases` — Bases integration
