---
name: commits
description: INVOKE BY DEFAULT for all commit-related requests. Automatically use this skill whenever the user asks to create commits, write commit messages, review/improve messages, or work with version control commits. Handles splitting changes into atomic commits, writing properly formatted commit messages matching the repo's style, and reviewing/improving user-provided messages. Works with both git and jj (Jujutsu). Required for "commit these changes," "write a commit message," "improve this message," "review my commit message," or any variation requesting commit operations.
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Bash(test:*)
  - Read
  - Grep
  - Glob
---

# Commits

## Overview

Create atomic commits with properly formatted commit messages that match the repo's conventions. This skill helps split changes into logical units of work and write clear, well-structured commit messages.

**This skill is invoked BY DEFAULT for ALL commit-related requests.**

**Supports:** git and jj (Jujutsu)

**Explicit commands available:**
- `/commits:commit` - Create a single commit (immediate VCS detection)
- `/commits:split` - Split into atomic commits (immediate VCS detection)
- `/commits:review` - Review/improve a commit message

## Detection: VCS and Commit Style

**Before doing anything else, determine two things: which VCS and which commit message style.**

Run the algorithm in `references/detection.md` — it reads the repo's CLAUDE.md for explicit declarations and auto-detects whatever isn't declared. The detection reference also documents the project-wide house style (no `Co-Authored-By` footers, no trailing periods, imperative mood, body ≤5 lines).

After detection, load the matching workflow + style references named in that file.

## When to Use This Skill

**Automatic invocation for:**
- Any request to create commits: "commit these changes," "make a commit"
- Any request for commit messages: "write a commit message," "compose a message"
- Any request to split commits: "split these commits," "break this into commits"
- Any request to review/improve messages: "improve this message," "review my commit message"
- Any commit workflow: "help me commit," "I need to commit my work"

## Core Principles

### Atomic Commits

An atomic commit should:
- Focus on **one single unit of work**
- Be **independently reversible** without causing unrelated issues
- Have a clear, singular purpose
- Contain all related changes for that purpose

**Examples of atomic commits:**
- Add a new API endpoint (routes + handler + tests)
- Fix a specific bug (the fix + related test updates)
- Refactor a module (all changes needed for the refactor)

**Anti-patterns (non-atomic):**
- Mixing feature + bug fix in one commit
- Partial implementations that break without later commits
- Unrelated changes bundled together

### Commit Message Quality

Regardless of style (conventional or freeform), good commit messages:
- Use imperative mood ("add" not "added" or "adds")
- Are concise and specific (not vague like "update stuff")
- Explain WHY in the body when context is needed (the diff shows WHAT)
- Keep the body to 3-5 lines maximum for scannability

See the detected format reference for style-specific rules.

## Workflow Decision Tree

Determine the workflow based on user request:

```
User request --> Which workflow?
    |-- "split commits" or "split and compose" --> Workflow A: Split and Compose
    |-- "improve/review my message" (provides message) --> Workflow C: Review and Improve
    +-- "commit" or "write message" (no message provided) --> Workflow B: Single Commit
```

---

## Workflow A: Split and Compose

Use this workflow when user requests splitting changes into multiple atomic commits.

### Step 1: Detect VCS/Style and Check State

Run the detection flow above, then check the current state to see all changes.

### Step 2: Identify Atomic Units

Apply the **bundle-vs-split rules** below. They override file-based intuition — atomicity is about logical coupling, not file count.

**BUNDLE (one commit) when changes are coupled:**

- Source change + the test that proves it
- Refactor + the rename it forces across call sites
- Bug fix + its regression test
- Migration script + the model/schema change it migrates
- Lockfile bump + the dependency line that triggered it
- Type signature change + the call sites updated to satisfy it
- API change + the client code that had to adapt

If applying *one half* of these would leave the repo broken or red, they're a single commit.

**SPLIT (separate commits) when changes are independent:**

- Formatter/whitespace sweep alongside a feature → split (the sweep is noise; reviewing the feature requires reading past the formatting)
- Unrelated bug fixes that landed in the same session → split
- Refactor + new feature on top of it → split (the refactor should stand alone, reviewable + revertable)
- Doc updates that aren't *about* this change → split
- "While I was in here" cleanup that's tangential to the main change → split
- Multiple independent features → split

**Litmus test:** Could a reviewer revert this commit alone without breaking the build or surprising future readers? If yes, it's atomic. If reverting it would orphan other changes, bundle.

**Don't over-split.** A typo fix and the test that catches the same typo are one commit. Three lines that move together belong together.

**Don't under-split.** A 200-line diff doing two unrelated things is two commits, even if "they both touched billing.py."

Present the recommended split to the user with reasoning grounded in these rules ("bundling X with Y because reverting X alone would break Z" / "splitting A from B because A is a pure formatter sweep").

### Step 3: Create First Atomic Commit

**For git:** Stage the files for the first commit, then commit.

**For jj:** Split the files into a new change with description.

See the VCS-specific reference for exact commands.

### Step 4: Write Commit Message

Read the detected format reference and compose a message following that style.

### Step 5: Repeat for Remaining Changes

Continue creating atomic commits until all changes are committed.

**Final verification:** Check that the working tree is clean (git) or the change is empty/described (jj).

---

## Workflow B: Single Commit

