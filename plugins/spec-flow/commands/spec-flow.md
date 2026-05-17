---
description: Drive a code change through spec-flow's contract lifecycle (start, implement, close)
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

- **`start <goal>`** — Open a contract for a new code change. Invokes `Skill(spec-flow:start)` with the goal text.
- **`implement [name]`** — Start (or resume) implementation against an existing contract. Invokes `Skill(spec-flow:implement)`. If `name` is omitted, infer from active contracts in `.docs/`.
- **`close [name]`** — Close an active contract and migrate findings to the durable layer. Invokes `Skill(spec-flow:close)`. If `name` is omitted, infer from active contracts.

## Dispatch rules

- **No subcommand given:** List active contracts in `.docs/` (any `.md` not in `.docs/archive/`) and ask the user which action and which contract.
- **Unknown subcommand:** List the three valid subcommands and ask the user to retry.

Arguments: $ARGUMENTS
