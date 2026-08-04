---
name: sunset
description: >-
  This skill should be used when the user says "/sunset", "close this project",
  "archive [project]", "I'm done with [project]", "sunset [project]", "I need to
  let go of [project]", or "shut down [project]". Guides intentional project
  closure with a structured conversation that captures restart context for
  future-you and reframes closing as a skill, not a failure.
---

# /sunset -- Intentional Project Closure

A guided conversation for intentionally closing a project. Captures why you're stopping, where things stand, and what future-you would need to pick it back up. The opposite of `/reentry` -- one opens projects, the other closes them. Closing projects is a skill, not a failure.

## Flow

Execute these steps in order. The conversation should feel warm and intentional -- use `coach-tone` with warmth bias throughout.

### Step 1: Identify Project (Silent/Interactive)

Determine which project the user wants to close:

- **If the user named a project:** Fuzzy-match against Linear project names and Obsidian note titles (search for project/hobby notes) -- same pattern as `/reentry`
- **If ambiguous or no match:** Ask: "Which project? I found these that might match:" and list candidates
- **If the user didn't name a project:** Show candidates from stale projects (22+ days since last activity -- Active: 0-7d, Drifting: 8-21d, Stale: 22+d) and ask: "Any of these ready to close?"
- **If no data sources:** Ask: "Which project are you closing?"

### Step 2: Gather Context (Silent)

Once the project is identified, gather everything available. Skip any source that is unavailable silently.

**Linear** (if available):
- Get the project details (status, description, progress)
- List open issues -- note count and any blockers
- Check for linked initiatives

**Obsidian** (if available):
- Read the project/hobby note
- Search `Journal/Weekly/` for recent mentions
- Search `Journal/Reviews/` for mentions in review notes
- Check modification date

If no sources are available, proceed with conversation only.

### Step 3: Closure Conversation (2-3 Exchanges)

This is the core of the skill. Ask these questions in order, one at a time:

**Exchange 1:**
> What made you decide to close this?

Accept the answer. Valid reasons include: lost interest, priorities shifted, it served its purpose, it's not worth the ongoing cost, or just "I don't want to anymore." All are fine. Acknowledge briefly.

**Exchange 2:**
> If future-you wanted to pick this back up in 6 months, what would they need to know?

This captures restart context -- the most valuable part of the closure note. Probe once if the answer is very sparse: "Anything about the technical state or decisions you'd want to remember?" But accept what you get.

**Exchange 3 (only if open items exist):**
> You have [N] open items. Want to:
> - Transfer them to another project
> - Note them in the closure record and let them go
> - Something else

If no open items, skip this exchange.

### Step 4: Write Closure Note (With Permission)

Honor the vault conventions in ~/Loose Ends/.claude/CLAUDE.md (frontmatter shape, naming, wikilink style) — read it before the first vault write of a session.

Once the conversation is complete, ask before writing:

> Want me to write a closure note?

**If Obsidian MCP is available and user agrees:**
- Propose path: `Journal/Sunsets/YYYY-MM-DD Sunset - [Project Name].md`
- Content structure:
  ```
  # Sunset: [Project Name]

  **Closed:** YYYY-MM-DD
  **Duration:** [First activity] to [Last activity] (approximate)
  **Status at close:** [Brief state summary]

  ## Why Closed
  - [User's stated reasons -- their words, not paraphrased]

  ## State When Closed
  - [Technical state, progress, what was working]
  - [Open items disposition if discussed]

  ## Restart Context
  - [What future-you needs to know to pick this back up]
  - [Key decisions that were made and why]
  - [Dependencies, accounts, environments to be aware of]

  ## Links
  - [Linear project link if available]
  - [Obsidian project note link if available]
  - [Any other relevant links]
  ```
- Ask the user to confirm or adjust the path before writing

**If Obsidian MCP is unavailable or user declines:**
- Display the closure summary in chat
- No file operations

### Step 5: Offer Linear Update (With Permission)

If Linear MCP is available and the project exists there:

> Want me to mark this as Paused in Linear?

- If yes: update project status to Paused
- **Never** archive or delete -- only Pause. The user can archive manually if they want
- If Linear is unavailable, skip this step

## Tone

Use `coach-tone` patterns with **warmth bias** throughout:

- Frame closure as intentional and positive: "Closing projects is a skill."
- Acknowledge the work that was done, not just what's left
- "Not abandoned -- intentionally closed" / "Parked with context, not forgotten"
- If the user expresses guilt about closing: "Having 20 open projects is harder than closing 5. This is you making space."
- Keep it warm but not saccharine -- brief acknowledgments, not eulogies

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| Project is very active (touched today) | "This project is pretty active. Sure you want to close it, or just park it for a bit?" |
| Project was already closed/archived | "Looks like this is already archived. Want to write a closure note anyway for the record?" |
| User wants to close multiple projects | Handle one at a time. After the first: "Want to sunset another?" |
| User is emotional about closing | Extra warmth. Acknowledge it: "It's okay to feel that. This project mattered to you." Then proceed. |
| No data sources available | Run the full conversation without project data -- focus on the user's knowledge |
| User changes mind mid-conversation | "No problem. It's still there when you're ready." Drop it. |

## Cross-References

- Complements `/reentry` -- opposite operation (one opens, one closes)
- Uses `project-pulse` classification pattern for identifying stale candidates
- Uses `coach-tone` with warmth bias
- Closure notes feed into `momentum` agent for pattern analysis

## What This Skill Does NOT Do

- Judge whether a project should be closed
- Archive or delete anything in Linear -- only Pause
- Delete notes, issues, or any data
- Pressure the user to close projects
- Require any specific vault structure or configuration
- Write anything without explicit permission
