# Git Workflow Reference

A decision card for git commit operations — read this once and you should not need `git --help` mid-task.

## What's different from jj (one paragraph)

Git has a **staging area**: you build each commit by staging files (`git add`), then committing what's staged. Editing history (amend, fixup) rewrites commits, and descendants do NOT follow automatically — that's what `rebase` is for. There is no operation log; recovery runs through `git reflog` and `git stash`, so create safety copies *before* risky rewrites, not after.

## Checking state

```bash
git status            # staged + unstaged overview
git diff              # unstaged changes
git diff --staged     # staged changes — prefer this as the "diff peek" source for message review; fall back to git diff if empty
git log --oneline -10 # recent history
```

## Operation → Command

| Goal | Command | Notes |
|------|---------|-------|
| Stage files for the next commit | `git add <file1> <file2>` | Verify with `git diff --staged` before committing. |
| Commit what's staged | `git commit -m "msg"` | |
| Commit with a body | `git commit -m "$(cat <<'EOF' ... EOF)"` | HEREDOC preserves multi-line formatting. |
| Unstage a file (keep its edits) | `git restore --staged <file>` | The only safe form of `restore` — without `--staged` it discards edits (hook-blocked). |
| Add a forgotten change to the last commit | `git add <file> && git commit --amend --no-edit` | Unpushed commits only. |
| Reword the last commit | `git commit --amend -m "new msg"` | Unpushed commits only. |
| Fix an older commit's content | `git commit --fixup=<sha>` then autosquash | See **Retrofit** below. |
| Verify a commit | `git log -1` / `git show <sha>` | |
| Set changes aside temporarily | `git stash push -m "WIP: ..."` / `git stash pop` | |
| Recover from a bad rewrite | `git reflog` then `git reset` to the old sha | Confirm with the user first — reset variants are guarded. |

## Splitting changes into multiple commits

```bash
git status && git diff           # see everything
git add <files-for-unit-1>
git diff --staged                # verify: only unit 1 staged
git commit -m "msg for unit 1"
# repeat per unit; finish when git status is clean
```

Example — refactor + feature in one working tree:

```bash
git add src/db.js
git commit -m "refactor: extract connection pool logic"
git add src/handler.js tests/handler.test.js
git commit -m "feat: add user authentication endpoint"
```

## Two logical changes in one file

`git add -p` is interactive and **off-limits for agents**. When one file mixes change A and change B, use **edit-stage-restore**:

```bash
git diff <file>            # capture both changes in the transcript first
# 1. Edit the file to temporarily remove change B (leave only A)
git add <file>             # stages the A-only version
# 2. Re-apply change B by editing the file again
git commit -m "msg for A"  # commits A; the working tree now holds only B
```

Unlike jj, git has no op log — the transcript copy of the diff from step 0 is your recovery path if re-applying B goes wrong. This is editing, not discarding; the hook-blocked commands stay unused.

(Generating a partial patch and `git apply --cached` also works but hand-built hunk headers break easily — prefer the edit technique.)

## Retrofit: edits that belong in an earlier commit

| Situation | Command |
|-----------|---------|
| Edit belongs in the last commit | `git add <files> && git commit --amend --no-edit` |
| Edit belongs in an older unpushed commit | `git add <files> && git commit --fixup=<sha>`, then autosquash (below) |
| Several retrofits across a stack | One `--fixup` commit per target, then a single autosquash |

Autosquash (squashes all `fixup!` commits into their targets):

```bash
git rebase --autosquash <base>                           # git ≥ 2.44 — non-interactive
GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash <base>   # older git — suppresses the editor
```

`<base>` = the parent of the oldest fixup target (e.g. `<oldest-sha>~1`).

Unlike `jj absorb`, git won't find the target for you — locate it with `git log --oneline -- <file>` or `git blame <file>`.

**Safety:**
- Never amend or rebase commits that are on a shared remote branch without explicit user confirmation. Check what's local-only: `git log --oneline @{upstream}..HEAD` (everything listed is safe to rewrite).
- Requires a clean working tree apart from the staged retrofit — stash unrelated edits first.
- Before a multi-commit rebase, create a safety ref: `git branch backup/pre-autosquash`.

## Stacking (brief)

Git has no native stacked-change support — descendants don't follow rewrites:

- One branch per reviewable slice; restack dependents with `git rebase --onto <new-base> <old-base> <branch>` after rewriting a lower slice.
- After any rewrite of pushed work, push with `git push --force-with-lease` (never bare `--force`), and only with user confirmation.
- For real stacked-PR workflows, dedicated tools (`gh`, git-spice, graphite) manage the restacking — don't hand-roll beyond two slices.

## Hard rules for agent use

1. **Never invoke interactive commands.** The dangerous incantations:
   - `git add -p` / `git add -i` → interactive prompt, hangs the agent
   - `git rebase -i` without `GIT_SEQUENCE_EDITOR` override → opens editor
   - `git commit` without `-m` → opens editor
2. **Never discard working-tree changes** — `git restore` (without `--staged`), `git checkout -- <path>`, `git reset --hard` are hook-blocked. Stash or commit instead.
3. **Never rewrite pushed commits without explicit user confirmation** — amend, fixup, autosquash, and rebase are local-only operations by default.
4. **Verify staging before every commit** (`git diff --staged`) and **state after** (`git status`).
