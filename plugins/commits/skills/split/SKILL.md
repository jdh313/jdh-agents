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

Run the canonical algorithm in `skills/commits/references/detection.md` to determine VCS (git/jj) and commit style (conventional/freeform). It reads CLAUDE.md for explicit declarations and auto-detects whatever isn't declared.

Then check repo state:

- **jj**: `jj status` then `jj diff`
- **git**: `git status` then `git diff` and `git diff --staged`

## Instructions

Based on the detection and changes shown above:

### Step 1: Identify Atomic Units

Apply the **bundle-vs-split rules** documented in `skills/commits/SKILL.md` under "Workflow A → Step 2: Identify Atomic Units". Atomicity is about logical coupling, not file count. Quick checklist:

- **Bundle** when reverting one half would leave the repo broken (source + its test, refactor + the rename it forces, fix + its regression test, migration + the model change it migrates).
- **Split** when one change is noise relative to the other (formatter sweep vs feature, unrelated bug fixes, "while I was in here" cleanups, doc updates not *about* this change).
- **Litmus**: Could a reviewer revert this commit alone without breaking anything? If yes, atomic. If no, bundle.

**Present your analysis:**
```
Recommended atomic commits:
1. [summary] - [files] — bundled because [reason]
2. [summary] - [files] — split from #1 because [reason]
...
```

Ground each row's grouping decision in the litmus test, not in file co-location.

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
