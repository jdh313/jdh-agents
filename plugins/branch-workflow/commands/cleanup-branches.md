---
description: Clean up old, merged, or abandoned branches/changes with guided selection and confirmation
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Bash([[:*)
  - Bash(if:*)
  - Read
---

# Cleanup Branches/Changes

Clean up old, merged, or abandoned branches/changes with guided multi-select deletion and confirmation.

## Immediate Execution

**VCS:** !`[[ -d .jj ]] && echo "jj" || echo "git"`

**Current Status:**
!`if [[ -d .jj ]]; then jj status; else git status; fi`

## Instructions

Based on the detected VCS shown above, follow these steps to identify and clean up branches or changes eligible for deletion.

### Step 1: List Cleanup Candidates

**For git:**

Display branches eligible for cleanup using:

```bash
git branch --merged | grep -v "main\|master\|develop" || echo "No merged branches found"
```

Also show branch details with age information:

```bash
git for-each-ref --sort='-committerdate:iso8601' --format=' %(committerdate:iso8601) %(refname:short)' refs/heads | grep -v "main\|master\|develop" || echo "No branches available for cleanup"
```

**For jj:**

List all changes that may be candidates for cleanup:

```bash
jj log --all --template '{change_id|short} {description|first_line}\n'
```

For each change shown, you can determine if it's eligible for abandonment based on:
- Is it an obsolete/abandoned change (no descendants)?
- Is it a completed/merged change?
- Has it been inactive?

### Step 2: Display Cleanup Candidates with Context

**For git (merged branches example output):**

```
Available branches for cleanup:
─────────────────────────────────────────
1. feature-login-page      (2024-12-15)
2. bugfix-null-pointer     (2024-12-10)
3. refactor-db-layer       (2024-12-05)
```

Show only branches that are:
- Merged into current branch (use `git branch --merged`)
- NOT main/master/develop (protected branches)
- Have a commit date (to show age)

**For jj (changes example output):**

```
Available changes for cleanup (review carefully before selecting):
────────────────────────────────────────────────────────────────
1. abc1234  feat: add authentication
2. def5678  refactor: extract utils
3. ghi9012  test: update coverage
```

Show:
- Change ID (short form)
- Description (first line)
- You can determine which ones are safe to abandon by reviewing the change log

### Step 3: Prompt for Multi-Select Deletion

Ask the user to select branches/changes for deletion using this format:

```
Select branches/changes to delete (enter numbers separated by commas, e.g., "1,2,3"):
Enter selection (or 'q' to cancel):
```

Validate the input:
- Accept comma-separated numbers (e.g., "1,2,3")
- Validate that each number corresponds to a listed item
- Accept 'q' or empty input to cancel
- Show an error if invalid numbers are provided and re-prompt

### Step 4: Build Deletion List

Parse the user's selection and build a list of branches/changes to delete.

**For git:**
- Extract the branch names from the selected items

**For jj:**
- Extract the change IDs from the selected items

Display the deletion list for confirmation:

```
Selected for deletion:
1. feature-login-page
2. bugfix-null-pointer

Proceed with deletion? (y/n):
```

### Step 5: Confirm Deletion

Prompt the user for final confirmation:

```
About to delete:
  - feature-login-page
  - bugfix-null-pointer

This action cannot be undone. Proceed? (y/n):
```

Validate input:
- 'y' or 'yes': Proceed with deletion
- 'n', 'no', or any other input: Cancel and show "Deletion cancelled."

### Step 6: Execute Deletion

**For git (safe delete by default):**

For each selected branch, attempt to delete with `-d` (safe delete):

```bash
git branch -d <branch-name>
```

If the branch has unmerged changes and the user wants to force delete it, offer them the option:

```
Failed to delete '<branch-name>' (unmerged changes).
Force delete anyway? (y/n):
```

If they confirm, use `-D`:

```bash
git branch -D <branch-name>
```

Track successes and failures:
- Successful deletions: "✓ Deleted: <branch-name>"
- Failed deletions (error): "✗ Failed to delete <branch-name>: <error-message>"

**For jj (abandon changes):**

For each selected change, attempt to abandon:

```bash
jj abandon <change-id>
```

Only attempt to abandon if the change appears safe (empty/no working copy).

Track successes and failures:
- Successful abandonment: "✓ Abandoned: <change-id>"
- Failed abandonment: "✗ Failed to abandon <change-id>: <error-message>"

### Step 7: Display Cleanup Summary

After all deletions complete, show a summary:

```
Cleanup Summary
═════════════════════════════════════════
Total deleted: 2
Total failed: 0

Deleted:
  ✓ feature-login-page
  ✓ bugfix-null-pointer

Remaining branches:
  - main
  - master
  - develop
  - your-active-branch
```

**Summary should include:**
- Total number of branches/changes successfully deleted
- Total number of failed deletions
- List of deleted names/IDs with status
- Any error messages from failed operations
- Current remaining branches/changes for context

**For git, also verify cleanup:**

```bash
git branch | grep -v "main\|master\|develop"
```

**For jj, verify:**

```bash
jj log --all --template '{change_id|short} {description|first_line}\n'
```

### Step 8: Final Status

Display final status:

**For git:**
```bash
git branch --show-current
```

**For jj:**
```bash
jj status
```

## Safety Considerations

### Protected Branches (Git Only)

- Never delete main, master, or develop branches
- Filter these out of the deletion list automatically
- Show a warning if user tries to select them

### Confirmation Required

- Always show what will be deleted before execution
- Require explicit confirmation (y/n) before proceeding
- Never auto-delete multiple branches/changes

### Force Delete (Git Only)

- Use `-d` (safe delete) by default
- Only offer `-D` (force delete) if `-d` fails with "unmerged changes" error
- Require explicit confirmation for force delete
- Warn user that force delete cannot be undone

### Change Safety (jj)

- Only suggest abandoning changes that appear to have no working copy
- Show change descriptions so users can identify them
- Warn if attempting to abandon a change with content

## Error Handling

Display clear error messages:

- **Git branch already deleted**: "Branch already deleted or not found"
- **Git branch has unmerged changes**: "Cannot delete unmerged branch. Use force delete (-D) if certain"
- **jj abandon failed**: "Cannot abandon change. It may have dependencies or contain work"
- **Invalid selection**: "Invalid selection. Please enter comma-separated numbers (e.g., '1,2,3')"
