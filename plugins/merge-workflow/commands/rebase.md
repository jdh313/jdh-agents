---
description: Rebase current branch (git) or change (jj) onto main/master with conflict detection
argument-hint: [target-branch]
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Bash([[:*)
  - Bash(if:*)
  - Read
---

# Rebase

Rebase the current branch (git) or change (jj) onto the main/master branch with automatic conflict detection and guidance for resolution.

**Supports:** Both git and jj repositories.

## Immediate Execution

**VCS Detection:**
!`[[ -d .jj ]] && echo "VCS: jj" || echo "VCS: git"`

**Current Status:**
!`if [[ -d .jj ]]; then jj status; elif [[ -d .git ]]; then git status; fi`

**Current Branch/Change:**
!`if [[ -d .jj ]]; then jj log -r @ --no-graph -T 'change_id.shortest()'; elif [[ -d .git ]]; then git rev-parse --abbrev-ref HEAD; fi`

## Instructions

This command rebases your current branch (git) or change (jj) onto the main/master branch, automatically detecting conflicts and guiding you through resolution if needed.

### Step 1: Detect VCS and Validate Repository State

First, determine which VCS is in use and check the current state:

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
echo "Rebase Workflow"
echo "════════════════════════════════════════════════════"
echo ""
```

### Step 2: Get Current Branch/Change Information

Display what will be rebased:

```bash
if [[ "$VCS" == "git" ]]; then
  # Get current branch
  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

  if [[ "$CURRENT_BRANCH" == "HEAD" ]]; then
    echo "ERROR: Detached HEAD state detected"
    echo "Cannot rebase from detached HEAD"
    exit 1
  fi

  echo "Current branch: $CURRENT_BRANCH"

  # Check for uncommitted changes
  if ! git diff-index --quiet HEAD --; then
    echo ""
    echo "⚠ Warning: Uncommitted changes detected"
    echo ""
    git diff-index --name-only HEAD -- | sed 's/^/  - /'
    echo ""
    echo "ERROR: Cannot rebase with uncommitted changes"
    echo "Stash or commit your changes first:"
    echo "  git stash"
    exit 1
  fi

  echo "Status: Working directory clean"

elif [[ "$VCS" == "jj" ]]; then
  # Get current change
  CURRENT_CHANGE=$(jj log -r @ --no-graph -T 'change_id.shortest()')

  echo "Current change: $CURRENT_CHANGE"

  # Jj automatically includes uncommitted changes in the change
  # No need to check for uncommitted state
  echo "Status: Ready to rebase (jj includes working changes)"
fi

echo ""
```

### Step 3: Identify Target Branch

Determine which branch to rebase onto:

```bash
if [[ "$VCS" == "git" ]]; then
  # Check for origin/main or origin/master
  TARGET_BRANCH=""

  if git rev-parse --verify origin/main >/dev/null 2>&1; then
    TARGET_BRANCH="origin/main"
  elif git rev-parse --verify origin/master >/dev/null 2>&1; then
    TARGET_BRANCH="origin/master"
  elif git rev-parse --verify main >/dev/null 2>&1; then
    TARGET_BRANCH="main"
  elif git rev-parse --verify master >/dev/null 2>&1; then
    TARGET_BRANCH="master"
  else
    echo "ERROR: Could not find main or master branch"
    echo "Available branches:"
    git branch -a | sed 's/^/  /'
    exit 1
  fi

  echo "Target branch: $TARGET_BRANCH"
  echo ""

  # Fetch to get latest remote state
  echo "Fetching latest from remote..."
  git fetch origin >/dev/null 2>&1

  if [[ $? -ne 0 ]]; then
    echo "⚠ Warning: git fetch failed (continuing with local state)"
  else
    echo "✓ Fetch completed"
  fi

elif [[ "$VCS" == "jj" ]]; then
  # For jj, rebase destination is typically "main"
  TARGET_BRANCH="main"

  echo "Target branch: $TARGET_BRANCH"
  echo ""

  # Jj doesn't require explicit fetch, uses local state
  echo "Status: Ready to rebase onto $TARGET_BRANCH"
fi

echo ""
```

### Step 4: Execute Rebase

Perform the rebase operation:

```bash
if [[ "$VCS" == "git" ]]; then
  echo "Executing: git rebase $TARGET_BRANCH --no-edit"
  echo "────────────────────────────────────────────────"
  echo ""

  git rebase "$TARGET_BRANCH"   REBASE_EXIT=$?

  if [[ $REBASE_EXIT -eq 0 ]]; then
    echo ""
    echo "✓ Rebase completed successfully"

  else
    echo ""
    echo "⚠ Rebase encountered conflicts"
    REBASE_EXIT_CODE=$REBASE_EXIT
  fi

elif [[ "$VCS" == "jj" ]]; then
  echo "Executing: jj rebase -d $TARGET_BRANCH"
  echo "────────────────────────────────────────────────"
  echo ""

  jj rebase -d "$TARGET_BRANCH"
  REBASE_EXIT=$?

  if [[ $REBASE_EXIT -eq 0 ]]; then
    echo ""
    echo "✓ Rebase completed successfully"

  else
    echo ""
    echo "⚠ Rebase encountered conflicts"
    REBASE_EXIT_CODE=$REBASE_EXIT
  fi
fi

echo ""
```

### Step 5: Check for Conflicts

Detect if conflicts were introduced by the rebase:

```bash
CONFLICTS_DETECTED=false

if [[ "$VCS" == "git" ]]; then
  # Check for merge/rebase in progress state
  if [[ -d .git/rebase-merge ]] || [[ -d .git/rebase-apply ]]; then
    echo "Detected: Git rebase in progress with conflicts"

    # Check for unmerged files
    if git diff --name-only --diff-filter=U 2>/dev/null | grep -q .; then
      CONFLICTS_DETECTED=true
    fi
  fi

elif [[ "$VCS" == "jj" ]]; then
  # Check for conflicts in the current change
  if jj diff --summary 2>/dev/null | grep -q "conflicted"; then
    CONFLICTS_DETECTED=true
  fi

  # Also check for conflict markers in modified files
  if jj diff 2>/dev/null | grep -q "^<<<<<<< "; then
    CONFLICTS_DETECTED=true
  fi
fi

echo ""
```

### Step 6: Handle Rebase Result

Display result and provide next steps:

```bash
echo "Rebase Result"
echo "════════════════════════════════════════════════════"
echo ""

if [[ "$CONFLICTS_DETECTED" == "true" ]]; then
  echo "⚠ CONFLICTS DETECTED"
  echo ""

  if [[ "$VCS" == "git" ]]; then
    echo "Conflicted files:"
    git diff --name-only --diff-filter=U | sed 's/^/  - /'

  elif [[ "$VCS" == "jj" ]]; then
    echo "Conflicted files:"
    jj diff --summary 2>/dev/null | grep -E "^\s+[MA]\s+" | awk '{print $2}' | while read file; do
      if grep -q "^<<<<<<<" "$file" 2>/dev/null; then
        echo "  - $file"
      fi
    done
  fi

  echo ""
  echo "Conflicts must be resolved before continuing."
  echo ""
  echo "Recommended next steps:"
  echo "1. Use /merge-workflow:detect-conflicts to analyze conflicts"
  echo "2. Use /merge-workflow:resolve-conflicts to resolve them"
  echo ""

  if [[ "$VCS" == "git" ]]; then
    echo "Or to abort the rebase:"
    echo "  git rebase --abort"
  fi

  echo ""
  exit 1

elif [[ $REBASE_EXIT_CODE -ne 0 ]]; then
  # Rebase failed but no conflicts detected
  echo "✗ Rebase failed"
  echo ""

  if [[ "$VCS" == "git" ]]; then
    echo "Error output:"
    git status
    echo ""
    echo "To abort rebase:"
    echo "  git rebase --abort"
  fi

  exit 1

else
  # Rebase successful, no conflicts
  echo "✓ Rebase Successful"
  echo ""

  if [[ "$VCS" == "git" ]]; then
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    COMMIT_COUNT=$(git rev-list --count $TARGET_BRANCH..)

    echo "Branch: $CURRENT_BRANCH"
    echo "Commits ahead of $TARGET_BRANCH: $COMMIT_COUNT"
    echo ""
    echo "Status: Ready to push or continue development"

    if [[ $COMMIT_COUNT -gt 0 ]]; then
      echo ""
      echo "To push rebase:"
      echo "  git push -f origin $CURRENT_BRANCH"
      echo ""
      echo "⚠ Note: Force push required because rebase rewrites history"
    fi

  elif [[ "$VCS" == "jj" ]]; then
    echo "Current change:"
    jj log -r @ --no-graph -T 'description ++ "\n"'
    echo ""
    echo "Status: Working copy updated with rebased changes"
  fi
fi

echo ""
```

### Step 7: Display Final Status

Show the current state after rebase:

```bash
echo "Final Status"
echo "════════════════════════════════════════════════════"
echo ""

if [[ "$VCS" == "git" ]]; then
  git status

elif [[ "$VCS" == "jj" ]]; then
  jj status
fi

echo ""
```

## Safety Considerations

### Pre-Rebase Checks (Git Only)

**Git requires clean working directory:**
```bash
# Check for uncommitted changes
git diff-index --quiet HEAD --

# This prevents loss of uncommitted work
# Stash or commit changes before rebasing
```

**Jj automatically includes working changes** in the current change, so no stash is required.

### Conflict Detection

**Git:** Uses `.git/rebase-merge` or `.git/rebase-apply` directories to detect active rebase with conflicts

**Jj:** Checks for conflict markers (`^<<<<<<<`) in modified files

### Reversibility

**Git:**
```bash
# Abort rebase before completion
git rebase --abort

# Revert to pre-rebase state with reflog
git reflog
git reset --hard HEAD@{X}
```

**Jj:**
```bash
# Undo last operation (including rebase)
jj undo

# View change history
jj log
```

### Force Push Warning

After rebasing, git will require force-push to update remote branch:
```bash
# Rebase rewrites history, so force push is necessary
git push -f origin <branch>

# Be cautious with force push on shared branches
```

## Error Handling

**Not in repository:**
```
ERROR: Not a git or jj repository
Exit with error code 1.
```

**Detached HEAD (git only):**
```
ERROR: Detached HEAD state detected
Cannot rebase from detached HEAD
Exit with error code 1.
```

**Uncommitted changes (git only):**
```
⚠ Warning: Uncommitted changes detected
ERROR: Cannot rebase with uncommitted changes
Stash or commit your changes first:
  git stash
Exit with error code 1.
```

**Target branch not found:**
```
ERROR: Could not find main or master branch
Available branches:
  [list of branches]
Exit with error code 1.
```

**Rebase fails with conflicts:**
```
⚠ Rebase encountered conflicts
Conflicted files:
  - src/file1.js
  - src/file2.js

Conflicts must be resolved before continuing.
Recommended next steps:
1. Use /merge-workflow:detect-conflicts to analyze conflicts
2. Use /merge-workflow:resolve-conflicts to resolve them

Exit with error code 1.
```

**Network/fetch failure:**
```
⚠ Warning: git fetch failed (continuing with local state)
Rebase will proceed with local branches
```

## Performance Considerations

**Large repositories:**
- Git rebase may take time with many commits
- Progress is shown during rebase process
- Jj rebase is typically faster for large changes

**Shallow clones:**
- May have missing commits if rebasing onto remote branch
- Full clone recommended for large rebases

## Integration with Other Commands

**Before rebase:**
- Use `/merge-workflow:detect-conflicts` to check current state
- Ensure you're on correct branch with: `git status` or `jj status`

**After successful rebase:**
- Git: Ready to push with `git push -f origin <branch>`
- Jj: Ready to continue development or create new change

**If conflicts occur:**
- Use `/merge-workflow:detect-conflicts` to analyze conflict types
- Use `/merge-workflow:resolve-conflicts` to resolve them interactively
- Rebase completes automatically after conflict resolution

## Example Workflow

### Successful Git Rebase (No Conflicts)

```
VCS: git
Rebase Workflow
════════════════════════════════════════════════════

Current branch: feature-auth
Status: Working directory clean

Target branch: origin/main

Fetching latest from remote...
✓ Fetch completed

Executing: git rebase origin/main ────────────────────────────────────────────────

✓ Rebase completed successfully

Rebase Result
════════════════════════════════════════════════════

✓ Rebase Successful

Branch: feature-auth
Commits ahead of origin/main: 3

Status: Ready to push or continue development

To push rebase:
  git push -f origin feature-auth

⚠ Note: Force push required because rebase rewrites history

Final Status
════════════════════════════════════════════════════

On branch feature-auth
Your branch is ahead of 'origin/main' by 3 commits.
```

### Git Rebase with Conflicts

```
VCS: git
Rebase Workflow
════════════════════════════════════════════════════

Current branch: feature-ui
Status: Working directory clean

Target branch: origin/main

Fetching latest from remote...
✓ Fetch completed

Executing: git rebase origin/main ────────────────────────────────────────────────

⚠ Rebase encountered conflicts

Rebase Result
════════════════════════════════════════════════════

⚠ CONFLICTS DETECTED

Conflicted files:
  - src/components/Button.jsx
  - src/styles/button.css

Conflicts must be resolved before continuing.

Recommended next steps:
1. Use /merge-workflow:detect-conflicts to analyze conflicts
2. Use /merge-workflow:resolve-conflicts to resolve them

Or to abort the rebase:
  git rebase --abort
```

### Jj Rebase Success

```
VCS: jj
Rebase Workflow
════════════════════════════════════════════════════

Current change: abc12345

Target branch: main
Status: Ready to rebase (jj includes working changes)

Executing: jj rebase -d main
────────────────────────────────────────────────

✓ Rebase completed successfully

Rebase Result
════════════════════════════════════════════════════

✓ Rebase Successful

Current change:
Add authentication feature

Status: Working copy updated with rebased changes

Final Status
════════════════════════════════════════════════════

Working copy now at: abc12345
Parent commit: main (origin/main)
```

## Command Reference

### Git Commands Used

```bash
# Get current branch
git rev-parse --abbrev-ref HEAD

# Check for uncommitted changes
git diff-index --quiet HEAD --

# Check for target branch
git rev-parse --verify origin/main

# Fetch latest
git fetch origin

# Execute rebase
git rebase origin/main 
# List conflicted files
git diff --name-only --diff-filter=U

# Check rebase state
[[ -d .git/rebase-merge ]] || [[ -d .git/rebase-apply ]]

# Show status
git status

# Abort rebase
git rebase --abort

# Push rebased branch (requires force)
git push -f origin <branch>
```

### Jj Commands Used

```bash
# Get current change
jj log -r @ --no-graph -T 'change_id.shortest()'

# Execute rebase
jj rebase -d main

# Check for conflicts
jj diff --summary

# Show conflicts in diff
jj diff

# Show status
jj status

# Undo rebase
jj undo

# View change log
jj log
```
