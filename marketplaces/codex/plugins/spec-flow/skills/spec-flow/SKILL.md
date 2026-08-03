---
name: spec-flow
description: >-
  Drive a code change through spec-flow's contract lifecycle (capture, draft,
  implement, close)
---

# /spec-flow

Dispatcher for spec-flow's contract lifecycle. Parses the first argument as a subcommand and invokes the corresponding skill.

## Subcommands

- **`capture <thought>`** — Zero-ceremony intake of a future change idea (stage zero — not a contract). Invokes `Skill(spec-flow:capture)` with the thought text.
- **`draft <goal>`** — Open a contract for a new code change. Invokes `Skill(spec-flow:draft)` with the goal text.
- **`implement [name]`** — Start (or resume) implementation against an existing contract. Invokes `Skill(spec-flow:implement)`. If `name` is omitted, infer from active contracts (`.docs/` plus Linear contract states when the MCP is connected).
- **`close [name]`** — Close an active contract and migrate findings to the durable layer. Invokes `Skill(spec-flow:close)`. If `name` is omitted, infer from active contracts.
- **`route <id>`** — Detect what phase a contract is in and hand off to the matching skill — for when you have a ticket but don't know (or care) where it sits in the lifecycle. Invokes `Skill(spec-flow:route)` with the identifier.

## Dispatch rules

- **Bare ticket token as the first argument** (matches `^[A-Z]{2,5}-\d+$`, e.g. `/spec-flow TEAM-123`): shorthand for `route` — invoke `Skill(spec-flow:route)` with the token. The user is saying "figure out where this ticket is and continue."
- **No subcommand given (and no bare ticket):** List active contracts — `.docs/` files (any `.md` not in `.docs/archive/` and not matching `*-companion.md`) plus, when the Linear MCP is connected, tickets carrying the `contracted` label (case-insensitive, any workflow state) — and ask the user which action and which contract.
- **Unknown subcommand:** List the five valid subcommands and ask the user to retry.

Arguments: $ARGUMENTS
