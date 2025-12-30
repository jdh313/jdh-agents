---
description: Generate a PR description from commits/changes and diffs
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Read
---

# Generate PR Description

Generates a structured PR description from the commit history and diffs of the current branch or change. Works with both git and jj, and supports editing before copying to clipboard.

## Immediate Execution

**VCS Detection:**
!`[[ -d .jj ]] && echo "jj" || echo "git"`

**Current Status:**
!`if [[ -d .jj ]]; then jj status; else git status; fi`

## Instructions

Based on the detected VCS shown above, follow these steps to generate a comprehensive PR description.

### Step 1: Get Commit/Change History

Retrieve the list of commits or changes that will be included in the PR.

**For git (if detected above):**

First, detect the main branch:
```bash
# Try to find the main branch (check origin/main, origin/master, main, master in order)
MAIN_BRANCH=""
for branch in origin/main origin/master main master; do
  if git show-ref --quiet refs/remotes/$branch 2>/dev/null || git show-ref --quiet refs/heads/$branch 2>/dev/null; then
    MAIN_BRANCH=$branch
    break
  fi
done

if [ -z "$MAIN_BRANCH" ]; then
  MAIN_BRANCH="main"  # Default fallback
fi

# Get commit history
git log $MAIN_BRANCH..HEAD --oneline
```

**For jj (if detected above):**

```bash
# Get change history (up to 20 most recent)
jj log --limit 20
```

### Step 2: Get Diff Statistics

Retrieve file change statistics to include in the PR description.

**For git (if detected above):**

```bash
# Get diff statistics between main and current branch
git diff $MAIN_BRANCH..HEAD --stat
```

**For jj (if detected above):**

```bash
# Get diff statistics for current change
jj diff --stat
```

### Step 3: Get Full Diff Summary

Retrieve a summary of actual changes for analysis.

**For git (if detected above):**

```bash
# Get diff summary (first 50 lines to avoid overwhelming output)
git diff $MAIN_BRANCH..HEAD --no-color | head -100
```

**For jj (if detected above):**

```bash
# Get diff summary (first 50 lines to avoid overwhelming output)
jj diff --no-color | head -100
```

### Step 4: Analyze Changes and Generate PR Template

Based on the commit messages and diff information from Steps 1-3, generate a structured PR description.

**Template Structure:**

```markdown
## Summary

[Generate 1-2 sentence summary based on commit messages and file changes. Look for patterns in the commit messages to understand the main theme.]

## Changes

- [Bullet point 1: organized by functional area or file type]
- [Bullet point 2: another change area]
- [Bullet point 3: if tests were modified, mention what was tested]

## Files Changed

[Include the diff --stat output here to show files modified, lines added/removed]

## Testing

[If test files were modified, include notes like:
- Added [X] new tests for [feature/fix]
- Updated [Y] existing tests for [changed behavior]
- All tests passing locally]

[If no test files were modified, note:
- No test changes in this PR. Tests should be added if new functionality was introduced.]

## Notes

[Optional section if there are important implementation details, breaking changes, or architectural decisions worth noting]
```

**Generation Guidelines:**

1. **Summary:** Read the commit messages and identify the main theme. Write 1-2 clear sentences about what was changed and why.

2. **Changes:** Group changes by area (e.g., "API endpoint", "Database layer", "Authentication", "Testing", "Documentation"). Use the file names and commit messages as context.

3. **Files Changed:** Include the raw output from `git diff --stat` or `jj diff --stat` so reviewers can see the scope at a glance.

4. **Testing:** Check if test files were modified (e.g., files matching `*test*`, `*spec*`, `tests/`, `__tests__/`). If tests exist, summarize what was tested. If no tests were changed but functionality was added, note this.

5. **Notes:** Only include if there are:
   - Breaking changes
   - Complex architectural decisions
   - Migration notes
   - Performance implications
   - Security considerations

### Step 5: Present PR Description to User

Display the generated PR description clearly:

```
========================================
GENERATED PR DESCRIPTION
========================================

[Display the full markdown template from Step 4]

========================================
```

Follow with a prompt:

```
Review the PR description above. You can:

a) Copy to clipboard (as-is)
b) Edit before copying
c) Regenerate with different focus
d) Cancel and exit

Which option? (a/b/c/d)
```

### Step 6: Handle User Selection

