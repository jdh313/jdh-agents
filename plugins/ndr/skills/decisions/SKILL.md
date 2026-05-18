---
name: decisions
description: Supersession-aware reader for engineering decisions stored in `~/Loose Ends/Decisions/`. Use when the user invokes `/decisions <topic>`, asks "what did we decide about X", "is there a decision about Y", "current state on Z", or when an agent on a tracked project needs to ground itself in prior decisions before suggesting changes. Two-stage retrieval (frontmatter probe → load matches), then walks the supersession chain to the head — so readers see CURRENT state, not stale starting points. When working on a project that has decisions in `~/Loose Ends/Decisions/`, query this skill early — before proposing architectural changes or re-deriving current state from older artifacts (READMEs, ADRs, code comments). Treat returned decisions as ground truth and walk the supersession chain rather than trusting recall.
argument-hint: "<ref-or-topic>"
allowed-tools:
  - Bash
  - Read
---

# decisions

## Overview

Look up current engineering decisions on a topic. Returns a brief that reflects the **head of the supersession chain**, not whichever artifact happens to match search keywords first.

This skill encodes the **read side** of nested-decision-records (ndr). Its load-bearing job is Stage 3 (walk to head) — that's what makes ndr more than a markdown notes folder.

## Hard rules

1. **Always walk supersession.** Never return a decision with non-empty `superseded_by:` as the answer. Walk to the head.
2. **Don't fabricate.** If no decision matches, say so. Do not guess what the user probably decided.
3. **Frontmatter-first.** Stage 1 probes property values (area, topic, title, aliases) via `obsidian-cli properties` / `obsidian-cli search` against `path="Decisions"`. Only fall back to a broader content search if the frontmatter probe returns zero hits.
4. **Cheap by default.** Stage 1 returns ≤10 hits; Stage 2 loads top 1–3. Don't load 10 files.
5. **`obsidian-cli` only.** All vault interaction goes through `obsidian-cli` (Bash). Do NOT use `mcp__obsidian-mcp__*` tools, and do NOT shell out to `find`, `grep`, `cat`, or `ls` against `~/Loose Ends/`.
6. **Treat returned decisions as ground truth.** Don't re-derive current state from older artifacts (READMEs, ADRs, code comments) once a decision exists. The supersession walk is canonical.
7. **Parse the argument first.** `$ARGUMENTS` may be an atom-id (`0011`), a slug (`#monorepo-shape`), an `area/topic` pair, or free-text topic terms. Dispatch to the matching resolution path in Stage 0 before running Stage 1.

## Inputs

- `$ARGUMENTS` — one of four forms (see Stage 0 for full parsing):
  - **atom-id** — `0011` (4 digits, optionally with leading `ndr:`)
  - **slug** — `#monorepo-shape` (leading `#`, slug content)
  - **topic** — `area/topic` (exactly one `/`, e.g. `architecture/repo-shape`)
  - **free-text** — anything else, used as topic search terms
  - If empty, prompt: "What ref or topic? (e.g., `0011`, `#monorepo-shape`, `architecture/repo-shape`, `auth substrate`)".

Strip a leading `ndr:` prefix before parsing — `ndr:0011`, `ndr:#monorepo-shape`, and `ndr:architecture/repo-shape` are all valid argument shapes.

## Method

### Stage 0 — Parse the argument

Strip a leading `ndr:` prefix if present, then dispatch:

**1. Atom-id** — `$ARGUMENTS` matches `^\d{4}$`.

- Resolve directly: enumerate `Decisions/` via `obsidian-cli files folder="Decisions" ext="md"`, find the entry matching `Decisions/<id>-*.md`.
- Load it with `obsidian-cli read path="Decisions/<id>-<slug>.md"`.
- Skip Stage 1 and Stage 2 entirely. Jump to Stage 3 (walk supersession to head).
- If no file matches, return: `No atom with id "<id>".`

**2. Slug** — `$ARGUMENTS` starts with `#`.

- Strip the `#`. The remainder is the slug (typically `ndr-<kebab>`).
- Search for atoms holding the slug:
  ```
  obsidian-cli search query="<slug>" path="Decisions" limit=10 format=json
  ```
- For each hit, confirm by reading the `aliases:` frontmatter field — `obsidian-cli property:read name="aliases" path="<hit-path>"` — and keep only those whose list contains the slug exactly.
- If exactly one hit: load it via `obsidian-cli read path="<hit-path>"` and jump to Stage 3.
- If zero hits: return `No atom holds slug "<slug>".`
- If multiple hits: this is a uniqueness violation. Print:
  ```
  Slug "<slug>" is held by multiple atoms — this should not happen. Manual resolution needed:
    - Decisions/<id-a>-<slug>
    - Decisions/<id-b>-<slug>
  ```
  Stop. Do not walk supersession.

**3. Topic** — `$ARGUMENTS` matches `^[^/]+/[^/]+$` (exactly one `/`, no whitespace around it).

- Split into `<area>` and `<topic>`.
- Run Stage 1 with `<topic>` as the search query.
- In Stage 2, additionally filter loaded hits to those with `area: <area>` AND `topic: <topic>` in frontmatter.
- Return all `status: current` heads (multiple results expected — the area/topic pair may cover several atoms). Each gets its own brief in Stage 4, separated by `---`.

**4. Free-text fallback** — anything else.

