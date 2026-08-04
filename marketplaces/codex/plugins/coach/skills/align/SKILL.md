---
name: align
description: >-
  This skill should be used when the user says "/align", "which projects serve
  my goals", "what should I focus on to learn [X]", "align my projects", "goal
  to project mapping", "which of my projects help with [X]", "what existing
  projects support [goal]", "am I working on the right things", or "focus my
  projects on [goal]". Scans Linear projects and Obsidian project/hobby notes to
  map existing work to a stated goal, recommending focus order and identifying
  gaps.
---

# /align — Goal-to-Project Mapping

Maps a stated goal or direction to existing projects, recommending focus order instead of starting something new. The forward-looking complement to `/review` — where `/review` sets a theme, `/align` operationalizes it by scanning what you already have.

Steers toward existing work before suggesting new projects. ADHD brains love the dopamine of starting fresh — this skill channels that energy into finishing what's already in motion.

## Flow

Execute these steps in order. The conversation should feel strategic, not judgmental.

### Step 1: Capture Goal

Ask: **"What's the goal or direction you're trying to move toward?"**

- Accept anything from specific ("learn web dev") to broad ("ship something")
- If the goal is too vague ("be better"), probe once: "Better at what specifically?" If still vague, work with it

**Check for existing theme** (Obsidian, if available):
- Search `Journal/Reviews/` for the most recent review note
- If found and it has a theme, offer it: "Your last theme was '[X]'. Working from that, or something different?"
- If the goal matches the current theme, reinforce: "This aligns with your current theme. Let's see how your projects map to it."

One exchange — capture and move on.

### Step 2: Scan Existing Projects (Silent)

Gather project data without user interaction. Use `data-queries.md` patterns for graceful degradation — if a source is unavailable, skip silently.

**Linear:**
- `list_projects` — get all projects with names, descriptions, status
- `list_initiatives` — get initiatives for broader context
- For promising matches, `get_project` to read full descriptions and tech stacks

**Obsidian:**
- `list_directory` for `Hobbies/Hobby Catalog/` — get hobby list
- `search_notes` for `Personal/Projects/` — get project notes
- Read relevant notes to understand what each involves (tech stack, domain, status)

Build a working list of all projects and hobbies with: name, description/domain, tech stack (if known), current status.

### Step 3: Map Alignment

Classify each project/hobby against the stated goal:

- **Direct** — clearly serves the goal (e.g., Glory Days → "learn web dev" because it's FastAPI + SvelteKit)
- **Partial** — touches the goal tangentially (e.g., Packing Pal → "learn web dev" has a Django backend but is already functional)
- **Unrelated** — doesn't serve this goal

Present the alignment map:

```
## Alignment Map: [Goal]

### Directly Serves
| Project | Why | Status | Next Step |
|---------|-----|--------|-----------|

### Partially Serves
| Project | Connection | Gap |
|---------|-----------|-----|

### Unrelated (N projects)
[One-line list — don't clutter the map with these]
```

Ask: **"Any surprises? Anything I'm missing?"** — one exchange to discuss and adjust classifications.

### Step 4: Recommend Focus Order

From the "Directly Serves" list, recommend an order based on:

1. **Closest to shippable** — momentum matters more than perfect fit
2. **Current status** — favor In Progress over Backlog (less re-entry cost)
3. **Learning surface** — which teaches the most for the stated goal

Frame the recommendation:
- **Multiple matches:** "I'd start with [X] because [reason]. Then [Y] once [X] ships."
- **Single match:** "Only one project lines up — [X]. Want to double down on it, or explore extending another?"
- **User wants to start something new:** Push back: "Before starting fresh, could [existing project] be extended to cover that?"

### Step 5: Identify Gaps & Next Steps

Note aspects of the goal not covered by any existing project.

**If gaps exist:**
- Suggest extending an existing project first
- Only suggest `/intake` if no existing project can reasonably cover the gap

**Offer follow-through:**
- Suggest: "Use `/plan-week` to schedule time on [recommended project] this week"
- If the goal came from `/review`, note: "This reinforces your current theme — keep it rolling"

## Tone

Use `coach-tone` at **medium intensity**:

- Strategic, not judgmental: "Let's see what already serves this."
- Steer toward existing work without dismissing new ideas
- If the map is overwhelming: "You've got a lot going on. Let's focus on the top match."
- Validate the goal regardless of how many projects align

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| No projects match the goal | "None of your current projects directly serve this. Want to run `/intake` to start one intentionally?" |
| All projects match | "You're already spread across this goal — the issue is focus, not alignment. Pick ONE to ship first." |
| Goal is vague ("be better") | Probe once: "Better at what specifically?" If still vague, work with it |
| No data sources available | Ask the user to describe their active projects, do alignment in conversation |
| Goal matches current `/review` theme | "This aligns with your current theme. Here's how your focus projects map:" — reinforce, don't re-derive |
| User insists on starting new | Acknowledge, then: "Got it. Run `/intake` so you onboard it intentionally with a WIP check." |

## What This Skill Does NOT Do

- Create projects, issues, or tasks
- Judge project quality or worthiness
- Replace `/review` (which sets themes) — `/align` operationalizes them
- Force dropping projects — surfaces alignment, user decides
- Write to Obsidian or any external system (read-only skill)

## Cross-References

- **`/review`** → sets theme → `/align` maps it to projects
- **`/align`** → recommends focus → `/plan-week` schedules it
- **`/align`** → finds gaps → suggests `/intake` if truly needed
- **`project-pulse`** agent can provide activity data to supplement alignment analysis
- **`coach-tone`** for calibration if user is overwhelmed by the map
