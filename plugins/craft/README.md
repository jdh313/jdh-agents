# craft

Software craftsmanship discipline skills: interviewing before acting, building test-first, diagnosing hard bugs, deepening architecture, and reviewing what changed. Several skills — and three post-edit review agents — are adapted from [`mattpocock/skills`](https://github.com/mattpocock/skills) (MIT, © 2026 Matt Pocock); each carries a per-skill `UPSTREAM.md` sidecar recording what diverged and why. This README doesn't restate those divergences.

## Skills

18 skills, grouped by what they're for. A skill marked **explicit invocation only** must be typed by name (or run via `wait-what`'s hard `disable-model-invocation: true` frontmatter field) — Claude won't reach for it on its own even when the trigger phrasing matches.

### Understanding a codebase

- **`grok`** — *explicit invocation only.* Durable, supersession-aware understanding of a codebase (or one subsystem) built up over multiple sessions, grounded in real sources — code, `CONTEXT.md`, NDR heads, git history — rather than parametric guesses. Persists confirmed understanding as vault records that graduate into `CONTEXT.md` and NDR atoms.
- **`zoom-out`** — *explicit invocation only.* Broader context or a higher-level perspective on how code fits into the bigger picture.
- **`quiz-me`** — *explicit invocation only, always user-pulled.* Opt-in active-recall comprehension check on code or a concept just explained — predict-then-verify, one question at a time, pitched at the why/mental-model level rather than syntax recall.

### Interviewing and deciding

- **`grill`** — The interview primitive: walk a design tree one question at a time, facts looked up by subagent rather than asked, no acting until shared understanding is reached.
- **`grill-with-docs`** — That same loop applied to vocabulary: grills a plan against a repo's `CONTEXT.md` glossary and NDR atoms, updating `CONTEXT.md` inline as terms crystallise.
- **`design-by-stories`** — Design or redesign an artifact's shape (schema, template, data model, config format, API surface) by modeling its actors and user stories first, then deriving the shape from the stories. One fork at a time, human adjudicates every fork.
- **`interrogate-model`** — Holistic representability review of a domain model as a whole (authz scheme, permission table, state machine, tenancy model): enumerates legitimate scenarios, marks which are unrepresentable or only reachable via overreach, and flags silently waived departures from stated principles. Stops for adjudication before routing findings onward.

### Building

- **`tdd`** — The red-green-refactor loop, done so the tests are worth keeping.
- **`prototype`** — Build a throwaway prototype to sanity-check whether a state model, logic, or UI direction feels right before committing it to real code.
- **`diagnose`** — Disciplined diagnosis loop for hard bugs and performance regressions: reproduce → minimise → hypothesise → instrument → fix → regression-test.
- **`resolve-conflicts`** — Recover each side's original intent — from commits, PRs, tickets, NDR heads — before resolving an in-progress merge, rebase, or jj conflict. Detects git vs. jj and follows that VCS's own mechanics.
- **`wizard`** — Generate an interactive bash wizard for the steps only a human can perform: third-party dashboards, credentials, CI secrets, one-off cutovers.

### Improving

- **`improve-codebase-architecture`** — Find deepening opportunities in a codebase, informed by the domain language in `CONTEXT.md` and decisions surfaced via NDR atoms.
- **`derive-conventions`** — Derives a repo's unwritten conventions (naming, error-handling shape, docstring format, CLI voice) from its own code, presents each inferred rule with its evidence for accept/edit/reject, and writes the approved set to `CONVENTIONS.md` so the review agents below stop re-deriving them every run. Never writes an unreviewed rule.

### Domain and vocabulary

- **`domain-modeling`** — Build and sharpen a project's domain model: terminology, `CONTEXT.md` glossary entries, and any architectural decision that surfaces while modelling.

### Review

- **`infra-review`** — Reviews an AWS Terraform pull request whose plans are produced by Atlantis: reconstructs before/after topology from the posted plan and stays read-only until an explicit human-approved posting gate. Not for application-code review or non-Terraform IaC.
- **`lucid-architecture-diagram`** — Create, review, or edit AWS cloud architecture diagrams in Lucid via the Lucid MCP server. Documents two non-obvious silent-failure modes (AWS shape-library bootstrapping, assisted-layout container rejection) and the user-places-then-agent-connects cadence that works around them.

### Communication

- **`wait-what`** — *User-invoked only (`disable-model-invocation: true`).* Re-pitch a message that didn't land, in Simplified Technical English, using the repo's own vocabulary.

## Agents

Three read-only post-edit review agents, each deriving the host repo's conventions from its own code rather than importing preferences — none of them edit:

- **`house-style-reviewer`** — A diff against the repo's own unlinted conventions (naming, file placement, error-handling shape, test structure), skipping whatever the repo's own linters already enforce.
- **`comment-reviewer`** — Docstrings and comments against the code they describe, including comments left unchanged while the code beneath them moved. Uses VCS history to separate stale comments from deliberate ones.
- **`copy-reviewer`** — User-facing strings (CLI output, error messages, help text, prompts, docs headings) against the voice the product already uses. Grounds every finding in an existing string it can cite.

## Reference docs

`craft` also ships three reference documents, not workflows in their own right:

- **`CONTEXT.md`** — the plugin's own domain glossary, currently anchored by `interrogate-model`'s representability vocabulary (model, axis, scenario, subject, departure, waive).
- **`CODEBASE-DESIGN.md`** — shared architecture vocabulary (module, interface, implementation, depth, seam, adapter) used by `tdd`, `improve-codebase-architecture`, and `grok`.
- **`RUNTIME.md`** — maps orchestration terms (invoking another skill, spawning an explorer, asking for adjudication, tracking a multi-phase workflow) onto their Claude Code and Codex equivalents, since craft skill bodies are canonical across both runtimes.

## Composes with

- **ndr** (external) — `interrogate-model` routes unrepresentable-scenario findings to `/capture-decision`; `grill-with-docs` and `domain-modeling` read and update NDR-adjacent context; `improve-codebase-architecture` and `grok` ground in NDR heads.
- **[spec-flow](../spec-flow/README.md)** — `design-by-stories` settles an artifact's shape before handing off to `spec-flow:draft` to contract the build; `spec-flow:draft` itself gates on `grill-with-docs` when a repo's `CONTEXT.md` is missing or inconsistent with the goal's central nouns; `prototype` points a validated prototype's branch back at the tracking spec-flow contract.

## Credits

Adapted in part from [`mattpocock/skills`](https://github.com/mattpocock/skills) (MIT, © 2026 Matt Pocock): `diagnose`, `domain-modeling`, `grill`, `grill-with-docs`, `improve-codebase-architecture`, `prototype`, `resolve-conflicts`, `tdd`, `wait-what`, `wizard`, and `zoom-out`. Each carries an `upstream:` frontmatter block (repo, path, reviewed SHA, review date) and a per-skill `UPSTREAM.md` sidecar with the divergence record — see those files for what changed and why.
