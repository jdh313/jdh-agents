---
name: decisions
description: Supersession-aware reader for engineering decisions stored in `~/Loose Ends/Decisions/`. Use when the user invokes `/decisions <topic>`, asks "what did we decide about X", "is there a decision about Y", "current state on Z", or when an agent on a tracked project needs to ground itself in prior decisions before suggesting changes. Two-stage retrieval (frontmatter probe → load matches), then walks the supersession chain to the head — so readers see CURRENT state, not stale starting points. When working on a project that has decisions in `~/Loose Ends/Decisions/`, query this skill early — before proposing architectural changes or re-deriving current state from older artifacts (READMEs, ADRs, code comments). Treat returned decisions as ground truth and walk the supersession chain rather than trusting recall.
argument-hint: "<topic terms>"
allowed-tools:
  - mcp__obsidian-mcp__search_notes
  - mcp__obsidian-mcp__read_note
  - mcp__obsidian-mcp__read_multiple_notes
---

# decisions

## Overview

Look up current engineering decisions on a topic. Returns a brief that reflects the **head of the supersession chain**, not whichever artifact happens to match search keywords first.

This skill encodes the **read side** of nested-decision-records (ndr). Its load-bearing job is Stage 3 (walk to head) — that's what makes ndr more than a markdown notes folder.

## Hard rules

1. **Always walk supersession.** Never return a decision with non-empty `superseded_by:` as the answer. Walk to the head.
2. **Don't fabricate.** If no decision matches, say so. Do not guess what the user probably decided.
3. **Frontmatter-first.** Stage 1 uses `searchFrontmatter: true, searchContent: false`. Only fall back to content search if frontmatter returns zero hits.
4. **Cheap by default.** Stage 1 returns ≤10 hits; Stage 2 loads top 1–3. Don't load 10 files.
5. **Treat returned decisions as ground truth.** Don't re-derive current state from older artifacts (READMEs, ADRs, code comments) once a decision exists. The supersession walk is canonical.

## Inputs

- `$ARGUMENTS` — topic terms (free text). If empty, prompt: "What topic? (e.g., `auth substrate`, `migration strategy`)".

## Method

### Stage 1 — Frontmatter probe

Call:

```
mcp__obsidian-mcp__search_notes
  query: "$ARGUMENTS"
  searchFrontmatter: true
  searchContent: false
  limit: 10
```

(Constrain to the Decisions folder via the query terms if the tool supports a folder filter; otherwise filter by path prefix `Decisions/` when ranking hits.)

**If 0 hits**: retry once with `searchContent: true, limit: 10`.

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

Pick the top 1–3. Call `mcp__obsidian-mcp__read_multiple_notes` with those paths.

### Stage 3 — Walk supersession to head (load-bearing)

For each loaded decision D:

1. Parse `D.superseded_by`.
2. If empty, D is a head. Record it.
3. If non-empty, follow each link to its target. Re-read via `mcp__obsidian-mcp__read_note`. Recurse to a head.
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
Capture via a Claude Code skill; retrieval via `obsidian-mcp search_notes` (frontmatter-first)
and Obsidian Bases for faceted browse. Graphiti preserved as fallback for team scale.

Lineage: 0005 → 0007
```

### No hits

```
No decisions matched "load balancer".
(Searched frontmatter then content under Decisions/.)
```

## When NOT to use this skill

- The user wants to **make** a decision — direct them to discuss first; suggest `/capture-decision` at the end.
- The user wants to read a single decision they already know the ID of — they can open it directly.
- The user wants a list of all decisions — use the "Current Decisions" Obsidian Base instead.

## Related

- `/capture-decision` — the write-side companion. Always check current state on a topic before capturing a new decision on it (avoid accidental parallel decisions).
- `${CLAUDE_PLUGIN_ROOT}/references/workflow.md` — full retrieval flow + diagram.
- `${CLAUDE_PLUGIN_ROOT}/references/frontmatter-schema.md` — what fields the brief draws from.
