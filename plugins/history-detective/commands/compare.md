---
description: Compare branches/changes to understand divergence and plan integration
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Read
---

# Compare Branches/Changes

Compare two branches (git) or changes (jj) to understand divergence, identify conflicts, and plan integration. Shows commit history, file changes, and a preview of what would be merged.

## Immediate Execution

**VCS Detection:**
!`[[ -d .jj ]] && echo "jj" || echo "git"`

**Current Status:**
!`if [[ -d .jj ]]; then jj status; else git status; fi`

## Instructions

Based on the detected VCS shown above, this command will guide you through comparing branches or changes with detailed divergence analysis.

### Step 1: Validate Repository State

**For git:**

Check that the repository is clean and we can perform comparisons:

```bash
if [[ ! -d .git ]]; then
  echo "Error: Not in a git repository."
  exit 1
fi

# Show current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"
```

**For jj:**

Check that we're in a valid jj workspace:

```bash
if [[ ! -d .jj ]]; then
  echo "Error: Not in a jj repository."
  exit 1
fi

# Show current change
CURRENT_CHANGE=$(jj log -T 'change_id.short()' --no-graph -r @ --limit 1)
echo "Current change: $CURRENT_CHANGE"
```

### Step 2: List Available Branches/Changes

**For git:**

List all available branches for comparison:

```bash
echo "=== Local Branches (sorted by recency) ==="
git for-each-ref --sort=-committerdate refs/heads/ --format='%(refname:short) | %(committerdate:short) | %(subject)'

echo ""
echo "=== Remote Branches (if any) ==="
git for-each-ref --sort=-committerdate refs/remotes/ --format='%(refname:short) | %(committerdate:short) | %(subject)' 2>/dev/null || echo "(no remote branches)"

echo ""
echo "Current branch: $CURRENT_BRANCH"
```

**For jj:**

List recent changes available for comparison:

```bash
echo "=== Recent Changes ==="
jj log -T 'change_id.short() ++ " | " ++ description.first_line()' --no-graph -r "ancestors(root())" --limit 15

echo ""
echo "Current change: $CURRENT_CHANGE"
```

### Step 3: Prompt for Source and Target

Prompt the user to specify which branches/changes to compare.

**For git:**

```bash
echo ""
read -p "Enter first branch name (or press Enter for current: $CURRENT_BRANCH): " BRANCH1
if [[ -z "$BRANCH1" ]]; then
  BRANCH1="$CURRENT_BRANCH"
fi

read -p "Enter second branch name (or press Enter for 'main'): " BRANCH2
if [[ -z "$BRANCH2" ]]; then
  BRANCH2="main"
  # Fallback if main doesn't exist
  if ! git show-ref --verify --quiet refs/heads/main; then
    if git show-ref --verify --quiet refs/heads/master; then
      BRANCH2="master"
    else
      echo "Error: Neither 'main' nor 'master' branch found."
      exit 1
    fi
  fi
fi

# Validate both branches exist
if ! git rev-parse --verify "$BRANCH1" > /dev/null 2>&1; then
  echo "Error: Branch '$BRANCH1' does not exist."
  exit 1
fi

if ! git rev-parse --verify "$BRANCH2" > /dev/null 2>&1; then
  echo "Error: Branch '$BRANCH2' does not exist."
  exit 1
fi

echo "Comparing $BRANCH1 <-> $BRANCH2"
```

**For jj:**

```bash
echo ""
read -p "Enter first change ID (or press Enter for current: $CURRENT_CHANGE): " CHANGE1
if [[ -z "$CHANGE1" ]]; then
  CHANGE1="$CURRENT_CHANGE"
fi

read -p "Enter second change ID (or press Enter for 'main'): " CHANGE2
if [[ -z "$CHANGE2" ]]; then
  CHANGE2="main"
fi

# Validate both changes exist
if ! jj log -r "$CHANGE1" > /dev/null 2>&1; then
  echo "Error: Change '$CHANGE1' does not exist."
  exit 1
fi

if ! jj log -r "$CHANGE2" > /dev/null 2>&1; then
  echo "Error: Change '$CHANGE2' does not exist."
  exit 1
fi

echo "Comparing $CHANGE1 <-> $CHANGE2"
```

