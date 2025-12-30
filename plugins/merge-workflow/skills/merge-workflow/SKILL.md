---
name: merge-workflow
description: Automate merge, rebase, and conflict resolution for git and jj repositories with VCS auto-detection
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Read
  - Edit
  - AskUserQuestion
---

# Merge Workflow Skill

Automate branch and change merge operations for git and jj with conflict detection, resolution guidance, and VCS auto-detection. This skill handles rebase operations, conflict detection, and guided conflict resolution for both git and Jujutsu repositories.

**Supports:** git and jj (Jujutsu)

**Explicit commands available:**
- `/merge-workflow:rebase` - Rebase current branch/change onto main
- `/merge-workflow:detect-conflicts` - Detect and categorize conflicts
- `/merge-workflow:resolve-conflicts` - Guided conflict resolution workflow
- `/merge-workflow:abort` - Abort merge/rebase operation (coming soon)

## When to Use This Skill

Use this skill when:
- You need to rebase your branch onto the latest main branch
- You want to detect and understand conflicts in your repository
- You're resolving merge or rebase conflicts and need guided help
- You want merge operations that work seamlessly in both git and jj
- You need to understand conflict types and resolution strategies
- You're preparing a branch for code review

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

### Example Detection Output

When you run a merge-workflow command, you'll see:

```
Detected VCS: git
Repository type: Git
You're working in a git repository. Merge operations will use git commands.
```

Or if using Jujutsu:

```
Detected VCS: jj
Repository type: Jujutsu
You're working in a jujutsu repository. Merge operations will use jj commands.
```

## Merge vs Rebase Terminology

| Concept | Git Term | Jujutsu Term | Purpose |
|---------|----------|--------------|---------|
| Incorporate Changes | Merge/Rebase | Rebase | Update your work with latest main |
| Replay Commits | `git rebase` | `jj rebase` | Reapply your commits on new base |
| Resolve Conflicts | `git status`, `git add`, `git rebase --continue` | `jj resolve`, `jj describe` | Handle code changes from both sides |
| Abort Operation | `git rebase --abort` | `jj undo` | Cancel merge/rebase if needed |
| View History | `git log` | `jj log` | See all commits/changes |

## Available Commands

### Rebase Command
Rebase your current branch (git) or change (jj) onto main/master.

**Usage:**
```
/merge-workflow:rebase
```

**What it does:**
1. Detects your VCS (git or jj)
2. Verifies working directory is clean (git only)
3. Fetches latest remote changes (git only)
4. Executes rebase with appropriate flags
5. Detects and reports any conflicts
6. Shows updated commit graph/change history

**When to use:**
- Your branch is behind the main branch
- You want to incorporate latest changes before code review
- You need a clean linear history without merge commits

### Detect Conflicts Command
Detect and categorize all conflicts in the current repository.

**Usage:**
```
/merge-workflow:detect-conflicts
```

**What it does:**
1. Scans for conflicted files in git or jj
2. Categorizes conflicts by type (content, add/add, delete)
3. Counts total conflicts per file
4. Generates comprehensive summary report
5. Offers resolution assistance options

**When to use:**
- After a rebase/merge that resulted in conflicts
- You want a clear overview of all conflicts
- You need to understand conflict types before resolving

**Conflict Types:**
- **Content conflicts**: Same file modified on both sides with different changes
- **Add/Add conflicts**: File added on both sides with different content
- **Delete conflicts**: One side modified, other side deleted the file

### Resolve Conflicts Command
Guided conflict resolution workflow that walks through conflicts one file at a time.

**Usage:**
```
/merge-workflow:resolve-conflicts
```

**What it does:**
1. Detects VCS and lists all conflicted files
2. Presents each conflict with full context
3. Offers resolution strategies (accept ours, accept theirs, manual edit, skip)
4. Handles manual editing with Read/Edit tools
5. Verifies all conflicts are resolved
6. Completes the merge/rebase operation

**When to use:**
- You have conflicts to resolve after rebase/merge
- You want step-by-step guidance through resolution
- You need to see context before deciding on each conflict
- You prefer manual control over automatic resolution

**Resolution Options:**
- **(a) Accept OURS** - Keep current branch/change version
- **(b) Accept THEIRS** - Take incoming branch/change version
- **(c) Edit manually** - Use Read/Edit tools to merge both versions
- **(d) Show full file** - See entire file with all conflicts
- **(s) Skip this file** - Resolve later, move to next file
- **(q) Quit** - Exit workflow, can resume later

## Core Principles

### Dual VCS Support

The same skill works in both git and jj repositories because:
1. **Detection happens at runtime** - Commands determine which VCS to use
2. **VCS-specific operations** - Each operation uses the right command for the detected VCS
3. **Consistent workflows** - Git rebase operations map cleanly to jj rebase operations
4. **No manual configuration** - The skill "just works" without setup

