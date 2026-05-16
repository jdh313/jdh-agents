# knowledge-work Rewrite Design

> **Status:** Draft — design session 2026-05-15. Not yet implemented.
> **Owner:** Jacob Hoehler
> **Lifetime:** Delete or move to `references/` after the rewrite ships.

This document captures the design decisions for restructuring the `knowledge-work` plugin. It is the source of truth for the implementation that follows.

## Why we are rewriting

The plugin grew to 20 skills + 2 agents domain-by-domain (wiki, catalog, meetings, experiments, anki, notes, vault meta) without a workflow shape. Symptoms surfaced in the design session:

- Wrong skills fire on ambiguous triggers, or no skill fires at all.
- The user cannot hold all 20 skills in working memory and reach for the right one.
- Skills are isolated tools, not steps in an end-to-end pipeline.
- Multiple skills do similar things with fuzzy boundaries (`wiki-stub` vs `wiki-ingest`, the maintenance trio, vault-knowledge vs bases-knowledge).
- Some skills are coupled to archived paths (`Waites/Meetings/`) — the user's work context shifted to Carta but the plugin did not follow.

## Design principles

1. **Workflow-first organization, not domain-first.** Skills map to lifecycle stages (Capture, Process, Retrieve, Evolve, Maintain), not to the data types they operate on. The README presents the matrix view.
2. **Gist hub + `expands:` children for substantial knowledge.** The catalog top-level page (e.g. `Jujutsu (jj)`) is the model: thin definition + auto-rendered Breadcrumbs codeblocks for "Going deeper" and "Related topics", with depth accumulating in child pages that declare `expands: [[Parent]]`.
3. **Template as forcing function.** A tight skeleton with no prose-friendly body slots prevents bloat at creation. The catalog gist holds shape because it has nowhere for new material to land except a child page. Apply the same logic to other gist-producing skills.
4. **No skill touches vault files directly.** All vault reads and writes flow through agents. The main session holds intent and structured summaries, never raw file contents.
5. **Skills draft, user approves, agents execute.** Skills generate finalized content in the main session (where the user can see it, correct it, and approve). Agents then execute the mechanical write + cascade work. This makes `note-editor` a Haiku-class executor rather than a Sonnet-class writer.
6. **Template inventory stays small; `wiki-graduate` is the escape valve.** New templates earn their place only when three or more pages would clearly fit the shape. Everything else uses the generic gist hub skeleton, and depth is split off via `wiki-graduate` when accumulation happens.

## Lifecycle (5 stages)

The skill inventory presents as a lifecycle matrix in the README. Empty cells are intentional — Bases handle catalog retrieval; meetings and experiments do not have dedicated maintenance because they age out via vault-wide cleanup.

| Stage | Skills |
|---|---|
| **Capture** | `wiki-create` (stub mode), `event-capture`, `meeting-notes`, `experiment-start`, `note-capture`, `note-suggester`, `catalog-evaluate` (new entry) |
| **Process** | `wiki-create` (ingest mode), `wiki-refresh`, `wiki-graduate`, `meeting-restructure`, `catalog-evaluate` (re-eval) |
| **Retrieve** | `wiki-query`, `meeting-followup`, `experiment-review` |
| **Maintain** | `vault-inspect`, `note-cleanup` |
| **Utility** | `base-add` |

## Skill inventory (16)

