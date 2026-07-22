---
name: weekly
description: >-
  This skill should be used when the user says "/weekly", "weekly review",
  "review my week", "week in review", "what should I focus on this week",
  "weekly planning", or "weekly check-in". Provides a structured weekly
  review conversation that audits project attention, enforces WIP limits,
  and converges on 1-2 focus projects for the coming week.
allowed-tools:
  # Linear — project health scan
  - mcp__linear-server__list_projects
  - mcp__linear-server__list_issues
  # Obsidian — daily notes, weekly notes, project notes, write weekly note
  - Bash(obsidian-cli *)
---

# /weekly — Weekly Project Review

A guided weekly review conversation that checks project health, compares actual attention to planned focus, and converges on 1-2 projects for the coming week. Enforces WIP limits through coached dialogue. Zero-config — works with or without external data sources.

## Flow

Execute these steps in order. The conversation should feel natural — adapt pacing to the user's responses.

### Step 1: Gather Context (Silent)

Before displaying anything to the user, attempt to gather context from available sources. Skip any source that is unavailable — do not error or mention missing sources.

**Project health** (using `project-pulse` pattern):
- Linear: list projects + recent issues per project
- Obsidian: search for project/hobby notes, check modification dates
- Classify each project as active (≤7 days), drifting (8-21 days), or stale (22+ days)

**Last week's daily notes** (Obsidian, if available):
- Read daily notes from the past 7 days
- Note which projects/topics received attention

**Previous weekly note** (Obsidian, if available):
- Search `Journal/Weekly/` for the most recent weekly note
- Extract last week's stated focus projects

If no sources are available, skip data gathering and start with an open conversation.

### Step 2: Review Last Week

Present what you found concisely:

- **If previous weekly focus exists:** "Last week you said you'd focus on [X, Y]. Here's what actually got attention:" followed by a short list
- **If daily notes show activity but no prior weekly note:** "Based on your daily notes, you spent time on:" followed by a list
- **If no data:** "What did you actually spend time on this past week?"

Ask: **"Does that feel accurate? Anything missing?"**

One exchange to calibrate — don't belabor it.

### Step 3: WIP Limit Conversation

Surface the current project landscape:

- Show project counts by status (active/drifting/stale) if data was gathered
- If no data, ask: "How many projects are you juggling right now?"

Then push toward constraint, calibrated per `coach-tone`:

- **Too many active projects (4+):** "That's a lot of plates spinning. Which ONE matters most this week?"
- **2-3 active:** "Solid. Which of these gets the main focus?"
- **1 or fewer:** "Focused. Is there something drifting that deserves a push this week?"

The goal is **1-2 projects with explicit focus**, everything else explicitly parked. Push back if the user tries to focus on more than 2. Use `coach-tone` calibration — be gentler at low energy, more direct at high energy.

### Step 4: Set This Week's Focus

Once focus is agreed, confirm the selection:

- **Focus projects (1-2):** What's getting active work this week
- **Parked projects:** Everything else — not abandoned, just not this week
- **One concrete next step** per focus project

Frame parked projects neutrally: "Parked" means intentional, not neglected.

### Step 5: Write Weekly Note (With Permission)

Honor the vault conventions in ~/Loose Ends/.claude/CLAUDE.md (frontmatter shape, naming, wikilink style) — read it before the first vault write of a session.

Once the review is complete, ask before writing:

> Want me to save this as a weekly note?

**If Obsidian MCP is available and user agrees:**
- Propose path: `Journal/Weekly/YYYY-[W]WW.md` (e.g., `Journal/Weekly/2026-W07.md`)
- Content structure:
  ```
  # Week WW Review

  ## Last Week
  - What got attention (bullets)

  ## This Week's Focus
  - Focus project 1: next step
  - Focus project 2: next step

  ## Parked
  - Parked project list
  ```
- Ask the user to confirm or adjust the path before writing

**If Obsidian MCP is unavailable or user declines:**
- Display the summary in chat
- No file operations

### Cross-References

- If no `/review` has been done in 30+ days (check `Journal/Reviews/` for recent files), suggest: "It's been a while since a big-picture review. Want to do a `/review` sometime this week?"
- Use `coach-tone` for all coaching calibration

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| Run mid-week | "Mid-week check-in or starting fresh?" — adjust scope accordingly |
| No previous weekly note exists | Skip comparison to prior focus, start with current state |
| All projects stale | No guilt. "Looks like things went quiet. That happens. What do you want to pick back up?" |
| User wants to focus on 3+ projects | Push back: "Three is a lot for a week. Which one could wait?" Allow 3 only if user insists |
| Run twice in same week | "You already did a weekly review. Want to revise your focus or check progress?" |

## What This Skill Does NOT Do

- Create tasks, issues, or calendar events
- Assign deadlines or time blocks
- Guilt the user about stale projects
- Require any specific vault structure or configuration
- Write anything without explicit permission
