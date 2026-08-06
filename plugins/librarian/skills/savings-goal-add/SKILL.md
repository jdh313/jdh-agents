---
name: savings-goal-add
description: Scaffold a new savings goal — a tracked plan to save toward a specific purchase with tier, budget, acceptance criteria, and decision triggers. Use when the user says "I want to save for X", "let's add a savings goal", "I'm planning to buy X eventually", "I should start saving for", or otherwise frames an upcoming substantial purchase as something needing deliberate funding.
---

# Savings Goal Add

Scaffold a new savings goal page under `Personal/Admin/Savings Goals/`. The schema defined here is queryable via `Bases/Savings Goals.base`, with a starting template at `Templates/Savings Goal.md`.

## Required skills

- **Skill(wiki-create)** — note creation, search, frontmatter, and Obsidian-flavored markdown conventions. Sibling skill in this plugin; invoke it by the bare name.

## When to use

- User wants to save toward a specific substantial purchase
- User is thinking about a future purchase that warrants deliberate funding (not impulse-buy territory)
- User wants to add a goal to the existing queue without committing to active funding yet

## Tier model

Four tiers, priority order (highest first):

1. **Health** — pain, preventative care, ergonomics, sleep
2. **Productivity** — work output (job + personal productivity)
3. **Hobby** — items tied to a named pursuit (photography, reading, 3D printing, concert-going-with-collecting, etc.)
4. **Discretionary** — lifestyle/QoL not tied to a hobby (travel, decor, cookware)

**Funding rule:** up to 4 concurrent active goals (one per tier). Serial within tier — next promotes when current funds.

**Tier-spanners:** assign to highest-priority tier the item qualifies for; secondary rationale lives in body prose.

**Boundary nudge for Hobby vs Discretionary:** Hobby = tied to a named ongoing pursuit. Discretionary = nice-to-have not tied to a pursuit. When the user is unsure, ask whether the underlying activity is something they actively practice or just occasionally do.

## Lifecycle

States: `queued | active | funded | acquired | dropped`

Transitions:
- `queued ↔ active` (promote/demote with funding capacity)
- `active → funded` (savings target hit)
- `funded → active` (decided to wait, restart contributions)
- `funded → acquired` (bought it)
- any state → `dropped` (decided against)

New goals default to `status: queued` unless user explicitly wants to start funding immediately. `active` requires a Lunch Money bucket.

## Queue prioritization within a tier

No persistent ranking field — decisions happen at promotion moments using current info.

**When an active goal funds or drops, promote one queued item.** Default heuristic: **highest compounding cost first**. Compounding cost = "every month without it gets worse" (escalating pain, productivity drag, workaround spend). Override with explicit user judgment when something else is clearly more pressing.

**When a new higher-priority item arrives in a tier with existing active goal:**
- Default: keep current active funding, queue the new item (preserves momentum)
- Exception: demote current to queued only if new item is genuinely emergency-level (acute pain, broken essential equipment)
- Lunch Money retains the balance on demotion — not destructive, just suboptimal pacing

The Base view shows queued items sorted by something inexpensive (cost, alphabetical) — that ordering is visual only, not authoritative. The actual promotion decision happens in conversation.

## Walkthrough

Build the goal incrementally. One question at a time, building from each answer. Don't bombard with multi-question prompts.

### 1. Current situation

Open with situation-gathering, not budget. Examples by item type:
- Furniture: "What's the current state? Causing problems, or want to upgrade before they emerge?"
- Hobby gear: "What's prompting this — picking up a new pursuit or upgrading existing?"
- Consumer items: "What problem does this solve that current setup doesn't?"

This shapes tier framing and rationale.

### 2. Tier check

Based on situation, propose tier with reasoning. Confirm or override.

- Pain/health-related → Health
- Work output / job-essential → Productivity
- Tied to a named pursuit → Hobby
- Lifestyle/QoL not tied to a pursuit → Discretionary

