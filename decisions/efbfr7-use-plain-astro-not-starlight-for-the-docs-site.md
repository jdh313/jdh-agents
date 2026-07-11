---
id: "efbfr7"
title: Use plain Astro, not Starlight, for the docs site
status: current
decision_date: 2026-07-11
author: Jacob Hoehler
conviction: tentative
project: cc-marketplace
labels:
  - architecture
  - tooling
binds: []
supersedes: []
superseded_by: []
derived_from:
  - https://linear.app/junglelan/issue/JUN-271
informed_by:
  - 3ve7bm
  - 1cpkrm
---

# efbfr7 — Use plain Astro, not Starlight, for the docs site

## Decision

The cc-marketplace docs site is built on plain Astro. Starlight, Astro's docs
theme, is not layered on top; the site's chrome is hand-built.

## Scope

- Binds: the layout/chrome layer on top of Astro — the open question 3ve7bm left unresolved.
- Does not bind: the choice of Astro itself (3ve7bm), or the single-generator shape (1cpkrm).

## Commitments

- Sidebar nav, search, theming, and dark mode are hand-built, not inherited from Starlight.
- Pages are plain Astro routes driven directly from marketplace.json — no Markdown content-collection intermediary.

## Revisit if

- The site grows a large body of hand-authored Markdown prose (guides, tutorials) where Starlight's docs chrome would earn its keep.
- Hand-building nav/search/theming proves costlier than the JSON-fit friction Starlight would have imposed.

## Context

- The whole site is generated from marketplace.json plus per-plugin plugin.json; 1cpkrm commits to one JSON-driven generator.
- Starlight's sidebar is bound to a Markdown content collection.
- JSON-driven pages would live as dynamic routes outside Starlight's docs tree, losing its auto-sidebar.
- The site is mostly-generated and internal, with little hand-authored prose.
- 3ve7bm chose Astro but explicitly left the Starlight-vs-plain-Astro layer open.

## Why

The site's content is JSON, not Markdown, so Starlight's central affordance — an
auto-generated sidebar built from a Markdown content collection — works against
the grain: JSON pages fall outside the docs tree and forfeit the very chrome
Starlight exists to provide. Plain Astro keeps a clean, direct data flow from
marketplace.json to rendered routes, at the cost of hand-building nav, search,
and theming — a bounded, one-time cost for an internal, mostly-generated site
with little prose. Starlight's docs-chrome-for-free pays off most when the
content is Markdown; here it isn't.

## Alternatives

- **Starlight** — verdict: rejected: its Markdown-bound sidebar fights JSON-driven pages, forfeiting the auto-chrome that is its main draw; hand-built layout on plain Astro keeps the data flow clean.
