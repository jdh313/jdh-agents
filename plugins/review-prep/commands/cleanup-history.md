---
description: Clean up git commit history by squashing and reordering commits (git only)
allowed-tools:
  - Bash(git:*)
  - Read
---

# Clean Up Commit History

Clean up your branch's commit history by squashing related commits and reordering commits into a logical sequence. This command uses non-interactive git rebase to safely reorganize commits before code review.

**Note:** This command is **git-only**. Jujutsu (jj) does not require commit squashing as it manages changes differently.

## Immediate Execution

**VCS Check:**
!`if [[ -d .jj ]]; then echo "ERROR: This command is git-only"; exit 1; elif [[ -d .git ]]; then echo "git repository detected"; else echo "Not a git repository"; exit 1; fi`

**Current Branch:**
!`git branch --show-current`

**Current Status:**
!`git status`

**Main Branch (for reference):**
!`git rev-parse --abbrev-ref origin/HEAD 2>/dev/null || git config --get init.defaultBranch || echo "main"`

## Instructions

This command helps you clean up your commit history before submitting for code review. Follow the steps below to reorganize and squash commits as needed.

### Step 1: Show Current Commit History

Display the commits on your branch that haven't been pushed to main yet. This gives you context for what can be cleaned up.

```bash
MAIN_BRANCH=$(git rev-parse --abbrev-ref origin/HEAD 2>/dev/null | sed 's@.*/@@' || git config --get init.defaultBranch || echo "main")
echo "Commits on your branch (since $MAIN_BRANCH):"
echo "=============================================="
git log --oneline $MAIN_BRANCH..HEAD | nl
echo ""
COMMIT_COUNT=$(git log --oneline $MAIN_BRANCH..HEAD | wc -l)
echo "Total commits: $COMMIT_COUNT"
```

**Expected output format:**
```
Commits on your branch (since main):
==================================================
1  a1b2c3d feat: add authentication module
2  d4e5f6g test: add auth tests
3  h7i8j9k fix: auth edge case
4  l0m1n2o chore: lint fixes
5  p3q4r5s feat: add password reset

Total commits: 5
```

### Step 2: Identify Squash Candidates

Look for commits that could be combined:

```bash
echo "Analyzing commit patterns..."
echo ""

# Check for commits with common patterns that might be squashable
echo "Potential squash candidates:"
echo "──────────────────────────────"

# Show any "fixup!" or "squash!" prefixed commits (these are autosquash markers)
FIXUP_COUNT=$(git log --oneline $MAIN_BRANCH..HEAD | grep -c "^.*fixup!\|^.*squash!" || true)
if [[ $FIXUP_COUNT -gt 0 ]]; then
  echo "Found $FIXUP_COUNT commits with fixup!/squash! prefixes (auto-squash ready)"
  git log --oneline $MAIN_BRANCH..HEAD | grep "fixup!\|squash!" || true
  echo ""
fi

# Show commits that modify the same files (candidates for squashing)
echo "Commits by file changes:"
git diff --name-only $MAIN_BRANCH..HEAD | sort | uniq -c | sort -rn | head -10
```

**What this shows:**
- Any "fixup!" or "squash!" prefixed commits (ready for autosquash)
- Files that were changed by multiple commits (potential candidates to squash)
- The structure helps identify related commits

### Step 3: Present Cleanup Options

Based on your commit history, present the following options:

```
Commit History Cleanup Options
════════════════════════════════════════════════════

Option A: Auto-squash fixup commits
  - Automatically squashes all commits prefixed with "fixup!" or "squash!"
  - Use if you've already prefixed related commits appropriately
  - Non-interactive, safe to run

Option B: Manual selection
  - Squash specific commits together
  - You specify which commits to combine
  - Requires careful input

Option C: Reorder commits
  - Change the order of commits in your branch
  - Define a new ordering (e.g., "2 1 3" to reorder)
  - Useful for logical grouping before review

Option D: Cancel
  - Exit without making changes

Select an option (a/b/c/d):
```

### Step 4: Execute Auto-Squash (Option A)

If the user selects Option A, execute the autosquash rebase:

```bash
MAIN_BRANCH=$(git rev-parse --abbrev-ref origin/HEAD 2>/dev/null | sed 's@.*/@@' || git config --get init.defaultBranch || echo "main")

echo "Starting auto-squash rebase..."
echo "This will squash all commits prefixed with fixup! or squash!"
echo ""

# Use non-interactive rebase with autosquash enabled
# GIT_SEQUENCE_EDITOR=: prevents opening an editor
GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash $MAIN_BRANCH

REBASE_EXIT=$?

if [[ $REBASE_EXIT -eq 0 ]]; then
  echo "✓ Auto-squash completed successfully"
else
  echo "✗ Auto-squash failed with exit code $REBASE_EXIT"
  echo ""
  echo "Check for rebase conflicts:"
  git status
  exit 1
fi
```

