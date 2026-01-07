---
description: Binary search through history to find bug-introducing commits (git only)
argument-hint: <bad-commit> [good-commit] [--auto=<test-command>]
context: fork
allowed-tools:
  - Bash(git:*)
  - Bash([[:*)
  - Bash(if:*)
  - Read
---

# Git Bisect - Find Bug-Introducing Commits

Binary search through commit history to locate the exact commit that introduced a bug or regression. Supports both manual and automated bisect modes.

**Note:** This command works with git only. Jujutsu does not have a built-in bisect equivalent.

## Immediate Execution

**VCS Detection:**
!`[[ -d .jj ]] && echo "jj" || echo "git"`

**Current Status:**
!`if [[ -d .jj ]]; then echo "⚠️  Jujutsu detected - bisect not available"; else git status; fi`

**Active Bisect Session:**
!`if [[ -d .jj ]]; then echo "N/A"; elif git rev-parse --verify BISECT_HEAD >/dev/null 2>&1; then echo "✓ Bisect session in progress"; else echo "No active bisect session"; fi`

## Instructions

### Step 1: Verify VCS and Bisect Availability

Check that you are using git (not jj) and that no bisect session is currently active.

**Check current VCS:**
```bash
[[ -d .jj ]] && echo "jj" || echo "git"
```

**If jj is detected:**
```
⚠️  ERROR: Bisect is not available in Jujutsu (jj)
jj does not have a binary search feature equivalent to git bisect.
Consider using: jj log --oneline to manually inspect history
```

Exit and inform the user that this command only works with git.

**If git is detected, check for existing bisect session:**
```bash
if [[ -d .git/BISECT_HEAD ]] || [[ -f .git/BISECT_START ]]; then
  echo "⚠️  An active bisect session is already in progress"
  git bisect log
  echo ""
  echo "Options:"
  echo "1) Continue this session (mark current commit as good/bad)"
  echo "2) Reset and start a new bisect"
  echo "3) Cancel"
  # Prompt user for choice
else
  echo "✓ Ready to start bisect"
fi
```

If a bisect session is already active, offer to continue or reset.

### Step 2: Choose Bisect Mode

Prompt the user to select their bisect approach:

```
Choose bisect mode:

1) Manual bisect
   - You test each commit and mark it as good (working) or bad (broken)
   - Shows progress and remaining commits
   - Best for understanding which commit introduced the bug

2) Automated bisect
   - Provide a test command that returns 0 (good) or non-zero (bad)
   - Bisect runs tests automatically on each commit
   - Best for regression testing with automated checks

3) Cancel

Enter choice (1/2/3):
```

#### If user selects option 1: Proceed to Manual Bisect (Step 3)
#### If user selects option 2: Proceed to Automated Bisect (Step 4)
#### If user selects option 3: Exit gracefully

### Step 3: Manual Bisect Mode

#### Step 3.1: Gather Required Commits

Prompt the user for the known good and bad commits:

```
Provide commit references for manual bisect:

Bad commit (where bug exists - usually HEAD or a commit hash):
  - Examples: HEAD, main, abc1234, v1.0.0
  Bad commit:
```

Validate the input:
```bash
# Check if bad commit exists
if ! git rev-parse <bad-commit> > /dev/null 2>&1; then
  echo "Error: Bad commit '<bad-commit>' not found"
  echo "Please provide a valid commit reference (hash, tag, or branch)"
  # Retry
fi
```

```
Good commit (where bug does NOT exist - usually an older commit):
  - Examples: abc5678, v0.9.0, main~10
  Good commit:
```

Validate the good commit:
```bash
# Check if good commit exists
if ! git rev-parse <good-commit> > /dev/null 2>&1; then
  echo "Error: Good commit '<good-commit>' not found"
  echo "Please provide a valid commit reference"
  # Retry
fi

# Verify good is actually before bad (optional check)
if ! git merge-base --is-ancestor <good-commit> <bad-commit>; then
  echo "Warning: Good commit may not be an ancestor of bad commit"
  echo "This might still work, but consider reversing the commits"
fi
```

#### Step 3.2: Initialize Bisect

Start the bisect session:

```bash
git bisect start <bad-commit> <good-commit>
```

Display initial status:
```bash
# Show remaining commits to test
REMAINING=$(git rev-list --bisect-left --count <good-commit>..<bad-commit>)
echo "Starting bisect session..."
echo "Commits to test: approximately $REMAINING"
echo ""
git bisect log
echo ""

# Show current commit being tested
echo "Current commit being tested:"
git log -1 --oneline
echo ""
git show --stat --no-patch
```

#### Step 3.3: Test and Mark Commits

For each commit in the bisect session, test for the bug and mark accordingly:

```
Testing commit: <commit-hash>
Description: <commit-message>

Is this commit good (no bug) or bad (contains bug)?

Commands:
- Type 'g' or 'good' to mark this commit as good
- Type 'b' or 'bad' to mark this commit as bad
- Type 's' or 'skip' to skip this commit (if unable to test)
- Type 'log' to see bisect progress
- Type 'reset' to abort bisect
- Type 'help' for more options

Enter choice:
```

**Processing user input:**

```bash
# If user enters 'good'
git bisect good
echo "✓ Marked as good"
REMAINING=$(git rev-list --count <good-commit>..HEAD)
echo "Remaining commits to test: $REMAINING"
# Show next commit

# If user enters 'bad'
git bisect bad
echo "✓ Marked as bad"
REMAINING=$(git rev-list --count HEAD..<bad-commit>)
echo "Remaining commits to test: $REMAINING"
# Show next commit

# If user enters 'skip'
git bisect skip
echo "✓ Skipped commit"
# Show next commit

# If user enters 'log'
git bisect log
# Continue loop

# If user enters 'reset'
git bisect reset
echo "✓ Bisect session aborted"
exit 0
```

#### Step 3.4: Display Commit Details

For each commit, show:

```bash
# Commit hash and message
git log -1 --oneline

# Detailed commit info
git show --stat --no-patch

# Preview of changes (first 50 lines)
git show --stat | head -50
```

Offer to show full diff if needed:

```
View full diff for this commit?
- Type 'diff' to see all changes
- Type 'files' to see changed files only
- Type 'skip' to continue without viewing
- Type 'help' for more options

Enter choice:
```

#### Step 3.5: Culprit Found

When bisect identifies the culprit (usually after ~log2(remaining commits) iterations):

```bash
if git bisect view > /dev/null 2>&1; then
  # Bisect found the culprit
  echo "✓ Culprit identified!"
  echo ""
  git bisect log
  echo ""
  echo "The bug was introduced in this commit:"
  git log -1 --format="%H %s" HEAD
  echo ""
  git show --stat
  echo ""
  git diff HEAD~1..HEAD
fi
```

Display full details:

```
=== BUG-INTRODUCING COMMIT FOUND ===

Commit:     <commit-hash>
Author:     <author-name> <author-email>
Date:       <commit-date>
Message:    <commit-message>

Files Changed:
<file changes summary>

Diff Preview:
<first 100 lines of diff>

Full diff available with 'git show <commit-hash>'
```

Offer next actions:

```
What would you like to do?

1) View full diff of this commit
2) View commit history around this commit
3) Reset bisect and return to original branch
4) Create a fix based on this analysis
5) Exit

Enter choice:
```

#### Step 3.6: Reset Bisect

After completing manual bisect:

```bash
git bisect reset
echo "✓ Bisect session closed"
echo "You are now back on your original branch"
git status
```

---

### Step 4: Automated Bisect Mode

Automated bisect runs a test command on each commit to find the culprit. The test command should return:
- **0 (exit code)** = commit is good (no bug)
- **non-zero (exit code)** = commit is bad (contains bug)

#### Step 4.1: Gather Required Information

Prompt for commit references (same as Step 3.1):

```
Provide commit references for automated bisect:

Bad commit (where bug exists):
  Bad commit:

Good commit (where bug does NOT exist):
  Good commit:
```

#### Step 4.2: Get Test Command

Prompt for the test command:

```
Provide the test command to run on each commit:

Examples:
- npm test          (runs test suite)
- pytest tests/     (Python tests)
- ./verify.sh       (custom verification script)
- python -m pytest --tb=short  (pytest with options)

The command should exit with:
  - 0 if commit is good (test passes)
  - non-zero if commit is bad (test fails)

Test command:
```

Validate the command is executable:

```bash
# Check if command exists and is executable
if ! command -v <first-word-of-command> &> /dev/null; then
  echo "Warning: Command '<first-word-of-command>' not found"
  echo "This may cause bisect to fail if not in PATH"
  echo "Continue anyway? (y/n)"
fi
```

#### Step 4.3: Initialize Automated Bisect

Start the bisect session and run automated tests:

```bash
git bisect start <bad-commit> <good-commit>
git bisect run <test-command>
```

Display progress:

```
Starting automated bisect with test command:
  $ <test-command>

Initial setup: <remaining> commits to test
Progress: Testing commits...
```

#### Step 4.4: Display Test Results for Each Commit

As bisect runs, show:

```
Testing commit: <commit-hash> <commit-message>
Test command: $ <test-command>
Running test...
```

After test completes:

```
Test result: [GOOD | BAD | SKIP]
Status: <detailed output from test>

Remaining commits to test: <count>
Progress: [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 25%
```

#### Step 4.5: Automated Culprit Identification

When bisect identifies the culprit:

```bash
# Capture final result
CULPRIT=$(git rev-parse HEAD)
CULPRIT_MSG=$(git log -1 --format="%s" $CULPRIT)

echo "✓ Culprit identified!"
echo ""
echo "The bug was introduced in:"
echo "  Commit: $CULPRIT"
echo "  Message: $CULPRIT_MSG"
echo ""
git show --stat
echo ""
echo "Test command exit code: <non-zero>"
echo "Test output:"
<last-test-output>
```

#### Step 4.6: Reset Automated Bisect

```bash
git bisect reset
echo "✓ Automated bisect session completed"
echo "✓ Returned to original branch"
git status
```

---

### Step 5: Bisect Management Commands

Provide quick access to bisect utilities regardless of which mode was used:

#### View Bisect Log

```
View bisect progress history:

$ git bisect log
```

Displays all marks (good/bad/skip) made during the session.

#### Skip Problematic Commits

If a commit cannot be tested (build broken, missing dependencies, etc.):

```bash
git bisect skip
```

This marks the commit as untestable and moves to the next candidate.

#### Reset Active Bisect

If you need to abort and start over:

```bash
git bisect reset
```

This ends the bisect session and returns to the original branch.

#### View Culprit Details

After bisect completes, examine the culprit commit:

```bash
# View the culprit commit
git show <culprit-hash>

# View commits between good and bad
git log <good-commit>..<bad-commit> --oneline

# View blame for specific file
git blame <filename>
```

---

## Safety Considerations

1. **No data loss:** Bisect does not modify your repository. It only checks out different commits.
2. **Easy abort:** Run `git bisect reset` at any time to return to your original branch.
3. **Safe skip:** Use `git bisect skip` if you encounter broken builds or test environment issues.
4. **Test isolation:** Automated bisect should use tests that can run reliably on any commit.
5. **Non-destructive:** All bisect operations are read-only and reversible.

---

## Resources

For detailed example workflows, troubleshooting guides, command reference tables, and performance notes, see: [Bisect Guide Reference](../references/bisect-guide.md)
