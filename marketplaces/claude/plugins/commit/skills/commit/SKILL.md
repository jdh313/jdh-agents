---
name: commit
description: >-
  INVOKE BY DEFAULT for all commit-related requests. Handles single commits,
  atomic splitting, message review against the repo's style, and retrofitting
  working-copy edits into prior commits (jj absorb / git fixup). Works with both
  git and jj (Jujutsu).
when_to_use: >-
  Automatically use this skill whenever the user asks to create commits, write
  commit messages, review/improve messages, split changes into atomic commits,
  or move an edit into an earlier commit. Required for "commit these changes,"
  "write a commit message," "improve this message," "split these commits," "this
  belongs in the last commit," or any variation requesting commit operations.
allowed-tools:
  - 'Bash(git:*)'
  - 'Bash(jj:*)'
  - 'Bash(test:*)'
  - Read
  - Grep
  - Glob
---

# Commit

## Overview

Create atomic commits with properly formatted messages that match the repo's conventions. One skill, four workflows: single commit, split into atomic commits, review a message, retrofit edits into earlier commits.

The body below is VCS-agnostic. All concrete commands live in the per-VCS workflow references — after detection, load exactly one of them plus one style reference, and execute its recipes.

**This skill is invoked BY DEFAULT for ALL commit-related requests.** It is also directly invocable as `/commit`.

## Detection: VCS and Commit Style

**Before doing anything else, determine two things: which VCS and which commit message style.**

Run the algorithm in `references/detection.md` — it reads the active agent-guidance files for explicit declarations and auto-detects whatever isn't declared (repository guidance always wins over inference). It also resolves the Co-Authored-By policy and issue-ref placement, and documents the rest of the house style (no trailing periods, imperative mood, body ≤5 lines).

After detection, load the matching workflow reference (`references/git-workflow.md` or `references/jj-workflow.md`) and style reference (`references/conventional-commits.md` or `references/freeform-commits.md`). Every "execute per your VCS recipe" instruction below refers to the loaded workflow reference.

## Workflow Decision Tree

```
User request --> Which workflow?
    |-- "split commits" / "break this into commits"            --> Workflow A: Split and Compose
    |-- "improve/review my message" (provides a message)       --> Workflow C: Review and Improve
    |-- "this belongs in an earlier commit" / amend / fixup    --> Workflow D: Retrofit
    +-- "commit" / "write message" (no message provided)       --> Workflow B: Single Commit
```

## Core Principles

### Atomic Commits

An atomic commit should:
- Focus on **one single unit of work**
- Be **independently reversible** without causing unrelated issues
- Have a clear, singular purpose
- Contain all related changes for that purpose

### Bundle-vs-Split Rules

These override file-based intuition — atomicity is about logical coupling, not file count.

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

**Don't over-split.** A typo fix and the test that catches the same typo are one commit. **Don't under-split.** A 200-line diff doing two unrelated things is two commits, even if "they both touched billing.py."

### Commit Message Quality

Regardless of style (conventional or freeform), good commit messages:
- Use imperative mood ("add" not "added" or "adds")
- Are concise and specific (not vague like "update stuff")
- Explain WHY in the body when context is needed (the diff shows WHAT)
- Keep the body to 3-5 lines maximum for scannability

See the loaded style reference for style-specific rules.

---

## Workflow A: Split and Compose

Use when the user wants changes split into multiple atomic commits.

1. **Detect and check state** — run detection, then inspect current changes (see "Checking state" in your VCS recipe).
2. **Identify atomic units** — apply the bundle-vs-split rules above. Present the recommended split with reasoning grounded in those rules ("bundling X with Y because reverting X alone would break Z" / "splitting A from B because A is a pure formatter sweep"). Get user confirmation.
3. **Create commits one unit at a time** — follow the "Splitting" recipe in your VCS recipe. If two logical changes share a file, use the "Two logical changes in one file" recipe instead of bundling by default.
4. **Compose each message** from the loaded style reference.
5. **Verify** — confirm via the recipe's verification commands that every change landed in a commit and nothing was lost.

## Workflow B: Single Commit

Use when the user wants one commit for current changes.

1. **Detect and check state.**
2. **Analyze changes** — what changed, why, and whether it is ONE atomic unit. If not atomic, say so and offer Workflow A instead.
3. **Compose the message** from the loaded style reference.
4. **Create the commit** per your VCS recipe.
5. **Verify** the commit exists and the remaining state is what you expect.

## Workflow C: Review and Improve Message

Use when the user provides a commit message for review.

