# Contract hosts

A spec-flow contract has a **host** — the container that holds the contract body during the change's lifecycle. Two hosts are supported:

- **`file`** — `.docs/YYYY-MM-DD-<slug>.md` in the working repo. Default.
- **`linear`** — a Linear issue (e.g. `TEAM-123`), whose description holds the contract body. At `draft`, the ticket may already exist or be created fresh ("linear-new" — see detection below); after creation the two are indistinguishable.

The lifecycle has a pre-contract stage: `spec-flow:capture` files a minimal artifact (Backlog ticket on the linear host, `status: captured` stub on the file host) that `draft` later upgrades. Captured artifacts are **not** contracts — they're excluded from active-contract enumeration and have no lifecycle state transitions.

The contract *shape* (the 6-section template in `contract-template.md`) is host-agnostic. The host changes only:

- Where the body is read from and written to.
- What happens to the container at close.
- Whether MCP availability gates the action.

The host is **not persisted**. Each skill re-detects it from the identifier (or goal text, at `draft`). Same model as cadence — no per-contract flag.

## Host detection

### At `draft`

The user is typing a goal, not an identifier. Detection uses the goal text:

| Input shape | Host | Notes |
|---|---|---|
| Bare ticket token (`TEAM-123`) | linear | The ID alone treated as the contract |
| `the contract is TEAM-123` / `use TEAM-123 as the contract` | linear | Explicit framing |
| `implement TEAM-123` / `pick up TEAM-123` | linear | Action-on-ticket = ticket-is-contract |
| `open a new ticket and ...` / `new linear ticket for ...` | linear-new | Fresh ticket created at the write step; title derived (rename in Linear if off), all fields per the linear plugin's conventions |
| `see TEAM-123` / `regarding TEAM-123` / `the work in TEAM-123` | ask once | Ticket present but framed as reference — ambiguous |
| `draft as .docs/` / `as a file` | file | Explicit file framing |
| No ticket token | file | Default. A goal matching a `status: captured` stub upgrades that stub in place |

The ticket-token pattern: `^[A-Z]{2,5}-\d+$` matched against whitespace-separated tokens in the goal text.

The ambiguous case escapes with a one-line ask: *"Use TEAM-123 itself as the contract, or draft a `.docs/` file that references TEAM-123?"* — do not silently pick.

### At `implement`, `amend`, `close`

The user passes an identifier (or it's inferred from active contracts). Detection is simpler:

| Identifier | Host |
|---|---|
| Matches `^[A-Z]{2,5}-\d+$` | linear |
| Anything else (kebab slug, filename) | file |

No phrasing analysis at this stage — the identifier shape is the signal.

## Per-host behavior

| Step | File host | Linear host |
|---|---|---|
| **`capture` — write** | Stub at `.docs/YYYY-MM-DD-<slug>.md` with `status: captured` | New Backlog ticket, lightweight Goal/Context body, fields per linear plugin conventions |
| **`draft` — locate** | Scan `.docs/*.md` for active contracts (skip `status: captured`) | `list_issues` on "Contract Review" + "In Progress" states; six-section description = contract |
| **`draft` — draft body** | Compose 6-section contract | Compose 6-section contract |
| **`draft` — approval** | Present in chat; user approves before the file is written | None in chat — write immediately; the Contract Review state is the review surface |
| **`draft` — write container** | `Write` to `.docs/YYYY-MM-DD-<slug>.md`; captured stubs upgraded in place | `mcp__linear-server__save_issue` against the ticket ID (linear-new: `save_issue` with no ID creates the ticket) |
| **`draft` — existing body** | Captured stub's Goal/Context is drafting input | Overwrite by default — no prompt. Prepend only if the user explicitly asked to preserve the existing text |
| **`draft` — status** | n/a — no status | After writing the body, set state to "Contract Review" via `list_issue_statuses` + `save_issue`; skip with a note if no such state |
| **`implement` — read** | `Read` the file | `mcp__linear-server__get_issue`, parse description |
| **`implement` — status** | n/a — no status | Before coding, set state to "In Progress" (fallback: first `started`-type state) via `save_issue` |
| **`amend` — write** | `Edit` the file | `mcp__linear-server__save_issue`, then post a before/after comment via `save_comment` (description overwrite erases history; comments are the changelog) |
| **`close` — done-when check** | Walk bullets from file body | Walk bullets from ticket description |
| **`close` — verification record** | n/a — verdict lives in conversation | Post the per-bullet contract-verifier verdict as a comment via `save_comment` before the state change |
| **`close` — container action** | `mv` to `.docs/archive/`, flip frontmatter | Advance state to a review state (In Review / Code Review / …) via `save_issue`; never set a completed state. Body untouched |
| **`close` — confirm wording** | "Contract archived at `.docs/archive/...`" | "Verification comment posted; moved to In Review; body intact. Set Done yourself at merge." |

## Linear MCP availability

Linear-host actions require the `mcp__linear-server__*` tools to be loaded. If a Linear-host action is attempted without them:

- Surface the fact: *"Linear MCP server isn't connected — I can't read or write TEAM-123."*
- Offer the user a choice: *"Fall back to a `.docs/` file contract, or pause while you wire up the MCP yourself?"*
- Never run `claude mcp add` or suggest a paste-and-go command. Connecting MCPs is a user decision.

Same wording across all four skills.

## What's *not* in spec-flow's job

spec-flow owns the contract lifecycle. It does **not** own:

- Linear title conventions
- Required fields at ticket creation (team, priority, labels)
- The team's status taxonomy in general — which states a team defines, what they mean
- PR-to-ticket linking expectations
- The decision of *when* to open a Linear ticket vs. a `.docs/` file

spec-flow *does* drive the contract-lifecycle state transitions: → **Contract Review** when the contract body is written at `draft`, → **In Progress** when `implement` begins coding, and → a **review state** when `close` finishes. All resolve the target by name via `list_issue_statuses` (never hardcoded) and skip gracefully if the team has no matching state. It never sets a **completed** state (Done/Closed) — merge happens outside the lifecycle, so that flip stays the human's.

Those concerns belong to the user's broader Linear workflow, owned by the sibling `linear` plugin in this marketplace. spec-flow assumes the user has a Linear ticket already (or knows how to create one — by deferring to the `linear` plugin's conventions); spec-flow only writes the contract body and reads it back.

## Linear-new (Shape B) — implemented

`draft` can *create* a new Linear ticket as part of the kickoff, not just attach to an existing one:

1. Detected from phrasing: *"open a Linear ticket and …"*, *"new linear ticket for …"*, *"create a ticket as the contract"*
2. Same context-gathering and drafting as the other hosts
3. Derive the **title** from the goal per the linear plugin's title conventions — no confirmation; the user reviews title and body together in Linear
4. `save_issue` with no ID to create, six-section contract as the body; **all other fields** (team, project, labels, priority) follow the `linear` skill's conventions — spec-flow never hardcodes them
5. Return the new ticket ID; proceed with the Contract Review transition as if the ticket had pre-existed

The original deferral reason — team/status discovery and Linear-side defaults — is resolved: the sibling `linear` plugin owns those conventions, and spec-flow defers to it.

## Future shape: GitHub Issues (Shape C)

Not implemented. Same adapter pattern as Linear would apply: detection by issue-URL or `owner/repo#NN` shape, read/write via `gh` or GitHub MCP, close-state-flip handled the same way as the Linear host (advance to a review state by name, never a completed state). Out of scope for the current update.
