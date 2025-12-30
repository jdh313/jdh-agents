---
name: history-detective
description: Investigate repository history with bisect, blame, file evolution, and branch comparison for git and jj repositories with VCS auto-detection
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Read
  - Edit
  - AskUserQuestion
---

# History Detective Skill

Investigate repository history with bisect, blame, file evolution tracking, and branch comparison tools for both git and Jujutsu repositories. This skill helps find when bugs were introduced, understand file changes over time, and compare history between branches.

**Supports:** git and jj (Jujutsu)

**Explicit commands available:**
- `/history-detective:bisect` - Binary search to find commit that introduced a bug
- `/history-detective:blame` - Analyze who made changes and why (coming soon)
- `/history-detective:file-evolution` - Track how a file has changed over time (coming soon)
- `/history-detective:branch-compare` - Compare history between branches/changes (coming soon)

## When to Use This Skill

Use this skill when:
- You need to find which commit introduced a bug or regression
- You want to understand when a file was last modified
- You need to see who made specific changes (blame analysis)
- You're comparing history between branches
- You want to investigate unexpected behavior in your codebase
- You need to narrow down changes across many commits
- You're doing root cause analysis on production issues

## VCS Detection

This skill automatically detects whether you're in a git or jj repository at runtime.

### Detection Logic

```bash
[[ -d .jj ]] && echo "jj" || echo "git"
```

**How it works:**
- Checks for the `.jj` directory (Jujutsu metadata)
- If `.jj` exists: Jujutsu is in use
- If `.jj` does not exist: Git is in use (or git is the default fallback)

**Speed:** Detection is instant (no command execution, just filesystem check)

### Example Detection Output

When you run a history-detective command, you'll see:

```
Detected VCS: git
Repository type: Git
You're working in a git repository. History operations will use git commands.
```

Or if using Jujutsu:

```
Detected VCS: jj
Repository type: Jujutsu
You're working in a jujutsu repository. History operations will use jj commands.
```

## History Investigation Terminology

| Concept | Git Term | Jujutsu Term | Purpose |
|---------|----------|--------------|---------|
| Commit History | `git log` | `jj log` | View all commits/changes |
| Blame Analysis | `git blame` | `jj log -p` | See who made each change |
| Binary Search | `git bisect` | Manual traversal | Find problematic commit |
| File History | `git log [file]` | `jj log [file]` | Track file changes over time |
| Branch Comparison | `git log branch1..branch2` | `jj log` with filters | Compare history between branches |

## Available Commands

### Bisect Command

Find the commit that introduced a bug or regression using binary search.

**Usage:**
```
/history-detective:bisect
```

**What it does:**
1. Detects your VCS (git or jj)
2. Verifies working directory is clean (git only)
3. Initiates bisect workflow with starting point
4. Guides through testing commits
5. Uses binary search to narrow commit range
6. Identifies exact commit that introduced issue
7. Shows commit details: hash, author, date, message, changes

**When to use:**
- Debugging when a test started failing
- Finding which commit caused a regression
- Tracking down when a feature broke
- Isolating problematic changes in large commit ranges
- Root cause analysis of unexpected behavior

**Example workflow:**

```
# Start bisect to find which commit broke a test
/history-detective:bisect

# Bisect tells you to test a commit (usually the middle)
# Run your test to see if it passes or fails

# Good commit? Type: good
# Bad commit? Type: bad

# Bisect narrows the range and repeats
# Eventually identifies the exact problem commit
```

**Bisect Workflow Details:**

1. **Start bisect**: You provide initial good and bad commit references
2. **Test commit**: Bisect checks out a commit (usually midpoint)
3. **Evaluate**: You test the commit and mark as good or bad
4. **Narrow range**: Search space is cut in half
5. **Repeat**: Steps 2-4 continue until one commit remains
6. **Report**: Final commit is identified with full details

**Commit Marking:**

