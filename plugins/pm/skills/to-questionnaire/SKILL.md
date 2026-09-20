---
name: to-questionnaire
description: >-
  Turn a decision you cannot answer alone into a questionnaire for someone else
  to fill in — a Markdown document handed to one person to answer async, or
  worked through together in a meeting. This skill should be used when the user
  invokes `/pm:to-questionnaire`, says "write a questionnaire", "I need to ask
  someone about this", "draft questions for X", "turn this into a list of
  questions", "I'm blocked on someone else's knowledge", or when a decision
  stalls because the facts live in another person's head. Interviews the user
  only about the send — who it goes to, what they need back — then writes
  questions aimed at the gap. Pairs with `pm:chart`, whose blocked tickets
  are the common source. Adapted from mattpocock/skills (MIT, © 2026 Matt
  Pocock).
argument-hint: "[topic, or a TEAM-N ticket blocked on someone else's knowledge]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  # Linear — read a blocked ticket as the source; optionally publish as a document
  - mcp__linear-server__get_issue
  - mcp__linear-server__save_issue
  - mcp__linear-server__save_comment
  # Obsidian — optional personal copy
  - mcp__obsidian-mcp__write_note
  # Compose with ndr capture and the linear/pm skills on the way back
  - Skill
upstream:
  repo: mattpocock/skills
  path: skills/productivity/to-questionnaire
  reviewed_sha: 321658273cb1
  reviewed: 2026-08-29
  status: reviewed
---

# to-questionnaire

## Overview

Turn something the user cannot answer alone into a **questionnaire**: a Markdown document they hand to one person to fill in async, or fill out together over a meeting. The recipient holds knowledge the user lacks; the questionnaire pulls it out of them.

**Grill the send, not the subject.** Interview the user only about the *send*, which they can always answer: who it goes to, and what they need back. The questions in the document then target the **gap** between what the recipient knows and what the user needs.

## Procedure

1. **Who is it going to?** Ask, in one exchange, the recipient's role, expertise, and relationship to the user. This fixes the questionnaire's tone and how much context it must carry. Done when you know who the recipient is and what they know that the user does not.

2. **What do you need back?** Ask, in one exchange, the specific decisions or facts the user cannot resolve alone and needs from this person. Done when you have a concrete list of what the user must walk away able to do or decide.

3. **Write the questionnaire.** Draft questions aimed at the gap from steps 1–2, following the *Document structure* below. Write it to `.docs/YYYY-MM-DD-questionnaire-<slug>.md` in the working repo, slug from the topic, and report the path. Outside a repo with a `.docs/` convention, write `to-questionnaire-<slug>.md` in the current directory instead. Done when the file exists and every item the user named in step 2 is covered by a question.

4. **Offer a shared copy** (optional, ask once). The Markdown file is the artifact — it goes to anyone, inside the workspace or out. Where the recipient is a Linear collaborator, offer to publish the same content as a Linear document so the answers land where the work is. Where the user keeps a vault, offer a personal copy via the librarian setup. Neither is the default; a file the user can paste anywhere is.

## Document structure

Frame the document as a **discovery questionnaire**: the user lacks context, the recipient holds it. Order questions most-important-first, since async means you may only get one pass, and group them under `##` headings by theme once there are more than a handful. Write it using the template below.

<questionnaire-template>

# <Questionnaire title>

**Purpose:** why this questionnaire exists and the decision riding on it.

**From:** <the user>, **To:** <the recipient>, **How your answers will be used:** <where they go>

## Context

One paragraph orienting a recipient who was not in the user's head. Enough to answer well, not a page.

## How to answer

Deadline and rough effort. Partial answers and "I don't know" are useful: flag anything you are unsure of rather than skipping it.

## <Theme heading>

One `##` section per theme. Under each, its questions, most-important-first. Every question is one idea, never compound, with an answer stub directly beneath, and a one-line _why this matters_ only where the question could be misread or invite a throwaway answer.

<question-example>
### What load is the system expected to handle at launch?

_Why this matters: it decides whether we provision for burst traffic now or defer it._

>
</question-example>

## Anything else?

A closing catch-all: anything we did not ask that we should know?

</questionnaire-template>

## When the answers come back

The questionnaire exists to unblock a decision, so route what comes back rather than leaving it in the file:

- **A decision the answers now settle** — dispatch the `ndr:capture-decision` skill so the call lands in the durable layer, not in a Markdown file nobody rereads.
- **Work the answers reveal** — the `spec-flow:capture` skill for a single thing, the `pm:breakdown` skill if it is a goal with several slices in it.
- **A `pm:chart` ticket this unblocked** — post the answers as the resolution comment on that ticket and close it, per that skill's resolution step. The questionnaire file is the linked asset, not the resolution.
- **Answers that raise new questions** — that is a normal outcome. A second questionnaire to the same person is cheaper than a guess.

## Rules

- **Never interview the user about the subject.** If you find yourself asking the user a question the recipient is supposed to answer, you have inverted the skill. The user's job is to describe the send; yours is to write the questions.
- **One idea per question.** A compound question gets a compound answer, and async means you cannot follow up cheaply.
- **Do not pad with questions the user did not ask for.** Every item in step 2 must be covered; coverage beyond that is the recipient's time being spent on the user's behalf.
- **Never send it.** This skill writes a document. Handing it to the recipient — email, Slack, a meeting invite — is the user's act.

## Composes with

- **`pm:chart`** (this plugin) — its `Chore` tickets are the common source: manual work blocked on another person's knowledge is a questionnaire.
- **`pm:breakdown`** (this plugin) — for answers that turn out to be a whole goal rather than a single fact.
- **`ndr:capture-decision`** (external ndr plugin) — captures the decision the answers unblock.
- **`spec-flow:capture`** (spec-flow plugin) — files a single piece of revealed work without ceremony.
- **`linear`** (linear plugin) — conventions for the ticket the questionnaire is attached to, and for publishing a shared copy.

## See also

- **`chart`** skill in this plugin — the upstream half of the common flow.
