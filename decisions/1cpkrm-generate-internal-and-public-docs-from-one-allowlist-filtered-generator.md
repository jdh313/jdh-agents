---
id: "1cpkrm"
title: Generate internal and public docs from one allowlist-filtered generator
status: current
decision_date: 2026-07-11
author: Jacob Hoehler
conviction: tentative
project: cc-marketplace
labels:
  - architecture
  - scope
binds: []
supersedes: []
superseded_by: []
derived_from: []
informed_by: []
---

# 1cpkrm — Generate internal and public docs from one allowlist-filtered generator

## Decision

A single docs generator produces both sites, differing only by build scope: the internal build reads the full marketplace.json, and the public build filters plugins through the existing export/public.json allowlist.

## Scope

- Binds: both build scopes share one Astro codebase and component system.
- The allowlist (export/public.json) is the single source of what is public.

## Commitments

- export/public.json stays the one control surface for public-vs-private plugin visibility; the docs inherit it rather than maintaining a second allowlist.
- The generator must accept a scope parameter selecting the full vs the filtered plugin set.

## Revisit if

- The public and internal sites need materially different structure or content, not just a different plugin subset — that would break the single-generator assumption.

## Context

- The repo already publishes an allowlisted subset of plugins to a public repo via export/public.json.
- Two docs audiences were identified: internal (full set) and public (shared subset).
- Visibility (private/public) and scope (full/subset) are not independent axes — "public" is defined as the allowlisted subset.

## Why

Because public is defined as the allowlisted subset, one list already determines both what ships publicly and what the public docs show — so the two sites are the same generator run at two scopes, not two products. A second, separate public site would duplicate the layout and component system and let them drift. Reusing export/public.json as the filter keeps a single seam and a single control surface.

## Alternatives

- **Two separate sites** — verdict: rejected: duplicates the component system and invites drift; the allowlist collapses the two into one generator.
