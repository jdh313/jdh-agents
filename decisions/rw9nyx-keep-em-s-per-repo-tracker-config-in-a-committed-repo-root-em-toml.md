---
id: "rw9nyx"
title: Keep em's per-repo tracker config in a committed repo-root .em.toml
status: current
decision_date: 2026-09-24
author: Jacob Hoehler
conviction: tentative
project: jdh-agents
labels:
  - tooling
  - substrate
binds:
  - plugins/em/references/config.md
  - plugins/em/skills/**
supersedes: []
superseded_by: []
derived_from:
  - "session research: Claude Code plugin per-project config (2026-09-24),
    plugins-reference userConfig scope"
informed_by: []
---

# rw9nyx — Keep em's per-repo tracker config in a committed repo-root .em.toml

## Decision

Which tracker a repo uses, and its tracker-specific identifiers, live in an optional committed `.em.toml` at the repo root. The tracker is resolved from the reference form first, then `.em.toml`, then one question to the user.

## Scope

- Binds: repo-level facts `em` needs: tracker, Linear team, Fibery database, GitHub repo, and cached discovered state names.
- Does not bind: personal per-machine defaults, which belong in plugin `userConfig` if ever needed.

## Commitments

- Writing to `.em.toml` is a repo change and happens only on the user's go-ahead.
- A missing file is normal; a file that fails to parse is reported, never skipped.
- The tracker is never inferred from which MCP servers happen to be connected.

## Revisit if

- Claude Code plugin `userConfig` gains project-scoped values.

## Context

- Claude Code's plugin `userConfig` holds one value per plugin per machine, and project-scoped `.claude/settings.json` entries are ignored for it.
- `enabledPlugins` supports project scope but carries only on/off, no values.
- This repo already had two workarounds: a committed `.ndr.toml` and `attention-workflow`'s uncommitted per-repo-hash `config.json` under `~/.claude/state/`.
- The user moves between Linear, Fibery, and GitHub Issues across repos.

## Why

Which tracker a repo uses is the same for everyone who works in it, so it belongs where teammates and reviewers can see it: in the repo. The native mechanism cannot vary by repo at all, and the per-machine state pattern hides a shared fact on one machine. Reference-first resolution keeps the file optional, since most references already name their tracker.

## Alternatives

- **Plugin `userConfig`** — rejected: machine-scoped, cannot say "this repo uses Fibery".
- **Per-machine state keyed by repo hash** — rejected: a shared repo fact becomes invisible and has to be re-entered on every machine.
- **Infer from connected MCP servers** — rejected: a session can have several trackers connected while the repo uses one.
