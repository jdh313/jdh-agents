---
name: grill-with-docs
description: Grill a plan against this repo's CONTEXT.md glossary and NDR atoms, sharpen terminology, and update CONTEXT.md inline as decisions crystallise. Use when stress-testing a plan against project vocabulary, locking in a domain term, or surfacing drift between code naming and the glossary. Adapted from mattpocock/skills (MIT, © 2026 Matt Pocock).
upstream:
  repo: mattpocock/skills
  path: skills/engineering/grill-with-docs
  reviewed_sha: 697d4ce9742d
  reviewed: 2026-07-27
  status: reviewed
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - Skill
---

Apply the skill-composition mapping in [`../../RUNTIME.md`](../../RUNTIME.md).

Run `Skill(craft:grill)` for the interview loop.

Two scopings for this variant: the subject is a **plan**, and the interview ends at one both of you are ready to enact; and the *facts* worth looking up live in **this repo** — the codebase, `CONTEXT.md`, and current NDR heads — so answer from those rather than asking the user to recall them.

## Maintain the glossary via domain-modeling

As terms get resolved during the conversation, run the `craft:domain-modeling` skill to update CONTEXT.md inline — don't batch, and don't maintain CONTEXT.md directly from this skill. `domain-modeling` owns where CONTEXT.md lives, its format, the conversation moves for challenging and sharpening terminology against it, and the gate for routing capture-worthy decisions to `/capture-decision`.

This skill owns neither half of what it runs: the interview loop is `craft:grill`'s, the glossary discipline is `domain-modeling`'s. What it contributes is the pairing — grilling a plan *while* the vocabulary it is written in gets sharpened, so terms settle at the moment they are contested rather than in a cleanup pass afterward.

## Composition with other plugins

- **`craft:grill`** is dispatched by this skill for the interview loop itself — the decision-tree walk, one question at a time, facts looked up rather than asked, and the gate against acting before shared understanding. Don't restate those moves here; they change upstream more often than anything else in this skill, and one owner keeps the copies from drifting.
- **`craft:domain-modeling`** is dispatched by this skill for all CONTEXT.md maintenance and NDR-capture discipline that surfaces mid-interview. See above.
- **`spec-flow:draft`** gates on this skill during contract drafting: when the repo has a `CONTEXT.md` and the goal's central nouns are missing from it or used inconsistently, draft invokes this skill before writing the contract. The gate is conditional, not universal — no `CONTEXT.md` (or no `craft` installed) means no gate, so both plugins still work standalone. Expect draft to arrive warm, having already scanned the codebase; scope the interview to the contested terms rather than the full decision tree.
- **`/drift-check`** (ndr plugin) can flag drift between CONTEXT.md term definitions and code naming. Out of scope for this skill — flag candidates for follow-up rather than fixing inline.
