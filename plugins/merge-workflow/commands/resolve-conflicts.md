---
description: Guided conflict resolution workflow for git and jj repositories
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Read
  - Edit
  - AskUserQuestion
---

# Resolve Conflicts

Guided conflict resolution workflow that walks you through resolving merge/rebase conflicts one file at a time. This command presents each conflict with context and offers strategic resolution options (accept ours, accept theirs, manual edit, or skip).

**Supports:** Both git and jj repositories.

## Immediate Execution

**VCS Detection:**
!`if [[ -d .jj ]]; then echo "VCS: jj"; elif [[ -d .git ]]; then echo "VCS: git"; else echo "ERROR: Not a git or jj repository"; exit 1; fi`

**Current Status:**
!`if [[ -d .jj ]]; then jj status; elif [[ -d .git ]]; then git status; fi`

**Conflict Check:**
!`if [[ -d .jj ]]; then jj diff --summary 2>/dev/null | grep -q "conflict" && echo "Conflicts detected" || echo "No conflicts detected"; elif [[ -d .git ]]; then git diff --name-only --diff-filter=U 2>/dev/null | grep -q . && echo "Conflicts detected" || echo "No conflicts detected"; fi`

## Instructions

This command provides a guided workflow for resolving merge or rebase conflicts one file at a time. It shows you each conflict with context and offers resolution strategies.

### Step 1: Detect VCS and List Conflicted Files

First, determine which VCS is in use and identify all files with conflicts:

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
echo "Conflict Resolution Workflow"
echo "════════════════════════════════════════════════════"
echo ""

# List conflicted files
if [[ "$VCS" == "git" ]]; then
  # Git: files with merge conflicts have U status
  CONFLICTED_FILES=$(git diff --name-only --diff-filter=U 2>/dev/null)

  if [[ -z "$CONFLICTED_FILES" ]]; then
    echo "No conflicts detected in git repository"
    echo "Status: Ready to continue"
    exit 0
  fi

  FILE_COUNT=$(echo "$CONFLICTED_FILES" | wc -l | tr -d ' ')
  echo "Found $FILE_COUNT conflicted file(s) in git repository"
  echo ""
  echo "Conflicted files:"
  echo "$CONFLICTED_FILES" | sed 's/^/  - /'

elif [[ "$VCS" == "jj" ]]; then
  # Jj: conflicts are marked in working copy with conflict markers
  # Check if any files have conflict markers
  CONFLICTED_FILES=$(jj diff --summary 2>/dev/null | grep -E "^\s+[MA]\s+" | awk '{print $2}' | while read file; do
    if grep -q "^<<<<<<<" "$file" 2>/dev/null; then
      echo "$file"
    fi
  done)

  if [[ -z "$CONFLICTED_FILES" ]]; then
    echo "No conflicts detected in jj repository"
    echo "Status: Working copy clean"
    exit 0
  fi

  FILE_COUNT=$(echo "$CONFLICTED_FILES" | wc -l | tr -d ' ')
  echo "Found $FILE_COUNT conflicted file(s) in jj repository"
  echo ""
  echo "Conflicted files:"
  echo "$CONFLICTED_FILES" | sed 's/^/  - /'
fi

echo ""
```

**Expected output:**
```
VCS: Git
Conflict Resolution Workflow
════════════════════════════════════════════════════
Found 3 conflicted file(s) in git repository

Conflicted files:
  - src/auth.js
  - tests/auth.test.js
  - README.md
```

### Step 2: Begin Per-File Resolution Loop

For each conflicted file, resolve conflicts one at a time. This step processes a single file and should be repeated for each remaining conflict.

#### 2a. Select Next Conflicted File

```bash
# Get first conflicted file from list
CURRENT_FILE=$(echo "$CONFLICTED_FILES" | head -1)

