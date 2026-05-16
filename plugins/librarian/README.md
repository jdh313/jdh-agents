# librarian

Curates, catalogs, retrieves, and maintains your library of notes and
knowledge in an Obsidian vault.
Workflow-shaped (Capture → Process → Retrieve → Maintain), agent-mediated
(skills draft, agents execute), reference-backed (conventions and
templates load on demand).

16 skills + 4 agents + 7 references, coupled to the vault at
`~/Loose Ends/` and governed by `~/Loose Ends/.claude/rules/{wiki.md,
catalog.md}`.

## Lifecycle matrix

| Stage | Skills |
|---|---|
| **Capture** | `wiki-create` (stub mode), `event-capture`, `meeting-notes`, `experiment-start`, `note-capture`, `note-suggester`, `catalog-evaluate` (new) |
| **Process** | `wiki-create` (ingest mode), `wiki-refresh`, `wiki-graduate`, `meeting-restructure`, `catalog-evaluate` (re-eval) |
| **Retrieve** | `wiki-query`, `meeting-followup`, `experiment-review` |
| **Maintain** | `vault-inspect`, `note-cleanup` |
| **Utility** | `base-add` |

Empty cells are intentional — Bases handle catalog retrieval; meetings
and experiments age out via vault-wide cleanup.

Architecture in one line: **skills gather intent and draft with the
user; agents own all vault I/O.** Every write flows through
`@note-editor` (Haiku) or `@vault-curator` (Sonnet); every read flows
through `@vault-reader` (Sonnet); diagnostic sweeps run in
`@vault-inspector` (Haiku).

## Agents

| Agent | Model | Verb | Invoked by |
|---|---|---|---|
| `vault-reader` | Sonnet 4.6 | Read + synthesize | `wiki-query`, `meeting-followup`, `experiment-review`, `event-capture` (entity lookup), `wiki-refresh` (drift check), `wiki-graduate` (link map), `catalog-evaluate` (existence check), `experiment-start` (promote mode) |
| `note-editor` | Haiku 4.5 | Mechanical write + cascade | `wiki-create`, `wiki-refresh`, `wiki-graduate`, `catalog-evaluate`, `meeting-notes`, `meeting-restructure`, `experiment-start`, `experiment-review` (verdict), `event-capture`, `note-capture`, `base-add` |
| `vault-curator` | Sonnet 4.6 | Interactive cleanup | `note-cleanup` |
| `vault-inspector` | Haiku 4.5 | Rule-check + structured report | `vault-inspect` |

The canonical skill→agent intent payload spec lives in
`agents/vault-reader.md` (`## Invocation contract`). All four agents
follow the same shape: `## Intent` / `## Constraints` / `## Input` /
`## Output shape` inbound, `## Result` / `## Sources` / `## Notes`
outbound.

## References

Loaded on demand by skills and agents that need vault context:

| File | Holds | Loaded by |
|---|---|---|
| `vault-conventions.md` | Folder structure, note types, frontmatter, naming, tags, links | Any agent that needs conventions |
| `bases.md` | Base registry, filter shapes, required properties per base | Agents working with `.base` files |
| `wiki-templates.md` | `page_type` skeletons (concept, gist hub catalog + non-catalog, how-to, evaluation) | `@note-editor` when writing wiki pages |
| `event-templates.md` | `type: event` skeletons (incident, appointment) + compositional pattern | `@note-editor` and `event-capture` |
| `inspect-rules.md` | Diagnostic rule sets (S-* structural, W-* wiki-semantic, W-EVENT-*) | `@vault-inspector` |
| `obsidian-cli-gotchas.md` | obsidian-cli patterns and shell-quoting gotchas | Any agent shelling to obsidian-cli |
| `work-context-config.md` | `${active_work_context}` substitution rules; reads `~/Loose Ends/.claude/librarian.local.md` | `meeting-notes`, `meeting-followup`, `meeting-restructure` |

Referenced from skills and agents via
`${CLAUDE_PLUGIN_ROOT}/references/<file>.md`.

## Configuration

Meeting skills read the current work-context folder from
`~/Loose Ends/.claude/librarian.local.md`:

```yaml
---
active_work_context: Carta
---
```

Travels with the vault (via Obsidian Sync), not the plugin install.
See `references/work-context-config.md` for details.

## Vault coupling

These skills are intentionally coupled to a specific vault layout at
`~/Loose Ends/`:

- Wiki pages: distributed across the vault, identified by `owner: ai` + `type: wiki`
- Sources: `Sources/`
- Index: `Reference/index.md`; log: `Reference/log.md`
- Software Catalog: `Reference/Tools/Software Catalog/`
- Events: live near their entity (devices in `Reference/Hardware/`, pets in `Personal/Pets/`, etc.)
- Meetings: `${active_work_context}/Meetings/` (resolved from local config)
- Hierarchy: Breadcrumbs plugin (`up:` for topic specialization, `expands:` for altitude descent)

Vault conventions (`wiki.md`, `catalog.md`) live in the vault — they
describe vault layout, not workflow logic — and are loaded by these
skills and agents as context.

## Companion plugins

`obsidian@obsidian-skills` is required:

- `obsidian:obsidian-cli` — note CRUD, search, frontmatter updates
- `obsidian:obsidian-markdown` — Obsidian-flavored markdown
- `obsidian:obsidian-bases` — Bases integration
- `obsidian:defuddle` — URL fetch/parse (optional; `wiki-create` ingest mode prefers WebFetch)

## See also

- `references/architecture.md` — per-stage explanation, agent roles, intent payload contract, design principles, how to add a new skill or event_kind
