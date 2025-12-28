---
name: atomic-commits
description: INVOKE BY DEFAULT for all commit-related requests. Automatically use this skill whenever the user asks to create commits, write commit messages, review/improve messages, or work with version control commits. Handles splitting changes into atomic commits, writing properly formatted Angular/Conventional Commit messages, and reviewing/improving user-provided messages for standards compliance and clarity. Works with both git and jj (Jujutsu). Required for: "commit these changes," "write a commit message," "improve this message," "review my commit message," or any variation requesting commit operations.
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Read
  - Grep
  - Glob
---

# Atomic Commits

## Overview

Create atomic commits with properly formatted Angular/Conventional Commit messages. This skill helps split changes into logical units of work and write clear, structured commit messages.

**This skill is invoked BY DEFAULT for ALL commit-related requests.**

**Supports:** git and jj (Jujutsu)

**Explicit commands available:**
- `/atomic-commits:commit` - Create a single commit (immediate VCS detection)
- `/atomic-commits:split` - Split into atomic commits (immediate VCS detection)
- `/atomic-commits:review` - Review/improve a commit message

## When to Use This Skill

**Automatic invocation for:**
- Any request to create commits: "commit these changes," "make a commit"
- Any request for commit messages: "write a commit message," "compose a message"
- Any request to split commits: "split these commits," "break this into commits"
- Any request to review/improve messages: "improve this message," "review my commit message"
- Any commit workflow: "help me commit," "I need to commit my work"

**In other words:** This skill should be used for ALL commit operations unless the user explicitly requests to bypass it.

## Detect Version Control System

**Before running any commands, detect which VCS is in use:**

```bash
# Check for .jj directory (fast, no command execution)
[[ -d .jj ]] && echo "jj" || echo "git"
```

**Then load the appropriate reference:**
- **jj detected**: Use `references/jj-workflow.md` for commands
- **git detected**: Use `references/git-workflow.md` for commands

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

### Commit Message Format

Follow Angular/Conventional Commits style:
- Type without scope (feat, fix, chore, docs, etc.)
- Concise summary in imperative mood
- Optional body for context (not required for small, self-explanatory changes)
  - When used, typically 3-5 lines (keeps messages scannable in git log)
  - Explains WHY, not WHAT (the diff shows what changed)

See `references/conventional-commits.md` for detailed format specification.

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

### Step 1: Detect VCS and Check State

First, detect the VCS and load the appropriate reference:

```
Read references/git-workflow.md   # If using git
Read references/jj-workflow.md    # If using jj
```

Check the current state to see all changes.

### Step 2: Identify Atomic Units

Analyze the changes to identify atomic commit candidates. Consider:

**File-based grouping:**
- Files that serve the same purpose (e.g., all test files, all config files)
- Related files changed together (e.g., source + corresponding test)

**Change-based grouping:**
- Bug fixes vs features vs refactoring
- Independent features that don't depend on each other
- Related changes that form a complete unit

**Example analysis:**
```
Changes:
  M src/handler.js       (new endpoint added)
  M src/db.js           (connection pool update)
  M tests/handler.test.js (tests for new endpoint)
  M README.md           (docs for new endpoint)

Recommended atomic commits:
  1. Refactor: db.js connection pool (independent improvement)
  2. Feature: handler.js + tests + README (complete new endpoint)
```

Present the recommended split to the user with clear reasoning.

### Step 3: Create First Atomic Commit

**For git:** Stage the files for the first commit, then commit.

**For jj:** Split the files into a new change with description.

See the VCS-specific reference for exact commands.

### Step 4: Write Commit Message

Read `references/conventional-commits.md` if needed.

Compose a commit message following the format:
- Determine appropriate type (feat, fix, chore, etc.)
- Write clear, imperative summary
- Add body if context needed (not required for simple changes)
  - When used, typically 3-5 lines for scannability

**Template:**
```
<type>: <summary>

[optional body explaining WHY, not WHAT]
```

### Step 5: Repeat for Remaining Changes

Continue creating atomic commits until all changes are committed.

**Final verification:** Check that the working tree is clean (git) or the change is empty/described (jj).

---

## Workflow B: Single Commit

Use this workflow when user wants one commit for current changes.

### Step 1: Detect VCS and Check State

Detect the VCS and check what changes will be included.

### Step 2: Analyze Changes

Review the changes to understand:
- What changed (files, functions, logic)
- The purpose of the change (bug fix, new feature, refactor, etc.)
- Whether it represents a single unit of work

If changes are **not atomic** (multiple unrelated changes), recommend splitting and offer to use Workflow A instead.

### Step 3: Write Commit Message

Read `references/conventional-commits.md` if needed.

