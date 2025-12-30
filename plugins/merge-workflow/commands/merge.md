---
description: Merge a branch (git) or create a merge change (jj) with custom message
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Read
---

# Merge Branch

Merge a branch (git) or create a merge change (jj) with a custom merge message. Supports both git and jj VCS with automatic conflict detection after merge.

## Immediate Execution

**VCS Detection:**
!`[[ -d .jj ]] && echo "jj" || echo "git"`

**Current Status:**
!`if [[ -d .jj ]]; then jj status; else git status; fi`

## Instructions

Based on the detected VCS shown above, this command will guide you through merging a branch or change with conflict detection.

### Step 1: Validate Repository State

**For git:**

Check that the repository is clean and no merge is already in progress:

```bash
# Check for merge in progress
if [[ -f .git/MERGE_HEAD ]]; then
  echo "Error: Git merge already in progress. Complete or abort the current merge first."
  echo "  To abort: git merge --abort"
  exit 1
fi

# Check for uncommitted changes that would block the merge
UNSTAGED=$(git diff --name-only)
STAGED=$(git diff --cached --name-only)
if [[ -n "$UNSTAGED" ]] || [[ -n "$STAGED" ]]; then
  echo "Warning: You have uncommitted changes:"
  [[ -n "$UNSTAGED" ]] && echo "  Unstaged: $UNSTAGED"
  [[ -n "$STAGED" ]] && echo "  Staged: $STAGED"
  echo "Note: These will not block the merge, but will be included in the merge commit."
fi
```

**For jj:**

Check that we're in a valid working state:

```bash
# Get current change
CURRENT_CHANGE=$(jj log -T change_id --no-graph -r @)
echo "Current change: $CURRENT_CHANGE"

# Show current status
jj status
```

### Step 2: List Available Branches/Changes

**For git:**

List all available branches to merge from:

```bash
# Show local branches (sorted by recency)
echo "=== Local Branches (sorted by recency) ==="
git for-each-ref --sort=-committerdate refs/heads/ --format='%(refname:short) | %(committerdate:short) | %(subject)'

echo ""
echo "=== Remote Branches ==="
git for-each-ref --sort=-committerdate refs/remotes/ --format='%(refname:short) | %(committerdate:short) | %(subject)'

# Show current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo ""
echo "Current branch: $CURRENT_BRANCH"
```

**For jj:**

List recent changes available to merge:

```bash
# Show recent changes
echo "=== Recent Changes ==="
jj log -T 'change_id.short() " | " description.first_line()' --no-graph -r "ancestors(root())" --limit 10

echo ""
echo "=== Current Workspace ==="
jj status
```

### Step 3: Prompt for Source Branch/Change

Prompt the user to specify what to merge.

**For git:**

```bash
echo ""
read -p "Enter branch name to merge (or 'cancel' to abort): " SOURCE_BRANCH

if [[ "$SOURCE_BRANCH" == "cancel" ]]; then
  echo "Merge cancelled."
  exit 0
fi

# Validate branch exists
if ! git rev-parse --verify "$SOURCE_BRANCH" > /dev/null 2>&1; then
  echo "Error: Branch '$SOURCE_BRANCH' does not exist."
  exit 1
fi

# Ensure it's not the current branch
if [[ "$SOURCE_BRANCH" == "$CURRENT_BRANCH" ]]; then
  echo "Error: Cannot merge branch into itself."
  exit 1
fi

echo "Source branch: $SOURCE_BRANCH"
```

**For jj:**

```bash
echo ""
read -p "Enter change ID or revision to merge (or 'cancel' to abort): " SOURCE_CHANGE

if [[ "$SOURCE_CHANGE" == "cancel" ]]; then
  echo "Merge cancelled."
  exit 0
fi

# Validate change exists
if ! jj log -r "$SOURCE_CHANGE" > /dev/null 2>&1; then
  echo "Error: Change '$SOURCE_CHANGE' does not exist."
  exit 1
fi

echo "Source change: $SOURCE_CHANGE"
```

### Step 4: Prompt for Merge Message

Prompt the user for a custom merge message.

**Common prompt:**

```bash
echo ""
echo "Enter merge message (or press Enter for default):"
read -p "> " MERGE_MESSAGE

# Set default if empty
if [[ -z "$MERGE_MESSAGE" ]]; then
  if [[ -d .jj ]]; then
    MERGE_MESSAGE="Merge $SOURCE_CHANGE"
  else
    MERGE_MESSAGE="Merge branch '$SOURCE_BRANCH'"
  fi
  echo "Using default message: $MERGE_MESSAGE"
fi
```

### Step 5: Execute Merge

**For git:**

Execute the merge with the specified message:

```bash
echo ""
echo "Merging '$SOURCE_BRANCH' into '$(git rev-parse --abbrev-ref HEAD)'..."
git merge "$SOURCE_BRANCH" -m "$MERGE_MESSAGE" --no-edit

MERGE_EXIT_CODE=$?

if [[ $MERGE_EXIT_CODE -eq 0 ]]; then
  echo "✓ Merge completed successfully."
  MERGE_SUCCESS="true"
else
  echo "⚠ Merge resulted in conflicts."
  MERGE_SUCCESS="false"
fi
```

**For jj:**

Create a new merge change:

```bash
echo ""
echo "Creating merge change from $SOURCE_CHANGE..."

# Get current change before creating merge
PARENT_CHANGE=$(jj log -T change_id --no-graph -r @)

# Create merge change: merge two parents (current + source)
jj new "$PARENT_CHANGE" "$SOURCE_CHANGE" -m "$MERGE_MESSAGE"

MERGE_EXIT_CODE=$?

if [[ $MERGE_EXIT_CODE -eq 0 ]]; then
  echo "✓ Merge change created successfully."
  MERGE_SUCCESS="true"
else
  echo "✗ Failed to create merge change."
  exit 1
fi
```

### Step 6: Detect Conflicts

After merge, automatically detect if conflicts exist:

**For git:**

```bash
if [[ "$MERGE_SUCCESS" == "true" ]]; then
  # Check for conflicts
  if git diff --name-only --diff-filter=U | grep -q .; then
    echo ""
    echo "⚠ Conflicts detected during merge."
    CONFLICTS_FOUND="true"
  else
    echo ""
    echo "✓ No conflicts detected."
    CONFLICTS_FOUND="false"
  fi
fi
```

**For jj:**

```bash
if [[ "$MERGE_SUCCESS" == "true" ]]; then
  # Check for conflicts in the new merge change
  if jj status | grep -q "Conflicted"; then
    echo ""
    echo "⚠ Conflicts detected in merge change."
    CONFLICTS_FOUND="true"
  else
    echo ""
    echo "✓ No conflicts detected."
    CONFLICTS_FOUND="false"
  fi
fi
```

### Step 7: Show Merge Result Summary

Display the outcome of the merge operation:

```bash
if [[ "$CONFLICTS_FOUND" == "true" ]]; then
  echo ""
  echo "=== Merge Status ==="
  echo "Status: CONFLICTS DETECTED"
  echo ""
  echo "Conflicted files:"
  if [[ -d .jj ]]; then
    jj status | grep "Conflicted"
  else
    git diff --name-only --diff-filter=U
  fi
  echo ""
  echo "Next steps:"
  echo "  1. Review conflicted files listed above"
  echo "  2. Resolve conflicts (edit files and remove conflict markers)"
  echo "  3. For git: stage resolved files with 'git add <file>'"
  echo "  4. For git: complete merge with 'git commit' (or use /merge-workflow:resolve-conflicts)"
  echo "  5. For jj: conflicts auto-resolve when saved correctly"
  echo ""
  echo "Use '/merge-workflow:detect-conflicts' to see detailed conflict analysis."
  echo "Use '/merge-workflow:resolve-conflicts' for conflict resolution assistance."
else
  echo ""
  echo "=== Merge Status ==="
  echo "Status: SUCCESS (no conflicts)"
  echo ""
  if [[ -d .jj ]]; then
    echo "Merge change created:"
    jj log -T 'change_id.short() " | " description.first_line()' --no-graph -r @ -1
  else
    echo "Merged successfully. Repository state:"
    git log -1 --oneline
  fi
fi
```

### Step 8: Offer Next Actions

Guide the user to next steps based on merge result:

```bash
echo ""
echo "Next options:"
if [[ "$CONFLICTS_FOUND" == "true" ]]; then
  echo ""
  echo "1. View conflict details with /merge-workflow:detect-conflicts"
  echo "2. Get resolution help with /merge-workflow:resolve-conflicts"
  echo "3. For git: abort merge with 'git merge --abort' (if needed)"
  echo ""
  read -p "Enter choice (1-3, or press Enter to finish): " NEXT_ACTION

  case "$NEXT_ACTION" in
    1)
      echo "Run: /merge-workflow:detect-conflicts"
      ;;
    2)
      echo "Run: /merge-workflow:resolve-conflicts"
      ;;
    3)
      if [[ -d .git ]]; then
        read -p "Are you sure you want to abort the merge? (yes/no): " CONFIRM
        if [[ "$CONFIRM" == "yes" ]]; then
          git merge --abort
          echo "✓ Merge aborted."
        fi
      else
        echo "Note: For jj, you can create a new change with 'jj new' to start fresh."
      fi
      ;;
  esac
else
  echo ""
  echo "Merge complete! You can now:"
  echo "1. Continue working (changes are in the working directory)"
  echo "2. Create another merge with /merge-workflow:merge"
  echo "3. Run tests to verify the merge"
  echo "4. For git: push to remote with 'git push'"
  echo "5. For jj: submit with 'jj submit' when ready"
fi
```

