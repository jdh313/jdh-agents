# linear

Personal Linear workflow conventions for AI-assisted development. Loads when an agent needs to create, transition, read, or update a Linear ticket — supplies the defaults so the agent doesn't have to guess.

`TEAM` and `TEAM-N` in examples are placeholders for the team and issue key
resolved from the connected workspace. They are never literal configuration;
the same plugin is used across workspaces with different team names.

## Premise

`spec-flow` uses Linear as a contract host. `ndr` uses Linear (via reference strings) to point at tickets. Both treat Linear as a tool they consume, not own. The conventions — what team, what labels, what status means what — belong somewhere stable that other plugins can defer to.

That's this plugin.

## Scope

- **Owns:** Ticket creation defaults (team, labels, priority, milestone), status flow semantics, title shape, description templates, MCP call patterns.
- **Does NOT own:** The decision of *whether* to open a ticket (project CLAUDE.md). The spec-flow contract lifecycle (spec-flow plugin). PR-to-ticket linking (deferred until PRs are introduced).
- **Currently scoped to:** A single Linear team.

## Skills

- **`linear`** — Single skill carrying the conventions and MCP call patterns. Renders as `/linear` (skill name matches the plugin name). Triggers on ticket creation, transitions, reads, and queries.

## Codex optional agent bundle

Installing Linear exposes its Markdown procedure and the explicit
`$linear:setup-codex-agents` skill; it does not register `linear:linear-ops`.
Choose either user or project scope through that skill. The active installed
`SKILL.md` supplies the plugin root for the helper, so setup never guesses a
cache path or version. Use an absolute path to a verified released AgentForge
binary and, for isolated testing, explicitly set and validate the intended
`CODEX_HOME` for every lifecycle command. Project setup also requires a
validated literal project-root argument.

In a fresh Codex session, run the selected-scope `check` immediately before
each exact `agent_type: "linear:linear-ops"` dispatch. A failed or stale check
blocks that registered-role path. Each native dispatch also receives the exact
installed `mcp-gotchas.md` path or its verbatim content, plus the PM
`layer-policy.md` path or content when its intent declares a parent. The
operator writes only that decided intent; a missing connector or required
context blocks before a write, and a read-only request stays on the Linear
read path.

The explicit Markdown-procedure fallback either embeds the installed
`agents/linear-ops.md` body in a generic bounded child with `agent_type`
omitted, or follows that installed body inline literally. Neither route claims
registration. Plugin removal does not remove registered roles; remove each
selected scope separately through the receipt-based setup action.

Codex receives no translation of Linear's Claude `haiku` alias, tool allowlist,
or permission settings. The registered role inherits Codex model and effort;
record values from runtime metadata when observable, otherwise record them as
unknown. The body boundary survives as a procedure, while the package records
the missing mechanical tool filter as a Codex loss.

## Composes with

- **[spec-flow](../spec-flow/README.md)** — When a contract is hosted in Linear, spec-flow writes the contract body to the ticket description. This plugin owns the ticket's other fields.
- **[pm](../pm/README.md)** — The pm skills (`groom`, `retro`, `breakdown`) propose ticket actions; `linear` applies any approved transitions and owns the field conventions pm's `issue-shape.md` defers to.
- **ndr** (ships from its own separate marketplace) — `Decision` is one of this plugin's type labels. Tickets that capture decision points get the label; the captured decision itself lives as an ndr atom.
