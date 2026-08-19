---
id: "6x3v6p"
title: Restate a sole-enforcement tool boundary in body prose
status: current
decision_date: 2026-08-03
author: Jacob Hoehler
conviction: strong
project: agent-marketplace
labels:
  - process
  - write-side
binds:
  - plugins/**
supersedes: []
superseded_by: []
derived_from:
  - linear:TEAM-352
  - https://github.com/jdh313/cc-marketplace/pull/26
informed_by: []
---

# 6x3v6p — Restate a sole-enforcement tool boundary in body prose

## Decision

When a frontmatter tool filter is the only thing enforcing a behavioral boundary, that boundary must also be stated in the artifact's body prose. The frontmatter stays and keeps enforcing where it can; the prose is a second, runtime-portable statement of the same rule.

## Scope

- Binds: any skill or agent published to more than one runtime whose `allowed-tools`, `disallowed-tools`, or agent `tools:` filter carries a behavioral boundary.
- Does not bind: filters that are only permission-prompt convenience, where nothing behavioral rides on them.

## Commitments

- Every enrollment of an artifact for a second runtime checks whether each stripped filter carries a boundary, and whether that boundary already survives in prose.
- The prose statement is phrased as an instruction to the model, in the operating section, not as documentation about the artifact.
- The frontmatter filter is never removed in exchange for the prose. Adding the second statement does not license dropping the first.
- A boundary that cannot be stated in prose is a signal the artifact is relying on sandboxing, and needs a declared loss instead.

## Revisit if

- A second runtime gains real tool-filter enforcement, making the prose redundant rather than load-bearing.
- Prose boundaries are observed being ignored often enough that stating them stops buying anything.

## Context

- Frontmatter tool filters are Claude-only; Codex role procedures and skills carry no allowlist and strip them.
- Some filters are permission-prompt convenience, and some are the sole enforcement of a rule the artifact was designed around.
- `compass` had already handled one instance of this by moving a `disallowed-tools` boundary into body prose, but as a one-off with no rule behind it.
- Enrolling the rest of the catalog surfaced six more instances across two packages.
- Three of those are `coach` skills designed never to write, whose filters name Todoist and Linear mutation tools, so losing the filter permits creating or modifying tasks and issues in those systems.
- A stripped filter is reported as a warning, so the loss is visible, but visibility does not restore the boundary.

## Why

The alternative on the table was to document each gap honestly in the compatibility doc and ship it. That is defensible for a loss of scope, and indefensible for a loss of restraint — and three of these are the latter, carrying external side effects no reader of the skill would anticipate.

What tips it is where the boundary actually lives. If a rule is real, it is part of what the artifact *is*, not part of how one runtime happens to sandbox it. Encoding it only in a field one target understands makes correctness a property of the deployment rather than of the artifact, and every new target then re-opens a question that should already be closed.

The prose is weaker enforcement than a sandbox, and that is worth saying plainly: an instruction can be ignored where a filter cannot. But an instruction that is present degrades to convention, while a filter that is stripped degrades to nothing. Trading strong-here-and-absent-there for strong-here-and-conventional-there is strictly better, and costs one sentence.

Keeping the frontmatter alongside it means Claude loses nothing. This is additive everywhere.

## Alternatives

- **Document the gap in the compatibility doc and ship it** — rejected: honest about a loss of restraint without preventing it, and the three worst cases mutate external systems.
- **Drop the frontmatter filter once prose states the boundary** — rejected: would weaken Claude to match Codex rather than lifting Codex toward Claude.
- **Declare a loss for every stripped filter** — deferred: right where a boundary genuinely cannot survive as prose, wrong as a blanket policy, since it records a gap that a sentence would have closed.