**Key details:**
- `GIT_SEQUENCE_EDITOR=:` makes the rebase completely non-interactive
- The `--autosquash` flag automatically reorders commits with "fixup!" prefixes
- If conflicts occur, the script exits and shows status

### Step 5: Execute Manual Selection (Option B)

If the user selects Option B, guide them through manual squashing:

```
Manual Squash Selection
════════════════════════════════════════════════════

You can squash commits in several ways:

Method 1: Combine consecutive commits (e.g., commits 3 and 4)
  Format: "3-4" or "3,4" to combine commits 3 through 4 into the first one

Method 2: Squash multiple separate commits
  Format: "1 3 5" to squash commits 1, 3, 5 into commit 1

Method 3: Reset and recommit
  Combines multiple commits by resetting to a base point

Which method would you prefer?
```

If user chooses to combine consecutive commits:

```bash
# Get the commit range from user (e.g., "3-4")
# For commits 3-4, find the actual hashes from the numbered list

# Get list of commits with numbers for reference
COMMITS=($(git log --oneline $MAIN_BRANCH..HEAD | awk '{print $1}'))

# Convert user selection (e.g., "3-4") to a range
# Then perform soft reset and recommit

echo "Getting commit range..."
# Extract the selected range, convert to git hashes

# Soft reset to an earlier point so all changes are staged
# Then recommit with a new message
```

**Alternative pattern - Using git reset soft:**

```bash
# For squashing commits 2 and 3 together:
BASE_COMMIT=$(git log --oneline $MAIN_BRANCH..HEAD | tail -1 | awk '{print $1}')  # First (oldest) commit
SQUASH_INTO=$(git log --oneline $MAIN_BRANCH..HEAD | sed -n '2p' | awk '{print $1}')  # Second commit

# Reset to before the commits to squash (soft keeps changes staged)
git reset --soft $BASE_COMMIT~1

# Recommit with all changes
git commit -m "feat: combined feature commits"
```

### Step 6: Execute Reorder (Option C)

If the user selects Option C, execute commit reordering:

```
Commit Reordering
════════════════════════════════════════════════════

Current commit order:
1  a1b2c3d  feat: add auth
2  d4e5f6g  test: add tests
3  h7i8j9k  fix: edge case

Enter new order (space-separated numbers, e.g., "2 3 1"):
```

When user provides new order (e.g., "2 3 1"):

```bash
MAIN_BRANCH=$(git rev-parse --abbrev-ref origin/HEAD 2>/dev/null | sed 's@.*/@@' || git config --get init.defaultBranch || echo "main")

# Validate user input is numeric and in range
USER_ORDER="2 3 1"  # Example from user

# Get original commits
COMMITS=($(git log --oneline $MAIN_BRANCH..HEAD | awk '{print $1}'))
COMMIT_COUNT=${#COMMITS[@]}

# Create a temporary script that will reorder commits
# GIT_SEQUENCE_EDITOR will use this script
TEMP_SCRIPT=$(mktemp)
cat > "$TEMP_SCRIPT" << 'EOF'
#!/bin/bash
# This script reorders the git rebase sequence
TODO_FILE=$1

# Read the original todo
mapfile -t ORIGINAL_TODOS < "$TODO_FILE"

# Rewrite with new order
: > "$TODO_FILE.new"
for NUM in $USER_ORDER; do
  IDX=$((NUM - 1))
  if [[ $IDX -ge 0 && $IDX -lt $COMMIT_COUNT ]]; then
    echo "${ORIGINAL_TODOS[$IDX]}" >> "$TODO_FILE.new"
  fi
done

# Replace original with reordered
mv "$TODO_FILE.new" "$TODO_FILE"
EOF

chmod +x "$TEMP_SCRIPT"

echo "Reordering commits: $USER_ORDER"
GIT_SEQUENCE_EDITOR="$TEMP_SCRIPT" git rebase -i $MAIN_BRANCH

REBASE_EXIT=$?
rm -f "$TEMP_SCRIPT"

if [[ $REBASE_EXIT -eq 0 ]]; then
  echo "✓ Commit reorder completed successfully"
else
  echo "✗ Commit reorder failed"
  echo "Check git status for details"
fi
```

### Step 7: Handle Rebase Conflicts

If rebase operations encounter conflicts, detect and guide the user:

```bash
# Check if rebase is in progress
if git status | grep -q "rebase in progress"; then
  echo "⚠️  REBASE IN PROGRESS"
  echo ""
  echo "A rebase operation has encountered conflicts."
  echo ""

  # Show conflicting files
  echo "Files with conflicts:"
  git status --short | grep "^UU\|^AA\|^DD\|^UD\|^DU" | awk '{print "  " $2}'
  echo ""

  echo "To resolve:"
  echo "  1. Edit the conflicting files to fix conflicts"
  echo "  2. Stage changes:  git add ."
  echo "  3. Continue rebase:  git rebase --continue"
  echo ""
  echo "To abort rebase:"
  echo "  git rebase --abort"
  echo ""

  exit 1
fi
```

