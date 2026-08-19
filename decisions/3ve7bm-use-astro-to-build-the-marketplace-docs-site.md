---
id: "3ve7bm"
title: Use Astro to build the marketplace docs site
status: current
decision_date: 2026-07-11
author: Jacob Hoehler
conviction: tentative
project: jdh-agents
labels:
  - tooling
binds: []
supersedes: []
superseded_by: []
derived_from: []
informed_by: []
---

# 3ve7bm — Use Astro to build the marketplace docs site

## Decision

The jdh-agents documentation site will be built with Astro.

## Scope

- Binds: the tool that generates the docs site from plugin metadata.
- Does not bind: Starlight vs plain Astro for the layer on top of Astro — that is still open.

## Commitments

- Introduces a Node/npm toolchain into an otherwise Python repo, contained to the docs subdirectory (its own package.json, node_modules gitignored).

## Revisit if

- The site never needs interactivity beyond static pages plus search, and the Node toolchain proves a maintenance burden — Hugo becomes the simpler pick.
- A chosen approach needs a capability Astro lacks.

## Context

- All plugin metadata already lives as JSON (marketplace.json plus per-plugin plugin.json).
- A docs site was wanted to surface that data; it will be CI-regenerated from the JSON on plugin changes.
- Several docs-as-code tools were catalogued (Starlight, Zensical, Docusaurus, Material for MkDocs) and a wider field surveyed (Hugo, VitePress, Nextra, Fumadocs, Eleventy).
- Astro and Hugo both natively generate one page per JSON entry; the built static output needs no runtime regardless of tool.
- Hugo ships as a single Go binary with no dependency tree to maintain.
- Astro carries a Node/npm toolchain but provides islands-architecture client interactivity and access to the npm component ecosystem.
- Template and component authoring is AI-handled either way.

## Why

The field narrowed to Astro vs Hugo — both generate pages from JSON natively, so capability was a tie. The maintenance and longevity edge initially credited to Hugo (single Go binary, no dependency churn) deflated once the site was recognized as CI-regenerated from marketplace.json: it never sits untouched long enough to bit-rot, and a pinned build reproduces regardless. With capability and longevity tied and authoring AI-handled, the tiebreaker became headroom — Astro's islands architecture and access to the npm component ecosystem leave room for a future app-like plugin browser (faceted filter, comparison tool) that Hugo would force into hand-rolled vanilla JS.

## Alternatives

- **Hugo** — verdict: rejected: capability and longevity tied Astro, but it offers no component-ergonomics headroom for future interactive browsing; retained as the fallback if the Node toolchain becomes a burden.
- **Starlight** — verdict: rejected: its docs chrome is Markdown-bound and fights JSON-driven pages.
- **Zensical** — verdict: rejected: no native per-entry page generation yet (immature ecosystem).
- **Docusaurus / Fumadocs** — verdict: rejected: heavier React/Next toolchain than the job warrants.
- **Eleventy** — verdict: deferred: simplest data-driven generation but zero docs chrome out of the box.
