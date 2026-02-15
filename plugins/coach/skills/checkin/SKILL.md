---
name: checkin
description: >-
  This skill should be used when the user says "/checkin", "end of day",
  "how did today go", "daily reflection", "what did I get done", "wrap up
  my day", or "day's over". Provides a quick end-of-day pulse that reads
  the morning's priorities, captures what actually happened, and writes a
  brief end-of-day section to the daily note.
---

# /checkin -- End-of-Day Pulse

A short end-of-day bookend to `/today`. Reads the morning's stated priorities, compares them to what actually happened, and captures the delta. Intentionally brief -- EOD energy is low. This is capture, not coaching.

## Flow

Execute these steps in order. The whole interaction should take 2-3 minutes.

### Step 1: Gather Context (Silent)

Before displaying anything to the user, attempt to gather today's context. Skip any source that is unavailable -- do not error or mention missing sources.

**Obsidian** (if available):
- Read today's daily note
- Look for a `## Today's Focus` section (written by `/today`)
- Extract the stated priorities

**Todoist** (if available):
- Query tasks completed today

**Linear** (if available):
- Query issues updated today by the user

If no sources are available, skip to Step 2 with no data.

### Step 2: Reflect (1 Exchange)

This is the only question you ask. Adapt based on what you found:

**If priorities were found:**
> You set [X, Y, Z] this morning. Here's what I can see happened: [data summary]. How does that feel?

**If data but no stated priorities:**
> Based on what I can see, you worked on [data summary]. Anything else that got your time today?

**If no data at all:**
> What actually got your time today?

Accept the answer. Do not push back, probe deeper, or coach. One question, one answer. If the user's response is emotional (frustration, guilt, excitement), respond with brief warmth per `coach-tone` low-energy patterns -- then move on. Do not extend the conversation.

### Step 3: Write End-of-Day (With Permission)

Once you have the user's response, ask before writing:

> Want me to add an end-of-day note?

**If Obsidian MCP is available and user agrees:**
- Append to today's daily note under a `## End of Day` heading
- Content structure:
  ```
  ## End of Day

  ### Done
  - [What got accomplished -- bullets]

  ### Drifted
  - [What shifted from the plan, if anything]

  ### Energy
  - [One-line energy/mood note from the user's response]
  ```
- If the heading already exists, replace its contents
- Keep it terse -- bullets only, no commentary

**If Obsidian MCP is unavailable or user declines:**
- Display the summary in chat
- No file operations

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| No `/today` was run this morning | Skip priority comparison, ask "What got your time today?" |
| Run in the morning | "End-of-day check-in before the day starts? Want to do `/today` instead?" |
| Nothing got done | No guilt. Capture it neutrally: "Rest days count." |
| User gives a one-word answer | Accept it. Write what you have. Don't fish for more. |
| Run twice in same day | "You already checked in. Want to update it?" |
| User wants to vent | Listen briefly, acknowledge, then offer to capture the key points. Do not therapize. |

## Cross-References

- Bookends with `/today` -- one opens the day, one closes it
- Uses `coach-tone` at low-energy intensity
- End-of-day notes feed into `momentum` agent for drift analysis (stated vs. actual)

## What This Skill Does NOT Do

- Coach, advise, or prescribe next actions
- Judge the gap between plan and reality
- Extend the conversation beyond 1-2 exchanges
- Create tasks, issues, or calendar events
- Lecture about consistency or habits
- Require any specific vault structure or configuration
- Write anything without explicit permission
