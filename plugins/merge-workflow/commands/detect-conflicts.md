---
description: Detect and categorize conflicts in the current repository
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Read
---

# Detect Conflicts

Detect and categorize conflicts in the current repository for both git and jj, providing a comprehensive conflict summary with conflict types and affected files.

## Immediate Execution

**VCS Detection:**
!`[[ -d .jj ]] && echo "jj" || echo "git"`

**Current Status:**
!`if [[ -d .jj ]]; then jj status; else git status; fi`

## Instructions

Based on the detected VCS shown above, this command will detect conflicts, categorize them by type, and generate a detailed summary report.

### Step 1: Check for Conflict State

**For git:**

Check if there are any unmerged paths indicating conflicts:

```bash
# Check for any unmerged paths
if git diff --name-only --diff-filter=U | grep -q .; then
  echo "CONFLICTS_DETECTED=true"
else
  echo "CONFLICTS_DETECTED=false"
fi
```

If no conflicts are detected, report:
```
✓ No conflicts detected. Working directory is clean.
```

**For jj:**

Check if there are any conflicted files:

```bash
# Check for conflicts in status
jj status | grep -q "Conflicted" && echo "CONFLICTS_DETECTED=true" || echo "CONFLICTS_DETECTED=false"

# Alternative: check diff for conflict markers
jj diff | grep -q "^<<<<<<< " && echo "CONFLICTS_DETECTED=true" || echo "CONFLICTS_DETECTED=false"
```

If no conflicts are detected, report:
```
✓ No conflicts detected. All changes are resolved.
```

### Step 2: List Conflicted Files

**For git:**

Get all files with merge conflicts:

```bash
# List all conflicted files (unmerged)
CONFLICTED_FILES=$(git diff --name-only --diff-filter=U)
echo "$CONFLICTED_FILES"
```

Also gather their conflict status types:

```bash
# Get detailed merge conflict status for each file
git diff --name-status --diff-filter=U
```

Conflict status codes from git:
- `UU` = both modified (content conflict)
- `AA` = both added (add/add conflict)
- `DU` = deleted by us, modified by them
- `UD` = modified by us, deleted by them
- `DD` = both deleted

**For jj:**

Get conflicted files from status:

```bash
# Extract conflicted files from status output
jj status | grep "Conflicted" | awk '{print $2}'

# Also check diff for conflict markers
jj diff | grep -B 5 "^<<<<<<< " | grep "diff --git" | awk '{print $NF}' | sed 's/^b\///'
```

### Step 3: Categorize Each Conflict

For each conflicted file, determine the conflict type.

**For git:**

Use git status porcelain to categorize:

```bash
# Get merge status codes
git status --porcelain | grep "^[UA][UAD]"

# Parse conflict types:
# UU = both modified (content conflict)
# AA = both added (add/add conflict)
# DU = deleted by us, modified by them (delete conflict)
# UD = modified by us, deleted by them (delete conflict)
```

Then for content and add/add conflicts, check the actual conflict markers:

```bash
# For each file with conflicts, count conflict markers
count_conflicts() {
  local file="$1"
  if [[ -f "$file" ]]; then
    grep -c "^<<<<<<< " "$file"
  else
    echo "0"
  fi
}

# Get status code for each file
while read -r status_code file; do
  conflict_count=$(count_conflicts "$file")
  echo "$file | $status_code | $conflict_count"
done < <(git status --porcelain | grep "^[UA][UAD]")
```

**For jj:**

Parse conflict markers from the diff and affected files:

```bash
# Get full diff to analyze conflicts
jj diff > /tmp/jj_diff.txt

# Extract conflicted files with conflict marker counts
while read -r file; do
  # Extract conflicts for this file from the diff
  conflict_count=$(sed -n "/^diff.*${file//\//\\/}/,/^diff/p" /tmp/jj_diff.txt | grep -c "^<<<<<<< ")
  # Determine type based on markers (simplified detection)
  echo "$file | content | $conflict_count"
done < <(jj status | grep "Conflicted" | awk '{print $2}')
```

**Categorization Logic:**

- **Content conflict**: File exists on both sides, both modified same content → type: "content"
- **Add/Add conflict**: File added on both sides with different content → type: "add/add"
- **Delete conflict**: One side modified, other side deleted → type: "delete"
- **Rename conflict**: Both sides renamed differently (for git only) → type: "rename"

For git, map the status codes:
- `UU` → content
- `AA` → add/add
- `DU` or `UD` → delete
- `RR` → rename (if supported)

