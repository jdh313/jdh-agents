---
name: coach:dump
description: >-
  This skill should be used when the user says "/dump", "brain dump", "I need to
  get everything out of my head", "what's on my mind", "mental clutter", "dump
  my thoughts", "clear my head", "everything is swirling", or "I'm overwhelmed
  with stuff to do". Unstructured multi-item brain purge with optional
  categorization and routing to the right places -- Todoist tasks, sparks, intake
  candidates, decisions. Pressure-release valve for ADHD mental overload.
allowed-tools:
  # Todoist — life-admin tasks and hard-deadline items
  - mcp__claude_ai_Todoist__add-tasks
  # Linear — project-related tasks as issues
  - mcp__linear-server__list_projects
  - mcp__linear-server__create_issue
  # Obsidian — read/create/append sparks log
  - Bash(obsidian-cli *)
  - Edit
---

# /dump -- Brain Dump

Get everything out of your head, then optionally sort it. A pressure-release valve for when there's too much swirling around. The goal is emptying, not organizing -- organization is optional and comes after.

## Flow

Execute these steps in order. Use `coach-tone` with warmth bias. Speed matters -- don't slow them down during the dump.

### Step 1: Dump (1-2 Exchanges)

**If user provides content in command args** (e.g., `/dump I need to: fix X, deploy Y, clean Z`): Treat as completed dump. Skip directly to Step 2 (mirror back).

**Otherwise**, one prompt:

> "Go. Everything that's on your mind -- tasks, worries, ideas, half-thoughts, whatever. No order needed."

Accept everything. Don't interrupt, clarify, or organize during the dump. If the user sends a wall of text, that's working as intended. If they send a short list, that's fine too.

If the dump seems incomplete, one gentle probe:

> "Anything else rattling around, or is that everything?"

Accept "that's it" immediately. Don't push for more.

### Step 2: Mirror Back (1 Exchange)

Read through everything and parse it into a numbered list. Don't categorize yet -- just extract individual items from the stream of consciousness.

Present the list back:

```
Here's what I heard ([N] items):

1. [Item]
2. [Item]
3. [Item]
...
```

Then ask: **"Anything missing, or does that capture it?"**

Let the user add, remove, or correct. The point is ensuring nothing got lost in translation.

### Step 3: Categorize (1 Exchange)

Suggest a category for each item:

- **Task (life-admin)** -- something to do with a hard deadline or life-admin nature (routes to Todoist)
- **Task (project)** -- something to do that belongs to a project (routes to Linear as issue)
- **Spark** -- an idea or interest to park (routes to `/spark`)
- **Project** -- something big enough to be its own project (routes to `/intake`)
- **Decision** -- something to decide (routes to `/decide`)
- **Noise** -- a worry or thought with no action -- acknowledged and released

Present the categorized list:

```
Here's how I'd sort these:

**Tasks**
1. [Item] -- task
4. [Item] -- task

**Sparks**
3. [Item] -- idea to park

**Projects**
6. [Item] -- big enough for its own project

**Noise** (no action needed -- just getting it out)
2. [Item]
5. [Item]
```

Then ask: **"Want me to adjust any of these, or does this sorting feel right?"**

Accept corrections. Don't argue categories -- if the user says something is noise, it's noise.

### Step 4: Route (With Permission)

Once categories are confirmed, offer to route items to their destinations. Handle each category:

**Tasks → route by type** (see `data-queries.md` routing convention):

*Life-admin or hard-deadline tasks → Todoist* (if available):
> "Want me to add the [N] life-admin tasks to Todoist?"
- If yes: use `add-tasks` to create each task. Ask about project/due date only if there are 3+ tasks -- otherwise just add them to inbox

*Project-related tasks → Linear* (if available):
> "[N] of these belong to projects. Want me to create Linear issues for them?"
- If yes: find or confirm the target project, then create issues
- If a task clearly belongs to an existing Linear project, route it there
- If the project doesn't exist yet, flag for `/intake` instead

- If neither service is available or user declines: display the task list for manual entry

**Sparks → Sparks log** (if Obsidian available):
> "Want me to capture the [N] sparks?"
- If yes: append each to the monthly sparks log at `Journal/Sparks/YYYY-MM Sparks.md` (same format as `/spark`)
- If no: display for manual capture

**Projects → flag for `/intake`:**
> "[Item] sounds like a project. Want to run `/intake` for it after we're done here?"
- Don't run `/intake` inline -- just flag it for after the dump is complete
- If multiple projects: note them all, suggest tackling one at a time later

**Decisions → flag for `/decide`:**
> "[Item] sounds like a decision to make. Want to run `/decide` for it later?"
- Same as projects -- flag, don't inline

**Noise → acknowledge and release:**
> "[N] things were just noise -- acknowledged and released. They don't need a home."

Report what was routed: "[N] tasks added to Todoist, [N] sparks captured, [N] items flagged for follow-up."

## Tone

Use `coach-tone` with **warmth bias**:

- "Getting it out of your head is the hardest part. You just did it."
- "Not everything needs a home. Some things just needed to be said."
- "Your brain isn't a filing cabinet -- let's get this stuff out of it."
- During the dump: stay quiet. Don't coach, don't react, don't organize. Just receive.
- After routing: "That's [N] fewer things living rent-free in your head."

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| Very short dump (1-3 items) | Skip the numbered mirror-back, work with items directly |
| Very long dump (20+ items) | Mirror back, then suggest tackling the top 5 for routing: "That's a lot. Want to route the most urgent 5 and park the rest?" |
| Everything is noise | "Sounds like you just needed to vent. That's valid. Nothing needs to happen here." |
| Everything is tasks | Skip spark/project/decision categories, go straight to routing -- still split by life-admin (Todoist) vs project-related (Linear) |
| User doesn't want to categorize | Skip Step 3 entirely: "No problem. It's out of your head -- that's the win." |
| User is emotional/overwhelmed | Extra warmth. Slow down. "Take your time. There's no rush." |
| No MCP servers available | Display categorized items in chat for manual routing |
| User wants to dump again in same session | "Round two? Go for it." No judgment about needing to dump multiple times |

## Cross-References

- Routes to `/spark` for ideas, `/intake` for projects, `/decide` for decisions
- Tasks route to Todoist (same integration as `/triage` and `/plan-week`)
- Uses `coach-tone` with warmth bias
- Complements `/today` -- dump clears the clutter, `/today` focuses the priorities
- Complements `/triage` -- dump captures new items, `/triage` cleans overdue ones

## What This Skill Does NOT Do

- Judge or evaluate what's dumped
- Force categorization or routing (both are optional)
- Run `/intake` or `/decide` inline (flags for follow-up only)
- Limit what can be dumped (tasks, feelings, worries, random thoughts -- all valid)
- Require any specific setup or configuration
- Write anything without explicit permission