# Calculate position in list
FILE_INDEX=1
TOTAL_FILES=$FILE_COUNT

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Resolving: $CURRENT_FILE (file $FILE_INDEX of $TOTAL_FILES)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
```

#### 2b. Show Conflict Context

Display the conflict with clear labeling of "ours" vs "theirs":

```bash
echo "Conflict Details"
echo "────────────────────────────────────────────────"

if [[ "$VCS" == "git" ]]; then
  # Git: Show conflict with context using diff
  echo ""
  echo "Full conflict context (with markers):"
  echo ""
  git diff "$CURRENT_FILE" | head -100

  # Check if output is very long
  DIFF_LINES=$(git diff "$CURRENT_FILE" | wc -l | tr -d ' ')
  if [[ $DIFF_LINES -gt 100 ]]; then
    echo ""
    echo "... (showing first 100 of $DIFF_LINES lines)"
    echo "Use option (d) to see full file"
  fi

elif [[ "$VCS" == "jj" ]]; then
  # Jj: Show conflict context
  echo ""
  echo "Full conflict context (with markers):"
  echo ""
  jj diff "$CURRENT_FILE" | head -100

  # Check if output is very long
  DIFF_LINES=$(jj diff "$CURRENT_FILE" | wc -l | tr -d ' ')
  if [[ $DIFF_LINES -gt 100 ]]; then
    echo ""
    echo "... (showing first 100 of $DIFF_LINES lines)"
    echo "Use option (d) to see full file"
  fi
fi

echo ""
```

#### 2c. Parse and Display Conflict Sections

Extract and display the conflicting versions clearly:

```bash
echo "Conflict Summary"
echo "────────────────────────────────────────────────"
echo ""

# Read the file and extract first conflict
if [[ -f "$CURRENT_FILE" ]]; then
  # Extract conflict markers
  CONFLICT_START=$(grep -n "^<<<<<<<" "$CURRENT_FILE" 2>/dev/null | head -1 | cut -d: -f1)

  if [[ -n "$CONFLICT_START" ]]; then
    # Find conflict boundaries
    CONFLICT_MIDDLE=$(tail -n +$CONFLICT_START "$CURRENT_FILE" | grep -n "^=======" | head -1 | cut -d: -f1)
    CONFLICT_END=$(tail -n +$CONFLICT_START "$CURRENT_FILE" | grep -n "^>>>>>>>" | head -1 | cut -d: -f1)

    if [[ -n "$CONFLICT_MIDDLE" && -n "$CONFLICT_END" ]]; then
      # Calculate actual line numbers
      MIDDLE_LINE=$((CONFLICT_START + CONFLICT_MIDDLE - 1))
      END_LINE=$((CONFLICT_START + CONFLICT_END - 1))

      echo "[OURS - current branch/change]"
      sed -n "$((CONFLICT_START + 1)),$((MIDDLE_LINE - 1))p" "$CURRENT_FILE"

      echo ""
      echo "[THEIRS - incoming branch/change]"
      sed -n "$((MIDDLE_LINE + 1)),$((END_LINE - 1))p" "$CURRENT_FILE"

      # Count total conflicts in file
      TOTAL_CONFLICTS=$(grep -c "^<<<<<<<" "$CURRENT_FILE" 2>/dev/null || echo "0")

      if [[ $TOTAL_CONFLICTS -gt 1 ]]; then
        echo ""
        echo "Note: This file has $TOTAL_CONFLICTS conflict(s) total"
        echo "      (showing first conflict above)"
      fi
    fi
  fi
fi

echo ""
```

**Expected output:**
```
Conflict Summary
────────────────────────────────────────────────
[OURS - current branch/change]
function authenticate(user, password) {
  return hashPassword(password) === user.passwordHash;
}

[THEIRS - incoming branch/change]
function authenticate(user, password) {
  const hash = await hashPasswordAsync(password);
  return hash === user.passwordHash;
}

Note: This file has 2 conflict(s) total
      (showing first conflict above)
