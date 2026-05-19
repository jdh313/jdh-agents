# Contract hosts

A spec-flow contract has a **host** — the container that holds the contract body during the change's lifecycle. Two hosts are supported:

- **`file`** — `.docs/YYYY-MM-DD-<slug>.md` in the working repo. Default.
- **`linear`** — a Linear issue (e.g. `CAR-49`), whose description holds the contract body.

The contract *shape* (the 5-section template in `contract-template.md`) is host-agnostic. The host changes only:

- Where the body is read from and written to.
- What happens to the container at close.
- Whether MCP availability gates the action.

The host is **not persisted**. Each skill re-detects it from the identifier (or goal text, at `start`). Same model as cadence — no per-contract flag.

## Host detection

### At `start`

The user is typing a goal, not an identifier. Detection uses the goal text:

| Input shape | Host | Notes |
|---|---|---|
| Bare ticket token (`CAR-49`) | linear | The ID alone treated as the contract |
| `the contract is CAR-49` / `use CAR-49 as the contract` | linear | Explicit framing |
| `implement CAR-49` / `pick up CAR-49` | linear | Action-on-ticket = ticket-is-contract |
| `see CAR-49` / `regarding CAR-49` / `the work in CAR-49` | ask once | Ticket present but framed as reference — ambiguous |
| `draft as .docs/` / `as a file` | file | Explicit file framing |
| No ticket token | file | Default |

The ticket-token pattern: `^[A-Z]{2,5}-\d+$` matched against whitespace-separated tokens in the goal text.

The ambiguous case escapes with a one-line ask: *"Use CAR-49 itself as the contract, or draft a `.docs/` file that references CAR-49?"* — do not silently pick.

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
| **`start` — locate** | Scan `.docs/*.md` for active contracts | n/a — Linear contracts are not enumerable cheaply; user names the ticket |
| **`start` — draft body** | Compose 5-section contract | Compose 5-section contract |
| **`start` — write container** | `Write` to `.docs/YYYY-MM-DD-<slug>.md` | `mcp__linear-server__save_issue` against the ticket ID |
| **`start` — existing body** | n/a — file is new | Read via `get_issue`; if existing description is substantive (>300 chars and not a stub template), ask *overwrite* or *prepend* before writing |
| **`implement` — read** | `Read` the file | `mcp__linear-server__get_issue`, parse description |
| **`amend` — write** | `Edit` the file | `mcp__linear-server__save_issue` |
| **`close` — done-when check** | Walk bullets from file body | Walk bullets from ticket description |
| **`close` — container action** | `mv` to `.docs/archive/`, flip frontmatter | None. Suggest the human flip ticket state at PR push; do not call `save_issue` to mutate state |
| **`close` — confirm wording** | "Contract archived at `.docs/archive/...`" | "Archive: N/A — Linear-tracked. Suggestion: flip ticket state when you push the PR." |

## Linear MCP availability

Linear-host actions require the `mcp__linear-server__*` tools to be loaded. If a Linear-host action is attempted without them:

- Surface the fact: *"Linear MCP server isn't connected — I can't read or write CAR-49."*
- Offer the user a choice: *"Fall back to a `.docs/` file contract, or pause while you wire up the MCP yourself?"*
- Never run `claude mcp add` or suggest a paste-and-go command. Connecting MCPs is a user decision.

Same wording across all four skills.

## What's *not* in spec-flow's job

spec-flow owns the contract lifecycle. It does **not** own:

- Linear title conventions
- Required fields at ticket creation (team, priority, labels)
- Linear status flow (which state means what; when to transition)
- PR-to-ticket linking expectations
- The decision of *when* to open a Linear ticket vs. a `.docs/` file

Those concerns belong to the user's broader Linear workflow, owned by the sibling `linear` plugin (`~/cc-marketplace/plugins/linear/skills/linear-workflow/SKILL.md`). spec-flow assumes the user has a Linear ticket already (or knows how to create one — by deferring to the `linear` plugin's conventions); spec-flow only writes the contract body and reads it back.

## Future shape: Linear-new (Shape B)

Not implemented. Documented here so the design shape is on record.

A future addition: `start` could *create* a new Linear ticket as part of the kickoff, not just attach to an existing one. The flow would be:

1. Detect Shape B from phrasing: *"open a Linear ticket and …"*, *"new linear ticket for …"*, or an explicit hint
2. Same context-gathering and drafting as today
3. Before writing, prompt for the Linear-specific fields the broader workflow requires: **title** (derive from goal, confirm), **team** (default to user's last-used or most-frequent), **status** (default to the team's leftmost / "Backlog"-equivalent — fetched via `list_issue_statuses`, not hardcoded)
4. `save_issue` with no ID to create; write the formatted contract as the body
5. Return the new ticket ID to the user

Why deferred: requires team/status discovery logic and decisions about Linear-side defaults that the broader Linear workflow needs to settle first. Ship existing-ticket support, learn from it, then revisit.

## Future shape: GitHub Issues (Shape C)

Not implemented. Same adapter pattern as Linear would apply: detection by issue-URL or `owner/repo#NN` shape, read/write via `gh` or GitHub MCP, close-state-flip handled the same way (suggestion-only, no automated mutation). Out of scope for the current update.
