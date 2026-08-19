---
id: "sa0z0q"
title: Restate cross-plugin conditions inline in publicly exported plugins
status: current
decision_date: 2026-07-27
author: Jacob Hoehler
conviction: tentative
project: agent-marketplace
labels:
  - architecture
  - scope
binds:
  - export/public.json
  - plugins/spec-flow/skills/**
supersedes: []
superseded_by: []
derived_from: []
informed_by:
  - v4wn6d
  - 1cpkrm
---

# sa0z0q — Restate cross-plugin conditions inline in publicly exported plugins

## Decision

A plugin on the public export allowlist states any condition it borrows from a non-allowlisted plugin inline in its own skill files, rather than referencing the plugin that owns it. Each restatement carries a note naming the canonical copy.

## Scope

- Binds: skill content in plugins listed in the `export/public.json` allowlist that reference plugins which stay private.
- Does not bind: references between two allowlisted plugins, or between two private plugins — both resolve fine in the install that receives them.

## Commitments

- Every inline restatement names its canonical source and tells future editors not to collapse it into a reference.
- Adding a plugin to the allowlist requires auditing its skills for references to plugins that remain private.
- The copies can drift apart silently; nothing checks that they still match.

## Revisit if

- The export gains content rewriting, so cross-plugin references can be stripped or inlined at export time.
- Every plugin referenced by an allowlisted plugin is itself added to the allowlist.

## Context

- `export/public.json` allowlists `spec-flow` but not `craft`.
- `plugins/spec-flow/skills/draft/SKILL.md` hooks two `craft` skills and already carries the full text of both trigger conditions it borrows from them.
- The export copies allowlisted plugin directories verbatim and does not rewrite their contents.
- A public install of `spec-flow` has no `craft` skill files present to resolve against.
- Deduplicating repeated conditions into a single canonical reference is the reflex a reviewer would otherwise apply here.

## Why

The export is a file copy, so anything a public skill points at must either travel inside the export or be self-contained in the file doing the pointing. A cross-plugin reference survives the copy as text but resolves to nothing, which is strictly worse than duplication: the reader gets a pointer with no target and no statement of the condition it was standing in for. Duplication trades a real drift risk for an artifact that always reads completely.

The drift risk is tolerable because these restatements are short and the note makes the coupling explicit at the exact place someone would edit. The remaining option — exporting the referenced plugin so the reference resolves — would let authoring convenience decide what gets published, inverting the control the allowlist exists to provide.

## Alternatives

- **Reference the owning plugin's skill** — rejected: the export copies files verbatim, so a public install resolves the reference to nothing.
- **Add the referenced plugin to the allowlist** — rejected: makes publication a side effect of authoring convenience rather than an explicit call.
- **Strip cross-plugin hooks from public builds** — deferred: needs export-time content rewriting, which the export deliberately does not do today.
