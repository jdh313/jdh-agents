---
name: grill-with-docs
description: Grill a plan against this repo's CONTEXT.md glossary and NDR atoms, sharpen terminology, and update CONTEXT.md inline as decisions crystallise. Use when stress-testing a plan against project vocabulary, locking in a domain term, or surfacing drift between code naming and the glossary. Adapted from mattpocock/skills (MIT, © 2026 Matt Pocock).
upstream:
  repo: mattpocock/skills
  path: skills/engineering/grill-with-docs
  reviewed_sha: 658d53e6ded8
  reviewed: 2026-07-09
  status: reviewed
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - Skill
---

Interview the user about every aspect of this plan until reaching a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, propose a recommended answer.

Ask one question at a time. Wait for the user's response before continuing.

If a question can be answered by exploring the codebase, explore the codebase instead of asking.

Do not enact the plan until the user confirms a shared understanding has been reached.

## Maintain the glossary via domain-modeling

As terms get resolved during the conversation, run the `craft:domain-modeling` skill to update CONTEXT.md inline — don't batch, and don't maintain CONTEXT.md directly from this skill. `domain-modeling` owns where CONTEXT.md lives, its format, the conversation moves for challenging and sharpening terminology against it, and the gate for routing capture-worthy decisions to `/capture-decision`.

This skill is the plan-grilling application of that discipline: the interview loop — the question-by-question walk down the design tree — stays here. Everything about *how* the glossary gets written, formatted, and maintained lives in `domain-modeling`, and this skill inherits it by dispatch.

## Composition with other plugins

- **`craft:domain-modeling`** is dispatched by this skill for all CONTEXT.md maintenance and NDR-capture discipline that surfaces mid-interview. See above.
- **`spec-flow:draft`** may invoke this skill when contested vocabulary surfaces during contract drafting. Soft composition only — both plugins work standalone.
- **`/drift-check`** (ndr plugin) can flag drift between CONTEXT.md term definitions and code naming. Out of scope for this skill — flag candidates for follow-up rather than fixing inline.
