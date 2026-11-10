---
id: "a1s7hf"
title: Install transponder from dotfiles on the personal host and retire the
  langfuse plugin
status: current
decision_date: 2026-11-10
author: Jacob Hoehler
conviction: strong
project: jdh-agents
labels:
  - repo-shape
  - scope
binds: []
supersedes:
  - wkentm
superseded_by: []
derived_from:
  - linear:JUN-668
informed_by:
  - rdyz4c
---

## Decision

The agent observability tool stays in its own repository, `transponder`. The operator's dotfiles install its Claude Code and Codex hooks on the personal host from transponder's Nix flake, pinned by `flake.lock`. The `langfuse` plugin is retired from this marketplace.

## Scope

- Binds: where agent tracing is installed from, and that this marketplace carries no tracing plugin.
- Does not bind: the tool's internal shape, its language, or which sinks it ships.

## Commitments

- Hook enrollment (Claude Code and Codex `Stop` and `SessionStart`, `timeout: 10`) lives in the operator's dotfiles, on the personal host only.
- Each `transponder` upgrade is a `flake.lock` bump, plus the runtime acceptance `ndr:rdyz4c` requires when the parser or transport changes.
- Decisions binding the plugin's old paths are updated in the change that removes them.

## Revisit if

- Tracing is wanted on a host the operator's dotfiles do not manage, or by other installers of this marketplace.
- AgentForge accepts a package with no artifacts and a published tracing plugin is wanted again.

## Context

- transponder's Nix flake exists as of JUN-671 and exposes the bundled hook for aarch64-darwin.
- Before retirement, the `langfuse` plugin was at v1.5.0, with a 1,746-line Python hook.
- AgentForge v1.3.0 rejects a package definition that declares no artifacts.

## Why

The operator asked (JUN-668, 2026-11-10) for tracing to be set in dotfiles and only on the personal machine, not the work machine. Which host runs tracing is already decided in the host's dotfiles, so a plugin there would only add a second place that enrolls the same hooks and stores the same keys. Installing from the flake puts the pin, the hooks and the keys in one host config; keys come from a `.env` on the personal host instead of plugin `userConfig`.

With the hooks gone, the plugin had nothing left to publish, and AgentForge cannot compile a package that has no artifacts, so the plugin was retired rather than kept as a shell.

## Alternatives

- **Thin installer plugin that pins a transponder release** (`ndr:wkentm`) — superseded: the operator chose dotfiles as the one install point, and the plugin would duplicate the enrollment the host config already does.
- **Keep the Python hook** — rejected, as in `ndr:wkentm`: adding harnesses and sinks grows a file that is already 1,746 lines.
- **Keep an empty `langfuse` package with a stub artifact** — rejected: AgentForge requires at least one artifact, and a stub would exist only to satisfy the compiler.