```

#### 2d. Present Resolution Options

Show the user their choices for resolving this conflict:

```bash
echo "Resolution Options"
echo "────────────────────────────────────────────────"
echo ""
echo "(a) Accept OURS     - Keep current branch/change version"
echo "(b) Accept THEIRS   - Take incoming branch/change version"
echo "(c) Edit manually   - Open file for manual conflict resolution"
echo "(d) Show full file  - Display entire file with all conflicts"
echo "(s) Skip this file  - Resolve later, move to next file"
echo "(q) Quit            - Exit resolution workflow (can resume later)"
echo ""
```

#### 2e. Get User Choice and Execute Resolution

Prompt for user selection and execute the chosen strategy:

```bash
# Prompt for user choice
read -p "Select option (a/b/c/d/s/q): " CHOICE

case "$CHOICE" in
  a|A)
    echo ""
    echo "Resolving: Accept OURS (current branch/change)"
    echo "────────────────────────────────────────────────"

    if [[ "$VCS" == "git" ]]; then
      # Git: checkout --ours and stage
      git checkout --ours "$CURRENT_FILE"
      if [[ $? -eq 0 ]]; then
        git add "$CURRENT_FILE"
        echo "✓ Accepted OURS and staged: $CURRENT_FILE"
      else
        echo "✗ Failed to accept OURS for: $CURRENT_FILE"
        exit 1
      fi

    elif [[ "$VCS" == "jj" ]]; then
      # Jj: resolve with :ours tool
      jj resolve --tool=:ours "$CURRENT_FILE"
      if [[ $? -eq 0 ]]; then
        echo "✓ Accepted OURS: $CURRENT_FILE"
      else
        echo "✗ Failed to accept OURS for: $CURRENT_FILE"
        exit 1
      fi
    fi
    ;;

  b|B)
    echo ""
    echo "Resolving: Accept THEIRS (incoming branch/change)"
    echo "────────────────────────────────────────────────"

    if [[ "$VCS" == "git" ]]; then
      # Git: checkout --theirs and stage
      git checkout --theirs "$CURRENT_FILE"
      if [[ $? -eq 0 ]]; then
        git add "$CURRENT_FILE"
        echo "✓ Accepted THEIRS and staged: $CURRENT_FILE"
      else
        echo "✗ Failed to accept THEIRS for: $CURRENT_FILE"
        exit 1
      fi

    elif [[ "$VCS" == "jj" ]]; then
      # Jj: resolve with :theirs tool
      jj resolve --tool=:theirs "$CURRENT_FILE"
      if [[ $? -eq 0 ]]; then
        echo "✓ Accepted THEIRS: $CURRENT_FILE"
      else
        echo "✗ Failed to accept THEIRS for: $CURRENT_FILE"
        exit 1
      fi
    fi
    ;;

  c|C)
    echo ""
    echo "Manual Edit Mode"
    echo "────────────────────────────────────────────────"
    echo ""
    echo "File: $CURRENT_FILE"
    echo ""
    echo "Instructions:"
    echo "1. The file will be displayed below with Read tool"
    echo "2. Review the conflict markers:"
    echo "   <<<<<<< (ours/current)"
    echo "   ======= (separator)"
    echo "   >>>>>>> (theirs/incoming)"
    echo "3. Use Edit tool to resolve conflicts manually"
    echo "4. Remove all conflict markers (<<<<<<<, =======, >>>>>>>)"
    echo "5. Keep the desired code or merge both versions"
    echo ""
    echo "Reading file for manual resolution..."

    # Note: The actual file read and edit will be done by Claude using Read and Edit tools
    # This section provides guidance for manual resolution
    echo ""
    echo "After editing, the file will be marked as resolved."

    if [[ "$VCS" == "git" ]]; then
      echo ""
      echo "After Edit tool completes, stage the file:"
      echo "  git add $CURRENT_FILE"
    elif [[ "$VCS" == "jj" ]]; then
      echo ""
      echo "After Edit tool completes, the file is automatically tracked."
      echo "Jj will reflect the resolved state in working copy."
    fi

    # Pause for manual resolution - in practice, Claude will use Read + Edit here
    echo ""
    echo "→ Use Read tool to view: $CURRENT_FILE"
    echo "→ Use Edit tool to resolve conflicts"
    echo "→ Remove all conflict markers before continuing"
    ;;

  d|D)
    echo ""
    echo "Full File Contents"
    echo "────────────────────────────────────────────────"
    echo ""

    # Show entire file with conflict markers
    if [[ "$VCS" == "git" ]]; then
      echo "File: $CURRENT_FILE (git diff output)"
      echo ""
      git diff "$CURRENT_FILE"
    elif [[ "$VCS" == "jj" ]]; then
      echo "File: $CURRENT_FILE (jj diff output)"
      echo ""
      jj diff "$CURRENT_FILE"
    fi

    echo ""
    echo "After reviewing, re-run this command to resolve."
    exit 0
    ;;

  s|S)
    echo ""
    echo "Skipping: $CURRENT_FILE"
    echo "────────────────────────────────────────────────"
    echo "File will remain conflicted. Resolve later."
    echo ""
    echo "To resume: Run this command again"
    echo ""
    # Continue to next file (in a loop implementation)
    ;;

  q|Q)
    echo ""
    echo "Exiting Conflict Resolution"
    echo "════════════════════════════════════════════════"
    echo ""
    echo "Status: Partial resolution"
    echo "Remaining conflicts: Check with status command"
    echo ""
    echo "To resume: Run this command again"
    echo ""

    if [[ "$VCS" == "git" ]]; then
      echo "Current git status:"
      git status --short
    elif [[ "$VCS" == "jj" ]]; then
      echo "Current jj status:"
      jj status
    fi
    exit 0
    ;;

  *)
    echo ""
    echo "Invalid option: $CHOICE"
    echo "Please select a, b, c, d, s, or q"
    exit 1
    ;;
