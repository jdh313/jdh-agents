---
id: "nyq74g"
title: Split learning-workspace schema ownership by concern
status: current
decision_date: 2026-09-16
author: Jacob Hoehler
conviction: strong
project: jdh-agents
labels:
  - architecture
  - write-side
  - read-side
binds:
  - plugins/teach/**
supersedes: []
superseded_by: []
derived_from:
  - "Fibery Project Tracking/Task #103"
informed_by:
  - kpefq4
  - grjvxz
---

# nyq74g — Split learning-workspace schema ownership by concern

## Decision

Vault-local guidance owns vault-wide placement, frontmatter, tag, hierarchy, and link conventions. Teach owns the learning-specific artifact set, artifact formats, teaching workflow, and safety gates. Each layer references the other at the boundary instead of duplicating the other's detailed schema.

## Scope

- Binds Teach's canonical package and the learning-workspace section of the user's vault guidance.
- Does not change unrelated vault schemas or the semantics of non-learning notes.

## Commitments

- Teach defers to current vault conventions for context placement, optional hierarchy links, and cross-cutting tags.
- Vault guidance describes how learning workspaces participate in the vault but leaves their detailed artifact contract to Teach.
- A Teach runtime reads the complete canonical vault guidance before deriving a workspace path or vault-specific fields; excerpts and search matches are insufficient.

## Revisit if

- Vault conventions become a machine-readable schema that Teach can consume directly.
- Teach no longer writes into a user-governed vault.
- A runtime demonstrates a genuine semantic difference that cannot be expressed portably.

## Context

- Teach and the vault guide both described the learning-workspace schema.
- The vault guidance is specific to the user's personal knowledge system.
- Teach is a portable, versioned plugin package projected into multiple runtimes.
- The copies drifted on lesson format, context tags, and the fallback for a missing parent MOC.
- A fresh Claude runtime read only selected guidance lines before writing, which left the drift undiscovered until after artifact creation.
- Current decisions require portable shared skill wording and fresh-runtime acceptance for support claims.

## Why

The split follows the natural authority boundary. The vault is the only durable authority for how all of its notes are placed, tagged, and linked, while the versioned Teach package is the only durable authority for what a teaching workspace contains and how teaching proceeds. Keeping one owner per concern removes the manual synchronization loop that produced the observed conflicts without making a personal vault contract part of a portable plugin package.

## Alternatives

- **Teach owns the entire schema** — rejected: a portable package cannot authoritatively define a user's changing vault-wide conventions.
- **Vault guidance owns the entire schema** — rejected: learning-specific artifact and workflow changes would bypass package versioning, generation, and acceptance tests.
- **Keep both copies and synchronize them manually** — rejected: this is the arrangement that drifted and failed runtime acceptance.
