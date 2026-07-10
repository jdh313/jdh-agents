---
name: implement
description: This skill should be used when the user runs `/spec-flow implement [name]` or otherwise signals a transition from a drafted contract to actual coding work. Trigger phrases include "spec-flow implement", "let's start coding on the X contract", "pick up the X contract", "resume the X change", "continue the okta-auth work". Accepts either a file slug or a Linear ticket ID (e.g. `TEAM-123`). Covers both first-run implementation (negotiate handoff cadence, begin work) and resumption (restore context from contract, summarize where work last left off, continue). Same flow either way — read state, summarize, confirm cadence, execute. May invoke `spec-flow:amend` mid-implementation when reality diverges from the contract.
argument-hint: "[contract slug or TEAM-N; omit to infer]"
allowed-tools:
  - mcp__linear-server__get_issue
  - mcp__linear-server__list_issues
  - mcp__linear-server__list_issue_statuses
  - Read
  - Glob
  - Grep
  - Bash(ls *)
---

# spec-flow:implement

Start or resume implementation against an active contract. Works for both file-hosted (`.docs/`) and Linear-hosted contracts; the only difference is where the body is read from. See `../../references/hosts.md`.

## When to invoke

- User runs `/spec-flow implement [name]`.
- User signals readiness to code on an existing contract: "let's start", "pick up the okta-auth contract", etc.
- Resumption of work on a contract from a prior session.

## Do NOT invoke for

- Drafting a new contract — that is `spec-flow:draft`.
- Closing a finished change — that is `spec-flow:close`.
- Code work that has no associated contract (trivial changes are out of scope by design).

## Workflow

### 1. Identify the target contract and detect host

If a name was given as argument:

- Argument matches `^[A-Z]{2,5}-\d+$` (e.g. `TEAM-123`) → **linear** host. Use the ticket ID.
- Otherwise → **file** host. Treat the argument as a slug or filename.

If no name was given, enumerate active contracts across both hosts:

- **File host** — scan `.docs/` (excluding `archive/` and `status: captured` stubs).
- **Linear host** (when the MCP is connected) — `mcp__linear-server__list_issues` filtered to "Contract Review" and "In Progress" states (team per the linear plugin's conventions; **no assignee filter** — list all team contracts), keeping only tickets whose description carries the six-section shape (`## What we're doing` heading is the cheap test). Display the assignee per contract so ownership is visible when listing.

Then:

- **Single active contract** — Use it.
- **Multiple active** — Match the user's recent prompt against contract topics/titles. If unambiguous, use the match. If ambiguous, list active contracts and ask which.
- **None active** — Tell the user there is nothing to implement and suggest `/spec-flow draft`. If the Linear MCP isn't connected, note that Linear contracts weren't checked.

If host = linear, check that `mcp__linear-server__*` tools are loaded. If not:

> "Linear MCP server isn't connected — I can't read TEAM-123. Fall back to a `.docs/` file contract, or pause while you wire up the MCP yourself?"

Do not run `claude mcp add` or suggest a paste-and-go connect command.

### 2. Read the contract

- **File host** — `Read` the contract file.
- **Linear host** — Fetch via `mcp__linear-server__get_issue` and parse the description for the 6 sections.

Follow any linked ndr atoms (`[[ndr-...]]` references) and read them.

### 2.5. Claiming check (Linear host only)

After reading the ticket, check its `assignee` field:

- **Assignee is the current user (`me`) or unassigned** — proceed normally.
- **Assignee is someone else** — warn before continuing:

  > "This contract is assigned to **[name]** — implement on their behalf (leave assignee unchanged), or reassign it to yourself first?"

  Wait for the user's explicit choice. Do not proceed silently, and do not block permanently — this is a guardrail, not a gate. If the user says "implement on their behalf", continue with the existing assignee. If "reassign to me", call `mcp__linear-server__save_issue(id=..., assignee="me")` before moving to In Progress.

(File-host contracts have no assignee concept — skip this step.)

### 3. Assess state

**Detect the VCS first.** If `.jj/` exists at the repo root, this is a jj-colocated repo — use `jj log` / `jj diff` / `jj st`, not `git`. Under jj, `git status` reflects the jj working-copy commit and misreads whether work has "already begun." Otherwise use `git`.

Check whether implementation has already begun:

- Recent commits (`jj log` / `git log`) referencing the contract's topic or slug.
- Uncommitted changes in the working tree (`jj st` / `git status`).
- Files modified since the contract was created.

Summarize back to the user in 2–3 lines:

- **First run:** "Contract is `<slug>`. Goal: X. Approach: Y. No implementation work yet."
- **Resumption:** "Contract is `<slug>`. Last session: A, B per git. Open forks remaining: ..." (the `[open]` rows in the Decision log).

### 4. Negotiate cadence

Ask the user briefly:

> "Implement all at once, or check in after a piece?"

If a sensible breakpoint exists, propose it:

> "I'd suggest checking in after the auth middleware is wired up, before touching the route layer. Sound good?"

Wait for the user's choice. Do not persist this — cadence is per-session.

### 5. Execute

**Linear host — move to In Progress.** Before writing any code, transition the ticket to the started state:

- Fetch the team's workflow states via `mcp__linear-server__list_issue_statuses` (the team comes from the issue read in step 2).
- Find the state named "In Progress" (case-insensitive match); if absent, fall back to the team's first `started`-type state.
- Set it via `mcp__linear-server__save_issue` (state field).
- If no started-type state exists, note it once and continue. Never block coding on a status change.

(File host has no status — skip this.)

Work according to the chosen cadence:

- **All at once** — Implement the full change; surface the diff at the end.
- **Check in after a piece** — Implement up to the agreed breakpoint; surface progress; await sanity-check; continue.

**Append Decision-log rows as forks resolve.** The Decision log is working-matter you *write into* during implementation — this is the routine `append` op (no sign-off; it logs a fact, not a renegotiation). As each fork lands, append a row:

- **[resolved]** — decided here: `<fork> → **<call>**, because <why>. _alt:_ <rejected + why-not>. _revisit if:_ <trigger>`. Reversing an earlier `[resolved]` row? Append a NEW row carrying `_supersedes:_ ^r<N>`, and add the `^r<N>` anchor to the original row so the pointer resolves (this anchor is the *only* touch the original takes). Never rewrite the original's call or reasoning — it stands as the record of why the first call was made.
- **[deferred]** — punted to elsewhere: `<fork> → tracked in <handle>, because <why-not-now>`. The handle is backfilled at close if not known yet (close gates archive on it).
- **[open]** — still unresolved: leave it, or add one if a new fork surfaces mid-flight. Close flags any `[open]` row that ships.

Write rows to a **fresh-closer legibility standard** — the closer may not be you. When a *Done when* bullet turns out to have shipped differently than worded (drift, not a miss), append a `[resolved]` row capturing *why* it drifted; `close`'s `reconcile` op will pick it up. A bullet that genuinely didn't ship is not drift — surface it, don't paper it into a row. On the Linear host, every write is a whole-description overwrite, so appends carry the concurrent-edit guard (re-fetch + compare); on the file host, append is append-only, no guard.

**Commit atomically as you go.** Cadence governs when you *check in with the user*, not when you commit — commit each logical, self-contained slice as it lands in the repo's house style via `Skill(commit:commit)`, which detects git vs. jj and writes the message for you. This holds even for "all at once": land the change as a series of atomic commits rather than one end-of-run blob. At a "check in after a piece" breakpoint, commit the slice once the user has sanity-checked the diff. Never commit over a failing verify (step 7). If the `commit` plugin isn't installed, commit directly following the repo's conventions (CLAUDE.md / recent history).

### 6. Amend when reality diverges

Distinguish the two working-matter writes from a front-matter amendment. Logging a fork's outcome to the **Decision log** is the routine `append` (step 5) — no sign-off. Invoke `Skill(spec-flow:amend)` only when the **front-matter** is becoming inaccurate — the *target itself* changes: wrong approach, a new constraint narrowing scope, an *Out of scope* item that now needs to be in scope, or a `[open]` Decision-log row whose resolution changes what *Done when* promises. Amending front-matter renegotiates the agreement, so it always takes sign-off. Do NOT silently work outside the contract; do NOT silently edit front-matter.

### 7. Verify against *Done when*

Before declaring the work done, verify each *Done when* bullet by **observing behavior**, not by reading the diff. Drift's signature is plausible code that looks right at a glance but doesn't do what the contract promised — reading the diff won't catch it; running the change will.

Dispatch the **`contract-verifier`** agent (via the Agent tool) so the running and log-reading happen in isolated context and the judgment is independent of your view as the implementer. Pass it:

- The *Done when* bullets verbatim.
- The change scope — `<base>..HEAD` (jj or git, per the VCS detected in step 3) or `"working tree"` if uncommitted.
- The detected `vcs`, and a `repo_hint` if you already know the test command; otherwise let the agent discover it.

It returns a per-bullet verdict (`met` / `not_met` / `drifted` / `unverifiable`, each with evidence). Surface the result to the user. If any bullet is **not met** (or unverifiable), do not paper over it — keep working, or (if the contract's notion of done genuinely changed) invoke `Skill(spec-flow:amend)`.

If the `contract-verifier` agent is unavailable for any reason, fall back to running the checks inline (tests + driving each behavior, `/verify` if available).

### 8. End

When the user signals completion (or the agreed scope has shipped) and the Done-when bullets verify, prompt:

> "Looks done from my end and the Done-when checks pass. Run `/spec-flow close` when ready to migrate findings to the durable layer."

Do NOT auto-close. Closing is an explicit user action.

## Notes

- "First run" and "resumption" share the same flow; behavior differs based on observed state, not on a persisted flag.
- Host is not persisted. Each invocation re-detects from the identifier shape.
- Confidence is not persisted. Each invocation re-negotiates cadence.
- Implementation must respect the contract's *Out of scope* — if a tempting addition surfaces, propose an amendment via `spec-flow:amend`. Do not just add it.
