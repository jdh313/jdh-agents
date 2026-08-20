# jdh-agents

Personal plugin marketplace shared by Claude Code and Codex, with canonical
AgentForge definitions, native runtime manifests, and automated validation.
Claude supports the full catalog; private Codex support currently covers
`commit`, `craft`, `linear`, and `spec-flow`.

See [Dual-agent operating model](docs/dual-agent-operating-model.md) for
ownership boundaries, runtime mappings, installation, and pilot acceptance.

## Directory Structure

```
jdh-agents/
├── MARKETPLACE.yaml          # Canonical AgentForge collection definition
├── .claude-plugin/           # Compiler output — the remote-install entry point
│   └── marketplace.json      # Root copy of the Claude publication
├── plugins/                  # Authoring source — hand-edited, never installed from
│   └── [plugin-name]/
│       ├── PACKAGE.yaml      # Canonical AgentForge package definition
│       └── ...               # Plugin files (commands, agents, skills, etc.)
├── marketplaces/             # Compiler output — committed, never hand-edited
│   ├── claude/               # Self-contained Claude marketplace root (16 plugins)
│   │   ├── .claude-plugin/marketplace.json
│   │   └── plugins/[name]/
│   └── codex/                # Self-contained Codex marketplace root (7 pilots)
│       ├── .agents/plugins/marketplace.json
│       └── plugins/[name]/
├── scripts/                  # Automation tooling
│   └── marketplace/          # `marketplace` CLI: sync, validate, lint, scan, check
└── .github/workflows/        # CI/CD automation
    └── validate.yml          # GitHub Actions workflow
```

Each directory under `marketplaces/` is a complete marketplace root, so a
runtime is pointed at that directory rather than at the repository. Pointing a
runtime at the repository root is what previously let Codex resolve canonical
Claude sources instead of its own projection.