## Error Handling

**Common error scenarios:**

1. **Not in a git/jj repository:**
   ```bash
   if [[ ! -d .git ]] && [[ ! -d .jj ]]; then
     echo "Error: Not in a git or jj repository."
     exit 1
   fi
   ```

2. **Branch/change does not exist:**
   - Message: "Error: [branch/change] does not exist."
   - Exit with error code

3. **Merge already in progress (git):**
   - Message: "Error: Git merge already in progress."
   - Suggest: `git merge --abort` or continue resolving

4. **Source and destination are the same:**
   - Message: "Error: Cannot merge branch into itself."
   - Exit with error code

5. **Merge failed (permission/network issue):**
   - Message: "Error: Merge operation failed."
   - Show git/jj error output
   - Exit with error code

## Safety Considerations

1. **No automatic conflict resolution**: Conflicts are detected but not automatically resolved (user decides).
2. **Merge state validation**: Check for existing merges before starting (git) to prevent conflicting operations.
3. **Clean working directory check**: Warn if there are uncommitted changes (they'll be included in merge).
4. **Branch validation**: Ensure source branch/change exists before attempting merge.
5. **Message validation**: Provide sensible defaults if user doesn't specify message.

## Performance Considerations

1. **Branch listing**: Use efficient git commands (for-each-ref with sorting) instead of listing all branches.
2. **Conflict detection**: Use fast status checks instead of parsing entire diffs.
3. **Avoid large operations**: Keep prompts and output focused on essential information.

## Example Usage

### Example 1: Git Merge (no conflicts)

```
VCS Detected: git
Current branch: main

=== Local Branches (sorted by recency) ===
feature/new-auth | 2025-12-28 | Add authentication module
fix/bug-123 | 2025-12-27 | Fix critical bug

Current branch: main

Enter branch name to merge (or 'cancel' to abort): feature/new-auth

Enter merge message (or press Enter for default):
> Merge feature/new-auth: add authentication

Merging 'feature/new-auth' into 'main'...
✓ Merge completed successfully.

✓ No conflicts detected.

=== Merge Status ===
Status: SUCCESS (no conflicts)

Merged successfully. Repository state:
abc1234 Merge feature/new-auth: add authentication

Next options:

Merge complete! You can now:
1. Continue working (changes are in the working directory)
2. Create another merge with /merge-workflow:merge
3. Run tests to verify the merge
4. For git: push to remote with 'git push'
```

### Example 2: Git Merge (with conflicts)

```
VCS Detected: git

Merging 'develop' into 'main'...
⚠ Merge resulted in conflicts.

⚠ Conflicts detected during merge.

=== Merge Status ===
Status: CONFLICTS DETECTED

Conflicted files:
src/auth.py
config/settings.json

Next steps:
  1. Review conflicted files listed above
  2. Resolve conflicts (edit files and remove conflict markers)
  3. For git: stage resolved files with 'git add <file>'
  4. For git: complete merge with 'git commit'
  5. Use '/merge-workflow:detect-conflicts' for details

Next options:

1. View conflict details with /merge-workflow:detect-conflicts
2. Get resolution help with /merge-workflow:resolve-conflicts
3. For git: abort merge with 'git merge --abort' (if needed)

Enter choice (1-3, or press Enter to finish): 1
Run: /merge-workflow:detect-conflicts
```

### Example 3: JJ Merge

```
VCS Detected: jj

Current change: a1b2c3d4

=== Recent Changes ===
f5e6d7c " | " Add database migration
e4d3c2b " | " Refactor API layer
d3c2b1a " | " Fix typo in docs

Current change: a1b2c3d4

Enter change ID or revision to merge (or 'cancel' to abort): f5e6d7c

Enter merge message (or press Enter for default):
> Merge database migration

Creating merge change from f5e6d7c...
✓ Merge change created successfully.

✓ No conflicts detected.

=== Merge Status ===
Status: SUCCESS (no conflicts)

Merge change created:
h9i8j7k6 | Merge database migration

Merge complete! You can now:
1. Continue working (changes are in the working directory)
2. Create another merge with /merge-workflow:merge
3. Run tests to verify the merge
4. For jj: submit with 'jj submit' when ready
```

## Related Commands

- `/merge-workflow:detect-conflicts` - Analyze and categorize conflicts in detail
- `/merge-workflow:resolve-conflicts` - Get guidance resolving specific conflicts
- `/merge-workflow:cleanup` - Clean up or reset merge state