### Step 4: Count Conflicts Per File

For each conflicted file, count the total number of conflicts (each set of `<<<<<<< ... ======= ... >>>>>>>` markers is one conflict).

**For git:**

```bash
count_markers_in_file() {
  local file="$1"
  if [[ -f "$file" ]]; then
    # Count opening markers (each one marks a conflict)
    grep -c "^<<<<<<< " "$file" 2>/dev/null || echo "0"
  else
    echo "0"  # File deleted, count as 0
  fi
}

# Process each conflicted file
echo "Conflict Count by File:"
while read -r file; do
  count=$(count_markers_in_file "$file")
  echo "  $file: $count conflicts"
done < <(git diff --name-only --diff-filter=U)
```

**For jj:**

```bash
# Extract conflict marker counts from diff output
jj diff | awk '
  /^diff/ { file = $NF; gsub(/^b\//, "", file) }
  /^<<<<<<< / { if (file != "") count[file]++ }
  END {
    for (f in count) {
      print "  " f ": " count[f] " conflicts"
    }
  }
'
```

### Step 5: Generate Summary Report

Compile all collected information into a comprehensive markdown report:

```markdown
## Conflict Summary

**Total conflicted files**: X
**Total conflicts**: Y (across all files)

### Conflict Types
- Content conflicts: N file(s)
- Add/Add conflicts: N file(s)
- Delete conflicts: N file(s)
- [Other types as detected]

### Conflicted Files

| File | Type | Conflict Count |
|------|------|---|
| path/to/file1.py | content | 3 |
| path/to/file2.js | add/add | 1 |
| config/settings.yaml | delete | 2 |

### Detailed Breakdown

[For each conflict type, show files in that category]

**Content Conflicts (3 files):**
- src/main.py (3 conflicts)
- src/utils.py (1 conflict)
- src/helpers.py (2 conflicts)

**Add/Add Conflicts (1 file):**
- config.yaml (1 conflict)

**Delete Conflicts (1 file):**
- README.md (1 conflict - modified by us, deleted by them)

### Resolution Status

**Blocking operations:**
- Git: Cannot commit until all conflicts are resolved. Use `git add <file>` to mark as resolved.
- Jj: Conflicts can coexist with normal work. Resolve when ready with `jj resolve` or by editing files.

### Next Steps

1. Review each conflicted file listed above
2. Edit files to resolve conflicts (remove markers, choose correct version)
3. For git: Stage resolved files with `git add <file>`
4. For jj: Conflicts auto-resolve when you save the file correctly
5. Commit or describe changes once all conflicts are resolved

**Use `/detect-conflicts` again** to verify all conflicts are resolved before proceeding.
```

**Report Generation:**

Generate the report with all sections:

1. Count total conflicted files: `git diff --name-only --diff-filter=U | wc -l` (git) or count from jj status
2. Count total conflicts: Sum of all conflict marker counts
3. Categorize files by type
4. Create summary table
5. List files under each conflict type category
6. Add resolution guidance specific to VCS

### Step 6: Display Report

Output the complete conflict summary report (from Step 5) to the user.

If conflicts were found, include:
- Summary metrics (files, total conflicts)
- Breakdown by conflict type
- Detailed table of conflicts
- Next steps for resolution

If no conflicts found:
```
✓ Conflict Detection Complete
  No conflicts detected in the repository.
  Working directory is clean and ready for next steps.
```

### Step 7: Offer Conflict Resolution Assistance

After displaying the report, if conflicts were found, ask:

```
Would you like help resolving conflicts?

1. Show detailed diff for a specific file
2. Get resolution strategy suggestions
3. Done (conflicts will need manual resolution)

Enter choice (1-3):
```

**For option 1** (show detailed diff):

Prompt for filename, then display:

**Git:**
```bash
# Show the conflicted file with markers
cat <user-specified-file>
```

**jj:**
```bash
# Show diff highlighting the conflicts
jj diff <user-specified-file>
```

**For option 2** (resolution strategy):

Provide guidance based on conflict types detected:

```markdown
## Resolution Strategy

### For Content Conflicts
1. Open the file in your editor
2. Find lines between <<<<<<< and =======  (your changes)
3. Find lines between ======= and >>>>>>> (their changes)
4. Choose which version to keep, or manually merge both
5. Remove the conflict markers (<<<<, ====, >>>>)

### For Add/Add Conflicts
1. Both sides added the file with different content
2. Open and manually merge the two versions
3. Remove conflict markers when done

### For Delete Conflicts
1. Decide: should the file be kept or deleted?
2. If keeping: edit to remove conflict markers and keep content
3. If deleting: remove the file (git rm / jj rm)

### After Resolution
- **Git**: git add <file>, then git commit
- **jj**: Changes auto-track when you edit the file
```