The one exception is `.claude-plugin/marketplace.json`, which exists so that
Claude Code can install from the repository remotely -- see
[Root manifest](#root-manifest). It is a compiled copy, not a hand-written one,
and it resolves packages back into `marketplaces/claude/`.

## Usage

> **Consuming vs. authoring.** Installing and using these plugins needs nothing
> but this repository — `marketplaces/` is compiled output and is committed, so
> every plugin is ready to install as-is. *Authoring* (the `sync` step below)
> additionally needs the [AgentForge compiler](https://github.com/jdh313/agentforge),
> which is public, at the pinned revision. Everything else — install,
> `validate`, `lint`, `pytest` — runs from a plain clone.

### Prerequisites

Nothing here is needed to *browse* the repo. These are what the plugins and the
tooling expect at runtime.

**For the marketplace tooling** (`validate`, `lint`, `check`, `pytest`):

- [`uv`](https://docs.astral.sh/uv/) on `PATH`
- Python >= 3.13 (`uv` will fetch it if missing)

**Per plugin.** Most plugins are self-contained, but several are inert or
misleading without an external account or binary. Check this table before
installing one and wondering why it does nothing:

| Plugin | Needs |
|---|---|
| `librarian`, `debate` | Obsidian vault + `obsidian-mcp` MCP server; `obsidian-cli` on `PATH` |
| `coach` | Obsidian vault + `obsidian-cli`; Todoist (via the claude.ai connector) |
| `compass` | Obsidian vault + `obsidian-cli`; Kagi MCP server (optional, for research) |
| `teach` | Obsidian vault + `obsidian-cli`; DEVONthink MCP server (optional) |
| `pm` | Obsidian vault; Linear MCP server; `ndr` on `PATH` |
| `linear`, `spec-flow` | Linear MCP server (`spec-flow` also uses Context7) |
| `attention-workflow` | Linear or Fibery MCP server |
| `craft` | `gh`, `git`/`jj`, `ndr`; IaC skills additionally want `tflint`, `checkov`, `trivy`, `infracost` |
| `langfuse` | A Langfuse account + `uv` on `PATH` (the Stop hook runs via `uv run`) |
| `skillsmith` | `gh` on `PATH` (for upstream-review) |
| `introspect` | Local Claude Code transcripts under `~/.claude/projects/` |
| `shake-tune` | Klippain Shake Tune PNG output from a Klipper printer |
| `commit`, `feedback` | Nothing beyond `git` (`commit` also supports `jj`) |

Vault-backed plugins default to a vault named `Loose Ends`. That is an example,
not a requirement — point them at your own vault by editing the paths in the
skill bodies.

### Installing the Marketplace

Claude Code installs remotely, with no clone:

```bash
/plugin marketplace add jdh313/jdh-agents
```

That resolves `.claude-plugin/marketplace.json` at the repository root, which is
a compiled copy of the Claude publication whose package sources point back into
`marketplaces/claude/`. It is generated, never hand-written -- see
[Root manifest](#root-manifest).

A local clone still works, and is what Codex needs:

```bash
git clone https://github.com/jdh313/jdh-agents
/plugin marketplace add /path/to/jdh-agents/marketplaces/claude
```

Codex local marketplace and pilots:

```bash
codex plugin marketplace add /path/to/jdh-agents/marketplaces/codex
codex plugin add commit@jdh-agents
codex plugin add craft@jdh-agents
codex plugin add linear@jdh-agents
codex plugin add spec-flow@jdh-agents
```

Both publications keep the marketplace name `jdh-agents`, so an existing
install survives the repoint: only the path each runtime resolves changes.

### Root manifest

Claude Code's `marketplace add <owner>/<repo>` form reads
`.claude-plugin/marketplace.json` at the repository root, so remote install
needs a manifest there -- but the compiled Claude publication lives under
`marketplaces/claude/`, and its package sources are relative to that directory.

`MARKETPLACE.yaml`'s Claude publication therefore declares `root-manifest: true`.
AgentForge writes a second copy of the same registry at the repository root and
rewrites every package source from `./plugins/<name>` to
`./marketplaces/claude/plugins/<name>`, so both copies enrol the same packages
and resolve to the same bytes. The Codex publication does not declare it: Codex
is installed from a local clone, and a second root file would collide with
nothing useful.

Like everything under `marketplaces/`, the root manifest is generated. Do not
hand-edit it -- `uv run marketplace sync` rewrites it, and
`uv run marketplace check` fails on drift in it, reporting the path relative to
the repository root rather than to `marketplaces/`.

### Adding a New Plugin (maintainer-only)

Step 3 requires the [AgentForge compiler](https://github.com/jdh313/agentforge).

1. Create plugin directory:
   ```bash
   mkdir -p plugins/my-plugin
   ```

2. Add plugin files and an authoritative `plugins/my-plugin/PACKAGE.yaml`. Declare
   only the runtimes whose native mappings have been validated.

3. Regenerate the committed native manifests with the pinned compiler:
   ```bash
   env AGENTFORGE_PROJECT=/path/to/agentforge-at-1dba647 \
     uv run marketplace sync
   ```

4. Validate the committed publications (read-only drift + schema + lint):
   ```bash
   uv run marketplace check
   ```

5. Run the full-corpus acceptance suite against the pinned compatible
   AgentForge checkout, then verify the committed tree with the native
   Claude validator:
   ```bash
   export AGENTFORGE_PROJECT=/path/to/agentforge-at-1dba647
   uv run pytest -q
   agentforge check MARKETPLACE.yaml --out marketplaces --claude-native
   ```

See [`docs/agentforge-compatibility.md`](docs/agentforge-compatibility.md) for
the current target matrix, payload handling, and reviewed compatibility
limitations.

## Marketplace CLI

A single tool (`scripts/marketplace/`) drives the registry. Run via `uv run marketplace <command>`:

### Sync

Compiles `MARKETPLACE.yaml` with AgentForge and materializes only the two root
marketplace manifests, all 15 Claude package manifests, and the five declared
Codex pilot manifests. It never replaces maintained skills, agents, commands,
hooks, references, or other source content.

```bash
env AGENTFORGE_PROJECT=/path/to/agentforge-at-1dba647 uv run marketplace sync
# use `sync --check` to fail on drift without writing
```

### Validate

Schema-validates a marketplace:

```bash
uv run marketplace validate                 # Claude
uv run marketplace validate --format codex  # Codex pilots
uv run marketplace validate --format codex --manifest PATH --plugins-root PATH  # generated publication
```

The Codex form validates the generated marketplace, each declared local plugin
manifest, skill metadata and explicit-only sidecars, and rejects missing or
undeclared materialized packages. Codex does not currently expose a native
non-interactive `plugin validate` command, so this repository-owned validator
is the native merge gate for the declared Codex publication.

AgentForge owns the cross-runtime translation from Claude
`disable-model-invocation: true` metadata to Codex
`policy.allow_implicit_invocation: false` skill sidecars. jdh-agents's
full-corpus suite verifies that translation against the real canonical corpus;
it does not reimplement the compiler rule.

### Lint

Checks plugin files for correctness:

```bash
uv run marketplace lint
```

### Check (merge gate)

Recompiles in a temporary directory, checks all committed generated manifests,
validates both repository-native publications, and runs lint. This command is
read-only and is the CI entrypoint:

```bash
uv run marketplace check
```

## CI/CD

GitHub Actions runs on every push and pull request:
- `uv run marketplace check` (Claude drift + Claude/Codex schemas + lint)
- `uv run pytest` with AgentForge pinned to release `v0.2.0`
- deterministic full-corpus compilation and read-only drift checks
- `claude plugin validate --strict` for the generated Claude publication,
  using Claude Code `2.1.216`
- `uv run marketplace validate --format codex` for the generated Codex publication

[`jdh313/agentforge`](https://github.com/jdh313/agentforge) publishes
per-platform release binaries, so the workflow downloads the pinned
`agentforge-linux-x64` binary and verifies it against a recorded SHA256
checksum instead of checking out and building the compiler from source. It
previously required an `AGENTFORGE_DEPLOY_KEY` repository secret and failed
closed without it; that requirement is gone now that nothing is checked out.

## Metadata ownership

`MARKETPLACE.yaml` and `plugins/*/PACKAGE.yaml` are the only maintained sources
of marketplace and package metadata, and `plugins/` is the only maintained
source of plugin content. Everything under `marketplaces/` is committed
compiler output — manifests and bodies alike. Edit the source and run
`uv run marketplace sync`; never hand-edit a file under `marketplaces/`, because
the next sync republishes the whole tree and silently discards the edit.

## Support

This is a personal marketplace maintained by one person, published so others can
install it. There is no service-level agreement, and new plugin submissions are
unlikely to be merged — forking is a first-class answer.

- **Something is broken:** open an issue with the
  [Plugin bug](https://github.com/jdh313/jdh-agents/issues/new?template=plugin-bug.yml)
  or [Marketplace tooling bug](https://github.com/jdh313/jdh-agents/issues/new?template=tooling-bug.yml)
  template.
- **Something is unsafe:** report it privately — see [`SECURITY.md`](SECURITY.md).
  Read the threat model there before installing; plugins are instructions and
  scripts your agent executes with your permissions, and three of them ship
  hooks that run automatically.
- **You want to change something:** [`CONTRIBUTING.md`](CONTRIBUTING.md) covers
  what lands, the pinned-compiler workflow, and the install trap behind most
  "my copy is stale" reports.

## License

Apache-2.0 (see [`LICENSE`](LICENSE)).

Portions are derived from third-party work under other terms — notably twelve
skills across `craft`, `pm`, `skillsmith`, and `teach` adapted from
[`mattpocock/skills`](https://github.com/mattpocock/skills) (MIT), and the
`langfuse` plugin, forked from
[`langfuse/Claude-Observability-Plugin`](https://github.com/langfuse/Claude-Observability-Plugin)
(MIT). Both upstreams' notices are reproduced in full. Required notices, the full MIT text, and a per-skill provenance table are in
[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md). Each adapted skill also
carries `upstream:` provenance in its frontmatter and an `UPSTREAM.md` ledger of
intentional divergences.
