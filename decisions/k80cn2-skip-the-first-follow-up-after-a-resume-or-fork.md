---
id: "k80cn2"
title: Skip the first follow-up after a resume or fork
status: current
decision_date: 2026-10-15
author: Jacob Hoehler
conviction: strong
project: jdh-agents
labels:
  - scope
binds:
  - docs/langfuse-human-followup-contract.md
supersedes: []
superseded_by: []
derived_from:
  - Claude Code session a7c25421-a3b6-4e7d-a9db-f93dd575e9e0 (2026-10-15)
informed_by: []
---

# k80cn2 — Skip the first follow-up after a resume or fork

## Decision

The Claude Code exporter records a start time for each session, at SessionStart or else at the first Stop that finds no record. It does not export a follow-up whose preceding human request is older than that start. The first follow-up after a resume, a fork, or enabling the feature mid-session is therefore skipped and never backfilled.

## Commitments

- The SessionStart hook stays registered, prints nothing, and builds no Langfuse client.
- The plugin docs state that the first follow-up after a resume, a fork, or mid-session enablement is not exported.

## Revisit if

- Claude Code exposes a resumed or forked session's parent session ID to hooks.
- Resumes become the main way sessions continue, so the per-resume loss becomes material.

## Context

- A resumed or forked Claude Code session's transcript can carry rows from the earlier session under the new session ID.
- The exporter's cursor and dedupe ledger are stored per session ID.
- Turning the feature on mid-session leaves earlier turns without any exporter state.
- On 2026-11-10 the follow-up exporter moved to transponder, and this repository stopped carrying it when the `langfuse` plugin was retired (JUN-668).

## Why

The exporter has no record of what it saw before the session started. Pairing the first new message with copied history would either re-export an exchange the earlier session had already exported, which the evaluator would then score twice, or export an exchange the exporter never saw happen live. Comparing the preceding request's timestamp with a recorded start time rules out both cases. The cost is one real follow-up per resume, fork, or enablement, which is acceptable.

## Alternatives

- **Pair across the boundary** — rejected: an exchange already exported under the original session ID would be exported again under the new one, and the per-session ledger cannot see the earlier export.
- **Carry exporter state across resumes by tracing session lineage** — deferred: needs the parent session ID, which hooks do not receive.
