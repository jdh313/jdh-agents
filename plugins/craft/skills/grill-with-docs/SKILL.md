---
name: grill-with-docs
description: Grill a plan against this repo's CONTEXT.md glossary and NDR atoms, sharpen terminology, and update CONTEXT.md inline as decisions crystallise. Use when stress-testing a plan against project vocabulary, locking in a domain term, or surfacing drift between code naming and the glossary. Adapted from mattpocock/skills (MIT, © 2026 Matt Pocock).
upstream:
  repo: mattpocock/skills
  path: skills/engineering/grill-with-docs
  reviewed_sha: e3b90b5238f3
  reviewed: 2026-06-11
  status: reviewed
---

Interview the user about every aspect of this plan until reaching a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, propose a recommended answer.

Ask one question at a time. Wait for the user's response before continuing.

If a question can be answered by exploring the codebase, explore the codebase instead of asking.

As terms get resolved during the conversation, update CONTEXT.md inline at the repo root — don't batch.

## Where CONTEXT.md lives

CONTEXT.md lives at the **repo root**. Always. Works the same for personal and work repos.

Create lazily — only when the first term is resolved in conversation. Don't pre-create empty files.

A repo earns a CONTEXT.md when it has internal vocabulary not covered by external sources (vault wiki pages for personal repos; internal Carta docs for work repos). One-off scratch repos and pure-config repos often don't earn one.

## What CONTEXT.md is and isn't

- **Is:** a glossary of terms specific to *this repo*. One-line definitions, banned aliases, optional `_See_:` pointers.
- **Is not:** a spec, a design doc, a scratch pad, or a decision log. Rationale lives in NDR atoms. What-we-did lives in code. CONTEXT.md only answers "what do we call this thing?"

If a section is growing past a glossary entry into prose explanation, the prose belongs in code docstrings, an NDR atom, or a vault wiki page — not CONTEXT.md.

## Maintenance discipline

CONTEXT.md is **skill-maintained**, not hand-maintained. This skill is the canonical writer. Don't ask the user to "go update CONTEXT.md when you have time." Either propose the edit in conversation and apply it now, or note it as a follow-up the next session picks up.

The user can still edit CONTEXT.md directly. If they do, the skill respects those edits and treats them as inputs.

## Format

See [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

Quick reference:

```markdown
# {Repo Name}

{One or two sentence description of what this repo is.}

## Language

**Term**
One- or two-sentence definition. Define what it IS.
_Avoid_: alias1, alias2, alias3
_See_: [[Vault Wiki Page]] OR ndr:area/topic/NNNN-slug
```

## Conversation moves

### Challenge against the glossary

When the user uses a term that conflicts with CONTEXT.md, call it out immediately. "CONTEXT.md defines `cancellation` as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When either side uses vague or overloaded terms, propose a precise canonical term. "You said `account` — do you mean the Customer or the User? Those are different things."

Either side may propose the canonical name first. The agent often spots drift the human has stopped noticing; the human often has the lived-experience name. Record the agreed term either way.

### Cross-reference with code

When a statement about behavior conflicts with the code, surface it. "The code calls this `cancelOrder` but you said partial cancellation is supported — does CONTEXT.md need a different term, or does the code need a rename?"

### Test concept boundaries with edge cases

When a term's scope is unclear, invent an edge case that forces the boundary. "If a customer cancels half the items on an order, is that still a `cancellation`, or do we need a separate term for partial cancellation?" The goal is to expose where one concept ends and another begins *before* the glossary entry locks in a fuzzy boundary. Keep edge cases pointed at terminology, not at general plan correctness — boundary-finding for the glossary, not a test plan.

### Update CONTEXT.md inline

When a term is resolved, update CONTEXT.md right then. Don't batch. Use the format in CONTEXT-FORMAT.md.

CONTEXT.md is **devoid of implementation details and rationale**. Don't paste paragraphs of decision context. The definition goes in CONTEXT.md; the rationale (if any) becomes an NDR atom via `/capture-decision`.

## Linking out

Two link conventions, both pragmatic — they work fully when the reader is in the right tool, and read as legible text otherwise.

- **`_See_: [[Wiki Page]]`** — pointer to a vault wiki page that holds deeper context. Renders as a live link in Obsidian; legible-as-text in code editors and agent context.
- **`_See_: ndr:area/topic/NNNN-slug`** — pointer to an NDR atom that holds the decision rationale. Resolved via `/decisions` or `@ndr-reader`.

Do **not** mix vault wikilinks into CONTEXT.md for **Carta repos** — Carta code is proprietary; the vault is personal. Carta cross-repo terms get an internal Carta authority (a `CONTEXT-MAP.md` in a shared internal docs repo) when/if that's worth setting up. Personal repos can link to the personal vault freely.

## Offering NDR atoms

NDR atoms replace the in-repo ADRs (`docs/adr/*.md`) of the source skill — same decision gate, different destination and authority. Rationale lives in the NDR ledger, written via `/capture-decision`; this skill never writes decision records to the repo directly.

Only offer to capture an NDR atom when **all three** hold:

1. **Hard to reverse** — meaningful cost to changing the decision later
2. **Surprising without context** — a future reader will wonder why
3. **The result of a real trade-off** — genuine alternatives existed and one was picked for specific reasons

Skip if any is missing. If offering, route through `/capture-decision` — don't write atoms directly.

## Composition with other plugins

- **`spec-flow:start`** may invoke this skill when contested vocabulary surfaces during contract drafting. Soft composition only — both plugins work standalone.
- **`/capture-decision`** (ndr plugin) is the canonical route for converting a resolved-but-rationale-bearing decision into a durable NDR atom. Don't write atom files directly.
- **`/drift-check`** (ndr plugin) can be extended to flag drift between CONTEXT.md term definitions and code naming. Out of scope for this skill — flag candidates for follow-up rather than fixing inline.

## Explicit non-goals

- **No example dialogue.** Definitions only — no demonstrative "dev meets domain expert" conversation. Write-once-never-maintained content. Skip.
- **No prose explanations.** Definitions only. Pressure to grow CONTEXT.md beyond a glossary is a sign content belongs elsewhere (code, NDR, wiki).
- **No CONTEXT-MAP.md for personal repos.** Multi-context maps are for proprietary monorepos with bounded contexts; personal repos use vault wiki pages as the cross-cutting authority.
