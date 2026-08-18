# cc-marketplace

Personal plugin marketplace shared by Claude Code and Codex, with canonical
AgentForge definitions, native runtime manifests, and automated validation.
Claude supports the full catalog; private Codex support currently covers
`commit`, `craft`, `linear`, and `spec-flow`.

See [Dual-agent operating model](docs/dual-agent-operating-model.md) for
ownership boundaries, runtime mappings, installation, and pilot acceptance.

## Directory Structure

```
cc-marketplace/
├── MARKETPLACE.yaml          # Canonical AgentForge collection definition
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
│   └── marketplace/          # `marketplace` CLI: sync, validate, lint, export, check
├── export/                   # Public export config
│   └── public.json           # Allowlist + public ("jdh") marketplace identity
└── .github/workflows/        # CI/CD automation
    └── validate.yml          # GitHub Actions workflow
```

Each directory under `marketplaces/` is a complete marketplace root, so a
runtime is pointed at that directory rather than at the repository. Pointing a
runtime at the repository root is what previously let Codex resolve canonical
Claude sources instead of its own projection.

## Usage

> **Consuming vs. authoring.** Installing and using these plugins needs nothing
> but this repository — `marketplaces/` is compiled output and is committed, so
> every plugin is ready to install as-is. *Authoring* (the `sync` step below)
> additionally needs the AgentForge compiler, which is not yet public; until it
> is, regenerating `marketplaces/` is a maintainer-only step. Everything else —
> install, `validate`, `lint`, `pytest` — runs from a plain clone.

### Installing the Marketplace

Each runtime is pointed at its own compiled publication, never at the
repository root.

Claude Code:

```bash
git clone https://github.com/jdh313/cc-marketplace
/plugin marketplace add /path/to/cc-marketplace/marketplaces/claude
```

Codex local marketplace and pilots:

```bash
codex plugin marketplace add /path/to/cc-marketplace/marketplaces/codex
codex plugin add commit@cc-marketplace
codex plugin add craft@cc-marketplace
codex plugin add linear@cc-marketplace
codex plugin add spec-flow@cc-marketplace
```

Both publications keep the marketplace name `cc-marketplace`, so an existing
install survives the repoint: only the path each runtime resolves changes.

### Adding a New Plugin (maintainer-only)

Step 3 requires the AgentForge compiler, which is not yet publicly available.

1. Create plugin directory:
   ```bash
   mkdir -p plugins/my-plugin
   ```

2. Add plugin files and an authoritative `plugins/my-plugin/PACKAGE.yaml`. Declare
   only the runtimes whose native mappings have been validated.

3. Regenerate the committed native manifests with the pinned compiler:
   ```bash
   env AGENTFORGE_PROJECT=/path/to/agentforge-at-0ebebbb \
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
   export AGENTFORGE_PROJECT=/path/to/agentforge-at-0ebebbb
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
env AGENTFORGE_PROJECT=/path/to/agentforge-at-0ebebbb uv run marketplace sync
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
`policy.allow_implicit_invocation: false` skill sidecars. cc-marketplace's
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

### Export

Copies the allowlisted subset (`export/public.json`) to the public marketplace repo:

```bash
uv run marketplace export --dry-run        # then --commit --push for the real export
```

## CI/CD

GitHub Actions runs on every push and pull request:
- `uv run marketplace check` (Claude drift + Claude/Codex schemas + lint)
- `uv run pytest` with AgentForge pinned to commit `0ebebbb`
- deterministic full-corpus compilation and read-only drift checks
- `claude plugin validate --strict` for the generated Claude publication,
  using Claude Code `2.1.216`
- `uv run marketplace validate --format codex` for the generated Codex publication

Because AgentForge is private, the workflow requires an
`AGENTFORGE_DEPLOY_KEY` repository secret with read access to
`jdh313/agentforge`. The job fails explicitly if that credential is absent; it
does not skip the acceptance gate.

## Metadata ownership

`MARKETPLACE.yaml` and `plugins/*/PACKAGE.yaml` are the only maintained sources
of marketplace and package metadata, and `plugins/` is the only maintained
source of plugin content. Everything under `marketplaces/` is committed
compiler output — manifests and bodies alike. Edit the source and run
`uv run marketplace sync`; never hand-edit a file under `marketplaces/`, because
the next sync republishes the whole tree and silently discards the edit.

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
