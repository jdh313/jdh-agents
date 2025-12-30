---
description: Update jj change descriptions and squash changes for review preparation (jj only)
allowed-tools:
  - Bash(jj:*)
  - Read
---

# Update Changes

Update jj change descriptions and squash changes together for review preparation. This command helps organize your change history before code review by updating descriptions and combining related changes.

**Note:** This command is **jj-only**. Git uses a different model (commits vs. changes) and should use the separate "Clean Up Commit History" command instead.

## Immediate Execution

**VCS Check:**
!`if [[ -d .git && ! -d .jj ]]; then echo "ERROR: This command is jj-only"; exit 1; elif [[ -d .jj ]]; then echo "jj repository detected"; else echo "Not a jj repository"; exit 1; fi`

**Current Status:**
!`jj status`

**Current Change Details:**
!`jj log --limit 1 -T 'change_id.short() ++ " - " ++ description.first_line()' && echo ""`

## Instructions

This command helps you update change descriptions and squash changes together before submitting for code review. Follow the steps below to organize your changes as needed.

### Step 1: Show Current Change and Its Description

Display the current change you're working on and its full description:

```bash
echo "Current Change Details"
echo "════════════════════════════════════════════════════"
jj log --limit 1 -T 'change_id ++ " - " ++ description' && echo ""
echo ""
echo "Current change status:"
jj status
```

**Expected output:**
```
Current Change Details
════════════════════════════════════════════════════
abc123def456 - feat: add authentication

Working copy now at: abc123def456
Parent commit: xyz789
```

### Step 2: Show Recent Changes for Context

Display the recent change history so you can see what's available to squash or modify:

```bash
echo "Recent Changes"
echo "════════════════════════════════════════════════════"
jj log --limit 10 -T 'change_id.short() ++ " " ++ if(description.first_line(), description.first_line(), "(empty)")'
echo ""
```

**Expected output:**
```
Recent Changes
════════════════════════════════════════════════════
abc123de feat: add authentication
def456gh test: add auth tests
ghi789jk fix: handle edge case
jkl012mn chore: lint fixes
mno345pq feat: add password reset
```

### Step 3: Analyze Current Diff to Suggest Description

Show what changed in the current working copy to help suggest an improved description:

```bash
echo "Current Change Diff Summary"
echo "════════════════════════════════════════════════════"

# Show which files were changed
echo "Files changed:"
jj diff --stat

echo ""
echo "File list for reference:"
jj diff --summary | sed 's/^/  /'

echo ""

# Show a snippet of the actual changes (limited to first few changes)
echo "Changes overview (first 50 lines):"
echo "──────────────────────────────────"
jj diff | head -50
if jj diff | wc -l | grep -q "[0-9]"; then
  TOTAL_LINES=$(jj diff | wc -l)
  if [[ $TOTAL_LINES -gt 50 ]]; then
    echo ""
    echo "... (showing first 50 of $TOTAL_LINES lines, use 'jj diff' to see full diff)"
  fi
fi

echo ""

# Suggest a description based on files changed
echo "Suggested description based on changes:"
echo "──────────────────────────────────────────"
CHANGED_FILES=$(jj diff --summary | awk '{print $2}' | head -5 | sed 's|src/||g' | sed 's|tests/||g' | sed 's|\..*$||g' | paste -sd ',' - | sed 's/,/, /g')

if [[ -z "$CHANGED_FILES" ]]; then
  echo "  (unable to determine from files)"
else
  echo "  Based on files modified: $CHANGED_FILES"
  echo "  Example: 'feat: implement $CHANGED_FILES feature'"
fi
```

**What this shows:**
- Which files were modified in the current change
- Summary statistics (additions/deletions)
- Snippet of actual changes
- A suggested description based on file names

### Step 4: Present Options to User

Based on the change analysis, present the following options:

