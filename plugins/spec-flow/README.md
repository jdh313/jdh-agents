# spec-flow

Personal SDLC scaffolding for AI-assisted development. Each code change is wrapped in a lightweight **contract** between user and AI — bullets, not prose; ephemeral, not durable. Durable knowledge migrates elsewhere on done.

## Premise

Existing SDLC tooling fails one of three ways:

- **Verbose prose docs** (openspec, spec-kit) help the AI but overwhelm the human.
- **Rigid phase gates** (spec-kit, Kiro, ce-engineering) shoehorn the user into a fixed workflow.
- **Visibility-ephemeral plans** (Claude Code plan mode) exist for one moment, then can't be re-read.

spec-flow's load-bearing principle is **epistemic fit**: it must work the way *you* think, not impose its own thinking. The contract is the agreement; the bullets are the residue.

## How it works

1. **Kickoff** — `/spec-flow start <goal>` opens a contract in `.docs/YYYY-MM-DD-<name>.md`. If other contracts are already open, the kickoff flags them.
2. **Context-gathering** — AI does proactive research (codebase, library docs via Context7, relevant ndr atoms), then asks targeted questions only where its path isn't clear. Conversation builds the shared model.
3. **Drafting** — Contract gets five sections: *What we're doing*, *Why*, *Approach* (larger strokes only), *Out of scope*, *Open questions*. Bullets/lists/tables, never prose.
4. **(Optional) Debate** — When the *how* is non-obvious, fork into the debate skill (advocate / devils-advocate / fact-checker / synthesizer); recommended approach + draft ndr atoms flow back into the contract.
5. **Implementation** — At handoff, AI asks *"all at once, or check in after a piece?"* and may propose a sensible breakpoint. Cadence decided per session, not persisted.
6. **Amendment** — When reality diverges, AI proposes a contract edit; user signs off before it lands.
7. **Resumption** — `/spec-flow resume <name>` or natural reference (*"pick up okta-auth"*). Multiple contracts in flight are allowed; the resume command matches the prompt to the best fit or asks.
8. **Done** — Explicit signal (*"this is done"*). AI proposes migrations: ndr atoms via `/capture-decision`, README updates via librarian. Contract moves to `.docs/archive/`.

## File layout

```
.docs/
├── 2026-05-17-okta-auth.md         # active contract
├── 2026-05-12-image-pipeline.md    # active contract
└── archive/
    └── 2026-05-03-config-cleanup.md
```

`.docs/` is gitignored by user convention (scratch artifacts).

## Contract shape

See `references/contract-template.md` for the literal scaffold and conventions.

## Composes with

- **[ndr](../ndr/README.md)** — Decision atoms. Context-gathering reads ndrs in the area; *done* migration emits new ones via `/capture-decision`. `spec-flow:close` offers an opt-in `ndr:drift-check` against the contract's diff to catch code-vs-decision drift before archiving.
- **[librarian](../librarian/README.md)** — Vault hygiene. *Done* migration uses librarian for README updates.
- **debate skill** — Advocate / devils-advocate / fact-checker / synthesizer. Forked when approach is uncertain.

## What this plugin is not

- Not a roadmap tool. Single-change-scoped only; no multi-feature planning.
- Not a system-spec maintainer. Durable knowledge lives in README + ndr atoms + code.
- Not a team tool. Solo workflow; no PR gates, no reviewer briefing.
- Not a replacement for `CLAUDE.md` or plan mode. spec-flow's contract layer composes with both.
