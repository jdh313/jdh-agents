---
name: review-prep
description: Automate code review preparation with PR description generation, commit cleanup, and diff analysis. Includes VCS auto-detection to work seamlessly in both git and jujutsu (jj) environments.
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Read
  - Glob
---

# Review Prep

## Overview

Automate code review preparation tasks including PR description generation, commit history cleanup, and intelligent diff analysis. This skill automatically detects your VCS and applies the appropriate commands for review preparation.

**Supports:** git and jj (Jujutsu)

**Explicit commands available:**
- `/review-prep:generate-pr` - Generate a PR description from commit history (coming soon)
- `/review-prep:cleanup-history` - Clean up and squash commits (git) or rebase changes (jj) (coming soon)
- `/review-prep:analyze-diff` - Analyze differences between branches (coming soon)

## When to Use This Skill

Use this skill when:
- Preparing code for review on GitHub, GitLab, or other platforms
- You need to clean up your commit history before creating a PR
- You want to understand what changed in your branch vs. main
- Creating comprehensive PR descriptions with proper context
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

- **Git detected**: Use `references/git-commands.md` for commit operations
- **Jujutsu detected**: Use `references/jj-commands.md` for change operations

References are stored at:
- `skills/review-prep/references/git-commands.md`
- `skills/review-prep/references/jj-commands.md`

### Example Detection Output

When you run a review-prep command, you'll see:

```
Detected VCS: git
Reference file: skills/review-prep/references/git-commands.md

Repository type: Git
You're working in a git repository. Review operations will use git commands.
```

Or if using Jujutsu:

```
Detected VCS: jj
Reference file: skills/review-prep/references/jj-commands.md

Repository type: Jujutsu
You're working in a jujutsu repository. Review operations will use jj commands.
```

## Commit vs Change Terminology

| Concept | Git Term | Jujutsu Term | Purpose |
|---------|----------|--------------|---------|
| Committed Work | Commit | Change | Record of work completed |
| Reorganize Work | `git rebase -i` | `jj rebase` | Reorder and clean history |
| Update Message | `git commit --amend` | `jj describe -m` | Change commit description |
| Combine Work | `git squash` | `jj squash` | Merge multiple units into one |
| View History | `git log` | `jj log` | See all committed work |

## Core Principles

### Dual VCS Support

The same plugin works in both git and jj repositories because:
1. **Detection happens at runtime** - Commands determine which VCS to use
2. **VCS-specific references** - Each operation loads the right command for the detected VCS
3. **Consistent workflows** - Git commit operations map cleanly to jj change operations
4. **No manual configuration** - The plugin "just works" without setup

### Safe Operations

All review preparation operations follow these safety principles:

- **Confirmation before changes** - Always show what will be changed
- **Uncommitted changes warning** - Alert user if there are unsaved changes
- **No interactive mode** - All commands use non-interactive flags by default
- **Clear feedback** - Show before/after state for all operations

## Workflow Examples

### Example 1: Generate a PR Description

1. Run a review-prep command to confirm your VCS and branch
2. Analyze commits/changes since main
3. Generate a structured PR description with:
   - Summary of changes
   - Files modified
   - Impact assessment
   - Testing recommendations

```bash
# Git: Analyzes commits between HEAD and main
$ git log main..HEAD

# Jujutsu: Analyzes changes from parent to current
$ jj log -r main..
```

### Example 2: Clean Up Your Commit History

1. Run `/review-prep:cleanup-history` to start interactive session
2. Review commits that will be organized
3. For git: Interactive rebase to squash and reorder
4. For jj: Rebase changes for logical grouping

```bash
# Git
$ git rebase -i main

# Jujutsu
$ jj rebase -r <change-range> --onto main
```

### Example 3: Analyze Your Diff

1. Run `/review-prep:analyze-diff` to compare with main
2. See detailed breakdown of:
   - Files changed
   - Lines added/removed
   - Modified functions/classes
   - Potential impacts
3. Identify test coverage needs

## Reference Materials

Load these references as needed:

- `references/git-commands.md` - Git-specific commands for commit operations
- `references/jj-commands.md` - Jujutsu-specific commands for change operations
