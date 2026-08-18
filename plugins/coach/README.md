# Coach

> **Requires an Obsidian vault.** Skills in this plugin read and write notes in an
> Obsidian vault, defaulting to `~/Loose Ends/`. That default is an example, not a
> requirement — point it at your own vault by editing the paths in the skill bodies
> (search for `Loose Ends`). Without a vault, the vault-writing skills will not work.

ADHD-friendly productivity coaching for Claude Code. Fifteen coaching commands -- `/today`, `/checkin`, `/weekly`, `/plan-week`, `/reentry`, `/review`, `/align`, `/sunset`, `/decide`, `/triage`, `/intake`, `/spark`, `/dump`, `/breakdown`, `/energy` -- plus adaptive tone calibration, a project health scanner, an overdue pattern analyzer, and a historical pattern analysis engine.

## Skills

### `/today` -- Morning Coaching Conversation

Guided daily planning in 7 steps:

1. **Gather context** -- silently checks Todoist, Linear, and Obsidian for tasks, issues, and yesterday's priorities (all optional)
2. **Energy check-in** -- one open-ended question to calibrate tone
3. **Overdue triage** -- inline triage of overdue tasks if present (1-2 exchanges max, or defer to `/triage`)
4. **Coached conversation** -- 2-4 exchanges to converge on ~3 priorities
5. **Write morning snapshot** -- optionally writes energy/triage/focus/shape to today's daily note
6. **Day shape recap** -- scannable summary before transitioning to coaching
7. **Activate coaching context** -- applies coach-tone patterns for the rest of the session

### `/checkin` -- End-of-Day Pulse

Quick end-of-day bookend to `/today`. Intentionally brief -- EOD energy is low:

1. **Gather context** -- silently reads today's daily note for stated priorities, Todoist completions, Linear updates
2. **Reflect** -- one question: compares plan to reality, asks how it feels
3. **Write end-of-day** -- optionally appends `## End of Day` to today's daily note with done/drifted/energy bullets

Capture, not coaching. One question, accept the answer, move on.

### `/weekly` -- Weekly Project Review

Structured weekly review that audits project attention and enforces WIP limits:

1. **Gather context** -- project health scan + daily notes from the past week
2. **Review last week** -- compare actual attention to stated focus
3. **WIP limit conversation** -- push toward 1-2 focus projects, park the rest
4. **Set this week's focus** -- explicit focus + parked list with next steps
5. **Write weekly note** -- optionally saves to `Journal/Weekly/YYYY-[W]WW.md`

### `/reentry` -- Project Re-Entry Briefing

Context dump for returning to a paused project:

1. **Identify project** -- fuzzy-match across Linear projects and Obsidian notes
2. **Gather context** -- issues, note content, modification dates
3. **Present briefing** -- last active date, where you left off, open items, single next step
4. **Offer to continue** -- transition into working on the next step

### `/review` -- Life-Direction Review

Monthly or quarterly zoom-out review:

1. **Determine period** -- monthly check-in or quarterly review based on last review date
2. **Life areas check-in** -- rate 6 areas (career, health, home, hobbies, relationships, learning) 1-5
3. **Initiative & project audit** -- project health scan, compare attention to plan
4. **Set next theme** -- ONE directional theme (not goals), 1-2 projects that serve it
5. **Write review note** -- optionally saves to `Journal/Reviews/YYYY-MM Review.md`

### `/align` -- Goal-to-Project Mapping

Maps a stated goal to existing projects, recommending focus order instead of starting something new:

1. **Capture goal** -- ask what direction to move toward; check Obsidian for current `/review` theme
2. **Scan existing projects** -- silently gathers Linear projects, initiatives, and Obsidian project/hobby notes
3. **Map alignment** -- classify each project as Direct, Partial, or Unrelated; present alignment table
4. **Recommend focus order** -- prioritize by shippability, current status, and learning surface
5. **Identify gaps & next steps** -- note uncovered aspects, suggest extending existing work before `/intake`

The forward-looking complement to `/review` -- where `/review` sets a theme, `/align` operationalizes it. Steers toward finishing what exists before starting fresh.

### `/sunset` -- Intentional Project Closure

Guided conversation for closing a project with captured restart context:

1. **Identify project** -- fuzzy-match or show stale candidates
2. **Gather context** -- Linear project details, Obsidian notes, weekly/review mentions
3. **Closure conversation** -- why closing, restart context for future-you, open items disposition
4. **Write closure note** -- optionally saves to `Journal/Sunsets/YYYY-MM-DD Sunset - [Project Name].md`
5. **Offer Linear update** -- mark project as Paused (never archive/delete)

Complements `/reentry` -- one opens projects, the other closes them. "Closing projects is a skill, not a failure."

### `/decide` -- Decision Journal

Structured decision capture to prevent re-litigation:

1. **Capture** -- what's the decision? If still deciding, brief coaching to land it
2. **Structure** -- organize into context, options, choice, rationale
3. **Enrich** -- link to related project notes and prior decisions
4. **Write record** -- optionally saves to `Journal/Decisions/YYYY-MM-DD [decision-slug].md`