esac

echo ""
```

#### 2f. For Manual Edit Option (c): Guide Through Resolution

When option (c) is selected, provide detailed guidance and use Read/Edit tools:

```bash
# This section is executed when user selects option (c)
# Claude will perform these steps using available tools

echo "Step 1: Read the conflicted file"
echo "────────────────────────────────────────────────"
# Use Read tool: Read(file_path="$CURRENT_FILE")

echo ""
echo "Step 2: Identify conflict sections"
echo "────────────────────────────────────────────────"
echo "Look for these markers in the file:"
echo "  <<<<<<< HEAD (or branch name) - Start of OURS section"
echo "  ======= - Separator between versions"
echo "  >>>>>>> branch-name - End of THEIRS section"

echo ""
echo "Step 3: Resolve conflicts with Edit tool"
echo "────────────────────────────────────────────────"
echo "For each conflict block:"
echo "  1. Decide which version to keep (ours, theirs, or both)"
echo "  2. Remove the conflict markers (<<<, ===, >>>)"
echo "  3. Keep only the desired code"
echo "  4. Ensure syntax is valid after merging"

# Use Edit tool to resolve conflicts
# Edit(file_path="$CURRENT_FILE", old_string="<conflict block>", new_string="<resolved code>")

echo ""
echo "Step 4: Mark as resolved"
echo "────────────────────────────────────────────────"

if [[ "$VCS" == "git" ]]; then
  # After Edit completes, stage the file
  git add "$CURRENT_FILE"

  if [[ $? -eq 0 ]]; then
    echo "✓ File resolved and staged: $CURRENT_FILE"
  else
    echo "✗ Failed to stage resolved file: $CURRENT_FILE"
    exit 1
  fi

elif [[ "$VCS" == "jj" ]]; then
  # Jj automatically tracks the resolved file
  # Verify no conflict markers remain
  if grep -q "^<<<<<<<" "$CURRENT_FILE" 2>/dev/null; then
    echo "⚠ Warning: Conflict markers still present in file"
    echo "  Ensure all <<<, ===, >>> markers are removed"
  else
    echo "✓ File resolved: $CURRENT_FILE"
  fi