```
Change Modification Options
════════════════════════════════════════════════════

Option A: Update current change description
  - Modify the description of the current change
  - Use this to improve the message or fix typos
  - Non-interactive with -m flag

Option B: Squash current change into parent
  - Combine current change with its parent change
  - Merges changes from working copy into parent
  - Keeps the parent's description unless both are non-empty

Option C: Squash specific change into another
  - Select a source change and target change
  - Combines the source changes into the target
  - Useful for reorganizing related changes

Option D: Cancel
  - Exit without making changes

Select an option (a/b/c/d):
```

### Step 5: Execute Option A - Update Description

If the user selects Option A, prompt for the new description and update it:

```bash
echo "Update Change Description"
echo "════════════════════════════════════════════════════"
echo "Current description:"
jj log --limit 1 -T 'description'
echo ""
echo ""
echo "Enter new description (use conventional format: type: summary):"
echo "Examples:"
echo "  - feat: add password reset functionality"
echo "  - fix: handle edge case in auth validation"
echo "  - refactor: extract authentication logic"
echo "  - test: add comprehensive auth tests"
echo ""

# Read user input
read -p "New description: " NEW_DESCRIPTION

if [[ -z "$NEW_DESCRIPTION" ]]; then
  echo "Error: Description cannot be empty"
  exit 1
fi

# Update the change description
echo ""
echo "Updating change description..."
jj describe -m "$NEW_DESCRIPTION"

if [[ $? -eq 0 ]]; then
  echo "✓ Description updated successfully"
  echo ""
  echo "New description:"
  jj log --limit 1 -T 'description'
else
  echo "✗ Failed to update description"
  exit 1
fi
```

**Key details:**
- Uses `-m` flag to set description non-interactively
- The `-m` flag prevents opening editor automatically
- Confirms success and shows new description

### Step 6: Execute Option B - Squash Into Parent

If the user selects Option B, squash the current change into its parent:

```bash
echo "Squash Current Change Into Parent"
echo "════════════════════════════════════════════════════"

# Show current change details
echo "Current change details:"
jj log --limit 1 -T 'change_id.short() ++ " - " ++ description.first_line()'
echo ""

# Show parent change
echo "Parent change (target for squash):"
jj log --limit 1 -r '@-' -T 'change_id.short() ++ " - " ++ description.first_line()'
echo ""

echo "Warning: This will combine the current change into its parent."
echo "The parent's description will be kept unless both have non-empty descriptions."
echo ""
read -p "Proceed with squash? (y/n): " CONFIRM

if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
  echo "Squash cancelled."
  exit 0
fi

echo ""
echo "Squashing current change into parent..."

# Squash with no arguments (uses default: squash @ into @-)
jj squash --use-destination-message

if [[ $? -eq 0 ]]; then
  echo "✓ Squash completed successfully"
  echo ""
  echo "Updated change history:"
  jj log --limit 5 -T 'change_id.short() ++ " " ++ if(description.first_line(), description.first_line(), "(empty)")'
else
  echo "✗ Squash failed"
  exit 1
fi
```

**Key details:**
- Shows source (current) and target (parent) changes
- Prompts for confirmation before executing
- `jj squash` with no args squashes current into parent
- Displays updated history after completion

### Step 7: Execute Option C - Squash Specific Changes

If the user selects Option C, allow them to choose source and target changes:

```bash
echo "Squash Specific Changes"
echo "════════════════════════════════════════════════════"
echo ""
echo "Available changes (select change ID to squash):"
echo "──────────────────────────────────────────────────"
jj log --limit 20 -T 'change_id.short() ++ " " ++ if(description.first_line(), description.first_line(), "(empty)")'
echo ""
echo ""

read -p "Enter source change ID (the change to squash FROM): " SOURCE_CHANGE

if [[ -z "$SOURCE_CHANGE" ]]; then
  echo "Error: Source change ID cannot be empty"
  exit 1
fi

echo ""
echo "Available target changes:"
jj log --limit 20 -T 'change_id.short() ++ " " ++ if(description.first_line(), description.first_line(), "(empty)")'
echo ""

read -p "Enter target change ID (the change to squash INTO): " TARGET_CHANGE

if [[ -z "$TARGET_CHANGE" ]]; then
  echo "Error: Target change ID cannot be empty"
  exit 1
fi

# Verify both changes exist
jj log -r "$SOURCE_CHANGE" > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
  echo "Error: Source change '$SOURCE_CHANGE' not found"
  exit 1
fi

jj log -r "$TARGET_CHANGE" > /dev/null 2>&1
if [[ $? -ne 0 ]]; then
  echo "Error: Target change '$TARGET_CHANGE' not found"
  exit 1
fi

# Show what will happen
echo ""
echo "Source change (will be squashed):"
jj log -r "$SOURCE_CHANGE" -T 'change_id.short() ++ " - " ++ description.first_line()'
echo ""
echo "Target change (will receive changes):"
jj log -r "$TARGET_CHANGE" -T 'change_id.short() ++ " - " ++ description.first_line()'
echo ""

read -p "Proceed with squash? (y/n): " CONFIRM

if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
  echo "Squash cancelled."
  exit 0
fi

echo ""
echo "Squashing $SOURCE_CHANGE into $TARGET_CHANGE..."

# Squash the specified changes
jj squash --from "$SOURCE_CHANGE" --into "$TARGET_CHANGE" --use-destination-message

if [[ $? -eq 0 ]]; then
  echo "✓ Squash completed successfully"
  echo ""
  echo "Updated change history:"
  jj log --limit 5 -T 'change_id.short() ++ " " ++ if(description.first_line(), description.first_line(), "(empty)")'
else
  echo "✗ Squash failed"
  exit 1
fi
```

**Key details:**
- Shows available changes with short IDs
- Prompts for source and target change IDs
- Verifies both changes exist before squashing
- Uses `jj squash --from X --into Y` syntax
- Displays updated history after completion

### Step 8: Show Updated State

After any modification, show the final state of changes:

```bash
echo ""
echo "Final Change History"
echo "════════════════════════════════════════════════════"
jj log --limit 5 -T 'change_id.short() ++ " " ++ if(description.first_line(), description.first_line(), "(empty)")'
echo ""
echo "Current status:"
jj status
echo ""

echo "Summary:"
echo "  - All changes visible above are ready for review"
echo "  - To see full descriptions: jj log"
echo "  - To see diff details: jj diff"
echo "  - To undo last change: jj undo"
```

**Expected output:**
```
Final Change History
════════════════════════════════════════════════════
abc123de feat: add authentication
def456gh fix: handle edge case
ghi789jk test: add auth tests
jkl012mn feat: add password reset

Current status:
Working copy now at: abc123de
Parent commit: xyz789

Summary:
  - All changes visible above are ready for review
  - To see full descriptions: jj log
  - To see diff details: jj diff
  - To undo last change: jj undo
```

## Safety Considerations

### VCS Detection

This command only works with jj repositories. If you're using git, use the "Clean Up Commit History" command instead.

```
If git detected:
✗ Error: This command is jj-only
Git uses commits, not changes. Use "cleanup-history" command instead.
Exit immediately.
```

### Reversibility

All jj operations are safe and reversible:

```bash
# If something goes wrong, undo the last operation
jj undo

# Undo multiple operations (repeats as needed)
jj undo && jj undo
```

### Change Merging Behavior

When squashing changes with different descriptions:
- If both source and target have non-empty descriptions, you will be prompted for the combined message
- If one is empty, the non-empty description is automatically used
- If both are empty, the result will be empty (can be described later)

### Abandoned Changes

If a source change becomes empty after squashing (no changes remain in it), it will be automatically abandoned. This is normal and safe.

### Parent-Only Squash

When using Option B (squash into parent), ensure:
- You have exactly one parent (not a merge commit)
- The parent exists in your working context
- You want to combine all changes from current into parent

## Error Handling

**jj not found:**
```
Error: jj command not found
This command requires Jujutsu to be installed
```
Exit with clear message.

