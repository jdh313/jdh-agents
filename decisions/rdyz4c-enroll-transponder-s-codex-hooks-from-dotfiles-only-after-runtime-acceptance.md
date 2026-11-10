---
id: "rdyz4c"
title: Enroll transponder's Codex hooks from dotfiles only after runtime acceptance
status: current
decision_date: 2026-11-10
author: Jacob Hoehler
conviction: strong
project: jdh-agents
labels:
  - scope
  - write-side
binds:
  - docs/agentforge-compatibility.md
supersedes:
  - 3t0szg
superseded_by: []
derived_from:
  - linear:JUN-668
informed_by:
  - v0a3bm
---

## Decision

transponder's Codex hooks are enrolled only after a runtime acceptance run. Enrollment happens in the operator's dotfiles, on the personal host. This marketplace no longer ships a Codex tracing integration.

## Scope

- Binds: when transponder's Claude Code and Codex hooks may be enrolled or their pin moved, and what an acceptance run must observe.
- Does not bind: how transponder is built beyond the commitments below, or whether other hook-backed packages in this marketplace are ready for Codex enrollment.

## Commitments

- Keep Claude transcript parsing and Codex rollout normalization behind one tested hook entry point in transponder.
- Preserve fail-open behavior when credentials, transcripts, network access, or supported payload fields are absent.
- Keep generated output, compilation checks, and observed runtime acceptance separate in compatibility claims.
- Before the transponder pin moves past a change to the parser, hook schemas, or Langfuse transport, run fresh Claude and Codex trace acceptance. Each run must produce a parsed turn and remotely queryable observations with the expected session, runtime, model, and release metadata. The Codex run must also produce a remotely queryable programmatic-spawn observation for `SessionStart`.

## Revisit if

- Codex changes its rollout or hook payload schema incompatibly.
- Langfuse removes or changes the OpenTelemetry or SDK contracts used by the lifecycle hooks.
- Fresh runtime evidence shows missing turns, tool observations, or runtime metadata.

## Context

- The `langfuse` package was retired from this marketplace on 2026-11-10 (`ndr:a1s7hf`), and transponder's hooks are now installed by the operator's dotfiles on the personal host.
- transponder's acceptance script (`scripts/acceptance.ts --harness codex`) runs Codex with hooks in a temporary `CODEX_HOME`.
- Codex requires users to review and trust hooks before they run.
- Fresh Codex CLI 0.155.1 and Claude Code 2.1.278 acceptance runs on 2026-09-21, against the retired plugin, each produced one parsed turn and the expected remote observations.

## Why

The rule that `ndr:3t0szg` set still holds: an observability hook that compiles and installs can still be silently inert, and only a runtime run shows that it is not. What moved is the thing being enrolled, which is now transponder rather than this marketplace's `langfuse` package, and where it is enrolled, which is the operator's dotfiles on the personal host rather than the Codex publication here.

## Alternatives

- **Keep `ndr:3t0szg` with a dated Context note** — rejected: a current atom whose Decision line is false misleads readers, and two reviewers read it that way.
