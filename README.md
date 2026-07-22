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
│   └── marketplace.json      # Generated Claude registry
├── .agents/plugins/
│   └── marketplace.json      # Curated Codex pilot registry
├── plugins/                  # Plugin files
│   └── [plugin-name]/
│       ├── PACKAGE.yaml      # Canonical AgentForge package definition
│       ├── .claude-plugin/   # Claude-native manifest
│       ├── .codex-plugin/    # Codex-native manifest for accepted pilots
│       └── ...               # Canonical shared bodies + thin adapters
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
codex plugin marketplace add /path/to/cc-marketplace
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

2. Create `plugins/my-plugin/.claude-plugin/plugin.json`:
   ```json
   {
     "name": "my-plugin",
     "version": "1.0.0",
     "description": "Plugin description",
     "author": {
       "name": "Your Name",
       "email": "you@example.com"
     },
     "keywords": ["automation", "workflow"]
   }
   ```

3. Add plugin files and a canonical `plugins/my-plugin/PACKAGE.yaml`. Declare
   only the runtimes whose native mappings have been validated.

4. Sync marketplace:
   ```bash
   uv run marketplace sync
   ```

5. Validate everything (sync drift + both schemas + lint):
   ```bash
   uv run marketplace check
   ```

6. Validate and compile the canonical AgentForge collection in an isolated
   output root:
   ```bash
   agentforge compile MARKETPLACE.yaml --out /tmp/cc-marketplace-agentforge
   agentforge check MARKETPLACE.yaml --out /tmp/cc-marketplace-agentforge
   ```

See [`docs/agentforge-compatibility.md`](docs/agentforge-compatibility.md) for
the current target matrix, payload dispositions, and reviewed compatibility
limitations.

## Marketplace CLI

A single tool (`scripts/marketplace/`) drives the registry. Run via `uv run marketplace <command>`:

### Sync

Regenerates `marketplace.json` from the `plugins/` directory:

```bash
uv run marketplace sync          # use --check to fail on drift without writing
```

### Validate

Schema-validates a marketplace:

```bash
uv run marketplace validate                 # Claude
uv run marketplace validate --format codex  # Codex pilots
```

### Lint

Checks plugin files for correctness:

```bash
uv run marketplace lint
```

### Check (merge gate)

Runs Claude sync drift, both validators, and lint together — the CI entrypoint:

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
- `uv run pytest`

## Plugin Structure

### Minimal plugin.json

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "What the plugin does",
  "author": {
    "name": "Your Name"
  }
}
```

### Full plugin.json

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "What the plugin does",
  "author": {
    "name": "Your Name",
    "email": "you@example.com",
    "url": "https://github.com/yourusername"
  },
  "category": "productivity",
  "keywords": ["automation", "workflow"],
  "homepage": "https://your-plugin-site.com",
  "repository": "https://github.com/user/plugin"
}
```

## Categories

Suggested categories:
- productivity
- devops
- testing
- security
- ai-ml
- api-development
- database
- performance
- documentation
- custom

## License

Apache-2.0
