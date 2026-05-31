# obsidian-permission-audit

Survey + classify + recommend fixes for Obsidian access inconsistencies across cc-marketplace plugins. **Pure analysis run.** No plugin source edits; the only file written is the report at `.docs/2026-05-31-obsidian-permission-audit.md`.

## Phases

1. **Survey (parallel, 4 tasks)** — fan out to `Explore` and `general-purpose` agents to enumerate every Obsidian touch point across skill frontmatter, agent frontmatter, body callsites, and settings.json permissions.
2. **Breakpoint 1** — user can narrow scope after seeing survey counts.
3. **Classify** — one agent clusters findings into 5–7 inconsistency categories ranked by prompt-frequency impact.
4. **Recommend** — one agent produces a prioritized action plan with effort/impact/risk per item.
5. **Breakpoint 2** — user reviews recommendations before the report is written.
6. **Write report** — single Markdown file at `.docs/2026-05-31-obsidian-permission-audit.md`.

## Inputs

| Field | Default | Purpose |
|-------|---------|---------|
| `repoRoot` | `/Users/jacob/Projects/cc-marketplace` | Plugin source root |
| `userSettingsPath` | `/Users/jacob/dotfiles/claude/settings.json` | User-level permissions |
| `projectSettingsPath` | `/Users/jacob/Projects/cc-marketplace/.claude/settings.local.json` | Project-level permissions (tolerated if missing) |
| `reportPath` | `.docs/2026-05-31-obsidian-permission-audit.md` | Output file (repo-relative) |

## Outputs

- A single Markdown report at `reportPath`
- A structured return value with counts (skills surveyed, agents surveyed, callsites, categories, actions)

## Safety boundaries

- Survey tasks are read-only (Explore + grep + JSON read)
- Classify + recommend tasks do not touch the filesystem
- Only the `write-report` task writes to disk, and only to `.docs/`
- No commits, no plugin source edits, no marketplace.json changes, no vault content changes
