---
id: "8vv4qg"
title: Let the committed plugin layout share one hook configuration with Claude
status: current
decision_date: 2026-07-30
author: Jacob Hoehler
conviction: tentative
project: cc-marketplace
labels:
  - architecture
  - repo-shape
binds:
  - plugins/**/PACKAGE.yaml
  - scripts/marketplace/codex_validate.py
supersedes: []
superseded_by: []
derived_from:
  - linear:JUN-341
  - git:0e6c4cd
informed_by:
  - v0a3bm
---

# 8vv4qg — Let the committed plugin layout share one hook configuration with Claude

## Decision

Keep one hook configuration file per plugin in the committed source layout, shared by both runtimes, and let the generated Codex manifest declare that shared path. Materialize the translated, Codex-shaped configuration only into the compiled publication tree. Do not commit a second runtime-specific hook file beside the first.

## Scope

- Binds: the committed plugin directory layout for hook-bearing packages.
- Does not bind: the compiled publication trees, which carry fully translated output.

## Commitments

- Enroll a package for a second runtime only while its hook configuration remains valid for both.
- Keep the native validator checking the committed layout, not only the compiled tree.
- Split the file the moment a shared configuration stops being valid for either runtime.

## Revisit if

- An enrolled package's hook configuration stops being valid configuration for both runtimes, through a field one of them lacks or a construct only one can express.
- A runtime stops resolving the compatibility aliases that make the shared file work today.

## Context

- Hook configuration exists on two surfaces: the compiled publication tree that actually ships, and the committed in-repo layout that both runtimes read from the same plugin directory.
- The plugin directory is shared, so a second runtime-specific file would collide with the first at the same path.
- The one hook-bearing enrolled package declares no fields the second runtime lacks, and its environment references resolve there through documented aliases.

## Why

Committing a second hook file would duplicate a configuration that is currently identical in meaning, creating two files to keep in sync for no present benefit. The seam is safe to accept because it is defended rather than merely tolerated: the native validator opens the declared configuration and rejects fields the runtime lacks and companion paths that were never materialized, so a package whose configuration stops being genuinely shared cannot enroll quietly. The divergence would announce itself as a validation failure, which is the trigger to split.

## Alternatives

- **Commit a runtime-specific hook file and declare that path** — rejected: a second file to keep in sync, duplicating a configuration identical in meaning today.
- **Declare nothing and rely on runtime auto-discovery** — rejected: gives up the machine-checkable link between what the manifest claims and what was materialized.
