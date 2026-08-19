---
id: "v0a3bm"
title: Enroll only runtime-validated plugin targets
status: current
decision_date: 2026-07-20
author: Jacob Hoehler
conviction: strong
project: agent-marketplace
labels:
  - scope
  - deployment
binds:
  - plugins/**
  - docs/**
supersedes: []
superseded_by: []
derived_from:
  - shortcut:STORY-35
informed_by: []
---

# v0a3bm — Enroll only runtime-validated plugin targets

## Decision

AgentForge publications enroll a plugin only for runtimes where its native mapping and fresh-runtime acceptance have been verified. The current collection enrolls all fifteen packages for Claude and the five accepted pilots—commit, craft, librarian, linear, and spec-flow—for Codex.

## Scope

- Binds: canonical AgentForge marketplace and package target declarations.
- Does not bind: native manifests retained during migration or future target acceptance work.

## Commitments

- Each new runtime enrollment must pass its native validator and a fresh-runtime smoke test.
- Unsupported targets remain absent rather than producing empty or misleading packages.

## Revisit if

- Another plugin completes a Codex-native mapping and fresh-runtime acceptance.
- AgentForge gains a separately represented experimental or unverified enrollment state.

## Context

- Claude supports the complete marketplace catalog.
- Codex support is an explicitly curated pilot catalog.
- Schema-valid package definitions can still omit runtime semantics or unsupported constructs.

## Why

Target support is a behavioral claim, not a consequence of schema validation. Gating enrollment on native mapping and runtime acceptance keeps generated catalogs honest while still allowing the canonical collection to represent the complete source inventory.

## Alternatives

- **Compile every package for every target** — verdict: rejected: successful emission would misrepresent untested or semantically incomplete runtime support.
