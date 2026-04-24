---
name: debate
description: This skill should be used when the user asks for an opinion on a decision, or when genuine decision/opinion questions are detected ("should I", "is it worth", "would you recommend", "X vs Y"). Spawns parallel advocate agents to research opposing perspectives, with optional fact-checking, devil's advocacy, and independent synthesis. Three modes (Quick/Standard/Deep) control pipeline depth. Not for factual questions, simple preferences, or single-answer lookups.
---

# Debate

Dialectical analysis through parallel research. Frame the question, gather personal context, dispatch advocate agents with opposing stances, optionally verify claims and challenge the consensus, then synthesize an opinionated verdict.

## When to Trigger

**Invoke for:**
- "Should I..." / "Is it worth..." / "Would you recommend..."
- "X vs Y" comparisons requiring research
- Genuine decision/opinion questions with meaningful trade-offs

**Do NOT invoke for:**
- Factual questions with single correct answers
- Simple preferences ("which color do you like?")
- Weather, time, or lookup queries
- Questions where the user has already decided and wants help executing

## Modes

Three pipeline modes control depth and thoroughness:

| Mode | Pipeline | Auto-detect When |
|------|----------|-----------------|
| **Quick** | Advocates → Synthesis | Simple binary, low-stakes, casual tone |
| **Standard** | Advocates (scored) → Fact-checker → Synthesis → [Decision record?] | Multi-option, domain-specific, moderate complexity |
| **Deep** | Advocates R1 → Fact-checker → Advocates R2 → Devil's advocate → Synthesizer → [Decision record?] | High-stakes keywords, irreversible decisions, user says "thorough" |

**User override:** `--quick`, `--standard`, `--deep` (e.g., `/debate --deep Should I change careers?`)

**Auto-detection heuristic:**
- **Deep** triggers on: "career change", "invest", "irreversible", "major", "life decision", explicit `--deep`, or user asking for thoroughness
- **Standard** triggers on: multi-option questions, domain-specific topics, moderate complexity
- **Quick** triggers on: simple binary questions, casual tone, low-stakes

Announce the selected mode: "Running in [Quick/Standard/Deep] mode."

## Domain Guidance

Based on the detected domain, inject domain-specific guidance into advocate prompts:

| Domain | Prioritize | Be Skeptical Of |
|--------|-----------|-----------------|
| **Tech** | Official docs, benchmarks, GitHub metrics, conference talks | Vendor marketing, outdated benchmarks (>2yr), hype cycles |
| **Finance** | Regulatory filings, academic research, established publications | Unverified returns, survivorship bias, crypto shilling |
| **Career** | BLS/labor data, industry surveys, practitioner accounts | Anecdotal success stories, hustle culture, recency bias |
| **Health** | Peer-reviewed journals, clinical guidelines, meta-analyses | Single studies, supplement marketing, influencer advice |
| **Life** | Psychology research, longitudinal studies, wellbeing indices | Self-help gurus, unfalsifiable claims, survivorship bias |

If the domain doesn't match any of the above, skip domain guidance.

## Orchestrator Flow

Execute these steps in order:

### Step 1: Frame the Question

Decompose the user's question into:
- **Core decision:** The binary choice or set of options being weighed
- **Stakeholder:** Who is affected (usually the user)
- **Domain:** Career, tech, life, finance, health, or other
- **Timeframe:** Short-term vs long-term implications
- **Personal context clues:** Anything from conversation history that personalizes this
- **Mode:** Auto-detect or use user override

### Step 2: Gather Personal Context

Search for relevant personal context BEFORE dispatching agents. All agents must receive identical context.

- Search Obsidian notes for relevant prior work, decisions, or situation details
- Search OpenMemory for relevant cross-project patterns or past evaluations
- Check `Journal/Decisions/` for prior decisions on related topics
- Extract relevant details from the current conversation history
- Compile into a brief context block (3-5 bullet points max)

If no relevant personal context exists, proceed with the framed question alone.

### Step 3: Determine Question Type and Options

Classify the question and identify positions:

- **Binary** ("Should I X?") — 2 advocates: one for, one against
- **Multi-option** ("X vs Y vs Z?") — One advocate per named option
- **Open-ended** ("What framework should I use?") — Do a quick web search to identify the top 3-4 reasonable options, then dispatch one advocate per option