**For option 3:**

End with message:
```
✓ Conflicts detected and categorized. Manual resolution required.
  Review the files listed above and resolve conflicts in your editor.
  Run `/detect-conflicts` again to verify all conflicts are resolved.
```

### Step 8: Final Summary

Display completion message:

```
✓ Conflict Detection Complete

**Summary:**
- Conflicted files: X
- Total conflicts: Y
- Conflict types: [list of types found]

**Recommendation:**
[Based on VCS and conflict types, suggest next action]

For git: Resolve all conflicts before committing
For jj: Resolve when ready, conflicts don't block work

Run `/detect-conflicts` again after resolving to verify clean state.
```

## Error Handling

**Common error scenarios:**

1. **Not in a git/jj repository:**
   - Message: "Error: Not in a git or jj repository. Run this command from a repository root."
   - Exit with error code

2. **No conflicts detected:**
   - Message: "No conflicts detected. Working directory is clean."
   - Exit gracefully with success

3. **Cannot read conflicted files:**
   - Message: "Warning: Could not read file <filename> (may be deleted)"
   - Continue with next file

4. **Merge in progress (git only):**
   - Message: "Git merge is in progress. Use 'git merge --abort' to cancel or continue resolving."
   - Show extra status information

5. **Rebase in progress (git only):**
   - Message: "Git rebase is in progress. Use 'git rebase --abort' to cancel or continue resolving."
   - Show extra status information

**Error detection:**

```bash
# Check for merge/rebase in progress (git)
if [[ -d .git/MERGE_HEAD ]]; then
  echo "Git merge in progress"
fi

if [[ -d .git/rebase-merge ]] || [[ -d .git/rebase-apply ]]; then
  echo "Git rebase in progress"
fi

# For jj, conflicts are not blocking, so no special state to check
```

## Safety Considerations

1. **Read-only operations**: All detection and analysis is read-only. No modifications to files or repository.
2. **No automatic resolution**: Conflicts are categorized but not automatically resolved (user must decide).
3. **File existence checks**: Handle deleted files gracefully (don't try to read non-existent files).
4. **Binary file safety**: Warn if binary files are involved in conflicts (hard to merge visually).
5. **Large conflict counts**: Warn if a single file has many conflicts (>20) as it may need special handling.

## Performance Optimizations

For large repositories:

1. **Stream processing**: Process files line-by-line instead of loading entire files
2. **Avoid full diffs**: Use `--name-only` and `--name-status` flags to minimize output
3. **Parallel detection**: Run conflict categorization in parallel if multiple files
4. **Cache results**: Run detection once and reuse results across steps

**Example optimization:**

```bash
# Process files in parallel
export -f count_markers_in_file
git diff --name-only --diff-filter=U | \
  parallel 'echo "{} | $(get_status {}) | $(count_markers_in_file {})"'
```

## Example Output

```markdown
## Conflict Summary

**Total conflicted files**: 3
**Total conflicts**: 6

### Conflict Types
- Content conflicts: 2 file(s)
- Add/Add conflicts: 1 file(s)
- Delete conflicts: 1 file(s)

### Conflicted Files

| File | Type | Conflict Count |
|------|------|---|
| src/main.py | content | 3 |
| src/utils.py | content | 1 |
| config.yaml | add/add | 1 |
| README.md | delete | 1 |

### Detailed Breakdown

**Content Conflicts (2 files):**
- src/main.py (3 conflicts in authentication logic)
- src/utils.py (1 conflict in helper function)

**Add/Add Conflicts (1 file):**
- config.yaml (1 conflict - both sides added different config structure)

**Delete Conflicts (1 file):**
- README.md (1 conflict - modified by us, deleted by them)

### Resolution Status

Git merge is in progress. Conflicts must be resolved before committing.

### Next Steps

1. Edit src/main.py and resolve 3 conflicts
2. Edit src/utils.py and resolve 1 conflict
3. Edit config.yaml and merge both versions
4. Decide on README.md (keep or delete?)
5. Stage resolved files: git add src/main.py src/utils.py config.yaml README.md
6. Commit: git commit -m "Merge: resolve conflicts"

Run `/detect-conflicts` again to verify all conflicts are resolved.
```