Tier matters because it determines the funding queue (concurrent vs serial) and which existing goals it competes with.

### 3. Cost target

Single number per schema. No ranges in frontmatter — body prose can elaborate uncertainty if needed.

Useful prompts:
- Anchor with a rough range based on item category before asking
- For sentimental/limited/irreplaceable items, surface archival/quality considerations *before* locking budget — these often shift the tier of solution (e.g., DIY → local pro)
- For path-uncertain items (DIY vs pro, used vs new, tabletop-only vs full replacement), help the user think through which path the budget targets

### 4. Acceptance criteria

The required section that does the most work in the schema. Push for specifics:

- "What would specifically satisfy this need?"
- Aim for 3–5 concrete criteria
- Capture the "must have" vs "nice to have" distinction
- If the user uses words like "matching", "consistent", "compatible" — these become criteria
- Budget/cost ceiling typically appears as a criterion alongside the functional ones

The criteria guard against scope creep at purchase time and create a clear "done" signal.

### 5. Decision triggers (optional but recommended)

What would change the plan? Common patterns:

- Quote/research finding pushes past budget → escalate, defer pieces, or re-evaluate path
- New information reveals a different solution path
- Item turns out rarer/more valuable than expected → upgrade quality
- Current setup degrades faster than expected → re-rank
- Post-purchase: solution doesn't solve the problem → root-cause investigation

### 6. Other optional sections

Ask if relevant; fill if so:

- **Current workaround** — what user is doing without it; helps justify priority + post-purchase verification
- **Alternatives considered** — paths weighed including ruled-out ones with reasoning preserved
- **Replaces** — frontmatter field; what the purchase would supersede (Catalog entry wikilink, or text for non-cataloged items)

## Iteration is the workflow

Three-item pilot showed: rationale + acceptance criteria benefit from "draft, react, revise" loop, not single-shot capture. Important context (sentimental value, hidden constraints, current workarounds) often surfaces mid-conversation. Don't lock the file too quickly — propose the full content for review, accept pushback, iterate.

## Creating the page

### Filename

`Personal/Admin/Savings Goals/<Item Name>.md` — descriptive, no date prefix, under 50 chars.

Examples: `Office Chair.md`, `Office Desk.md`, `Concert Poster Framing.md`, `Camera Body Upgrade.md`.

If folder doesn't exist, create with `mkdir -p` first.

### Frontmatter

```yaml
---
owner: jacob
type: savings-goal
tier: health         # health | productivity | hobby | discretionary
status: queued       # queued | active | funded | acquired | dropped
estimated_cost: 0
lunch_money_bucket: ""    # populated when active
replaces: ""              # what this supersedes (optional)
---
```

`date created` and `date_modified` are managed by the Linter plugin — do not include them in template emission.

### Body skeleton

Sections in narrative order. Required sections must be present and concrete.

1. `## Rationale` — *required* — why this is a goal, what problem it solves
2. `## Acceptance criteria` — *required* — bullets of what specifically satisfies the need
3. `## Current workaround` — optional — what the user is doing without it
4. `## Alternatives considered` — optional — paths weighed including ruled-out
5. `## Decision triggers` — optional — branching paths and re-rank conditions
6. `## Acquisition log` — placeholder, populated post-purchase: `*(populated after `acquired`)*`

## Quality rules

- `tier` must be one of four valid values; pick the highest-priority qualifying tier for spanners
- `status` defaults to `queued`; only `active` if the user has Lunch Money bucket ready
- Acceptance criteria must be present and concrete — refuse vague ones like "be better than current"
- For sentimental/irreplaceable items, surface the archival/quality consideration before locking budget
- One item per goal — don't bundle multiple goals in a single note

## Report

Tell the user:
- Path of created page
- Tier assigned + reason
- Status (default `queued`)
- Whether folder was created
- Suggested next step:
  - If `active`: create matching Lunch Money bucket
  - If `queued`: note where it sits in tier queue
