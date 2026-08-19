---
id: "swsskq"
title: Host the docs site in-repo as a subdirectory
status: current
decision_date: 2026-07-11
author: Jacob Hoehler
conviction: tentative
project: agent-marketplace
labels:
  - repo-shape
binds: []
supersedes: []
superseded_by: []
derived_from: []
informed_by: []
---

# swsskq — Host the docs site in-repo as a subdirectory

## Decision

The documentation site lives inside the cc-marketplace repository as a subdirectory, not in a separate repository.

## Scope

- Binds: the docs generator reads marketplace.json and plugins/*/plugin.json in place.
- Does not bind: the subdirectory name (docs/ vs site/ vs www/) — still open.

## Commitments

- The Astro/Node project coexists with the Python marketplace tooling in one repo, contained to the subdirectory.
- The public export must continue to exclude the docs subdirectory (it copies only allowlisted plugins plus a regenerated manifest).

## Revisit if

- The docs site source must become public or forkable, which would move it toward the public repo.

## Context

- cc-marketplace is the private source of truth holding all plugins; a subset is exported one-way to a public repo.
- The generator's input (marketplace.json, plugin.json) lives in this repo.
- The internal build's audience is personal and documents the full private plugin set.
- The export gate copies only allowlisted plugins/<name>/ plus a regenerated manifest, never a top-level non-plugin directory.

## Why

Co-locating the generator with the JSON it reads makes the docs lockstep with the data for free — no submodule, no cross-repo copy, no drift. A separate repo would reintroduce exactly the data-sync plumbing the private-source-of-truth-plus-export pattern exists to avoid. Because the internal build documents private plugins it must sit with the private source anyway, and the existing export gate keeps a top-level docs directory private automatically, so in-repo carries no leak risk.

## Alternatives

- **Separate docs repo** — verdict: rejected: reintroduces cross-repo data sync and drift; only justified if the site source must be public.
