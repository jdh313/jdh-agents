---
name: draft
description: This skill should be used when the user runs `/spec-flow draft <goal>` or otherwise signals the start of a new contract-tracked code change. Trigger phrases include "spec-flow draft", "open a contract for", "let's scaffold a contract for", "new spec-flow change", "draft a contract for this change", "open a new ticket and draft a contract". Performs the kickoff lifecycle — detects the contract host (`.docs/` file, existing Linear ticket, or a NEW Linear ticket created at draft time), flags any other active contracts, runs proactive context-gathering (codebase, library docs via Context7, relevant ndr atoms), conducts a conversational pass asking targeted questions only where the AI's path isn't clear, drafts a six-section contract using the contract template, and writes it to the chosen host. Upgrades `status: captured` stubs from `spec-flow:capture` in place. Does NOT start implementation — that requires explicit `/spec-flow implement`.
---

# spec-flow:draft

Open a contract for a new code change. Drafts only; does not implement.

A contract has a **host** — either a `.docs/` file or an existing Linear ticket. The contract *shape* is host-agnostic; the host changes only where the body is written. See `../../references/hosts.md` for the dual-host model.

## When to invoke

- User runs `/spec-flow draft <goal>`.
- User explicitly says "let's spec-flow this" or "open a contract for X".
- User describes a non-trivial change and asks for a contract first.

## Do NOT invoke for

- Trivial changes the user can just do (5-line bugfixes, type fixes, one-file glue). Contracts are opt-in by design.
- Multi-feature roadmaps. spec-flow is single-change-scoped.
- Resuming or implementing an existing contract — that is `spec-flow:implement`.

## Workflow

### 1. Detect host

Parse the goal text for a Linear ticket token (`^[A-Z]{2,5}-\d+$`):

- **Explicit new-ticket framing** (`open a new ticket and ...`, `new linear ticket for ...`, `create a ticket as the contract`) → **linear-new** host: a fresh ticket created at write time (step 6). No ticket token needed.
- **No ticket token** (and no new-ticket framing) → **file** host. Proceed. If the goal names an existing `status: captured` stub in `.docs/` (or the slug matches one), this draft is the stub's second touch — it will be upgraded in place at step 6.
- **Ticket token framed as the contract** (`the contract is TEAM-123`, `use TEAM-123`, `implement TEAM-123`, or bare `TEAM-123`) → **linear** host.
- **Ticket token framed as a reference** (`see TEAM-123`, `regarding TEAM-123`, `the work in TEAM-123`, `draft a contract for TEAM-123`) → **ask once**: *"Use TEAM-123 itself as the contract, or draft a `.docs/` file that references it?"* Use the user's answer.
- **Explicit file framing** (`draft as .docs/`, `as a file`) → **file** host even if a ticket token is present.

If host = linear or linear-new, check that `mcp__linear-server__*` tools are loaded. If not:

> "Linear MCP server isn't connected — I can't read or write the ticket. Fall back to a `.docs/` file contract, or pause while you wire up the MCP yourself?"

Do not run `claude mcp add` or suggest a paste-and-go connect command. Wait for the user.

Full detection table and rationale: `../../references/hosts.md`.

### 2. Detect other active contracts

