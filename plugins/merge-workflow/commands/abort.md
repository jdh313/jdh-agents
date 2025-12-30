---
description: Abort an in-progress merge or rebase operation and return to clean state
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Read
---

# Abort

Abort an in-progress merge or rebase operation and return to the repository to its pre-operation state.

**Supports:** Both git and jj repositories.

## Immediate Execution

**VCS Detection:**
!`[[ -d .jj ]] && echo "VCS: jj" || echo "VCS: git"`

**Current Status:**
!`if [[ -d .jj ]]; then jj status; elif [[ -d .git ]]; then git status; fi`

**Operation Detection:**
!`if [[ -d .git ]]; then if [[ -d .git/rebase-merge ]] || [[ -d .git/rebase-apply ]]; then echo "Git: Rebase in progress"; elif [[ -f .git/MERGE_HEAD ]]; then echo "Git: Merge in progress"; else echo "Git: No operation in progress"; fi; elif [[ -d .jj ]]; then jj status | grep -q "unresolved" && echo "Jj: Conflict resolution in progress" || echo "Jj: No operation in progress"; fi`

## Instructions

This command aborts any in-progress merge or rebase operation, safely returning the repository to its pre-operation state.

### Step 1: Detect VCS and Check for Active Operations

First, determine which VCS is in use and check for active merge/rebase operations:

```bash
# Detect VCS
if [[ -d .jj ]]; then
  VCS="jj"
  echo "VCS: Jujutsu (jj)"
elif [[ -d .git ]]; then
  VCS="git"
  echo "VCS: Git"
else
  echo "ERROR: Not a git or jj repository"
  exit 1
fi

echo ""
echo "Abort Workflow"
echo "════════════════════════════════════════════════════"
echo ""
```

### Step 2: Detect Current Operation State

Check what operation is currently in progress:

```bash
OPERATION_TYPE="none"

if [[ "$VCS" == "git" ]]; then
  # Check for rebase in progress
  if [[ -d .git/rebase-merge ]]; then
    OPERATION_TYPE="rebase-merge"
    echo "Detected: Git rebase (interactive or regular) in progress"
  elif [[ -d .git/rebase-apply ]]; then
    OPERATION_TYPE="rebase-apply"
    echo "Detected: Git rebase (patch apply) in progress"
  # Check for merge in progress
  elif [[ -f .git/MERGE_HEAD ]]; then
    OPERATION_TYPE="merge"
    echo "Detected: Git merge in progress"
  else
    OPERATION_TYPE="none"
    echo "No merge or rebase operation detected"
  fi

elif [[ "$VCS" == "jj" ]]; then
  # Check for conflicts in working state
  if jj status 2>/dev/null | grep -q "unresolved\|conflict"; then
    OPERATION_TYPE="conflict-resolution"
    echo "Detected: Jj conflict resolution in progress"
  else
    OPERATION_TYPE="none"
    echo "No conflict resolution in progress"
  fi
fi

echo ""
```

### Step 3: Show What Will Be Aborted

Display information about what will be discarded:

```bash
if [[ "$OPERATION_TYPE" == "none" ]]; then
  echo "No operation in progress. Nothing to abort."
  echo ""

  if [[ "$VCS" == "git" ]]; then
    git status
  elif [[ "$VCS" == "jj" ]]; then
    jj status
  fi

  exit 0
fi

echo "State Before Abort"
echo "════════════════════════════════════════════════════"
echo ""

if [[ "$VCS" == "git" ]]; then
  if [[ "$OPERATION_TYPE" == "rebase-merge" ]] || [[ "$OPERATION_TYPE" == "rebase-apply" ]]; then
    echo "Rebase Details:"

    # Show commits that would be rebased
    if [[ -d .git/rebase-merge ]]; then
      NEXT=$(cat .git/rebase-merge/next 2>/dev/null || echo "unknown")
      LAST=$(cat .git/rebase-merge/last 2>/dev/null || echo "unknown")
      echo "  - Commits in rebase: $NEXT of $LAST"
    fi

    # Show conflicted files if any
    if git diff --name-only --diff-filter=U 2>/dev/null | grep -q .; then
      echo "  - Conflicted files:"
      git diff --name-only --diff-filter=U | sed 's/^/      /'
    fi

  elif [[ "$OPERATION_TYPE" == "merge" ]]; then
    echo "Merge Details:"

    # Show branches being merged
    if [[ -f .git/MERGE_HEAD ]]; then
      MERGE_HEAD=$(cat .git/MERGE_HEAD)
      echo "  - Merging commit: $MERGE_HEAD"
    fi

    # Show conflicted files if any
    if git diff --name-only --diff-filter=U 2>/dev/null | grep -q .; then
      echo "  - Conflicted files:"
      git diff --name-only --diff-filter=U | sed 's/^/      /'
    fi
  fi

elif [[ "$VCS" == "jj" ]]; then
  if [[ "$OPERATION_TYPE" == "conflict-resolution" ]]; then
    echo "Conflict Resolution Details:"

    # Show current changes with conflicts
    jj status | head -20 | sed 's/^/  /'

    echo ""
    echo "Conflicted files:"
    jj diff --summary 2>/dev/null | grep -E "^\s+[MA]\s+" | awk '{print $2}' | while read file; do
      if grep -q "^<<<<<<<" "$file" 2>/dev/null; then
        echo "  - $file"
      fi
    done
  fi
fi

echo ""
```

