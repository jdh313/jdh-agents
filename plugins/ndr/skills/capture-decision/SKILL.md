---
name: capture-decision
description: Capture engineering decisions from the current conversation as atomic markdown artifacts in `~/Loose Ends/Decisions/`. Use when the user invokes `/capture-decision`, says "capture this decision", "record this", "let's write this up as a decision", or signals at end of a chat that decisions landed and should be persisted. Materializes one file per atomic decision with required frontmatter, enforces taxonomy, and structurally protects the supersession primitive (refuses to write a revising decision without `supersedes:`).
argument-hint: "[optional hint about what to capture]"
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Agent
  - mcp__obsidian-mcp__read_note
  - mcp__obsidian-mcp__read_multiple_notes
  - mcp__obsidian-mcp__list_directory
  - mcp__obsidian-mcp__search_notes
---

# capture-decision

## Overview

Thin orchestrator for the NDR capture pipeline. The work itself is delegated:

```
in-skill scan ──► user confirms candidates ──► ndr-drafter ──► ndr-reviewer ──► persist.py ──► summary
```

This skill detects atomic decisions in the current conversation, confirms them with the user, delegates composition to the `ndr-drafter` subagent, sends drafts to `ndr-reviewer` for a verdict, then hands off to `scripts/persist.py` for the deterministic write. Each stage has a single responsibility; the skill itself owns scope detection and user interaction.

## Hard rules

These constraints are upstream of any subagent — the skill enforces them at the orchestration layer.

1. **Atomic only.** One chosen path, one set of consequences. Bundled candidates get split before reaching the drafter. Never let a bundle through.
2. **Supersession refusal is structural, not advisory.** If revising intent appears in the conversation ("revises", "supersedes", "instead of", "we changed our mind on") OR `informed_by:` points at a `current` decision being contradicted, AND the user has not named what's being superseded — refuse to proceed. Print:
   > "This looks like a revising decision but `supersedes:` is empty. Name the decision(s) being revised, or confirm this is a fresh decision."
3. **Review-then-persist.** No draft hits disk until the reviewer passes and the user accepts. There is no `draft` status. Drafts live in memory.
4. **Taxonomy enforcement.** `area:` and `topic:` must come from `~/Loose Ends/Decisions/.taxonomy/{areas,topics}.yaml`. Unknown values trigger "use existing or add new?" before drafting. `persist.py` re-checks; the orchestrator's check is the friendly-prompt layer.
5. **Single-file atoms.** `<id>-<kebab-title>.md`. No directory form, no descent files. Length is managed by hybrid altitude callouts inside the file.
6. **Lazy slug minting.** Default `aliases: []`. Only mint a slug when the user signals atom-grain external referenceability is needed. `ndr-` namespace prefix. Most atoms never carry a slug.
7. **Slug uniqueness.** Before minting, search the vault. `persist.py` re-checks before write.

## Inputs

- `$ARGUMENTS` — optional free-text hint about what to capture. If absent, scan the whole conversation.

## Reference paths

- **Vault decisions:** `~/Loose Ends/Decisions/` (one atom per file, `<id>-<kebab-title>.md`).
- **Taxonomy (vault-resident, mutable):** `~/Loose Ends/Decisions/.taxonomy/{areas,topics}.yaml`.
- **Schema spec:** `${CLAUDE_PLUGIN_ROOT}/references/frontmatter-schema.md`.
- **Template:** `${CLAUDE_PLUGIN_ROOT}/references/decision-single.md`.
- **Persistence helper:** `${CLAUDE_PLUGIN_ROOT}/scripts/persist.py`.
- **Subagents:** `ndr-drafter`, `ndr-reviewer` (and `ndr-extractor` for long-source captures, `ndr-curator` for periodic audits — both out of scope for the routine capture flow).

## Method

### Step 1 — Scan

Scan the current conversation for atomic decisions. The context is already loaded — no subagent needed here. Atomic = one chosen path with one set of consequences. Common shapes:

- "Use X for Y" (one tool, one purpose)
- "Don't do X" (a rejected path)
- "X over Y because Z" (a chosen path with a named alternative)

Split bundles. "We'll use FastAPI and Postgres" is two atoms. "Use FastAPI because it's async and we already have Postgres" is one atom (Postgres is context).

Discard non-decisions: open questions, observations, tasks, hypotheticals.

**If the source is too long to scan inline** (e.g. the user pastes a full transcript or asks you to capture from a file), invoke the `ndr-extractor` subagent with the source. It returns structured candidates. For routine in-conversation captures, scan inline.

### Step 2 — Detect supersession intent

Before confirming candidates, scan the conversation for revising intent:

- Phrases: "revises", "supersedes", "instead of", "we changed our mind on", "switching from X to Y".
- Substantive: a candidate directly contradicts a decision named in `informed_by:` context, or named in chat by id/slug.

For each candidate with revising signal, you'll need to ask the user: **what is being superseded?** Note this against the candidate; ask in Step 3.

### Step 3 — Confirm candidates

Present each candidate as a one-line summary. For candidates with revising signal, append the question:

```
I see N atomic decisions in this conversation:

  1. Use FastAPI for the auth service
  2. Single Postgres instance, no read replicas at MVP
  3. Switch from JWT to PASETO  ← revises a prior decision; which one? (id, slug, or wikilink)

Confirm, edit titles, drop any, or answer the revising question.
```

Wait for the user's response. Capture for each confirmed candidate:

- Title (user can edit)
- `supersedes:` list (wikilinks like `[[Decisions/0042-...]]`) — required when revising signal triggered; defaults to `[]`.
- Whether to mint a slug (default no).

