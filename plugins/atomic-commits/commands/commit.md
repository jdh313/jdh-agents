---
description: Create a single atomic commit with a conventional commit message
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Read
  - Glob
---

# Single Commit Command

## Immediate Execution

**VCS:** !`[[ -d .jj ]] && echo "jj" || echo "git"`

**Status:**
!`if [[ -d .jj ]]; then jj status; else git status; fi`

**Changes:**
!`if [[ -d .jj ]]; then jj diff; else git diff && echo "---STAGED---" && git diff --staged; fi`

## Instructions

Based on the VCS detection and changes shown above:

### Step 1: Analyze the changes

- What files are modified?
- What is the purpose of these changes?
- Do they represent ONE atomic unit of work?

### Step 2: Check atomicity

If changes are **NOT atomic** (multiple unrelated changes):
- Inform the user
- Recommend using `/atomic-commits:split` instead
- Ask for confirmation before proceeding with a single commit

If changes **ARE atomic**, proceed to Step 3.

### Step 3: Compose the commit message

Read `skills/atomic-commits/references/conventional-commits.md` for type selection guidance.

1. Determine the appropriate type (feat, fix, refactor, chore, docs, test, perf, build, ci)
2. Write a clear summary in imperative mood, lowercase, no period
3. Add body only if context is needed (max 5 lines, explain WHY not WHAT)

### Step 4: Create the commit

**For jj (detected above):**
```bash
jj describe -m "<message>"
jj new
```

**For git (detected above):**
```bash
git add <files>
git commit -m "<message>"
```

Read `skills/atomic-commits/references/jj-workflow.md` or `skills/atomic-commits/references/git-workflow.md` for VCS-specific command details.

### Step 5: Verify

Show the created commit and confirm clean state or remaining work.
