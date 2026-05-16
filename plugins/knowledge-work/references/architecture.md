# knowledge-work architecture

Per-stage detail behind the README's lifecycle matrix, plus the design
principles and contracts that hold it together. The README is the
wide shot; this file is the descent.

## Design principles

1. **Workflow-first organization.** Skills map to lifecycle stages, not to data types. The matrix in the README is the load-bearing visual.
2. **Gist hub + `expands:` children for substantial knowledge.** Catalog top-level pages are the model: thin definition + auto-rendered Breadcrumbs "Going deeper" and "Related topics", with depth accumulating in child pages that declare `expands: [[Parent]]`. Same pattern applies to entity pages with event children.
3. **Template as forcing function.** Tight skeletons with no prose-friendly body slots prevent bloat at creation. The catalog gist holds shape because it has nowhere for new material to land except a child page.
4. **No skill touches vault files directly.** All vault reads and writes flow through agents. The main session holds intent and structured summaries, never raw file contents.
5. **Skills draft, user approves, agents execute.** Skills generate finalized content in the main session (where the user sees, corrects, and approves). Agents then execute the mechanical write + cascade work. `@note-editor` is a Haiku-class executor rather than a Sonnet-class writer.
6. **Template inventory stays small; `wiki-graduate` is the escape valve.** New templates earn their place only when three or more pages would clearly fit the shape. Everything else uses the generic gist hub skeleton; depth splits off via `wiki-graduate` when accumulation happens.

## Lifecycle stages

### Capture

Bring new information into the vault.

- `wiki-create` (stub mode) — lightweight "what is X" page from common knowledge
- `event-capture` — incident or appointment with entity backlink
- `meeting-notes` — format raw meeting notes (or transcripts) and file
- `experiment-start` — scaffold a hypothesis + protocol + review_date
- `note-capture` — one-liner to today's daily note (slash command)
- `note-suggester` — passive ambient suggestions during coding (no I/O at trigger; batches at session end)
- `catalog-evaluate` (new entry path) — gist hub + Decision child with lifecycle verdict

### Process

Transform captured material into a more durable shape.

- `wiki-create` (ingest mode) — fetch a source, draft wiki pages, link, log
- `wiki-refresh` — pull current information from external sources, integrate, flag drift
- `wiki-graduate` — split a fat gist into an `expands:` child cleanly
- `meeting-restructure` — redistribute durable facts from a meeting note into canonical pages; leave a slim log with outbound links + provenance footnotes
- `catalog-evaluate` (re-eval path) — lifecycle transition, refresh `last_evaluated`

### Retrieve

Pull existing knowledge for a current task.

- `wiki-query` — search + synthesize an answer from the wiki
- `meeting-followup` — surface unchecked action items relevant to current work context
- `experiment-review` — pulse-check mid-run or guide the verdict at `review_date`

Catalog retrieval is handled by Obsidian Bases directly; no skill needed.

### Maintain

Keep the vault healthy.

- `vault-inspect` — diagnostic sweep, S-*, W-*, and W-EVENT-* rules
- `note-cleanup` — interactive cleanup session (forks to `@vault-curator`)

### Utility

Mechanical helpers.

- `base-add` — create a structured entry for a named Obsidian Base

## Agent roles

Four agents handle all vault I/O. The split is by *verb* (read vs write
vs cleanup vs inspect), not by data type.

- **`vault-reader`** (Sonnet 4.6) — searches the vault, follows links, synthesizes across pages. Returns structured summary + cited paths. Never writes.
- **`note-editor`** (Haiku 4.5) — executes vault writes given finalized content. Drafts come from the skill (with the user); the agent's job is mechanical pattern application: frontmatter shape, skeleton order, hierarchy fields, link integrity.
- **`vault-curator`** (Sonnet 4.6) — interactive cleanup. Makes judgment calls on merges, splits, orphan resolution, convention violations. Invoked via the `note-cleanup` slash command.
- **`vault-inspector`** (Haiku 4.5) — runs the diagnostic rule set from `inspect-rules.md`, returns a scannable issue list. Never fixes; surfacing is the whole job.

### Why these four

Sonnet for the readers/curator — synthesis across pages and judgment
calls need reasoning capability. Haiku for the editor and inspector —
when content is drafted in the skill with user approval, the write is
mechanical pattern application; rule-checking is bulk pattern matching.
Both fit Haiku's strengths and budget.

No Opus. Defer until evidence emerges that specific operations need it
— most likely candidate would be a high-stakes Decision-page writer.

## Skill→agent contract

The invocation payload is a structured Markdown block. Canonical spec
lives in `agents/vault-reader.md` (`## Invocation contract`).

