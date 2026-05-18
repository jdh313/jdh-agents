# ndr — Nested Decision Records

A personal-discipline plugin for capturing engineering decisions as **atomic markdown artifacts** with explicit lineage and **supersession-aware reading**, so cross-session decision drift becomes structurally visible rather than discoverable in hindsight.

## What it does

| Skill | Trigger | Behavior |
| --- | --- | --- |
| `/capture-decision` | Manual, at end of a chat | Scans the conversation for atomic decisions, drafts each, asks the user to confirm, writes the file with valid frontmatter + hybrid altitude body |
| `/decisions <topic>` | Manual, when the user has a topic or `ndr:` ref in hand | Frontmatter-first search → load 1–3 hits → walk supersession chain to head → return a brief |
| `/ground [scope]` | Before substantive code work, or before delegating to a coding subagent (junior-dev / senior-dev / tech-lead) | Infers scope from CWD / file path / user phrase, dispatches `@ndr-reader` to walk supersession, returns a brief plus `ndr:` reference strings the delegating prompt can paste in |
| `/drift-check [scope]` | Manual, or offered by `spec-flow:close` before archiving | Walks current heads, compares each against a chosen diff scope (working tree / branch range / commit range / full repo), surfaces divergences with three resolutions per item — amend, supersede, revert |
| `/ndr-bootstrap` | Once per machine after plugin install | Copies seed decision atoms, the Obsidian Base, and the initial taxonomy YAML into `~/Loose Ends/`. Idempotent |

## Install

```
/plugin marketplace add jdhoehler/cc-marketplace
/plugin install ndr@cc-marketplace
/ndr-bootstrap
```

After install:
- Decisions live as `~/Loose Ends/Decisions/<id>-<kebab-title>.md` — one atom per file, always single-file.
- Each atom uses a **hybrid altitude body**: heading + one-line gist for every section, with deeper texture in default-collapsed `[!info]-` / `[!warning]-` callouts.
- The Obsidian Base at `~/Loose Ends/Bases/Current Decisions.base` gives a faceted rollup (cards, tables, by area, superseded chain).
- Taxonomy (`area:`, `topic:`) lives in the vault at `~/Loose Ends/Decisions/.taxonomy/{areas,topics}.yaml`. The capture skill validates against these lists.

## Plugin layout

```
ndr/
├── .claude-plugin/
│   └── plugin.json
├── README.md                  # this file
├── skills/
│   ├── capture-decision/      # write-side
│   ├── decisions/             # read-side, user-driven (supersession-aware)
│   ├── ground/                # read-side, active-work grounding for coding agents
│   ├── drift-check/           # code-vs-decision coherence (on-demand)
│   └── ndr-bootstrap/         # one-time vault content install
├── agents/
│   ├── ndr-curator.md         # corpus health
│   ├── ndr-drafter.md         # atom drafting
│   ├── ndr-drift-auditor.md   # code-vs-decision walk + compare
│   ├── ndr-extractor.md       # candidate extraction from long sources
│   ├── ndr-reader.md          # supersession-aware read + synthesize (dispatched by /ground)
│   └── ndr-reviewer.md        # pre-write atom validation
├── references/                # static schema + workflow docs + template
│   ├── frontmatter-schema.md
│   ├── taxonomy.md
│   ├── workflow.md
│   └── decision-single.md
└── assets/                    # vault content the bootstrap skill installs
    ├── decisions/             # seed atoms — A–H meta-chain (0001-0008) plus reference-addressability resolution (0049-0051)
    ├── bases/
    │   └── current-decisions.base
    └── taxonomy/
        ├── areas.yaml
        └── topics.yaml
```

## Conventions

- **Atomic decisions.** One chosen path, one set of consequences. Bundled decisions get split.
- **Supersession-aware reading.** When a decision is revised, the old artifact stays, gets `status: superseded` + a `superseded_by:` pointer; the successor carries `supersedes:`. Readers walk to the head.
- **Hybrid altitude body.** Each section: heading + one-sentence gist + (optional) default-collapsed callout. Right detail at the right time.
- **Required frontmatter.** Capture skill refuses to write if any required field is missing (`id`, `title`, `status`, `decision_date`, `project`, `area`, `topic`, `reversibility`). `supersedes:` must be present (may be empty).
- **Finite taxonomy.** `area:` and `topic:` are validated against `~/Loose Ends/Decisions/.taxonomy/*.yaml`. New values require explicit add — friction is the feature.
- **Project-scoped browsing.** Every decision has a `project:` wikilink. Embed `![[Current Decisions.base#Log]]` on a project page for a live decision log scoped to that project.
- **Reference convention.** External code and vault notes use `ndr:<grain>` to point at atoms — atom-id (`ndr:0011`, frozen historical anchor), slug (`ndr:#monorepo-shape`, follows supersession via the atom's `aliases:` field), or topic (`ndr:architecture/repo-shape`, area-grain). The `/decisions` skill parses all three. See `references/workflow.md#reference-convention`.

See `references/frontmatter-schema.md`, `references/taxonomy.md`, `references/workflow.md` for full spec.

## History

Originally scaffolded as a standalone repo at `~/Projects/nested-decision-records/` (preserved as the historical scaffold; not the canonical source). Migrated into this plugin to get free cross-machine sync via the plugin marketplace. The seed atoms in `assets/decisions/` are ndr's own decision history — the A–H meta-chain (0001-0008) that produced the substrate + atomicity + read-side decisions, plus the reference-addressability resolution (0049-0051) that introduced the three-grain reference scheme and `aliases:` field. Installing them gives you a working corpus from day one.
