---
id: "grjvxz"
title: Name intent rather than tool identifiers in instruction prose
status: current
decision_date: 2026-07-31
author: Jacob Hoehler
conviction: tentative
project: jdh-agents
labels:
  - process
  - write-side
binds:
  - plugins/**/*.md
supersedes: []
superseded_by: []
derived_from:
  - linear:TEAM-354
informed_by:
  - kpefq4
---

# grjvxz — Name intent rather than tool identifiers in instruction prose

## Decision

Instruction prose in skills, agents, and commands names what to do, not which tool does it. Reference and diagnostic documents are excepted: they keep exact tool identifiers and carry a runtime-adapter paragraph explaining how another runtime should map them.

## Scope

- Binds: body prose in plugin markdown.
- Does not bind: frontmatter `tools:` and `allowed-tools:` allowlists, which are machine-readable and must name tools exactly.
- Does not bind: worked examples whose subject is a tool's argument shape.

## Commitments

- A document in the exception class carries its adapter paragraph unconditionally, shipped to every runtime including the one where it is redundant.
- Skills that probe a specific endpoint, and references documenting a specific API's argument semantics, stay in the exception class and are not rewritten toward intent.
- New instruction prose is written this way from the outset; the convention is not a one-time cleanup.

## Revisit if

- Routing by intent proves unreliable enough that naming a tool becomes necessary for correctness in ordinary instruction prose.
- A runtime arrives with no equivalent for a described operation, leaving intent phrasing nothing to resolve to.
- The exception class grows past a handful of documents, which would mean the boundary is drawn wrong.

## Context

- Plugin markdown compiles to runtimes other than Claude Code, where `mcp__*` identifiers name tools that do not exist.
- 65 body occurrences outside the `linear` plugin are ordinary instruction prose; roughly 13 inside it are load-bearing.
- Tool identifiers are chosen by the MCP server and can change without notice to the documents naming them.
- A model reading a skill already has the available tool list, with descriptions, in its context.
- Two documents already carry a hand-written adapter paragraph, and it ships to Claude Code today without incident.
- A connectivity check that does not name its tool can be satisfied from model memory or the web while the integration is down.

## Why

Naming a tool identifier in prose couples an instruction to a runtime detail the instruction does not depend on. The identifier adds nothing to routing that the tool list does not already supply, while subtracting portability. It also rots: a rename on the server side silently invalidates every document that spelled it out, and nothing in the document reveals the breakage.

The exception is narrow enough to state rather than leave to judgment. A connectivity check asserts that a specific transport is alive, so intent phrasing lets it pass against the wrong source. A gotcha reference records that a particular parameter value on a particular tool fails silently, and intent phrasing reproduces the exact mental model that causes the bug it documents. In both, the identifier is the content rather than an implementation detail of the content.

Handling that exception with an unconditional adapter paragraph, rather than per-runtime variants, keeps the convention free of tooling. The paragraph is two sentences, it is already present in both documents, and it already reaches the runtime where it is redundant with no observed harm.

## Alternatives

- **Per-target substitution of tool identifiers by the compiler** — rejected: requires a mapping table maintained per target, and per identifier, for a problem the prose dissolves at no cost.
- **Conditional emission of the adapter paragraph** — rejected: needs a templating mechanism in order to delete two sentences that are already harmless where they land.
- **Leave identifiers everywhere and accept the loss on other runtimes** — rejected: ships instructions that name tools which do not exist, which is worse than vaguer routing.
