---
name: branch-workflow
description: Automate branch/change creation, switching, and cleanup for git and jj repositories. Includes VCS auto-detection to work seamlessly in both git and jujutsu (jj) environments.
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Read
  - Glob
---

# Branch Workflow

## Overview

Automate branch/change management operations for both git and jj (Jujutsu) repositories. This skill automatically detects your VCS and applies the appropriate commands for branch creation, switching, and cleanup.

**Supports:** git and jj (Jujutsu)

**Explicit commands available:**
- `/branch-workflow:detect-vcs` - Detect and display which VCS is in use
- `/branch-workflow:create-branch` - Create a new branch or change (coming soon)
- `/branch-workflow:switch-branch` - Switch between branches/changes (coming soon)
- `/branch-workflow:cleanup-branches` - Clean up old branches/changes (coming soon)

## When to Use This Skill

Use this skill when:
- Creating new branches for feature work (git) or changes (jj)
- Switching between different branches/changes
- Cleaning up old, merged, or abandoned branches/changes
- Working in projects that use different VCS systems
- You want VCS detection to happen automatically

## VCS Detection

This skill automatically detects whether you're in a git or jj repository at runtime.

### Detection Logic

```bash
[[ -d .jj ]] && echo "jj" || echo "git"
```

**How it works:**
- Checks for the `.jj` directory (Jujutsu metadata)
- If `.jj` exists: Jujutsu is in use
- If `.jj` does not exist: Git is in use (or git is the default fallback)

**Speed:** Detection is instant (no command execution, just filesystem check)

### Loading VCS References

After detection, load the appropriate command reference:

- **Git detected**: Use `references/git-commands.md` for branch operations
- **Jujutsu detected**: Use `references/jj-commands.md` for change operations

References are stored at:
- `skills/branch-workflow/references/git-commands.md`
- `skills/branch-workflow/references/jj-commands.md`

### Example Detection Output

When you run `/branch-workflow:detect-vcs`, you'll see:

```
Detected VCS: git
Reference file: skills/branch-workflow/references/git-commands.md

Repository type: Git
You're working in a git repository. Branch operations will use git commands.
```

Or if using Jujutsu:

```
Detected VCS: jj
Reference file: skills/branch-workflow/references/jj-commands.md

Repository type: Jujutsu
You're working in a jujutsu repository. Change operations will use jj commands.
```

## Branch vs Change Terminology

| Concept | Git Term | Jujutsu Term | Purpose |
|---------|----------|--------------|---------|
| Active Work Unit | Branch | Change | Isolate work in progress |
| List Units | `git branch` | `jj log` | See all available units |
| Create Unit | `git checkout -b <name>` | `jj new -m "<name>"` | Start new work |
| Switch Unit | `git checkout <name>` | `jj edit <change-id>` | Move to different unit |
| Delete Unit | `git branch -d <name>` | `jj abandon <change-id>` | Remove completed/old unit |

## Core Principles

### Dual VCS Support

The same plugin works in both git and jj repositories because:
1. **Detection happens at runtime** - Commands determine which VCS to use
2. **VCS-specific references** - Each operation loads the right command for the detected VCS
3. **Consistent workflows** - Git branch operations map cleanly to jj change operations
4. **No manual configuration** - The plugin "just works" without setup

### Safe Operations

All branch/change operations follow these safety principles:

- **Confirmation before deletion** - Always show what will be deleted
- **Uncommitted changes warning** - Alert user if there are unsaved changes
- **No interactive mode** - All commands use non-interactive flags (--no-edit, -m, etc.)
- **Clear feedback** - Show before/after state for all operations

## Workflow Examples

### Example 1: Create a New Branch/Change

1. Run `/branch-workflow:detect-vcs` to confirm your VCS
2. Run `/branch-workflow:create-branch` and enter a name
3. For git: Creates and checks out a new branch
4. For jj: Creates a new change with the description

```bash
# Git
$ git checkout -b feature/new-auth

# Jujutsu
$ jj new -m "feature/new-auth"
```

### Example 2: Switch Branches/Changes

1. Run `/branch-workflow:switch-branch` to list available branches/changes
2. Select the target from the list
3. For git: Checks out the branch (warns if uncommitted changes)
4. For jj: Edits the change (preserves current working copy state)

### Example 3: Clean Up Old Branches/Changes

1. Run `/branch-workflow:cleanup-branches` to list candidates
2. Select multiple branches/changes for deletion
3. Confirm the deletion
4. For git: Deletes using `git branch -d` (or -D for unmerged)
5. For jj: Abandons using `jj abandon`

## Reference Materials

Load these references as needed:

- `references/git-commands.md` - Git-specific commands for branch operations
- `references/jj-commands.md` - Jujutsu-specific commands for change operations
