---
name: design-by-stories
description: Design or redesign an artifact's shape — a schema, template, data model, config format, note type, or API surface — by modeling its actors and user stories first, then deriving the shape from the stories. Use when the user says "let's design X", "redesign this template/schema", "rework this note type", "design it like software", "model the actors for X", "what should the shape of X be", or starts an open-ended, iterative design of an artifact's structure. One fork at a time, human adjudicates every fork. Distinct from interrogate-model (critiques an existing model for what it can't express), first-principles (elicits needs for a purchase/problem), and spec-flow:draft (contracts a code change for implementation).
argument-hint: "[artifact or model to design]"
effort: high
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Agent
  - AskUserQuestion
  - Write
  - Edit
  - TodoRead
  - TodoWrite
---

# design-by-stories

## Overview

Design an artifact the way you'd design software: **actors first, then one user story per actor, then derive the shape from the stories — never template-first.** The artifact can be anything with a structure: a schema, a frontmatter contract, a note type, a data model, a config format, an API surface, a directory layout.

The failure this skill targets is **template-first design** — opening the existing shape and tweaking fields. Tweaking preserves fields no actor needs, misses fields the load-bearing actor does, and never surfaces the actor you forgot to list (which is usually the one that reframes everything). Modeling the actors and stories *first* makes every field trace to a need, and exposes structural flaws — like one field conflating two independent axes — before they get baked in.

```
frame + ground ──► cast the actors (and challenge the cast) ──► stories, hardest first
   ──► sharpen each story, one fork at a time ──► derive the shape from the stories
   ──► ground in a real instance ──► lock / park ledger ──► emit + hand off
```

This is a **collaborative facilitation**, not an autonomous pass. Every fork is a user turn. Surface one question at a time; the next question is the load-bearing fork, not the next item on a checklist.

## When to use

- (Re)designing the shape of an artifact: a schema, template, frontmatter contract, note type, data model, config format, directory layout, or API surface.
- A template "feels off" but it isn't clear *why* — modeling the actors reveals which fields serve no one and which needs have no field.
- An iterative, exploratory design where the right structure isn't known up front and will emerge from how the thing is actually used.
- Before writing a `spec-flow` contract for a change whose *shape* is still open — design the shape here, then hand the settled shape to `spec-flow:draft`.

**Do NOT use** for:

- **Critiquing an existing model** for what it can't represent → `interrogate-model` (the audit counterpart — run it *after* this skill to stress-test the derived shape).
- **Eliciting needs for a purchase or recurring-problem** ("what should I use for X", "what do I actually want from a Y") → `first-principles`. That skill produces a needs map; this one produces an artifact shape. first-principles is upstream — its needs can seed the actors here.
- **Contracting a code change for implementation** → `spec-flow:draft`. That drives *building*; this designs *the shape* that gets built.
- **Clarifying your own stance or feelings** → `compass:reflect` / `compass:mull`.

## Inputs

- `$ARGUMENTS` — the artifact or model to design (e.g. "the software catalog template", "the event note schema", "the webhook config format"). If empty, infer it from the conversation / working area and confirm in one line before starting: `"Designing: <one-line artifact description>. Right thing?"`

## Method

Surface each phase's output as you go — list-first, terse. The phases build on each other; do not dump them all at once. Every fork is the user's call — propose a default and a recommendation, then **stop for their answer**.

### Phase 1 — Frame and ground

**Entry:** the artifact is identified.
**Actions:**
1. If the artifact already exists, read its current shape (the template, the schema, a real instance) so both sides work from the same starting point. State the shape it defines *today* in a few bullets.
2. For a tracked codebase or the vault, ground in governing context — `/ground` for NDR heads, the project `CONTEXT.md` glossary, or the vault rules — so the design respects existing decisions.
3. Anchor the redesign with **one** question: *what's prompting this?* (a felt problem, a new requirement, a real instance that doesn't fit). Don't touch the shape until the direction is anchored.

**Exit:** the current shape is stated, and the motivation is named.

### Phase 2 — Cast the actors

**Entry:** the motivation is anchored.
**Actions:**
1. Enumerate every *user* of the artifact. **Include non-human actors** — the AI that reads/writes it, a query or `.base` that projects it into columns, a renderer (Breadcrumbs, a UI), a downstream tool that consumes it. They have requirements too, and they are the ones humans forget.
2. **Challenge the cast** in one question: *"Is there an actor I'm missing — or one here to drop?"* The load-bearing actor is usually the one not yet listed (e.g. a *decide-right-now* actor distinct from a *retrieve-a-settled-answer* actor). This challenge is where the design's hardest, most valuable distinction often appears — do not skip it.

**Exit:** a confirmed cast of actors, human and non-human.

### Phase 3 — Stories, hardest first

**Entry:** the cast is confirmed.
**Actions:**
1. Write one user story per actor: **"As [actor], I want [X] so that [Y]."**
2. **Start with the most contentious or interesting actor**, not the easy ones — the hard story drives the most structure. Easy actors' stories often fall out as corollaries once the hard one is resolved.

