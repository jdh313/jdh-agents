# Git Workflow Reference

This reference provides git-specific commands for the atomic commits workflow.

## Checking Current State

```bash
# View all changes (staged and unstaged)
git status

# View unstaged changes
git diff

# View staged changes
git diff --staged

# View recent commit history
git log --oneline -10
```

## Staging Changes

### Stage Specific Files

```bash
# Stage individual files
git add <file1> <file2> <file3>

# Stage all changes
git add -A

# Stage all changes in a directory
git add src/
```

### Partial File Staging

When a file contains changes for multiple commits, use interactive staging:

```bash
# Interactive hunk-by-hunk staging
git add -p <file>

# Commands in interactive mode:
# y - stage this hunk
# n - skip this hunk
# s - split into smaller hunks
# e - manually edit the hunk
# q - quit
```

### Verify Staging

```bash
# Confirm what's staged
git diff --staged

# Confirm what remains unstaged
git diff
```

## Creating Commits

### Standard Commit

```bash
git commit -m "type: summary"
```

### Commit with Body (HEREDOC)

Use HEREDOC for multi-line messages to preserve formatting:

```bash
git commit -m "$(cat <<'EOF'
type: summary

Body explaining why this change was made.
Additional context if needed.
EOF
)"
```

### Verify Commit

```bash
# Show the commit just created
git log -1

# Confirm working tree is clean (or shows remaining changes)
git status
```

## Splitting Changes into Multiple Commits

### Workflow

1. **Check current state:**
   ```bash
   git status
   git diff
   ```

2. **Stage first atomic unit:**
   ```bash
   git add <files-for-first-commit>
   ```

3. **Verify staging:**
   ```bash
   git diff --staged  # Should show only first commit's changes
   git diff           # Should show remaining changes
   ```

4. **Create first commit:**
   ```bash
   git commit -m "type: first change summary"
   ```

5. **Repeat for remaining changes**

### Example: Splitting a Feature + Refactor

```bash
# Initial state shows mixed changes
git status
# M src/db.js         (refactor)
# M src/handler.js    (feature)
# M tests/handler.test.js (feature tests)

# First commit: refactor
git add src/db.js
git commit -m "refactor: extract connection pool logic"

# Second commit: feature with tests
git add src/handler.js tests/handler.test.js
git commit -m "feat: add user authentication endpoint"
```

## Undoing Mistakes

### Unstage Files

```bash
# Unstage specific file
git restore --staged <file>

# Unstage all files
git restore --staged .
```

### Amend Last Commit

Only use when the commit hasn't been pushed:

```bash
# Add more changes to last commit
git add <forgotten-file>
git commit --amend --no-edit

# Change the commit message
git commit --amend -m "new message"
```

### Discard Uncommitted Changes

```bash
# Discard changes in specific file
git restore <file>

# Discard all uncommitted changes (CAUTION)
git restore .
```

## Viewing History

```bash
# Compact history
git log --oneline -20

# Detailed history with diffs
git log -p -5

# History for specific file
git log --oneline -- <file>

# Show specific commit
git show <commit-hash>
```

## Best Practices

1. **Always verify staging** before committing with `git diff --staged`
2. **Use partial staging** (`git add -p`) when files have mixed changes
3. **Check status after each commit** to confirm clean state or remaining work
4. **Use HEREDOC** for commit messages with bodies to preserve formatting
5. **Don't amend** commits that have been pushed to shared branches