| # | Skill | Pattern | Notes |
|---|---|---|---|
| 1 | `wiki-create` | Forks to `note-editor` (ingest) / Inline (stub) | Merger of `wiki-ingest` + `wiki-stub`. Detects "URL/file provided?" — ingest mode if yes, stub mode otherwise. References hold per-mode templates. |
| 2 | `wiki-refresh` | Forks to `note-editor` | Update existing page with newer info. Refresh-aware: small updates to gist, substantive updates create or update a child. |
| 3 | `wiki-query` | Forks to `vault-reader` | Search + synthesize answer from wiki. Agent returns synthesis + cited sources to main session. |
| 4 | `wiki-graduate` | Forks to `note-editor` | New skill. Split a fat gist into `expands:` child cleanly: section move, link rewrite, Breadcrumbs update. |
| 5 | `catalog-evaluate` | Forks to `note-editor` (re-eval) / Inline+light fork (new entry) | Creates gist hub + Decision child. Re-eval updates verdict, alternatives, last_evaluated across two pages. |
| 6 | `event-capture` | Inline + light fork | New skill. Captures `type: event` pages (incident/appointment/extensible). Interactive field gathering inline; forks to `note-editor` for write + entity check. |
| 7 | `meeting-notes` | Forks to `note-editor` | Reads `active_work_context` from plugin local config. Was hardcoded to `Waites/Meetings/`. |
| 8 | `meeting-followup` | Forks to `vault-reader` | Same config retarget. Read-only surfacing of unchecked action items. |
| 9 | `meeting-restructure` | Forks to `note-editor` | Same retarget. Distributes durable facts from a meeting note across multiple destination pages. |
| 10 | `experiment-start` | Forks to `note-editor` | Scaffolds experiment page. Already vault-location-agnostic (uses top-level `Experiments/`). |
| 11 | `experiment-review` | Forks to `vault-reader` (check-in pull) then inline (verdict walk) | Pulls daily-note check-ins via agent, then walks user through verdict interactively. |
| 12 | `note-capture` | Forks to `note-editor` | One-liner capture to today's daily note. Manual-only (`disable-model-invocation: true`). |
| 13 | `note-suggester` | Inline | Passive ambient suggestions during coding. No vault I/O at trigger moment; batched captures at session end. |
| 14 | `note-cleanup` | Forks to `vault-curator` | Already correct. Tighten description to call out the fork-context value. |
| 15 | `vault-inspect` | Forks to `vault-inspector` | Merger of `note-health` + `wiki-lint`. Scope arg: `--structural`, `--wiki`, default both. |
| 16 | `base-add` | Forks to `note-editor` | Manual utility. Disable-model-invocation. |

## Skills removed

| Skill | Disposition |
|---|---|
| `wiki-ingest` | Merged into `wiki-create` |
| `wiki-stub` | Merged into `wiki-create` |
| `note-health` | Merged into `vault-inspect` |
| `wiki-lint` | Merged into `vault-inspect` |
| `vault-knowledge` | Demoted to `references/vault-conventions.md` |
| `bases-knowledge` | Demoted to `references/bases.md` |
| `anki-cards` | Removed entirely (Anki use deprecated) |
| `anki-learn` | Removed entirely (Anki use deprecated) |

## Agent inventory (4)

| # | Agent | Model | Verb | Invoked by |
|---|---|---|---|---|
| 1 | `vault-reader` | Sonnet 4.6 | Read + synthesize | `wiki-query`, `meeting-followup`, `experiment-review`, `event-capture` (entity lookup) |
| 2 | `note-editor` | Haiku 4.5 | Mechanical write + cascade | `wiki-create`, `wiki-refresh`, `wiki-graduate`, `catalog-evaluate`, `meeting-notes`, `meeting-restructure`, `experiment-start`, `event-capture` (writes), `note-capture`, `base-add` |
| 3 | `vault-curator` | Sonnet 4.6 | Interactive cleanup | `note-cleanup` |
| 4 | `vault-inspector` | Haiku 4.5 | Rule-check + structured report | `vault-inspect` |

### Model rationale

- **Sonnet for reader and curator** — synthesis across pages, judgment calls on merge/split/keep, convention enforcement during cleanup. These tasks need reasoning capability.
- **Haiku for editor and inspector** — when content is drafted in the skill (with user approval) and the agent receives finalized payload, the write becomes mechanical pattern application. Inspection is bulk rule-checking against rule sets. Both fit Haiku's strengths.
- **No Opus** — defer until evidence emerges that specific operations need it. Most likely candidate for a future Opus agent: writing catalog Decision pages. Currently those are drafted in the main session at the session's model.

### Why agents own all vault I/O

Main session context stays clean even after dozens of vault operations. Skills shrink to ~30-50 line files (gather intent, fork, display result). Vault expertise — conventions, templates, link integrity rules, anti-staleness — centralizes in agent prompts and reference files. Tool allowlists tighten (only agents hold vault-write tools).

## References (5 + 1 existing)

| Reference | Holds | Loaded by |
|---|---|---|
| `vault-conventions.md` | Folder structure, note types, frontmatter conventions, naming, tags, link rules. Was the `vault-knowledge` skill. | Loaded on-demand by any agent that needs conventions context |
| `bases.md` | Base registry, filter shapes, property templates per base. Was the `bases-knowledge` skill. | Agents working with `.base` files or producing entries |
| `wiki-templates.md` | Page_type skeletons: catalog gist hub, non-catalog gist hub, generic concept, how-to, evaluation. | `note-editor` when writing wiki pages |
| `event-templates.md` | Event_kind skeletons: incident, appointment. Extensible via new kind entries without new skills. | `note-editor` when writing event pages, `event-capture` when prompting |
| `inspect-rules.md` | Diagnostic rule sets — structural (orphans, dead-ends, frontmatter, naming) and wiki-semantic (page_type validation, skeleton match, anti-staleness, hard-wrap detection). | `vault-inspector` |
| `obsidian-cli-gotchas.md` | Existing. Obsidian-cli patterns and command examples. | Kept as-is. |