### Step 8: Verify and Show Updated History

After successful cleanup, show the final result:

```bash
MAIN_BRANCH=$(git rev-parse --abbrev-ref origin/HEAD 2>/dev/null | sed 's@.*/@@' || git config --get init.defaultBranch || echo "main")

echo "Updated Commit History"
echo "════════════════════════════════════════════════════"
git log --oneline $MAIN_BRANCH..HEAD | nl
echo ""

NEW_COUNT=$(git log --oneline $MAIN_BRANCH..HEAD | wc -l)
ORIGINAL_COUNT=5  # From Step 1

echo "Summary:"
echo "  Original commits: $ORIGINAL_COUNT"
echo "  Updated commits:  $NEW_COUNT"
echo "  Net change:       $(($ORIGINAL_COUNT - $NEW_COUNT)) commits removed"
echo ""

echo "Current status:"
git status
```

**Expected output:**
```
Updated Commit History
════════════════════════════════════════════════════
1  x9y0z1a  feat: add authentication
2  b2c3d4e  feat: add password reset
3  f5g6h7i  test: comprehensive coverage

Summary:
  Original commits: 5
  Updated commits:  3
  Net change:       2 commits removed

Current status:
On branch feature/auth
Your branch and 'origin/main' have diverged...
```

## Safety Considerations

### History Rewriting Warning

```
⚠️  WARNING: COMMIT HISTORY REWRITING
────────────────────────────────────────

This operation rewrites commit history. Use ONLY on:
  ✓ Local branches not yet pushed
  ✓ Branches before submitting for review
  ✓ Branches where all collaborators are aware

DO NOT use on:
  ✗ Branches already pushed to remote (unless agreed by team)
  ✗ Main, master, or shared branches
  ✗ Branches with active collaborators

To check if your branch is pushed:
  git branch -vv

If your branch shows "origin/branch-name" as the tracked branch,
history has already been pushed. Rewriting will cause conflicts
for other developers.
```

### Rebase Conflict Handling

If conflicts occur during rebase:
1. The script pauses and shows conflicting files
2. Resolve conflicts manually in your editor
3. Run `git add .` to stage resolved files
4. Run `git rebase --continue` to resume
5. Repeat until rebase completes

**To safely abort:**
```bash
git rebase --abort
```

### Autosquash Prefix Conventions

If using Option A (autosquash), use these prefixes on commits you want to squash:

```bash
# To squash into previous commit (commits merge into previous)
git commit -m "fixup! feat: add authentication"

# To reword previous commit while squashing
git commit -m "squash! feat: add authentication"
```

The autosquash will reorder and squash these automatically.

## Error Handling

**Rebase fails with merge conflicts:**
- Shown in Step 7
- User must resolve manually or abort

**Not a git repository:**
```
Error: Not a git repository
Exit with clear message before attempting any operations
```

**Jujutsu repository detected:**
```
Error: This command is git-only
Jujutsu (jj) manages changes differently and doesn't require commit squashing
Exit immediately without proceeding
```

**Invalid user input (Option B or C):**
```
Error: Invalid selection. Please enter valid numbers or operations
Re-prompt the user to try again
```

**Commits already pushed:**
```
Warning: Your branch appears to be pushed to remote.
Rewriting history may cause issues for collaborators.
Proceed with caution.

To check: git branch -vv
```

## Best Practices

1. **Squash only before pushing**: Always clean up history before pushing
2. **Group logically**: Squash commits that represent a single logical change
3. **Test before cleanup**: Ensure tests pass before rewriting history
4. **Clear commit messages**: After squashing, ensure final commit messages are descriptive
5. **Review before pushing**: After cleanup, review the final history before pushing
6. **Don't squash main branches**: Never rewrite history on main, master, or develop

## Examples

**Example 1: Auto-squash with fixup commits**

```bash
# Before
1. feat: add authentication
2. fixup! feat: add authentication
3. fix: auth edge case
4. fixup! fix: auth edge case
5. test: add comprehensive tests

# After running Option A (auto-squash)
1. feat: add authentication
2. fix: auth edge case
3. test: add comprehensive tests
```

**Example 2: Manual squash (reduce 3 commits to 1)**

```bash
# Before
1. feat: module A
2. feat: module B
3. feat: module C

# After Option B selection (squash all into first)
1. feat: modules A, B, and C
```

**Example 3: Reorder commits**

```bash
# Before
1. test: add tests
2. chore: lint fixes
3. feat: new feature

# After Option C with input "3 1 2" (logical order: feature, tests, chores)
1. feat: new feature
2. test: add tests
3. chore: lint fixes
```
