---
name: capture-decision
description: Capture engineering decisions from the current conversation as atomic markdown artifacts in `~/Loose Ends/Decisions/`. Use when the user invokes `/capture-decision`, says "capture this decision", "record this", "let's write this up as a decision", or signals at end of a chat that decisions landed and should be persisted. Materializes one file per atomic decision with required frontmatter, enforces taxonomy, and structurally protects the supersession primitive (refuses to write a revising decision without `supersedes:`).
argument-hint: "[optional hint about what to capture]"
allowed-tools:
  - mcp__obsidian-mcp__write_note
  - mcp__obsidian-mcp__read_note
  - mcp__obsidian-mcp__read_multiple_notes
  - mcp__obsidian-mcp__update_frontmatter
  - mcp__obsidian-mcp__list_directory
  - mcp__obsidian-mcp__search_notes
  - Read
  - Edit
  - Write
---

# capture-decision

## Overview

Detect atomic decisions in the current conversation, draft each as a markdown atom, confirm with the user, and write to `~/Loose Ends/Decisions/`. Refuse to write malformed or supersession-blind artifacts.

This skill encodes the **write side** of nested-decision-records (ndr). It is the only path to creating a decision record in this system — the discipline is the tool.

## Hard rules (don't relax)

1. **Atomic only.** One chosen path, one set of consequences. Bundled candidates (e.g. "use FastAPI + Postgres") MUST be split into N atoms. Never write a bundle.
2. **Required frontmatter.** Refuse to write if any of these is missing or empty: `id`, `title`, `status`, `decision_date`, `project`, `area`, `topic`, `reversibility`. `supersedes:` must be **present** (may be `[]`).
3. **Supersession refusal is structural, not advisory.** If the conversation shows revising intent ("revises", "supersedes", "instead of", "we changed our mind on") OR `informed_by:` includes a `current` decision whose substance the new decision contradicts, AND `supersedes:` is empty — refuse. Print: "This looks like a revising decision but `supersedes:` is empty. Name the decision(s) being revised, or confirm this is a fresh decision."
4. **Two-write supersession (three-write with alias handover).** When `supersedes:` is non-empty: write the successor first, THEN patch each predecessor (`status: superseded`, append successor wikilink to `superseded_by:`). **If a predecessor carries any `aliases:`, the patch also moves each slug** — append to the successor's `aliases:` and clear the predecessor's `aliases:` to `[]`. The slug handover is part of the same patch sequence, not a separate user step. If a patch fails after the successor lands, REPORT the half-state (which slugs were moved, which weren't) and exit non-zero. Never silently leave a partial.
5. **Multi-supersession is manual.** If a predecessor is already `superseded` by a different successor, refuse the patch. Print which atom is the prior successor and stop. The user must reconcile by hand.
6. **Taxonomy enforcement.** Reject unknown `area:` or `topic:` values. Prompt "use existing or add new?"; on "add new", append the value to the relevant `~/Loose Ends/Decisions/.taxonomy/*.yaml` file before writing the atom.
7. **Review-then-persist.** No draft hits disk before the user accepts. There is no `draft` status. Lineage and identity stay reviewed longest.
8. **Always single-file.** Decisions are written as `<id>-<kebab-title>.md`. No directory form, no descent files — hybrid altitude callouts handle length-management inside the single file.
9. **Hybrid altitude body shape.** Every section is `heading + one-line gist + (optional) collapsible callout`. The trailing `-` on `[!info]-` / `[!warning]-` makes callouts default-collapsed. Reader sees gist on scan; callouts open on demand.
10. **Assumptions live in the body, not frontmatter.** Each load-bearing assumption appears as a backtick-separated slug under `## Assumptions`, plus one `> [!warning]- <slug>` callout containing description + `**Current state:**` / `**Revisit if:**`. Never serialize assumption details into YAML.
11. **No frontmatter restatements in prose.** `derived_from:`, `supersedes:`, `informed_by:` are YAML fields. Don't repeat them in the body as `derived_from: F. revises: A.scope` — body prose explains substance.
12. **Omit empty sections.** If no alternatives were considered, drop `## Alternatives` entirely. Don't render empty headings. `## Decision` is the only always-required section.
13. **Slug uniqueness.** Any value in `aliases:` must be unique vault-wide. Before writing an atom with non-empty `aliases:`, verify via `mcp__obsidian-mcp__search_notes` that no other atom holds the slug. Refuse to write a duplicate. (Exception: during supersession, a slug being moved from predecessor to successor is exempt from the uniqueness check against its predecessor — the predecessor is vacating the slug in the same operation.)
14. **Lazy slug minting.** Default `aliases: []`. Only mint a slug when the user signals the atom needs atom-grain external referenceability (i.e., the decision must be referenceable as `ndr:#<slug>` from code or vault notes, not just by id or topic). Use `ndr-` namespace prefix. Most atoms never carry a slug.

## Inputs

- `$ARGUMENTS` — optional free-text hint about what to capture. If absent, scan the whole conversation.

## Reference paths

- **Vault decisions:** `~/Loose Ends/Decisions/` (one atom per file, `<id>-<kebab-title>.md`).
- **Schema spec:** `${CLAUDE_PLUGIN_ROOT}/references/frontmatter-schema.md`.
- **Taxonomy files (vault-resident, mutable):** `~/Loose Ends/Decisions/.taxonomy/areas.yaml`, `~/Loose Ends/Decisions/.taxonomy/topics.yaml`. The capture skill reads and (with user approval) appends to these.
- **Taxonomy doc:** `${CLAUDE_PLUGIN_ROOT}/references/taxonomy.md` (growth-rule spec).
- **Template:** `${CLAUDE_PLUGIN_ROOT}/references/decision-single.md`.

## Method

### Step 1 — Scan

Read the current conversation context. Identify N candidate atomic decisions. Atomic = one chosen path, one set of consequences. Common atomic shapes:

- "Use X for Y" (one tool, one purpose)
- "Don't do X" (a rejected path)
- "X over Y because Z" (a chosen path with a named alternative)

Split bundles. "We'll use FastAPI and Postgres" is two atoms. "Use FastAPI because it's async and we already have Postgres" is one atom (Postgres is context, not a co-decision).

Discard:

- Open questions ("should we use X?") — not decisions yet.
- Pure observations ("this is slow") — not decisions.
- Tasks ("write the migration") — not decisions.

### Step 2 — Confirm count

Present each candidate as a one-line summary. Ask the user to confirm, edit titles, or remove candidates. Example:

```
I see 3 atomic decisions in this conversation:

1. Use FastAPI for the auth service
2. Single Postgres instance, no read replicas at MVP
3. Skip the worker queue for now

Confirm, edit titles, or drop any. (e.g. "drop 2, change 1 title to ...")
```

Wait for confirmation before drafting.

### Step 3 — Draft each atom

For each confirmed atom:

1. **Load schema + taxonomy.** Read the schema spec (`${CLAUDE_PLUGIN_ROOT}/references/frontmatter-schema.md`) and taxonomy YAML files (`~/Loose Ends/Decisions/.taxonomy/{areas,topics}.yaml`) on first iteration; cache for the rest of the session.
2. **Allocate ID.** List `~/Loose Ends/Decisions/` (via `mcp__obsidian-mcp__list_directory` with path `Decisions`). Parse `NNNN-<slug>.md` filenames. New ID = `max(existing) + 1`, zero-padded to 4 digits. If the folder doesn't exist or is empty, start at `0001`.
3. **Fill frontmatter from context.** Map conversation evidence to fields. Surface any missing required field as a prompt. Default `aliases: []` — do not mint a slug speculatively.
4. **Body.** Use the template from `${CLAUDE_PLUGIN_ROOT}/references/decision-single.md`. Hybrid altitude shape: each section gets a heading + one-line gist + (optional) collapsible callout for depth. Sections in order: `## Decision` (gist only, no callout), `## Why` (gist + `[!info]- Full reasoning`), `## Alternatives` (gist + `[!info]- Why they lost`; omit if none), `## Assumptions` (slug list + one `[!warning]- <slug>` per assumption; omit if none), `## Consequences` (gist + `[!info]- Detail`). Fill from conversation; sections with no content are omitted entirely.
5. **Optional slug minting.** After the body is drafted, ask once: "Does this decision need to be referenceable from outside the vault by an atom-grain name (i.e., not just by id or topic)? Most atoms don't." If yes, prompt for a slug. Namespace it with `ndr-` prefix (e.g., `ndr-monorepo-shape`). Check uniqueness via `mcp__obsidian-mcp__search_notes` for any atom whose `aliases:` field contains the proposed slug. If found, prompt for a different slug. Set `aliases: [<slug>]`.

### Step 4 — Review

Present the full draft (frontmatter + body) to the user. Accept edits inline. Make sure these fields are explicitly confirmed:

- `title`
- `project` (the project page this decision belongs to — wikilink)
- `area`, `topic` (with taxonomy check)
- `supersedes` (especially if empty — confirm "this is a fresh decision, not revising anything")
- `derived_from` (the rich source — chat path / mull wikilink)
- `aliases` (only if non-empty — confirm the slug is the right name and atom-grain external reference is actually needed)
- Body `## Assumptions` (load-bearing inputs whose change would flip the decision)

### Step 5 — Taxonomy check

Before writing: re-read `~/Loose Ends/Decisions/.taxonomy/areas.yaml` and `~/Loose Ends/Decisions/.taxonomy/topics.yaml`. If the draft's `area:` or `topic:` is not in the corresponding list:

```
"<value>" is not in <areas.yaml | topics.yaml>.
Use existing: <comma-separated list>
Or add new: <value>?
```

If "add new", `Edit` the appropriate vault taxonomy YAML file to append the value (alphabetical or end-of-list; preserve comments).

### Step 6 — Supersession check

If `supersedes:` is empty AND the conversation has revising intent OR the draft contradicts a `current` decision in `informed_by:`, REFUSE:

```
This looks like a revising decision (reason: <quote evidence>),
but `supersedes:` is empty.

Either:
  - Name the decision(s) being revised, e.g. `supersedes: ["[[Decisions/0042-...]]"]`
  - Confirm this is a fresh decision (re-invoke after editing).
```

Do not write.

### Step 7 — Write (single)

If `supersedes:` is empty:

- Write the file via `mcp__obsidian-mcp__write_note` to `Decisions/<id>-<kebab-title>.md`.
- Confirm: `Wrote Decisions/<id>-<kebab-title>.md`.

### Step 7-super — Write (two-write supersession, three-write with alias handover)

If `supersedes:` is non-empty:

For each predecessor wikilink P in `supersedes:`:

1. Read P via `mcp__obsidian-mcp__read_note`. Parse its `status:`, `superseded_by:`, and `aliases:`.
2. **Refuse if P.status is already `superseded` AND P.superseded_by != [this successor]:** print the existing successor and stop. Don't write anything.
3. **If P has non-empty `aliases:`, check slug uniqueness across the rest of the vault.** For each slug S in P.aliases: search for any atom (other than P) holding S in its `aliases:`. If found, REFUSE with:
   ```
   Slug "<S>" is held by both <P> and <other> — duplicate before supersession. Manual resolution needed.
   ```
   Stop. Don't write anything.

If all checks pass:

4. Write the successor file first. The successor's `aliases:` field includes any slugs being inherited from predecessors (merge: start with whatever was drafted as the successor's own `aliases:`, then append all slugs from each P.aliases).
5. For each P, patch via `mcp__obsidian-mcp__update_frontmatter`:
   - `status: superseded`
   - append the successor wikilink to `superseded_by:`
   - **If P had non-empty `aliases:`, set `aliases: []`** — the slugs have moved to the successor (written in step 4).
