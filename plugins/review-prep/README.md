# Review Prep Plugin

Automate code review preparation with PR description generation, commit history cleanup, and intelligent diff analysis.

## Features

- **VCS Auto-Detection**: Automatically detects whether you're in a git or jj (Jujutsu) repository
- **PR Description Generation**: Analyze commits and generate comprehensive PR descriptions
- **Commit History Cleanup**: Squash and reorder commits (git) or rebase changes (jj) for clean history
- **Diff Analysis**: Examine changes between branches to identify impact and test requirements
- **Dual VCS Support**: Same plugin works in both git and jj repositories without configuration

## Commands

- **`/review-prep:generate-pr`** - Generate a PR description from commit history (coming soon)
- **`/review-prep:cleanup-history`** - Clean up and squash commits (git) or rebase changes (jj) (coming soon)
- **`/review-prep:analyze-diff`** - Analyze differences between branches (coming soon)

## Quick Start

### Generate a PR Description

Run this to create a comprehensive PR description based on your commits:

```
/review-prep:generate-pr
```

This will analyze your commit history (git) or change descriptions (jj) and generate a structured PR description.

### Clean Up Your History

Prepare your commits for review by squashing and reorganizing:

```
/review-prep:cleanup-history
```

For git: Interactive rebase to squash, reorder, and edit commits
For jj: Rebase changes for a clean history

### Analyze Your Diff

Understand what changed between your branch and main:

```
/review-prep:analyze-diff
```

Shows a detailed analysis of added, removed, and modified code.

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
review-prep/
├── .claude-plugin/
│   └── plugin.json              # Plugin metadata
├── commands/                    # Commands directory (placeholder)
├── skills/review-prep/
│   ├── SKILL.md                # Skill documentation
│   └── references -> ../../shared-references
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
| Commit | Change | A unit of committed work |
| `git rebase -i` | `jj rebase` | Reorganize work units |
| `git commit --amend` | `jj describe -m` | Update commit message |
| `git squash` | `jj squash` | Combine work units |

## Safety Features

All operations include safety checks:

- **Confirmation before changes** - Always show what will be changed
- **Uncommitted changes warning** - Alert user if there are unsaved changes
- **Non-interactive defaults** - Uses non-interactive flags to prevent unexpected prompts
- **Clear feedback** - Shows before/after state for all operations

## Future Commands

This plugin is part of Phase 2 of the VCS Tools project. Planned commands:

- PR description generation with configurable templates
- Intelligent commit squashing with message aggregation
- Diff analysis with impact detection
- Automated changelog generation

## Related Plugins

- **branch-workflow**: Create and manage branches/changes (Phase 1)
- **atomic-commits**: Create atomic commits with conventional messages (also supports both git and jj)

## Author

Jacob Waites
