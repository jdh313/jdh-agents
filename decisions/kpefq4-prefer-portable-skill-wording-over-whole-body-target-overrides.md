---
id: "kpefq4"
title: Prefer portable skill wording over whole-body target overrides
status: current
decision_date: 2026-07-21
author: Jacob Hoehler
conviction: strong
project: agent-marketplace
labels:
  - architecture
  - write-side
binds:
  - plugins/*/skills/**
supersedes: []
superseded_by: []
derived_from:
  - shortcut:STORY-36
informed_by:
  - 98f5vm
  - v0a3bm
---

# kpefq4 — Prefer portable skill wording over whole-body target overrides

## Decision

When Claude and Codex invocation semantics agree, write shared skill instructions in target-neutral language. Add a full target body override only when runtime behavior genuinely diverges.

## Scope

- Binds canonical skill bodies compiled for more than one runtime.
- Does not bind runtime-specific executable instructions whose behavior cannot be expressed portably.

## Commitments

- Remediate avoidable target-specific prose in canonical skill sources.
- Require runtime evidence of semantic divergence before duplicating a complete skill body for one target.

## Revisit if

- Shared wording causes either target to lose supplied-input or no-input behavior.
- AgentForge gains a granular body transformation that avoids complete target-body duplication.

## Context

- Four shared skill bodies used Claude-only argument placeholders in explanatory prose.
- Claude appends invocation arguments when `$ARGUMENTS` is absent; Codex supplies the user's invocation context without Claude substitution.
- A target body override replaces the complete skill body rather than patching an individual passage.

## Why

One canonical instruction body keeps shared behavior legible and prevents target copies from drifting. When the runtimes already receive equivalent invocation context, target-specific placeholders are an avoidable source-format leak rather than a meaningful behavioral distinction.

The exception remains explicit because runtime semantics, not textual uniformity, are the boundary. A complete override is justified when shared wording cannot preserve behavior, but its duplication cost should follow evidence rather than anticipation.

## Alternatives

- **Full Codex body overrides for the four skills** — rejected: they duplicate complete bodies without a semantic divergence.
- **Retain warning-only compatibility dispositions** — rejected: declared-compatible output would continue exposing avoidable Claude syntax.
