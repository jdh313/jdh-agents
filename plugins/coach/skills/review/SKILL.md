---
name: coach:review
description: >-
  This skill should be used when the user says "/review", "monthly review",
  "quarterly review", "life review", "big picture check-in", "theme setting",
  "zoom out", "life direction", or "what am I doing with my life". Provides
  a structured life-direction review across career, health, home, hobbies,
  relationships, and learning — setting one theme and 1-2 projects for the
  next period.
allowed-tools:
  # Linear — project health, initiatives
  - mcp__linear-server__list_projects
  - mcp__linear-server__list_issues
  - mcp__linear-server__list_initiatives
  # Obsidian — reviews, project notes, write review
  - Bash(obsidian-cli *)
---

# /review — Life-Direction Review

A guided monthly or quarterly review that zooms out from daily tasks to life direction. Checks satisfaction across life areas, audits project alignment, and converges on ONE theme for the next period. Uses themes (direction) instead of goals (targets) — themes are more ADHD-compatible because partial progress still counts.

## Flow

Execute these steps in order. The conversation should feel reflective, not interrogative.

### Step 1: Determine Review Period

Before diving in, establish scope:

**Search for prior reviews** (Obsidian, if available):
- Search `Journal/Reviews/` for the most recent review note
- If found, note the date and stated theme

**Determine cadence:**
- If last review was 3+ months ago (or none found): suggest quarterly review
- If last review was 1-3 months ago: suggest monthly check-in
- Ask: "Monthly check-in or bigger quarterly review?" Let the user decide.

If no data sources are available, ask the user when they last did a review and proceed.

### Step 2: Life Areas Check-In

Walk through each life area from the `life-areas` reference. For each area:

Present all 6 areas at once and ask the user to rate satisfaction 1-5:

> Quick pulse check across your life areas. Rate each 1-5 (1 = needs attention, 5 = thriving):
>
> - **Career** — work, professional growth, income
> - **Health** — physical, mental, energy, sleep
> - **Home & Infra** — living space, homelab, systems
> - **Hobbies** — creative and hands-on projects
> - **Relationships** — family, friends, community
> - **Learning** — skills, curiosity, growth areas

Accept the ratings without judgment. Note any area rated 1-2 — these are candidates for theme attention. Do not prescribe actions yet.

### Step 3: Initiative & Project Audit

Surface the project landscape:

**Data gathering** (using `project-pulse` pattern):
- Linear: list initiatives + projects, classify by activity
- Obsidian: search for project/hobby notes, check modification dates
- Classify each as active/drifting/stale

**Present the audit:**
- Group projects by life area where possible
- Show status (active/drifting/stale) for each
- If a prior review set a theme: "Last time, your theme was '[X]'. Here's how projects aligned with that:"

**Compare plan to reality:**
- Which life areas got the most project attention?
- Which areas with low satisfaction ratings have no active projects?
- Any projects running that don't connect to a life area?

Ask: **"Any surprises here?"** One exchange to discuss.

### Step 4: Set Next Theme

Guide toward ONE theme for the next period. A theme is a direction, not a measurable goal:

- **Good themes:** "Stability", "Deep work", "Health foundations", "Ship things", "Simplify"
- **Bad themes:** "Lose 20 pounds", "Launch 3 products", "Read 50 books" (these are goals, not themes)

Based on the life-area ratings and project audit:
- Suggest 2-3 candidate themes that connect low-rated areas to available projects
- Ask: **"Which theme resonates?"**

Once a theme is chosen:
- Identify 1-2 projects that serve the theme
- Everything else gets explicitly parked for this period
- Push back if the user picks more than 2 projects — use `coach-tone` calibration

Frame it: "Your theme is [X]. These 1-2 projects serve it. Everything else is parked — not abandoned, just not now."

### Step 5: Write Review Note (With Permission)

Once the review is complete, ask before writing:

> Want me to save this review?

**If Obsidian MCP is available and user agrees:**
- Propose path: `Journal/Reviews/YYYY-MM Review.md` (e.g., `Journal/Reviews/2026-02 Review.md`)
- For quarterly reviews: `Journal/Reviews/YYYY-QN Review.md` (e.g., `Journal/Reviews/2026-Q1 Review.md`)
- Content structure:
  ```
  # YYYY-MM Review

  ## Life Areas
  | Area | Rating | Notes |
  |------|--------|-------|
  | Career | N | ... |
  | Health | N | ... |
  | ... | | |

  ## Theme
  **[Theme name]** — [one-line description]

  ## Focus Projects
  - Project 1: connection to theme
  - Project 2: connection to theme

  ## Parked
  - Parked project list

  ## Reflections
  - [Key insights from the conversation]
  ```
- Ask the user to confirm or adjust the path before writing

**If Obsidian MCP is unavailable or user declines:**
- Display the summary in chat
- No file operations

### Cross-References

- Use `project-pulse` data-gathering pattern for project classification
- Use `coach-tone` for coaching calibration throughout
- Reference `life-areas` for the area definitions and rating scale
- At the end, suggest: "Use `/weekly` to keep this focus on track week-to-week"

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| First review ever | No comparison to prior review. Frame as: "Let's set a baseline" |
| All life areas rated high | "Nice. Anything you want to push further or are you in maintenance mode?" |
| All life areas rated low | No alarm. "Sounds like a reset period. What ONE area would make the biggest difference?" |
| User wants multiple themes | Push back: "Themes work best as a single lens. Which one would help the most right now?" Allow 2 only if user insists |
| Review done recently (<2 weeks ago) | "You did a review recently. Want to check progress against your theme, or start fresh?" |
| No data sources available | Run the full conversation without project data — focus on life areas and theme setting |

## What This Skill Does NOT Do

- Set measurable goals or KPIs
- Create tasks, issues, or calendar events
- Prescribe specific actions or habits
- Judge gaps between reviews
- Require any specific vault structure or configuration
- Write anything without explicit permission
