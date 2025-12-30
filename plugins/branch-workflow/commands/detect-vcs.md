---
description: Detect which VCS (git or jj) is in use and display the detected system for verification
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
---

# Detect VCS Command

## Immediate Execution

**VCS Detection:**
!`[[ -d .jj ]] && echo "jj" || echo "git"`

**Working Directory:**
!`pwd`

**Repository Status:**
!`if [[ -d .jj ]]; then jj status 2>/dev/null || echo "Not a jj repository"; else git status 2>/dev/null || echo "Not a git repository"; fi`

## Instructions

Based on the detection results above:

### Step 1: Confirm Detected VCS

The detection above shows which VCS system is in use in the current directory:

- **jj**: You're in a Jujutsu repository. Recommended reference file: `skills/branch-workflow/references/jj-commands.md`
- **git**: You're in a Git repository. Recommended reference file: `skills/branch-workflow/references/git-commands.md`

### Step 2: Report Results to User

**If jj was detected:**

Present the findings clearly:
```
✓ Detected VCS: Jujutsu (jj)
  - Repository metadata: .jj directory exists
  - Reference file: skills/branch-workflow/references/jj-commands.md
  - Command type: change operations (jj new, jj edit, jj abandon)
```

**If git was detected:**

Present the findings clearly:
```
✓ Detected VCS: Git
  - Repository metadata: .git directory exists
  - Reference file: skills/branch-workflow/references/git-commands.md
  - Command type: branch operations (git checkout, git branch, etc.)
```

### Step 3: Verify Detection Accuracy

The repository status output above confirms the detection:

- If you see `jj log` output or jj-specific status information, jj detection is correct
- If you see `git` status output or branch information, git detection is correct
- If you see "Not a X repository" message, the system is not set up correctly

### Step 4: Next Steps

Based on the detected VCS, the skill knows to use the appropriate commands for:

- **Branch/change creation**: `git checkout -b` vs `jj new -m`
- **Branch/change switching**: `git checkout` vs `jj edit`
- **Branch/change deletion**: `git branch -d` vs `jj abandon`

All subsequent branch-workflow commands will use the detected VCS automatically.

## Detection Logic Explanation

The detection uses this bash check:

```bash
[[ -d .jj ]] && echo "jj" || echo "git"
```

**Why this works:**
- Jujutsu creates a `.jj/` directory in the repository root (similar to how git creates `.git/`)
- Checking for this directory is fast and requires no command execution
- If `.jj` doesn't exist, we default to git (the most common case)

**What it checks:**
- `-d .jj`: Test if the `.jj` directory exists
- `&&`: If true, echo "jj"
- `||`: Otherwise, echo "git"

This is the fastest, most reliable way to detect the VCS in use.
