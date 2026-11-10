---
id: "5de6ma"
title: Make Claude Code follow-up export a separate opt-in from tracing
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
informed_by:
  - 3t0szg
---

# 5de6ma — Make Claude Code follow-up export a separate opt-in from tracing

## Decision

Claude Code follow-up export runs only when the `CC_LANGFUSE_FOLLOWUP_ENABLED` plugin option is true. The option defaults to false and is independent of the settings that turn on turn tracing.

## Scope

- Binds: the follow-up pass of transponder's Claude Code exporter.
- Does not bind: turn-tracing export, which keeps its own switches.

## Commitments

- The option's documentation states what a follow-up observation contains and that it is sent on for model scoring.
- Turning tracing on never turns follow-up export on as a side effect.

## Revisit if

- Follow-up export stops forwarding content to an evaluation model, so it carries no more exposure than tracing.

## Context

- A follow-up observation holds the person's verbatim message, the preceding request, and the full assistant response.
- Every observation that matches the evaluation rule is forwarded to an external model provider for scoring.
- People who already run the plugin enabled tracing before follow-up export existed.
- On 2026-11-10 the follow-up exporter moved to transponder, and this repository stopped carrying it when the `langfuse` plugin was retired (JUN-668).

## Why

Follow-up export creates a data flow that tracing did not: verbatim human messages paired with the responses they answer, forwarded to an evaluation model. People who enabled tracing never agreed to that flow. If it were on by default, upgrading the plugin would start it for them without anyone choosing it. A separate default-off option makes it a deliberate choice.

## Alternatives

- **Enable follow-ups together with tracing** — rejected: it attaches a new data flow to an older consent, and an upgrade alone would start it.
