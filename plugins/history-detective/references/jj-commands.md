# Jujutsu (jj) Commands Reference

Shared jj command patterns for change operations used across VCS plugins.

## Key Concepts

jj differs from git in fundamental ways:
- **No staging area:** The working copy IS the current change
- **Immutable commits:** Changes create new commit IDs
- **Always a change:** Every edit is part of a tracked change
- **Automatic working copy:** Changes are tracked automatically without `git add`

## Change Operations

### Create New Change

```bash
# Create new empty change on top of current
jj new

# Create new change with description
jj new -m "type: description"
```

**Non-interactive:** `-m` flag prevents editor from opening.

### Describe Change (Commit)

```bash
# Add description to current change
jj describe -m "type: description"

# Multi-line description
jj describe -m "type: summary

Body explaining why this change was made.
Additional context if needed."
```

**Non-interactive:** `-m` flag prevents editor from opening. Use HEREDOC for multi-line messages.

### List Changes

```bash
# View recent change history
jj log

# Limit number of changes shown
jj log --limit 20

# Show current change ID
jj log --limit 1

# Show all changes with graph
jj log --all
```

**Non-interactive:** All listing commands are read-only, no prompts.

### View Current Change

```bash
# Show status of current working copy
jj status

# Show diff of current change
jj diff

# Show diff of specific change
jj diff -r <change-id>

# Show detailed change info
jj show <change-id>
```

## Change Management

### Abandon Change

```bash
# Abandon current (empty) change
jj abandon

# Abandon specific change (must be empty)
jj abandon <change-id>
```

**Non-interactive:** No prompts when change is empty.

**Safety:** Only works on changes with no modifications. Safe for automation.

### Edit Existing Change

```bash
# Switch to editing a previous change
jj edit <change-id>

# Make edits to the change's files
# Working copy now shows the edited change

# Create new change when done with edits
jj new
```

### Describe With Arguments (Non-Interactive)

```bash
# Prevent editor from opening
jj describe -m "feat: add new feature" --no-edit

# Also works with new command
jj new -m "refactor: extract function" --no-edit
```

**Safety:** Always use `-m` with messages to prevent interactive editor.

## Change Cleanup Patterns

### List Abandoned Changes

```bash
# Show all changes in history
jj log --all

# Identify changes that are abandoned (no descendants)
jj log --all | grep "abandoned"
```

### Batch Abandon Changes

```bash
# Abandon multiple changes (one at a time)
jj abandon <change-id-1>
jj abandon <change-id-2>
jj abandon <change-id-3>

# After cleanup, verify with
jj log
```

**Safety:** Changes with descendants cannot be abandoned. Must be done in order.

### List Changes Not Pushed

```bash
# Show unpushed changes
jj log --all

# View pending changes awaiting push
jj status
```

## Change Information

### Get Current Change ID

```bash
# Show current change details
jj status

# Get just the change ID
jj log -r @ --no-graph --template '{change_id}\n'
```

### Get Change Details

```bash
# Show commit message of a change
jj show <change-id>

# Show files changed in a change
jj diff -r <change-id> --name-status

# Show full commit info
jj log -r <change-id> -T detailed
```

### Compare Changes

```bash
# Show diff between two changes
jj diff -r <change-id-1>:<change-id-2>

# Show what's different in current vs parent
jj diff
```

## Non-Interactive Patterns

**Key patterns to prevent interactive prompts:**

- **Create change:** `jj new -m "description"` (flag prevents editor)
- **Describe change:** `jj describe -m "message"` (flag prevents editor)
- **List changes:** `jj log`, `jj status` (read-only, no prompts)
- **Abandon change:** `jj abandon <id>` (no prompts when empty)
- **Edit change:** `jj edit <id>` (switches context, no prompts)

**Avoid these interactive patterns:**

- `jj new` (without -m) - opens editor for description
- `jj describe` (without -m) - opens editor for message
- `jj split -i` - opens interactive editor for split selection
- `jj edit` (without target) - prompts for selection

## Safety Considerations

### Prevent Accidental Deletions

```bash
# Check change has no modifications before abandon
jj status

# Verify change is safe to abandon
jj show <change-id>

# Abandon only after verification
jj abandon <change-id>
```

### Verify Current Change Before Operations

```bash
# Always check current context
jj status

# Review changes before describing
jj diff

# Confirm change was created
jj log --limit 1
```

### Restore Changes

```bash
# Undo the last jj operation
jj undo

# Recover abandoned changes (if not yet garbage collected)
jj log --all
```

## Splitting Changes (For Atomic Commits)

### Split by Files

```bash
# Split specific files into new change
jj split <file1> <file2> -m "type: description"

# Remaining files stay in current working copy
```

**Non-interactive:** `-m` flag prevents editor. Files explicitly listed.

### Split Interactively

```bash
# Interactive split (opens editor)
jj split -i

# Edit right side to choose what goes in new change
# Save and close editor to complete
```

### Example: Multiple Atomic Commits

```bash
# Initial state: mixed changes in working copy
jj status

# First: split refactor work
jj split src/db.js -m "refactor: extract connection pool"

# Second: split test updates
jj split tests/handler.test.js -m "test: add authentication tests"

# Third: describe remaining feature work
jj describe -m "feat: add authentication endpoint"

# Create empty change for next work
jj new

# Verify history
jj log --limit 5
```

## Best Practices

1. **Always use -m flag:** Prevents editor from opening: `jj new -m "msg"`, `jj describe -m "msg"`
2. **Check status before operations:** `jj status` confirms current context
3. **Create new change after describing:** Keeps working copy organized: `jj describe -m "msg"` then `jj new`
4. **Use --no-edit flag:** For absolute safety in automation: `jj describe -m "msg" --no-edit`
5. **Verify with jj log:** Always confirm changes were created correctly
6. **Abandon empty changes:** Clean up with `jj abandon` when working copy is empty
7. **Use jj undo liberally:** Safe to experiment since you can undo: `jj undo`
8. **Keep descriptions clear:** Use conventional commit format (type: summary)