### Step 4: Find Common Ancestor (Git Only)

**For git:**

Find the merge base (common ancestor) of both branches:

```bash
MERGE_BASE=$(git merge-base "$BRANCH1" "$BRANCH2")
echo ""
echo "=== Common Ancestor ==="
echo "Commit: $MERGE_BASE"
git log -1 "$MERGE_BASE" --format="%h | %ai | %s"
```

**For jj:**

jj doesn't use explicit merge bases like git. The comparison is relative to the repository root instead. Skip this step for jj.

### Step 5: Calculate Divergence

**For git:**

Count commits unique to each branch and show divergence:

```bash
echo ""
echo "=== Divergence Analysis ==="

# Count commits on each side
LEFT_RIGHT=$(git rev-list --left-right --count "$BRANCH1"..."$BRANCH2")
LEFT_COUNT=$(echo "$LEFT_RIGHT" | awk '{print $1}')
RIGHT_COUNT=$(echo "$LEFT_RIGHT" | awk '{print $2}')

echo "Commits ahead in $BRANCH1: $LEFT_COUNT"
echo "Commits ahead in $BRANCH2: $RIGHT_COUNT"

if [[ $LEFT_COUNT -eq 0 ]] && [[ $RIGHT_COUNT -eq 0 ]]; then
  echo ""
  echo "✓ Branches are identical (no divergence)"
elif [[ $LEFT_COUNT -eq 0 ]]; then
  echo ""
  echo "$BRANCH1 is BEHIND $BRANCH2 by $RIGHT_COUNT commits"
elif [[ $RIGHT_COUNT -eq 0 ]]; then
  echo ""
  echo "$BRANCH1 is AHEAD of $BRANCH2 by $LEFT_COUNT commits"
else
  echo ""
  echo "⚠ Both branches have diverged:"
  echo "  $BRANCH1 has $LEFT_COUNT unique commits"
  echo "  $BRANCH2 has $RIGHT_COUNT unique commits"
fi
```

**For jj:**

Show the relationship between changes:

```bash
echo ""
echo "=== Relationship Analysis ==="

# Check if CHANGE1 is ancestor of CHANGE2 or vice versa
if jj log -r "ancestors($CHANGE2) & $CHANGE1" > /dev/null 2>&1; then
  echo "$CHANGE1 is an ancestor of $CHANGE2"
elif jj log -r "ancestors($CHANGE1) & $CHANGE2" > /dev/null 2>&1; then
  echo "$CHANGE2 is an ancestor of $CHANGE1"
else
  echo "Changes have diverged (no ancestor relationship)"
fi
```

### Step 6: Show Commits Unique to Each Branch

**For git:**

Display commits that exist in one branch but not the other:

```bash
echo ""
echo "=== Commits in $BRANCH1 but not in $BRANCH2 ==="
git log "$BRANCH2".."$BRANCH1" --oneline --format="%h | %ai | %s" || echo "(none)"

echo ""
echo "=== Commits in $BRANCH2 but not in $BRANCH1 ==="
git log "$BRANCH1".."$BRANCH2" --oneline --format="%h | %ai | %s" || echo "(none)"
```

**For jj:**

Display changes in the range between two changes:

```bash
echo ""
echo "=== Changes between $CHANGE1 and $CHANGE2 ==="

# Show changes from CHANGE1 to CHANGE2
jj log -r "$CHANGE1"::$CHANGE2 -T 'change_id.short() ++ " | " ++ description.first_line()' || echo "(no changes in range)"
```

### Step 7: Collect File Change Summary

**For git:**

Get list of files changed between the two branches:

```bash
echo ""
echo "=== Files Changed (name-status) ==="
echo ""

# Use 3-dot range (symmetric difference) to show all files changed on either side
git diff --name-status "$BRANCH1"..."$BRANCH2" --find-renames

echo ""
echo "=== File Change Summary ==="
git diff --shortstat "$BRANCH1"..."$BRANCH2"
```

