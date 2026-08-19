---
id: "7gf4vb"
title: Exclude langfuse from Codex by decision, not as a pending mapping
status: current
decision_date: 2026-08-03
author: Jacob Hoehler
conviction: strong
project: agent-marketplace
labels:
  - scope
  - write-side
binds:
  - plugins/langfuse/PACKAGE.yaml
supersedes: []
superseded_by: []
derived_from:
  - linear:TEAM-352
  - linear:TEAM-350
  - https://github.com/jdh313/cc-marketplace/pull/26
informed_by: []
---

# 7gf4vb — Exclude langfuse from Codex by decision, not as a pending mapping

## Decision

`langfuse` does not declare a Codex target, and its absence is a reviewed decision rather than an unfinished mapping. It stays out until its transcript reader can parse Codex rollouts, because a package that compiles, installs, and traces nothing is worse than an absent one.

## Scope

- Binds: whether `langfuse` declares `targets.codex`, and how its absence is described in generated-count assertions and compatibility docs.
- Does not bind: the Claude publication, which is unaffected.

## Commitments

- The Codex enrollment set is expressed as the full catalog minus an explicit exclusion list, so a new package is enrolled by default and an omission has to be stated.
- The compatibility doc carries the reason for the exclusion, not merely the fact of it.
- Re-enrollment waits on the transcript reader dispatching on payload shape, so one implementation serves both runtimes.

## Revisit if

- The transcript reader gains Codex row support.
- Codex adopts a rollout format the existing reader can already parse.

## Context

- The plugin's whole function is a `Stop` hook that parses a session transcript and emits one trace per turn.
- The reader keys on Claude Code's JSONL row shape, testing `type` for `user`/`assistant` and then reading `message.role`.
- Codex rollout rows carry `payload` rather than `message`, with types like `response_item`, `event_msg`, and `turn_context`.
- Run against three real Codex rollouts, the plugin's own parser resolved zero turns from 8,127 rows.
- Both its hook events are supported Codex lifecycle events, its argument arrays fold correctly into Codex's single command string, plugin-root variables translate, and the executable payload keeps its mode.
- Codex skips plugin-bundled hooks until the user reviews and trusts them, so nothing runs before an explicit trust step.
- The package presents in the marketplace as an observability integration, which is what a user installing it expects it to be.
- On a run that resolves no turns the hook exits 0 and logs `Processed 0 turns` to a path under `~/.claude`, which is not a location a Codex user has reason to read.
- A separate ticket already scopes porting the transcript reader.

## Why

Everything mechanical about this projection works, which is exactly what makes shipping it wrong. Install, validation, and the trust gate all pass, and what waits on the far side is a hook that runs every turn, reads a transcript it cannot interpret, and reports its own failure only to a log the user has no reason to open.

An observability tool that fails silently is worse than an absent one, because it retires the user's suspicion that anything is wrong. A missing integration prompts someone to go install it. A present one that emits nothing produces an empty dashboard read as an empty period.

Recording this as a decision rather than a gap matters because the two look identical from outside — both are a package with no `targets.codex` block. Without the record, the next person to sweep the catalog for unenrolled packages sees an oversight and closes it, reintroducing the exact failure. The compiler cannot catch that, since the projection is clean.

## Alternatives

- **Enroll with a caveat in the compatibility doc** — rejected: the caveat is invisible at the moment of use, and the failure mode is silence, so nothing would ever surface the note.
- **Enroll and let the trust gate hold it inert** — rejected: the gate defers the problem rather than preventing it; past the gate the plugin does the wrong thing continuously.
- **Port the transcript reader before enrolling the rest of the catalog** — deferred: substantial work that would have blocked fourteen finished packages behind one, and it already has its own ticket.
