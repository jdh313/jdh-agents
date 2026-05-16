---
name: experiment-review
description: Review an experiment — pulse-check mid-run, or record the verdict at/after review_date. Reads the experiment page plus all daily-note check-ins, summarizes observations, probes for missing context, and (if review_date has arrived) guides the adopt/modify/drop/inconclusive verdict. Use when the user says "how is X going", "review the X experiment", "time to review", "verdict on", "what did I learn from", or when an experiment's review_date has arrived.
---

# Experiment Review

Read an experiment plus all its daily-note check-ins, summarize what's
happened, probe gaps, and (if at/after `review_date`) guide the verdict.
Schema lives in `~/dotfiles/claude/rules/11-knowledge-wiki.md` →
**Experiments**.

## Required skills
- **Skill(obsidian:obsidian-cli)** — for reading/updating notes and frontmatter
- **Skill(obsidian:obsidian-markdown)** — for Obsidian-flavored markdown

## When to use

- User asks about the state of a running experiment
- An experiment's `review_date` has been reached or passed
- User wants to record a verdict
- User mentions they want to adopt/drop/modify something they've been testing

## Workflow

### 1. Identify the experiment

If unambiguous from context, pick it. Otherwise, list active experiments
(`status: running` or `reviewing`) from `Experiments/` via obsidian-cli
and ask the user to pick one.

### 2. Read the page and all check-ins

- Read the experiment page (hypothesis, success criteria, protocol, dates).
- Find daily-note mentions: search `Daily Notes/` for wikilinks to the
  experiment (obsidian-cli backlinks or grep by wikilink text).
- For each mention, read the surrounding list context — the check-in line
  plus sibling bullets that give the entry meaning.

### 3. Build a timeline summary

A condensed, dated timeline of observations — not a raw dump. Group by
theme where useful (e.g., "energy observations", "friction points",
"adjustments made"). Front-load what changed; strip filler.

### 4. Detect gaps

Before asking the user anything, scan for:

- **Uncovered success criteria** — any criterion from the page with no
  observation in check-ins
- **Silent stretches** — no check-ins for >N days (default N=4 for running
  experiments; adjust for experiment cadence)
- **Protocol drift** — check-ins describe behavior that diverges from the
  stated protocol
- **Conflicting signals** — early check-ins positive, later negative (or
  vice versa) without a stated cause
- **Missing verdict context** — if `review_date` has arrived, is there
  enough in check-ins to decide? If not, name what's missing.

### 5. Ask targeted follow-ups

One question at a time. Only ask about *real* gaps from step 4, not a
checklist. The goal is to surface what didn't get logged. Examples:

- "Success criterion was 'fewer afternoon energy crashes' — check-ins
  don't mention afternoon energy. Did you notice a change?"
- "Protocol called for 90-minute blocks; most check-ins mention
  60-minute ones. Did you adjust, or is the protocol outdated?"
- "No check-ins for 9 days in the middle — was that a break in the
  protocol, or did logging drop off while you kept going?"

When the user fills a gap inline, fold their answer into the page — as a
commentary bullet under `## Check-ins`, or into a draft `## Verdict` if
you're in verdict mode.

### 6. Branch on review_date

**Before review_date — pulse mode:**

- Output: timeline summary, gaps found, user's gap-fill answers, and a
  recommendation: keep going / adjust protocol / extend review_date / cut
  short
- Do NOT write `## Verdict`. Do NOT change `status`.
- If protocol drift is significant and the user confirms, offer to edit
  `## Protocol` to match reality (and note the change in check-ins).

**At or past review_date — verdict mode:**

- Propose one of:
  - `adopt` — keep doing it, it worked
  - `modify` — worth keeping in altered form (name the modification)
  - `drop` — not worth continuing (say why)
  - `inconclusive` — not enough signal to decide; propose a followup
    experiment or extension
- Write `## Verdict` with reasoning that ties back to each success
  criterion and the original hypothesis.
- Write `## Learnings` — separate "works for me" from "general principle"
  so future-you can tell which is transferable.
- Update frontmatter: `status: concluded`, `outcome: <verdict>`,
  `date_updated: today`.
- If the learnings deserve a wiki page (or extension of an existing one),
  offer to route to `wiki-create` (stub mode) or `wiki-refresh`. Add bidirectional
  links via `related:` and `## See also`.
- If the verdict affects a Software Catalog entry (e.g., adopting a tool
  moves it from `trial` to `adopt`), offer to route to `catalog-evaluate`.

### 7. Report

- Mode taken (pulse or verdict)
- Timeline summary and key gaps
- Follow-up answers the user provided
- For verdicts: outcome recorded, status change, any downstream routing
  (`wiki-create`, `wiki-refresh`, `catalog-evaluate`, follow-up experiment)

## Quality rules

- One question at a time. Don't batch gap-fill questions.
- Don't write a verdict before `review_date` unless the user explicitly
  asks to cut the experiment short.
- Never overwrite user-authored `## Verdict` or `## Learnings` content —
  extend, append, or comment below.
- If the user rejects the proposed verdict, record *their* verdict and
  reasoning. It's their experiment.
- `inconclusive` is a valid outcome. Don't force a decision from thin
  evidence; propose an extension or followup instead.