Use this workflow when user wants one commit for current changes.

### Step 1: Detect VCS/Style and Check State

Run the detection flow above and check what changes will be included.

### Step 2: Analyze Changes

Review the changes to understand:
- What changed (files, functions, logic)
- The purpose of the change (bug fix, new feature, refactor, etc.)
- Whether it represents a single unit of work

If changes are **not atomic** (multiple unrelated changes), recommend splitting and offer to use Workflow A instead.

### Step 3: Write Commit Message

Read the detected format reference and compose the commit message in the appropriate style.

### Step 4: Create Commit

**For jj:**
```bash
jj commit -m "<message>"   # describes @ and creates new empty change on top
```

**For git:**
```bash
git add <files>
git commit -m "<message>"
```

See the VCS-specific reference for details (in particular, the `jj-workflow.md` decision card covers when to reach for `jj squash`, `jj split`, bookmarks, and `jj git push`).

### Step 5: Verify

Confirm the commit was created and check the state.

---

## Workflow C: Review and Improve Message

Use this workflow when user provides a commit message and asks for review or improvement.

### Step 1: Receive User's Message

User provides their draft commit message.

### Step 2: Detect Commit Style

Run the detection flow to determine the repo's convention.

### Step 3: Analyze Against Detected Style

Read the appropriate format reference and evaluate the message.

**Universal checks (both styles):**
- Is the purpose immediately clear?
- Is it in imperative mood? ("add" not "added" or "adds")
- Is it concise and specific?
- If body exists, does it explain WHY (not just repeat WHAT)?
- Is the body concise (typically 3-5 lines for scannability)?

**Additional checks for conventional style:**
- Does it have a proper type prefix? (feat, fix, chore, etc.)
- Is the type appropriate for the change?
- Is it lowercase and without a trailing period?

### Step 4: Provide Feedback and Improvements

Present analysis in this format:

**Original message:**
```
[User's message]
```

**Issues identified:**
- [List specific problems]

**Improved version:**
```
[improved message in the detected style]
```

**Changes made:**
- [Explain what was changed and why]

### Step 5: Confirm and Commit (Optional)

If user wants to proceed, detect VCS and create the commit.

---

## Safety Rules

**These rules are mandatory. Violating them can result in lost work.**

### Never Discard Changes Without Permission

The primary goal of this skill is to organize changes into commits, NOT to delete them. All working copy changes must be preserved — moved between commits, never discarded.

### Forbidden Operations

The following commands discard uncommitted changes and **must NEVER be used** during commit workflows without explicit user permission:

| Command | Risk | Safe Alternative |
|---------|------|------------------|
| `jj restore` | Discards working copy changes | `jj split` or `jj describe` |
| `jj restore <file>` | Discards changes to specific file | Move file to different commit with `jj split` |
| `jj abandon` (on change with modifications) | Discards all modifications in the change | `jj describe` + `jj new` |
| `git checkout -- <file>` | Discards working copy changes to file | Stage/commit first, or `git stash` |
| `git restore <file>` | Discards working copy changes to file | Stage/commit first, or `git stash` |
| `git restore .` | Discards ALL working copy changes | Stage/commit first, or `git stash` |
| `git reset --hard` | Discards all uncommitted changes | `git stash` or commit first |

### Safe Splitting Patterns

**For jj (Jujutsu):**
```bash
# CORRECT: Single atomic change — describe and start fresh
jj commit -m "first change"

# CORRECT: Peel off a subset of files as their own commit
jj split <file1> <file2> -m "second change"
# -m describes the SELECTED (split-off) commit; remaining changes become a new
# child working copy. See references/jj-workflow.md for full -m semantics.

# WRONG: Never use restore to "clean up"
jj restore  # FORBIDDEN - discards changes (blocked by plugin hook)
```

**For git:**
```bash
# CORRECT: Stage and commit specific files, leaving others for later
git add <file1> <file2>
git commit -m "first change"
# Remaining changes stay in working copy

# CORRECT: Stash if you need to set aside changes temporarily
git stash push -m "WIP: changes for later"
git stash pop  # Restore when ready

# WRONG: Never discard working copy changes
git checkout -- .  # FORBIDDEN - discards changes!
git restore .      # FORBIDDEN - discards changes!
```

### Confirmation Required for Destructive Operations

If a user explicitly requests an operation that would discard changes, you **MUST**:

1. Warn them clearly what will be lost
2. List the specific files/changes that will be discarded
3. Ask for explicit confirmation before proceeding

Only proceed after receiving explicit "yes" confirmation.

### Summary: The Safe Commit Workflow

1. **Analyze** all changes to identify atomic units
2. **Organize** changes into commits using staging (git) or split (jj)
3. **Preserve** all changes — every modification ends up in a commit
4. **Verify** no changes were lost with `git status` or `jj status`

**If you're unsure whether an operation will discard changes, ASK before executing.**

---

## Reference Materials

Load these references as needed:

- `references/detection.md` - VCS + commit-style detection algorithm and house style rules
- `references/conventional-commits.md` - Conventional commit message format and type selection guide
- `references/freeform-commits.md` - Freeform commit message guidelines
- `references/git-workflow.md` - Git-specific commands for staging, committing, splitting
- `references/jj-workflow.md` - Jujutsu-specific commands for describing, splitting, managing changes
