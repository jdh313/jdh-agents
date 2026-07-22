---
id: "39j5qb"
title: Contract Decision-log rows carry a supersedes pointer for reversals
status: current
decision_date: 2026-07-10
author: Jacob Hoehler
conviction: tentative
project: cc-marketplace
labels:
  - architecture
  - write-side
binds:
  - plugins/spec-flow/**
supersedes: []
superseded_by: []
derived_from:
  - .docs/model-review-2026-07-10-contract-v2.md
informed_by: []
---

# 39j5qb — Contract Decision-log rows carry a supersedes pointer for reversals

## Decision

A spec-flow contract Decision-log row carries an optional row-level supersedes pointer, with a stable row-id minted on demand, so a mid-change reversal links its successor row back to the original instead of overwriting it.

## Scope

- Binds: the contract worksheet's Decision-log row grammar.
- Does not bind: the ndr atom schema, which already has supersession.

## Commitments

- Rows gain an optional id, minted only when a later row points back.
- Close follows the pointer when harvesting a reversed decision.
- A superseded row is retained in the ledger, never deleted.

## Revisit if

- Rows routinely need full atom supersession semantics (chains, multi-supersede).

## Context

- v2 rows were monotonic: born open, died resolved, terminal, with no supersession field.
- A resolved decision that reversed mid-change had no representable form.
- Editing the row in place destroyed the original call, its why, and its alternative.
- Appending an unlinked second row produced two rows about one fork with no link between them.
- The ndr atom layer's defining feature is supersession.

## Why

The reversal itself — the hard-won "we tried X, it broke on the shape, hence Y" — is usually the most decision-worthy artifact in a whole contract, and both pointer-free options lose it: an in-place edit destroys the history, an unlinked append destroys the link. A row-level pointer adds exactly the one field the "atom-shaped row" claim already promised, keeps the two-state lifecycle intact, and mints ids lazily — the lightest shape that makes intra-contract reversal representable and keeps promotion honestly copy-not-transform.

## Alternatives

- **three-state lifecycle (open/resolved/superseded)** — verdict: rejected: a full state machine is more than an ephemeral per-change scratch space warrants.
- **push reversals to the atom layer only** — verdict: rejected: does not fix the live history loss, since close would have to reconstruct the reversal from the already-overwritten row.
