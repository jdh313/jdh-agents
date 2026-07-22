---
name: today
description: >-
  This skill should be used when the user says "/today", "plan my day",
  "what should I focus on today", "morning planning", "daily priorities",
  "start my day", or "daily planning". Provides a structured morning
  check-in that converges on 3 priorities through an adaptive coaching
  conversation with energy-calibrated tone.
allowed-tools:
  # Todoist — gather tasks, reschedule during triage
  - mcp__claude_ai_Todoist__find-tasks-by-date
  - mcp__claude_ai_Todoist__update-tasks
  # Linear — gather active issues
  - mcp__linear-server__list_issues
  # Obsidian — read daily notes, write morning snapshot
  - Bash(obsidian-cli *)
  - Edit
  # Claude Code tools
  - AskUserQuestion
---

# /today — Morning Coaching Conversation

A guided morning planning conversation that gathers context, checks energy, triages overdue items, and converges on ~3 priorities through coached dialogue. Zero-config — works with or without external data sources.

## Flow

Execute these steps in order. The conversation should feel natural, not robotic — adapt pacing to the user's responses.

### Step 1: Gather Context (Silent)

Before displaying anything to the user, gather context from available MCP servers.
Use query patterns from `references/data-queries.md`. Skip any unavailable source silently.

**Todoist** (if available):
- Query today's tasks + overdue (see data-queries.md § Todoist → Today's Tasks)
- Note task priorities, project groupings, and due dates
- Silently count: how many are overdue vs due today (needed for Step 3)

**Linear** (if available):
- Query active issues (see data-queries.md § Linear → My Active Issues)
- Note issue status and priority

**Obsidian** (if available):
- Read yesterday's daily note
- Look for a `## Today's Focus` or similar priorities section
- Note any carry-forward items

If no MCP servers are available, skip this step entirely. The conversation works without external data.

### Step 2: Energy Check-In

This is the first thing the user sees. Ask one open-ended question:

> How's your energy/headspace right now?

Do not provide multiple-choice options. Accept a free-form response. Use the answer to calibrate tone per the `coach-tone` skill:

- Mentions of tiredness, low mood, rough night → **low energy**
- Neutral, "fine", "okay", nothing strong → **medium energy**
- Mentions of feeling good, motivated, caffeinated, ready → **high energy**

### Step 3: Overdue Triage

Skip this step if there are no overdue tasks.

**If 1-14 overdue items:**
Surface them concisely after the task/issue presentation, grouped by project:
- "You also have [N] overdue from this week:"
- Present as a grouped bullet list
- Ask: "Which of these should move to today, and which should we push?"
- Accept batch answers: "push all the admin stuff to Monday", "keep the insurance one"
- Execute reschedules via Todoist MCP if available and user confirms
- 1-2 exchanges max — don't belabor it

**If 15+ overdue items:**
- Surface the count but not the full list: "You've got [N] overdue tasks piling up."
- Suggest: "Want to do a quick `/triage` first, or just pick the urgent ones for today?"
- If user wants full triage → suggest they run `/triage` and come back to `/today` after
- If user wants to pick urgent ones → show only p1/p2 items or the 5 most overdue, triage those inline

**Tone:** Use `coach-tone` warmth. Frame as renegotiation, not failure. "These piled up — let's sort them out."

**Constraint mentions:** If the user mentioned constraints during the energy check (e.g., "partner is sick", "meetings all afternoon"), reference them: "Given [constraint], which of these are realistic for today?"

### Step 4: Coached Conversation (2-4 Exchanges)

If triage just happened, re-present the remaining items: "After sorting that out, here's what's left for today:" — only today's tasks, overdue already handled.

Surface what was gathered in Step 1. Present it concisely — bullets, not paragraphs.

- If data sources found tasks/issues: "Here's what I see on your plate today:" followed by a short grouped list
- If yesterday's priorities exist: "Yesterday you were focused on [X, Y, Z]"
- If nothing was gathered: "What's on your mind for today?"

Then ask: **"What feels most important today?"** (not "most urgent")

Based on the user's response, push back calibrated to their energy level:

