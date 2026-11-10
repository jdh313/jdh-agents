---
id: "0d0t26"
title: Refuse Langfuse Cloud hosts for follow-up export
status: current
decision_date: 2026-10-15
author: Jacob Hoehler
conviction: strong
project: jdh-agents
labels:
  - scope
  - deployment
binds:
  - docs/langfuse-human-followup-contract.md
supersedes: []
superseded_by: []
derived_from:
  - Claude Code session a7c25421-a3b6-4e7d-a9db-f93dd575e9e0 (2026-10-15)
informed_by: []
---

# 0d0t26 — Refuse Langfuse Cloud hosts for follow-up export

## Decision

When the configured Langfuse base URL's host is `langfuse.com` or one of its subdomains, the Claude Code follow-up pass does nothing. The repository never names a specific self-hosted host.

## Scope

- Binds: the follow-up pass of transponder's Claude Code exporter.
- Does not bind: turn-tracing export, which sends to any configured base URL.

## Commitments

- The host check is a denylist of Langfuse Cloud domains, so a new hosted domain must be added to it by hand.

## Revisit if

- Langfuse Cloud starts serving from a domain outside `langfuse.com`.
- Follow-up evaluation is wanted on Langfuse Cloud, with consent stated explicitly for that destination.

## Context

- The plugin is published from a public repository, and other installers may point it at Langfuse Cloud.
- A follow-up observation holds verbatim human messages and full assistant responses.
- The only Langfuse deployment this exporter was built and verified against is self-hosted.
- On 2026-11-10 the follow-up exporter moved to transponder, and this repository stopped carrying it when the `langfuse` plugin was retired (JUN-668).

## Why

Verbatim follow-ups should land only on infrastructure the installer runs. A denylist does this by rejecting one known third-party domain. An allowlist would instead have to name private infrastructure in a public repository and would block every other self-hoster.

## Alternatives

- **Pin the self-hosted hostname** — rejected: it puts private infrastructure in a public repository and blocks every other self-hoster.
- **Allow Langfuse Cloud** — deferred: no current need; it would need its own explicit consent for that destination.
