---
name: meeting-restructure
description: Restructure an already-filed meeting note by redistributing its durable facts into canonical notes (project pages, people pages, wiki pages) and leaving the meeting note as a slim log with outbound links. Use when the user says "restructure this meeting note", "distribute this meeting", "split this meeting up", "pull durable facts out of this meeting", "this note is stream-of-consciousness", or otherwise asks to refactor an existing meeting note. Distinct from `meeting-notes`, which files fresh raw notes — this skill operates on notes that are already filed, possibly days or weeks later.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(obsidian-cli *)
---

# Meeting Restructure

## Core principle

The meeting note owns no content it didn't originate. Durable facts live on canonical reference pages; the meeting note is a dated log with outbound links and provenance footnotes on the destinations.

This skill drafts the distribution map and reshaped meeting note
interactively; `@vault-reader` reads source and destination context, an
independent `general-purpose` subagent fact-checks the rewrites, and
`@note-editor` executes all writes.

## Configuration

Path references use `${active_work_context}` as a placeholder for the
top-level work-context folder. Before any vault write, read
`~/Loose Ends/.claude/librarian.local.md` and extract
`active_work_context` from its frontmatter. Substitute that value for
`${active_work_context}` everywhere below. Default to `Work` if the
config file or key is missing. See
`${CLAUDE_PLUGIN_ROOT}/references/work-context-config.md` for full
substitution rules.

## When to Invoke

- User asks to restructure, redistribute, or split an existing meeting note.
- User describes a meeting note as "stream-of-consciousness" or "unstructured".
- User notices that a meeting note has accumulated facts worth surfacing elsewhere.
- User has a transcript for a meeting whose note was already restructured
  and wants to diff and augment the canonical pages — run in **Follow-up
  mode** (see end of workflow).

Do NOT invoke for:
- Fresh raw notes that haven't been filed yet — use `meeting-notes`.
- One-line clarifications — edit directly.
- Migrating notes between folders — that's a filing operation.

## Vault tool usage

Use `obsidian-cli append file=<target> content='...'` for section-level redistribution into other notes. Use `mcp__obsidian-mcp__patch_note` to replace the original section in the meeting note with a slim summary + outbound link. Use Edit only when patch_note can't anchor (e.g., section boundaries are fuzzy).

## Workflow

### 1. Pull the meeting note and surrounding context

Dispatch via `@vault-reader`:

```markdown
## Intent
read meeting note and gather destination context for restructure

## Constraints
- Read the target meeting note in full
- Read any notes it references by wikilink (project pages, people pages, wiki pages — wherever facts could land)
- Flag wikilinks to pages that don't exist (tools, concepts, people, projects that may need stubs)

## Input
meeting note path: <path>

## Output shape
- meeting_note: <full content>
- destination_candidates: [{path, snippet of relevant section}]
- missing_targets: [<wikilink target with no backing page>]
```

### 2. Classify each line

Useful mental model: a 2×2 on **durable vs ephemeral** and **about a thing vs about a person**.

|  | About a thing | About a person |
|---|---|---|
| **Durable** | Project / wiki / catalog page | Person page |
| **Ephemeral** | Stays in meeting note | Stays in meeting note |

Plus two orthogonal annotations:

- **Action items** — stay in the meeting note under `## Action items`.
- **Verbatim quotes** — stay in the meeting note under `## Quotable`. Quotable means literal speech; paraphrase is never Quotable. If a quote also encodes a durable fact, do both: canonicalize as prose on the destination *and* keep the quote in the meeting note.

