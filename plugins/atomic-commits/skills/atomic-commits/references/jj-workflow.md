# Jujutsu (jj) Workflow Reference

This reference provides jj-specific commands for the atomic commits workflow.

## Key Concepts

jj differs from git in important ways:
- **No staging area**: The working copy IS the current change
- **Immutable commits**: Changes create new commit IDs
- **Working copy is always a change**: Every edit is part of the current change
- **Split instead of stage**: Use `jj split` to separate changes into commits

## Checking Current State

```bash
# View working copy changes
jj status

# View diff of current change
jj diff

# View recent history
jj log --limit 10

# View diff of specific revision
jj diff -r <revision>
```

## Creating Changes (Commits)

### Describe Current Change

The working copy always has uncommitted changes. Describe it to "commit":

```bash
# Add description to current change
jj describe -m "type: summary"

# Multi-line description
jj describe -m "type: summary

Body explaining why this change was made.
Additional context if needed."
```

### Create New Change

After describing, create a new empty change to continue working:

```bash
# Create new change on top of current
jj new

# Create new change with description
jj new -m "type: next change summary"
```

### Typical Commit Flow

```bash
# 1. Make edits (automatically tracked)
# 2. Review changes
jj diff

# 3. Describe the change
jj describe -m "feat: add user authentication"

# 4. Create new change for next work
jj new
```

## Splitting Changes into Multiple Commits

### Split by Files

Split specific files into a new change with a description:

```bash
# Split specific files into a described change
jj split <file1> <file2> -m "type: summary for these files"

# Remaining changes stay in working copy
```

### Split Interactively

```bash
# Interactive split (opens diff editor)
jj split -i

# Edit the right side to choose what goes in the new change
# Save and close to complete the split
```

### Example: Splitting a Feature + Refactor

```bash
# Initial state shows mixed changes
jj status
# M src/db.js         (refactor)
# M src/handler.js    (feature)
# M tests/handler.test.js (feature tests)

# First: split out the refactor
jj split src/db.js -m "refactor: extract connection pool logic"

# Second: describe remaining feature changes
jj describe -m "feat: add user authentication endpoint"

# Create new change for next work
jj new
```

### Split Workflow for Multiple Commits

```bash
# 1. View all changes
jj status
jj diff

# 2. Split first atomic unit
jj split <files> -m "type: first change"

# 3. Split second atomic unit (from remaining)
jj split <files> -m "type: second change"

# 4. Describe final remaining changes
jj describe -m "type: final change"

# 5. Verify history
jj log --limit 5
```

## Modifying History

### Squash into Parent

Combine current change into its parent:

```bash
# Squash current change into parent
jj squash

# Squash with new combined message
jj squash -m "type: combined summary"
```

### Edit a Previous Change

```bash
# Edit a specific revision
jj edit <revision>

# Make changes, then return to latest
jj new
```

### Reorder or Reorganize

```bash
# Rebase current change onto different parent
jj rebase -d <destination>

# Rebase a branch of changes
jj rebase -s <source> -d <destination>
```

## Undoing Mistakes

### Restore Files

```bash
# Restore specific file to parent version
jj restore <file>

# Restore all files (discard all working copy changes)
jj restore
```

### Abandon Changes

```bash
# Abandon current change (if empty or unwanted)
jj abandon

# Abandon specific revision
jj abandon <revision>
```

### Undo Last Operation

```bash
# Undo the last jj operation
jj undo
```

## Viewing History

```bash
# Default log view
jj log

# Limit entries
jj log --limit 20

# Show specific revision details
jj show <revision>

# Show diff for a revision
jj diff -r <revision>
```

## Working with Git Backend

jj can work with git repositories:

```bash
# Check git HEAD alignment
jj log  # Shows git_head() marker

# Git operations still available if needed
jj git push
jj git fetch
```

## Best Practices

1. **Describe changes promptly**: Don't accumulate large undescribed changes
2. **Use `jj split` liberally**: It's the primary tool for atomic commits
3. **Split by files first**: `jj split <files> -m "msg"` is cleaner than interactive
4. **Create new change after describing**: Keep working copy clean with `jj new`
5. **Check `jj log` frequently**: Verify your change history looks correct
6. **Use `jj undo`**: It's safe to experiment since you can undo
7. **Abandon empty changes**: Clean up with `jj abandon` when working copy is empty