List file-host contracts in `.docs/` excluding `archive/` (skip `status: captured` stubs — captures aren't contracts):

```bash
ls .docs/*.md 2>/dev/null || true
```

If the Linear MCP is connected, also enumerate Linear-host contracts: `mcp__linear-server__list_issues` filtered to the `contracted` label (team per the linear plugin's conventions; **no assignee filter** — show all team contracts regardless of owner). The label is the canonical "this is a contract" signal — more robust than sniffing the description for the six-section shape, and independent of whatever workflow state the ticket sits in. Match the label name case-insensitively. If the team has no `contracted` label yet, there are no Linear-host contracts to surface. Display the assignee for each contract so ownership is visible.

If any exist (either host), surface them to the user:

> "You have N other active contracts: X, Y. Continue opening a new one?"

Wait for confirmation. Do not block — this is a visibility flag, not a gate. If the Linear MCP isn't connected, note that Linear contracts weren't checked.

### 3. Gather context proactively

Before asking the user anything, do legwork:

- **Codebase scan** — Read `CLAUDE.md`, search for patterns the change might touch (`rg` / `grep`), read the entry points relevant to the goal.
- **Library docs** — If the goal mentions a library or framework, resolve and fetch docs via `mcp__plugin_context7_context7__resolve-library-id` then `query-docs`.
- **Installed version** — If the goal names a specific dep, check the installed major version in the target repo (`bun info <pkg>`, `npm ls <pkg>`, `pip show <pkg>`, `cargo tree | grep <pkg>`, etc.) before drafting against the docs. Docs-vs-installed drift is a common amendment trigger.
- **Relevant ndr atoms** — If the `ndr` plugin is installed, hand off to it to surface atoms scoped to this project/repo for the area or related concepts.
- **Project rules** — Check `.claude/rules/` if present.
- **Linear host (existing ticket) only** — Read the existing ticket description via `mcp__linear-server__get_issue`. Treat it as input to drafting (stakeholder context, what the PM or you-yesterday wrote — often a `spec-flow:capture` Goal/Context body). The body is overwritten by default at step 6, so its length no longer gates a prompt — it's drafting input only.
- **Captured file stub only** — Read the stub's Goal/Context as drafting input, same role as an existing ticket body.

Synthesize: what you have a clear path on vs. what you don't.

### 4. Converse, but only where uncertain

Surface findings to the user in chat:

> "I've read X, Y, Z. Clear path on A, B. Two things I'm not sure about: ..."

Ask targeted questions where the path isn't clear. Do NOT ask open-ended *"what do you want?"* — propose a default and let the user redirect.

If the *done* state isn't obvious from the goal — i.e. you can't list 2–3 observable outcomes confidently — surface a proposed *Done when* draft and ask the user to confirm/correct before writing the contract. The Done-when section is what the close skill reviews against; thin drafting here means a fuzzy close later.

If the *how* is non-obvious enough to warrant real deliberation, suggest forking into the debate skill (advocate / devils-advocate / fact-checker / synthesizer). The debate's output — recommended approach plus draft ndr atoms — flows back into the contract's *Approach* section.

If contested or fuzzy vocabulary surfaces during the conversation — terms used inconsistently, ambiguous nouns, drift between code naming and how the user is talking about the change — and the `craft` plugin is installed, suggest invoking `/grill-with-docs` to lock the terms down in the repo's `CONTEXT.md` glossary before drafting. Soft composition: spec-flow:draft works fine without craft installed; the suggestion simply doesn't fire if the skill isn't available.

If the change **designs or extends a model that spans dimensions** — adding a second/orthogonal axis, a new role/tier, or a new principal type to an authz scheme, permission table, state machine, data model, or tenancy model — and the `craft` plugin is installed, suggest invoking `/interrogate-model` to check the extended model's representability *before* drafting the Approach. This is the design-time catch for emergent cross-axis conflations (decisions made weeks apart fusing at the seam). Same soft composition as above — the suggestion simply doesn't fire if craft isn't installed.

### 5. Draft the contract

Use `../../references/contract-template.md` as the literal scaffold. Six sections:

- **What we're doing** — one or two bullets, plain language.
- **Why** — one or two bullets, trigger or motivation.
- **Approach** — bullets, larger strokes only. No task list, no enumeration.
- **Out of scope** — explicit non-goals.
- **Done when** — 2–4 bullets describing observable outcomes (what's visibly different when the change ships). Bullets, not checkboxes. Load-bearing for the close skill's review.
- **Open questions** — things deferred to during implementation; load-bearing because they shape the handoff cadence later.

The shape is identical for both hosts.

### 6. Write to the host

Approval is host-dependent:

- **File host** — present the drafted contract in chat and ask the user to read and approve. Iterate inline before finalizing. (A `.docs/` file has no review surface of its own, so chat is where review happens.)
- **Linear hosts (existing or new)** — write immediately, **no in-chat approval gate**. The contract body lands in the ticket description and the user reviews it in Linear. Don't paste the full contract into chat — report the ticket ID and a one-line summary. If the user wants changes after reading it in Linear, they say so and the description gets updated (no `amend` ceremony before implementation starts).

Write to the chosen host:

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

If the draft upgrades a `status: captured` stub: rewrite that file in place (keep the filename), flip `status` to `active`, set `started` to today, and keep the original `captured:` date line.

**Linear-new host (fresh ticket created at draft):**

1. Derive a title from the goal per the linear plugin's title conventions (noun-phrase). No confirmation — the user reviews title and body together in Linear and can rename there.
2. Create the ticket via `mcp__linear-server__save_issue` with the six-section contract as the description, `assignee="me"` (self-assign per linear plugin conventions), deferring all other fields (team, project, labels, priority) to the `linear` skill's conventions.
3. Report the new ticket ID, then continue with the `contracted` label application below as if it were an existing-ticket host.

**Linear host (existing ticket):**

**Concurrent-edit guard:** Before writing, compare the ticket's current description (from the `get_issue` call in step 3) to what you're about to overwrite. If the description changed between when you read it and now — i.e. a second `get_issue` call returns different content — warn the user and offer three choices:

> "The ticket description changed since I last read it (someone may have edited concurrently). Merge my draft over theirs, overwrite anyway, or abort and let you resolve it?"

Wait for the user's choice before proceeding. If no re-fetch was done (e.g. the ticket was read only in step 3 and no time has passed in the session), proceed without the guard — re-fetching every write would be noisy in practice.

Overwrite the ticket's description with the formatted contract via `mcp__linear-server__save_issue`. Overwrite is the default — do **not** prompt, even when the existing description is substantive.

Exception — only when the user explicitly asked to preserve the existing text (e.g. "prepend", "keep the description", "don't overwrite") in the goal or during the conversation. In that case, prepend the contract above the original instead of replacing it.

No frontmatter in Linear-hosted contracts. The ticket's own metadata (state, assignee, labels) is the workflow signal; the contract body holds only the 6 sections.

**Linear host — apply the `contracted` label.** Once the contract body is written, mark that the artifact exists by applying a label. This is orthogonal to workflow state — **do NOT change the issue's state.** Leave it wherever it is (a Todo ticket stays Todo; it just gains the label).

- List the team's labels via `mcp__linear-server__list_issue_labels` (the team comes from the issue read in step 3). Find one named `contracted` (case-insensitive match).
- If no such label exists, create it once via `mcp__linear-server__create_issue_label` with name `contracted` and description "Has a spec-flow contract in the description; ready for /spec-flow implement". If creation isn't possible (e.g. permissions), tell the user once — *"No `contracted` label on this team and I couldn't create one; skipping the label step. Create a `contracted` label to enable contract detection."* — and skip the rest of this step.
- Apply the label **append-only** — never drop the issue's existing labels. `save_issue`'s `labels` field replaces the full label set (it is not additive and there is no remove-labels parameter), so set the union: take the issue's current labels (from the step-3 `get_issue` read), add `contracted` if absent, and pass the combined list to `mcp__linear-server__save_issue` (`labels` field). If the issue already carries `contracted`, this is a no-op.

### 7. End

Do NOT proceed to implementation. Tell the user:

- **File host:** *"Contract drafted at `.docs/YYYY-MM-DD-<slug>.md`. Run `/spec-flow implement` when ready to start coding."*
- **Linear host:** *"Contract written to TEAM-123 and the `contracted` label applied (state left as-is) — review it in Linear. Run `/spec-flow implement TEAM-123` when it reads right."*

## Notes

- Bullets / lists / tables only. No prose paragraphs.
- The contract is an agreement, not a delivery — its purpose is shared model, not enumerated work.
- `.docs/` is gitignored by the user's scratch-artifact convention.
- Host is not persisted. `implement`, `amend`, and `close` re-detect host from the identifier each time.
- spec-flow does not own Linear-side conventions (title patterns, general labels, the team's status taxonomy). It writes the contract body, applies the `contracted` label at `draft`, and drives the lifecycle state transitions — → In Progress at `implement`, → a review state at `close` (never Done — that's the user's at merge). `draft` does **not** transition state on Linear hosts; "a contract exists" is the `contracted` label, orthogonal to workflow state. Broader Linear workflow lives outside spec-flow.