If revising signal triggered and the user neither named a predecessor nor confirmed "this is fresh", refuse. Print the rule-2 message and stop.

### Step 4 — Taxonomy preflight (optional but friendly)

For each candidate, suggest an `area:` and `topic:` based on the conversation. Read `~/Loose Ends/Decisions/.taxonomy/{areas,topics}.yaml` once and cache. If a suggested value is not in the taxonomy:

```
"<value>" is not in <areas.yaml | topics.yaml>.
Use existing: <comma-separated list>
Or add new: <value>?
```

If "add new", `Edit` the relevant YAML file to append the value before drafting. `persist.py` will re-validate — this preflight is friendly UX, not the structural gate.

### Step 5 — Delegate composition

Invoke the `ndr-drafter` subagent. Pass:

```json
{
  "candidates": [
    {
      "title": "Use FastAPI for the auth service",
      "gist": "...",
      "quotes": ["..."],
      "suggested_area": "tooling",
      "suggested_topic": "substrate",
      "suggested_project": "[[Auth Rewrite]]",
      "supersedes": [],
      "derived_from": ["[[<chat / mull source>]]"],
      "informed_by": [],
      "decision_date": "<ISO today>",
      "project": "[[Auth Rewrite]]",
      "mint_slug": false,
      "slug": null
    }
  ]
}
```

The drafter returns `{drafts: [{frontmatter, body, missing_fields}]}`. If any `missing_fields` are non-empty: prompt the user, fill in the values, and re-invoke the drafter with the filled candidate. Repeat until all drafts come back with `missing_fields: []`.

### Step 6 — Review

Invoke `ndr-reviewer` with `{mode: "pre-persist", drafts: [...]}`. The reviewer returns either:

- `{verdict: "pass", issues: []}` — proceed to Step 7.
- `{verdict: "fail", issues: [...]}` — surface issues to the user. For `severity: load-bearing` (atomicity, body altitude), the user must decide whether to edit the candidate(s) and re-draft, or proceed despite the warning (rare — prefer fixing). For `severity: mechanical`, you may auto-fix (e.g. set missing field) and re-invoke the reviewer.

Do not call `persist.py` until the reviewer passes (or the user explicitly overrides a load-bearing flag).

### Step 7 — Persist

Pass the drafts to `persist.py` as JSON on stdin:

```bash
echo "$DRAFTS_JSON" | uv run --with pyyaml "${CLAUDE_PLUGIN_ROOT}/scripts/persist.py"
```

`persist.py` returns a JSON summary on stdout. Exit codes:

- `0` — success. Parse `written`, `superseded`, `aliases_moved` for the summary.
- `1` — validation failure (taxonomy, required fields, malformed input). Surface the errors and loop back to drafting.
- `2` — supersession conflict (predecessor already superseded by a different atom). Surface and stop — manual resolution.
- `3` — mid-transaction failure (half-state). Surface the full `errors[*].half_state` so the user knows exactly what to repair by hand.

### Step 8 — Summarize

Report what was written, what was patched, and any alias handovers. One line per file. See Output examples below.

## When to use the extractor subagent

The default flow scans the conversation inline (Step 1). Invoke `ndr-extractor` instead when:

- The user pastes a long transcript, doc, or PR thread.
- The user asks to capture decisions from a file path or wikilink.
- The conversation has accumulated so much context that an inline scan would be unreliable.

The extractor returns the same `{candidates: [...]}` structure that Step 3 expects.

## Output examples

### Fresh decision

```
Captured 1 decision:

  Decisions/0009-use-fastapi-for-auth.md
    area: tooling, topic: substrate
    supersedes: [] (fresh decision)
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

### Refused (supersession-blind)

```
Refused: "Switch to Litestar for auth" looks like a revising decision
(intent words: "switch to", "instead of FastAPI"),
but `supersedes:` is empty.

Name the decision being revised, or confirm this is fresh.
```

### Half-state (exit 3 from persist.py)

```
HALF-STATE during supersession:

  Successor written: Decisions/0099-split-apps-into-services.md
  Aliases moved: [ndr-monorepo-shape]
  Patch failed on: [[Decisions/0011-monorepo-symmetric-apps-layout]]
  Reason: file not found

Manual fix: edit Decisions/0011-..., set status: superseded,
append "[[Decisions/0099-split-apps-into-services]]" to superseded_by,
clear aliases: [].
```

## When NOT to use this skill

- The user is **considering** a decision, not making one. (Capture afterward.)
- The user wants a quick journal entry — use `/note-capture` (daily-note append).
- The user wants to revise a decision's *body* without changing its substance — edit the file directly; don't write a new atom.

## Related

- `/decisions <topic>` — the read-side companion. Use it BEFORE capture to check whether a current decision on the topic already exists (avoid accidental parallel decisions).
- `ndr-extractor` — long-source candidate extraction.
- `ndr-drafter` — frontmatter + body composition.
- `ndr-reviewer` — pre-persist judge (atomicity, body altitude, soft mechanical checks).
- `ndr-curator` — corpus-level health audit (run periodically, not per-capture).
- `${CLAUDE_PLUGIN_ROOT}/references/frontmatter-schema.md` — full schema spec.
- `${CLAUDE_PLUGIN_ROOT}/references/taxonomy.md` — taxonomy rules and growth protocol.
- `${CLAUDE_PLUGIN_ROOT}/references/workflow.md` — capture + read end-to-end.
- `${CLAUDE_PLUGIN_ROOT}/scripts/persist.py` — the deterministic write helper.