- **Too many items** → Constrain: "That's a lot. If you could only finish 3, which 3?"
- **Too few items** → Probe: "Anything you've been putting off that's nagging at you?"
- **Misaligned with prior priorities** → Question: "Yesterday [X] was a focus and it's still open. Dropping it intentionally?"
- **Vague items** → Clarify: "What does 'work on the project' actually mean — what's the next concrete step?"
- **Constraints mentioned** → Reference them: "You mentioned [partner sick / meetings / low energy]. Does [priority] still fit given that?"

Converge on approximately 3 priorities. The exact number can flex (2-4), but resist more than 4.

### Step 5: Write Morning Snapshot (With Permission)

Honor the vault conventions in ~/Loose Ends/.claude/CLAUDE.md (frontmatter shape, naming, wikilink style) — read it before the first vault write of a session.

Once priorities are agreed, ask before writing anything:

> Want me to add a morning snapshot to today's daily note?

**If Obsidian MCP is available and user agrees:**
- Write to today's daily note under a `## Today's Focus` heading
- If the heading already exists, replace its contents
- Write a **morning snapshot** — the shape of the day, not a task mirror:

```markdown
- **Energy:** [One-liner from energy check-in, including constraints if mentioned]
- **Triage:** [Only if triage happened. What was moved/dropped and where]
- **Focus:** [The 2-4 agreed priorities, phrased as intent]
- **Shape:** [One sentence: the character of the day — "admin wins day", "deep work morning", etc.]
```

Rules:
- Energy line is always present
- Triage line is omitted if there were no overdue tasks
- Focus line lists priorities but as intent, not a Todoist copy (e.g., "knock out insurance + student loans, get something printing" not "Submit Jackson meds to insurance")
- Shape line captures the overall day feel in one sentence
- No timestamps, no metadata, no task IDs

**If Obsidian MCP is unavailable or user declines:**
- Display the morning snapshot in chat
- No file operations

### Step 6: Day Shape Recap

Present a brief scannable summary before transitioning to coaching mode:

> Here's your day:
>
> **Energy:** [level + constraints]
> **Shape:** [one-liner]
> **Priorities:**
> 1. [Priority 1]
> 2. [Priority 2]
> 3. [Priority 3]
>
> **Parked:** [items explicitly deferred but still on today's list — omit if none]
>
> [One-line transition, e.g., "Ready when you are." or "LinkedIn first, then ride the momentum."]

This is output only — no user exchange needed. It provides closure on the planning conversation and a reference point for coaching.

### Step 7: Activate Coaching Context

After priorities are set, apply the `coach-tone` skill patterns when the user asks coaching-type questions for the remainder of the session — "what should I do next", "I'm stuck", "I got distracted", "how's my day going". Reference the agreed priorities, energy level, **and any constraints mentioned** when responding.

For all other questions (code, research, file operations), respond normally without coaching behavior.

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| `/today` run twice in same session | "You already set priorities — want to revise them or start fresh?" |
| Gap of several days since last daily note | No guilt. Neutrally: "Last time you set priorities, you were focused on [X, Y, Z]" |
| Run in the afternoon | "Late start or afternoon reset?" — adjust scope expectations accordingly |
| User says "stop coaching" | Drop coaching context, return to normal Claude behavior |
| User provides no energy info | Default to medium energy tone |
| `/today` after `/triage` same session | Skip the triage step — it was already done. "You already triaged earlier — working from your updated task list." |
| User mentions constraints during energy | Carry forward explicitly. Reference during triage and priority pushback. |
| Daily note doesn't exist yet | Create it with standard frontmatter + headings before writing, or note that user should create it. |
| No Todoist MCP (can't detect overdue) | Skip triage step. During coached conversation, ask: "Anything overdue or piling up?" |

## What This Skill Does NOT Do

- Assign time blocks or create schedules
- Create Todoist tasks or move Linear issues
- Lecture about productivity systems or habits
- Require any specific setup, vault structure, or configuration
- Interrupt or nudge proactively after setup is complete
- Mirror the Todoist/Linear task list into the daily note (captures context, not a task copy)
