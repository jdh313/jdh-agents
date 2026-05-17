---
name: start
description: This skill should be used when the user runs `/spec-flow start <goal>` or otherwise signals the start of a new contract-tracked code change. Trigger phrases include "spec-flow start", "open a contract for", "let's scaffold a contract for", "new spec-flow change", "draft a contract for this change". Performs the kickoff lifecycle — flags any other active contracts, runs proactive context-gathering (codebase, library docs via Context7, relevant ndr atoms), conducts a conversational pass asking targeted questions only where the AI's path isn't clear, drafts a five-section contract using the contract template, and writes it to `.docs/YYYY-MM-DD-<slug>.md`. Does NOT start implementation — that requires explicit `/spec-flow implement`.
---

# spec-flow:start

Open a contract for a new code change. Drafts only; does not implement.

## When to invoke

- User runs `/spec-flow start <goal>`.
- User explicitly says "let's spec-flow this" or "open a contract for X".
- User describes a non-trivial change and asks for a contract first.

## Do NOT invoke for

- Trivial changes the user can just do (5-line bugfixes, type fixes, one-file glue). Contracts are opt-in by design.
- Multi-feature roadmaps. spec-flow is single-change-scoped.
- Resuming or implementing an existing contract — that is `spec-flow:implement`.

## Workflow

### 1. Detect other active contracts

List contracts in `.docs/` excluding `archive/`:

```bash
ls .docs/*.md 2>/dev/null || true
```

If any exist, surface them to the user:

> "You have N other active contracts: X, Y. Continue opening a new one?"

Wait for confirmation. Do not block — this is a visibility flag, not a gate.

### 2. Gather context proactively

Before asking the user anything, do legwork:

- **Codebase scan** — Read `CLAUDE.md`, search for patterns the change might touch (`rg` / `grep`), read the entry points relevant to the goal.
- **Library docs** — If the goal mentions a library or framework, resolve and fetch docs via `mcp__plugin_context7_context7__resolve-library-id` then `query-docs`.
- **Relevant ndr atoms** — Scan `~/Loose Ends/Decisions/` for atoms tagged with the area, project, or related concepts.
- **Project rules** — Check `.claude/rules/` if present.

Synthesize: what you have a clear path on vs. what you don't.

### 3. Converse, but only where uncertain

Surface findings to the user in chat:

> "I've read X, Y, Z. Clear path on A, B. Two things I'm not sure about: ..."

Ask targeted questions where the path isn't clear. Do NOT ask open-ended *"what do you want?"* — propose a default and let the user redirect.

If the *how* is non-obvious enough to warrant real deliberation, suggest forking into the debate skill (advocate / devils-advocate / fact-checker / synthesizer). The debate's output — recommended approach plus draft ndr atoms — flows back into the contract's *Approach* section.

### 4. Draft the contract

Use `references/contract-template.md` as the literal scaffold. Five sections:

- **What we're doing** — one or two bullets, plain language.
- **Why** — one or two bullets, trigger or motivation.
- **Approach** — bullets, larger strokes only. No task list, no enumeration.
- **Out of scope** — explicit non-goals.
- **Open questions** — things deferred to during implementation; load-bearing because they shape the handoff cadence later.

Filename: `.docs/YYYY-MM-DD-<slug>.md`. `<slug>` is short kebab-case derived from the goal (e.g. `okta-auth`, `dishka-di-refactor`). Create the `.docs/` directory if it does not exist.

Frontmatter:

```yaml
---
status: active
topic: <slug>
started: YYYY-MM-DD
---
```

### 5. Confirm

Present the drafted contract. Ask the user to read and approve. If amendments are needed, iterate inline before finalizing.

### 6. End

Do NOT proceed to implementation. Tell the user:

> "Contract drafted at `.docs/YYYY-MM-DD-<slug>.md`. Run `/spec-flow implement` when ready to start coding."

## Notes

- Bullets / lists / tables only. No prose paragraphs.
- The contract is an agreement, not a delivery — its purpose is shared model, not enumerated work.
- `.docs/` is gitignored by the user's scratch-artifact convention.
