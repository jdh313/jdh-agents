---
name: ground
description: >
  Ground a coding session in relevant prior decisions before substantive
  edits. **This is the default first move on any substantive code task
  in a tracked NDR project** (refactor, new feature, migration, schema
  change, dependency swap) — invoke it before reaching for grep / Read
  / Linear context. Also use when delegating code work to a coding
  subagent (junior-dev / senior-dev / tech-lead) so the delegation
  prompt can include the live decision heads, or when the user says
  "what decisions touch this", "ground me in the NDRs", "what governs
  this area", "are there decisions about X in this repo". **Use even
  when ticket bodies or prior chat name specific atom IDs** — named
  atoms may be superseded; `Read`ing them directly bypasses the
  supersession walk and is the single biggest failure mode of this
  plugin. Dispatches the read work to `@ndr-reader` and returns a
  compact brief plus the `ndr:` reference strings the caller can paste
  into prompts, code comments, or commit messages.
argument-hint: "[scope-or-question]"
allowed-tools:
  - Read
  - Bash(pwd)
  - Bash(git rev-parse *)
  - Bash(obsidian-cli properties *)
  - Bash(obsidian-cli files *)
---

# ground

## Overview

Surface the current decisions that govern an active piece of code work,
so the orchestrator can either consult them directly or fold them into a
delegation prompt for a coding subagent. The skill detects scope, hands
the read work to `@ndr-reader`, and presents the brief.

This is the read-side companion most useful **before** code is written:
`/decisions` answers "what did we decide about X?" when the user asks;
`/ground` answers "what should this coding agent know before it starts?"
without waiting for an explicit question.

## When to activate

1. **Starting substantive work on a tracked project** — repo with NDR
   coverage; before edits beyond trivial fixes.
2. **Before delegating to junior-dev / senior-dev / tech-lead** — so the
   delegation prompt carries the live heads, not stale recollection.
3. **The user asks for grounding** — "what decisions touch this",
   "ground me in the NDRs for this area", "are there decisions about X".
4. **A file path or area is about to change** — refactor, migration,
   schema change, dependency swap.

**Do NOT activate** for:

- Single-line fixes or typo corrections.
- Questions about the meaning of one specific atom the user already
  named (use `/decisions ndr:NNNN` instead).
- Projects with no NDR coverage — return a one-line "no decisions on
  this project" and stop.

## Inputs

- `$ARGUMENTS` — free-form. May be:
  - empty → infer scope from CWD + a one-line summary of the active task
  - a file path → `src/auth/middleware.py`
  - an area phrase → `auth`, `migrations`, `repo shape`
  - a full question → `what governs the auth substrate in this repo?`

If empty and the active task is unclear from conversation context, ask
the user one tight question — "Grounding for what area? (file path, area
name, or short phrase)" — and proceed.

## Workflow

### 1. Detect the active scope

Build a scope payload from whatever signals are available:

- `cwd` — `pwd` (or `git rev-parse --show-toplevel` when inside a repo).
- `project` — best-guess wikilink from the repo name. Confirm by
  probing the taxonomy / project pages via
  `obsidian-cli properties path="Decisions/..."` if uncertain; otherwise
  leave `project` unset and let `@ndr-reader` search broadly.
- `file path` / `area words` — from `$ARGUMENTS` or from recent context
  (files just edited, files the user named).
- `ref` — if `$ARGUMENTS` matches an `ndr:` reference, pass it through
  unchanged.

Keep this lightweight. Do not load atoms here — that is the agent's job.

### 2. Dispatch to `@ndr-reader`

Invoke `@ndr-reader` with the canonical payload:

```markdown
## Intent
ground the active coding session in current decisions for <scope summary>

## Constraints
- scope: <project-wikilink or "unspecified">
- cwd: <repo root>
- file path: <path-or-unset>
- area: <area-word-or-unset>
- topic: <topic-word-or-unset>
- ref: <ndr:... or unset>

## Input
<the user's free-text scope, or a one-line summary of what the orchestrator
 is about to do>

## Output shape
brief
```

