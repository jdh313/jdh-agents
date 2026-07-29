# spec-flow

Personal SDLC scaffolding for AI-assisted development. Each code change is wrapped in a lightweight **contract** between user and AI — bullets, not prose; ephemeral, not durable. Durable knowledge migrates elsewhere on done.

## Premise

Existing SDLC tooling fails one of three ways:

- **Verbose prose docs** (openspec, spec-kit) help the AI but overwhelm the human.
- **Rigid phase gates** (spec-kit, Kiro, ce-engineering) shoehorn the user into a fixed workflow.
- **Visibility-ephemeral plans** (Claude Code plan mode) exist for one moment, then can't be re-read.

spec-flow's load-bearing principle is **epistemic fit**: it must work the way *you* think, not impose its own thinking. The contract is the agreement; the bullets are the residue.

## How it works

0. **Capture** — `/spec-flow capture <thought>` is stage zero: a future change idea becomes a minimal artifact with zero ceremony — no questions, no research. Linear host: a Backlog ticket (fields per the `linear` plugin's conventions). File host: a `.docs/` stub with `status: captured`. Draft is typically the *second* touch on the captured artifact. Many captures never become contracts — that's fine.
1. **Kickoff** — `/spec-flow draft <goal>` opens a contract. Default host is `.docs/YYYY-MM-DD-<name>.md` in the working repo. If the goal names a Linear ticket as the contract (`/spec-flow draft "the contract is TEAM-123"`), the kickoff writes the contract to the ticket description instead; phrasing like *"open a new ticket and draft …"* creates the ticket fresh (fields per the `linear` plugin). Linear drafts write **without an in-chat approval gate** — the user reviews the contract in Linear; file drafts are approved in chat first since a `.docs/` file has no review surface of its own. The kickoff flags other active contracts on both hosts — `.docs/` files plus Linear tickets carrying the `contracted` label. See `references/hosts.md`.
2. **Context-gathering** — AI does proactive research (codebase, library docs via Context7, relevant ndr atoms), then asks targeted questions only where its path isn't clear. Conversation builds the shared model.
3. **Drafting** — The contract is a **worksheet split across two documents** by audience. The durable **contract doc** holds cold-legible *front-matter* (*What we're doing*, *Why*, *Out of scope*, *Done when*) and lives on the chosen host — that is the surface you sign off and amend. The throwaway **companion doc** holds the *working-matter* ledger (*Approach / wiring* plus a three-state *Decision log* whose rows are born `[open]`, resolve to `[resolved]`, or punt to `[deferred]`) and always lives at `.docs/YYYY-MM-DD-<name>-companion.md`, on both hosts. Mid-flight churn therefore never touches your sign-off surface, and "working-matter evaporates" is literal — `close` deletes the companion. Bullets/lists/tables, never prose. See `references/contract-template.md`.
4. **(Optional) Debate** — When the *how* is non-obvious, fork into the debate skill (advocate / devils-advocate / fact-checker / synthesizer); recommended approach + a saved decision record flow back into the contract.
5. **Implementation** — At handoff, AI asks *"all at once, or check in after a piece?"* and may propose a sensible breakpoint. Cadence decided per session, not persisted. Then a **red phase**: the **`redphase-author`** agent compiles each *Done when* bullet into an automated test that **fails**, and commits those tests before any implementation code exists. The author is deliberately isolated — it gets the contract, never the plan — because a test author who can see the implementation writes tests the implementation passes. Implementation then works those tests green. Before declaring done, the **`contract-verifier`** agent independently runs each *Done when* bullet in isolated context and returns a met / not-met / drifted verdict — verification is behavioral, not a diff-read. Two gates, different evidence.
6. **Amendment** — When reality diverges, AI proposes a contract edit; user signs off before it lands. On Linear-host contracts the before/after is also posted as a ticket comment — the description overwrite would otherwise erase the history.
7. **Resumption** — `/spec-flow implement <name>` or natural reference (*"pick up okta-auth"*). Resumption is just `implement` re-detecting prior work from git/jj state — there's no separate `resume` subcommand. Multiple contracts in flight are allowed; `implement` matches the prompt against active contracts on both hosts or asks.
8. **Done** — Explicit signal (*"this is done"*). AI proposes migrations from the companion: ndr atoms via `/capture-decision`, README updates via librarian. Once those land, **the companion is deleted** — on both hosts, and only after the harvest, so the deletion is the drain's completion signal rather than a loss. The contract doc survives: file-host ones move to `.docs/archive/`; Linear-host ones get the contract-verifier's per-bullet verdict posted as a comment, keep their body intact, and advance to a review state (see *Linear status lifecycle* below).

### Linear status lifecycle

On a Linear-host contract, "a contract exists" is a **`contracted` label**, not a workflow state — orthogonal axes. At kickoff `draft` applies the label and **leaves the ticket's state untouched** (a Todo ticket stays Todo and just gains the label; you move it to a started state independently when actively designing). spec-flow advances state only twice: → **In Progress** when implementation starts, → a **review state** at done; `close` also strips the `contracted` label as the contract migrates to the durable layer. It never sets a completed state (Done/Closed) — merge happens outside the contract lifecycle, so that flip stays yours. Target states and the label are resolved by name (never hardcoded), matched case-insensitively, and skipped gracefully if the team doesn't define them.

## File layout

```
.docs/
├── 2026-05-17-okta-auth.md              # active file-host contract doc
├── 2026-05-17-okta-auth-companion.md    # its working-matter companion
├── 2026-05-12-image-pipeline.md         # active file-host contract doc
├── 2026-05-12-image-pipeline-companion.md
├── 2026-06-14-billing-companion.md      # companion for Linear-host contract TEAM-88
├── 2026-06-02-rate-limit-idea.md        # captured stub (status: captured) — not yet a contract
└── archive/
    └── 2026-05-03-config-cleanup.md     # closed contract doc; its companion was deleted
```

`.docs/` is gitignored by user convention (scratch artifacts). Linear-host contracts keep their *front-matter* in the ticket description, but still leave a companion on disk — that is the one file-system footprint they have. Captured stubs have no companion; `draft` creates it when it upgrades the stub.

## Contract shape

See `references/contract-template.md` for the literal scaffold and conventions. The contract doc is host-agnostic and the companion is always a `.docs/` file — see `references/hosts.md` for the two-document model, the dual-host model, and the host-selection heuristic.

## Composes with

- **linear** (sibling plugin in this marketplace) — Owns ticket mechanics: team, title shape, labels, priority, status semantics, MCP gotchas. `capture` and Linear-new `draft` create tickets by deferring to its conventions; spec-flow never hardcodes Linear-side fields.
- **ndr** (ships from its own separate marketplace) — Decision atoms. Context-gathering reads ndrs in the area; *done* migration emits new ones via `/capture-decision`. `spec-flow:close` offers an opt-in `ndr:drift-check` against the contract's diff to catch code-vs-decision drift before archiving. Optional — without it, the ndr steps are skipped.
- **librarian** (personal setup, not in this marketplace) — Vault hygiene. *Done* migration uses librarian for README updates when present; otherwise the repo README is edited directly.
- **debate skill** — Advocate / devils-advocate / fact-checker / synthesizer. Forked when approach is uncertain.

## What this plugin is not

- Not a roadmap tool. Single-change-scoped only; no multi-feature planning.
- Not a system-spec maintainer. Durable knowledge lives in README + ndr atoms + code.
- Not a process-enforcement tool. Works solo or small-team (assignee claiming, outcome summaries, opt-in reviewer routing), but imposes no PR gates and no mandatory review flow.
- Not a replacement for `CLAUDE.md` or plan mode. spec-flow's contract layer composes with both.