- **(good)** - This commit works correctly (doesn't have the bug)
- **(bad)** - This commit has the problem (introduced the bug)
- **(skip)** - Can't test this commit, bisect will skip it
- **(abort)** - Cancel bisect operation and return to starting state

### Blame Command (Coming Soon)

Analyze who made changes and understand the context for specific lines.

**Usage:**
```
/history-detective:blame [file] [line]
```

**What it does:**
1. Shows who modified each line in a file
2. Displays commit hash, author, date, and message
3. Links to full commit details
4. Helps trace when changes were made
5. Shows context around each change

**When to use:**
- Understanding who made a specific change
- Finding the original author for context
- Tracing when a line was added or modified
- Investigating code you don't recognize

### File Evolution Command (Coming Soon)

Track how a file has changed over time with full diff history.

**Usage:**
```
/history-detective:file-evolution [file]
```

**What it does:**
1. Lists all commits affecting a specific file
2. Shows file state across major changes
3. Displays diffs between versions
4. Tracks rename/move operations
5. Identifies when file was created/deleted

**When to use:**
- Understanding how a feature evolved
- Reviewing entire history of a file
- Finding when a bug was introduced in a file
- Tracing feature development across commits

### Branch Compare Command (Coming Soon)

Compare history and differences between branches or changes.

**Usage:**
```
/history-detective:branch-compare [branch1] [branch2]
```

**What it does:**
1. Lists commits unique to each branch
2. Shows commits not yet merged
3. Compares file changes between branches
4. Identifies merge points and divergence
5. Suggests potential conflicts

**When to use:**
- Preparing branches for merge/rebase
- Understanding what changed on a branch
- Planning integration strategy
- Reviewing changes before code review

## Core Principles

### Dual VCS Support

The same skill works in both git and jj repositories because:
1. **Detection happens at runtime** - Commands determine which VCS to use
2. **VCS-specific operations** - Each operation uses the right command for the detected VCS
3. **Consistent workflows** - Git bisect maps to jj change traversal
4. **No manual configuration** - The skill "just works" without setup

### Safe Operations

All history investigation operations follow these safety principles:

- **Non-destructive** - History commands never modify commits or branches
- **Confirmation before changes** - Bisect requires explicit good/bad marking
- **Clear feedback** - Show commit details and analysis results
- **Reversible actions** - Bisect can be aborted at any time
- **Context preservation** - Original branch preserved during investigation

### Targeted Investigation

History-detective tools focus the investigation:
- **Binary search**: Bisect dramatically reduces search space (log N vs N)
- **Blame precision**: Find exact line author and context
- **File focus**: Evolution tracking shows only relevant changes
- **Branch isolation**: Compare only what differs between branches

## Workflow Examples

### Example 1: Simple Bisect

1. Run `/history-detective:bisect`
2. Specify good and bad commit references
3. Test the suggested commit
4. Mark it as good or bad
5. Repeat 3-4 until bisect completes
6. Review the identified problematic commit

### Example 2: Finding a Regression

Scenario: Tests were passing, now they fail. When did it break?

1. Run `/history-detective:bisect`
2. Provide last known good commit (recent passing run)
3. Provide bad commit (current HEAD)
4. Test each suggested commit
5. Identify exact commit that broke tests
6. Review that commit's changes
7. Plan fix based on changes identified

### Example 3: Complex History Investigation

Scenario: Feature works on main but breaks on your branch.

1. Run `/history-detective:branch-compare` to see unique commits
2. If bisect needed, run `/history-detective:bisect`
3. Test commits on your branch until problem found
4. Use `/history-detective:file-evolution` on affected files
5. Review changes and plan fix

## Key Differences: Git vs Jujutsu

| Aspect | Git | Jujutsu |
|--------|-----|---------|
| Bisect Command | `git bisect start/good/bad` | Manual change traversal |
| History View | `git log` with options | `jj log` with queries |
| Blame Support | `git blame` for lines | `jj log -p` for context |
| File Evolution | `git log [file]` | `jj log [file]` |
| Branch Comparison | `git log branch1..branch2` | `jj log` with filters |
| Commit Movement | Not possible (history immutable) | Changes auto-track (immutable IDs) |

## Safety Considerations

### When NOT to Use Bisect

- On already-pushed branches without team coordination
- On main, master, or other protected branches
- When you have uncommitted work (git)
- If you're not sure how to test for the issue
- When the problem is intermittent or unreproducible

### Best Practices

1. **Reliable test**: Ensure your test case is reproducible and reliable
2. **Accurate marking**: Mark good/bad commits correctly during bisect
3. **Clear criteria**: Know exactly what you're looking for
4. **Review results**: Always inspect the identified commit
5. **Document findings**: Note the problematic commit for team
6. **Test surroundings**: Check commits before and after

## Error Handling

The commands handle these common scenarios:

- **Not a git/jj repository**: Shows error and exits
- **No history available**: Reports when repository is empty
- **Uncommitted changes (git)**: Warns user to commit or stash first
- **Unstable bisect**: Suggests testing more commits if results vary
- **All commits tested**: Reports complete bisect with full details
- **Bisect abortion**: Safe cleanup of bisect state

## Reference Materials

Load these references as needed for detailed command information:

- **Git bisect commands**: `git bisect start`, `good`, `bad`, `skip`, `abort`
- **Jujutsu change references**: Understanding change IDs and descriptions
- **History query syntax**: For filtering commits/changes by author, date, message
- **VCS auto-detection**: How the skill detects git vs jj at runtime

## Integration with Other Commands

**Related plugins/skills:**
- `/branch-workflow:create-branch` - Create new branches/changes for fixes
- `/branch-workflow:switch-branch` - Switch during bisect investigation
- `/merge-workflow:rebase` - Prepare bisect findings for merge
- `/review-prep:cleanup-history` - Clean up after bisect investigation

**Typical debugging workflow:**
1. Run tests and identify failure
2. Bisect with `/history-detective:bisect` to find problem commit
3. Review identified commit and its changes
4. Create fix branch with `/branch-workflow:create-branch`
5. Implement fix and test
6. Prepare for review with `/review-prep:cleanup-history`

## Limitations

- Bisect requires testable commits (can't test all commits)
- File evolution shows only content changes, not structural refactors
- Blame analysis limited to recent history (very old changes may be lost)
- Branch comparison doesn't show merge commit details
- Intermittent failures may require manual testing validation

## Future Enhancements

- Automated test execution during bisect
- Smart blame analysis with heuristics
- File lineage tracking (renames/moves)
- Intelligent merge conflict prediction
- Integration with CI/CD for automated bisect
- Change causality analysis and dependency tracking