## New templates: `type: event`

Two new page_types under the `type: event` umbrella, both share frontmatter conventions and skim-friendly skeletons with domain-specific section names.

### `page_type: incident`

For reactive issue+fix documentation. Smart home, hobbies, homelab, devices. Distinct from `how-to` (which is a known recipe) — incidents are standalone issues that don't belong inside any recipe.

Frontmatter:

```yaml
---
owner: jacob | ai
type: event
page_type: incident
date: YYYY-MM-DD               # when it happened
status: resolved               # open | resolved | recurring
severity: medium               # low | medium | high (optional)
expands:
  - "[[Device/System]]"        # required — the entity affected
participants: []               # optional, e.g. ["[[Vendor Support]]"]
follow_up_by: YYYY-MM-DD       # optional
tags: []
date_created: YYYY-MM-DD HH:mm
date_modified: YYYY-MM-DD HH:mm
---
```

Skeleton:

1. *Neutral one-sentence summary*
2. `## Symptoms` — observable behavior, errors, logs
3. `## Context` — what changed, when it started, what was being attempted
4. `## Diagnosis` — what was actually wrong (the gold — this is what makes the page worth keeping)
5. `## Fix` — what resolved it (steps)
6. `## Prevention` — how to avoid recurrence (optional, omit if no clear answer)
7. `## See also`

### `page_type: appointment`

For medical, vet, dental, therapy, and similar provider visits. Single template covers human and pet (`expands:` target tells you which).

Frontmatter:

```yaml
---
owner: jacob
type: event
page_type: appointment
date: YYYY-MM-DD               # when the appointment occurred
status: completed              # completed | scheduled | cancelled | no-show
specialty: vet                 # vet | gp | dental | specialist | therapy | etc.
expands:
  - "[[Subject]]"              # human or pet
  - "[[Condition]]"            # optional — for condition-tracking
provider: "[[Dr. ___]]"        # optional, can also be a plain string
cost:                          # optional — useful for vet/uncovered
follow_up_by: YYYY-MM-DD       # next visit / monitoring deadline
tags: []
date_created: YYYY-MM-DD HH:mm
date_modified: YYYY-MM-DD HH:mm
---
```

Skeleton:

1. *Neutral one-sentence summary* (purpose + outcome)
2. `## Reason` — why this visit
3. `## Findings` — what the provider observed or determined
4. `## Treatment` — prescribed, performed, recommended
5. `## Follow-up` — next steps, next visit, at-home monitoring
6. `## See also`

### Compositional pattern (entity + event-log children)

The same shape composes across domains:

| Entity (gist hub) | Event children (`expands:` the entity) |
|---|---|
| Gear / device | Incidents |
| Pet (Jackson) | Vet visits, health-log entries |
| Health condition | Appointments, symptom changes |
| Person | Meetings, conversations |
| Project | Project meetings, decisions |

Entity pages auto-render their event history via Breadcrumbs `field-groups: [expansions]` codeblocks in `## Going deeper`. Free per-entity dashboards as a side effect of normal capture.

## Maintenance boundaries (documented decision)

The five maintenance pieces are distinct enough to keep separate. The fix is documentation, not merging.

| Piece | Verb | Scope | Mode |
|---|---|---|---|
| `vault-inspect --structural` | inspect (diagnostic) | Vault-wide structure | Read-only |
| `vault-inspect --wiki` | inspect (diagnostic) | Wiki-semantic (`owner: ai` + `type: wiki`) | Read-only |
| `note-cleanup` | entry point | (delegates to vault-curator in fork-context) | Forks to agent |
| `vault-curator` (agent) | cleanup worker | Anywhere directed | Read + write |
| `note-editor` (agent) | editing worker (different verb) | Anywhere directed | Read + write |

Decision tree to add to `wiki.md` or a new `maintenance.md` rule:

> When something feels wrong with the vault:
> - "What is broken structurally?" -> `vault-inspect --structural`
> - "Are wiki pages following conventions?" -> `vault-inspect --wiki`
> - "Let us clean up the vault together" -> `note-cleanup` (forks to `vault-curator`)
> - "Help me restructure / merge / enrich these notes" -> `@note-editor`

