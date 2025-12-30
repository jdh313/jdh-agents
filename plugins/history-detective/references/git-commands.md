# Git Commands Reference

Shared git command patterns for branch operations used across VCS plugins.

## Branch Operations

### Create and Switch Branch

```bash
# Create and immediately switch to a new branch
git checkout -b <branch-name>
```

**Non-interactive:** `git checkout -b` automatically switches to the new branch.

### List Branches

```bash
# List all local branches
git branch

# List all branches (local + remote)
git branch -a

# List remote branches only
git branch -r
```

### Switch to Existing Branch

```bash
# Switch to an existing branch
git checkout <branch-name>
```

**Non-interactive:** Use branch name directly. No prompts required.

### Delete Branch

#### Safe Delete (Merged Only)

```bash
# Delete a branch only if it's fully merged
git branch -d <branch-name>
```

**Behavior:** Returns error if branch has unmerged changes. Safe for automation.

#### Force Delete (Unmerged)

```bash
# Force delete a branch regardless of merge status
git branch -D <branch-name>
```

**Caution:** Use only when certain the branch should be deleted.

### Check Branch Merge Status

```bash
# List branches merged into current branch
git branch --merged

# List branches NOT merged into current branch
git branch --no-merged
```

## Branch Cleanup Patterns

### List Mergeable Branches (Safe for Cleanup)

```bash
# Show all branches merged into HEAD (can be safely deleted)
git branch --merged

# Filter to exclude protected branches
git branch --merged | grep -v "main\|master\|develop"
```

### List Old Branches

```bash
# Show branches with last commit older than 2 weeks
git branch -v | grep "ago"

# More detailed: show last commit date
git for-each-ref --sort='-committerdate:iso8601' --format=' %(committerdate:iso8601) %(refname:short)' refs/heads
```

### Batch Delete Merged Branches

```bash
# Delete all branches merged into current branch (except main/master)
git branch --merged | grep -v "main\|master" | xargs -r git branch -d

# Dry run: see what would be deleted without deleting
git branch --merged | grep -v "main\|master"
```

## Branch Information

### Get Current Branch

```bash
# Show current branch name
git branch --show-current
```

### Get Branch Details

```bash
# Show commit details for each branch
git branch -v

# Show remote tracking info
git branch -vv

# Show full commit hash and author
git for-each-ref --sort='-committerdate' --format='%(refname:short) %(objectname:short) %(committerdate:short) %(subject)' refs/heads
```

## Non-Interactive Patterns

**Key patterns to prevent interactive prompts:**

- **Create branch:** `git checkout -b <name>` (no prompts, creates and switches automatically)
- **Switch branch:** `git checkout <name>` (no prompts, direct switch)
- **Delete branch:** `git branch -d <name>` or `git branch -D <name>` (no prompts when flags used)
- **List branches:** `git branch`, `git branch -a`, `git branch --merged` (read-only, no prompts)

**Avoid these interactive patterns:**

- `git checkout` (without -b flag or branch name) - prompts for selection
- Interactive rebase: `git rebase -i` - opens editor
- Interactive add: `git add -i` - opens interactive mode
- Interactive stash: `git stash -i` - opens interactive mode

## Safety Considerations

### Prevent Accidental Deletions

```bash
# Always check merged status before deleting
git branch --merged | grep <target-branch>

# List what will be deleted (dry run)
git branch --merged | grep -v "main\|master\|develop"

# Delete specific branch only after verification
git branch -d <specific-branch>
```

### Verify Current Branch Before Operations

```bash
# Always verify current context
git branch --show-current

# Check if working directory is clean
git status
```

### Restore Deleted Branch

```bash
# If you accidentally deleted a branch, find it in reflog
git reflog

# Recreate from reflog entry
git checkout -b <branch-name> <reflog-hash>
```

## Best Practices

1. **Always verify before delete:** Use `git branch --merged` to confirm merge status
2. **Protect main branches:** When scripting cleanup, explicitly exclude main, master, develop
3. **Check current branch:** Before switching or deleting, confirm with `git branch --show-current`
4. **Use descriptive names:** Branch names in kebab-case are recommended (feature/user-auth, bugfix/memory-leak)
5. **Batch operations carefully:** When using xargs for bulk operations, dry-run first
6. **Keep branches organized:** Regularly cleanup merged branches to reduce clutter
