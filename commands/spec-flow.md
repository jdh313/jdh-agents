---
description: Drive a code change through spec-flow's contract lifecycle (capture, draft, implement, close)
argument-hint: <subcommand> [args]
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Skill
---

# /spec-flow

Dispatcher for spec-flow's contract lifecycle. Parses the first argument as a subcommand and invokes the corresponding skill.

## Subcommands

- **`capture <thought>`** — Zero-ceremony intake of a future change idea (stage zero — not a contract). Invokes `Skill(spec-flow:capture)` with the thought text.
- **`draft <goal>`** — Open a contract for a new code change. Invokes `Skill(spec-flow:draft)` with the goal text.
- **`implement [name]`** — Start (or resume) implementation against an existing contract. Invokes `Skill(spec-flow:implement)`. If `name` is omitted, infer from active contracts (`.docs/` plus Linear contract states when the MCP is connected).
- **`close [name]`** — Close an active contract and migrate findings to the durable layer. Invokes `Skill(spec-flow:close)`. If `name` is omitted, infer from active contracts.

## Dispatch rules

- **No subcommand given:** List active contracts — `.docs/` files (any `.md` not in `.docs/archive/`) plus, when the Linear MCP is connected, tickets in the contract lifecycle states (Contract Review / In Progress with a six-section description) — and ask the user which action and which contract.
- **Unknown subcommand:** List the four valid subcommands and ask the user to retry.

Arguments: $ARGUMENTS
