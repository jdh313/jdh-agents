---
name: experiment-review
description: >-
  Review an experiment — pulse-check mid-run, or record the verdict at/after
  review_date. Reads the experiment page plus all daily-note check-ins (via
  @vault-reader), summarizes observations, probes for missing context, and (if
  review_date has arrived) guides the adopt/modify/drop/inconclusive verdict.
  Use when the user says "how is X going", "review the X experiment", "time to
  review", "verdict on", "what did I learn from", or when an experiment's
  review_date has arrived.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(obsidian-cli *)
---

# Experiment Review

Read an experiment plus all its daily-note check-ins, summarize what's
happened, probe gaps, and (if at/after `review_date`) guide the verdict.
The check-in pull dispatches to `@vault-reader`; the verdict walk runs
inline; the verdict write dispatches to `@note-editor`.

**Dispatch shape:** this is a multi-step *reader* session — you pull the
page, then often need follow-up reads (a related experiment, a linked
wiki page, re-reading the page after a write). Keep the **same**
`@vault-reader` instance alive across these reads: dispatch it once
(step 1 or 2), then re-engage it (via `SendMessage` to its agent ID) for
any further read in this review, rather than cold-spawning a fresh reader
each time. The reader retains the experiment page and check-ins it
already loaded, so follow-ups are cheap and consistent. The
`@note-editor` write (step 6) stays **one-shot** — it's a single
finalized append with no state to carry.

Schema lives in `~/Loose Ends/.claude/rules/wiki.md` →
**Experiments**.

## When to use

- User asks about the state of a running experiment
- An experiment's `review_date` has been reached or passed
- User wants to record a verdict
- User mentions they want to adopt/drop/modify something they've been testing

## Workflow

### 1. Identify the experiment

If unambiguous from context, pick it. Otherwise, dispatch a brief lookup
to `@vault-reader`:

```markdown
## Intent
list active experiments

## Constraints
- Folder: `Experiments/`
- Filter: `status: running` or `status: reviewing`

## Output shape
List of paths with title and review_date.
```

Ask the user to pick one.

### 2. Pull the page + check-ins (via vault-reader)

If step 1 already spun up a `@vault-reader` to list experiments,
**re-engage that same instance** with this payload instead of dispatching
a new one. Otherwise dispatch fresh:

```markdown
## Intent
pull experiment page and all daily-note check-ins for <experiment-path>

## Constraints
- Read the experiment page: hypothesis, success criteria, protocol, dates
- Find daily-note mentions via `obsidian-cli backlinks` against the
  experiment path — do not scan `Daily Notes/` with find/glob/grep
- For each backlinking daily note, return the check-in line plus
  sibling bullets

## Output shape
- Page snapshot: hypothesis, success criteria (list), protocol, start_date, review_date, current status
- Check-ins: chronological list with date, source daily-note path, content
```

### 3. Build a timeline summary (inline)

Condensed, dated timeline of observations — not a raw dump. Group by
theme where useful ("energy observations", "friction points",
"adjustments made"). Front-load what changed; strip filler.

### 4. Detect gaps (inline)

Before asking the user anything, scan for:

- **Uncovered success criteria** — any criterion with no observation in check-ins
- **Silent stretches** — no check-ins for >N days (default N=4 for running experiments; adjust for cadence)
- **Protocol drift** — check-ins describe behavior diverging from the stated protocol
- **Conflicting signals** — early positive, later negative (or vice versa) without stated cause
- **Missing verdict context** — if `review_date` has arrived, is there enough in check-ins to decide? Name what's missing.
- **Off-protocol adoption** — if check-ins are sparse or absent, do not
  jump to `inconclusive`. Check whether the thing under test got used
  anyway, outside the protocol: search project memory, the repo's
  `CLAUDE.md`, recent commits, and related vault notes for real usage in
  the experiment window. An experiment can be simultaneously *untested*
  (its hypothesis never exercised) and *its subject adopted* (through
  work the protocol wasn't watching). That combination is `modify`, not
  `inconclusive` — the verdict narrows the scope to what was actually
  proven and names what remains open.

### 5. Ask targeted follow-ups (inline)

One question at a time. Only ask about *real* gaps from step 4, not a
checklist. Examples:

- "Success criterion was 'fewer afternoon energy crashes' — check-ins don't mention afternoon energy. Did you notice a change?"
- "Protocol called for 90-minute blocks; most check-ins mention 60-minute ones. Did you adjust, or is the protocol outdated?"
- "No check-ins for 9 days in the middle — was that a break, or did logging drop off?"

When the user fills a gap inline, hold the answer in working memory —
it goes into the page in step 6 (via the agent).

### 6. Branch on review_date

**Before review_date — pulse mode:**

- Output inline: timeline summary, gaps found, user's gap-fill answers, and a recommendation (keep going / adjust protocol / extend review_date / cut short)
- Do NOT write `## Verdict`. Do NOT change `status`.
- If the user wants gap-fill answers added to `## Check-ins`, or wants protocol updated, dispatch to `@note-editor`:

  ```markdown
  ## Intent
  append commentary to <experiment-path>

  ## Constraints
  - Append under existing `## Check-ins` heading
  - Preserve all other content

  ## Input
  <the bullets to add, drafted with the user>

  ## Output shape
  Confirm file modified.
  ```

**At or past review_date — verdict mode:**

- Propose one of: `adopt` / `modify` / `drop` / `inconclusive`
- Draft `## Verdict` inline with the user, tying back to each success criterion and the original hypothesis
- Draft `## Learnings` inline, separating "works for me" from "general principle"
- Once the user approves the draft, dispatch the write to `@note-editor`:

  ```markdown
  ## Intent
  conclude experiment <experiment-path>

  ## Constraints
  - Append `## Verdict` and `## Learnings` sections (do not overwrite existing)
  - Update frontmatter: `status: concluded`, `outcome: <verdict>`, `date_updated: today`

  ## Input
  <the verdict and learnings drafted with the user>

  ## Output shape
  Confirm file modified with all three changes.
  ```

- If the learnings deserve a wiki page, offer to route to `wiki-create` (stub mode) or `wiki-refresh`.
- If the verdict affects a Software Catalog entry, offer to route to `catalog-evaluate`.

### 7. Report

- Mode taken (pulse or verdict)
- Timeline summary and key gaps
- Follow-up answers the user provided
- For verdicts: outcome recorded, status change, any downstream routing offered

## Quality rules

- One question at a time. Don't batch gap-fill questions.
- Don't write a verdict before `review_date` unless the user explicitly asks to cut the experiment short.
- Never overwrite user-authored `## Verdict` or `## Learnings` content — the agent appends.
- If the user rejects the proposed verdict, record *their* verdict and reasoning.
- `inconclusive` is a valid outcome. Don't force a decision from thin evidence; propose an extension or followup instead.
- Before recording `inconclusive`, confirm the subject genuinely went
  unused. Absent check-ins mean the protocol wasn't followed, not that
  nothing happened — see "Off-protocol adoption" in step 4.
