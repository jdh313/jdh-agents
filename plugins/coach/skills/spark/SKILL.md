---
name: coach:spark
description: >-
  This skill should be used when the user says "/spark", "I had an idea", "I
  want to try", "what if I", "this looks cool", "new interest", "capture this
  idea", or "I'm curious about". Low-friction idea capture to a monthly sparks
  log -- validates the dopamine hit without committing to a project. Speed over
  structure. Sparks get reviewed during /weekly or /review for promotion to
  /intake.
allowed-tools:
  # Obsidian — read/create/append sparks log
  - Bash(obsidian *)
  - Edit
---

# /spark -- Interest/Idea Capture

A parking lot for the "ooh shiny" moment. Captures an idea or interest in under a minute to a monthly sparks log. Validates the dopamine hit without committing to a project. Speed over structure -- if this takes more than 60 seconds, it's too slow.

## Flow

Execute these steps in order. Minimal coaching -- capture only.

### Step 1: Capture (1 Exchange)

One question:

> "What caught your attention?"

Accept anything from a sentence to a paragraph. Don't probe for detail -- the point is speed. If the user already stated the idea in their message (e.g., "/spark I want to try building a Rust CLI"), skip this question and use what they said.

### Step 2: Tag (1 Exchange)

Suggest a category based on the content:

- `hobby` -- personal interests, creative pursuits
- `tool` -- utilities, scripts, developer tools
- `learning` -- courses, technologies, skills to explore
- `project-idea` -- potential builds, apps, services
- `business` -- monetization ideas, side hustles

Auto-suggest the best match: "I'd tag this as `[category]`. Sound right?"

Accept custom tags. Don't debate categories -- whatever the user picks is fine.

### Step 3: Write (With Permission)

Ask before writing:

> "Want me to add this to your sparks log?"

**If Obsidian MCP is available and user agrees:**
- Append to monthly sparks log at `Journal/Sparks/YYYY-MM Sparks.md`
- If the file doesn't exist, create it with a header: `# YYYY-MM Sparks`
- Append entry:
  ```
  ### YYYY-MM-DD: [One-line title]
  - **Category:** [tag]
  - [The idea in the user's words]
  ```
- Don't ask for path confirmation -- the location is standardized

**If Obsidian MCP is unavailable or user declines:**
- Display the captured spark in chat: "Captured. Here it is if you want to save it somewhere:"
- No file operations

After writing: **"Captured."** That's a valid complete response. No follow-up, no coaching, no "what's next?"

## Tone

Minimal. This is capture, not coaching.

- "Captured." is a complete response
- Don't evaluate the idea
- Don't suggest next steps unless asked
- Don't ask "do you want to start working on this?" -- that defeats the purpose
- Match the user's energy: if they're excited, a brief "Nice." is fine; if they're just parking something, keep it quiet

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| User wants to start the project now | "Sounds like this might be ready for `/intake` instead. Want to set it up as a project?" |
| Multiple sparks at once | Capture each one with its own entry, same exchange |
| Spark is very vague ("something with AI") | Capture as-is. Vague is fine -- the monthly review will filter naturally |
| User wants to see past sparks | Read and display the current month's sparks file (or specify which month) |
| Spark duplicates an existing one | Don't check for duplicates -- the monthly review handles dedup naturally |
| No Obsidian MCP | Display in chat, suggest the user save it somewhere |

## Cross-References

- Sparks that grow up become `/intake` projects
- Reviewed during `/weekly` and `/review` for promotion
- Monthly log format prevents file proliferation (unlike per-spark files)
- No connection to Todoist or Linear -- sparks are pre-commitment

## What This Skill Does NOT Do

- Evaluate or judge ideas
- Create projects, tasks, or commitments
- Add to Todoist or Linear
- Push for follow-up or next steps
- Require any specific vault structure or configuration
- Write anything without explicit permission
