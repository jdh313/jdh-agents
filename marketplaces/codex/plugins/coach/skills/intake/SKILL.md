---
name: intake
description: >-
  This skill should be used when the user says "/intake", "new project", "start
  a project", "I want to build", "project kickoff", "add a project", or "I have
  an idea for a project". Structured new project onboarding with a WIP awareness
  check -- impulse control without gatekeeping. The opposite of /sunset: one
  opens projects, the other closes them. Sparks that graduate become intakes.
---

# /intake -- New Project Intake

Structured onboarding for a new project. Captures what it is, what done looks like, and the first concrete step. Includes a WIP awareness check -- not a blocker, just visibility into how many plates are already spinning. The opposite of `/sunset` -- one opens projects, the other closes them.

## Flow

Execute these steps in order. Use `coach-tone` at medium intensity. Keep it conversational, not a form.

### Step 1: Capture (1-2 Exchanges)

Three questions, asked conversationally (not as a numbered list):

1. **"What's the project?"** -- accept anything from a sentence to a paragraph
2. **"What does done look like?"** -- the definition of done in the user's words. Accept vague answers ("it works", "I can use it daily") without pushing for precision
3. **"What's the first concrete step?"** -- the single next action. If the user says something vague like "set it up", probe once: "What does 'set it up' actually mean -- creating a repo, installing something, sketching a design?"

These can flow naturally across 1-2 exchanges. Don't force the exact wording.

### Step 2: WIP Check (Silent + 1 Exchange)

Gather current active projects from available sources. Skip any unavailable silently.

**Linear** (if available):
- Query active projects (not paused/completed)
- Count and list names

**Obsidian** (if available):
- Search for project/hobby notes
- Cross-reference with `project-pulse` classification if data is available

Present the WIP count:

> "You have [N] active projects right now: [top 5 names]. Which one does this replace, or is this genuinely additive?"

Accept "it's additive" without pushback. The point is awareness, not gatekeeping.

If no sources are available, ask: "How many projects are you actively working on right now?" -- conversational WIP check.

### Step 3: Scope (1 Exchange)

Quick gut check on size:

> "Quick gut check: is this a weekend project, a month-long build, or an ongoing thing?"

Accept the answer. This sets expectations without requiring detailed planning. Use the answer to calibrate the project note structure.

### Step 4: Write Project Note (With Permission)

Honor the vault conventions in ~/Loose Ends/.claude/CLAUDE.md (frontmatter shape, naming, wikilink style) — read it before the first vault write of a session.

Once the conversation is complete, ask before writing:

> Want me to create a project note?

**If Obsidian MCP is available and user agrees:**
- Propose a path -- ask the user where project notes live, or suggest a reasonable location based on vault structure
- Content structure:
  ```
  # [Project Name]

  **Started:** YYYY-MM-DD
  **Scope:** [Weekend / Month / Ongoing]
  **Definition of Done:** [User's words]

  ## First Step
  - [The concrete first step]

  ## Notes
  - [Any context from the conversation]
  ```
- Ask the user to confirm the path before writing

**If Obsidian MCP is unavailable or user declines:**
- Display the project summary in chat
- No file operations

### Step 5: Offer Integrations (With Permission)

Optionally create external tracking:

**Linear** (if available):
> "Want me to create a Linear project for this?"
- If yes: create project with name, description from the conversation
- **After project creation succeeds**: If the conversation surfaced identifiable sub-tasks (from scope discussion, first steps, or breakdown), offer to create issues:
  > "Want me to create Linear issues for the tasks we discussed? ([list task names])"
  - If yes: create issues in the newly created project
  - Report created issue count and IDs
- **Icon setting**: Linear expects specific icon library names (e.g., "Radar", "Database", "Home"). If unsure of the exact name, skip icon setting rather than guessing -- user can set manually in Linear

**Todoist** (only for life-admin projects or tasks with hard external deadlines):
> "Want me to add the first step as a Todoist task?"
- Only offer this if the project is genuinely life-admin (e.g., "organize tax documents") or has a hard external deadline
- Most project first-steps should be Linear issues instead (created above)
- If yes: create task with the first concrete step, due date based on scope (weekend = this weekend, month = this week, ongoing = no date)

If neither is available, skip this step.

## Tone

Use `coach-tone` at **medium intensity**:

- Validate the excitement: "Cool, let's get this set up."
- WIP check is awareness, not judgment: "You're not adding to a pile, you're making a conscious choice."
- Don't cool the user's enthusiasm -- channel it into the first step
- If user seems to be impulse-starting: no judgment, but the WIP check provides natural friction

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| User is graduating a `/spark` | "Nice -- this started as a spark. Let's turn it into a real project." Reference the spark if the user mentions it |
| WIP count is very high (10+) | Extra awareness, not blocking: "That's [N] active projects. This one genuinely adding, or is it time to `/sunset` a couple first?" |
| User doesn't know what "done" looks like | Accept "I'll know it when I see it" -- not every project needs a crisp definition of done |
| User wants to intake multiple projects | Handle sequentially with progress tracking. Acknowledge batch upfront: "Got it -- [N] projects. I'll go through each one: [names]. Starting with [first]." Track progress: "Project 2 of N: [name]." At the end, provide summary: "All [N] projects set up: [list with Linear/Obsidian links]." |
| Project already exists in Linear/Obsidian | "Looks like [project] already exists. Want to update it instead, or is this a fresh start?" |
| User changes mind mid-conversation | "No problem. The idea's not going anywhere." Drop it |
| No data sources for WIP check | Ask conversationally: "How many projects are you juggling right now?" |

## Cross-References

- Opposite of `/sunset` -- one opens, one closes
- Graduates from `/spark` -- sparks that grow up become intakes
- Uses `project-pulse` classification pattern for WIP context
- Uses `coach-tone` at medium intensity
- First step feeds into `/today` or `/plan-week` for scheduling

## What This Skill Does NOT Do

- Block project creation or gatekeep
- Require detailed planning, timelines, or milestones
- Judge project worthiness or feasibility
- Create project infrastructure (repos, CI, etc.)
- Force the user to close other projects before starting
- Require any specific vault structure or configuration
- Write anything without explicit permission