## Configuration

A new plugin-local config file replaces hardcoded Waites paths:

`<repo>/.claude/knowledge-work.local.md`:

```yaml
---
active_work_context: Carta
---
```

Skills that depended on `Waites/Meetings/` now read `${active_work_context}/Meetings/`. When the work context shifts again, update one line.

## Plugin doc shape

README is the gist (wide shot — the lifecycle matrix + headline architecture). Depth lives in `references/`. The matrix table is the load-bearing visual; individual stage explanations live in `references/architecture.md` and per-skill SKILL.md files.

The current README is reorganized accordingly.

## Migration plan (proposed order)

1. **Anki removal** — delete `skills/anki-cards/` and `skills/anki-learn/`. Update README. Cheap, isolated.
2. **Reference extraction** — convert `vault-knowledge` and `bases-knowledge` skills to reference files. Update other skills' allowlists.
3. **New agents** — write `vault-reader`, `vault-inspector`. Define their tool allowlists, prompts, models.
4. **Skill collapses** — merge `wiki-ingest` + `wiki-stub` -> `wiki-create`. Merge `note-health` + `wiki-lint` -> `vault-inspect`. Update trigger phrases. Move shared logic to references.
5. **Existing skills retargeting** — wire `meeting-notes` / `meeting-followup` / `meeting-restructure` to `active_work_context` config.
6. **Existing skills delegation** — convert skills to fork-and-delegate pattern. Skills become thin orchestrators; agents own the writes.
7. **New skills** — `event-capture`, `wiki-graduate`.
8. **New templates** — add `incident` and `appointment` to `wiki.md` (vault rules) and `references/event-templates.md`. Update `vault-inspect` rule sets.
9. **README and architecture docs** — rewrite README as gist. Add `references/architecture.md`. Update plugin.json version.
10. **Plugin validation** — run `python scripts/sync_marketplace.py && python scripts/validate_schema.py && python scripts/lint_plugins.py`.

## Out of scope (intentional)

- **Vault `CLAUDE.md` updates.** The vault rules at `~/Loose Ends/.claude/CLAUDE.md` describe Waites/ as current work context, with subfolders (Meetings, Decisions, Projects, Repos, System Notes). Carta is not mentioned. The Bases registry still references Waites paths. This is a vault-maintenance task to address separately; the plugin redesign should not also tackle vault docs.
- **`ndr` plugin territory.** Engineering decisions in `~/Loose Ends/Decisions/` are owned by the `ndr` plugin (separate work in progress by another agent). `Waites/Decisions/` is archived and not relevant.
- **Service calls / travel / shopping research / purchases templates.** The event template is extensible; add new event kinds (via `references/event-templates.md`) when demand emerges. Do not pre-build.
- **Splitting `note-editor` for high-stakes writes.** Defer until evidence shows Decision page quality is suffering at Haiku-with-drafted-content quality.
- **Inbox triage skill.** Open question — see below.

## Open questions

| Question | Status |
|---|---|
| Is an Inbox-triage skill needed, or does Inbox/ stay write-once-read-manually? | Defer until pain emerges |
| Should `wiki-create` (stub mode) stay inline, or fork to `note-editor` like all other writes? | Lean fork for uniformity. Confirm during implementation. |
| What does the skill->agent intent schema look like in practice? | Specified during agent prompt writing. Likely a small JSON-shaped payload per skill type. |
| `note-suggester` triggers — currently fires during coding sessions. Should it also fire during writing/research sessions? | Defer. Current behavior is fine. |

## Pre-existing dependencies and risks

- **Vault `CLAUDE.md` is stale.** Carta/, Personal/Reflections/, Mulling/, top-level Decisions/, etc. are not described in the rules. `vault-knowledge` (and its replacement `references/vault-conventions.md`) loads stale info. Flagged as separate maintenance task.
- **Bases registry references Waites paths.** Filters like `file.inFolder("Waites/Repos")` will return empty results. Out of scope for plugin redesign; vault maintenance task.
- **Plugin assets lint.** Per `45a6371 chore: allow .base extension in plugin asset lint allowlist`, recent loosening of allowlist. Verify new reference files (.md) pass lint.

## Counts

| | Before | After |
|---|---|---|
| Skills | 20 | 16 |
| Agents | 2 | 4 |
| References | 1 | 6 |
| Anki skills | 2 | 0 |
| Total skill/agent components | 22 | 20 |

Slight reduction in component count, but the structural change is the bigger win: workflow-shaped, agent-mediated, reference-backed instead of skill-sprawled.