fi

echo ""
```

### Step 3: Check for Remaining Conflicts

After resolving each file, check if more conflicts remain:

```bash
echo "Checking for remaining conflicts..."
echo "────────────────────────────────────────────────"
echo ""

if [[ "$VCS" == "git" ]]; then
  # Git: check for unmerged files
  REMAINING_CONFLICTS=$(git diff --name-only --diff-filter=U 2>/dev/null)

  if [[ -z "$REMAINING_CONFLICTS" ]]; then
    echo "✓ All conflicts resolved"
    echo ""
    echo "Status: Ready to continue"
  else
    REMAINING_COUNT=$(echo "$REMAINING_CONFLICTS" | wc -l | tr -d ' ')
    echo "⚠ $REMAINING_COUNT file(s) still have conflicts:"
    echo "$REMAINING_CONFLICTS" | sed 's/^/  - /'
    echo ""
    echo "Run this command again to resolve remaining conflicts"
    exit 0
  fi

elif [[ "$VCS" == "jj" ]]; then
  # Jj: check for files with conflict markers
  REMAINING_CONFLICTS=$(jj diff --summary 2>/dev/null | grep -E "^\s+[MA]\s+" | awk '{print $2}' | while read file; do
    if grep -q "^<<<<<<<" "$file" 2>/dev/null; then
      echo "$file"
    fi
  done)

  if [[ -z "$REMAINING_CONFLICTS" ]]; then
    echo "✓ All conflicts resolved"
    echo ""
    echo "Status: Working copy clean"
  else
    REMAINING_COUNT=$(echo "$REMAINING_CONFLICTS" | wc -l | tr -d ' ')
    echo "⚠ $REMAINING_COUNT file(s) still have conflicts:"
    echo "$REMAINING_CONFLICTS" | sed 's/^/  - /'
    echo ""
    echo "Run this command again to resolve remaining conflicts"
    exit 0
  fi
fi

echo ""
```

### Step 4: Complete Resolution Process

Once all conflicts are resolved, complete the merge/rebase operation:

```bash
echo "Completing Resolution"
echo "════════════════════════════════════════════════"
echo ""

if [[ "$VCS" == "git" ]]; then
  # Determine if we're in rebase or merge
  if [[ -d .git/rebase-merge ]] || [[ -d .git/rebase-apply ]]; then
    echo "Detected: Git rebase in progress"
    echo "Continuing rebase..."

    git rebase --continue

    if [[ $? -eq 0 ]]; then
      echo "✓ Rebase completed successfully"
    else
      echo "✗ Rebase continuation failed"
      echo "Check status with: git status"
      exit 1
    fi

  elif [[ -f .git/MERGE_HEAD ]]; then
    echo "Detected: Git merge in progress"
    echo "Completing merge..."

    git commit --no-edit

    if [[ $? -eq 0 ]]; then
      echo "✓ Merge completed successfully"
    else
      echo "✗ Merge commit failed"
      echo "Check status with: git status"
      exit 1
    fi

  else
    echo "No active rebase or merge detected"
    echo "Conflicts resolved, working directory clean"
  fi

elif [[ "$VCS" == "jj" ]]; then
  # Jj: describe the resolution
  echo "Jujutsu conflict resolution complete"
  echo ""
  echo "Describing resolved change..."

  # Prompt for resolution description
  echo "Enter description for resolved conflicts:"
  echo "(Example: 'Resolved merge conflicts from feature branch')"
  echo ""
  read -p "Description: " RESOLUTION_DESC

  if [[ -z "$RESOLUTION_DESC" ]]; then
    RESOLUTION_DESC="Resolved conflicts"
  fi

  jj describe -m "$RESOLUTION_DESC"

  if [[ $? -eq 0 ]]; then
    echo "✓ Resolution described successfully"
  else
    echo "✗ Failed to describe resolution"
    exit 1
  fi