**Durability test:** does this inform decisions beyond the immediate next action? If yes, durable. Transient state (who was traveling, who's on PTO) is ephemeral even if factually true.

**Action items with embedded facts:** when an action item carries a parenthetical or subordinate clause encoding a durable fact ("pull X from Harvest (the data is actually in Y)"), extract the fact to its destination and leave a cleaner action item behind.

**Destination choice, most specific wins.** When a fact could plausibly land on two pages, put it on the most-specific page; other pages cross-link with `see [[X]]` rather than duplicating.

**Destination choice within a page:** cluster related content near semantically adjacent sections. Extend an existing subsection when the topic already has a home; avoid scattering related bullets across multiple new sections.

### 3. Propose a distribution map — pause for approval

The map is the single planning gate. Present a table with every destination edit, every stub decision, and every risk flagged up front — don't let these leak into later steps.

| Source line | Destination | New section? | Flags |
|---|---|---|---|
| "Moving to open-source models later this year" | Lighthouse.md → ## Roadmap | Yes | |
| "Each hospital deployment has its own AWS account" | Lighthouse.md → ### Architecture | No (append) | |
| "Freddie treats X like any user" | AcmeOS.md → ## Stakeholder direction | No (append) | |

Flags to surface in the map when they apply:

- **Anchor hazard** — destination heading contains `:`, `/`, `?`, `#`, or wikilink syntax (`[[…]]`). For wikilinks specifically: the link form must use the *rendered* text (alias-resolved, brackets stripped) — e.g. `## [[Pydantic]] Vs. [[Python Dataclasses|Dataclasses]]` is referenced as `[[Page#Pydantic Vs. Dataclasses]]`, not as nested brackets (which is malformed). Propose linking to the parent heading instead, or ask the user if renaming the subheading is acceptable.
- **Memory collision** — a user-level memory or feedback rule might restrict this decision (e.g. a "don't stub Reference/ pages from employer sources" rule). State the rule, state your reading, and let the user rule on it before editing.
- **Stub decision** — page doesn't exist. Person → stub by default; tool/concept/project → flag and defer unless asked.
- **Frontmatter backfill** — meeting note missing `summary:` or `participants:`. Note the planned value.

**Scope guard:** if the map would be hard for the user to review in one pass (many destinations, many new sections, many new stubs), propose staging into rounds.

Wait for approval or adjustment before editing.

### 4. Draft the distribution edits

For each destination edit, prepare the exact insertion content and
location. Drafting rules:

- **Append vs new section:** append when thematic scope *and* structural style match (bullets into bullets, prose into prose). Otherwise new subsection. When in doubt, new subsection — less invasive than reformatting existing content.
- **Cluster on the destination:** place the new content near existing content on the same actor or topic. Don't scatter a new section at the top of the page when a related section already exists mid-file.
- **Canonical-reference tone, not meeting-minute tone.** "Bruce said we should move to open-source models" becomes "Move to open-source models later in 2026."
- Add the provenance footnote on the first mention per destination page; reuse the same ID for subsequent references.

The writes themselves dispatch to `@note-editor` after step 5
(fact-check). The agent prefers Edit over Write to preserve hand-set
frontmatter, bumps `date_updated` on every destination, and applies
footnotes per the format below.

#### Provenance footnote format (applied during step 4)

```markdown
Fact text here.[^2026-04-21-bruce]

[^2026-04-21-bruce]: Per [[Person Name]] in [[path/to/meeting note]].
```

Convention: `<YYYY-MM-DD>-<lastname-lowercased>`. For multi-principal meetings: if principals each drove distinct topical threads, split per-principal (`2026-04-22-stevie`, `2026-04-22-joni`); if they co-discussed a single topic, use topic-based (`2026-04-22-ops-tool`).

**Relayed speech:** cite the person in the room, not the person being quoted. If the relay matters, surface it in the body: "Per [[Stevie]] (relaying [[Freddie]]): …"

Reuse one ID per meeting per page — one footnote, many references.

### 5. Fact-check the rewrites (independent subagent)

Before reshaping the meeting note, dispatch a foreground `general-purpose` subagent for an independent fact-check. The subagent has no session context — that's the point. The meeting note is still the full source of truth at this moment; once step 6 reshapes it, this check is much harder to run.

Subagent prompt shape (self-contained — the subagent cannot see this conversation):

```
Independent fact-check of a meeting-note restructure. You have no prior context — that's intentional. Do not infer beyond what's literally in the files.

Source meeting note: <absolute path>
Edits applied (file → section → rewritten text):
1. <destination file> → <section> → "<rewritten prose>"
2. ...

For each edit, produce one row:

| Destination claim | Source line(s) | Verdict | Notes |
|---|---|---|---|
| <rewritten prose> | <literal quote from meeting note, or "NOT FOUND"> | matches / certainty-drift / attribution-drift / precision-drift / unsupported | <one line> |

Verdict definitions:
- matches — faithful to source, no drift
- certainty-drift — source hedge ("maybe", "should", "might", "consider") disappeared in rewrite
- attribution-drift — person cited in provenance footnote didn't actually say it
- precision-drift — numbers, dates, names, or quantifiers diverged
- unsupported — no source line justifies this claim

Return only the table plus a one-line summary of issues found. Do not propose rewrites.
```

**After the subagent returns:**

- Show the full table to the user regardless of outcome (always-report mode — calibration signal for when the check earns its keep).
- If all rows are `matches`: proceed to step 6.
- If any row is not `matches`: stop, propose corrections for each flagged row, wait for user approval before reshaping the meeting note.

Subagent flags; main agent fixes. Do not have the subagent write — it doesn't have the placement/section context needed to decide *how* to correct.

### 6. Dispatch the writes (distribution + reshape)

Hand the approved edits and the reshaped meeting note to `@note-editor`:

```markdown
## Intent
restructure meeting note: distribute facts and reshape

## Constraints
- Order: destination edits first (with provenance footnotes), then meeting note reshape
- Prefer Edit over Write to preserve hand-set frontmatter
- Append vs new section per the drafted plan; do not improvise placement
- Bump `date_updated` on every destination that received a material edit
- Footnote IDs: `<YYYY-MM-DD>-<lastname-lowercased>`; reuse per page
- Meeting note reshape target shape: see below

## Input
- destination_edits: [{path, section_target, append_vs_new, content, footnote_id, footnote_definition}]
- meeting_note_target: <full reshaped content per the target shape below>
- stubs_to_create: [<full drafted content per stub>] (only when explicitly approved)

## Output shape
Per file: action (edit/write), path, sections touched, one-line change summary.
```

Meeting-note reshape target shape:

```markdown
---
type: meeting
date: YYYY-MM-DD
date_created: YYYY-MM-DD
date_updated: YYYY-MM-DD
participants:
  - "[[Jacob Hoehler|Me]]"
  - "[[Other Person]]"
summary: "Topic with [[Principal]]; plus side-thread on X."
tags:
  - type/meeting
  - context/<area>
---

`= this.summary`

## Topics covered

- **Topic** — one-line description. → [[Destination#Section]]

## Quotable

> Verbatim quote, if any, with attribution.

## Open questions

(none)

## Action items

- [ ] Item text [owner: @person] [by: YYYY-MM-DD | open] [src: MM:SS]
```

- First body line is a Dataview inline query echoing the summary frontmatter.
- Summary template: "Topic with [[Principal]]; plus side-thread on X." — concise, wikilinks the principals, names the threads.
- `date_created` preserves the note's original creation date; `date_updated` is bumped whenever the meeting note itself is edited (not when canonical destinations are). Backfill both when restructuring a note that lacks them — use the meeting `date:` for `date_created` and today for `date_updated`.
- Omit `## Quotable` when there are no verbatim quotes.
- For empty sections (`## Open questions`, `## Action items` with nothing to record): use the literal `(none)` marker, not an empty bullet or blank body. The marker is what distinguishes "author considered this and had nothing" from "author forgot."
- Action items carry `[owner:]` and `[by:]` (date or literal `open`) on every open item, plus `[src: MM:SS]` when a transcript exists. See the `meeting-notes` skill's Action Item Handling section for the full convention.

### 7. Verify before reporting done

Run through this checklist literally (using the agent's per-file change
summary plus a quick `@vault-reader` re-read of any destination whose
anchor normalization is suspect):

- [ ] Every outbound `[[Target#Section]]` link: the *rendered* heading text exists on the destination file. If the heading contains wikilinks (`## [[X]] Vs. [[Y|Z]]`), normalize before comparing — strip `[[`/`]]`, resolve `[[Target|alias]]` to `alias`.
- [ ] Footnote definitions count matches footnote reference count per destination page.
- [ ] New stubs are linked from at least one existing note.
- [ ] `date_updated` (or equivalent) bumped on every destination that received material edits.
- [ ] Obsidian anchor normalization: verify any `[[Page#Section]]` where Section contains punctuation by reading the destination, not trusting the anchor resolves.

## Follow-up mode: transcript arrived after restructure

When a transcript is provided for a meeting whose note is already in the slim log shape (detection: `## Topics covered` contains `→ [[Target#Section]]` outbound links), do not treat the transcript as a fresh restructure input. Run in diff-and-correct mode — compute the delta between the transcript and what's already on canonical pages, then augment rather than duplicate.

See `references/follow-up-mode.md` for the full workflow: preconditions, the two-subagent delta/drift passes, the delta-map format, the per-row correction approval gate, and the footnote-body upgrade pattern.

## Vault Conventions

Target vault: `~/Loose Ends/`.

- **People notes:** `People/` (flat). Self-note is `People/Jacob Hoehler.md` with alias `Me`. Template: `Templates/Person Note.md`.
- **Work project notes:** `${active_work_context}/Projects/`.
- **Work meeting notes:** `${active_work_context}/Meetings/`. Template: `Templates/Meeting Note.md`.
- **Wiki pages:** distributed; identified by `owner: ai` + `type: wiki`. See `~/dotfiles/claude/rules/11-knowledge-wiki.md`.
- **Software Catalog:** `Reference/Tools/Software Catalog/`. See `~/dotfiles/claude/rules/12-software-catalog.md`.

Meeting note frontmatter: `type: meeting`, `participants:` (list of wikilinks), `date: YYYY-MM-DD`, `summary:` (string, wikilinks allowed).

Person note structure: `## Key Information`, optional `## Notable Interactions`, and `## Meeting Log` with a Dataview block scoped by `FROM [[#]] WHERE type = "meeting"`.

## What the skill does not automate

Leave to model plus user judgment:

- Which exact fact belongs on which page when multiple destinations are plausible.
- Whether a quote is worth preserving inline.
- Whether a stub should be minimal or full.
- Whether to stage a large restructure into rounds.

When in doubt, put the choice in the distribution map and let the user rule on it.