### Step 4: Confirm Abort with User

Request user confirmation before proceeding:

```bash
echo "⚠ Warning: This will discard all changes from the in-progress operation"
echo ""

read -p "Do you want to abort the $OPERATION_TYPE operation? (y/N) " -r CONFIRM

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo ""
  echo "Abort cancelled. Operation remains in progress."
  exit 0
fi

echo ""
```

### Step 5: Execute Abort Command

Perform the abort operation:

```bash
echo "Aborting operation..."
echo "────────────────────────────────────────────────"
echo ""

ABORT_SUCCESS=false

if [[ "$VCS" == "git" ]]; then
  if [[ "$OPERATION_TYPE" == "rebase-merge" ]] || [[ "$OPERATION_TYPE" == "rebase-apply" ]]; then
    echo "Executing: git rebase --abort"
    git rebase --abort
    ABORT_EXIT=$?

  elif [[ "$OPERATION_TYPE" == "merge" ]]; then
    echo "Executing: git merge --abort"
    git merge --abort
    ABORT_EXIT=$?
  fi

elif [[ "$VCS" == "jj" ]]; then
  if [[ "$OPERATION_TYPE" == "conflict-resolution" ]]; then
    echo "Executing: jj abandon"
    jj abandon
    ABORT_EXIT=$?
  fi
fi

echo ""

if [[ $ABORT_EXIT -eq 0 ]]; then
  ABORT_SUCCESS=true
  echo "✓ Operation aborted successfully"
else
  echo "✗ Error aborting operation"
  echo ""
  echo "Exit code: $ABORT_EXIT"
  exit 1
fi

echo ""
```

### Step 6: Verify Clean State

Verify that the repository has returned to a clean state:

```bash
echo "Verifying clean state..."
echo "────────────────────────────────────────────────"
echo ""

CLEAN_STATE=true

if [[ "$VCS" == "git" ]]; then
  # Check no rebase/merge markers remain
  if [[ -d .git/rebase-merge ]] || [[ -d .git/rebase-apply ]] || [[ -f .git/MERGE_HEAD ]]; then
    echo "✗ Repository still in merge/rebase state"
    CLEAN_STATE=false
  fi

  # Check for conflict markers in files
  if git diff --name-only --diff-filter=U 2>/dev/null | grep -q .; then
    echo "✗ Conflicted files still present"
    CLEAN_STATE=false
  fi

  # Check working directory status
  if ! git status --porcelain | grep -q .; then
    # Working directory is clean (no changes)
    :
  fi

elif [[ "$VCS" == "jj" ]]; then
  # Check no conflicts remain
  if jj status 2>/dev/null | grep -q "unresolved\|conflict"; then
    echo "✗ Conflicts still detected"
    CLEAN_STATE=false
  fi

  # Check for conflict markers
  if jj diff 2>/dev/null | grep -q "^<<<<<<<"; then
    echo "✗ Conflict markers still present"
    CLEAN_STATE=false
  fi
fi

if [[ "$CLEAN_STATE" == "true" ]]; then
  echo "✓ Repository is clean"
else
  echo "⚠ Warning: Repository may not be fully clean"
  echo "Please review the status below"
fi

echo ""
```

### Step 7: Display Final Status

Show the current repository state after abort:

```bash
echo "Final Status"
echo "════════════════════════════════════════════════════"
echo ""

if [[ "$VCS" == "git" ]]; then
  # Show current branch
  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
  echo "Branch: $CURRENT_BRANCH"
  echo ""

  # Show git status
  git status

elif [[ "$VCS" == "jj" ]]; then
  # Show current change
  CURRENT_CHANGE=$(jj log -r @ --no-graph -T 'change_id.shortest()')
  echo "Current change: $CURRENT_CHANGE"
  echo ""

  # Show jj status
  jj status
fi

echo ""

if [[ "$ABORT_SUCCESS" == "true" ]]; then
  echo "✓ Abort Complete"
  echo ""
  echo "The repository is back to its state before the merge/rebase."
  echo "You can now proceed with other operations or retry the merge/rebase."
else
  echo "✗ Abort Failed"
  exit 1
fi

echo ""
```

## Safety Considerations

### Pre-Abort Verification

**Git operations:**
```bash
# Rebase in progress
[[ -d .git/rebase-merge ]] || [[ -d .git/rebase-apply ]]

# Merge in progress
[[ -f .git/MERGE_HEAD ]]
```

**Jj operations:**
```bash
# Conflict resolution in progress
jj status | grep -q "unresolved\|conflict"
```

### State After Abort