fi

echo ""
```

### Step 5: Verify Clean State

After completion, verify there are no remaining conflicts:

```bash
echo "Final Verification"
echo "════════════════════════════════════════════════"
echo ""

if [[ "$VCS" == "git" ]]; then
  # Git: verify clean status
  git status

  echo ""

  # Check for any remaining merge markers
  if git diff --check 2>/dev/null | grep -q "conflict"; then
    echo "⚠ Warning: Potential conflict markers still present"
    echo "Run: git diff --check"
  else
    echo "✓ Working directory clean - no conflicts"
  fi

  # Check if still in merge/rebase state
  if [[ -d .git/rebase-merge ]] || [[ -d .git/rebase-apply ]] || [[ -f .git/MERGE_HEAD ]]; then
    echo "⚠ Merge/rebase still in progress"
    echo "Additional conflicts may need resolution"
  else
    echo "✓ No active merge or rebase"
  fi

elif [[ "$VCS" == "jj" ]]; then
  # Jj: verify clean status
  jj status

  echo ""

  # Check for conflict markers in tracked files
  MARKER_CHECK=$(jj diff --summary 2>/dev/null | grep -E "^\s+[MA]\s+" | awk '{print $2}' | while read file; do
    if grep -q "^<<<<<<<" "$file" 2>/dev/null; then
      echo "$file"
    fi
  done)

  if [[ -n "$MARKER_CHECK" ]]; then
    echo "⚠ Warning: Conflict markers found in:"
    echo "$MARKER_CHECK" | sed 's/^/  - /'
  else
    echo "✓ No conflict markers detected"
  fi

  echo "✓ Working copy reflects resolved state"
fi

echo ""
echo "Resolution workflow complete!"
echo ""
```

**Expected final output:**
```
Final Verification
════════════════════════════════════════════════
On branch feature-auth
nothing to commit, working tree clean

✓ Working directory clean - no conflicts
✓ No active merge or rebase

Resolution workflow complete!
```

## Safety Considerations

### Non-Interactive Mode

All operations use non-interactive flags:
- Git: `git checkout --ours/--theirs` (no prompts)
- Git: `git add <file>` (direct staging)
- Git: `git rebase --continue` (continues without editor)
- Git: `git commit --no-edit` (uses existing message)
- Jj: `jj resolve --tool=:ours/:theirs` (non-interactive resolution)
- Jj: `jj describe -m "message"` (no editor)

### Partial Resolution Support

This workflow supports partial resolution:
- Files can be skipped with option (s)
- Workflow can be quit with option (q)
- Resume by running command again
- Resolved files are marked immediately (git: staged, jj: tracked)

### Manual Edit Safety

When using manual edit option (c):
- Read tool shows exact conflict markers
- Edit tool removes conflicts surgically
- Verification checks for remaining markers
- Git: File must be staged after edit
- Jj: File is automatically tracked

### Reversibility

**Git:**
```bash
# Abort rebase (before completion)
git rebase --abort

# Abort merge (before commit)
git merge --abort

# Undo staged resolution
git reset HEAD <file>
git checkout <file>
```

**Jj:**
```bash
# Undo last operation (including resolution)
jj undo

# Restore original conflicted state
jj undo && jj undo
```

### Conflict Detection Accuracy

**Git:** Uses `git diff --name-only --diff-filter=U` to find unmerged files (most accurate)

**Jj:** Checks for conflict markers in modified files (reliable for standard conflicts)

## Error Handling

**No conflicts detected:**
```
No conflicts detected in git repository
Status: Ready to continue
```
Exit cleanly without error.

**VCS not found:**
```
ERROR: Not a git or jj repository
Must be run from a git or jj workspace
```
Exit with error code 1.

**Resolution command fails:**
```
✗ Failed to accept OURS for: src/auth.js
Check file permissions and try again
```
Exit with error code 1 and guidance.

**Conflict markers remain after manual edit:**
```
⚠ Warning: Conflict markers still present in file
Ensure all <<<, ===, >>> markers are removed
```
Warn but allow user to continue editing.

**Continue operation fails:**
```
✗ Rebase continuation failed
Check status with: git status

