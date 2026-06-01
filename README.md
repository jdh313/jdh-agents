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
├── scripts/                  # Automation scripts
│   ├── validate_schema.py    # Schema validator
│   ├── lint_plugins.py       # Plugin linter
│   └── sync_marketplace.py   # Auto-sync marketplace.json
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
   python scripts/sync_marketplace.py
   ```

5. Validate:
   ```bash
   python scripts/validate_schema.py
   python scripts/lint_plugins.py
   ```

## Automation Scripts

### Schema Validation

Validates `marketplace.json` structure:

```bash
python scripts/validate_schema.py
```

### Plugin Linting

Checks plugin files for correctness:

```bash
python scripts/lint_plugins.py
```

### Auto-Sync

Automatically updates `marketplace.json` from `plugins/` directory:

```bash
python scripts/sync_marketplace.py
```

## CI/CD

GitHub Actions automatically:
- Validates marketplace schema
- Lints all plugin files
- Checks marketplace.json is in sync

Runs on every push and pull request.

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
