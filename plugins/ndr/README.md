# ndr — Nested Decision Records

A personal-discipline plugin for capturing engineering decisions as **atomic markdown artifacts** with explicit lineage and **supersession-aware reading**, so cross-session decision drift becomes structurally visible rather than discoverable in hindsight.

## What it does

| Skill | Trigger | Behavior |
| --- | --- | --- |
| `/capture-decision` | Manual, at end of a chat | Scans the conversation for atomic decisions, drafts each, asks the user to confirm, writes the file with valid frontmatter + hybrid altitude body |
| `/decisions <topic>` | Manual, or invoked when an agent needs to ground itself in prior decisions | Frontmatter-first search → load 1–3 hits → walk supersession chain to head → return a brief |
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
│   ├── decisions/             # read-side (supersession-aware)
│   └── ndr-bootstrap/         # one-time vault content install
├── references/                # static schema + workflow docs + template
│   ├── frontmatter-schema.md
│   ├── taxonomy.md
│   ├── workflow.md
│   └── decision-single.md
└── assets/                    # vault content the bootstrap skill installs
    ├── decisions/             # 8 seed atoms (the A–H meta-chain — ndr's own decision history)
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

See `references/frontmatter-schema.md`, `references/taxonomy.md`, `references/workflow.md` for full spec.

## History

Originally scaffolded as a standalone repo at `~/Projects/nested-decision-records/` (preserved as the historical scaffold; not the canonical source). Migrated into this plugin to get free cross-machine sync via the plugin marketplace. The 8 seed atoms in `assets/decisions/` are ndr's own decision history (A–H meta-chain) — installing them gives you a working corpus from day one.
