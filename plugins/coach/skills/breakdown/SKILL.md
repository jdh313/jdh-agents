---
name: coach:breakdown
description: >-
  This skill should be used when the user says "/breakdown", "break this down",
  "decompose [project]", "what are the tasks for [project]", "help me plan
  [project]", "this project feels overwhelming", "I don't know where to start",
  "task list for [project]", or "reconcile tasks on [project]". Conversational
  project decomposition into ADHD-friendly, sequenced Linear issues. Auto-detects
  whether to decompose from scratch or recompose drifted existing tasks.
allowed-tools:
  # Linear — find project, read/create/update issues
  - mcp__linear-server__list_projects
  - mcp__linear-server__get_project
  - mcp__linear-server__list_issues
  - mcp__linear-server__create_issue
  - mcp__linear-server__update_issue
  # Obsidian — find and update project notes
  - Bash(obsidian *)
  - Edit
  # Interactive
  - AskUserQuestion
---

# /breakdown -- Project Task Decomposition

Conversational decomposition of a project into workable tasks. Takes a project -- new or in-flight -- and produces a sequenced, ADHD-friendly task list in Linear through coached dialogue. Auto-detects two modes: **decompose** (no tasks yet, break down from scratch) or **recompose** (existing Linear issues that have drifted, reconcile and reorder).

## Flow

Execute these steps in order. Use `coach-tone` at medium intensity. The conversation should feel like working through a whiteboard together, not filling out a form.

### Step 1: Gather Context (Silent)

Before saying anything, pull everything available. Skip any unavailable source silently.

**Identify the project:**
- **If the user named a project:** Fuzzy-match against Linear project names and Obsidian note titles
- **If ambiguous or no match:** Ask: "Which project? I found these that might match:" and list candidates
- **If the user didn't name a project:** Ask: "Which project do you want to break down?"

**Linear** (if available):
- `list_projects` to find the project
- `get_project` for details (status, description, progress)
- `list_issues` for existing issues -- note count, status, assignees

**Obsidian** (if available):
- `search_notes` for the project/hobby note
- `read_note` for context, goals, scope, and any existing task lists

**Mode detection:**
- If the project has **0 open Linear issues** → **Decompose mode**
- If the project has **1+ open Linear issues** → **Recompose mode**
- If no Linear project exists → **Decompose mode** (offer to create the project in Step 4)

### Step 2: Orient (1-2 Exchanges)

Present what you found and calibrate the conversation.

**Decompose mode:**
> "Here's what I know about [project]: [2-3 bullets from Obsidian/Linear]. What's the current state -- what's done, what's next?"

If the project is greenfield with no prior context:
> "Starting from scratch. What are you building and what does done look like?"

**Recompose mode:**
> "You have [N] open issues on [project]:
> - [Issue A] -- [status]
> - [Issue B] -- [status]
> - [Issue C] -- [status]
>
> Still accurate, or has the plan shifted?"

Accept brief answers. The point is to sync on reality before decomposing. If the user says "it's all wrong," treat the rest as decompose mode and handle existing issues in Step 4 (close/update stale ones).

### Step 3: Breakdown (2-4 Exchanges)

This is the core of the skill. Work through the project conversationally, producing a task list together.

**Approach:**
1. Ask what the major pieces are: "What are the big chunks of work?"
2. For each chunk, probe once for subtasks: "What does [chunk] actually involve?"
3. Sequence the tasks: suggest an order, ask if it feels right
4. Identify the first task explicitly: "So [task] is the entry point?"

**Apply ADHD principles silently** (see section below). Don't announce them -- just shape the tasks accordingly.

**In recompose mode**, reconcile as you go:
- Map existing issues to the new breakdown
- Flag stale issues: "Is [issue] still relevant, or can we close it?"
- Identify gaps: "You have [X] and [Z] but nothing for [Y] -- should we add one?"

**Present the final list** before writing:
```
Here's the breakdown:

1. [Task title] (~30min) -- [done criteria]
2. [Task title] (~1hr) -- [done criteria]
3. [Task title] (~2hr) -- [done criteria]
...

Does this look right, or want to adjust anything?
```

### Step 4: Write (With Permission)

Once the user approves the task list, ask before writing:

> "Want me to create these as Linear issues?"

**If Linear MCP is available and user agrees:**
- Create issues with:
  - Title from the task list
  - Description including done criteria and size estimate
  - Correct project assignment
  - Sequential ordering (use issue order if supported, otherwise number prefixes)
