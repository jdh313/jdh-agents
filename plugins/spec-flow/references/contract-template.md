# Contract Template (v2.1)

Used by `spec-flow:draft` to scaffold a new contract, and by `implement` / `amend` / `close` / `pm:breakdown` as the shared shape they read and write. The body below is the literal scaffold `draft` produces.

The contract shape is **host-agnostic** — the same sections work whether the contract lives in `.docs/YYYY-MM-DD-<slug>.md` or in a Linear ticket description. Only frontmatter is file-only (Linear has its own metadata). See `hosts.md` (same directory) for host selection and per-host behavior.

Governing decisions: ndr `39j5qb` (row supersedes pointer), `k7vepz` (nested parent), `233ar3` (cold-legible close), `kq7za5` (`[deferred]` drain), `957bqa` (audience primary). Rationale: `.docs/model-review-2026-07-10-contract-v2.md`.

## The model

The contract is a **worksheet** the change is written *into*, not a write-once agreement.

- **Audience is the primary organizing axis** (`957bqa`). Front-matter (the cold-legible shared model) sits above working-matter (the ledger `implement` writes into). **Reading order = audience.**
- **Drain is a property of working-matter only** (`957bqa`) — *not* a co-equal axis. At close the Decision log promotes to durable sinks (ndr atoms) and Approach/wiring evaporates. **Front-matter has no structural drain** — its durable content is the decision-whys already flowing through the Decision log; the rest rests in the archived contract.
- **Audience applies recursively and reaches working-matter at close** (`233ar3`). A cold *reviewer*'s **default** surface at the review gate is front-matter; a cold *closer* reads front-matter **and working-matter** at the close gate — the closer may not be the implementer. Working-matter is therefore held to a **fresh-closer legibility standard** (the atom-shaped row already meets it). Neither surface is written for a mid-flight-churn reader.
- **Working-matter is pullable at the review gate on demand.** Front-matter is what the review gate puts *up for review*; the reviewer default-reads it. But the whole contract is one document, so a reviewer who wants to object to the integration plan **may pull *Approach / wiring* into review** — the audience order sets the default reach, not a hard ceiling. This keeps the pre-implementation architectural objection available without promoting Approach back into front-matter.

The shape is **one shape, nested** (`k7vepz`) — a contract, or a tree of contracts. See *Variable fill*.

## Scaffold

```markdown
---
status: active
topic: <slug>
started: YYYY-MM-DD
---

# <Goal in plain language, one line>

<!-- ── front-matter: cold-legible, read at the gates ── -->

## What we're doing

- <one or two bullets: what's changing>

## Why

- <the trigger / motivation; the reason future-you and a cold reader care>

## Out of scope

- <fence only — a non-goal never seriously considered. "Was it a live fork?" NO → here.>
- <a considered-and-rejected option → Decision log [resolved] rejected-alt; a "not now, maybe later" → Decision log [deferred].>

## Done when

- <observable outcome — what the user/system can now do that it couldn't before>
- <visible state change — file exists, command works, endpoint returns>
- <verification gate — "tests pass", or "manual smoke: X" if non-obvious>
- <may be RELATIVE in a breakdown slice: "call sites moved; end-to-end green promised at <sibling>">

<!-- ── working-matter: internal ledger, cold-legible at close ── -->

## Approach / wiring

- <ephemeral integration mechanics, larger strokes — how it slots in>
- <the *call* behind the wiring lives in the Decision log; this holds only mechanics>
- <no task list, no enumeration. Evaporates at close.>

## Decision log

<!--
Each row is a fork. Three states, three close fates:
  [open]      unresolved  → close FLAGS it (shipped with a hole)
  [resolved]  decided here → close offers it to /capture-decision (canonical rubric)
  [deferred]  handled elsewhere → close MUST materialize it as a tracked artifact
Rows carry an atom's LIVE-ONLY fields (fork/call/why/alt/revisit) — the ones lost if
not written now; close fills the derivable remainder (Scope, Commitments, id).
A resolved decision that REVERSES gets a NEW row pointing back via ^id.
-->

- **[open]** <fork, as a question> — leaning: <tentative default>
- **[resolved]** ^r1 <fork> → **<call>**, because <why>. _alt:_ <rejected + why-not>. _revisit if:_ <trigger>
- **[resolved]** <fork> → **<new call>**, because <why>. _supersedes:_ ^r1. _alt:_ <the old call + why-abandoned>.
- **[deferred]** <fork> → tracked in <handle / trigger>, because <why-not-now>.

<!-- ^r1 is minted on the FIRST row only because the third row points back at it. The
     third (reversing) row carries no anchor of its own — nothing points back at it yet. -->

```

## Conventions

### Mutation ops

Three operations, organized by **"does this renegotiate the live agreement?"**:

| Op | Touches | When | Renegotiates? | Sign-off |
|----|---------|------|---------------|----------|
| **append** | Decision log | in flight | no — logs a fact | none |
| **amend** | front-matter | in flight | **yes** — changes the target | **required** |
| **reconcile** | front-matter | at close | no — corrects record to shipped reality | rides close's sign-off |

