# Merge Workflow Plugin

Automate branch and change merge operations for git and jj with conflict detection, resolution guidance, and VCS auto-detection.

## Features

- **VCS Auto-Detection**: Automatically detects git or jj repositories
- **Rebase Operations**: Non-interactive rebase with automatic conflict detection
- **Conflict Resolution**: Clear guidance when conflicts occur during rebase
- **Safety Checks**: Pre-rebase validation to prevent data loss
- **Clear Feedback**: Visual confirmation of updated commit/change history

## Commands

### Rebase

Rebase your current branch (git) or change (jj) onto main/master.

**Usage:**
```
/merge-workflow:rebase
```

**What it does:**
1. Detects your VCS (git or jj)
2. Verifies working directory is clean (git only)
3. Fetches latest remote changes (git only)
4. Executes rebase with `git rebase origin/main --no-edit` or `jj rebase -d main`
5. Detects and reports any conflicts
6. Shows updated commit graph/change history

**When to use:**
- Your branch is behind the main branch and needs to incorporate latest changes
- You want to keep your commits on top of latest main before code review
- You need a clean linear history without merge commits

**Example:**
```bash
# Check current branch status
git status

# Run rebase command
/merge-workflow:rebase

# If successful, your branch is now rebased on latest main
# If conflicts occur, follow the guidance to resolve them
```

## Supported VCS

- **Git**: Tested with git 2.30+
- **Jujutsu**: Tested with jj 0.10+

## VCS-Specific Behavior

### Git

- Requires clean working directory before rebase
- Fetches latest remote changes first
- Uses non-interactive rebase (`--no-edit` flag)
- Detects conflicts by checking `git status` for rebase state
- Shows conflicts using `git status --short`

### Jujutsu

- Automatically tracks all changes (no staging required)
- Rebases using `jj rebase -d main`
- Can create conflicts but doesn't block the operation
- Changes are immutable, rebase creates new change IDs

## Conflict Resolution

When conflicts occur during rebase:

1. **For git:**
   - Edit conflicted files to resolve markers
   - Stage changes with `git add`
   - Continue rebase with `git rebase --continue`
   - Abort with `git rebase --abort` if needed

2. **For jj:**
   - Edit conflicted files to resolve markers
   - Changes are auto-tracked by jj
   - No additional steps needed

Detailed guidance is shown by the rebase command when conflicts are detected.

## Related Commands

- **Create Branch/Change**: `/branch-workflow:create-branch`
- **Switch Branch**: `/branch-workflow:switch-branch`
- **Cleanup Branches**: `/branch-workflow:cleanup-branches`
- **Clean History**: `/review-prep:cleanup-history`

## Error Handling

The command handles these common scenarios:

- **Not a git/jj repository**: Shows error and exits
- **Uncommitted changes (git)**: Warns user to commit or stash first
- **Network errors (git)**: Shows fetch error with remediation
- **Rebase conflicts**: Lists conflicted files and provides resolution guidance
- **Rebase failure**: Shows error and suggests undo/abort options

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

## Requirements

- **Git**: Version 2.30 or later
- **Jujutsu**: Version 0.10 or later
- Clean working directory (git only)
- Network access to fetch remote changes (git only)

## Limitations

- Interactive rebase not supported (use `/review-prep:cleanup-history` for commit editing)
- Merge commits not created (rebase is used instead)
- For git, `--no-edit` means commit messages are preserved as-is

## Future Enhancements

- Resolve-conflicts command for guided conflict resolution
- Interactive rebase support for commit reordering
- Auto-resolution of simple conflicts
- Integration with CI/CD for pre-rebase validation