If the caller already has a specific `ndr:` reference, pass `ref:` and
let the agent skip Stage 1.

### 3. Present the brief (non-interrupting)

If `## Result` is one or more head briefs:

- **Inline (1–2 heads):** show the brief verbatim from the agent payload,
  prefixed with `**NDR grounding:**`.
- **Batch (3+ heads):** present as a compact table of titles + atom-ids
  + `ndr:` slug refs, with a one-line invitation: "Pull any of these
  into the working context? (1-N, all, skip)".
- **Assumption warnings** (`⚠ Assumption to revisit: ...`) — always
  surface; these are the load-bearing signal that prior reasoning may
  be tripping.

If `## Result` is "No decisions matched ...":

- Surface a single line: `No NDR coverage for <scope>. Proceeding
  without grounding.` Do not nag.

### 4. Optionally hand off

If the orchestrator is about to dispatch a coding subagent (`junior-dev`,
`senior-dev`, `tech-lead`), append the `ndr:` reference strings from the
brief to the delegation prompt so the subagent has stable identifiers it
can include in code comments or commit messages without having to query
the vault itself.

## Output examples

### Single relevant head

```markdown
**NDR grounding** (`auth` in `[[Apex]]`):

Auth substrate = Okta + custom session middleware (Decisions/0042-okta-session-substrate)
  area: auth, topic: substrate, decision: 2026-04-18
  reversibility: hard

Okta handles identity; a thin session middleware translates Okta tokens
to internal session cookies. PostgreSQL-backed session store; no third
session-mgmt library.

Lineage: 0030 → 0042

References:
  - ndr:0042
  - ndr:#auth-substrate
  - ndr:auth/substrate

⚠ Assumption to revisit: shared-okta-tenant — assumes the Carta-wide
  Okta tenant covers this product surface.
  Revisit if: this product surface moves to a non-Carta tenant.
  Current state: still on the shared tenant.
```

### Multiple heads (batch)

```markdown
**NDR grounding** (`repo shape`):

| Atom | Title | Slug |
|---|---|---|
| 0011 | Monorepo, symmetric apps layout | ndr:#monorepo-shape |
| 0013 | Python packaging in monorepo | ndr:0013 |
| 0021 | Per-app CI builders, shared cache | ndr:#ci-strategy |

Pull any of these into the working context? (1-N, all, skip)
```

### No coverage

```markdown
No NDR coverage for `marketing-site` repo. Proceeding without grounding.
```

## Hard rules

1. **Always dispatch to `@ndr-reader`.** Don't query `obsidian-cli` for
   atom bodies directly in this skill — the agent owns the supersession
   walk and the synthesis. The skill only handles scope detection and
   presentation. **Specifically: never `Read` an atom file directly
   from `~/Loose Ends/Decisions/` as a shortcut, even when a ticket
   body or prior chat names specific atom IDs.** Named atoms may be
   superseded; reading them directly returns the seed, not the head.
2. **Don't surface superseded atoms.** If the agent ever returns one,
   that is a bug in the agent, not something to paper over here.
3. **Stay quiet on empty.** No-coverage scenarios get one line. Don't
   nag, don't re-prompt for a different scope unless the user asks.
4. **Don't capture or write.** Grounding is read-only. If the user wants
   to record a new decision, redirect to `/capture-decision`.

## When NOT to use this skill

- The user already named a specific atom (`ndr:0011`, `0042`) — they
  want `/decisions` with a ref argument, not active-context grounding.
- The user is asking a topic-shaped question ("what did we decide about
  X?") — `/decisions` is the right surface.
- The repo has no NDR coverage and the user knows it.
- The work is too small to need grounding (typo fix, comment update).

## Related

- `@ndr-reader` — the worker this skill dispatches to.
- `/decisions <ref-or-topic>` — user-facing slash command for explicit
  queries with a topic or ref in hand.
- `/capture-decision` — the write-side companion. Ground first, then
  capture if the conversation produces a new decision.
- `${CLAUDE_PLUGIN_ROOT}/references/workflow.md` — full retrieval flow.