Status codes:
- `A` = Added (new file)
- `M` = Modified
- `D` = Deleted
- `R###` = Renamed (### shows similarity percentage)

**For jj:**

Get summary of file changes:

```bash
echo ""
echo "=== File Changes ==="

# Show summary of changes between the two changes
jj diff --from "$CHANGE1" --to "$CHANGE2" --summary
```

### Step 8: Show Detailed Change Statistics

**For git:**

Calculate comprehensive statistics on divergence:

```bash
echo ""
echo "=== Detailed Statistics ==="

# Per-file statistics showing impact
git diff --stat "$BRANCH1"..."$BRANCH2"

echo ""

# Overall statistics
git diff --shortstat "$BRANCH1"..."$BRANCH2"
```

**For jj:**

Show statistics for the comparison:

```bash
echo ""
echo "=== Detailed Statistics ==="

# Statistics for changes between the two revisions
jj diff --from "$CHANGE1" --to "$CHANGE2" --stat
```

### Step 9: Preview Merge Impact (Conflict Detection)

**For git:**

Check if merging would create conflicts:

```bash
echo ""
echo "=== Merge Preview ==="

# Do a dry-run merge to detect conflicts without actually merging
# Create a temporary merge commit to test
git merge-tree "$MERGE_BASE" "$BRANCH1" "$BRANCH2" > /tmp/merge_preview.txt 2>&1

# Check for conflicts in merge preview
if grep -q "<<<<<< " /tmp/merge_preview.txt; then
  echo "⚠ WARNING: Merging $BRANCH2 into $BRANCH1 would create CONFLICTS"
  echo ""
  echo "Conflicted files:"
  grep -E "^\+\+\+|<<<<<<" /tmp/merge_preview.txt | grep -B1 "<<<<<<" | head -20
else
  echo "✓ Merging $BRANCH2 into $BRANCH1 would complete without conflicts"
fi

rm -f /tmp/merge_preview.txt
```

**For jj:**

Check conflict status for the changes:

```bash
echo ""
echo "=== Merge Preview ==="

# Check if either change has conflicts
CHANGE1_CONFLICTS=$(jj log -r "$CHANGE1" -T 'if(conflict, "yes", "no")')
CHANGE2_CONFLICTS=$(jj log -r "$CHANGE2" -T 'if(conflict, "yes", "no")')

if [[ "$CHANGE1_CONFLICTS" == "yes" ]] || [[ "$CHANGE2_CONFLICTS" == "yes" ]]; then
  echo "⚠ One or more changes have conflicts"
  if [[ "$CHANGE1_CONFLICTS" == "yes" ]]; then
    echo "  $CHANGE1 has conflicts"
  fi
  if [[ "$CHANGE2_CONFLICTS" == "yes" ]]; then
    echo "  $CHANGE2 has conflicts"
  fi
else
  echo "✓ No conflicts detected in either change"
fi
```

### Step 10: Generate Comparison Report

**For git:**

Create a comprehensive comparison report:

```markdown
# Branch Comparison Report

## Summary

**Branches Compared:**
- Branch 1: $BRANCH1
- Branch 2: $BRANCH2
- Common Ancestor: $MERGE_BASE

**Divergence Status:**
- $BRANCH1 is ahead by: $LEFT_COUNT commits
- $BRANCH2 is ahead by: $RIGHT_COUNT commits

**File Statistics:**
- Files changed: <count>
- Lines added: <insertions>
- Lines removed: <deletions>
- Net change: +/- <net> lines

---

## Unique Commits

### In $BRANCH1 but not in $BRANCH2
<list of commits>

### In $BRANCH2 but not in $BRANCH1
<list of commits>

---

## Changed Files

<files with status codes>

---

## Merge Feasibility

**Can merge $BRANCH2 into $BRANCH1?**
<yes/no with conflict status>

**Recommendation:**
<Based on number of unique commits and conflicts>

---
```

**For jj:**

Create a comparison report for changes:

```markdown
# Change Comparison Report

## Summary

**Changes Compared:**
- Change 1: $CHANGE1
- Change 2: $CHANGE2

**Relationship:**
<ancestor/diverged>

**File Changes:**
<summary of changes>

---

## Changes Between

<list of changes in range>

---

## Merge Feasibility

**Status:**
<no conflicts / conflicts present>

---
```

### Step 11: Offer Detailed Diff View

After displaying the report, ask the user if they want to see detailed diffs:

```bash
echo ""
echo "Would you like to see detailed diffs? Choose an option:"
echo ""
echo "1. View diff of all changes"
echo "2. View diff of specific file"
echo "3. View unified diff (with context)"
echo "4. Skip detailed view"
echo ""
read -p "Enter choice (1-4): " DIFF_CHOICE

case "$DIFF_CHOICE" in
  1)
    # For git
    if [[ -d .git ]]; then
      echo ""
      echo "=== Full Diff ==="
      git diff "$BRANCH1"..."$BRANCH2"
    # For jj
    else
      echo ""
      echo "=== Full Diff ==="
      jj diff --from "$CHANGE1" --to "$CHANGE2"
    fi
    ;;
  2)
    # Prompt for specific file
    read -p "Enter filename (relative path): " FILENAME

    if [[ -d .git ]]; then
      git diff "$BRANCH1"..."$BRANCH2" -- "$FILENAME"
    else
      jj diff --from "$CHANGE1" --to "$CHANGE2" "$FILENAME"
    fi
    ;;
  3)
    # Show unified diff with more context
    if [[ -d .git ]]; then
      git diff -U5 "$BRANCH1"..."$BRANCH2"
    else
      jj diff --from "$CHANGE1" --to "$CHANGE2"
    fi
    ;;
  4)
    echo "Skipping detailed diff view."
    ;;
esac
```

### Step 12: Provide Next Steps

Guide the user based on the comparison results:

```bash
echo ""
echo "=== Next Steps ==="
echo ""

if [[ -d .git ]]; then
  if grep -q "<<<<<< " /tmp/merge_preview.txt 2>/dev/null; then
    echo "Conflicts detected. Consider:"
    echo "1. Review conflicted files: git diff --name-only --diff-filter=U"
    echo "2. Try a test merge: git merge --no-commit --no-ff $BRANCH2"
    echo "3. Use /merge-workflow:merge to merge with conflict guidance"
  else
    echo "No conflicts expected. You can:"
    echo "1. Merge the branch: git merge $BRANCH2"
    echo "2. Create a merge PR for code review"
    echo "3. Use /merge-workflow:merge for guided merging"
  fi
else
  if [[ "$CHANGE1_CONFLICTS" == "yes" ]] || [[ "$CHANGE2_CONFLICTS" == "yes" ]]; then
    echo "Conflicts present. Consider:"
    echo "1. Review conflict status: jj status"
    echo "2. Resolve conflicts in the change"
    echo "3. Use /merge-workflow:merge to create a merge change"
  else
    echo "No conflicts. You can:"
    echo "1. Create a merge change: jj new $CHANGE1 $CHANGE2"
    echo "2. Review the merged result"
    echo "3. Use /merge-workflow:merge for guided merging"
  fi
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

3. **Invalid comparison (same branch/change):**
   - Message: "Warning: Comparing a branch/change to itself will show no changes."
   - Allow user to proceed or cancel

4. **No common ancestor (jj):**
   - Message: "Warning: Changes have no common ancestor."
   - Continue with comparison

5. **Empty branch/change:**
   - Message: "No changes to compare (branches are identical)."
   - Exit gracefully

## Safety Considerations

1. **Read-only operations:** All commands are read-only. No modifications to repository state.
2. **No destructive actions:** Analysis only. No commits, resets, or merges.
3. **Merge preview only:** Uses `git merge-tree` for safe preview without side effects.
4. **Large repository handling:** Limits output for large change sets.
5. **Temporary file cleanup:** Remove temporary merge preview files after use.

## Example Output

### Git Example

```
Current branch: feature/new-auth

=== Local Branches (sorted by recency) ===
feature/new-auth | 2025-12-28 | Add authentication module
develop | 2025-12-27 | Merge PR #42
main | 2025-12-20 | Release v2.1.0

Current branch: feature/new-auth

Comparing feature/new-auth <-> main

=== Common Ancestor ===
Commit: abc1234f
abc1234 | 2025-12-15 10:30:00 | Fix API endpoint handling

=== Divergence Analysis ===
Commits ahead in feature/new-auth: 5
Commits ahead in main: 0

feature/new-auth is AHEAD of main by 5 commits

=== Commits in feature/new-auth but not in main ===
f5e6d7c | 2025-12-28 10:00:00 | Add OAuth2 provider support
e4d3c2b | 2025-12-27 15:45:00 | Add JWT token validation
d3c2b1a | 2025-12-27 12:30:00 | Add authentication middleware
c2b1a09 | 2025-12-26 18:00:00 | Add user session management
b1a0987 | 2025-12-25 14:30:00 | Add password hashing utilities

=== Commits in main but not in feature/new-auth ===
(none)

=== Files Changed (name-status) ===
A  src/auth/__init__.py
A  src/auth/oauth.py
A  src/auth/jwt_validator.py
A  src/auth/middleware.py
M  src/api/handler.py
M  src/config/settings.yaml
A  tests/test_auth.py
A  tests/test_oauth.py

=== File Change Summary ===
 8 files changed, 520 insertions(+), 45 deletions(-)

=== Detailed Statistics ===
 src/auth/__init__.py        |  20 ++++++++
 src/auth/oauth.py           | 150 ++++++++++++++++++++++++++++++++++++
 src/auth/jwt_validator.py   | 120 +++++++++++++++++++++++++++
 src/auth/middleware.py      |  95 ++++++++++++++++++++++++
 src/api/handler.py          |  45 +++++++----
 src/config/settings.yaml    |   8 ++-
 tests/test_auth.py          |  75 +++++++++++++++++++
 tests/test_oauth.py         |  70 +++++++++++++++++
 8 files changed, 520 insertions(+), 45 deletions(-)

=== Merge Preview ===
✓ Merging main into feature/new-auth would complete without conflicts

Would you like to see detailed diffs? Choose an option:

1. View diff of all changes
2. View diff of specific file
3. View unified diff (with context)
4. Skip detailed view

Enter choice (1-4): 4
Skipping detailed diff view.

=== Next Steps ===

No conflicts expected. You can:
1. Merge the branch: git merge main
2. Create a merge PR for code review
3. Use /merge-workflow:merge for guided merging
```

### Jj Example

```
Current change: a1b2c3d4

=== Recent Changes ===
a1b2c3d | Add OAuth2 provider support
f5e6d7c | Fix JWT token validation
e4d3c2b | Add authentication middleware
d3c2b1a | Add user session management
c2b1a09 | Add password hashing

Current change: a1b2c3d4

Comparing a1b2c3d4 <-> main

=== Relationship Analysis ===
a1b2c3d4 is an ancestor of main

=== Changes between a1b2c3d4 and main ===
f5e6d7c | Refactor API layer
e4d3c2b | Update dependencies
d3c2b1a | Add documentation

=== File Changes ===
A  src/auth/oauth.py
M  src/api/handler.py
M  config/settings.yaml

=== Detailed Statistics ===
 src/auth/oauth.py      | 150 +++++++++++++++
 src/api/handler.py     |  45 ++++---
 config/settings.yaml   |   8 +-
 3 files changed, 185 insertions(+), 18 deletions(-)

=== Merge Preview ===
✓ No conflicts detected in either change

=== Next Steps ===

No conflicts. You can:
1. Create a merge change: jj new a1b2c3d4 main
2. Review the merged result
3. Use /merge-workflow:merge for guided merging
```

## Related Commands

- `/merge-workflow:merge` - Execute a merge with conflict detection and guidance
- `/merge-workflow:detect-conflicts` - Analyze conflicts in detail
- `/review-prep:analyze-diff` - Comprehensive diff analysis for code review
