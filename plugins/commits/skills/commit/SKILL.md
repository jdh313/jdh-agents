---
name: commit
description: Create a single atomic commit with a properly formatted message matching the repo's style
disable-model-invocation: true
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Bash(test:*)
  - Read
  - Glob
---

# Single Commit Command

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

### Step 1: Analyze the changes

- What files are modified?
- What is the purpose of these changes?
- Do they represent ONE atomic unit of work?

### Step 2: Check atomicity

If changes are **NOT atomic** (multiple unrelated changes):
- Inform the user
- Recommend using `/commits:split` instead
- Ask for confirmation before proceeding with a single commit

If changes **ARE atomic**, proceed to Step 3.

### Step 3: Compose the commit message

Read the appropriate format reference based on the detected commit style:
- **Conventional:** Read `skills/commits/references/conventional-commits.md`
- **Freeform:** Read `skills/commits/references/freeform-commits.md`

Compose the message following that style.

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

Read `skills/commits/references/jj-workflow.md` or `skills/commits/references/git-workflow.md` for VCS-specific command details.

### Step 5: Verify

Show the created commit and confirm clean state or remaining work.