Compose the commit message:
1. Determine the appropriate type
2. Write a clear, imperative summary
3. Add body if the change needs context (not required for simple changes)
   - When used, typically 3-5 lines for scannability

### Step 4: Create Commit

**For git:** Stage changes and commit.

**For jj:** Describe the change (and optionally `jj new` to start fresh).

See the VCS-specific reference for exact commands.

### Step 5: Verify

Confirm the commit was created and check the state.

---

## Workflow C: Review and Improve Message

Use this workflow when user provides a commit message and asks for review or improvement.

### Step 1: Receive User's Message

User provides their draft commit message. It may be:
- A simple one-line message
- Multi-line with body
- Formatted (attempting Conventional Commits)
- Unformatted (free-form text)

### Step 2: Analyze Against Standards

Read `references/conventional-commits.md`.

Evaluate the message against Conventional Commits standards:

**Format compliance:**
- Does it have a proper type? (feat, fix, chore, etc.)
- Is the type appropriate for the change?
- Is it in imperative mood? ("add" not "added" or "adds")
- Is it lowercase and concise?
- Does it avoid ending with a period?

**Clarity assessment:**
- Is the purpose immediately clear?
- Does it explain WHAT changed (summary)?
- If body exists, does it explain WHY (not just repeat WHAT)?
- Is the body concise (typically 3-5 lines for scannability)?

**Common issues to check:**
- Past tense: "added feature" --> "add feature"
- Vague: "update stuff" --> "update user authentication logic"
- Wrong type: "feat: fix bug" --> "fix: resolve memory leak"
- No type: "added new endpoint" --> "feat: add user endpoint"
- Uppercase/period: "Fix: Added Feature." --> "fix: add feature"
- Body too verbose: condense for scannability (typically 3-5 lines)

### Step 3: Provide Feedback and Improvements

Present analysis in this format:

**Original message:**
```
[User's message]
```

**Issues identified:**
- [List specific problems with formatting/clarity]

**Improved version:**
```
<type>: <improved summary>

[optional improved body explaining WHY]
```

**Changes made:**
- [Explain what was changed and why]

### Step 4: Confirm and Commit (Optional)

If user wants to proceed with the improved message, use the appropriate VCS commands to create the commit.

**Note:** Always get user confirmation before committing. They may want to iterate on the message further.

---

## ⚠️ Safety Rules

**These rules are mandatory. Violating them can result in lost work.**

### Never Discard Changes Without Permission

The primary goal of this skill is to organize changes into commits, NOT to delete them. All working copy changes must be preserved—moved between commits, never discarded.

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
# CORRECT: Describe current change, then create new for remaining work
jj describe -m "feat: first change"
jj new  # Remaining changes stay in working copy

# CORRECT: Split specific files into a described change
jj split <file1> <file2> -m "fix: second change"
# Remaining changes stay in current working copy

# WRONG: Never use restore to "clean up"
jj restore  # FORBIDDEN - discards changes!
```

**For git:**
```bash
# CORRECT: Stage and commit specific files, leaving others for later
git add <file1> <file2>
git commit -m "feat: first change"
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

**Example confirmation prompt:**
```
⚠️ This will permanently discard the following uncommitted changes:
  - src/handler.js (15 lines modified)
  - tests/handler.test.js (new file, 42 lines)

These changes cannot be recovered. Proceed? (yes/no)
```

Only proceed after receiving explicit "yes" confirmation.

### Summary: The Safe Commit Workflow

1. **Analyze** all changes to identify atomic units
2. **Organize** changes into commits using staging (git) or split (jj)
3. **Preserve** all changes—every modification ends up in a commit
4. **Verify** no changes were lost with `git status` or `jj status`

**If you're unsure whether an operation will discard changes, ASK before executing.**

---

## Best Practices

### Atomic Commit Guidelines
- **One purpose:** Each commit should have a single, clear reason to exist
- **Complete:** Include all changes needed for that purpose (code + tests + docs)
- **Independent:** Should be revertable without breaking unrelated functionality
- **Logical order:** Commit refactoring before features that depend on it

### Commit Message Guidelines
- **Imperative mood:** "add feature" not "added feature" or "adds feature"
- **Lowercase:** Type and summary should be lowercase
- **No period:** Summary should not end with a period
- **Concise:** Summary should be clear but brief
- **Body optional:** Not required for small, self-explanatory changes
- **Body purpose:** When used, explains WHY not WHAT (the diff shows what)
- **Body length:** Typically 3-5 lines for scannability in git log

---

## Reference Materials

Load these references as needed:

- `references/conventional-commits.md` - Commit message format specification and type selection guide
- `references/git-workflow.md` - Git-specific commands for staging, committing, splitting
- `references/jj-workflow.md` - Jujutsu-specific commands for describing, splitting, managing changes
