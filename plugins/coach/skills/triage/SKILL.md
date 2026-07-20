---
name: triage
description: >-
  This skill should be used when the user says "/triage", "overdue tasks",
  "clean up my tasks", "task backlog", "reschedule overdue", "my tasks are a
  mess", "triage my tasks", or "what's overdue". Provides guilt-free batch processing of overdue
  Todoist tasks with reschedule/do/drop/delegate actions and ADHD-friendly
  framing -- these aren't failures, they're renegotiations.
allowed-tools:
  # Todoist — overdue tasks, activity history, reschedule, complete
  - mcp__claude_ai_Todoist__find-tasks-by-date
  - mcp__claude_ai_Todoist__find-activity
  - mcp__claude_ai_Todoist__update-tasks
  - mcp__claude_ai_Todoist__complete-tasks
---

# /triage -- Overdue Task Rescue

Guilt-free batch processing of overdue tasks. Groups by project, flags chronic reschedulers, and offers four actions: reschedule, do today, drop, or delegate. Batch decisions reduce decision fatigue -- don't ask about each task individually unless the user wants to.

## Flow

Execute these steps in order. Use `coach-tone` with warmth bias throughout. Frame overdue tasks as renegotiations, not failures.

### Step 1: Gather Overdue Tasks (Silent)

Before displaying anything to the user, query Todoist for overdue tasks. Skip if Todoist MCP is unavailable.

**Todoist** (if available):
- Query `find-tasks-by-date` with startDate `today` (includes overdue items)
- Filter to tasks where the due date is before today
- Group tasks by project
- For each task, calculate days overdue

**Todoist activity** (if available):
- Query `find-activity` for recent rescheduling events
- Identify chronic reschedulers: tasks that have been rescheduled 3+ times
- Note reschedule count per task

If Todoist MCP is unavailable: "I need Todoist access to pull your overdue tasks. Want to list them manually instead?"

### Step 2: Present Batch

Present overdue tasks grouped by project. Keep it scannable -- bullets, not prose.

Format:
```
Here's what's overdue:

**[Project Name]** (N tasks)
- Task A (3 days overdue)
- Task B (11 days overdue) -- this one keeps coming back (rescheduled 4x)
- Task C (1 day overdue)

**[Another Project]** (N tasks)
- Task D (7 days overdue)
...

[Total] tasks across [N] projects. These aren't failures -- they're renegotiations.
```

Flag chronic reschedulers (3+ reschedules) inline: "this one keeps coming back" or "rescheduled [N]x".

Then ask: **"For each group, what do you want to do?"**

### Step 3: Triage Decisions (1-2 Exchanges)

For each task or group, offer 4 actions:

- **Reschedule** -- to a specific date (not just "tomorrow" -- encourage a real date)
- **Do today** -- move to today's list
- **Drop** -- complete or delete with no guilt
- **Delegate** -- reassign if project has collaborators

Accept batch decisions: "reschedule all of these to next Monday", "drop the bottom 3", "do the first two today". Don't force individual decisions unless the user wants to go one-by-one.

If the user hesitates on dropping: "Dropping a task you're not going to do is more honest than rescheduling it again. It's fine."

### Step 4: Execute (With Permission)

Before executing, confirm the batch action summary:

```
Here's what I'll do:
- Reschedule [Task A, Task B] to Monday 2/17
- Move [Task C] to today
- Mark [Task D] as complete (dropped)

Go ahead?
```

**If user confirms and Todoist MCP is available:**
- `update-tasks` to reschedule tasks (update due dates)
- `update-tasks` to move tasks to today (set due date to today)
- `complete-tasks` to drop tasks
- Report what changed: "[N] rescheduled, [N] moved to today, [N] dropped"

**If Todoist MCP is unavailable or user declines:**
- Display the action plan in chat for the user to execute manually

## Tone

Use `coach-tone` with **warmth bias**:

- "These aren't failures, they're renegotiations."
- "Having 15 overdue tasks doesn't mean you failed 15 times. It means your past self was optimistic."
- "Permission to drop things is always on the table."
- Never: "You should have done this sooner" or "Why did you let these pile up?"

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| No overdue tasks | "Clean slate -- nothing overdue. Nice." End the skill. |
| 1-2 overdue tasks | Handle individually instead of batch grouping |
| 50+ overdue tasks | Group by project, suggest tackling one project at a time: "That's a lot. Want to start with [project with fewest]?" |
| All tasks in one project | Skip project grouping, list tasks directly |
| User wants to go task-by-task | Switch to individual mode -- present one at a time |
| Todoist MCP unavailable | Ask user to list overdue tasks manually, then coach through triage |
| User feels guilty about dropping | Extra warmth: "Dropping a task you won't do is more productive than carrying it around." |
| Chronic reschedulers (3+ times) | Flag but don't judge: "This one keeps coming back. Want to do it, drop it, or figure out why it's stuck?" |

## Cross-References

- Uses `coach-tone` with warmth bias
- Feeds into `/plan-week` -- triage cleans the backlog before scheduling
- `overdue-rescue` agent provides deeper pattern analysis on chronic reschedulers
- Complements `/weekly` -- triage is tactical (individual tasks), weekly is strategic (project focus)

## What This Skill Does NOT Do

- Write to Obsidian or create notes
- Create new tasks
- Judge why things slipped
- Lecture about planning or time management
- Require any specific setup or configuration
- Modify anything without explicit permission