Primarily capture, not coaching. Accepts "gut feel" as valid rationale. "Revisit Conditions" section defines when to reconsider.

### `/triage` -- Overdue Task Rescue

Guilt-free batch processing of overdue Todoist tasks:

1. **Gather overdue tasks** -- silently queries Todoist for overdue items, groups by project, flags chronic reschedulers (3+ times)
2. **Present batch** -- overdue tasks grouped by project with age and rescheduling history
3. **Triage decisions** -- four actions per task/group: reschedule (to a real date), do today, drop (no guilt), delegate
4. **Execute** -- confirms batch summary, then updates Todoist

Batch processing reduces decision fatigue. "These aren't failures, they're renegotiations."

### `/plan-week` -- Week Ahead Scheduling

Forward-looking week planning with a max-3-tasks-per-day constraint:

1. **Gather context** -- Todoist (week tasks + overdue), latest weekly note, Linear sprint
2. **Landscape** -- present what's on the plate, ask for 3 things that would make the week feel successful
3. **Slot priorities** -- map priorities + tasks across days, max 3 real tasks/day
4. **Write week plan** -- optionally appends `## Week Plan` to the weekly note
5. **Offer Todoist updates** -- optionally reschedules task due dates to match

Complements `/weekly` (which reviews) -- this one schedules ahead.

### `/intake` -- New Project Intake

Structured onboarding for new projects with WIP awareness:

1. **Capture** -- what's the project, what does done look like, what's the first step
2. **WIP check** -- shows active project count, asks "which one does this replace, or is this additive?"
3. **Scope** -- quick gut check: weekend, month, or ongoing
4. **Write project note** -- optionally creates Obsidian project note
5. **Offer integrations** -- optionally creates Linear project and/or Todoist task

The opposite of `/sunset` -- one opens projects, the other closes them. Impulse control without gatekeeping.

### `/breakdown` -- Project Task Decomposition

Conversational decomposition of a project into sequenced, ADHD-friendly Linear issues:

1. **Gather context** -- identify the project, check Linear for existing issues, read Obsidian notes
2. **Orient** -- present what you found, detect decompose vs. recompose mode
3. **Breakdown** -- work through the project conversationally to produce a task list
4. **Write** -- create Linear issues or display for manual entry
5. **Update project note** -- optionally patches Obsidian with the breakdown

Auto-detects two modes: **decompose** (no tasks yet, break down from scratch) or **recompose** (existing Linear issues that have drifted, reconcile and reorder). Graduates from `/spark` → `/intake` → `/breakdown` through the project lifecycle.

### `/spark` -- Interest/Idea Capture

Low-friction idea parking lot in under 60 seconds:

1. **Capture** -- "What caught your attention?" Accept anything
2. **Tag** -- auto-suggest category: hobby, tool, learning, project-idea, business
3. **Write** -- append to monthly sparks log at `Journal/Sparks/YYYY-MM Sparks.md`

Speed over structure. Validates the dopamine hit without committing. Sparks get reviewed during `/weekly` or `/review` for promotion to `/intake`.

### `/dump` -- Brain Dump

Get everything out of your head, then optionally sort it:

1. **Dump** -- unstructured purge: tasks, worries, ideas, half-thoughts, whatever
2. **Mirror back** -- extracted numbered list for confirmation
3. **Categorize** -- sort into tasks, sparks, projects, decisions, or noise
4. **Route** -- tasks to Todoist, sparks to log, projects/decisions flagged for `/intake` or `/decide`

Pressure-release valve for mental overload. "Not everything needs a home. Some things just needed to be said."

### `/energy` -- Energy-Aware Task Matching

Reorders today's tasks based on current energy level:

1. **Energy check** -- high (deep work), medium (structured), low (routine), crashed (bare minimum)
2. **Match tasks** -- pulls today's tasks, categorizes by energy required, reorders to match
3. **Offer Todoist reorder** -- optionally updates priorities to match

Can be used multiple times per day. "You don't need motivation, you need the right task for your current state."

### `coach-tone` -- Adaptive Coaching Personality

Tone calibration and response patterns for coaching interactions. Loaded automatically by coaching skills.

- **Low energy** -- gentle, reduced scope, smallest viable step
- **Medium energy** -- balanced, contextual nudges
- **High energy** -- direct, challenging, aim bigger

## Agents

### `project-pulse` -- Project Activity Scanner

Data engine that scans Linear projects and Obsidian project/hobby notes to classify activity levels:

- **Active** (0-7 days) -- recently touched
- **Drifting** (8-21 days) -- losing momentum
- **Stale** (22+ days) -- no recent attention

Triggered by: "what projects have I neglected?", "stale projects", "project health check"

### `momentum` -- Historical Pattern Analysis

Data engine that reads coaching notes from Obsidian to surface trends invisible in the moment:

- **Focus trends** -- which projects got attention each week (table view)
- **Consistent focus** -- projects with 3+ weeks of sustained attention
- **Chronic parking** -- projects that keep getting parked (sunset candidates)
- **Drift analysis** -- stated-vs-actual match rate from daily notes
- **Theme alignment** -- whether focus projects serve the stated theme
- **Life area trajectory** -- how satisfaction ratings shift across reviews