6. On any patch failure: print
   ```
   HALF-STATE: successor <id> written, but patching <P> failed: <error>
   Slugs moved to successor: <list of slugs that were on P, now on successor>
   Manual fix: edit <P>, set status: superseded, append "[[Decisions/<id>-<slug>]]" to superseded_by, clear aliases: [].
   ```
   Exit non-zero.

### Step 8 — Summarize

Report what was written and what was patched. One line per file.

## File naming

`<id>-<kebab-title>.md` — id is zero-padded 4 digits, title is kebab-cased ASCII. Example: `0042-use-fastapi-for-auth.md`. Always single-file.

## Output examples

### Fresh decision

```
Captured 1 decision:

  Decisions/0009-use-fastapi-for-auth.md
    area: tooling, topic: substrate
    supersedes: [] (fresh decision)
```

### Revising decision

```
Captured 1 decision with supersession:

  Decisions/0010-switch-to-litestar.md (successor)
    area: tooling, topic: substrate
    supersedes: ["[[Decisions/0009-use-fastapi-for-auth]]"]

  Patched:
    Decisions/0009-use-fastapi-for-auth.md
      status: current → superseded
      superseded_by: [] → ["[[Decisions/0010-switch-to-litestar]]"]
```

### Revising decision with alias handover

```
Captured 1 decision with supersession + alias handover:

  Decisions/0099-split-apps-into-services.md (successor)
    area: architecture, topic: repo-shape
    supersedes: ["[[Decisions/0011-monorepo-symmetric-apps-layout]]"]
    aliases: [ndr-monorepo-shape]  (moved from 0011)

  Patched:
    Decisions/0011-monorepo-symmetric-apps-layout.md
      status: current → superseded
      superseded_by: [] → ["[[Decisions/0099-split-apps-into-services]]"]
      aliases: [ndr-monorepo-shape] → []
```

### Refused

```
Refused: "Switch to Litestar for auth" looks like a revising decision
(intent words: "switch to", "instead of FastAPI"),
but `supersedes:` is empty.

Set supersedes to the decision being revised, or confirm this is fresh.
```

## When NOT to use this skill

- The user is **considering** a decision, not making one. (Capture afterward.)
- The user wants a quick journal entry — use `/note-capture` (daily-note append).
- The user wants to revise a decision's *body* without changing its substance — edit the file directly; don't write a new atom.

## Related

- `/decisions <topic>` — the read-side companion. Use it BEFORE capture to check whether a current decision on the topic already exists (avoid accidental parallel decisions).
- `${CLAUDE_PLUGIN_ROOT}/references/frontmatter-schema.md` — full schema spec.
- `${CLAUDE_PLUGIN_ROOT}/references/taxonomy.md` — taxonomy rules and growth protocol.
- `${CLAUDE_PLUGIN_ROOT}/references/workflow.md` — capture + read end-to-end.