**Inbound (caller → agent):**

```markdown
## Intent
<one-line: operation + target>

## Constraints
<bullets: paths, conventions, scope flags, date ranges>

## Input
<substantive payload — query, paths, drafted content>

## Output shape
<what the caller expects back — synthesis, table, list, single answer>
```

**Outbound (agent → caller):**

```markdown
## Result
<the requested output in the requested shape>

## Sources
<bulleted: cited paths used in the synthesis>

## Notes
<caveats, ambiguities, missing data>
```

Errors return a `## Result: ERROR` + `## Suggested next step` block.

The payload is plain Markdown for two reasons: it's readable in
conversation logs without parsing, and it composes with how Claude
already structures responses.

## Where the rules live

| Layer | Source | Used by |
|---|---|---|
| Vault conventions | `~/Loose Ends/.claude/rules/wiki.md`, `~/Loose Ends/.claude/rules/catalog.md` | Humans + agents (loaded on demand) |
| Plugin reference (write-side distillation) | `references/wiki-templates.md`, `references/event-templates.md`, `references/bases.md`, `references/vault-conventions.md` | Agents (loaded by `@note-editor`, `@vault-reader`) |
| Diagnostic rules | `references/inspect-rules.md` | `@vault-inspector` |
| Tool gotchas | `references/obsidian-cli-gotchas.md` | Any agent shelling to obsidian-cli |
| Work-context substitution | `~/Loose Ends/.claude/knowledge-work.local.md` + `references/work-context-config.md` | Meeting skills |

Vault rules are the canonical source of truth. Plugin references
distill them for agent-loading convenience; when they diverge, the
vault rule wins and the reference is regenerated.

## Adding things

### A new skill

1. Decide its lifecycle stage. Pick an existing-stage column in the matrix; if it genuinely doesn't fit, propose a new stage and challenge whether it's really new work or a peer of an existing skill.
2. Pick the target agent. New writes route to `@note-editor`; new reads to `@vault-reader`; new diagnostics to `@vault-inspector`; new interactive cleanup to `@vault-curator`.
3. Write the skill body following the established pattern: intent gathering inline, then a dispatch block with the invocation payload, then result-surfacing logic.
4. Update the README matrix and this file's stage section.

### A new agent

Default answer: don't. Four agents cover the four verbs (read / write /
cleanup / inspect) and adding a fifth introduces coordination cost.
Acceptable triggers:

- A new verb that doesn't fit (e.g., a "diff two vaults" agent for backup verification — but does that belong in this plugin at all?)
- Evidence that one of the existing agents is overloaded at its model class and splitting helps (e.g., `@note-editor` quality suffering on Decision-page writes — split into `@note-editor` Haiku + `@decision-editor` Sonnet)

### A new `page_type`

1. Justify by usage: three or more pages of the new shape should be plausible. Until then, the closest existing template covers the case.
2. Add the skeleton to `~/Loose Ends/.claude/rules/wiki.md` (or the appropriate vault rule).
3. Mirror in the plugin reference (`references/wiki-templates.md` for wiki types, `references/event-templates.md` for event types).
4. Add corresponding `W-*` or `W-EVENT-*` rules to `references/inspect-rules.md`.
5. Update the skill(s) that produce the new shape (or add `event-capture`-style routing if it's a new event_kind).

### A new reference

Move an inline body block out of a SKILL.md when:

- Two or more skills reference the same substantive content
- The content is long enough that it bloats the skill description in `marketplace.json`
- It changes independently of the skill workflow (e.g., vault conventions vs the skill that uses them)

Don't preemptively externalize content used by exactly one skill.

## What's intentionally out of scope

- Cross-vault operations (importing from a second Obsidian vault, exporting to git, mirroring to Notion). The plugin is single-vault.
- Live transcription. Skills accept pasted transcripts; they don't record.
- Engineering decisions in `~/Loose Ends/Decisions/` (those are owned by the `ndr` plugin).
- Vault-wide bulk migrations. `vault-inspect` flags issues; `note-cleanup` resolves them interactively; neither tries to fix everything at once.
- An Inbox-triage skill. Open question; defer until pain emerges.

## History

The plugin grew domain-by-domain (wiki, catalog, meetings, experiments,
notes) to 20 skills + 2 agents before settling on this workflow shape.
The rewrite from 0.x to 1.0 (May 2026) collapsed near-duplicate skills
(`wiki-ingest` + `wiki-stub` → `wiki-create`; `note-health` +
`wiki-lint` → `vault-inspect`), removed two Anki-specific skills, moved
vault-knowledge and bases-knowledge from skills to references, and
converted every remaining skill to the fork-and-delegate pattern.
