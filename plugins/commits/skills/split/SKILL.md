---
name: split
description: Split changes into multiple atomic commits with properly formatted messages matching the repo's style
disable-model-invocation: true
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Bash(test:*)
  - Read
  - Glob
---

# Split and Compose Command

## Immediate Execution

### VCS and Style Detection

First, determine the VCS and commit style:

1. **Check CLAUDE.md context** — does the repo specify VCS (jj/git) or commit style (conventional/freeform)?
2. **VCS fallback:** Check if `.jj/` exists (jj) or not (git)
3. **Style fallback:** Analyze the last ~20 commits — if >60% have type prefixes like `feat:`, `fix:`, etc., use conventional style; otherwise use freeform

**For Jujutsu repositories:**
- Run: `jj status`
- Run: `jj diff`

**For git repositories:**
- Run: `git status`
- Run: `git diff` and `git diff --staged`

## Instructions

Based on the detection and changes shown above:

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
1. [summary] - [files]
2. [summary] - [files]
...
```

### Step 2: Get User Confirmation

Ask user to confirm or adjust the proposed split before proceeding.

### Step 3: Create Commits

Read the appropriate format reference based on detected commit style:
- **Conventional:** Read `skills/commits/references/conventional-commits.md`
- **Freeform:** Read `skills/commits/references/freeform-commits.md`

For each atomic unit:

**jj workflow:**
```bash
jj split <files> -m "message"
```

**git workflow:**
```bash
git add <files>
git commit -m "message"
```

Read `skills/commits/references/jj-workflow.md` or `skills/commits/references/git-workflow.md` for VCS-specific command details.

### Step 4: Handle Remaining Changes

After all splits, describe any remaining changes or confirm working tree is clean.

### Step 5: Verify

Show the commit history to confirm all changes were committed properly:
- **jj**: `jj log --limit 10`
- **git**: `git log --oneline -10`