**Exit:** a draft story for the hardest actor (others can be deferred until it's resolved).

### Phase 4 — Sharpen each story, one fork at a time

**Entry:** a draft story exists.
**Actions:**
1. Find the fork in the story that **dominates everything downstream** and ask only that, one question per turn. (Worked example: *does this actor READ a materialized verdict, or THINK IN a worksheet they actively fill?* — that one fork decides whether the shape needs scaffolding fields or just display fields.)
2. When a fork resolves, write the **"Resolved story:"** line explicitly so it's locked and visible.
3. Repeat down the actors. A later actor's story may reopen an earlier fork — that's fine; re-resolve and re-lock.

**Exit:** resolved stories for the actors that drive structure.

### Phase 5 — Derive the shape from the stories

**Entry:** the driving stories are resolved.
**Actions:**
1. Read the fields / sections / structure **off the stories** — each element exists because a story needs it. If a field traces to no story, it's a candidate to cut; if a story needs something no field carries, that's a gap to add.
2. Name where each element lives (which page, which layer, which axis). When two concerns want to vary independently, give them separate elements — see the conflation rule below.

**Exit:** a derived shape, every element traceable to a story.

### Phase 6 — Ground in a real instance

**Entry:** a derived shape exists.
**Actions:**
1. Pull a **concrete existing instance** of the artifact and check the derived shape against it — abstract shapes hide flaws that a real example exposes. (Worked example: a real catalog page that predated the template revealed the template's split was wrong and that a dropped field was actually needed.)
2. Watch for the **axis-conflation tell**: when a value *feels impossible to set* ("I can't say A over B because B might be right elsewhere"), the field is conflating two independent axes. Split them — one axis per element. This is the single highest-value structural fix the method produces, and it's also exactly what `interrogate-model` audits for; if the artifact is load-bearing, hand the derived shape to `interrogate-model` for a full representability pass.

**Exit:** the shape survives contact with a real instance, conflations split.

### Phase 7 — Keep the lock / park ledger

**Throughout phases 3–6**, maintain an explicit running ledger so state never gets lost across a long session:
- **`Locked:`** — a decision that's settled.
- **`Provisionally locked:`** — settled enough to build on, revisitable.
- **`Resolved story:`** — a story whose driving fork is closed.
- **`Parked:`** — a fork that doesn't block progress. **Park it and keep momentum** — design what's progress either way; many parked forks resolve themselves once downstream content is known.

Restate the ledger when re-entering after a break or when the user asks where things stand.

### Phase 8 — Emit and hand off

**Entry:** the shape is settled (or settled-enough to materialize for review).
**Actions:**
1. Write the designed artifact where it belongs — the template, the schema file, the example note — using the project's own conventions and tools (for the vault, the `librarian` skills / `obsidian-cli`; for code, the repo's patterns). Materialize it for review rather than only describing it.
2. Hand off the parts this skill doesn't own:
   - **Representability stress-test** → `interrogate-model`.
   - **Build the change** → `spec-flow:draft`.
   - **Record the load-bearing calls** as durable decisions → `/capture-decision`.

**Exit:** the artifact exists, and follow-ups are routed.

## Rationalizations to reject

| Rationalization | Why it's wrong |
|-----------------|----------------|
| "I'll just tweak the existing template." | Template-first preserves fields no actor needs and hides the actor you forgot. Derive the shape from stories; the existing template is at most a real instance to test against in Phase 6. |
| "The actors are obvious." | The load-bearing actor is usually the one not on your first list. Phase 2's *challenge the cast* exists precisely to find it — skip it and the design inherits the blind spot. |
| "Humans are the only users." | The AI, a query/base, and a renderer all have requirements. Omitting non-human actors is how fields end up un-queryable or un-renderable. |
| "Let's resolve every open question before moving on." | Forcing every fork stalls the session. Park non-blocking forks and design what's progress either way — most resolve once downstream content exists. |
| "One field can carry that." | If a value feels impossible to set, it's two axes conflated. Split them — one independent concern per element. |
| "It's clear in my head, I'll just write the final shape." | Then write it as a real instance and run Phase 6 — grounding in a concrete example is where the head-shape meets the flaw it was hiding. |

## Hard rules

1. **Actors before stories before shape.** Never start from the template. The existing shape is an input to test against (Phase 6), not the starting point.
2. **Challenge the cast (Phase 2).** Always ask whether an actor is missing or droppable — the highest-value distinction usually lives here.
3. **Include non-human actors** — the AI, queries/bases, renderers, downstream consumers.
4. **One fork at a time, user adjudicates.** Propose a default and a recommendation; stop for the answer. This is a collaboration, not an autonomous run.
5. **Ground in a real instance before finalizing (Phase 6).** Abstract shapes hide flaws.
6. **Split conflated axes.** A value that's impossible to set is the tell — one independent concern per element.
7. **Park, don't force.** Keep momentum on what's progress either way; maintain the lock/park ledger.
8. **Emit the artifact.** Materialize the designed shape for review; don't leave it as prose.

## Related

- `interrogate-model` — the **audit** counterpart: critiques an existing model for the scenarios it can't express (axes, conflations, latent axes). Run it *after* this skill to stress-test the derived shape. The conflation tell in Phase 6 is exactly its bread and butter.
- `improve-codebase-architecture` — structural review (depth, coupling) of code; a different counterpart for code artifacts.
- `prototype` — when the open question is "does this *behave* right?" rather than "what *shape* should it have?", build a throwaway to find out, then bring the answer back here.
- `spec-flow:draft` (spec-flow) — the build handoff once the shape is settled.
- `/capture-decision`, `/ground` (ndr) — record the load-bearing calls; ground the design in governing heads.
- `first-principles` — upstream needs-elicitation; its needs map can seed the actors and stories here.
- [`EXAMPLE.md`](EXAMPLE.md) — the validated worked run (software-catalog redesign) the method was distilled from.
