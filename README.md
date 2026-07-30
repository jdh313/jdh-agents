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
├── MARKETPLACE.yaml              # Canonical AgentForge collection definition
├── .claude-plugin/
│   └── marketplace.json      # Generated, committed Claude registry
├── .agents/plugins/
│   └── marketplace.json      # Generated, committed Codex pilot registry
├── plugins/                  # Plugin files
│   └── [plugin-name]/
│       ├── PACKAGE.yaml      # Canonical AgentForge package definition
│       ├── .claude-plugin/   # Generated Claude-native manifest
│       ├── .codex-plugin/    # Generated Codex-native manifest for pilots
│       └── ...               # Plugin files (commands, agents, skills, etc.)
├── scripts/                  # Automation tooling
│   └── marketplace/          # `marketplace` CLI: sync, validate, lint, export, check
├── export/                   # Public export config
│   └── public.json           # Allowlist + public ("jdh") marketplace identity
└── .github/workflows/        # CI/CD automation
    └── validate.yml          # GitHub Actions workflow
```

## Usage

### Installing the Marketplace

Claude Code:

```text
/plugin marketplace add jdh313/cc-marketplace
```

Codex local marketplace and pilots:

```bash
codex plugin marketplace add /Users/jacob/Projects/cc-marketplace
codex plugin add commit@cc-marketplace
codex plugin add craft@cc-marketplace
codex plugin add linear@cc-marketplace
codex plugin add spec-flow@cc-marketplace
```

### Adding a New Plugin

1. Create plugin directory:
   ```bash
   mkdir -p plugins/my-plugin
   ```

2. Add plugin files and an authoritative `plugins/my-plugin/PACKAGE.yaml`. Declare
   only the runtimes whose native mappings have been validated.

3. Regenerate the committed native manifests with the pinned compiler:
   ```bash
   env AGENTFORGE_PROJECT=/path/to/agentforge-at-14dbb35 \
     uv run marketplace sync
   ```

4. Validate repository-native files (read-only drift + schema + lint):
   ```bash
   uv run marketplace check
   ```

5. Run the full-corpus acceptance suite against the pinned compatible
   AgentForge checkout and compile into an isolated output root:
   ```bash
   export AGENTFORGE_PROJECT=/path/to/agentforge-at-14dbb35
   uv run pytest -q
   agentforge compile MARKETPLACE.yaml --out /tmp/cc-marketplace-agentforge
   agentforge check MARKETPLACE.yaml --out /tmp/cc-marketplace-agentforge --claude-native
   uv run marketplace validate \
     --format codex \
     --manifest /tmp/cc-marketplace-agentforge/codex/.agents/plugins/marketplace.json \
     --plugins-root /tmp/cc-marketplace-agentforge/codex/plugins
   ```

See [`docs/agentforge-compatibility.md`](docs/agentforge-compatibility.md) for
the current target matrix, payload dispositions, and reviewed compatibility
limitations.

## Marketplace CLI

A single tool (`scripts/marketplace/`) drives the registry. Run via `uv run marketplace <command>`:

### Sync

Compiles `MARKETPLACE.yaml` with AgentForge and materializes only the two root
marketplace manifests, all 15 Claude package manifests, and the five declared
Codex pilot manifests. It never replaces maintained skills, agents, commands,
hooks, references, or other source content.

```bash
env AGENTFORGE_PROJECT=/path/to/agentforge-at-14dbb35 uv run marketplace sync
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
- `uv run pytest` with AgentForge pinned to commit `14dbb35`
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
of marketplace and package metadata. The JSON files under `.claude-plugin/`,
`.agents/plugins/`, and package `.claude-plugin/` / `.codex-plugin/`
directories are committed generated outputs. Edit the YAML and regenerate;
never hand-edit those JSON manifests.

## License

Apache-2.0
