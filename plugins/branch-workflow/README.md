# Branch Workflow Plugin

Automate branch/change management operations for both git and jj repositories.

## Features

- **VCS Auto-Detection**: Automatically detects whether you're in a git or jj (Jujutsu) repository
- **Branch/Change Creation**: Create new branches (git) or changes (jj) with proper naming
- **Branch/Change Switching**: Switch between branches/changes with safety checks
- **Branch/Change Cleanup**: Clean up old, merged, or abandoned branches/changes
- **Dual VCS Support**: Same plugin works in both git and jj repositories without configuration

## Commands

- **`/branch-workflow:detect-vcs`** - Detect and display which VCS is in use
- **`/branch-workflow:create-branch`** - Create a new branch or change (coming soon)
- **`/branch-workflow:switch-branch`** - Switch between branches/changes (coming soon)
- **`/branch-workflow:cleanup-branches`** - Clean up old branches/changes (coming soon)

## Quick Start

### Detect Your VCS

Run this first to verify which system you're using:

```
/branch-workflow:detect-vcs
```

This will tell you if you're in a git or jj repository and confirm the appropriate commands will be used.

## VCS Detection

This plugin uses a fast directory check to detect the VCS:

```bash
[[ -d .jj ]] && echo "jj" || echo "git"
```

- **Jujutsu**: Detects the `.jj/` directory (Jujutsu's metadata folder)
- **Git**: Default to git if `.jj` is not present

No command execution is required, making detection instant.

## Architecture

### Directory Structure

```
branch-workflow/
├── .claude-plugin/
│   └── plugin.json          # Plugin metadata
├── commands/
│   └── detect-vcs.md        # VCS detection command
├── skills/branch-workflow/
│   ├── SKILL.md            # Skill documentation
│   └── references/
│       ├── git-commands.md   # Git command reference
│       └── jj-commands.md    # Jujutsu command reference
└── README.md
```

### How VCS Detection Works

1. **Runtime Detection**: Each command runs `[[ -d .jj ]] && echo "jj" || echo "git"` to detect the VCS
2. **Load Reference**: Based on detection, loads the appropriate command reference file
3. **Execute Commands**: Uses VCS-specific commands for all operations

This approach ensures:
- No configuration needed
- Works in both git and jj repositories
- Automatic fallback to git if neither system is detected
- Fast execution (no subprocesses)

## Terminology

| Git | Jujutsu | Concept |
|-----|---------|---------|
| Branch | Change | A unit of isolated work |
| `git checkout -b` | `jj new -m` | Create a new unit |
| `git checkout` | `jj edit` | Switch to a unit |
| `git branch -d` | `jj abandon` | Remove a unit |

## Safety Features

All operations include safety checks:

- **Confirmation before deletion** - Always show what will be deleted
- **Uncommitted changes warning** - Alert user if there are unsaved changes
- **Non-interactive commands** - Uses `--no-edit`, `-m` flags to prevent prompts
- **Clear feedback** - Shows before/after state for all operations

## Future Commands

This plugin is part of Phase 1 of the VCS Tools project. Planned commands:

- Branch/change creation with validation
- Intelligent switching with safety warnings
- Batch cleanup with multi-select
- Change/branch filtering and search

## Related Plugins

- **atomic-commits**: Create atomic commits with conventional messages (also supports both git and jj)

## Author

Jacob Hoehler
