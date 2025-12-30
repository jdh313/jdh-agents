---
description: Split changes into multiple atomic commits with conventional messages
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Bash([[:*)
  - Bash(if:*)
  - Read
  - Glob
---

# Split and Compose Command

## Immediate Execution

**VCS:** !`[[ -d .jj ]] && echo "jj" || echo "git"`

**All Changes:**
!`if [[ -d .jj ]]; then jj status && echo "---DIFF---" && jj diff; else git status && echo "---DIFF---" && git diff && echo "---STAGED---" && git diff --staged; fi`

## Instructions

Based on the VCS detection and changes shown above:

### Step 1: Identify Atomic Units

Analyze all changes and group them into atomic commits. Consider:

**File-based grouping:**
- Files serving the same purpose (all tests, all configs)
- Related files (source + corresponding test)

**Change-based grouping:**
- Bug fixes vs features vs refactoring
- Independent features
- Related changes forming a complete unit

**Present your analysis:**
```
Recommended atomic commits:
1. [type]: [summary] - [files]
2. [type]: [summary] - [files]
...
```

### Step 2: Get User Confirmation

Ask user to confirm or adjust the proposed split before proceeding.

### Step 3: Create Commits

Read `skills/atomic-commits/references/conventional-commits.md` for message formatting.

For each atomic unit:

**jj workflow:**
```bash
jj split <files> -m "type: summary"
```

**git workflow:**
```bash
git add <files>
git commit -m "type: summary"
```

Read `skills/atomic-commits/references/jj-workflow.md` or `skills/atomic-commits/references/git-workflow.md` for VCS-specific command details.

### Step 4: Handle Remaining Changes

After all splits, describe any remaining changes or confirm working tree is clean.

### Step 5: Verify

Show the commit history to confirm all changes were committed properly:
- **jj**: `jj log --limit 10`
- **git**: `git log --oneline -10`
