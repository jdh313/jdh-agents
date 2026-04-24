---
name: experiment-start
description: Scaffold a new experiment — a time-bounded test of a productivity technique, tool, method, routine, or habit with a hypothesis and a review date. Use when the user says "I want to try", "let's experiment with", "test out", "start an experiment", "someday I want to try", or otherwise frames something as an experiment. Also handles parking future ideas as `status: considering` and promoting a considering experiment to `running`.
---

# Experiment Start

Scaffold a new experiment page under `Experiments/` or promote an existing
`considering` entry to `running`. Schema and skeleton live in
`~/dotfiles/claude/rules/11-knowledge-wiki.md` → **Experiments**.

## Required skills
- **Skill(obsidian:obsidian-cli)** — for note creation, search, and frontmatter
- **Skill(obsidian:obsidian-markdown)** — for Obsidian-flavored markdown

## When to use

- User wants to try a productivity method, tool, habit, routine, or diet
  change in a deliberate, time-bounded way
- User has a "maybe someday" experiment to park in the backlog
  (`status: considering`)
- User is ready to promote a considering experiment to `running`

## Modes

Detect which of two modes applies from context.

### Mode 1 — New experiment

When the user describes something they want to try that has no existing
page, walk through the hypothesis, criteria, protocol, and commitment:

1. **Pin down the hypothesis** — one sentence in the shape "if I do X, then
   Y will improve." Push back on vague ones ("be more productive") —
   fuzzy hypotheses make the verdict impossible later.
2. **Elicit success criteria** — how will they know it worked? Prefer
   concrete or measurable signals over vibes, but don't force it —
   subjective criteria are fine if honest. One to three is plenty.
3. **Define the protocol** — what they'll actually do, and for how long.
   Default durations: 2 weeks for habits/routines, 4 weeks for bigger
   behavioral shifts. Steer away from "for a while" — name a date.
4. **Commit or park?** Ask whether to start now or queue it:
   - Start now → `status: running`, `start_date: today`,
     `review_date: start_date + duration`
   - Park it → `status: considering`, leave `start_date` and
     `review_date` empty

### Mode 2 — Promote considering → running

When the user refers to an idea already parked ("let's start the X
experiment I was considering"):

1. Read the existing `considering` page in `Experiments/`.
2. Re-confirm (or update) the hypothesis, success criteria, and protocol —
   the context that led to parking may have shifted.
3. Ask for duration → compute `review_date`.
4. Update frontmatter: `status: running`, fill `start_date` and
   `review_date`, bump `date_updated`.

## Creating the page

### Filename

`Experiments/<descriptive slug>.md` — e.g. `Time-blocking trial.md`,
`90-min deep work blocks.md`, `Morning pages.md`. No date prefix (unlike
`Sources/`). Keep under 60 characters.

### Frontmatter

```yaml
---
owner: jacob
type: experiment
category: method        # tool | method | routine | habit | other

status: running         # or: considering
outcome:                # blank until concluded

hypothesis: "One line, if-then form"
start_date: YYYY-MM-DD  # empty if considering
review_date: YYYY-MM-DD # empty if considering

related: []
date_created: YYYY-MM-DD
date_updated: YYYY-MM-DD
tags: [experiment/<topic>]
---
```

### Body skeleton

Emit H2s in this order; omit sections that aren't applicable yet (e.g.,
leave `## Verdict` and `## Learnings` empty until review).

1. *One-line hypothesis* (first non-frontmatter line, no heading)
2. `## Context` — why now, what prompted this
3. `## Success criteria` — the concrete signals
4. `## Protocol` — what the user is doing, duration, any daily/weekly cadence
5. `## Check-ins` — emit this Dataview block verbatim:

   ````markdown
   ```dataview
   TABLE WITHOUT ID file.link AS "Date", L.text AS "Note"
   FROM "Daily Notes"
   FLATTEN file.lists AS L
   WHERE contains(L.outlinks, this.file.link)
   SORT file.name DESC
   ```
   ````

6. `## Verdict` — placeholder: `_Filled at review._`
7. `## Learnings` — placeholder: `_Filled at review._`
8. `## See also` — relevant wiki pages, projects, or sources up front

## Quality rules

- `running` status requires hypothesis + protocol + `review_date`. No
  open-ended trials — refuse to set `status: running` without a review
  date.
- Push back on fuzzy hypotheses. Good ones name the intervention *and* the
  expected effect.
- Prefer measurable success criteria, but subjective is acceptable if the
  user is honest that it's a feel-check.
- Remind the user of the check-in convention: write
  `- [[<Experiment Name>]] — short note` in their daily note during the run.

## Report

Tell the user:
- Page created, path, current status
- `start_date` and `review_date` (if running)
- The check-in syntax they'll use in daily notes
- Any `related` links that were added