**Maximum: 5 advocates.** If more than 5 options exist, narrow to the top 5 contenders based on quick research before dispatching.

### Step 4: Dispatch Advocate Agents (Round 1)

Launch all advocate agents simultaneously using the Task tool with `subagent_type: "advocate"` and `model: "sonnet"`.

Each agent's prompt must include:

```
You are arguing [FOR/AGAINST] the following position: [framed question]

OR

You are arguing in favor of: [Option Name]

## Personal Context
[compiled context from Step 2, or "No specific personal context available"]

## Domain
[domain from Step 1]

## Domain Guidance
[domain-specific source priorities and red flags from the table above, or "No specific domain guidance"]

## Timeframe
[timeframe considerations from Step 1]

## Round
Round 1 — initial research.

Research this position thoroughly using web search. Rate every source's quality (1-5). Follow the output format defined in your agent instructions exactly.
```

### Step 5: Quick Mode — Synthesize and Done

**Quick mode only.** After advocates return:

1. Present each position with key arguments, inline source citations, counterarguments, and confidence
2. Analyze where positions actually conflict vs. talk past each other
3. Evaluate evidence quality — is one side backed by data while the other relies on opinion?
4. Consider personal context — how does the user's situation tilt the balance?
5. Deliver the verdict with confidence level, reasoning, and conditions where the opposite answer would be correct
6. Collect sources — deduplicated list from all advocates with attribution

Skip to **Output Format** section.

### Step 6: Fact-Check (Standard + Deep)

Dispatch the fact-checker agent using the Task tool with `subagent_type: "fact-checker"` and `model: "sonnet"`:

```
## Question
[framed question]

## Advocate Outputs
[paste all advocate R1 outputs verbatim]

Verify the key claims, validate source quality ratings, and check for logical issues. Follow the output format defined in your agent instructions exactly.
```

### Step 7: Standard Mode — Synthesize with Fact-Check

**Standard mode only.** After fact-checker returns:

Same as Quick synthesis (Step 5) but additionally:
- Incorporate fact-checker findings — note disputed claims and adjusted source ratings
- Weight verified claims higher than unverified ones
- Mention any logical issues flagged
- Offer decision record (see Step 11)

Skip to **Output Format** section.

### Step 8: Dispatch Advocates Round 2 (Deep Only)

**Deep mode only.** After fact-checker returns, dispatch all advocates again in parallel:

```
You are arguing [FOR/AGAINST] the following position: [framed question]

OR

You are arguing in favor of: [Option Name]

## Personal Context
[same as Round 1]

## Domain
[same as Round 1]

## Domain Guidance
[same as Round 1]

## Timeframe
[same as Round 1]

## Round
Round 2 — informed rebuttal. You must address the counterarguments and fact-checker findings below.

## Your Round 1 Output
[paste this advocate's R1 output]

## Fact-Checker Assessment of Your Claims
[paste relevant sections from fact-checker output for this advocate]

## Counterarguments to Address
[extract the strongest arguments from OTHER advocates that this advocate must rebut]

Shore up disputed claims with new evidence, directly address the counterarguments, and update your confidence. Follow the output format defined in your agent instructions exactly.
```

### Step 9: Dispatch Devil's Advocate (Deep Only)

**Deep mode only.** After R2 advocates return, determine the leading position (highest confidence after R2), then dispatch using the Task tool with `subagent_type: "devils-advocate"` and `model: "sonnet"`:

```
## Question
[framed question]

## Leading Position
[which side/option is currently winning] at [X%] confidence

## All Advocate Outputs
[paste all R1 and R2 outputs]

## Fact-Checker Results
[paste fact-checker output]

## Personal Context
[same as advocates received]

Attack the leading position. Find weaknesses, hidden assumptions, and failure scenarios. Follow the output format defined in your agent instructions exactly.
```

### Step 10: Dispatch Synthesizer (Deep Only)

**Deep mode only.** After devil's advocate returns, dispatch using the Task tool with `subagent_type: "synthesizer"` and `model: "sonnet"`:

```
## Question
[framed question]

## All Advocate Outputs (Both Rounds)
[paste all R1 and R2 outputs]

## Fact-Checker Results
[paste fact-checker output]

## Devil's Advocate Output
[paste devil's advocate output]

## Personal Context
[same as advocates received]

## Domain
[domain]

## Timeframe
[timeframe]

Produce an independent verdict. You did not frame this question — evaluate the evidence fresh. Follow the output format defined in your agent instructions exactly.
```