Possible causes:
- Additional conflicts detected
- Commit message required
- Pre-commit hooks failed
```
Exit with error and diagnostic guidance.

## Best Practices

1. **Resolve systematically:** Work through conflicts one file at a time
2. **Review context first:** Use option (d) to see full file before deciding
3. **Test after resolution:** Run tests after resolving all conflicts
4. **Commit atomic resolutions:** Each file resolved is immediately marked (git staged, jj tracked)
5. **Use skip option wisely:** Skip difficult conflicts to resolve easier ones first
6. **Manual edit for complex cases:** When both versions needed, use option (c) to merge manually
7. **Verify clean state:** Always check final status to confirm no remaining conflicts
8. **Document resolution:** For complex merges, note why certain versions were chosen

## Examples

**Example 1: Accept OURS for All Files**

```bash
# Conflict in: src/auth.js (1 of 3)
Select option: a

✓ Accepted OURS and staged: src/auth.js

# Conflict in: tests/auth.test.js (2 of 3)
Select option: a

✓ Accepted OURS and staged: tests/auth.test.js

# Conflict in: README.md (3 of 3)
Select option: a

✓ Accepted OURS and staged: README.md

✓ All conflicts resolved
✓ Rebase completed successfully
```

**Example 2: Mixed Resolution Strategies**

```bash
# Conflict in: src/api.js (1 of 3)
# Review shows THEIRS has better implementation
Select option: b

✓ Accepted THEIRS and staged: src/api.js

# Conflict in: src/utils.js (2 of 3)
# Both versions needed - manual merge required
Select option: c

# (Claude uses Read + Edit to merge both versions)
✓ File resolved and staged: src/utils.js

# Conflict in: package.json (3 of 3)
# Keep current dependencies
Select option: a

✓ Accepted OURS and staged: package.json

✓ All conflicts resolved
✓ Merge completed successfully
```

**Example 3: Partial Resolution with Skip**

```bash
# Conflict in: src/complex.js (1 of 5)
# Not sure which version yet - skip for now
Select option: s

Skipping: src/complex.js

# Conflict in: src/simple.js (2 of 5)
Select option: a

✓ Accepted OURS and staged: src/simple.js

# Resolve more files...

# Later, run command again to resume:
Found 2 conflicted file(s) in git repository
  - src/complex.js
  - src/another.js
```

## Command Reference

### Git Commands Used

```bash
# List conflicted files
git diff --name-only --diff-filter=U

# Show conflict with context
git diff <file>

# Accept ours (keep current)
git checkout --ours <file>

# Accept theirs (take incoming)
git checkout --theirs <file>

# Stage resolved file
git add <file>

# Continue rebase
git rebase --continue

# Complete merge
git commit --no-edit

# Verify clean state
git status
git diff --check
```

### Jj Commands Used

```bash
# Show working copy status
jj status

# Show conflict diff
jj diff <file>

# Show summary of changes
jj diff --summary

# Resolve with ours
jj resolve --tool=:ours <file>

# Resolve with theirs
jj resolve --tool=:theirs <file>

# Describe resolution
jj describe -m "message"

# Undo resolution
jj undo
```

## Integration with Other Commands

**Before resolving conflicts:**
- Use `start-merge` or `start-rebase` commands to initiate operations

**After resolving conflicts:**
- Git: Rebase/merge automatically completes
- Jj: Use `jj new` to create next change if needed

**If conflicts are complex:**
- Use option (s) to skip and resolve easier files first
- Use option (d) to review full context before deciding
- Use option (c) for surgical manual resolution

**To verify resolution:**
- Git: `git log` to see completed merge/rebase
- Jj: `jj log` to see updated change history
- Run tests to ensure functionality preserved