**Git:**
- All `.git/rebase-*` directories removed
- `.git/MERGE_HEAD` file removed
- Working directory returned to pre-operation state
- No staged changes related to merge/rebase

**Jj:**
- Current change abandoned (if in conflict resolution)
- Conflict markers removed
- Working copy returned to pre-conflict state

### No Operation in Progress

If no operation is detected, the command exits cleanly with no changes made.

## Error Handling

**Not in repository:**
```
ERROR: Not a git or jj repository
Exit with error code 1.
```

**Abort cancelled by user:**
```
Do you want to abort the [operation] operation? (y/N) n

Abort cancelled. Operation remains in progress.
Exit with code 0.
```

**Abort command failed:**
```
✗ Error aborting operation
Exit code: 1
Exit with error code 1.
```

**Repository not fully clean after abort:**
```
⚠ Warning: Repository may not be fully clean
Please review the status below
```

## Integration with Other Commands

**Before aborting:**
- Use `/merge-workflow:detect-conflicts` to analyze current conflicts
- Ensure you understand what will be discarded

**After aborting:**
- Repository is ready for new operations
- Can retry merge/rebase with: `/merge-workflow:merge` or `/merge-workflow:rebase`
- Can push to update remote: `git push origin <branch>`

## Example Workflow

### Aborting Git Rebase with Conflicts

```
VCS: git
Abort Workflow
════════════════════════════════════════════════════

Detected: Git rebase (interactive or regular) in progress

State Before Abort
════════════════════════════════════════════════════

Rebase Details:
  - Commits in rebase: 2 of 5
  - Conflicted files:
      src/app.js
      src/config.js

⚠ Warning: This will discard all changes from the in-progress operation

Do you want to abort the rebase-merge operation? (y/N) y

Aborting operation...
────────────────────────────────────────────────

Executing: git rebase --abort

✓ Operation aborted successfully

Verifying clean state...
────────────────────────────────────────────────

✓ Repository is clean

Final Status
════════════════════════════════════════════════════

Branch: feature-branch
On branch feature-branch
Your branch is behind 'origin/main' by 10 commits, and can be fast-forwarded.

✓ Abort Complete

The repository is back to its state before the merge/rebase.
You can now proceed with other operations or retry the merge/rebase.
```

### Aborting Git Merge

```
VCS: git
Abort Workflow
════════════════════════════════════════════════════

Detected: Git merge in progress

State Before Abort
════════════════════════════════════════════════════

Merge Details:
  - Merging commit: abc1234def5678
  - Conflicted files:
      package.json
      src/index.js

⚠ Warning: This will discard all changes from the in-progress operation

Do you want to abort the merge operation? (y/N) y

Aborting operation...
────────────────────────────────────────────────

Executing: git merge --abort

✓ Operation aborted successfully

Verifying clean state...
────────────────────────────────────────────────

✓ Repository is clean

Final Status
════════════════════════════════════════════════════

Branch: main
On branch main
Your branch is up to date with 'origin/main'.

✓ Abort Complete

The repository is back to its state before the merge/rebase.
You can now proceed with other operations or retry the merge/rebase.
```

### Aborting Jj Conflict Resolution

```
VCS: jj
Abort Workflow
════════════════════════════════════════════════════

Detected: Jj conflict resolution in progress

State Before Abort
════════════════════════════════════════════════════

Conflict Resolution Details:
  Working copy now at: abc12345

Conflicted files:
  - src/auth.js
  - src/utils.js

⚠ Warning: This will discard all changes from the in-progress operation

Do you want to abort the conflict-resolution operation? (y/N) y

Aborting operation...
────────────────────────────────────────────────

Executing: jj abandon

✓ Operation aborted successfully

Verifying clean state...
────────────────────────────────────────────────

✓ Repository is clean

Final Status
════════════════════════════════════════════════════

Current change: def67890

✓ Abort Complete

The repository is back to its state before the merge/rebase.
You can now proceed with other operations or retry the merge/rebase.
```

### No Operation in Progress

```
VCS: git
Abort Workflow
════════════════════════════════════════════════════

No merge or rebase operation detected

No operation in progress. Nothing to abort.

On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

## Command Reference

### Git Commands Used

```bash
# Check for rebase in progress (merge type)
[[ -d .git/rebase-merge ]]

# Check for rebase in progress (apply type)
[[ -d .git/rebase-apply ]]

# Check for merge in progress
[[ -f .git/MERGE_HEAD ]]

# List conflicted files
git diff --name-only --diff-filter=U

# Abort rebase
git rebase --abort

# Abort merge
git merge --abort

# Show status
git status

# Show current branch
git rev-parse --abbrev-ref HEAD
```

### Jj Commands Used

```bash
# Show status (includes conflict info)
jj status

# Show current change
jj log -r @ --no-graph -T 'change_id.shortest()'

# Show differences (includes conflict markers)
jj diff

# Abandon current change (for conflict resolution)
jj abandon

# Show summary (includes conflict details)
jj diff --summary
```
