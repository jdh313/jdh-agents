# VCS and Commit Style Detection

Canonical detection algorithm used by every skill in this plugin. Each SKILL.md points here instead of restating the steps.

## Two things to detect

1. **VCS**: `git` or `jj` (Jujutsu)
2. **Commit style**: `conventional` (e.g. `feat: add login`) or `freeform` (e.g. `Add login`)

Both can be declared in the repo's CLAUDE.md; otherwise auto-detect from repo state.

## Step 1 — Read CLAUDE.md for explicit config

Use the Grep tool against `CLAUDE.md` (if it exists):

- pattern: `^\s*-\s*(VCS|Commit style)\s*:`
- flags: `-i` (case-insensitive), `path: CLAUDE.md`

Recognized lines:

- `- VCS: jj` or `- VCS: git`
- `- Commit style: conventional` or `- Commit style: freeform`

Use what's declared. Auto-detect anything not declared. If `CLAUDE.md` doesn't exist, skip to Step 2.

## Step 2 — Auto-detect VCS

```bash
[ -d .jj ] && echo "jj" || echo "git"
```

`.jj/` is authoritative — both jj-native repos and jj-on-top-of-git colocated repos have it.

## Step 3 — Auto-detect commit style

Sample the last 20 commit subject lines:

```bash
# git
git log --pretty=%s -20

# jj (excludes empty/working-copy descriptions)
jj log --no-graph --limit 20 -T 'description.first_line() ++ "\n"' -r '..@'
```

Classify each subject. A line is **conventional** if it matches:

```
^(feat|fix|chore|docs|style|refactor|perf|test|build|ci|revert)([\[\(][^\]\)]+[\]\)])?:\s
```

This accepts `feat:`, `feat(scope):`, and `feat[scope]:`. Anything else is **freeform**.

If ≥60% of sampled subjects are conventional → `conventional`. Otherwise → `freeform`.

## Step 4 — Load matching references

| VCS | Reference |
|-----|-----------|
| git | `references/git-workflow.md` |
| jj  | `references/jj-workflow.md` |

| Style | Reference |
|-------|-----------|
| conventional | `references/conventional-commits.md` |
| freeform     | `references/freeform-commits.md` |

## House style (both VCSes, both message styles)

- **No `Co-Authored-By:` footers.** The commit message describes the change; the VCS records authorship separately. Strip these footers if present in a draft message.
- **No trailing period** on the summary line.
- **Imperative mood** ("add" not "added" or "adds").
- **Body ≤5 lines**, explains WHY (the diff shows WHAT).
- **No issue numbers** in the summary (PR description, not commit subject).