**Not a jj repository:**
```
Error: Not a jj repository
Must be run from a jj workspace
```
Exit immediately without proceeding.

**Git repository detected:**
```
Error: This command is jj-only
You are in a git repository. Use "cleanup-history" command instead.
```
Exit immediately.

**Invalid change ID:**
```
Error: Change 'abc123' not found
Verify the change ID is correct and try again
```
Re-prompt the user or exit.

**Squash conflict during merge:**
```
Error: Squash failed - conflicting descriptions
Both source and target changes have descriptions.
New merged description needed.
```
Prompt user for combined description and retry.

## Best Practices

1. **Update descriptions before squashing**: Clear descriptions help during code review
2. **Squash related changes**: Combine changes that represent a single logical feature
3. **Keep atomic changes**: Each change should represent one unit of work
4. **Review before finalizing**: Always check `jj log` after making changes
5. **Use conventional format**: Start descriptions with type (feat, fix, refactor, test, chore)
6. **Test after cleanup**: Ensure your code still works after any reorganization
7. **Use undo liberally**: No harm in experimenting—`jj undo` always works

## Examples

**Example 1: Update Description Only**

```bash
# Before
Current change: abc123de - add authentication

# User selects Option A and provides:
# "feat: implement JWT authentication with refresh tokens"

# After
abc123de - feat: implement JWT authentication with refresh tokens
```

**Example 2: Squash Into Parent**

```bash
# Before
abc123de - feat: add authentication
def456gh - fix: handle edge case in auth
ghi789jk - test: add auth tests

# User selects Option B while on def456gh
# System squashes def456gh into abc123de

# After
abc123de - feat: add authentication (now contains both feat + fix)
ghi789jk - test: add auth tests
```

**Example 3: Squash Specific Changes**

```bash
# Before
abc123de - feat: add authentication
def456gh - test: add auth tests
ghi789jk - test: add edge case tests
jkl012mn - feat: add password reset

# User selects Option C
# From: ghi789jk (edge case tests)
# Into: def456gh (other auth tests)

# After
abc123de - feat: add authentication
def456gh - test: add auth tests (now contains both test files)
jkl012mn - feat: add password reset
```

## Detailed jj Squash Reference

### Squash Current Into Parent

```bash
jj squash
# Equivalent to: jj squash --from @ --into @-
```

Combines all changes from working copy into parent.

### Squash Specific Changes

```bash
jj squash --from abc123de --into def456gh
```

Moves changes from `abc123de` into `def456gh`. If `abc123de` becomes empty, it is abandoned.

### Partial Squash (Specific Files Only)

```bash
jj squash --from abc123de --into def456gh -- src/auth.js tests/auth.test.js
```

Squash only specific files from source into target. Remaining files stay in source.

### Squash With Change Tracking

After squashing, jj automatically:
1. Creates a new change ID for modified revisions
2. Updates parent references for dependent changes
3. Abandons empty source changes (unless `--keep-emptied` is used)
4. Preserves working copy structure

## Common Workflows

**Workflow 1: Clean Up Before Review**

```bash
# 1. Update description for clarity
jj describe -m "feat: complete authentication system"

# 2. View recent changes
jj log --limit 5

# 3. Squash test files with main feature
jj squash --from test-change-id --into feature-change-id

# 4. Final verification
jj log --limit 3
```

**Workflow 2: Reorganize Changes**

```bash
# 1. View all recent changes
jj log --limit 20

# 2. Squash refactoring into initial implementation
jj squash --from refactor-id --into impl-id

# 3. Squash fixes into appropriate features
jj squash --from fix1-id --into feature1-id
jj squash --from fix2-id --into feature2-id

# 4. Review final organization
jj log
```

**Workflow 3: Combine Related Work**

```bash
# 1. You have: 3 separate feature changes, 2 test changes
jj log

# 2. Squash tests into their feature changes
jj squash --from tests1-id --into feature1-id
jj squash --from tests2-id --into feature2-id

# 3. Verify cleaner history
jj log
```
