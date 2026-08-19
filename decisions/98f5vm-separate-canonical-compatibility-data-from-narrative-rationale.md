---
id: "98f5vm"
title: Separate canonical compatibility data from narrative rationale
status: current
decision_date: 2026-07-20
author: Jacob Hoehler
conviction: tentative
project: agent-marketplace
labels:
  - architecture
  - write-side
binds:
  - plugins/**
  - docs/**
supersedes: []
superseded_by: []
derived_from:
  - shortcut:STORY-35
informed_by: []
---

# 98f5vm — Separate canonical compatibility data from narrative rationale

## Decision

Canonical AgentForge YAML carries machine-enforceable target support, payload declarations, and native exceptions. Narrative warning dispositions, unsupported-construct explanations, and parity caveats live in repository documentation.

## Scope

- Binds: AgentForge collection definitions and compatibility documentation.
- Does not bind: user-facing runtime metadata that is intentionally emitted into native manifests.

## Commitments

- Canonical definitions contain only data that AgentForge validates or projects intentionally.
- Every emitted diagnostic or unsupported behavior receives an explicit disposition in documentation.

## Revisit if

- AgentForge adds validated compatibility metadata that is not emitted into native manifests.
- Runtime manifests gain a standard non-user-facing compatibility reporting surface.

## Context

- Target-native overlays are projected into generated runtime manifests.
- Migration rationale is useful to maintainers but is not runtime metadata.
- AgentForge currently has no non-emitted compatibility-rationale field.

## Why

Keeping executable declarations in canonical YAML preserves machine validation without leaking internal migration prose into generated manifests. A dedicated compatibility document can record nuance, warnings, and semantic limits at the level maintainers need without weakening the schema boundary.

## Alternatives

- **Store rationale in target-native freeform fields** — verdict: rejected: the prose would leak into generated runtime manifests and blur runtime metadata with migration evidence.