### Safe Operations

All merge workflow operations follow these safety principles:

- **Confirmation before changes** - Always show what will be changed
- **Uncommitted changes warning** - Alert user if there are unsaved changes (git)
- **No destructive defaults** - Operations require explicit confirmation
- **Clear feedback** - Show before/after state for all operations
- **Reversible actions** - All operations can be aborted or undone

### Partial Resolution Support

The resolve-conflicts command supports partial resolution:
- Files can be skipped with option (s)
- Workflow can be quit with option (q)
- Resume by running command again
- Resolved files are marked immediately (git: staged, jj: tracked)

## Workflow Examples

### Example 1: Simple Rebase

1. Run `/merge-workflow:rebase`
2. VCS is detected automatically
3. Latest main is fetched (git) or used (jj)
4. Your changes are replayed on latest main
5. If successful, your branch is updated
6. If conflicts occur, resolve-conflicts guidance is shown

### Example 2: Conflict Detection and Analysis

1. Run `/merge-workflow:detect-conflicts`
2. Get comprehensive report of all conflicts
3. See breakdown by conflict type
4. Review which files are affected
5. Plan resolution strategy based on conflict types

### Example 3: Guided Conflict Resolution

1. Run `/merge-workflow:resolve-conflicts`
2. Review first conflicted file with context
3. Choose resolution strategy (accept ours, accept theirs, manual, etc.)
4. Continue through all conflicted files
5. Skip difficult ones to resolve easier files first
6. Use manual edit option for complex merges
7. Verify all conflicts resolved
8. Merge/rebase completes automatically

## Key Differences: Git vs Jujutsu

| Aspect | Git | Jujutsu |
|--------|-----|---------|
| Working Directory | Must be clean before rebase | Auto-tracks all changes |
| Fetch Required | Yes, must fetch before rebase | No, jj tracks locally |
| Conflict Blocking | Blocks commit until resolved | Doesn't block normal work |
| Interactive Mode | Supported | Not supported in this skill |
| Staging | Must stage after resolve | Auto-tracked |
| Undo Mechanism | `git rebase --abort` | `jj undo` |

## Safety Considerations

### When NOT to Use Rebase

- On already-pushed branches without team coordination
- On main, master, or other protected branches
- When you have uncommitted work (git)
- If you're not sure what rebase does

### Best Practices

1. **Commit your work first**: For git, ensure all changes are committed
2. **Rebase frequently**: Don't let your branch drift too far from main
3. **Test after rebase**: Run tests to ensure no broken functionality
4. **Review history**: Check updated commits before pushing
5. **Handle conflicts promptly**: Don't delay conflict resolution

## Error Handling

The commands handle these common scenarios:

- **Not a git/jj repository**: Shows error and exits
- **Uncommitted changes (git)**: Warns user to commit or stash first
- **Network errors (git)**: Shows fetch error with remediation
- **Rebase conflicts**: Lists conflicted files and provides resolution guidance
- **Rebase failure**: Shows error and suggests undo/abort options
- **No conflicts detected**: Reports clean state and exits gracefully

## Reference Materials

Load these references as needed for detailed command information:

- **Git-specific operations**: Git commands for rebase, merge, conflict resolution
- **Jujutsu-specific operations**: Jj commands for rebase, change operations, conflict handling
- **Conflict markers format**: Understanding `<<<<<<<`, `=======`, `>>>>>>>` markers
- **VCS auto-detection**: How the skill detects git vs jj at runtime

## Integration with Other Commands

**Related plugins/skills:**
- `/branch-workflow:create-branch` - Create new branches/changes
- `/branch-workflow:switch-branch` - Switch between branches/changes
- `/branch-workflow:cleanup-branches` - Clean up old branches
- `/review-prep:cleanup-history` - Clean up commit history before review

**Typical workflow sequence:**
1. Create branch with `/branch-workflow:create-branch`
2. Make changes and commit
3. Rebase with `/merge-workflow:rebase`
4. If conflicts, resolve with `/merge-workflow:resolve-conflicts`
5. Push and create PR

## Limitations

- Interactive rebase not supported (use `/review-prep:cleanup-history` for commit editing)
- Merge commits not created (rebase is used instead)
- For git, `--no-edit` means commit messages are preserved as-is
- Partial merges not supported (must rebase entire branch)

## Future Enhancements

- Support for merge commits (alternative to rebase)
- Interactive rebase support for commit reordering
- Auto-resolution of simple conflicts
- Integration with CI/CD for pre-rebase validation
- Multiple main branch detection (main, master, develop)
