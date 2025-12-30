# Git Bisect - Detailed Reference Guide

Complete documentation for advanced workflows, troubleshooting, and performance optimization.

## Example Workflow: Manual Bisect

```
$ (run bisect command)

=== GIT BISECT - FIND BUG-INTRODUCING COMMIT ===

Choose bisect mode:
1) Manual bisect
2) Automated bisect
3) Cancel

Enter choice: 1

Bad commit (where bug exists): main
Good commit (where bug does NOT exist): v1.0.0

Starting bisect session...
Commits to test: approximately 42

Current commit being tested:
abc1234 (merge) Merge pull request #42 from feature/auth

Is this commit good (no bug) or bad (contains bug)?
Commands: g/good, b/bad, s/skip, log, reset, help

Enter choice: b
✓ Marked as bad
Remaining commits to test: 21

Current commit being tested:
def5678 Add OAuth provider support

Is this commit good or bad? g
✓ Marked as good
Remaining commits to test: 10

...continuing bisect...

Current commit being tested:
ghi9012 Refactor token validation

Testing commit: ghi9012
Description: Refactor token validation

Is this commit good or bad? b
✓ Marked as bad
Remaining commits to test: 5

Current commit being tested:
jkl3456 Fix JWT expiry check

Testing commit: jkl3456
Description: Fix JWT expiry check

Is this commit good or bad? b
✓ Marked as bad
Remaining commits to test: 2

Current commit being tested:
mno7890 Update token parsing

Testing commit: mno7890
Description: Update token parsing

Is this commit good or bad? b
✓ Marked as bad
Remaining commits to test: 1

=== BUG-INTRODUCING COMMIT FOUND ===

Commit:     mno7890
Author:     Jane Smith <jane@example.com>
Date:       2024-01-15 14:32:00
Message:    Update token parsing

Files Changed:
 src/auth/token.py       | 24 +++++++++++++++++------
 tests/test_token.py     |  8 +++++---
 2 files changed, 23 insertions(+), 9 deletions(-)

Diff Preview:
diff --git a/src/auth/token.py b/src/auth/token.py
index abc123..def456 100644
--- a/src/auth/token.py
+++ b/src/auth/token.py
@@ -45,7 +45,10 @@ def parse_token(token_str):
     try:
-        decoded = jwt.decode(token_str, key, algorithms=['HS256'])
+        decoded = jwt.decode(token_str, key, algorithms=['HS256'],
+                              options={'verify_exp': False})
     except jwt.ExpiredSignatureError:
         return None
...

What would you like to do?
1) View full diff
2) View commit history around this
3) Reset bisect
4) Exit

Enter choice: 1
```

## Example Workflow: Automated Bisect

```
$ (run bisect command)

=== GIT BISECT - FIND BUG-INTRODUCING COMMIT ===

Choose bisect mode:
1) Manual bisect
2) Automated bisect
3) Cancel

Enter choice: 2

Bad commit (where bug exists): main
Good commit (where bug does NOT exist): v1.0.0

Provide the test command to run on each commit:

Examples:
- npm test
- pytest tests/
- ./verify.sh

Test command: pytest tests/test_auth.py -v

Starting automated bisect with test command:
  $ pytest tests/test_auth.py -v

Initial setup: 42 commits to test
Progress: Testing commits...

Testing commit: abc1234 Merge pull request #42
Test command: $ pytest tests/test_auth.py -v
Running test...
Test result: BAD
Status: FAILED test_token_validation

Remaining commits: 21
Progress: [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 25%

Testing commit: def5678 Add OAuth provider support
Test command: $ pytest tests/test_auth.py -v
Running test...
Test result: GOOD
Status: PASSED all tests

Remaining commits: 10
Progress: [████████████████░░░░░░░░░░░░░░░░░░░░░░] 50%

...continuing automated tests...

Testing commit: mno7890 Update token parsing
Test command: $ pytest tests/test_auth.py -v
Running test...
Test result: BAD
Status: FAILED test_token_validation

✓ Culprit identified!

The bug was introduced in:
  Commit: mno7890
  Message: Update token parsing

Files Changed:
 src/auth/token.py       | 24 +++++++++++++++++------
 tests/test_token.py     |  8 +++++---
 2 files changed, 23 insertions(+), 9 deletions(-)

Test output:
FAILED tests/test_auth.py::test_token_validation - AssertionError: Token parsing failed with: options={'verify_exp': False}

Next steps:
1) Review the commit diff to understand the change
2) Check if tests in this commit were adequate
3) Plan remediation strategy
```

## Troubleshooting

### Bisect Not Starting

If `git bisect start` fails:

```bash
# Check for existing bisect session
ls -la .git/BISECT_*

# If found, reset:
git bisect reset

# Then try again
git bisect start <bad> <good>
```

### Test Command Fails Unexpectedly

If automated bisect reports test errors:

```bash
# Manually test the command on HEAD
<test-command>

# Check if environment is clean
git status
git diff

# Ensure dependencies are installed
npm install  # or equivalent
```

### Uncommitted Changes Block Bisect

If you have uncommitted changes:

```bash
# Option 1: Stash changes
git stash

# Option 2: Commit changes
git add .
git commit -m "WIP: stash before bisect"

# Then start bisect
git bisect start <bad> <good>
```

### Commits Missing or History Corrupted

```bash
# Verify commit exists
git rev-parse <commit-hash>

# Check git integrity
git fsck --full

# Fetch missing history
git fetch --all --prune
```

## Key Git Bisect Commands Reference

| Command | Purpose |
|---------|---------|
| `git bisect start <bad> <good>` | Initialize bisect session |
| `git bisect good` | Mark current commit as good |
| `git bisect bad` | Mark current commit as bad |
| `git bisect skip` | Skip current commit (untestable) |
| `git bisect run <cmd>` | Run automated bisect with test command |
| `git bisect log` | View bisect history |
| `git bisect reset` | Abort bisect and return to original branch |
| `git bisect view` | Show current commit in viewer |
| `git bisect replay <log-file>` | Replay a previous bisect session |

## Performance Notes

- **Typical bisect time:** O(log n) - For 1000 commits, expect ~10 iterations
- **Manual bisect:** 5-10 minutes per iteration (includes testing time)
- **Automated bisect:** 1-2 minutes per iteration (depends on test speed)
- **Large repositories:** Consider narrowing date range with `--since` / `--until` flags

## Next Steps After Finding Culprit

1. **Understand the change:** Review the full commit diff and its context
2. **Analyze impact:** Check what depends on this code
3. **Verify with blame:** Use `git blame` to find related changes
4. **Plan fix:** Determine if you should revert, patch, or refactor
5. **Prevent recurrence:** Add automated tests to catch similar issues
