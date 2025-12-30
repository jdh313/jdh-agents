# History Detective Plugin

Investigate git and jj repository history with bisect, blame, file evolution tracking, and branch comparison tools with VCS auto-detection.

## Features

- **VCS Auto-Detection**: Automatically detects git or jj repositories
- **Bisect Operations**: Binary search for commits that introduced bugs or regressions
- **Blame Analysis**: Find who made changes and understand the context
- **File Evolution**: Track how files have changed over time
- **Branch Comparison**: Compare history and differences between branches/changes
- **Clear Feedback**: Visual reports and detailed analysis of historical changes

## Commands

### Bisect

Find the commit that introduced a bug or regression using binary search.

**Usage:**
```
/history-detective:bisect
```

**What it does:**
1. Detects your VCS (git or jj)
2. Initiates bisect workflow
3. Guides you through testing commits
4. Identifies the exact commit that introduced the issue
5. Shows the commit details and author information

**When to use:**
- You need to find which commit introduced a bug
- A regression appeared recently but you're not sure when
- You want to narrow down changes across many commits
- You need to blame a specific feature for problems

**Example:**
```bash
# Find the commit that broke a test
/history-detective:bisect

# When prompted, indicate if the current commit is good or bad
# Bisect automatically narrows the range
```

## Supported VCS

- **Git**: Tested with git 2.30+
- **Jujutsu**: Tested with jj 0.10+

## VCS-Specific Behavior

### Git

- Uses `git bisect` workflow for binary search
- Automatically checkouts commits for testing
- Shows commit hash, author, date, and message
- Can bisect across all commits or specific ranges
- Supports `git bisect skip` for untestable commits

### Jujutsu

- Uses `jj log` and change references for historical traversal
- Binary search through change history
- Tracks change IDs and descriptions
- Can traverse parent-child relationships
- Immutable change history ensures consistency

## History Analysis Commands (Coming Soon)

These commands are planned for future releases:

- **`/history-detective:blame`** - Blame analysis for specific lines of code
- **`/history-detective:file-evolution`** - Track how a file has changed over time
- **`/history-detective:branch-compare`** - Compare history between branches

## Error Handling

The commands handle these common scenarios:

- **Not a git/jj repository**: Shows error and exits
- **No history available**: Reports when repository is too new
- **Unstable bisect**: Suggests testing additional commits
- **All commits tested**: Reports the bisect result with full details
- **Bisect abort**: Allows safe cancellation and cleanup

## Safety Considerations

### Best Practices

1. **Test thoroughly**: Ensure your test case is reliable and reproducible
2. **Mark commits accurately**: Correctly identify good vs bad commits during bisect
3. **Review results**: Always inspect the identified commit before taking action
4. **Document findings**: Note the problematic commit for team reference
5. **Check context**: Look at surrounding commits to understand impact

### When NOT to Use Bisect

- When you have uncommitted changes (git)
- On repositories with non-linear history
- When you're not sure how to test for the issue
- If you can't reliably reproduce the problem

## Related Commands

- **Create Branch/Change**: `/branch-workflow:create-branch`
- **Switch Branch**: `/branch-workflow:switch-branch`
- **Merge/Rebase**: `/merge-workflow:rebase`
- **Review Prep**: `/review-prep:cleanup-history`

## Requirements

- **Git**: Version 2.30 or later
- **Jujutsu**: Version 0.10 or later
- Clean or staged working directory for initial bisect setup
- Ability to test commits (reproducible test case)

## Limitations

- Interactive bisect editing not fully supported
- Manual commit checkout may be needed in complex scenarios
- Skipped commits don't count toward final narrow-down
- For git, bisect range limited to linear history

## Future Enhancements

- Blame analysis for specific lines
- File evolution tracking with diffs
- Branch history comparison
- Automated blame reports
- Integration with code review systems
- Change causality analysis
