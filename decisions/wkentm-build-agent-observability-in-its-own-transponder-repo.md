---
id: "wkentm"
title: Build agent observability in its own transponder repo
status: current
decision_date: 2026-11-09
author: Jacob Hoehler
conviction: strong
project: jdh-agents
labels:
  - repo-shape
  - scope
binds:
  - plugins/langfuse/**
supersedes: []
superseded_by: []
derived_from:
  - Claude Code session 036b78d0-a5d9-4f7a-acb7-60bcd2eb8550 (2026-11-09)
informed_by:
  - 3t0szg
---

# wkentm — Build agent observability in its own transponder repo

## Decision

The agent observability tool lives in its own repository, `transponder`. The `langfuse` plugin in this marketplace stops carrying tracing code and becomes a thin installer that invokes a pinned `transponder` release.

## Scope

- Binds: where the tracing code, its tests, and its releases live.
- Does not bind: the tool's internal shape, its language, or which sinks it ships.

## Commitments

- The plugin keeps the Claude and Codex hook enrollment, trust, and consent surface in this marketplace.
- Each `transponder` upgrade reaches users through a pin change and a plugin version bump, with the runtime acceptance `ndr:3t0szg` requires when the parser or transport changes.
- Decisions binding the plugin's paths are updated in the same change that removes the code from this repo.

## Revisit if

- AgentForge gains a Pi target and can host a package's own test suite and release cadence.
- The tool stays small enough that a separate release cycle costs more than it saves.

## Context

- The `langfuse` plugin's hook is a single Python script of 1,746 lines.
- The hook's tests live outside the plugin, in the marketplace's `scripts/tests` directory.
- Plugin output is produced by `agentforge compile`, which reads the whole marketplace and republishes the entire `marketplaces/` tree.
- This marketplace publishes Claude and Codex packages only. Pi receives tracing from a separately installed npm plugin.
- Seven decisions in this ledger cite the plugin's paths.
- Expansion to Pi and to backends beyond Langfuse was proposed on 2026-11-09.

## Why

The expanded tool needs a build, a test suite, and a release stream of its own, and a package here is a set of declared files versioned and compiled as part of the marketplace. Pi tips the call further: one of the three harnesses cannot be published from this marketplace at all, so an install path outside it has to exist regardless.

A thin installer keeps what the marketplace is good at, which is enrolling hooks on Claude and Codex. The price is a pin to bump on every release and a one-time update to the decisions citing the old paths, and that price was accepted.

## Alternatives

- **Package inside jdh-agents** — rejected: the tool would still share this repo's compile, gates, and plugin-version scheme while needing its own release cadence.
- **Keep one script** — rejected: adding harnesses and sinks grows a file that is already 1,746 lines.
