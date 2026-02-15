# Coach

ADHD-friendly productivity coaching for Claude Code. Seven coaching commands -- `/today`, `/checkin`, `/weekly`, `/reentry`, `/review`, `/sunset`, `/decide` -- plus adaptive tone calibration, a project health scanner, and a historical pattern analysis engine.

## Skills

### `/today` -- Morning Coaching Conversation

Guided daily planning in 5 steps:

1. **Gather context** -- silently checks Todoist, Linear, and Obsidian for tasks, issues, and yesterday's priorities (all optional)
2. **Energy check-in** -- one open-ended question to calibrate tone
3. **Coached conversation** -- 2-4 exchanges to converge on ~3 priorities
4. **Write priorities** -- optionally appends to today's Obsidian daily note
5. **Activate coaching context** -- applies coach-tone patterns for the rest of the session

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

## Design Principles

- **No guilt** -- gaps acknowledged neutrally, inconsistency is expected
- **Zero config** -- works with no MCP servers, better with them
- **Constraint over options** -- "pick your top 3" beats "here are your 47 tasks"
- **Themes over goals** -- directional themes are more ADHD-compatible than measurable targets
- **Capture over coaching** -- `/checkin` and `/decide` prioritize recording over advising
- **Coach doesn't interrupt** -- only responds to coaching-type questions
- **Permission before writing** -- never writes to Obsidian without asking
- **Closing is a skill** -- `/sunset` reframes closure as intentional, not failure

## Data Sources (All Optional)

| Source | Used By | Provides | If Unavailable |
|--------|---------|----------|----------------|
| Todoist MCP | `/today`, `/checkin` | Today's tasks, completed items | Skip |
| Linear MCP | `/today`, `/weekly`, `/reentry`, `/review`, `/sunset`, `project-pulse` | Projects, issues, initiatives | Skip |
| Obsidian MCP | All skills + all agents | Daily notes, project notes, weekly/review/sunset/decision history | Skip |
| None | All | Pure conversation -- asks what you know | Works fine |

## Cross-References

```
/today --writes--> Daily Note (## Today's Focus)
  +--uses--> coach-tone

/checkin --reads--> Daily Note (## Today's Focus)
  +--writes--> Daily Note (## End of Day)
  +--uses--> coach-tone (reduced)

/weekly --uses--> project-pulse, coach-tone
  +--writes--> Journal/Weekly/
  +--suggests--> /review (if >30 days), /sunset (for chronically stale)

/review --uses--> project-pulse, coach-tone, life-areas
  +--writes--> Journal/Reviews/
  +--suggests--> /weekly

/reentry --(standalone)--

/sunset --uses--> project-pulse, coach-tone (warmth bias)
  +--writes--> Journal/Sunsets/
  +--complements--> /reentry (opposite operation)

/decide --uses--> coach-tone (reduced)
  +--writes--> Journal/Decisions/

momentum --reads--> Weekly + Reviews + Sunsets + Daily Notes
  +--identifies candidates for--> /sunset

project-pulse --(data engine: current state)--
coach-tone --(personality: all coaching skills)--
```

## Installation

```bash
/install coach@cc-marketplace
```

## Future

- **Calendar integration** -- surface meeting load for day planning
- **Persistent coaching persona** -- coaching context across sessions
