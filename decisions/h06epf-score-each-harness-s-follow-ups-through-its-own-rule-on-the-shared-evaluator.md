---
id: "h06epf"
title: Score each harness's follow-ups through its own rule on the shared evaluator
status: current
decision_date: 2026-10-15
author: Jacob Hoehler
conviction: strong
project: jdh-agents
labels:
  - architecture
  - scope
binds:
  - docs/langfuse-human-followup-contract.md
supersedes: []
superseded_by: []
derived_from:
  - Claude Code session a7c25421-a3b6-4e7d-a9db-f93dd575e9e0 (2026-10-15)
  - docs/langfuse-human-followup-contract.md
informed_by: []
---

# h06epf — Score each harness's follow-ups through its own rule on the shared evaluator

## Decision

Every harness that exports human follow-up observations gets its own Langfuse evaluation rule, filtered on that harness's observation name and `metadata.source`. All of these rules use the one shared coding-agent feedback evaluator with the same `input` to `context` and `output` to `followup` mapping. No harness widens another harness's rule.

## Scope

- Binds: evaluation rules for human follow-up observations from Pi, Claude Code, and any future exporter such as Codex.
- Does not bind: the evaluator definition itself, which stays a single shared evaluator rather than one copy per harness.

## Commitments

- A new harness adds its own rule; it never edits an existing rule's filters.
- Every exporter sets a distinct `metadata.source`, because rule filters select on it.
- An evaluator change (questions, model, version) applies to every harness at once.

## Revisit if

- Langfuse lets one rule carry per-source sampling and enablement.
- Harnesses need different rubrics, which calls for separate evaluators rather than separate rules.

## Context

- A Langfuse evaluation rule pairs evaluators with an observation filter, a sampling rate, and an enabled flag.
- The Pi rule matched only observations named `Pi Human Follow-up` with `metadata.source = pi-feedback`.
- Claude Code follow-ups needed a `metadata.submission_kind = prompt` filter to exclude slash commands, and Pi never sets that key.
- The brief for the Claude Code work ruled out changing the live Pi rule or duplicating the evaluator.

## Why

A shared evaluator keeps one rubric and one series of score names, so rates from different harnesses can be compared and a rubric change lands everywhere at once. A separate rule per harness gives each one its own enable, sampling, and filter controls: pausing Claude Code scoring means disabling one rule, not editing a filter that Pi also depends on. A combined rule would have to pass Pi rows that lack `submission_kind` while rejecting Claude Code slash-command rows. That works only if Langfuse's handling of a missing metadata key cooperates, and every later edit made for one harness would risk the other.

## Alternatives

- **Widen the Pi rule to match both harnesses** — rejected: one filter would control both harnesses' enablement and sampling, and the Claude Code slash-command exclusion would need a negative filter whose behaviour on a missing key is unverified.
- **Duplicate the evaluator per harness** — rejected: the rubric copies would drift apart and the score series would split.
