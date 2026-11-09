---
id: "ek0hyq"
title: Build a cross-harness hub instead of filling gaps around Langfuse plugins
status: current
decision_date: 2026-11-09
author: Jacob Hoehler
conviction: tentative
project: jdh-agents
labels:
  - architecture
  - scope
binds:
  - plugins/langfuse/**
supersedes: []
superseded_by: []
derived_from:
  - Claude Code session 036b78d0-a5d9-4f7a-acb7-60bcd2eb8550 (2026-11-09)
informed_by:
  - 3t0szg
  - djr6w1
---

# ek0hyq — Build a cross-harness hub instead of filling gaps around Langfuse plugins

## Decision

`transponder` captures Claude Code, Codex, and Pi sessions itself, through one adapter per harness, into one neutral model, and exports through pluggable sinks. It replaces the existing hook and the upstream Pi plugin for tracing, rather than only adding the records those tools lack.

## Scope

- Binds: the capture path for turn traces and human follow-ups on the three harnesses.
- Does not bind: the Langfuse transport, the implementation language, or whether a Grafana sink or an OTel Collector ever exists.

## Commitments

- Each harness adapter produces the neutral model and does not depend on another harness's row shape.
- Adding a sink requires no change to any harness adapter.
- This project owns parser upkeep for three session formats that can change without notice.
- Human follow-ups stay at-most-once unless `ndr:djr6w1` is superseded.

## Revisit if

- A maintained tool offers one schema across all three harnesses with OTel export and works with self-hosted Langfuse.
- Every sink other than Langfuse goes unused.
- Harness-native telemetry carries full prompts, tool input and output, and span hierarchy on all three harnesses.

## Context

- Prior-art research on 2026-11-09, not independently verified, reported the facts below.
- Langfuse publishes separate MIT plugins for Claude Code, Codex, and Pi, each a separate code path that exports only to Langfuse.
- The Pi plugin is marked experimental, and whether the Codex plugin works against self-hosted Langfuse is unverified.
- No tool found offers one schema across all three harnesses with OTel export. The closest multi-harness parser, agentsview, has no trace export.
- No tool found pairs a genuine human reply with the exchange before it.
- Codex documents native logs and metrics but no spans. Claude Code's native traces are beta and redact content by default.
- Langfuse was the only confirmed consumer on 2026-11-09, and what a Grafana view should show was undecided.

## Why

The goal is a capture layer that is independent of any one backend, and that is the gap the research found nothing filling. Per-harness Langfuse plugins answer a narrower question: they get each harness to Langfuse, and leave no shared model or route to a second backend.

Filling only the gaps would be smaller, and it was the recommendation in review, on the grounds that no second consumer was confirmed. The owner chose the hub anyway as the intended design, accepting that it is built ahead of a confirmed second consumer. That acceptance is why conviction is tentative and why unused sinks are a revisit condition.

## Alternatives

- **Follow-up exporter only** — rejected: leaves traces split across two codebases and reaching only Langfuse.
- **Full switch to upstream Langfuse plugins** — rejected: no shared model, and self-hosted Codex support is unverified.
- **Harness-native OTel** — rejected: Codex documents no spans, and Claude Code's traces are beta and redacted by default.
- **Gateway capture at the LLM API** — rejected: a proxy cannot see turn boundaries or tell human messages from injected ones.
