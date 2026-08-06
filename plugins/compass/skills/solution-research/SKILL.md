---
name: solution-research
description: Generate a systems-first parallel-research handoff prompt from a locked needs map or requirements doc. This skill should be used when a needs map exists (typically produced by `first-principles`) and the user wants to research the solution space — "research options against the needs map", "generate the research prompt", "find systems that solve this", "send off subagents to research X". Produces a prompt for a fresh session that dispatches parallel research subagents — each designing one end-to-end system (backbone + tools assigned to roles) — with real-incident test scenarios as gates, primary-source citation requirements, an adversarial verification pass attacking the seams between tools, and composition-aware synthesis. Not for running research directly in-session (use `deep-research` for that).
---

# Solution Research

Turn a locked needs map into a research handoff prompt whose output cannot anchor on individual tools. The core inversion: the unit of evaluation is the **system** — an end-to-end architecture where tools fill roles — and a system passes a gate only by walking the user's real friction incidents end-to-end. The prompt is the artifact; the research itself runs in a fresh session that pastes it.

## Prerequisites

A signed-off needs map with: must-solve gates, nice-to-haves, exclusions, and an evidence section of real incidents. `first-principles` produces exactly this shape and locks it to a vault note. If no needs map exists, run `first-principles` first — generating research lanes from an unvetted wishlist reproduces the tool-comparison stall this skill exists to avoid.

## Procedure

Follow the assembly checklist and template in `references/research-handoff.md`. The load-bearing properties — each mapped to the failure it prevents in the reference's design-rules table — are:

1. **Systems, not tools** — each subagent designs ONE system per lane (backbone + role→tool table); gates apply to the system as a whole; a role with no good tool is a reported gap with integration cost, never a disqualifier.
2. **Real-incident test scenarios** — convert the map's evidence incidents into 2–4 walkthrough scenarios with concrete physical detail and explicit pass/fail tripwires. Prevents gate verdicts earned from marketing feature lists.
3. **Anchoring guard** — forbid opening prior comparison notes (name them, titles only) and forbid seeding subagent prompts with tool names.
4. **Primary-source citations** — every load-bearing tool claim cites official docs/repo or is marked "unverified".
5. **Adversarial verification pass** — one refuter subagent per viable system, attacking the seams between tools (does layer A actually talk to layer B; is the API read-only or paywalled; is the glue a weekend or a month).
6. **Composition-aware synthesis** — call out tools shared across systems; they may recombine into a hybrid better than any single lane produced.

Also from the checklist: name the search MCP subagents must use with the exact `ToolSearch("select:<tool>")` loading step, include an LLM-native/DIY lane when the user has the capability, include a community-practice lane, and end with the user's interaction preferences for the synthesis discussion.

## Output

Render the prompt verbatim in a fenced code block and mirror it to `$TMPDIR` (filename: `handoff-YYYY-MM-DD-HHMM-<slug>.md`). Remind the user to `/clear` in the fresh session before pasting. The `handoff` skill's conventions apply: prompt-not-doc, reference-don't-embed, one screen if possible.

## Composes with

- `first-principles` — upstream; produces and locks the needs map this skill consumes.
- `handoff` — this is a specialized instance of it; reuse its output conventions.
- `deep-research` — alternative when the user wants research run directly in-session as a cited report, rather than a systems-first handoff for a fresh session.
- `debate:debate` — downstream if the resulting shortlist ends in a close call between two systems.
- `librarian:catalog-evaluate` — downstream, once a decision lands and is worth cataloging.
