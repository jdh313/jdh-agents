---
id: "zfvewx"
title: Publish the public docs output-only, keeping source private
status: current
decision_date: 2026-07-11
author: Jacob Hoehler
conviction: tentative
project: agent-marketplace
labels:
  - deployment
binds: []
supersedes: []
superseded_by: []
derived_from: []
informed_by: []
---

# zfvewx — Publish the public docs output-only, keeping source private

## Decision

The public documentation site is published output-only: private CI builds the public scope and pushes the static dist/ to a public host, while the Astro source is not exported and the public plugins repo stays plugins-only.

## Scope

- Binds: the public deploy pipeline ships built HTML, not source.
- Does not bind: which public host serves it (GitHub Pages vs other) — still open.

## Commitments

- The docs generator source stays in the private repo; the public repo gains no build tooling.
- CI owns building the public scope and pushing dist/ to the public host.

## Revisit if

- The docs site source should become public or forkable by others.

## Context

- The public plugins repo (shared-claude-plugins) is a curated derived artifact, never hand-edited — the export ships only current file state, never source or history.
- The docs generator lives in the private repo.
- The open question was whether to publish just the built output or also export the source.

## Why

Publishing only the built dist/ keeps the generator logic and any private-data references inside the private repo and spares the public repo any build tooling — the least machinery, and consistent with the repo's existing derived-artifact philosophy, where only current file state ships and never source or history. Exporting the Astro source would let others fork the site but adds an export path and a second build environment for no benefit to a personal marketplace.

## Alternatives

- **Export site source to public repo** — verdict: rejected: adds export machinery and a second build environment; source-forkability isn't wanted for a personal marketplace.
