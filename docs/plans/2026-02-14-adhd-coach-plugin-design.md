# ADHD Coach Plugin — Design Document

**Date:** 2026-02-14
**Status:** Approved
**Plugin path:** `plugins/adhd-coach/`
**Approach:** Skill + Output Style (lightest viable)

## Overview

A Claude Code plugin providing ADHD-friendly productivity coaching through a `/today` skill and an adaptive coach output style. Zero-config, graceful degradation when MCP servers aren't available.

## Design Principles (ADHD-Specific)

1. **Single entry point** — One command (`/today`), not multiple to choose from
2. **Gentle re-entry** — No guilt for missed days; neutral acknowledgment of gaps
3. **Constraint over options** — "Pick your top 3" beats "here are your 47 tasks"
4. **Forgiveness built in** — Inconsistency is the default, not failure
5. **Low friction** — Minimize decisions to start using the system
6. **Conversation > artifact** — The coached thinking matters more than the written list

## Plugin Structure

```
plugins/adhd-coach/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── today.md              # /today — morning coaching conversation
│   └── weekly.md             # /weekly — weekly review (future, not v1)
├── output-styles/
│   └── coach.md              # Adaptive productivity coach persona
└── README.md
```

No hooks, no agents, no required configuration.

## Data Sources (All Optional, Detected at Runtime)

| Source | What It Provides | If Unavailable |
|--------|-----------------|----------------|
| Todoist MCP | Today's tasks + overdue items | Skip |
| Linear MCP | Assigned issues in current cycle | Skip |
| Obsidian MCP | Yesterday's daily note / carry-forward priorities | Skip |
| None available | Pure conversation — asks what you're working on | Works fine |

## `/today` Skill Flow

### Step 1: Gather Context (Silent)

Query available MCP servers for tasks, issues, yesterday's priorities. Skip any unavailable source gracefully.

### Step 2: Energy Check-In (First Thing User Sees)

One open-ended question: "How's your energy/headspace right now?"

Free-form response, not multiple choice. Coach calibrates tone from the answer:

- **Low energy** → Gentle mirror, smaller asks
- **Medium** → Balanced, contextual nudges
- **High energy** → Direct, challenge to aim bigger

### Step 3: Coached Conversation (2-4 Exchanges)

- Surface what data sources show (overdue tasks, sprint items, yesterday's priorities)
- Ask: "What feels most important today?" (not "most urgent")
- Push back based on tone calibration:
  - Too many items → constrain
  - Too few → probe
  - Misaligned with prior priorities → question
- Converge on ~3 priorities

### Step 4: Write Priorities (With Permission)

- Append to today's daily note under `## Today's Focus`
- Simple bullet list
- If no Obsidian MCP, display in chat only

### Step 5: Activate Coach Context

- Coach context (energy level, priorities) stays in session memory
- Responds to coaching questions; normal Claude behavior for everything else

### What `/today` Does NOT Do

- Assign time blocks
- Create Todoist tasks or move Linear issues
- Lecture about productivity
- Require any specific setup

## Coach Output Style

### Personality

- Concise, not chatty (lists > prose)
- Warm but not performative — no "Great job!" but acknowledges real progress naturally
- Adapts tone based on energy check-in

### Tone Calibration

| Energy | Style | Example |
|--------|-------|---------|
| Low | Gentle, reduced scope | "Just one thing. What's the smallest step that would feel like a win?" |
| Medium | Balanced, contextual | "You've got 3 priorities. Which one are you pulling first?" |
| High | Direct, challenging | "You're sharp today. What's the hard thing you've been avoiding?" |

### Coaching Responses (Only When Asked)

| User Says | Coach Response Pattern |
|-----------|----------------------|
| "What should I do next?" | References priorities, suggests the next one |
| "I'm stuck" | One diagnostic question, not a prescription |
| "I got distracted" | No judgment. "What were you doing? Ready to come back to X?" |
| "How's my day going?" | Quick status against the 3 priorities |

### Scope

- Only activates for coaching-type questions
- Normal Claude behavior for code, research, etc.
- Does NOT interrupt, nudge, or monitor proactively

### Deactivation

- End of session (natural)
- User says "stop coaching" or switches output style

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| No MCP servers available | Pure conversation — asks what you're working on |
| `/today` run twice | "You already set priorities — want to revise or start fresh?" |
| Gap of several days | No guilt. Neutrally: "Last time you focused on X, Y, Z" |
| Run at 4pm | "Late start or afternoon reset?" — adjusts scope |
| "Stop coaching" | Drops context, returns to normal |

## Future Expansion (Not in V1)

- **`/weekly` skill** — Reads the week's daily notes, reflection conversation
- **Coaching notes** (Approach 2 upgrade) — Folder for pattern tracking over time
- **Calendar integration** — Surface meeting load for day planning

## Non-Goals

- No goal cascade / hierarchy system
- No time tracking or pomodoro
- No gamification or streaks
- No required vault structure or configuration
