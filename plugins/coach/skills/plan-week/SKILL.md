---
name: coach:plan-week
description: >-
  This skill should be used when the user says "/plan-week", "plan my week",
  "schedule my week", "what's my week look like", "week ahead", "weekly
  schedule", "set up my week", or "next week". Forward-looking week scheduling with a
  3-priority constraint that maps tasks across days without overloading --
  complements /weekly (which reviews) by scheduling ahead.
allowed-tools:
  # Todoist — week tasks, reschedule
  - mcp__claude_ai_Todoist__find-tasks-by-date
  - mcp__claude_ai_Todoist__update-tasks
  # Linear — cycle issues
  - mcp__linear-server__list_issues
  # Obsidian — read weekly note, write/patch week plan
  - Bash(obsidian-cli *)
  - Edit
---

# /plan-week -- Week Ahead Scheduling

Forward-looking week planning that maps priorities and tasks across days. Constraint-based: max 3 real tasks per day to prevent ADHD overloading. Complements `/weekly` (which reviews the past week) -- this one schedules the next one.

## Flow

Execute these steps in order. Use `coach-tone` at medium energy throughout.

### Step 1: Gather Context (Silent)

Before displaying anything, gather from available sources. Skip any that are unavailable.

**Todoist** (if available):
- Query tasks due this week (Monday through Sunday)
- Query overdue tasks
- Note task priorities and project groupings

**Obsidian** (if available):
- Read the latest weekly note from `Journal/Weekly/` for project focus list and parked list
- Check if a week plan already exists for this week

**Linear** (if available):
- Query issues assigned to the user in the current cycle/sprint
- Note issue priority and status

If no sources are available, proceed with conversation only.

### Step 2: Landscape (1 Exchange)

Present what's on the plate for the week. Keep it scannable.

```
Here's what I see for this week:

- [N] Todoist tasks due this week
- [M] overdue (carrying forward)
- [K] Linear issues in the current cycle
- Focus projects from your last /weekly: [list]
```

Then ask: **"What are the 3 things that would make this week feel successful?"**

Not "what needs to get done" -- what would make it feel successful. This distinction matters for ADHD motivation.

### Step 3: Slot Priorities (1-2 Exchanges)

Help map the 3 priorities plus existing tasks across the week.

**Constraint: suggest max 3 real tasks per day.** "Real tasks" means things that require focused effort -- quick admin doesn't count against the limit.

If a day is overloaded:
> "That's [N] tasks on Wednesday. Which 2 matter most?"

Suggest moving overflow to later in the week or next week. Don't just accept an overloaded day.

Consider:
- Monday: easing in, admin catch-up
- Tuesday-Thursday: peak focus days
- Friday: wrap-up, lighter tasks

But follow the user's lead on their own energy patterns if they share them.

### Step 4: Write Week Plan (With Permission)

Once the plan is agreed, ask before writing:

> Want me to add this to your weekly note?

**If Obsidian MCP is available and user agrees:**
- Append a `## Week Plan` section to the current weekly note in `Journal/Weekly/`
- If the weekly note doesn't exist yet, note this and ask if the user wants to create one or just see the plan in chat
- Format:
  ```
  ## Week Plan

  ### Monday
  - [ ] Task 1
  - [ ] Task 2

  ### Tuesday
  - [ ] Task 1
  - [ ] Task 2
  - [ ] Task 3

  ### Wednesday
  - [ ] Task 1
  - [ ] Task 2

  ...
  ```
- Ask the user to confirm before writing

**If Obsidian MCP is unavailable or user declines:**
- Display the week plan in chat
- No file operations

### Step 5: Offer Todoist Updates (With Permission)

If Todoist MCP is available:

> Want me to update the due dates in Todoist to match this plan?

- If yes: use `update-tasks` to reschedule tasks to their planned days
- Only update tasks that were explicitly slotted -- don't touch tasks the user didn't mention
- Report what was changed

If Todoist is unavailable, skip this step.

## Tone

Use `coach-tone` at **medium energy**:

- Forward-looking and energizing, not overwhelming
- "3 real things per day. If you finish early, that's a bonus."
- Resist the urge to pack the week: "An ambitious plan you abandon by Wednesday is worse than a modest plan you actually follow."
- If the user tries to overload: "I know it feels like you should do more. But planning for 3 things and doing 3 things beats planning for 8 and doing 2."

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| Run on a Wednesday | Plan the remainder of the week (Wed-Sun), not the full week |
| Large backlog of overdue tasks | Suggest `/triage` first: "You have [N] overdue tasks. Want to triage those first so we're planning from a clean list?" |
| User wants to plan 2+ weeks | Plan one week at a time: "Let's nail this week first. We can plan next week on Friday/Monday." |
| Already have a week plan for this week | "You already have a week plan. Want to revise it or start fresh?" |
| No tasks from any source | Pure conversation: "What are your 3 priorities this week?" then build the plan from there |
| User has no weekly note yet | Offer to create one or just display the plan in chat |
| User's 3 priorities don't match existing tasks | That's fine -- priorities might be high-level goals, not individual tasks. Map tasks to priorities. |

## Cross-References

- Complements `/weekly` -- `/weekly` reviews the past week, `/plan-week` schedules the next one
- Best used after `/triage` -- clean backlog first, then schedule
- Uses `coach-tone` at medium energy
- Week plan feeds into `/today` -- daily planning can reference the week plan
- Pairs with `/energy` -- if energy shifts mid-week, `/energy` reorders within a day

## What This Skill Does NOT Do

- Access calendar or create time blocks (no calendar MCP -- work with Todoist dates and the user's knowledge of their schedule; if the user mentions a busy day, factor it in)
- Auto-schedule without permission
- Replace `/weekly` (they complement -- one reviews, one schedules)
- Create new tasks in Todoist
- Plan beyond one week ahead
- Require any specific vault structure or configuration
- Write anything without explicit permission