1. **Receive the draft message.** If none was provided, ask for it.
2. **Detect commit style** and load the style reference.
3. **Peek at the diff** — style-only review only catches surface issues; a real review checks whether the message's claims match the actual change. Read the working-copy/staged diff per your VCS recipe (cap at ~200 lines). If no diff is available (not in a repo, no changes), proceed with style-only review and say so. If a diff is available, check:
   - **Type match (conventional):** does `feat:` actually add behavior? Does `fix:` fix something? Does `refactor:` preserve behavior?
   - **Scope honesty:** `fix: resolve memory leak` on a diff that only adds tests is a mismatch.
   - **Specificity:** if the diff touches one function or module, the message can name it.
   - **Hidden bundling:** if the diff contains multiple atomic units, recommend Workflow A instead of approving the message.
   Don't paste the diff back at the user — use it as context for sharper feedback.
4. **Analyze against the detected style.**
   - Universal: purpose clear? imperative mood? concise and specific? body explains WHY? body ≤5 lines? `Co-Authored-By:` footer matches detected policy (always strip AI/tool footers; keep human pairing footers when the policy is `keep` / CLAUDE.md mandates it / history uses it)? no trailing period? issue refs match detected placement (default PR-only; keep `(TEAM-123)`/`#123` in summary if CLAUDE.md declares it or history uses it)?
   - Conventional additionally: proper type? type appropriate for the change (verify against the diff if visible)? lowercase?
5. **Provide feedback** in this shape: original message → issues identified → improved version → changes made. If the message's claims don't match the visible diff, flag that prominently — it's the highest-value catch of this workflow.
6. **Offer to commit** with the improved message if the user wants.

## Workflow D: Retrofit into an Earlier Commit

Use when working-copy edits logically belong to an existing commit: "add this to the last commit," review-feedback touch-ups across a stack, a forgotten test for something already committed.

1. **Detect and check state.**
2. **Identify the target commit(s)** — which prior commit does each edit belong to? If an edit is genuinely new work, it stays out of this workflow (commit it normally).
3. **Author check:** before retrofitting into or amending any commit, inspect its author (see "Author check before rewriting" in your VCS recipe). If the target was authored by someone other than the current user, warn and require explicit confirmation before proceeding.
4. **Apply the retrofit** per the "Retrofit" recipe in your VCS recipe (`jj absorb` / squash-into for jj; `--amend` / fixup + autosquash for git).
5. **Safety gate:** never rewrite commits that have been pushed to a shared branch without explicit user confirmation. The VCS recipes state how to check.
6. **Verify** the edits landed in the intended commits and descendants are intact.

---

## Safety Rules

**These rules are mandatory. Violating them can result in lost work.**

### Never Discard Changes Without Permission

The goal of this skill is to organize changes into commits, NOT to delete them. All working-copy changes must be preserved — moved between commits, never discarded.

### Forbidden Operations

The following discard uncommitted changes and **must NEVER be used** without explicit user permission (the plugin's hook also blocks them):

| Command | Risk | Safe Alternative |
|---------|------|------------------|
| `jj restore` | Discards working-copy changes | `jj split` or `jj describe` |
| `jj abandon` (on a non-empty change) | Discards the change's content | `jj describe` + `jj new`, or `jj squash` |
| `git checkout <rev> -- <path>` / `git checkout -- <path>` | Discards working-tree changes for the listed paths | Stage/commit first, or `git stash` |
| `git checkout .` | Discards ALL working-tree changes (bare `.` pathspec) | Stage/commit first, or `git stash` |
| `git restore <file>` / `git restore .` | Discards working-tree changes | `git restore --staged` to unstage; stash to set aside |
| `git restore --staged --worktree <file>` | `--worktree` discards working-tree changes even alongside `--staged` | `git restore --staged <file>` only (no `--worktree`) |
| `git reset --hard` / `--merge` | Discards all uncommitted changes | `git stash` or commit first |
| `git stash drop` / `git stash clear` | Destroys the stash's recoverable safety copies | `git stash list` to review; drop only with explicit user approval |

### Confirmation Required for Destructive Operations

If the user explicitly requests an operation that would discard changes: warn what will be lost, list the specific files, and proceed only after an explicit "yes."

### Summary: The Safe Commit Workflow

1. **Analyze** all changes to identify atomic units
2. **Organize** changes into commits using your VCS recipe
3. **Preserve** all changes — every modification ends up in a commit
4. **Verify** nothing was lost (`git status` / `jj status`)

**If you're unsure whether an operation will discard changes, ASK before executing.**

---

## Reference Materials

- `references/detection.md` — VCS + commit-style detection algorithm and house style rules
- `references/git-workflow.md` — git decision card: staging, splitting, retrofit (fixup/autosquash), stacking, recovery
- `references/jj-workflow.md` — jj decision card: describe/split/squash, retrofit (absorb), stacking, recovery
- `references/conventional-commits.md` — conventional message format and type selection
- `references/freeform-commits.md` — freeform message guidelines
