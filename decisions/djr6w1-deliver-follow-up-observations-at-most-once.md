---
id: "djr6w1"
title: Deliver follow-up observations at most once
status: current
decision_date: 2026-10-15
author: Jacob Hoehler
conviction: strong
project: jdh-agents
labels:
  - architecture
binds:
  - docs/langfuse-human-followup-contract.md
supersedes: []
superseded_by: []
derived_from:
  - Claude Code session a7c25421-a3b6-4e7d-a9db-f93dd575e9e0 (2026-10-15)
  - docs/langfuse-human-followup-contract.md
informed_by: []
---

# djr6w1 — Deliver follow-up observations at most once

## Decision

Before emitting anything, the exporter saves its per-session cursor and its ledger of recent entry IDs, covering every follow-up planned in that pass. It never retries a failed or unconfirmed send. An observation that does not reach Langfuse is lost.

## Commitments

- The state write precedes the emit; reordering them breaks the guarantee.
- Follow-up export has no retry loop and no backlog queue.

## Revisit if

- Langfuse ingestion becomes idempotent on an observation ID the caller supplies, so a resend overwrites rather than duplicates.
- Lost sends become frequent enough to bias the sample, which shows up as transcript follow-ups with no matching observation.

## Context

- The Langfuse SDK gives each span a fresh random span ID, so re-emitting the same follow-up creates a second observation rather than overwriting the first.
- The Stop hook flushes the SDK on a background thread capped at 5 seconds and swallows flush errors, so it cannot tell a lost send from a delivered one.
- The evaluation rule scores every matching observation at model cost, and each observation counts in the score rates.
- On 2026-11-10 the follow-up exporter moved to transponder, and this repository stopped carrying it when the `langfuse` plugin was retired (JUN-668).

## Why

Here a duplicate does more harm than a gap. A duplicate pays for a second evaluation and double-counts in the intervention rates, while a lost observation only shrinks the sample. The hook cannot confirm delivery, so a retry might resend something that already landed. The only way to guarantee no duplicates is to advance the state before sending and never resend.

## Alternatives

- **At-least-once with retries** — rejected: a send that landed but went unconfirmed would be resent as a second observation.
- **Deterministic observation IDs plus retries** — deferred: retries would be safe only if Langfuse deduplicates on that ID at ingestion, and that is unverified.