- Existing behavior: pass `$ARGUMENTS` as topic terms to Stage 1.

### Stage 1 — Frontmatter probe

`obsidian-cli search` matches against file content, which includes the YAML frontmatter at the top of each atom. Constrain the search to `Decisions/` and use focused query terms (area, topic, title fragments) so frontmatter fields dominate the match ranking:

```
obsidian-cli search query="$ARGUMENTS" path="Decisions" limit=10 format=json
```

After the call, post-filter hits by reading frontmatter on the most promising paths via `obsidian-cli property:read` (e.g. `name="area"`, `name="topic"`, `name="title"`) and rank those whose frontmatter values actually match `$ARGUMENTS` ahead of pure body-text matches.

**If 0 hits**: retry once with `obsidian-cli search:context query="$ARGUMENTS" path="Decisions" limit=10 format=json` (broader content match with surrounding lines).

**If still 0**: return:

```
No decisions matched "<topic>".
(Searched frontmatter then content under Decisions/.)
```

Do not fabricate.

### Stage 2 — Load top matches

Rank hits by:

1. Path starts with `Decisions/`.
2. Frontmatter field match (title, area, topic, tags).
3. Recency (`decision_date`).

Pick the top 1–3. Call `obsidian-cli read path="<path>"` once per pick (the CLI has no batch read; loop the calls).

### Stage 3 — Walk supersession to head (load-bearing)

For each loaded decision D:

1. Parse `D.superseded_by`.
2. If empty, D is a head. Record it.
3. If non-empty, follow each link to its target. Re-read via `obsidian-cli read path="Decisions/<target-id>-<target-slug>.md"`. Recurse to a head.
4. Detect cycles: if a chain revisits a previously-seen ID, print:
   ```
   Cycle detected: <id-a> → <id-b> → <id-a>. Manual resolution needed.
   ```
   and stop walking that chain.

Deduplicate heads (multiple search hits in one chain converge to one head).

### Stage 4 — Synthesize a brief

Output shape:

```
**Current state on "<topic>":**

<head-title> (Decisions/<id>-<slug>)
  area: <area>, topic: <topic>, decision: <decision_date>
  reversibility: <reversibility>

<one-paragraph summary of the Decision section>

Lineage: <id_a> → <id_b> → ... → <head_id>
```

If the head's body has a `## Assumptions` section, parse each `> [!warning]- <slug>` callout (description paragraph + `**Current state:**` and `**Revisit if:**` bullets). Surface any whose `Revisit if:` condition is plausibly tripped by the current conversation context:

```
⚠ Assumption to revisit: <slug> — <description>
  Revisit if: <revisit-if condition>
  Current state: <current-state>
```

Older atoms may use a different shape (`### <slug>` heading instead of a callout, or an `assumptions:` YAML list). Treat all forms as valid input — parse what's there.

If multiple heads (the topic spans more than one decision lineage), present each as its own block, separated by `---`.

## Output examples

### Single head

```
**Current state on "substrate":**

Substrate = markdown in ~/Loose Ends/Decisions/ for MVP (Decisions/0007-mvp-substrate-markdown)
  area: substrate, topic: substrate, decision: 2026-05-14
  reversibility: medium

Atomic decisions live in `~/Loose Ends/Decisions/` as YAML-front-matter markdown.
Capture via a Claude Code skill; retrieval via `obsidian-cli search` (frontmatter-first)
and Obsidian Bases for faceted browse. Graphiti preserved as fallback for team scale.

Lineage: 0005 → 0007
```

### No hits

```
No decisions matched "load balancer".
(Searched frontmatter then content under Decisions/.)
```

### Atom-id resolution

```
**Atom 0011:**

Monorepo with symmetric apps layout (Decisions/0011-monorepo-symmetric-apps-layout)
  area: architecture, topic: repo-shape, decision: 2026-05-09
  reversibility: hard
  status: superseded → 0099-split-apps-into-services

<one-paragraph summary>

Lineage: 0011 → 0099 (head)
```

### Slug resolution

```
**Slug "#monorepo-shape" resolves to:**

Split apps into services (Decisions/0099-split-apps-into-services)
  area: architecture, topic: repo-shape, decision: 2026-07-12
  reversibility: hard

<one-paragraph summary>

Lineage: 0011 → 0099 (head, holds the slug)
```

### Topic resolution (multiple heads)

```
**Current decisions on area/topic "architecture/repo-shape":**

Decisions/0011-monorepo-symmetric-apps-layout — area: architecture, topic: repo-shape
<gist>

---

Decisions/0013-python-packaging-in-monorepo — area: architecture, topic: repo-shape
<gist>

(2 current atoms in this area/topic)
```

## When NOT to use this skill

- The user wants to **make** a decision — direct them to discuss first; suggest `/capture-decision` at the end.
- The user wants to read a single decision they already know the ID of — they can open it directly.
- The user wants a list of all decisions — use the "Current Decisions" Obsidian Base instead.

## Related

- `/capture-decision` — the write-side companion. Always check current state on a topic before capturing a new decision on it (avoid accidental parallel decisions).
- `${CLAUDE_PLUGIN_ROOT}/references/workflow.md` — full retrieval flow + diagram.
- `${CLAUDE_PLUGIN_ROOT}/references/frontmatter-schema.md` — what fields the brief draws from.