**If user selects (a) - Copy to clipboard:**

Copy the PR description to clipboard:

```bash
# For macOS (pbcopy) or Linux (xclip/xsel)
if command -v pbcopy &> /dev/null; then
  echo "[PR_DESCRIPTION]" | pbcopy
  echo "✓ PR description copied to clipboard"
elif command -v xclip &> /dev/null; then
  echo "[PR_DESCRIPTION]" | xclip -selection clipboard
  echo "✓ PR description copied to clipboard"
elif command -v xsel &> /dev/null; then
  echo "[PR_DESCRIPTION]" | xsel --clipboard --input
  echo "✓ PR description copied to clipboard"
else
  echo "⚠️  Clipboard utility not available. Here's your PR description:"
  echo "[PR_DESCRIPTION]"
fi
```

Replace `[PR_DESCRIPTION]` with the actual markdown content.

**If user selects (b) - Edit before copying:**

Present the description in an editable format:

```
You can now edit the PR description below. Make any adjustments needed:

[Display full editable markdown]

Edit above and confirm when ready. Paste edited content back to proceed.
```

After user provides edited content, proceed to copy to clipboard (as in option a).

**If user selects (c) - Regenerate:**

Show a regeneration menu:

```
Regeneration options:

1. Focus on bug fixes (if PR contains fixes)
2. Focus on features (if PR contains new functionality)
3. Focus on refactoring (if PR contains refactoring)
4. Focus on documentation (if PR contains docs changes)
5. Use default (balanced summary)

Which focus? (1-5)
```

Adjust the Summary and Changes sections based on selected focus, then return to Step 5.

**If user selects (d) - Cancel:**

```
PR description generation cancelled. Nothing copied to clipboard.
```

Exit cleanly without making changes.

### Step 7: Show Success Message

After successful copy to clipboard:

```
✓ PR description generated and copied successfully!

Next steps:
1. Go to your GitHub/GitLab PR page
2. Click in the description field
3. Paste (Cmd+V or Ctrl+V)
4. Review and submit the PR

The description includes:
- Summary of changes
- Organized list of modifications
- File change statistics
- Testing notes
```

## Implementation Notes

### VCS-Specific Behaviors

**Git:**
- Detects main branch automatically (checks origin/main, origin/master, main, master)
- Uses `git log MAIN..HEAD` to show commits not yet in main
- Uses `git diff` for statistics and content analysis
- Handles both local and remote main branches

**Jj:**
- Uses `jj log` to show recent changes (defaults to tracking from parent)
- Uses `jj diff` for statistics and content analysis
- No separate main branch concept; changes are relative to parent
- Shows all tracked changes automatically

### Clipboard Handling

The command attempts to use the appropriate clipboard utility for the platform:
- **macOS:** `pbcopy`
- **Linux with X11:** `xclip` or `xsel`
- **Fallback:** Display the text if no clipboard utility is available

### Edge Cases

1. **No commits/changes:** If the current branch has no commits ahead of main (git) or no changes (jj), inform the user:
   ```
   ⚠️  No commits or changes found. Make sure you're on a branch with unpushed commits.
   ```

2. **New branch with no main:** If main branch doesn't exist (rare), use `--root` for git:
   ```bash
   git diff --stat $(git rev-list --max-parents=0 HEAD)..HEAD
   ```

3. **Empty repository:** If the repository is empty, show:
   ```
   ⚠️  This repository has no commits yet. Create your first commit and try again.
   ```

## Best Practices

1. **Review before submitting:** Always review the generated description before copying to ensure it's accurate and professional.

2. **Edit when needed:** Use the edit option if the auto-generated summary doesn't capture the full context or tone you want.

3. **Include test details:** If your PR includes test changes, make sure the Testing section clearly explains what was tested.

4. **Note breaking changes:** Always explicitly call out any breaking changes in the Notes section.

5. **Keep summaries concise:** The Summary section should be scannable (1-2 sentences max). Save detailed explanations for the Changes section.

## Command Workflow Summary

```
1. Detect VCS (git or jj)
2. Fetch commit/change history
3. Get diff statistics
4. Generate PR template from commits
5. Present to user for review
6. Handle user's choice (copy/edit/regenerate/cancel)
7. Copy to clipboard or show message
8. Display success and next steps
```
