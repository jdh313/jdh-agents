---
name: energy
description: >-
  This skill should be used when the user says "/energy", "I'm tired", "low
  energy", "what should I work on", "I can't focus", "energy check", "match
  tasks to energy", or "I'm in the zone". Reorders today's tasks based on
  current energy level -- you don't need motivation, you need the right task for
  your current state. Can be used multiple times per day as energy shifts.
allowed-tools:
  # Todoist — today's tasks, reorder
  - mcp__claude_ai_Todoist__find-tasks-by-date
  - mcp__claude_ai_Todoist__update-tasks
  # Obsidian — read daily note for Today's Focus
  - Bash(obsidian-cli *)
---

# /energy -- Energy-Aware Task Matching

Matches today's tasks to current energy level. You don't need motivation, you need the right task for your current state. Can be used multiple times per day as energy shifts -- energy isn't linear or predictable.

## Flow

Execute these steps in order. Calibrate tone to the reported energy level.

### Step 1: Energy Check (1 Exchange)

One question:

> "How's your energy right now?"

Offer 4 levels:

- **High** -- creative, complex, deep work
- **Medium** -- structured, moderate focus
- **Low** -- routine, admin, low-stakes
- **Crashed** -- bare minimum, self-care OK

If the user already described their energy in their message (e.g., "/energy I'm exhausted"), map to the appropriate level and confirm: "Sounds like you're at low/crashed. That right?"

### Step 2: Match Tasks (Silent + 1 Exchange)

Gather today's tasks from available sources. Skip any unavailable silently.

**Todoist** (if available):
- Query today's tasks (due today)
- Note task content, project, and priority

**Obsidian** (if available):
- Read today's daily note for `## Today's Focus` priorities
- Content may be a morning snapshot (Energy/Triage/Focus/Shape lines) rather than a simple bullet list — extract priorities from the **Focus:** line if snapshot format is present

If no sources are available: "What's on your list for today?" and work from the user's response.

**Categorize each task by energy required** (infer from content):
- **High energy:** Creative tasks, complex coding, writing, design, strategic decisions
- **Medium energy:** Structured work, meetings, reviews, moderate coding, research
- **Low energy:** Email, admin, filing, simple fixes, routine updates, data entry

**Present reordered list based on energy level:**

- **High energy:** Lead with the hardest, most creative task. "You've got the juice -- start with the big one."
- **Medium energy:** Lead with structured work. "Good for steady work. Start with something that has clear steps."
- **Low energy:** Lead with the easiest, most routine task. "Start with the quick wins. Momentum helps."
- **Crashed:** "Honestly? Pick the easiest one, or take a break. Both are fine."

Format:
```
Based on [energy level], I'd suggest this order:

1. [Task] -- [brief reason: "quick win", "needs focus", "just admin"]
2. [Task] -- [brief reason]
3. [Task] -- [brief reason]

[If crashed: "Or skip all of this and take care of yourself. That's productive too."]
```

### Step 3: Offer Todoist Reorder (With Permission)

If Todoist MCP is available and the user likes the suggested order:

> "Want me to reorder these in Todoist?"

- If yes: use `update-tasks` to adjust task due dates or order -- do **not** overwrite priority levels (p1/p2/p3/p4), as the user may use those semantically (e.g., p1 = urgent). Only change priorities if the user explicitly asks for it
- Report what changed
- If no: leave Todoist as-is

If Todoist is unavailable, skip this step.

## Tone

Calibrate `coach-tone` to the reported energy level:

- **High energy:** Direct, confident. "You've got this. Start with [hardest task]."
- **Medium energy:** Steady, supportive. "Solid energy. Here's a good order."
- **Low energy:** Gentle, no pressure. "Low energy is fine. Let's find the right task for right now."
- **Crashed:** Minimal, warm. "Hey. It's okay. Here's the lowest-effort option, or just rest."

Never judge energy level. Never prescribe rest. Never say "you should take a break" -- offer it as an equal option to working.

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| No tasks for today | "Nothing on the list for today. Want to pull something from this week, or take the win?" |
| Only 1 task | "One task today: [task]. [Energy-appropriate encouragement]." No need to reorder |
| User ran `/energy` earlier today | "Energy shifted? Let's re-sort." No judgment about the change |
| User says "crashed" but has urgent deadlines | Acknowledge both: "I hear you're crashed. [Task] is urgent though -- want to do the minimum viable version, or push it?" |
| Energy level doesn't match task demands | "Your energy is low but [task] needs focus. Options: do the minimum version now, or swap it to a higher-energy day." |
| User doesn't want to categorize energy | Skip Step 1, infer from context or default to medium |

## Cross-References

- Pairs with `/today` -- morning priorities set the list, `/energy` reorders mid-day
- Can be used after `/plan-week` for within-day adjustments
- Uses `coach-tone` calibrated to energy level
- Independent of `/triage` -- `/energy` works with today's tasks only

## What This Skill Does NOT Do

- Judge energy level or prescribe rest
- Diagnose burnout or mental health
- Create new tasks or schedule future tasks
- Modify the task list content (only reorders/reprioritizes)
- Require any specific setup or configuration
- Write anything without explicit permission
