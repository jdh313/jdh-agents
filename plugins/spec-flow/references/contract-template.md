# Contract Template (v2.3)

Used by `spec-flow:draft` to scaffold a new contract, and by `implement` / `amend` / `close` / `pm:breakdown` as the shared shape they read and write. The body below is the literal scaffold `draft` produces.

A contract is **two documents** (v2.3): a durable **contract doc** holding front-matter, and a throwaway **companion doc** holding working-matter. The contract doc is **host-agnostic** — the same sections work whether it lives in `.docs/YYYY-MM-DD-<slug>.md` or in a Linear ticket description; only frontmatter is file-only (Linear has its own metadata). The companion is always `.docs/YYYY-MM-DD-<slug>-companion.md`, on both hosts. See `hosts.md` (same directory) for host selection and per-host behavior.

Governing decisions: ndr `39j5qb` (row supersedes pointer), `k7vepz` (nested parent), `233ar3` (cold-legible close), `kq7za5` (`[deferred]` drain), `957bqa` (audience primary). Rationale: `.docs/model-review-2026-07-10-contract-v2.md`.

The `Not yet specified` section (v2.2) adapts the **fog of war** model from the `wayfinder` skill in [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, © 2026 Matt Pocock) — the dim view ahead, the phrase-it-now sharpness test, and graduation as the frontier advances. The idea only; no skill was ported, and this contract shape is otherwise unrelated to wayfinder's map.

## The model

The contract is a **worksheet** the change is written *into*, not a write-once agreement.

- **Audience is the primary organizing axis** (`957bqa`). Front-matter (the cold-legible shared model) and working-matter (the ledger `implement` writes into) are **two documents** — the durable *contract doc* and the throwaway *companion doc*. v2.2 and earlier expressed the same axis as two section groups in one document; v2.3 makes it a document boundary. The axis is unchanged; only its granularity is.
- **Drain is a property of working-matter only** (`957bqa`) — *not* a co-equal axis. At close the Decision log promotes to durable sinks (ndr atoms), Approach/wiring evaporates, and the companion doc is deleted. **Front-matter has no structural drain** — its durable content is the decision-whys already flowing through the Decision log; the rest rests in the archived contract doc.
- **Evaporation is now literal.** Under one document, "Approach/wiring evaporates" held only on the file host — the Linear body persisted forever with working-matter in it. A separate companion makes the throwaway tier actually throwaway on both hosts. (The companion is a committed `.docs/` file, so git history retains it; deletion removes it from the working set, not from the record.)
- **Audience applies recursively and reaches working-matter at close** (`233ar3`). A cold *reviewer*'s **default** surface at the review gate is the contract doc; a cold *closer* reads the contract doc **and** the companion at the close gate — the closer may not be the implementer. Working-matter is therefore held to a **fresh-closer legibility standard** (the atom-shaped row already meets it). Neither surface is written for a mid-flight-churn reader.
- **Working-matter is pullable at the review gate on demand** (`7br5yf`). The contract doc is what the review gate puts *up for review*; the reviewer default-reads it. A reviewer who wants to object to the integration plan **may pull the companion into review** — the audience order sets the default reach, not a hard ceiling. The original rationale for this ("it's all one document anyway") no longer holds, but the affordance survives on the pointer: the contract doc names its companion, so reaching it costs one hop, not a search.

The shape is **one shape, nested** (`k7vepz`) — a contract, or a tree of contracts. See *Variable fill*.

## Scaffold

### Contract doc — `.docs/YYYY-MM-DD-<slug>.md`, or the Linear description

Frontmatter is file-host only; on the Linear host the ticket's own metadata carries state, and the `companion:` pointer becomes a `Companion:` line at the foot of the description.

```markdown
---
status: active
topic: <slug>
started: YYYY-MM-DD
companion: .docs/YYYY-MM-DD-<slug>-companion.md
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

```

### Companion doc — `.docs/YYYY-MM-DD-<slug>-companion.md`, both hosts

