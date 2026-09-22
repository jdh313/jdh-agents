---
id: "3t0szg"
title: Enroll langfuse in Codex after runtime acceptance
status: current
decision_date: 2026-09-21
author: Jacob Hoehler
conviction: strong
project: jdh-agents
labels:
  - scope
  - write-side
binds:
  - plugins/langfuse/**
supersedes:
  - 7gf4vb
superseded_by: []
derived_from:
  - fibery:Project_Tracking/Task/110
informed_by:
  - v0a3bm
---

# 3t0szg — Enroll langfuse in Codex after runtime acceptance

## Decision

`langfuse` declares a Codex target and ships one shared, runtime-aware lifecycle integration for Claude Code and Codex. Codex enrollment requires explicit hook trust and separate consent for telemetry export.

## Scope

- Binds: Codex enrollment, rollout parsing, lifecycle-hook transport, runtime-specific state, and the compatibility claims attached to this package.
- Does not bind: whether other hook-backed packages are ready for Codex enrollment.

## Commitments

- Keep Claude transcript parsing and Codex rollout normalization behind one tested hook entry point.
- Preserve fail-open behavior when credentials, transcripts, network access, or supported payload fields are absent.
- Keep generated output, compilation checks, and observed runtime acceptance separate in compatibility claims.
- Re-run fresh Claude and Codex trace acceptance when the parser, hook schemas, or Langfuse transport changes materially.

## Revisit if

- Codex changes its rollout or hook payload schema incompatibly.
- Langfuse removes or changes the OpenTelemetry or SDK contracts used by the lifecycle hooks.
- Fresh runtime evidence shows missing turns, tool observations, or runtime metadata.

## Context

- The previous reader resolved zero turns from real Codex rollout rows because it expected Claude transcript envelopes.
- Claude transcripts and Codex rollouts use different message envelopes, state homes, and hook-output schemas.
- Codex provides `SessionStart` and `Stop` lifecycle events but requires users to review and trust plugin-bundled hooks.
- Langfuse v4 accepts lifecycle spans through its OpenTelemetry endpoint rather than the legacy ingestion endpoint.
- Non-interactive ancestor command lines can contain prompt text and therefore cannot be exported as tripwire metadata.
- Fresh Codex CLI 0.155.1 and Claude Code 2.1.278 acceptance runs each produced one parsed turn and remotely queryable observations with the expected session, runtime, model, and release metadata.
- The Codex acceptance run also produced a remotely queryable programmatic-spawn observation for `SessionStart`.

## Why

The exclusion existed to prevent a cleanly compiled but silently inert observability package. Fresh evidence now crosses the boundary that compilation cannot: both runtimes produced parsed turns and the expected remote observations, including Codex's separate lifecycle marker.

Keeping one implementation matters because the package's behavioral contract is shared even though the transcript envelopes and hook schemas differ. Retaining explicit trust and consent as commitments keeps enrollment from implying that data export is automatic or universally appropriate.

## Alternatives

- **Keep Codex excluded after the parser is accepted** — rejected: it would preserve a stale scope restriction after its stated revisit condition was satisfied.
- **Fork independent Claude and Codex hooks** — rejected: duplicated parsing and emission logic would make compatibility drift harder to detect and maintain.
