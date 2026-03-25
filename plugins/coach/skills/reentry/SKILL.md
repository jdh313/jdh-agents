---
name: coach:reentry
description: >-
  This skill should be used when the user says "/reentry", "help me get
  back into [project]", "where did I leave off", "catch me up on [project]",
  "what was I doing on [project]", "resume [project]", or "context dump
  for [project]". Gathers context from Linear and Obsidian to create a
  structured briefing for returning to a paused or dormant project.
allowed-tools:
  # Linear — project details and issues
  - mcp__linear-server__get_project
  - mcp__linear-server__list_issues
  # Obsidian — project notes
  - Bash(obsidian read *)
  - Bash(obsidian search *)
---

# /reentry — Project Re-Entry Briefing

A structured context dump for returning to a project you haven't touched in a while. Gathers what it can from Linear and Obsidian, presents where you left off, and identifies the single next step to get moving again. Standalone — no dependencies on other coaching skills.

## Flow

Execute these steps in order. Steps 1 and 2 are silent — the user sees only the briefing.

### Step 1: Identify Project (Silent)

Determine which project the user wants to re-enter:

- **If the user named a project:** Fuzzy-match against Linear project names and Obsidian note titles (search for project/hobby notes)
- **If ambiguous or no match:** Ask: "Which project? I found these that might match:" and list candidates
- **If the user didn't name a project:** Ask: "Which project do you want to get back into?"

### Step 2: Gather Context (Silent)

Once the project is identified, gather everything available. Skip any source that is unavailable silently.

**Linear** (if available):
- Get the project details (status, description)
- List recent issues — note which are open, in progress, or done
- Identify the most recently updated issue

**Obsidian** (if available):
- Read the project/hobby note
- Check modification date
- Look for any related notes (search by project name)

### Step 3: Present Briefing

Present a structured briefing — concise, scannable, no fluff:

```markdown
## Re-Entry: [Project Name]

**Last active:** YYYY-MM-DD (NN days ago)
**Source:** Linear / Obsidian / both

### Where You Left Off
- [2-3 bullets summarizing the last known state]
- [Most recent work or decisions]
- [Any open threads or blockers noted]

### Open Items
- [Open issues/tasks, grouped if many]

### Next Step
→ [Single concrete action to resume work]
```

Adapt the sections based on available data:
- If only Linear data: focus on issue status and recent activity
- If only Obsidian data: focus on note content and modification dates
- If both: merge into a unified picture
- If neither source is available: tell the user you couldn't find data and ask them to describe where they left off

### Step 4: Offer to Continue

After the briefing, ask:

> Want to dive into [next step] now?

If the user agrees, transition into working on that next step normally. If they want to do something else, let it go — no pressure.

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| Project not found in any source | "I couldn't find a project matching '[name]'. Can you point me to it?" |
| Multiple close matches | Present the top 2-3 matches and ask which one |
| Project is very active (touched today) | Still present the briefing — user may want context even on active work |
| Project has no open items | Note it: "No open items found. What's the next thing you want to tackle?" |
| No data sources available | "I need Linear or Obsidian MCP servers to pull project context. Tell me what you remember and I'll help you get started." |

## What This Skill Does NOT Do

- Judge how long the project has been inactive
- Suggest whether the project is worth continuing
- Create tasks, issues, or notes
- Reference other coaching skills or suggest reviews
- Require any specific vault structure or configuration