Triggered by: "what patterns do you see?", "momentum check", "am I making progress?", "focus history"

Read-only -- reports patterns, doesn't prescribe actions. Making the invisible visible for ADHD time-blindness.

### `overdue-rescue` -- Todoist Overdue Pattern Analysis

Data engine that analyzes Todoist overdue tasks and activity history to surface patterns:

- **Overdue summary** -- total count, average age, oldest task
- **Chronic reschedulers** -- tasks rescheduled 3+ times with count
- **Project health** -- which projects accumulate the most overdue tasks
- **Completion patterns** -- when tasks actually get done (day/time patterns)
- **Recommendations** -- suggests `/triage` for chronic reschedulers, `/sunset` for unhealthy projects

Triggered by: "overdue patterns", "why do my tasks slip?", "task health", "chronic overdue"

Read-only -- reports patterns, doesn't modify tasks. Complements `momentum` (Obsidian patterns) by reading Todoist.

## Design Principles

- **No guilt** -- gaps acknowledged neutrally, inconsistency is expected
- **Zero config** -- works with no MCP servers, better with them
- **Constraint over options** -- "pick your top 3" beats "here are your 47 tasks"
- **Themes over goals** -- directional themes are more ADHD-compatible than measurable targets
- **Capture over coaching** -- `/checkin`, `/decide`, and `/spark` prioritize recording over advising
- **Energy acceptance** -- `/energy` matches tasks to state, not the other way around
- **Awareness not gatekeeping** -- `/intake` WIP check informs without blocking
- **Coach doesn't interrupt** -- only responds to coaching-type questions
- **Permission before writing** -- never writes to Obsidian without asking
- **Closing is a skill** -- `/sunset` reframes closure as intentional, not failure

## Data Sources (All Optional)

| Source | Used By | Provides | If Unavailable |
|--------|---------|----------|----------------|
| Todoist MCP | `/today`, `/checkin`, `/triage`, `/plan-week`, `/energy`, `overdue-rescue` | Tasks, completed items, activity history | Skip |
| Linear MCP | `/today`, `/weekly`, `/reentry`, `/review`, `/align`, `/sunset`, `/intake`, `/breakdown`, `project-pulse` | Projects, issues, initiatives | Skip |
| Obsidian MCP | All skills + `momentum` | Daily notes, project notes, weekly/review/sunset/decision/sparks history | Skip |
| None | All | Pure conversation -- asks what you know | Works fine |

## Cross-References

```
DAILY CYCLE:
/today --writes--> Daily Note (## Today's Focus -- morning snapshot)
  +--uses--> coach-tone
/energy --reads--> Todoist today's tasks --reorders--> by energy level
/checkin --reads--> Daily Note + Todoist completed --writes--> Daily Note (## End of Day)

WEEKLY CYCLE:
/plan-week --reads--> Todoist (week tasks + overdue) + Weekly Note
  +--writes--> Weekly Note (## Week Plan)
  +--optionally updates--> Todoist due dates
/weekly --reviews--> project health --writes--> Journal/Weekly/
  +--suggests--> /review (if >30 days), /sunset (for chronically stale)
/triage --reads--> Todoist overdue --updates--> Todoist (reschedule/drop/do)

PROJECT LIFECYCLE:
/spark --captures--> Journal/Sparks/ (monthly log)
  +--reviewed by--> /weekly, /review
/dump --routes--> Todoist (tasks) + Journal/Sparks/ (ideas)
  +--flags for--> /intake (projects), /decide (decisions)
/intake --creates--> project note + optional Linear/Todoist
  +--checks WIP via--> project-pulse pattern
  +--graduates from--> /spark
/breakdown --decomposes--> Linear issues (sequenced task list)
  +--graduates from--> /intake
  +--feeds into--> /today, /plan-week, /reentry
/align --reads--> Linear projects + Obsidian projects/hobbies
  +--maps goal to--> existing projects (focus order)
  +--operationalizes--> /review theme
  +--gaps suggest--> /intake, /plan-week
/reentry --(context dump for paused projects)--
/sunset --closes--> Journal/Sunsets/
  +--complements--> /reentry (opposite operation)

ANALYSIS:
momentum --reads--> Obsidian (Weekly + Reviews + Sunsets + Daily)
overdue-rescue --reads--> Todoist (overdue + activity + completion patterns)
project-pulse --reads--> Linear + Obsidian (current state)

CROSS-CUTTING:
/decide --uses--> coach-tone (reduced) --writes--> Journal/Decisions/
/review --uses--> project-pulse, coach-tone, life-areas --writes--> Journal/Reviews/
coach-tone --(personality: all coaching skills)--
life-areas --(reference: /review)--
```

## Installation

```bash
/install coach@cc-marketplace
```

## Future

- **Calendar integration** -- surface meeting load for day planning
- **Persistent coaching persona** -- coaching context across sessions
