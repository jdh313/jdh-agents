# Jujutsu (jj) Workflow Reference

A decision card for jj commit operations — read this once and you should not need `jj --help` mid-task.

## What's different from git (one paragraph)

In jj, the working copy *is* a commit (called the "current change", denoted `@`). There's no staging area. Every edit you make is already part of `@`. You commit by **describing** `@` and creating a new empty change on top (`jj commit -m "..."`, or the two-step `jj describe -m "..."` + `jj new`). You "split" by moving some of `@`'s content into a separate commit. Bookmarks are jj's equivalent of git branches; they don't move automatically, so you advance them deliberately before `jj git push`.

## Checking state

```bash
jj status          # what's in @ (the working copy change)
jj diff            # @'s diff — this is also the "diff peek" source for message review
jj log --limit 10  # recent history / stack shape
```

There is no staging area, so there's no staged-vs-unstaged distinction: `jj diff` is the whole picture.

## Operation → Command

Pick the row that matches what you want to do.

| Goal | Command | Notes |
|------|---------|-------|
| Record `@`'s contents and start a fresh change | `jj commit -m "msg"` | Equivalent to `jj describe -m "msg" && jj new`. Working copy becomes a new empty child. |
| Record `@`, but stay on it | `jj describe -m "msg"` | Just attaches the description. No new change created. |
| Split one or more files out of `@` into a separate commit | `jj split <file1> <file2> -m "msg for the split-off part"` | See **`-m` semantics** below. |
| Split `@` into two commits interactively | `jj split` (no args, no `-m`) | Opens diff editor — **avoid in agent contexts**. Provide filesets instead. |
| Combine `@` into its parent | `jj squash` | `@` is abandoned if it becomes empty. |
| Combine `@` into its parent with a new combined message | `jj squash -m "combined msg"` | Replaces parent's description. |
| Move a hunk from one commit to another (non-adjacent OK) | `jj squash --from <src> --into <dst>` | Or `jj squash --from <src> --into <dst> <files>` for path-scoped moves. |
| Distribute `@`'s edits into the ancestors that last touched those lines | `jj absorb` | Hunk-precise, automatic targeting. See **Retrofit** below. |
| Absorb only some paths | `jj absorb <fileset>` | Same, restricted to the listed paths. |
| Fix the description on `@` | `jj describe -m "new msg"` | Idempotent — replaces existing description. |
| Fix the description on `@`'s parent | `jj describe -r @- -m "new msg"` | `@-` is the parent of the working copy. |
| Fix the description on any commit | `jj describe -r <revset> -m "new msg"` | jj rewrites cleanly even for old changes. |
| Create a new empty change on top of current | `jj new` | Working copy moves to the new empty child. |
| Create a new change on top of a specific commit | `jj new <revset>` | E.g. `jj new main` to start fresh from main. |
| Resume working on an old change | `jj new <revset>` then make edits — or `jj edit <revset>` | Prefer `jj new`; `jj edit` is discouraged by jj itself. |
| List bookmarks | `jj bookmark list` | Or `jj b l`. |
| Move a bookmark to a revision | `jj bookmark move <name> --to <revset>` | E.g. `jj bookmark move main --to @-` to point main at the parent of the working copy. |
| Create a new bookmark at current change | `jj bookmark create <name> -r @-` | Usually point at `@-` (last described change), not `@` (empty working copy). |
| Push tracked bookmarks to git | `jj git push` | Pushes bookmarks ahead of their remote counterparts. |
| Push a specific bookmark | `jj git push --bookmark <name>` | Force-with-lease semantics. Safe by default. |
| Push the current change as an ad-hoc branch | `jj git push --change @-` | Generates a `push-XXX` bookmark from the change ID. |
| Undo the last jj operation | `jj undo` | jj's operation log makes mistakes recoverable — use this freely. |

## `jj split` -m semantics (subtle, get it wrong every time without this)

`jj split <files> -m "msg"` does two things:

1. The **selected files** stay in the original commit's position (which becomes the **parent** in the default layout). `-m` describes **this** commit.
2. The **remaining changes** move to a **new child** commit, with no description. The working copy (`@`) is now this new child.

So when splitting a refactor out of a feature change:

```bash
# @ contains both refactor (db.js) and feature (handler.js + tests)
jj split src/db.js -m "refactor: extract connection pool"
# now: @-  = refactor (described)
#      @   = feature (working copy, undescribed)

jj describe -m "feat: add auth endpoint"
# now: @-  = refactor (described)
#      @   = feature (described, working copy)
```

If you instead want the split-off part to become the **child** (newer commit) and the remaining part to stay as the parent, pass `--parallel` or `--insert-after`.

## Topology after `jj split`

| Flag | Layout |
|------|--------|
| (default) | Selected → parent. Remaining → child (becomes `@`). Linear: `J → selected → remaining(@)`. |
| `--parallel` / `-p` | Selected and remaining become siblings (both children of `J`). Working copy is the remaining one. |
| `--insert-after <rev>` / `-A` | Selected commit is inserted as a child of `<rev>`; remaining stays where `@` was. |
| `--insert-before <rev>` / `-B` | Selected commit is inserted as a parent of `<rev>`; remaining stays where `@` was. |

For atomic-commit workflows, the **default layout is what you want**: split off a piece, then describe what's left.

## `jj commit` vs `jj split` (when to use which)

| Situation | Command |
|-----------|---------|
| `@` is a single atomic unit, ready to commit | `jj commit -m "msg"` |
| `@` mixes multiple units; you want to peel off a subset | `jj split <files> -m "msg"`, then `jj describe -m "msg"` for what remains, then `jj new` |
| `@` mixes multiple units; you want to commit ALL of them as separate atomic units | Loop: `jj split <files> -m "msg"` per unit, finishing with `jj describe -m "msg"` for the last leftover |

