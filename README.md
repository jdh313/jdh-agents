# linear

Personal Linear workflow conventions for AI-assisted development. Loads when an agent needs to create, transition, read, or update a Linear ticket — supplies the defaults so the agent doesn't have to guess.

## Premise

`spec-flow` uses Linear as a contract host. `ndr` uses Linear (via reference strings) to point at tickets. Both treat Linear as a tool they consume, not own. The conventions — what team, what labels, what status means what — belong somewhere stable that other plugins can defer to.

That's this plugin.

## Scope

- **Owns:** Ticket creation defaults (team, labels, priority, milestone), status flow semantics, title shape, description templates, MCP call patterns.
- **Does NOT own:** The decision of *whether* to open a ticket (project CLAUDE.md). The spec-flow contract lifecycle (spec-flow plugin). PR-to-ticket linking (deferred until PRs are introduced).
- **Currently scoped to:** A single Linear team.

## Skills

- **`linear`** — Single skill carrying the conventions and MCP call patterns. Renders as `/linear` (skill name matches the plugin name). Triggers on ticket creation, transitions, reads, and queries.

## Composes with

- **[spec-flow](../spec-flow/README.md)** — When a contract is hosted in Linear, spec-flow writes the contract body to the ticket description. This plugin owns the ticket's other fields.
- **[pm](../pm/README.md)** — The pm skills (`groom`, `retro`, `breakdown`) propose ticket actions; `linear` applies any approved transitions and owns the field conventions pm's `issue-shape.md` defers to.
- **ndr** (ships from its own separate marketplace) — `Decision` is one of this plugin's type labels. Tickets that capture decision points get the label; the captured decision itself lives as an ndr atom.
