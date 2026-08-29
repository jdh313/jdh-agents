---
name: resolve-conflicts
description: >-
  Resolve an in-progress merge, rebase, or jj conflict by recovering each side's
  original intent before picking a resolution. Detects git vs jj and follows
  that VCS's own mechanics. Use when the user says "resolve these conflicts",
  "fix the merge conflicts", "this rebase is conflicted", "jj log shows a
  conflict", or when a merge/rebase/squash leaves conflict markers in the tree.
  Adapted from mattpocock/skills (MIT, © 2026 Matt Pocock).
---

# Resolve conflicts

A conflict is two intents that the VCS could not reconcile. Resolving it is a **reading** task before it is an editing task: recover what each side was trying to do, then write the version that serves both.

## 0. Detect the VCS first

**`.jj/` is authoritative.** A jj-colocated repo has *both* `.jj/` and `.git/`, and driving it with git commands corrupts jj's view of the working copy.

```bash
ls -d .jj 2>/dev/null && echo jj || echo git
```

The two VCSs disagree about what a conflict even *is*, so the branch matters at steps 1, 3 and 5:

- **git** — a conflict is a halted operation. The tree holds markers, the merge or rebase is mid-flight, and nothing else can happen until you finish or abort it.
- **jj** — a conflict is *recorded in the commit*. Nothing halts. `jj log` marks the conflicted revision, descendants keep their shape, and you resolve whenever you like.

## Never

Regardless of VCS, these discard work and are blocked here:

- `git reset --hard`, `git checkout -- <path>`, `git restore <path>`
- `jj restore`, `jj abandon` on a non-empty change
- `git merge --abort` / `git rebase --abort` — **always resolve; never abort.** Abandoning the merge throws away the reading you have already done and hands the same conflict back to the next person.

Recovery, if a resolution goes wrong, is `jj undo` / `jj op restore <id>` on jj, and re-editing the file on git. Neither needs a discard command.

## 1. See the current state

**git**

```bash
git status              # which operation is in flight, which paths are unmerged
git log --oneline --graph --left-right HEAD...MERGE_HEAD   # both sides of a merge
git diff --diff-filter=U                                   # the conflicted hunks
```

For a rebase, `REBASE_HEAD` names the commit being replayed and `git rebase --show-current-patch` shows it in full.

**jj**

```bash
jj status                  # conflicted paths in the working copy
jj log -r 'conflicts()'    # every conflicted revision, not just this one
jj resolve --list          # per-path conflict summary (read-only)
```

Check the whole set: a mid-stack rewrite can leave several descendants conflicted at once, and resolving only `@` leaves the rest broken.

## 2. Find the primary sources

For each conflict, understand deeply why each change was made and what the original intent was — before touching a line.

- **Commit messages** on both sides (`git log -p <range>` / `jj show <rev>`). This is the cheapest source and usually the best.
- **The pull request** (`gh pr view <n> --comments`) for the review conversation that shaped the change.
- **The tracking ticket.** Ticket references such as `TEAM-123` resolve through the `linear` plugin; read the ticket body and its comments, not just the title.
- **Prior decisions governing the area.** Run `/ground` on the conflicted subsystem: a conflict between two plausible implementations is often already adjudicated by a decision head, and that head settles the hunk without guesswork.

If a side's intent stays opaque after all four, say so and ask rather than guessing — a wrong resolution is a silent bug with two authors and no reviewer.

## 3. Resolve each hunk

Preserve both intents where possible. Where they are genuinely incompatible, pick the one matching the merge's stated goal and note the trade-off in the commit message. **Do not invent new behaviour** — a conflict resolution is not the place to improve either side. If the right answer is a third thing neither side wrote, resolve to one side first, then make that change as its own separate commit.

**git** — edit the file, remove every marker, then `git add <path>`. `git diff --check` catches leftover markers.

**jj** — do not run bare `jj resolve`; it opens a merge editor, which an agent cannot drive.

```bash
jj new <conflicted-rev>    # a fresh change on top of the conflicted one
# edit the materialised conflict markers out of the files
jj squash                  # fold the resolution into <conflicted-rev>
```

Descendants rebase automatically, so a resolution partway down a stack propagates on its own. Repeat per revision returned by `jj log -r 'conflicts()'`, working oldest-first so each fix has a chance to clear the ones above it.

## 4. Run the project's automated checks

Discover them rather than assuming — typically typecheck, then tests, then format. Fix anything the merge broke. A conflict resolution that compiles is not evidence that it is correct; the test suite is the only thing that reads both intents back.

## 5. Finish

**git** — stage everything and commit. For a rebase, `git rebase --continue` and repeat from step 1 for each remaining conflicted commit until the rebase completes.

**jj** — there is nothing to continue; the resolution landed when you squashed it. Confirm with:

```bash
jj log -r 'conflicts()'   # must come back empty
jj log --limit 10         # confirm the stack shape, and where bookmarks point
```

Bookmarks do not follow rewritten commits, so advance any that lag with `jj bookmark move <name> --to <rev>` before pushing.
