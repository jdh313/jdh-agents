# jdh-agents

Personal plugin marketplace shared by Claude Code and Codex, with canonical
AgentForge definitions, native runtime manifests, and automated validation.
Claude supports the full catalog; Codex enrolls 16 packages, with completed
fresh-task runtime smoke acceptance for 8.

See [Dual-agent operating model](docs/dual-agent-operating-model.md) for
ownership boundaries, runtime mappings, installation, and runtime acceptance.

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
│   ├── claude/               # Self-contained Claude marketplace root (19 packages)
│   │   ├── .claude-plugin/marketplace.json
│   │   └── plugins/[name]/
│   └── codex/                # Self-contained Codex marketplace root (16 packages)
│       ├── .agents/plugins/marketplace.json
│       └── plugins/[name]/
├── .betterleaks.toml         # Privacy-gate rules
├── .betterleaks-baseline.json  # Pre-existing findings, accepted once
├── scripts/                  # Automation tooling
│   ├── agentforge.sh         # Fetches + sha256-verifies the pinned compiler
│   ├── privacy-scan.sh       # History secret/privacy gate (pinned Betterleaks)
│   └── tests/                # Gate self-test + attention-workflow behavior
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
> every plugin is ready to install as-is. *Authoring* (the `compile` step below)
> additionally needs the [AgentForge compiler](https://github.com/jdh313/agentforge),
> which `scripts/agentforge.sh` fetches and verifies on first use — no manual
> install, and no credential, since that repository is public.

### Prerequisites

Nothing here is needed to *browse* the repo. These are what the plugins and the
tooling expect at runtime.

**For the marketplace tooling** (`compile`, `check`):

- `bash` and `curl` — `scripts/agentforge.sh` fetches the pinned compiler binary
  and verifies it against a per-platform sha256 before executing it
- `git` — `scripts/privacy-scan.sh` scans committed history, so it needs the
  repository's commits (in CI, `actions/checkout` with `fetch-depth: 0`)
- [`uv`](https://docs.astral.sh/uv/) — only to run
  `scripts/tests/test_attention_workflow.py`, which declares its own `pytest`
  dependency in a PEP 723 header. The repo declares no project, so there is
  nothing to install and no lockfile to sync.

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
| `em` | A tracker (Linear MCP server, Fibery MCP server, or `gh`) and a VCS; `ndr`, `workspaces`, `craft`, `pm` optional |
| `craft` | `gh`, `git`/`jj`, `ndr`; IaC skills additionally want `tflint`, `checkov`, `trivy`, `infracost` |
| `langfuse` | A Langfuse account + `uv` on `PATH` (the Stop hook runs via `uv run`) |
| `skillsmith` | `gh` on `PATH` (for upstream-review) |
| `introspect` | Local Claude Code transcripts under `~/.claude/projects/`; invocable from Claude Code or Codex, but does not parse Codex rollout files |
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

Codex local marketplace. Fifteen of the nineteen packages declare
`targets.codex` and are therefore enrolled -- enrollment means the package
compiled and published for Codex, not that it was exercised on a Codex runtime.
Six have a passing fresh-task smoke test on top of that: the four installed
below plus `librarian` and `teach`.

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
hand-edit it -- `agentforge compile` rewrites it, and `agentforge check` fails on
drift in it, reporting the path with a `<root>` prefix rather than relative to
`marketplaces/`.

### Adding a New Plugin (maintainer-only)

Step 3 requires the [AgentForge compiler](https://github.com/jdh313/agentforge).

1. Create plugin directory:
   ```bash
   mkdir -p plugins/my-plugin
   ```

2. Add plugin files and an authoritative `plugins/my-plugin/PACKAGE.yaml`. Declare
   only the runtimes whose native mappings have been validated.

3. Regenerate the committed publications with the pinned compiler:
   ```bash
   scripts/agentforge.sh compile MARKETPLACE.yaml --out marketplaces
   ```
   The pinned compiler is fetched and sha256-verified on first use; nothing to
   install or configure.

4. Verify the committed tree, including the native Claude validator:
   ```bash
   scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native
   ```

5. Run the privacy gate over the whole tree:
   ```bash
   scripts/privacy-scan.sh
   ```

See [`docs/agentforge-compatibility.md`](docs/agentforge-compatibility.md) for
the current target matrix, payload handling, and reviewed compatibility
limitations.

## Tooling

Two commands drive the registry. There is no repo-specific CLI to install.

### Compile

Compiles `MARKETPLACE.yaml` into the committed publication roots under
`marketplaces/`, plus the root manifest beside `MARKETPLACE.yaml`. AgentForge
stages into a temporary directory and publishes by rename, so a failed compile
leaves the committed tree untouched and a successful one prunes every stale file.

```bash
scripts/agentforge.sh compile MARKETPLACE.yaml --out marketplaces
```

`scripts/agentforge.sh` is a ~40-line wrapper that pins the compiler by release
version and per-platform sha256, fetches it on first use, verifies the bytes
before executing them, and caches it under `.cache/agentforge/<version>/`. The
hash is re-verified on every run, so a corrupted or tampered cache is replaced
rather than trusted. CI runs this same script — there is no separate CI pin.

### Check (merge gate)

Diffs the compilation plan against the committed tree without writing, and
reports missing, extra, changed, and permission drift. It also gates managed
output content, parses every managed `.json`, validates skill frontmatter,
checks manifest parity, and resolves every declared plugin path. With
`--claude-native` it cross-checks the Claude publication using
`claude plugin validate --strict`.

```bash
scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native
```

AgentForge owns the cross-runtime translation from Claude
`disable-model-invocation: true` metadata to Codex
`policy.allow_implicit_invocation: false` skill sidecars, and reports it as a
`translated-construct` note during `check`.

### Privacy gate

```bash
scripts/privacy-scan.sh
```

Hard-fails on absolute machine-home paths and secret-shaped assignments across
the repository's committed history. Every finding fails; there is no advisory
tier. The pinned Betterleaks binary fetches and sha256-verifies itself on first
use, so there is nothing to install.

This is the one gate AgentForge cannot own: AgentForge only ever sees files a
publication declares, so a leak in an undeclared file — a doc, a workflow, a
decision atom — is invisible to it.

## CI/CD

GitHub Actions runs on every push and pull request:
- `scripts/tests/test_privacy_gate.sh`, then `scripts/privacy-scan.sh` over committed history
- `agentforge check --claude-native` with AgentForge pinned to release `v0.4.0`
- `claude plugin validate --strict` for the generated Claude publication,
  using Claude Code `2.1.216`

[`jdh313/agentforge`](https://github.com/jdh313/agentforge) publishes
per-platform release binaries, so the workflow downloads the pinned
`agentforge-linux-x64` binary and verifies it against a recorded SHA256
checksum instead of checking out and building the compiler from source.

## Metadata ownership

`MARKETPLACE.yaml` and `plugins/*/PACKAGE.yaml` are the only maintained sources
of marketplace and package metadata, and `plugins/` is the only maintained
source of plugin content. Everything under `marketplaces/` is committed
compiler output — manifests and bodies alike. Edit the source and run
`scripts/agentforge.sh compile`; never hand-edit a file under `marketplaces/`,
because the next compile republishes the whole tree and silently discards the edit.

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
