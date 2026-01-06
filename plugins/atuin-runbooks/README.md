# Atuin Runbooks Plugin

Create and modify [Atuin Desktop](https://atuin.sh) runbooks (`.atrb` files) from natural language.

## Features

- **Create runbooks** - Generate complete `.atrb` files from descriptions
- **Add blocks** - Append new blocks to existing runbooks
- **Auto-detect workspace** - Finds your Atuin workspace automatically

## Usage

Simply describe what runbook you want:

```
Create a runbook for deploying my Node.js app
```

Or add to existing:

```
Add a terminal block to run tests in my Deploy runbook
```

## What are Atuin Runbooks?

Atuin Desktop provides "runbooks that run" - executable documentation combining:

- Rich text (headings, paragraphs, lists)
- Interactive terminal blocks
- Scripts with output capture
- Environment and directory configuration
- Template variables

Learn more at [Atuin Desktop Docs](https://docs.atuin.sh/desktop/).

## Block Types Supported

| Category | Types |
|----------|-------|
| Text | heading, paragraph, bulletListItem, numberedListItem, quote |
| Executable | run (terminal), script |
| Context | directory, local-directory, env, var |
| Display | var_display |
| Interactive | dropdown, editor |

See `skills/runbook-builder/references/block-types.md` for complete schemas.

## Requirements

- Atuin Desktop installed
- Workspace with `atuin.toml` (typically in `~/Documents/Atuin Runbooks`)
