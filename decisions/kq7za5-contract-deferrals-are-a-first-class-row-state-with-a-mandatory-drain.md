---
id: "kq7za5"
title: Contract deferrals are a first-class row state with a mandatory drain
status: current
decision_date: 2026-07-10
author: Jacob Hoehler
conviction: tentative
project: cc-marketplace
labels:
  - process
  - write-side
binds:
  - plugins/spec-flow/**
supersedes: []
superseded_by: []
derived_from:
  - .docs/model-review-2026-07-10-contract-v2.md
informed_by: []
---

# kq7za5 — Contract deferrals are a first-class row state with a mandatory drain

## Decision

A deliberately deferred fork is a first-class Decision-log resolution, marked [deferred], distinct from [open] and [resolved]. At close it must materialize as a durable tracked artifact — a spec-flow:capture ticket by default, or a link to an existing one — and close will not cleanly archive a contract that still holds an un-materialized deferral.

## Scope

- Binds: the Decision-log row grammar and close's archive gate.
- Absorbs the "not now, might later" exclusion case that would otherwise land in Out-of-scope.

## Commitments

- Three row tokens map one-to-one to three close fates: open flags, resolved harvests, deferred spawns a follow-up.
- Close gains a gate that blocks archive on an un-materialized deferral.
- The deferral's forward pointer backfills to the spawned artifact's id.

## Revisit if

- spec-flow contracts stop being ephemeral, so a persistent contract could hold a deferral without forwarding it.

## Context

- v2 collapsed deliberate deferral and forgetting into one stray [open] row and had close ask which at archive.
- The contract is ephemeral and its rows die at archive, so a deferral tracked only in the row is lost.
- A deliberate punt is a decision — handled elsewhere — not an unresolved loop.
- spec-flow:capture already mints zero-ceremony Backlog tickets.

## Why

An ephemeral artifact cannot honestly carry "later" — a deferral must hand off to the durable tracked layer or it is just slower forgetting, which is why the drain is mandatory rather than optional. Making [deferred] a distinct token keeps close a structural read, where the token is the close instruction, instead of forcing archaeology on the row's call text — the same goal the whole worksheet is designed around. Reusing [resolved] with the call "defer" would collapse two close fates into one token and reintroduce exactly the parsing the design exists to avoid.

## Alternatives

- **reuse [resolved] with the call set to "defer"** — verdict: rejected: forces close to parse call text to tell a punt from a real decision, defeating the structural-read goal.
- **optional drain, at the closer's discretion** — verdict: rejected: because the contract archives the row, an un-forwarded deferral silently evaporates, so "later" is lost unless the drain is forced.
