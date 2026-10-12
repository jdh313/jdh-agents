# Standalone Pi packages

This directory holds committed generated Pi packages, not a Pi marketplace.
Author source under `plugins/<name>/`; its adjacent `PACKAGE.pi.yaml` declares
what ships. Never hand-edit the generated package subdirectories.

| Package | Source definition | Invocation |
| --- | --- | --- |
| EM | `plugins/em/PACKAGE.pi.yaml` | `/skill:em-scope`, `/skill:em-lead` |
| Workspaces | `plugins/workspaces/PACKAGE.pi.yaml` | `/skill:workspaces`; opt-in native jjx provider |

## Rebuild and check

From the repository root:

```sh
scripts/pi-packages.sh compile
scripts/pi-packages.sh check
```

The script uses local AgentForge **2.1.0** at `$HOME/Projects/agentforge`.
Set `AGENTFORGE_PROJECT` to use a different source-checkout location. This is
local source tooling, not a verified release-binary pin; Bun is required.
The existing Claude/Codex compiler pin and marketplace publication stay unchanged.

Every `plugins/*/PACKAGE.pi.yaml` builds into its corresponding
`packages/pi/<name>/`. Each package subdirectory is an owned snapshot replaced
on compilation; keep dependencies, settings, and other consumer data elsewhere.
`check` does not write or execute extensions. Removing/renaming a definition
requires explicitly reviewing and removing its old publication; the script does
not silently prune orphan package directories.

Pi outputs live outside `marketplaces/` because the marketplace compiler owns
and replaces that separate snapshot. Commit source changes and regenerated Pi
output together. This README is maintained documentation outside the generated
package roots.

## Activation is separate

Dotfiles/Pi settings should reference these packages, not duplicate their code.
From this repository, explicit local installation is:

```sh
pi install "$PWD/packages/pi/workspaces"
pi install "$PWD/packages/pi/em"
```

These commands are examples, not run by compilation/checking. Local packages
load in place: rebuilding affects the next load. Keep the checkout at a stable
path and restart/reload Pi after rebuilding. Do not load both authoring source
and generated packages; that can duplicate extensions or collide skill names.

Load the separately installed `@gotgenes/pi-subagents` before Workspaces.
Workspaces defaults to **no isolated agent types**; review its
[`pi/README.md`](workspaces/pi/README.md) before supplying `--jjx-workspaces`.
EM's prerequisites, invocation, and working-time runtime trial expectations are
in its [`pi/README.md`](em/pi/README.md). Packaging alone does not prove runtime
behavior. No automatic installation, trust change, or dedicated E2E gate is
introduced here.