For Deep mode, use the synthesizer's verdict as the primary verdict in the output. The orchestrator may add brief editorial notes but should not override the synthesizer's conclusion without clear justification.

### Step 11: Offer Decision Record (Standard + Deep)

After synthesis, ask: "Want me to save this as a decision record?"

If the user agrees, write to Obsidian using MCP:

**Path:** `Journal/Decisions/YYYY-MM-DD [decision-slug].md`

**Content:**
```markdown
# [Decision Title]

**Date:** YYYY-MM-DD
**Status:** Decided
**Method:** Debate ([Quick/Standard/Deep])

## Context
[Why this decision came up — from the framed question]

## Options Considered
1. **[Option A]** — [summary from advocate]
2. **[Option B]** — [summary from advocate]

## Decision
[The verdict]

## Rationale
[Synthesized reasoning — evidence quality, key trade-offs]

## Confidence
[X%] — [Brief explanation]

## Key Evidence
- [Top 3-5 sources that most influenced the verdict]

## Risks & Conditions
- [When to reconsider — from devil's advocate output if available]

## Related
- [Links to Obsidian notes found during context gathering]
```

If Obsidian MCP is unavailable, display the decision record in chat instead.

## Output Format

### Binary Decision

```markdown
## [Mode] Debate: [question summary]

## For: [position]
- **[Argument]** — [evidence] ([Source](url)) [Quality: N/5]
- **[Argument]** — [evidence] ([Source](url)) [Quality: N/5]
- **Strongest counterargument:** [what the other side gets right]
- **Fact-check notes:** [any disputed claims or adjustments, if Standard/Deep]
- **Confidence:** [X%]

## Against: [position]
- **[Argument]** — [evidence] ([Source](url)) [Quality: N/5]
- **[Argument]** — [evidence] ([Source](url)) [Quality: N/5]
- **Strongest counterargument:** [what the other side gets right]
- **Fact-check notes:** [any disputed claims or adjustments, if Standard/Deep]
- **Confidence:** [X%]

## Devil's Advocate Challenge (Deep only)
[Key weaknesses and failure scenarios identified]

## Verdict (Confidence: [X%])
[Clear recommendation with reasoning. Notes conditions where the
opposite answer would be correct.]

## Sources
- [Source](url) — Quality: [N/5] — cited by: For/Against/Both
```

### Multi-Option Decision

```markdown
## [Mode] Debate: [question summary]

## Option 1: [name]
- **[Argument]** — [evidence] ([Source](url)) [Quality: N/5]
- **Strongest counterargument(s):** [what other options get right]
- **Fact-check notes:** [if Standard/Deep]
- **Confidence:** [X%]

## Option 2: [name]
...

## Devil's Advocate Challenge (Deep only)
[Key weaknesses and failure scenarios for the leading option]

## Verdict (Confidence: [X%])
[Recommendation with reasoning and conditions where other options win.]

## Sources
- [Source](url) — Quality: [N/5] — cited by: [which options]
```

### Confidence Levels

Express confidence as a percentage (0-100%):
- **80-100%:** Clear winner backed by strong evidence or expert consensus
- **50-79%:** Winner with notable trade-offs or situational dependencies
- **Below 50%:** Genuinely close call, heavily depends on priorities or circumstances

## Constraints

- Maximum 5 advocate agents per round
- All agents run as `sonnet`; orchestrator stays in main context
- Advocates do web research only — orchestrator handles all local/personal context gathering
- All agents receive identical personal context (no asymmetry)
- Sources must be real URLs from web search results, not hallucinated
- If advocates return weak or conflicting evidence, say so — do not manufacture certainty
- Decision record creation requires explicit user confirmation
- Deep mode can dispatch up to 13 agents total (5 advocates x2 + fact-checker + devil's advocate + synthesizer) — warn user this takes longer
- **Agent failure handling:** If an agent returns empty, incoherent, or clearly broken output: (1) retry once with the same prompt, (2) if it fails again, skip that agent and note the gap in the synthesis — e.g., "fact-check was unavailable, evidence claims are unverified" or "devil's advocate failed, consensus was not stress-tested". Never silently proceed as if the agent succeeded.
