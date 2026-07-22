---
name: experiment-start
description: "Scaffold a new experiment \u2014 a time-bounded test of a productivity technique, tool, method, routine, or habit with a hypothesis and a review date. Use when the user says \"I want to try\", \"let's experiment with\", \"test out\", \"start an experiment\", \"someday I want to try\", or otherwise frames something as an experiment. Also handles parking future ideas as `status: considering` and promoting a considering experiment to `running`."
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(obsidian-cli *)
---

# Experiment Start

Scaffold a new experiment page under `Experiments/` or promote an
existing `considering` entry to `running`. Schema and skeleton live in
`~/Loose Ends/.claude/rules/wiki.md` → **Experiments**.

This skill drafts interactively (hypothesis, criteria, protocol,
commitment); `@vault-reader` reads existing pages when promoting; and
`@note-editor` executes the write.

## Vault tool usage

Use `obsidian-cli create name='...' content='...'` for the experiment page. Use `obsidian-cli property:set` for `status`, `start_date`, `review_date`, `hypothesis`, `category` — typed per field. Use `obsidian-cli append file=<daily-note>` to log the experiment start in today's daily note.

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
page, walk through:

1. **Pin down the hypothesis** — one sentence: "if I do X, then Y will improve." Push back on vague ones ("be more productive"). Fuzzy hypotheses make the verdict impossible later.
2. **Elicit success criteria** — how will they know it worked? Prefer concrete or measurable signals; subjective is fine if honest. 1-3 criteria.
3. **Define the protocol** — what they'll actually do, and for how long. Default durations: 2 weeks for habits/routines, 4 weeks for bigger behavioral shifts. Steer away from "for a while" — name a date.
4. **Commit or park?**
   - Start now → `status: running`, `start_date: today`, `review_date: start_date + duration`
   - Park it → `status: considering`, leave `start_date` and `review_date` empty

### Mode 2 — Promote considering → running

When the user refers to an idea already parked ("let's start the X experiment I was considering"):

1. Dispatch to `@vault-reader` to read the `considering` page:

   ```markdown
   ## Intent
   read experiment page at `Experiments/<slug>.md`

   ## Output shape
   Page content + frontmatter snapshot.
   ```

2. Re-confirm (or update) the hypothesis, success criteria, and protocol — the context that led to parking may have shifted.
3. Ask for duration → compute `review_date`.
4. The dispatch in step 5 below will update the frontmatter: `status: running`, fill `start_date` and `review_date`, bump `date_updated`.

## Page conventions

### Filename

`Experiments/<descriptive slug>.md` — e.g. `Time-blocking trial.md`,
`90-min deep work blocks.md`, `Morning pages.md`. No date prefix
(unlike `Sources/`). Keep under 60 characters.

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

## Dispatch the write

After drafting with the user, dispatch to `@note-editor`:

```markdown
## Intent
<create | promote> experiment <slug>

## Constraints
- Mode 1 (create): write `Experiments/<slug>.md` with the drafted frontmatter + body
- Mode 2 (promote): edit existing `Experiments/<slug>.md` — update frontmatter (status, start_date, review_date, date_updated) and refresh any sections whose content shifted during re-confirmation
- Schema: per `~/Loose Ends/.claude/rules/wiki.md` → Experiments

## Input
<full drafted frontmatter + body>

## Output shape
Confirm file written/modified with path and a one-line change summary.
```

## Quality rules

- `running` status requires hypothesis + protocol + `review_date`. No open-ended trials — refuse to set `status: running` without a review date.
- Push back on fuzzy hypotheses. Good ones name the intervention *and* the expected effect.
- Prefer measurable success criteria, but subjective is acceptable if the user is honest about it.
- Remind the user of the check-in convention: write `- [[<Experiment Name>]] — short note` in their daily note during the run.

## Report

Tell the user:

- Page created/promoted, path, current status
- `start_date` and `review_date` (if running)
- The check-in syntax they'll use in daily notes
- Any `related` links that were added
