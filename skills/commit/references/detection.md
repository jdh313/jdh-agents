# VCS and Commit Style Detection

Canonical detection algorithm for the commit skill. The SKILL.md points here instead of restating the steps.

## Two things to detect

1. **VCS**: `git` or `jj` (Jujutsu)
2. **Commit style**: `conventional` (e.g. `feat: add login`) or `freeform` (e.g. `Add login`)
3. **Co-Authored-By policy**: `keep` or `strip` (default `strip`)
4. **Issue-ref placement**: `summary` or `pr` (default `pr`)

All four can be declared in the repo's CLAUDE.md; otherwise auto-detect from repo state.

## Step 1 — Read CLAUDE.md for explicit config

Use the Grep tool against `CLAUDE.md` (if it exists):

- pattern: `^\s*-\s*(VCS|Commit style|Co-Authored-By|Issue refs)\s*:`
- flags: `-i` (case-insensitive), `path: CLAUDE.md`

Recognized lines:

- `- VCS: jj` or `- VCS: git`
- `- Commit style: conventional` or `- Commit style: freeform`
- `- Co-Authored-By: keep` or `- Co-Authored-By: strip`
- `- Issue refs: summary` or `- Issue refs: pr`

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

## Step 3b — Auto-detect message conventions

Only for whatever Step 1 didn't declare. Sample the same recent commits (use full messages, not just subjects, for the trailer check):

- **Co-Authored-By:** if ≥60% of recent commit messages carry a `Co-Authored-By:` trailer → `keep`; otherwise → `strip`.
- **Issue refs:** if ≥60% of recent subjects carry a ticket key (`(TEAM-123)`, `#123`) → `summary`; otherwise → `pr`.

**Precedence: repo CLAUDE.md > user CLAUDE.md > history.** A user-level mandate to add `Co-Authored-By:` is honored unless the repo declares otherwise.

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

- **`Co-Authored-By:` footers** follow the detected policy (Step 1, else Step 3b). Default `strip` — the message describes the change, the VCS records authorship separately. Honor `keep` when CLAUDE.md mandates it or history consistently uses it.
- **No trailing period** on the summary line.
- **Imperative mood** ("add" not "added" or "adds").
- **Body ≤5 lines**, explains WHY (the diff shows WHAT).
- **Issue numbers in the summary** follow the detected placement (Step 1, else Step 3b). Default `pr` — refs belong in the PR description, not the subject. Honor `summary` when CLAUDE.md declares it or history consistently uses it.
