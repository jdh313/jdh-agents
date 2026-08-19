---
id: "jsw3nz"
title: State an unenforceable stance boundary in the skill body, not only in
  frontmatter
status: current
decision_date: 2026-08-03
author: Jacob Hoehler
conviction: strong
project: jdh-agents
labels:
  - architecture
  - write-side
binds:
  - plugins/*/skills/**
supersedes: []
superseded_by: []
derived_from:
  - linear:TEAM-344
  - git:a1b8726
informed_by:
  - kpefq4
  - grjvxz
  - v0a3bm
---

# jsw3nz — State an unenforceable stance boundary in the skill body, not only in frontmatter

## Decision

When a skill's frontmatter tool policy is the only thing enforcing a behavioral boundary, state that boundary in the skill body as well. Frontmatter carries the enforcement on the runtime that has one; the body carries the instruction everywhere.

## Scope

- Binds: skills whose declared behavior depends on a tool restriction — a stance, a refusal, a "never reach for X" guarantee.
- Does not bind: tool policy used for permission-prompt convenience or capability hints, where losing enforcement costs friction rather than behavior.
- Does not bind: frontmatter itself. The allowlist stays, spelled exactly; this adds prose, it does not remove declarations.

## Commitments

- A skill whose description promises a behavioral boundary states that boundary in its body, not only in `allowed-tools` / `disallowed-tools`.
- Compiling such a skill for a target that enforces no tool filter is not treated as a declared loss when the body carries the boundary — the instruction survives; only its enforcement does not.
- New multi-runtime skills are written this way from the outset rather than remediated at enrollment.

## Revisit if

- A non-Claude target gains real tool-filter enforcement, which would make the frontmatter load-bearing again and the prose redundant rather than primary.
- A boundary proves unreliable in prose in practice — a model crossing it despite an explicit instruction would mean prose is not a sufficient carrier and the construct needs declaring instead.

## Context

- `compass` splits one job across three skills that differ mainly in how much the agent commits: `reflect` mirrors, `mull` contributes takes, `converge` researches and recommends.
- `reflect` and `mull` enforced "never web-search, never delegate" solely through `disallowed-tools`. Their bodies mentioned research only as a trigger for handing off to `converge`, never as a prohibition on themselves.
- No non-Claude target enforces a tool filter, so both fields are stripped when the package compiles for one.
- Under compiler pin `a0701ec` the field was additionally invisible: absent from the canonical schema, discarded at parse, reported nowhere, and carrying no construct token that would let it be declared. AgentForge tracked that as L-001 and fixed it; under `0ebebbb` the key is enumerated, round-trips into the Claude projection, and is reported as stripped.
- The compiler-visibility fix (`a0701ec` to `0ebebbb`) changed only whether the strip is reported, not whether the target enforces the field.

## Why

A tool policy is an enforcement mechanism, not a statement of intent. It tells a runtime what to block; it never tells the model what the skill is for. When a boundary lives only there, the skill's whole reason for existing is encoded in a field that any target without the same enforcement discards — and the model reads the stripped body and finds nothing forbidding the thing the skill was built to forbid.

Prose is the weaker enforcement and the stronger carrier. It cannot stop a tool call the way an allowlist can, but it reaches every runtime, survives every projection, and is legible to the model actually deciding what to do next. For a stance the boundary *is* the product, so a weaker guarantee that ships everywhere beats a stronger one that silently does not.

The compiler-visibility fix is the argument's sharpest evidence. Improving the diagnostic made the loss announced rather than silent, which is strictly better, and changed nothing about what the target enforces. Anything resting on the diagnostic would have moved; the prose did not.

## Alternatives

- **Declare it as a loss and accept the degradation** — rejected: no construct token existed for a skill's tool filter, and a declaration documents a gap rather than closing it. The skill would still ship a body that fails to forbid what it exists to forbid.
- **A per-target body override carrying the boundary for targets that need it** — rejected: duplicates a complete body to add two sentences, and the sentences are true on every runtime including the one that enforces the field.
- **Wait for the compiler to make the strip visible** — rejected: visibility is not enforcement. The fix landed mid-change and improved the diagnostic without changing what the target does.
