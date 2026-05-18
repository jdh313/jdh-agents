---
name: decisions
description: Supersession-aware reader for engineering decisions stored in `~/Loose Ends/Decisions/`. Use when the user invokes `/decisions <topic>`, asks "what did we decide about X", "is there a decision about Y", "current state on Z", or supplies an `ndr:` reference and wants the resolved atom. **Use even when you already know specific atom IDs** (e.g. ticket bodies, prior chat) — named atoms may be superseded and the supersession walk to the head is the whole point. **Never `Read` an atom file directly from `~/Loose Ends/Decisions/` as a shortcut; route through this skill or `@ndr-reader`.** Parses the argument (atom-id, slug, area/topic, or free-text), then dispatches `@ndr-reader` to do the obsidian-cli work and the supersession walk in isolated context. Returns a brief that reflects the **head** of the supersession chain — never a stale starting point. For active-work grounding (before code edits, before delegating to a coding subagent) use `/ground` instead.
argument-hint: "<ref-or-topic>"
allowed-tools:
  - Bash(obsidian-cli files *)
  - Read
---

# decisions

## Overview

Look up current engineering decisions when the user (or another agent)
already knows the topic, area, or `ndr:` reference. Parses the argument
into a structured constraint, hands the read work to `@ndr-reader`, and
presents the brief.

This skill is the **user-driven** read entry point. For active-work
grounding (skill detects scope, surfaces relevant atoms before code
edits) use `/ground`.

## Hard rules

1. **Always dispatch to `@ndr-reader`.** The agent owns the supersession
   walk and synthesis. This skill does argument parsing and presentation
   only. **Specifically: never `Read` an atom file directly from
   `~/Loose Ends/Decisions/` as a shortcut, even when the user names a
   specific atom ID.** A named atom may be superseded; reading it
   directly returns the seed, not the head. The supersession walk is
   the whole point of this skill — bypassing it defeats the primitive.
2. **Don't fabricate.** If the agent returns "no decisions matched",
   say so. Do not guess what the user probably decided.
3. **Parse the argument first.** `$ARGUMENTS` may be an atom-id (`0011`),
   a slug (`#monorepo-shape`), an `area/topic` pair, or free-text topic
   terms. Convert to the agent's `ref:` / `area:`+`topic:` / Input
   constraint shape before dispatching.
4. **Treat returned decisions as ground truth.** Don't re-derive current
   state from older artifacts (READMEs, ADRs, code comments) once the
   agent has returned a head.

## Inputs

- `$ARGUMENTS` — one of four forms:
  - **atom-id** — `0011` (4 digits, optionally with leading `ndr:`)
  - **slug** — `#monorepo-shape` (leading `#`, slug content)
  - **topic** — `area/topic` (exactly one `/`, e.g. `architecture/repo-shape`)
  - **free-text** — anything else, used as topic search terms
  - If empty, prompt: "What ref or topic? (e.g., `0011`, `#monorepo-shape`, `architecture/repo-shape`, `auth substrate`)".

Strip a leading `ndr:` prefix before parsing — `ndr:0011`,
`ndr:#monorepo-shape`, and `ndr:architecture/repo-shape` are all valid.

## Method

### Stage 0 — Parse the argument

Strip a leading `ndr:` if present, then categorize:

| Pattern | Form | Agent payload |
| --- | --- | --- |
| `^\d{4}$` | atom-id | `ref: ndr:<id>` |
| starts with `#` | slug | `ref: ndr:#<slug>` |
| exactly one `/`, no whitespace | area/topic | `area: <area>`, `topic: <topic>` |
| anything else | free-text | Input: `<terms>` |

For atom-id specifically, you can pre-resolve the file path with
`obsidian-cli files folder="Decisions" ext="md"` and pass it to the
agent — but this is optional. The agent does the same lookup if you
pass only `ref: ndr:<id>`.

### Stage 1 — Dispatch to `@ndr-reader`

Invoke `@ndr-reader` with the canonical payload:

```markdown
## Intent
resolve a user-supplied decision reference / topic and return a current-head brief

## Constraints
- ref: <ndr:... if Stage 0 produced one, else unset>
- area: <area if topic form, else unset>
- topic: <topic if topic form, else unset>

## Input
<the original $ARGUMENTS verbatim — gives the agent free-text fallback
 context if Stage 0 matched none of the structured forms>

## Output shape
brief
```

### Stage 2 — Present the agent's result

The agent returns the canonical `## Result / ## Sources / ## Notes`
payload. Surface the result block verbatim to the user (it is already
formatted as a brief — see "Brief shape" in `agents/ndr-reader.md`).

If the agent reports a uniqueness violation (slug held by multiple atoms)
or a cycle in the supersession chain, surface the agent's report
unchanged and stop. Don't paper over corpus problems.

If the agent's `## Result` is "No decisions matched ...", present that
line and offer:

```
No decisions on "<topic>". Options:
  - broaden the search ("<broader terms>")
  - check a specific atom by id ("/decisions 0011")
  - capture one now if a decision should exist ("/capture-decision")
```

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

### No hits

```
No decisions matched "load balancer".
(Searched frontmatter then content under Decisions/.)
```

## When NOT to use this skill

- The user wants to **make** a decision — direct them to discuss first;
  suggest `/capture-decision` at the end.
- The orchestrator wants to **ground a coding subagent** for active work
  — use `/ground` instead. It detects scope and presents the brief in a
  form designed to fold into delegation prompts.
- The user wants a list of all decisions — use the "Current Decisions"
  Obsidian Base.

## Related

- `@ndr-reader` — the worker this skill dispatches to.
- `/ground [scope]` — active-work-grounding companion; detects scope from
  cwd / file path / area phrase rather than requiring a topic in hand.
- `/capture-decision` — the write-side companion. Always check current
  state on a topic before capturing a new decision on it (avoid
  accidental parallel decisions).
- `${CLAUDE_PLUGIN_ROOT}/references/workflow.md` — full retrieval flow.
- `${CLAUDE_PLUGIN_ROOT}/references/frontmatter-schema.md` — what fields
  the brief draws from.
