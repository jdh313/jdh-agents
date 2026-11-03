# VCS and Commit Style Detection

Canonical detection algorithm for the commit skill. The SKILL.md points here instead of restating the steps.

## Two things to detect

1. **VCS**: `git` or `jj` (Jujutsu)
2. **Commit style**: `conventional` (e.g. `feat: add login`) or `freeform` (e.g. `Add login`)
3. **Co-Authored-By policy**: `keep` or `strip` (see "Co-Authored-By trailers" below; it governs AI and human trailers differently)
4. **Issue-ref placement**: `summary` or `pr` (default `pr`)

All four can be declared in repository agent guidance; otherwise auto-detect from repo state.

## Step 1 — Read agent guidance for explicit config

Read `AGENTS.md` files that apply to the working directory. If `CLAUDE.md`
also exists, use its non-conflicting repository facts as supporting guidance.
On Claude Code, where `CLAUDE.md` is the native instruction surface, read it
directly. Search the applicable files for:

- pattern: `^\s*-\s*(VCS|Commit style|Co-Authored-By|Issue refs)\s*:`
- flags: `-i` (case-insensitive)

Recognized lines:

- `- VCS: jj` or `- VCS: git`
- `- Commit style: conventional` or `- Commit style: freeform`
- `- Co-Authored-By: keep` or `- Co-Authored-By: strip`
- `- Issue refs: summary` or `- Issue refs: pr`

Use what's declared. Auto-detect anything not declared. When files conflict,
the active runtime's native repository guidance wins; nearer repository
guidance wins over user-level guidance.

## Step 2 — Auto-detect VCS

```bash
test -d .jj && echo "jj" || echo "git"
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

- **Co-Authored-By (human pairing trailers only):** if ≥60% of recent commit messages carry a human `Co-Authored-By:` trailer → `keep`; otherwise → `strip`. History never removes an AI attribution trailer (see below).
- **Issue refs:** if ≥60% of recent subjects carry a ticket key (`(TEAM-123)`, `#123`) → `summary`; otherwise → `pr`.

**Precedence: applicable repository guidance > user guidance > history.** The
runtime's attribution instruction (e.g. Claude Code's system reminder that says
"End git commit messages with: Co-Authored-By: ...") counts as user guidance.

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

- **`Co-Authored-By:` trailers**: see "Co-Authored-By trailers" below.
- **No trailing period** on the summary line.
- **Imperative mood** ("add" not "added" or "adds").
- **Body ≤5 lines**, explains WHY (the diff shows WHAT).
- **Issue numbers in the summary** follow the detected placement (Step 1, else Step 3b). Default `pr` — refs belong in the PR description, not the subject. Honor `summary` when repository guidance declares it or history consistently uses it.

## Co-Authored-By trailers

Two kinds, decided separately:

- **AI attribution trailer** (e.g. `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`): add it when user guidance or the runtime's attribution instruction supplies one, copied verbatim, never with the model name edited or guessed. Omit it only when repository guidance declares `- Co-Authored-By: strip`. If nothing supplies one, add none: never invent a trailer. Repo history does not override it, so a repo whose past commits carry no trailer still gets one.
- **Human pairing trailer** (`Co-Authored-By: Name <email>`): add one line per human co-author only when two people genuinely paired on the commit, and only when the policy is `keep` (repository guidance, else Step 3b history). A teammate who only reviewed is not a co-author.

When reviewing a message (Workflow C), flag a missing or edited AI trailer the same way as a missing human one.
