# Craft registered Codex agent acceptance

Date: 2026-10-01. Migration order: Linear → Craft → Librarian; this work
migrates Craft only. EM receives a minimal verification-caller adapter and
patch version bump; it remains Claude-only. No push or release is authorized.

## Inputs and pre-edit inventory

| Layer | Input |
|---|---|
| Repository/base | Clean JJ working copy in `jdh-agents`, parent `2a1bd1d2e73539304dc74c9ccd85e3d7beec6e86`, published Linear bookmark |
| Package | Craft 0.15.0 → 0.16.0; EM caller adapter 1.0.0 → 1.0.1 |
| Compiler | Released AgentForge v1.2.0; wrapper pin unchanged |
| Consumer binary | Absolute resolved repository `.cache/agentforge/1.2.0/agentforge-darwin-arm64`; exact path saved locally |
| SHA-256 | `67107b2a96892a1a3429010bbb8475d61c4100e1ac01783367e23aef402c2d54` |
| Runtime/platform | Codex CLI 0.158.0, Darwin arm64 |
| Tracker reads | JUN-439–443 Done; JUN-444 In Review; no distinct Craft migration issue established in that project |
| NDR grounding | Current heads `6x3v6p` and `kpefq4`, resolved through CLI |

`AGENTS.md`, `CLAUDE.md`, the operating model, compiler compatibility,
Debate/Linear source and lifecycle/acceptance records, and Craft's package,
runtime adapter, all agents and their calling procedures were read first.
The count was rechecked: exactly three canonical agents, with emitted names
`craft:house-style-reviewer`, `craft:comment-reviewer`, and
`craft:copy-reviewer`. Each has Claude `model: sonnet` and a repository-reading
tool filter; none requires a connector or bundled runtime resource.

House style reviews naming, placement, error shape, API idioms and test
structure. Comment review expands changed hunks to enclosing declarations,
including unchanged stale comments, and reads history/blame. Copy review
compares changed user-facing strings with the existing product corpus. All
three return grounded advisory reports, never edit, and exclude correctness
and linter-enforced findings. No role authorizes repository, tracker, vault,
message, commit, or publication side effects.

The sole direct named-role caller is `plugins/em/references/verify.md`.
Craft's `derive-conventions` consumes findings but does not dispatch these
roles. Generic callers remain generic: `grill` fact-finding, `grok-explorer`,
`arch-explorer` in `improve-codebase-architecture`, `model-cartographer` in
`interrogate-model`, and the architecture skill's `DESIGN-IT-TWICE.md` fan-out.
The last three named explorer workflows retain addressable follow-ups; those
labels are not packaged registered roles. `infra-review` describes a future
companion and does not dispatch it; `design-by-stories` has an Agent
permission without a dispatch operation.

Craft's wider skills can write convention files, reports, prototypes, tests,
conflict resolutions, vault records, NDRs and Lucid diagrams. Those side effects
are not authorized by migrating the three reviewers. The Lucid skill's MCP
dependency and fallback are unchanged; no live connector write is tested.

## Bounded acceptance fixtures defined before editing

The definition was saved before canonical edits at
`/private/tmp/craft-codex-plan-20261001/pre-edit-fixtures.md`. Separate isolated
user/project/fallback Codex homes and trusted disposable Git projects have
apps disabled and no MCP servers. A committed baseline plus one controlled
working diff supplies three positives:

- House style: `fetchInvoice` against declared snake_case guidance and three
  sibling public functions; naming is not covered by the fixture linter.
- Comments: an unchanged "amount in cents" docstring above a changed body
  returning dollars, with baseline history available for blame.
- Copy: changed `DELETE ACCOUNT NOW!!!` against declared sentence-case/no
  terminal punctuation and existing `Save changes`, `Cancel`, `Delete account`.

The fixture includes unrelated `notes.txt`, guidance, convention and linter
config. Review sessions must preserve repository bytes/modes/mtimes, Git HEAD
and status. Initial fixture commits and deliberate lifecycle edits happen only
in disposable repositories. Native user/project fan-out, a same-reviewer
follow-up, a generic architecture explorer follow-up, separate Markdown child
and inline procedures, and missing/stale-registration refusal are the bounded
runtime tests. Full interactive design, vault, integration, and mutation flows
are excluded. Raw traces stay local rather than being committed.

## Source, generated output, installed state and runtime

Acceptance is in progress. Source/generated commit, cache equality, setup
activation, selected-scope checks, exact dispatch, observed instruction
behavior/settings, side effects, cleanup, gates and Git outcome will be
recorded separately after verification. A compiled TOML or packaged Markdown
file alone is not runtime acceptance. Unobserved values will be unknown.