## Retrofit: edits that belong in an earlier commit

jj's answer to git's amend/fixup, and usually better. Pick by how much you know about the target:

| Situation | Command |
|-----------|---------|
| Edits in `@` belong to whichever stack commits last touched those lines | `jj absorb` |
| Only some files should be absorbed | `jj absorb <fileset>` |
| Restrict candidate targets | `jj absorb --into <revset>` |
| You know exactly which commit an edit belongs to | `jj squash --into <rev> [<files>]` |
| The edit belongs in `@`'s parent | `jj squash [<files>]` |

How `jj absorb` works: for each changed hunk in `@`, it finds the closest **mutable** ancestor whose diff last modified those lines and squashes the hunk there. Hunks with no unambiguous target (new lines, lines owned by immutable commits, or lines touched by multiple candidates) **stay in `@`** — absorb never guesses.

After absorbing:

```bash
jj op show -p     # review exactly what moved where
jj status         # whatever's left in @ had no unambiguous target
jj undo           # if the result is wrong
```

For leftovers, fall back to `jj squash --into <rev> <file>` (moves the whole file's diff — not hunk-precise) or commit them as new work.

Descendants are rebased automatically — no manual rebase step after any of these.

**Safety:** absorb only targets `mutable()` revisions, so pushed-to-trunk commits are protected by default. Still confirm with the user before retrofitting into any commit that's already on a shared remote bookmark (`jj log -r 'remote_bookmarks()..@'` shows what's local-only).

## Two logical changes in one file

`jj split <files>` is file-granular and interactive split is off-limits for agents. When one file mixes change A and change B:

1. **Prefer `jj absorb`** when A or B belongs to an existing stack commit — absorb is hunk-precise and handles this case outright.
2. **Edit-split-restore** when both changes are new:
   ```bash
   jj diff <file>                       # capture both changes in the transcript first
   # 1. Edit the file to temporarily remove change B (leave only A)
   jj split <file> -m "msg for A"       # A goes to the parent; @ keeps the other files
   # 2. Re-apply change B by editing the file again
   ```
   Every working-copy state is snapshotted in the op log, so if re-applying B goes wrong, `jj op log` + `jj op restore <id>` recovers the original A+B state. This is editing, not discarding — the hook-blocked commands stay unused.
3. **Accept the bundle** when A and B are small and genuinely entangled (same lines). Note the bundling in the commit body rather than fighting it.

## Stacked-change hygiene

Working as a stack of described changes (one reviewable slice per commit):

- **Inspect the stack:** `jj log -r 'trunk()..@'` — everything local on top of trunk.
- **Mid-stack edits don't need rebases:** fix from `@` with `jj absorb` or `jj squash --into <rev>`; jj rebases all descendants automatically. This is the workflow git's fixup/autosquash approximates manually.
- **Conflicts don't stop you:** a mid-stack rewrite may leave descendants conflicted — jj records the conflict *in* the commit and `jj log` marks it. Resolve with `jj new <conflicted-rev>`, fix the files, `jj squash`.
- **One bookmark per reviewable slice:** `jj bookmark create <name> -r <rev>`, advance with `jj bookmark move <name> --to <rev>` after rewrites (bookmarks don't follow rewritten commits to new heads automatically — check `jj log` for where they point).
- **Push:** `jj git push` pushes all ahead bookmarks; `jj git push --change <rev>` for an ad-hoc `push-*` bookmark per slice.
- Keep `@` as an empty undescribed change on top of the stack between tasks (`jj new` after each described slice).

## Hard rules for agent use

1. **Never invoke commands that open an editor.** Always pass `-m "msg"` for descriptions. The dangerous incantations:
   - `jj describe` (no `-m`) → opens editor
   - `jj split` (no filesets, no `-m`) → opens diff editor
   - `jj commit -i` (interactive) → opens diff editor
   - `jj squash -i` → opens diff editor
2. **Never use `jj restore` or `jj abandon` on a non-empty change** — both discard content. The commit plugin's hook blocks these.
3. **Verify with `jj log` after each split/squash.** jj rewrites history cleanly, so a wrong-shape rewrite is reversible with `jj undo` — but only if you notice in time.

## Splitting a mixed change into atomic commits (full example)

Starting state: `@` contains a refactor, a feature, and a doc tweak.

```bash
jj status                                              # see all changes
jj split src/db.js -m "refactor: extract pool logic"   # @-  = refactor, @ = feature+docs
jj split README.md -m "docs: note pool extraction"     # @-- = refactor, @- = docs, @ = feature
jj describe -m "feat: add auth endpoint"               # @ now described
jj new                                                  # fresh empty change for next work
jj log --limit 5                                       # verify topology
```

Final history (newest first):
```
@   (empty working copy)
@-  feat: add auth endpoint
@-- docs: note pool extraction
@-- refactor: extract pool logic
```

## Pushing work to a git remote

```bash
# 1. Make sure a bookmark points at the change you want to push
jj bookmark list                                  # which bookmarks exist?
jj bookmark move main --to @-                     # advance main to last described change
# (or create one: jj bookmark create feature-x -r @-)

# 2. Push
jj git push --bookmark main
# Or push everything that's ahead:
jj git push
```

For ad-hoc pushes without managing bookmarks:

```bash
jj git push --change @-       # generates a push-<changeid> bookmark and pushes it
```

## Recovery: I think I lost work

```bash
jj undo               # reverts the last jj op (works for almost anything)
jj op log             # full operation log; pick a target with jj op restore <id>
jj op restore <id>    # restore the repo to that point in time
```

jj's operation log makes recovery routine — don't panic, just `jj undo` and try again.