- In recompose mode: also update or close stale issues per the conversation
- Report what was created/updated: "[N] issues created, [N] updated, [N] closed"

**If no Linear project exists:**
> "There's no Linear project for this yet. Want me to create one?"
- If yes: create the project first, then create issues under it

**If Linear MCP is unavailable or user declines:**
- Display the complete task list in chat for manual entry
- No API operations

**Obsidian update** (if available and project note exists):
> "Want me to update the project note with this breakdown?"
- If yes: patch the note with a `## Tasks` or `## Breakdown` section containing the task list
- If no project note exists, don't offer to create one -- that's `/intake`'s job

## ADHD Principles

These are applied silently during Step 3. They shape how you decompose -- they are not explained or lectured about.

| Principle | What the coach does |
|-----------|---------------------|
| **Right-sized chunks** | Target 30min-2hr per task. If something is bigger, probe: "What's the first half of that?" |
| **Sequential by default** | Order tasks so each one has a single predecessor. Only mark tasks as parallel when genuinely independent |
| **Quick wins first** | Front-load small, concrete tasks for momentum. "What's the easiest piece?" |
| **Clear done criteria** | Every task has a one-line "done when..." statement. If the user gives a vague task, probe once: "How would you know [task] is done?" |
| **Vague tasks get one probe** | Ask once for clarity. If still vague, accept it and move on -- perfectionism kills momentum |
| **Anti-spiral** | If decomposition exceeds 6 exchanges or the user starts second-guessing the breakdown: "Good enough -- let's go with this and adjust later." |
| **No meta-work** | If the user starts planning how to plan, redirect: "Let's just list the actual work." |

## Task Format

Each task in the final list follows this structure:

```
**Title:** [Verb] [object] -- imperative, specific
**Size:** ~[30min / 1hr / 2hr / half-day]
**Done when:** [One sentence -- observable outcome]
**Depends on:** [Previous task number, or "none"]
```

When creating Linear issues, the title becomes the issue title and the rest goes in the description.

## Tone

Use `coach-tone` at **medium intensity**:

- "Let's break this into pieces" -- collaborative, not prescriptive
- If the project feels overwhelming: "We don't need to get this perfect. What are the obvious pieces?"
- If the user over-scopes: "That's a lot. What's the version that ships first?"
- During recompose: "Plans drift -- that's normal. Let's get this back in shape."
- After writing: "There's your list. First one's [task] -- you could start that now if you want." (offer, don't push)

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| No project found in Linear or Obsidian | Ask what the project is, treat as greenfield decompose |
| Project in Obsidian but not Linear | Read Obsidian note for context, offer to create Linear project in Step 4 |
| All tasks already completed | "Looks like everything's done. Is there a next phase, or is this one wrapped up?" |
| User wants to decompose mid-conversation | Accept -- skip straight to Step 3 with whatever context is available |
| Decomposition spiraling (>6 exchanges in Step 3) | "Good enough -- let's go with this and adjust later." Present what you have |
| Task too big but user insists | Accept it, note the size estimate honestly, move on |
| Multiple projects mentioned | Handle one at a time: "Let's finish [first] and then do [second]." |
| User already has a clear task list | Validate and offer to enter it: "Sounds like you've already got it. Want me to put these in Linear?" |
| Very large project (20+ tasks) | Group into phases: "That's a big list. Want to break it into phases and just detail phase 1?" |
| User wants to reprioritize, not decompose | Reorder existing issues: "Same tasks, different order? Let me pull what you have." |

## Cross-References

- Graduates from `/spark` → `/intake` → `/breakdown` -- the project lifecycle
- Feeds into `/today` and `/plan-week` for scheduling the created tasks
- Uses `project-pulse` classification if available for project context
- Reconciliation aspect overlaps with `/triage` (but `/triage` is Todoist-focused, `/breakdown` is Linear-focused)
- Opposite lifecycle direction from `/sunset`
- `/reentry` gathers context for returning; `/breakdown` structures what to do next

## What This Skill Does NOT Do

- Schedule work (that's `/today` and `/plan-week`)
- Create the project itself from scratch (that's `/intake` -- though it will create a Linear project if needed for task assignment)
- Coach on priorities across projects (that's `/align`)
- Touch Todoist -- tasks go to Linear
- Lecture about ADHD strategies or time management
- Block on missing data sources -- degrades gracefully to conversation-only
- Delete issues -- only close or update
- Write anything without explicit permission
