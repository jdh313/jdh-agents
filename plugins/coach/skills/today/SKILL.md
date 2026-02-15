---
name: today
description: >-
  This skill should be used when the user says "/today", "plan my day",
  "what should I focus on today", "morning planning", "daily priorities",
  "start my day", or "daily planning". Provides a structured morning
  check-in that converges on 3 priorities through an adaptive coaching
  conversation with energy-calibrated tone.
---

# /today — Morning Coaching Conversation

A guided morning planning conversation that gathers context, checks energy, and converges on ~3 priorities through coached dialogue. Zero-config — works with or without external data sources.

## Flow

Execute these steps in order. The conversation should feel natural, not robotic — adapt pacing to the user's responses.

### Step 1: Gather Context (Silent)

Before displaying anything to the user, attempt to gather context from available MCP servers. Skip any source that is unavailable — do not error or mention missing sources.

**Todoist** (if available):
- Query today's tasks and any overdue items
- Note task priorities and project groupings

**Linear** (if available):
- Query issues assigned to the user in the current cycle
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

### Step 3: Coached Conversation (2-4 Exchanges)

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

Converge on approximately 3 priorities. The exact number can flex (2-4), but resist more than 4.

### Step 4: Write Priorities (With Permission)

Once priorities are agreed, ask before writing anything:

> Want me to add these to today's daily note?

**If Obsidian MCP is available and user agrees:**
- Append to today's daily note under a `## Today's Focus` heading
- Simple bullet list, no metadata or timestamps
- If the heading already exists, replace its contents

**If Obsidian MCP is unavailable or user declines:**
- Display the final priority list in chat
- No file operations

### Step 5: Activate Coaching Context

After priorities are set, apply the `coach-tone` skill patterns when the user asks coaching-type questions for the remainder of the session — "what should I do next", "I'm stuck", "I got distracted", "how's my day going". Reference the agreed priorities and energy level when responding.

For all other questions (code, research, file operations), respond normally without coaching behavior.

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| `/today` run twice in same session | "You already set priorities — want to revise them or start fresh?" |
| Gap of several days since last daily note | No guilt. Neutrally: "Last time you set priorities, you were focused on [X, Y, Z]" |
| Run in the afternoon | "Late start or afternoon reset?" — adjust scope expectations accordingly |
| User says "stop coaching" | Drop coaching context, return to normal Claude behavior |
| User provides no energy info | Default to medium energy tone |

## What This Skill Does NOT Do

- Assign time blocks or create schedules
- Create Todoist tasks or move Linear issues
- Lecture about productivity systems or habits
- Require any specific setup, vault structure, or configuration
- Interrupt or nudge proactively after setup is complete
