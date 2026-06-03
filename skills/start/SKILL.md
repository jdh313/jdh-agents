---
name: start
description: This skill should be used when the user runs `/spec-flow start <goal>` or otherwise signals the start of a new contract-tracked code change. Trigger phrases include "spec-flow start", "open a contract for", "let's scaffold a contract for", "new spec-flow change", "draft a contract for this change". Performs the kickoff lifecycle — detects the contract host (`.docs/` file or existing Linear ticket), flags any other active contracts, runs proactive context-gathering (codebase, library docs via Context7, relevant ndr atoms), conducts a conversational pass asking targeted questions only where the AI's path isn't clear, drafts a six-section contract using the contract template, and writes it to the chosen host. Does NOT start implementation — that requires explicit `/spec-flow implement`.
---

# spec-flow:start

Open a contract for a new code change. Drafts only; does not implement.

A contract has a **host** — either a `.docs/` file or an existing Linear ticket. The contract *shape* is host-agnostic; the host changes only where the body is written. See `references/hosts.md` for the dual-host model.

## When to invoke

- User runs `/spec-flow start <goal>`.
- User explicitly says "let's spec-flow this" or "open a contract for X".
- User describes a non-trivial change and asks for a contract first.

## Do NOT invoke for

- Trivial changes the user can just do (5-line bugfixes, type fixes, one-file glue). Contracts are opt-in by design.
- Multi-feature roadmaps. spec-flow is single-change-scoped.
- Resuming or implementing an existing contract — that is `spec-flow:implement`.

## Workflow

### 1. Detect host

Parse the goal text for a Linear ticket token (`^[A-Z]{2,5}-\d+$`):

- **No ticket token** → **file** host. Proceed.
- **Ticket token framed as the contract** (`the contract is TEAM-123`, `use TEAM-123`, `implement TEAM-123`, or bare `TEAM-123`) → **linear** host.
- **Ticket token framed as a reference** (`see TEAM-123`, `regarding TEAM-123`, `the work in TEAM-123`, `draft a contract for TEAM-123`) → **ask once**: *"Use TEAM-123 itself as the contract, or draft a `.docs/` file that references it?"* Use the user's answer.
- **Explicit file framing** (`draft as .docs/`, `as a file`) → **file** host even if a ticket token is present.

If host = linear, check that `mcp__linear-server__*` tools are loaded. If not:

> "Linear MCP server isn't connected — I can't read or write the ticket. Fall back to a `.docs/` file contract, or pause while you wire up the MCP yourself?"

Do not run `claude mcp add` or suggest a paste-and-go connect command. Wait for the user.

Full detection table and rationale: `references/hosts.md`.

### 2. Detect other active contracts

List file-host contracts in `.docs/` excluding `archive/`:

```bash
ls .docs/*.md 2>/dev/null || true
```

If any exist, surface them to the user:

> "You have N other active contracts: X, Y. Continue opening a new one?"

Wait for confirmation. Do not block — this is a visibility flag, not a gate. Linear-host contracts are not enumerable cheaply and are skipped at this step; the user is responsible for knowing whether other tickets are in flight.

### 3. Gather context proactively

Before asking the user anything, do legwork:

- **Codebase scan** — Read `CLAUDE.md`, search for patterns the change might touch (`rg` / `grep`), read the entry points relevant to the goal.
- **Library docs** — If the goal mentions a library or framework, resolve and fetch docs via `mcp__plugin_context7_context7__resolve-library-id` then `query-docs`.
- **Installed version** — If the goal names a specific dep, check the installed major version in the target repo (`bun info <pkg>`, `npm ls <pkg>`, `pip show <pkg>`, `cargo tree | grep <pkg>`, etc.) before drafting against the docs. Docs-vs-installed drift is a common amendment trigger.
- **Relevant ndr atoms** — If the `ndr` plugin is installed, hand off to it to surface atoms scoped to this project/repo for the area or related concepts.
- **Project rules** — Check `.claude/rules/` if present.
- **Linear host only** — Read the existing ticket description via `mcp__linear-server__get_issue`. Treat it as input to drafting (stakeholder context, what the PM or you-yesterday wrote). The body is overwritten by default at step 6, so its length no longer gates a prompt — it's drafting input only.

Synthesize: what you have a clear path on vs. what you don't.

### 4. Converse, but only where uncertain

Surface findings to the user in chat:

> "I've read X, Y, Z. Clear path on A, B. Two things I'm not sure about: ..."

Ask targeted questions where the path isn't clear. Do NOT ask open-ended *"what do you want?"* — propose a default and let the user redirect.

If the *done* state isn't obvious from the goal — i.e. you can't list 2–3 observable outcomes confidently — surface a proposed *Done when* draft and ask the user to confirm/correct before writing the contract. The Done-when section is what the close skill reviews against; thin drafting here means a fuzzy close later.

If the *how* is non-obvious enough to warrant real deliberation, suggest forking into the debate skill (advocate / devils-advocate / fact-checker / synthesizer). The debate's output — recommended approach plus draft ndr atoms — flows back into the contract's *Approach* section.

If contested or fuzzy vocabulary surfaces during the conversation — terms used inconsistently, ambiguous nouns, drift between code naming and how the user is talking about the change — and the `craft` plugin is installed, suggest invoking `/grill-with-docs` to lock the terms down in the repo's `CONTEXT.md` glossary before drafting. Soft composition: spec-flow:start works fine without craft installed; the suggestion simply doesn't fire if the skill isn't available.

### 5. Draft the contract

Use `references/contract-template.md` as the literal scaffold. Six sections:

- **What we're doing** — one or two bullets, plain language.
- **Why** — one or two bullets, trigger or motivation.
- **Approach** — bullets, larger strokes only. No task list, no enumeration.
- **Out of scope** — explicit non-goals.
- **Done when** — 2–4 bullets describing observable outcomes (what's visibly different when the change ships). Bullets, not checkboxes. Load-bearing for the close skill's review.
- **Open questions** — things deferred to during implementation; load-bearing because they shape the handoff cadence later.

The shape is identical for both hosts.

### 6. Confirm and write to the host

Present the drafted contract. Ask the user to read and approve. If amendments are needed, iterate inline before finalizing.

Then write to the chosen host:

**File host:**

Filename: `.docs/YYYY-MM-DD-<slug>.md`. `<slug>` is short kebab-case derived from the goal (e.g. `okta-auth`, `dishka-di-refactor`). Create the `.docs/` directory if it does not exist.

Frontmatter (file-only — Linear has no frontmatter):

```yaml
---
status: active
topic: <slug>
started: YYYY-MM-DD
---
```

**Linear host:**

Overwrite the ticket's description with the formatted contract via `mcp__linear-server__save_issue`. Overwrite is the default — do **not** prompt, even when the existing description is substantive.

Exception — only when the user explicitly asked to preserve the existing text (e.g. "prepend", "keep the description", "don't overwrite") in the goal or during the conversation. In that case, prepend the contract above the original instead of replacing it.

No frontmatter in Linear-hosted contracts. The ticket's own metadata (state, assignee, labels) is the workflow signal; the contract body holds only the 6 sections.

**Linear host — move to Contract Review.** Once the contract body is written, the contract is ready to be reviewed. Transition the ticket's state:

- Fetch the team's workflow states via `mcp__linear-server__list_issue_statuses` (the team comes from the issue read in step 3).
- Find the state named "Contract Review" (case-insensitive match).
- Set it via `mcp__linear-server__save_issue` (state field).
- If no such state exists on the team, tell the user once — *"No 'Contract Review' state on this team; leaving status unchanged."* — and skip. Do not guess a different state.

### 7. End

Do NOT proceed to implementation. Tell the user:

- **File host:** *"Contract drafted at `.docs/YYYY-MM-DD-<slug>.md`. Run `/spec-flow implement` when ready to start coding."*
- **Linear host:** *"Contract written to TEAM-123's description and moved to Contract Review. Run `/spec-flow implement TEAM-123` when ready to start coding."*

## Notes

- Bullets / lists / tables only. No prose paragraphs.
- The contract is an agreement, not a delivery — its purpose is shared model, not enumerated work.
- `.docs/` is gitignored by the user's scratch-artifact convention.
- Host is not persisted. `implement`, `amend`, and `close` re-detect host from the identifier each time.
- spec-flow does not own Linear-side conventions (title patterns, labels, the team's status taxonomy). It writes the contract body and drives the lifecycle state transitions — → Contract Review at `start`, → In Progress at `implement`, → a review state at `close` (never Done — that's the user's at merge). Broader Linear workflow lives outside spec-flow.
