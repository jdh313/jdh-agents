# cc-marketplace

Personal Claude Code plugin marketplace with automated validation and synchronization.

## Directory Structure

```
cc-marketplace/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace metadata and plugin index
├── plugins/                  # Plugin files
│   └── [plugin-name]/
│       ├── plugin.json       # Plugin metadata
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

Add this marketplace to Claude Code:

```bash
/plugin marketplace add <your-github-username>/cc-marketplace
```

### Adding a New Plugin

1. Create plugin directory:
   ```bash
   mkdir -p plugins/my-plugin
   ```

2. Create `plugins/my-plugin/plugin.json`:
   ```json
   {
     "name": "my-plugin",
     "version": "1.0.0",
     "description": "Plugin description",
     "author": {
       "name": "Your Name",
       "email": "you@example.com"
     },
     "category": "productivity",
     "keywords": ["automation", "workflow"]
   }
   ```

3. Add plugin files (commands, agents, skills, etc.)

4. Sync marketplace:
   ```bash
   uv run marketplace sync
   ```

5. Validate everything (sync drift + schema + lint):
   ```bash
   uv run marketplace check
   ```

## Marketplace CLI

A single tool (`scripts/marketplace/`) drives the registry. Run via `uv run marketplace <command>`:

### Sync

Regenerates `marketplace.json` from the `plugins/` directory:

```bash
uv run marketplace sync          # use --check to fail on drift without writing
```

### Validate

Schema-validates `marketplace.json`:

```bash
uv run marketplace validate
```

### Lint

Checks plugin files for correctness:

```bash
uv run marketplace lint
```

### Check (merge gate)

Runs sync-drift + validate + lint together — the CI entrypoint:

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
- `uv run marketplace check` (sync drift + schema + lint)
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
