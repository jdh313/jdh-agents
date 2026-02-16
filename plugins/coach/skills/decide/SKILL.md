---
name: coach:decide
description: >-
  This skill should be used when the user says "/decide", "decision journal",
  "log a decision", "I need to decide", "record this decision", "why did I
  choose", "document this decision", or "decision record". Captures structured
  decisions with context, options considered, rationale, and revisit conditions
  to prevent re-litigation.
allowed-tools:
  # Linear — linked issues (if referenced)
  - mcp__linear-server__list_issues
  # Obsidian — prior decisions, project notes, write record
  - mcp__obsidian-mcp__search_notes
  - mcp__obsidian-mcp__write_note
---

# /decide -- Decision Journal

A structured decision capture tool. Records what was decided, why, what alternatives were considered, and when to revisit. Primarily capture, not coaching -- the goal is to prevent future re-litigation by making the decision's rationale findable. Accepts "gut feel" as valid rationale.

## Flow

Execute these steps in order. Keep the conversation efficient -- decisions lose clarity the longer you deliberate.

### Step 1: Capture (1-2 Exchanges)

Determine the decision state:

**If the decision is already made:**
> What's the decision?

Accept the answer and move to Step 2.

**If the user is still deciding:**
Brief coaching only -- do not become a decision framework:

> What are the options you're weighing?

Then:
> Which way are you leaning?

If they have a lean, validate it and move to Step 2 with that as the decision. If they're truly stuck, help them name the tension (e.g., "Sounds like it's speed vs. quality") and ask them to pick. Do not enumerate pros and cons -- that's procrastination fuel.

### Step 2: Structure (1 Exchange)

Organize what you've gathered into a draft structure:

```
**Decision:** [One-line statement]
**Context:** [Why this decision came up now]
**Options considered:**
1. [Option A] -- [brief note]
2. [Option B] -- [brief note]
3. [Others if mentioned]
**Choice:** [Which option, or custom path]
**Rationale:** [Why -- including "gut feel" if that's what it is]
```

Present the draft and ask:

> Does this capture it? Anything to adjust?

Accept edits. Do not push for more detail than the user wants to give. "It felt right" is a complete rationale.

### Step 3: Enrich (Silent)

Before writing, silently add context if available:

**Obsidian** (if available):
- Search `Journal/Decisions/` for prior decisions that might be related
- If a related decision exists, note it for linking
- Search for project notes mentioned in the decision context

**Linear** (if available):
- If the decision references a project or issue, note the link

### Step 4: Revisit Conditions (1 Exchange)

Ask one question to define when this decision should be reconsidered:

> When should you reconsider this? Or is it final?

- If the user mentioned conditions earlier ("unless X changes"): pre-fill and confirm
- If not, suggest one based on the decision: "Revisit if [reasonable trigger]"
- Accept "it's final" -- not every decision needs a revisit clause

### Step 5: Write Record (With Permission)

Once the decision is captured, ask before writing:

> Want me to save this decision?

**If Obsidian MCP is available and user agrees:**
- Propose path: `Journal/Decisions/YYYY-MM-DD [decision-slug].md`
  - Slug is a kebab-case summary of the decision (e.g., `2026-02-14 use-postgres-over-sqlite.md`)
- Content structure:
  ```
  # [Decision Title]

  **Date:** YYYY-MM-DD
  **Status:** Decided

  ## Context
  [Why this decision came up -- what prompted it]

  ## Options Considered
  1. **[Option A]** -- [notes, trade-offs]
  2. **[Option B]** -- [notes, trade-offs]

  ## Decision
  [What was chosen]

  ## Rationale
  [Why -- in the user's own framing]

  ## Revisit Conditions
  - [When to reconsider, if applicable]

  ## Related
  - [Links to project notes, prior decisions, Linear issues if found]
  ```
- Ask the user to confirm or adjust the path before writing

**If Obsidian MCP is unavailable or user declines:**
- Display the decision record in chat
- No file operations

## Tone

Use `coach-tone` at **reduced intensity**:

- This is a capture tool, not a coaching session
- Brief, efficient, structured
- No judgment about the decision quality
- "Gut feel" and "it just makes sense" are valid rationale -- do not push for more
- If the user is agonizing: "You've thought about it enough. Pick and record it. You can revisit later."

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| Trivial decision ("what to eat for lunch") | Capture it if they want. Don't gatekeep what counts as a decision. |
| Reversible decision | Note reversibility in the record: "Low cost to reverse" |
| Decision involves other people | Note stakeholders if mentioned, but don't prompt for consensus |
| User wants to revisit an old decision | Search `Journal/Decisions/` for it. If found, present it and ask: "Has something changed?" |
| Multiple decisions at once | Handle one at a time. "Let's capture the first one, then the next." |
| No data sources available | Run the full conversation without enrichment -- capture is the priority |

## Cross-References

- Decision records feed into `momentum` agent for pattern analysis
- Uses `coach-tone` at reduced intensity
- Prior decisions in `Journal/Decisions/` are referenced for context

## What This Skill Does NOT Do

- Make decisions for the user
- Run decision frameworks (pros/cons lists, weighted matrices)
- Judge decision quality or rationale
- Require group consensus or stakeholder analysis
- Create tasks or action items from decisions
- Require any specific vault structure or configuration
- Write anything without explicit permission