```markdown
---
contract: <slug-or-TEAM-123>
started: YYYY-MM-DD
---

# Companion — <same goal line>

<!-- ── working-matter: internal ledger, cold-legible at close, deleted after drain ── -->

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

## Not yet specified

<!--
BREAKDOWN PARENTS ONLY — omit on a single contract.
The fog ahead: forks you can tell are coming but cannot yet state as a question.
The test is whether you can PHRASE it now, not whether you can ANSWER it now —
a sharp-but-unanswerable fork is a Decision-log [open] row or its own slice, not fog.
Patches GRADUATE: when a slice closes and sharpens one, it becomes slices and leaves here.
Coarser than a slice — one patch may graduate into several, or none.
Excludes: what's decided (Decision log), what's already a slice, what's past the
destination (Out of scope — that's a scope call, not a sharpness one).
-->

- <area of fog — the suspected question, as loosely as the view allows>

```

## Conventions

### Mutation ops

Three operations, organized by **"does this renegotiate the live agreement?"**:

| Op | Touches | Document | When | Renegotiates? | Sign-off |
|----|---------|----------|------|---------------|----------|
| **append** | Decision log | companion | in flight | no — logs a fact | none |
| **amend** | front-matter | contract doc | in flight | **yes** — changes the target | **required** |
| **reconcile** | front-matter | contract doc | at close | no — corrects record to shipped reality | rides close's sign-off |

- **append** is `implement`'s routine write — logging a `[open]` / `[resolved]` / `[deferred]` row as forks resolve. No sign-off.
- **amend** changes what the contract promises (`spec-flow:amend`) — always sign-off.
- **reconcile** is legal ONLY on a `drifted` Done-when bullet (shipped, worded wrong), never a `not_met` one (didn't ship → halt-and-ask). It **spawns a Decision-log row** capturing *why* the criterion drifted, so the insight harvests instead of evaporating.
- **Sign-off follows the op; the concurrency guard follows the document.** Appends land in the companion — a `.docs/` file on both hosts — so they are append-only and need **no** guard anywhere. Only writes to the contract doc carry one, and only on the Linear host, where a write is a whole-description overwrite (re-fetch + compare; pragmatic — it only bites when a concurrent edit is detected). This is the second thing the split buys: mid-flight churn no longer touches the user's sign-off surface at all.

### Decision-log rows

- Row = the atom's **live-only fields** (`fork → call · because · alt · revisit-if`). Close fills the derivable remainder (Scope, Commitments, minted id). *Not* "copy-not-transform" — copy-plus-fill.
- **Row-id syntax:** an anchor `^r<N>` (`^r1`, `^r2`, …) placed right after the state token. Ids are **minted on demand** — a row gets one only when a later row points back at it. A successor references it inline: `_supersedes:_ ^r1`.
- **Reversal:** a reversed decision gets a NEW `[resolved]` row carrying `_supersedes:_ ^<row-id>` pointing at the original; the original row is **retained, not edited** (its reasoning is the record of why the first call was made).
- **Exclusions** route by the test *"was this a live fork?"*: never-considered → Out-of-scope fence; considered-and-rejected → `[resolved]` rejected-alt (may promote at close); not-now-maybe-later → `[deferred]` (mandatory drain).
- **Not yet a fork at all** → `Not yet specified` (breakdown parents only). A Decision-log row *is* a fork — it carries `fork → call · because · alt · revisit`. Something you can't yet phrase as a question has no fork to write, so it can't be a row; it's fog. The router's question is sharpness, and it runs **before** the live-fork test: can you state it now? No → fog. Yes → the live-fork test decides which slot.

### Drain at close

- **The companion only.** Decision log `[resolved]` rows are the **candidate set** handed to `/capture-decision`, which applies the **canonical ndr worthiness rubric** — the worksheet does NOT pre-filter with its own gate. Approach/wiring evaporates; durable/user-facing wiring reaches README via close's existing README-update proposal, not a section drain. Once the drain completes, `close` **deletes the companion file** — that deletion is the drain's completion signal, so it must not run before the `[deferred]` gate and the harvest have both landed.
- **`[deferred]` rows carry a mandatory drain.** Each must materialize as a tracked artifact (a `spec-flow:capture` ticket by default, or a link to an existing one) before close can archive — an ephemeral contract cannot honestly carry "later." See the close skill's deferral gate.
- **Un-graduated `Not yet specified` patches drain too**, at parent-close, by the same logic: fog written down because you expected it to matter cannot quietly evaporate with the worksheet. Three dispositions, user's call per patch — **graduated** (already became slices; nothing to do), **out of scope** (the effort's destination moved past it; one line to the Out-of-scope fence, citing the patch), or **still real** (drains to `spec-flow:capture`). Capture is the natural landing: it is the zero-ceremony path built to accept a one-liner or rough paragraph, which is exactly a fog patch's shape. See the close skill's breakdown-parent gate.
- **Front-matter** has no structural drain (rests in the archived contract doc / Linear body).