- **append** is `implement`'s routine write — logging a `[open]` / `[resolved]` / `[deferred]` row as forks resolve. No sign-off.
- **amend** changes what the contract promises (`spec-flow:amend`) — always sign-off.
- **reconcile** is legal ONLY on a `drifted` Done-when bullet (shipped, worded wrong), never a `not_met` one (didn't ship → halt-and-ask). It **spawns a Decision-log row** capturing *why* the criterion drifted, so the insight harvests instead of evaporating.
- **Sign-off follows the op; the concurrency guard follows the host.** On the Linear host every write is a whole-description overwrite, so *every* write — append included — carries the concurrent-edit guard (re-fetch + compare; pragmatic — it only bites when a concurrent edit is detected). On the file host, append is append-only and needs no guard; only amends do.

### Decision-log rows

- Row = the atom's **live-only fields** (`fork → call · because · alt · revisit-if`). Close fills the derivable remainder (Scope, Commitments, minted id). *Not* "copy-not-transform" — copy-plus-fill.
- **Row-id syntax:** an anchor `^r<N>` (`^r1`, `^r2`, …) placed right after the state token. Ids are **minted on demand** — a row gets one only when a later row points back at it. A successor references it inline: `_supersedes:_ ^r1`.
- **Reversal:** a reversed decision gets a NEW `[resolved]` row carrying `_supersedes:_ ^<row-id>` pointing at the original; the original row is **retained, not edited** (its reasoning is the record of why the first call was made).
- **Exclusions** route by the test *"was this a live fork?"*: never-considered → Out-of-scope fence; considered-and-rejected → `[resolved]` rejected-alt (may promote at close); not-now-maybe-later → `[deferred]` (mandatory drain).

### Drain at close

- **Working-matter only.** Decision log `[resolved]` rows are the **candidate set** handed to `/capture-decision`, which applies the **canonical ndr worthiness rubric** — the worksheet does NOT pre-filter with its own gate. Approach/wiring evaporates; durable/user-facing wiring reaches README via close's existing README-update proposal, not a section drain.
- **`[deferred]` rows carry a mandatory drain.** Each must materialize as a tracked artifact (a `spec-flow:capture` ticket by default, or a link to an existing one) before close can archive — an ephemeral contract cannot honestly carry "later." See the close skill's deferral gate.
- **Front-matter** has no structural drain (rests in the archived contract / Linear body).

### Audience & state

- **Cold-reader reach:** reviewer → front-matter (review gate); closer → front-matter + working-matter (close gate). Working-matter meets a fresh-closer legibility standard.
- **State signaling (file host):** `status: active` in flight; on close the file moves to `.docs/archive/` and the field flips to `archived`. Placement is canonical; the field is informational.

## Variable fill — one shape, nested

There is **one shape**. A contract, or a **tree of contracts**. Verbose-vs-thin is fill depth, not a second shape.

- **Single change** — front-matter lean, Decision log local. The everyday contract.
- **Breakdown** — the **parent is a normal contract at change altitude** (full front-matter + working-matter), **not** read-only. Each substantial slice is its own contract with a pointer to the parent.
  - **Decision altitude (duplication rule):** whole-change and cross-slice decisions live in the **parent's** Decision log; slice-local decisions live in the **slice's**. A decision belongs to exactly one log. Placement is author judgment during implement; `close` flags literal cross-log duplication at parent-close, not misplacement.
  - **Parent-close harvests too:** `close` runs per-slice, and the parent closes **last** — harvesting its integration/whole-change decisions. The parent has its own amend discipline (a breakdown's whole-change Done-when *can* change mid-flight).
  - **Wide refactor (shared integration):** migrate slices carry a **relative** Done-when ("call sites moved; end-to-end green promised at `<final slice>`"); close honors the deferral (`met-with-deferral`, not `not_met`). The final integrate-and-verify slice owns the cross-batch Done-when + integration Decision log.
- **Host follows fill.** Single change → a Linear issue or `.docs/` file. Breakdown → the parent may **stay a Linear issue with child issues** (a Document is an optional static-home preference, not required); or a `.docs/` parent file with child issues. *Boundary:* an all-`.docs` breakdown (file parent + file children) has no skill — `pm:breakdown` always publishes Linear children.
- **Transition (single → breakdown):** when a lean contract outgrows single scope, run `/pm:breakdown` on it — the contract *becomes* the parent (keeping its front-matter and change-altitude Decision log); breakdown spawns the slices. No worksheet is shed; no host teardown.

## Out-of-scope sections

Things the contract deliberately does *not* include:

- **Task list / enumerated steps** — implementation, not the contract.
- **System spec / "current state of the app"** — durable layer (README, ndr atoms, code).
- **Cross-change roadmap** — spec-flow is single-change-scoped (a breakdown tree is still one change, sliced).
- **Enumerated acceptance criteria / test plan** — `Done when` captures gates as observable outcomes; specific cases stay in implementation.
- **Glossary / vocabulary** — drains to `CONTEXT.md` at draft (via `craft:grill-with-docs` when the craft plugin is installed).
