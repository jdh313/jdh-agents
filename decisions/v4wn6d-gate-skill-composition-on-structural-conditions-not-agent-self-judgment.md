---
id: "v4wn6d"
title: Gate skill composition on structural conditions, not agent self-judgment
status: current
decision_date: 2026-07-27
author: Jacob Hoehler
conviction: tentative
project: agent-marketplace
labels:
  - architecture
  - process
binds:
  - plugins/spec-flow/skills/**
  - plugins/craft/skills/**
supersedes: []
superseded_by: []
derived_from: []
informed_by: []
---

# v4wn6d — Gate skill composition on structural conditions, not agent self-judgment

## Decision

A cross-skill composition hook triggers on a condition observable from the repo or the change itself — a file's presence, a named structural property — never on the authoring agent's in-conversation judgment about output it produced itself.

## Scope

- Binds: composition hooks between plugins in this marketplace, where one skill invokes or suggests another mid-run.
- Does not bind: a skill's own `description` / `when_to_use` triggers, which the harness matches against the user's request rather than the skill evaluating them mid-run.

## Commitments

- Every composition hook states its trigger as a checkable condition, and the check lands in the hosting skill's context-gathering phase so the condition has an input by the time it is evaluated.
- A hook whose trigger is already structural stays a suggestion. Converting one to a gate needs separate justification, because a gate duplicating an always-loaded rule fires the same review twice.
- A hosting skill that invokes rather than suggests carries `Skill` in its `allowed-tools`.

## Revisit if

- Structural triggers fire often enough that drafting routinely stalls on gates.
- The harness gains a way for one skill to observe another's trigger evaluation directly.

## Context

- `spec-flow:draft` hooked `craft:grill-with-docs` on the condition "if contested or fuzzy vocabulary surfaces during the conversation".
- The drafting agent authors the contract's domain nouns itself, so that hook asked it to detect drift in terminology it had just chosen.
- Vocabulary written into a contract propagates: *Done when* bullets, *Out of scope* fences, and Decision-log rows are all phrased in domain nouns, and `close` migrates them into ndr atoms.
- The `craft:interrogate-model` hook in the same skill already stated its trigger as a structural property of the change — a new axis, role, or principal type.
- `~/dotfiles/claude/rules/model-representability.md` fires `interrogate-model` on those same structural triggers at the always-loaded rule layer.

## Why

A judgment trigger asks the agent to audit an artifact it just produced, which is the position from which drift is least visible — the nouns were chosen precisely because they seemed right. So the observable failure is not that such a hook fires rarely; it is that it fires only once the user has already noticed, by which point the hook has contributed nothing. Sharpening the wording of a judgment trigger does not repair this, because the sharper trigger still routes through the same judgment.

The asymmetry decides the gate-versus-suggestion split. A wrong noun is nearly free to correct at draft time and expensive to unwind after close, so occasionally paying for an unnecessary interview is the cheaper side to err on. Where a trigger is already structural that argument does not apply: the hook fires reliably as a suggestion, and hardening it would only duplicate a rule that already fires on its own.

## Alternatives

- **Sharpen the judgment trigger's wording** — rejected: a more precise description of "contested vocabulary" still requires the authoring agent to judge its own output.
- **Gate every composition hook unconditionally** — rejected: hooks with structural triggers have no defect to fix, and a gate duplicating an always-loaded rule double-fires the same heavy review.
- **Drop the hook and rely on the user to invoke** — rejected: preserves exactly the "fires only when the user already noticed" failure the gate exists to close.