### Audience & state

- **Cold-reader reach:** reviewer → contract doc (review gate); closer → contract doc + companion (close gate). The companion meets a fresh-closer legibility standard.
- **State signaling (file host):** `status: active` in flight; on close the contract doc moves to `.docs/archive/` and the field flips to `archived`. Placement is canonical; the field is informational. The companion carries no `status:` — its existence *is* its state, and it is deleted at close.

## Variable fill — one shape, nested

There is **one shape**. A contract, or a **tree of contracts**. Verbose-vs-thin is fill depth, not a second shape.

- **Single change** — front-matter lean, Decision log local, **no `Not yet specified`**. A single change with fog in it isn't a contract yet; that's a `spec-flow:capture` stub.
- **Breakdown** — the **parent is a normal contract at change altitude** (full front-matter + working-matter), **not** read-only. Each substantial slice is its own contract with a pointer to the parent.
  - **Fog lives on the parent only.** `Not yet specified` is the parent's dim view of the whole effort; slices inherit nothing. It is **working-matter**, so it lives in the parent's *companion*, and adding a patch is a free append — no amend sign-off, the same as logging a Decision row. `pm:breakdown` writes it while charting and owns graduation; `spec-flow:close` owns its drain at parent-close.
  - **Decision altitude (duplication rule):** whole-change and cross-slice decisions live in the **parent's** Decision log; slice-local decisions live in the **slice's**. A decision belongs to exactly one log. Placement is author judgment during implement; `close` flags literal cross-log duplication at parent-close, not misplacement.
  - **Parent-close harvests too:** `close` runs per-slice, and the parent closes **last** — harvesting its integration/whole-change decisions. The parent has its own amend discipline (a breakdown's whole-change Done-when *can* change mid-flight).
  - **Wide refactor (shared integration):** migrate slices carry a **relative** Done-when ("call sites moved; end-to-end green promised at `<final slice>`"); close honors the deferral (`met-with-deferral`, not `not_met`). The final integrate-and-verify slice owns the cross-batch Done-when + integration Decision log.
- **Every contract in the tree gets its own companion.** A breakdown parent and each slice are separate contracts, so each has its own contract doc and its own `-companion.md`. The decision-altitude rule below routes rows between the parent's companion and a slice's.
- **Host follows fill** (contract docs only — companions are always `.docs/`). Single change → a Linear issue or `.docs/` file. Breakdown → the parent may **stay a Linear issue with child issues** (a Document is an optional static-home preference, not required); or a `.docs/` parent file with child issues. *Boundary:* an all-`.docs` breakdown (file parent + file children) has no skill — `pm:breakdown` always publishes Linear children.
- **Transition (single → breakdown):** when a lean contract outgrows single scope, run `/pm:breakdown` on it — the contract *becomes* the parent (keeping its front-matter and change-altitude Decision log); breakdown spawns the slices. No worksheet is shed; no host teardown.

## Out-of-scope sections

Things the contract deliberately does *not* include:

- **Task list / enumerated steps** — implementation, not the contract.
- **System spec / "current state of the app"** — durable layer (README, ndr atoms, code).
- **Cross-change roadmap** — spec-flow is single-change-scoped (a breakdown tree is still one change, sliced).
- **Enumerated acceptance criteria / test plan** — `Done when` captures gates as observable outcomes; specific cases stay in implementation.
- **Glossary / vocabulary** — drains to `CONTEXT.md` at draft (via `craft:grill-with-docs` when the craft plugin is installed).
