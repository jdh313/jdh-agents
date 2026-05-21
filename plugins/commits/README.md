# Commits

Format-aware atomic commits for git and jj (Jujutsu).

## What It Does

- **Auto-detects VCS**: Checks for `.jj/` to determine git vs jj
- **Auto-detects commit style**: Analyzes recent commits to match the repo's convention (conventional or freeform); explicit CLAUDE.md config wins
- **Atomic splitting**: Groups changes by logical coupling, not by file co-location
- **Safety-first**: A `PreToolUse` hook hard-blocks destructive operations (`git reset --hard`, `git restore` without `--staged`, `git checkout --`, `jj restore`, `jj abandon`) so changes aren't accidentally discarded
- **jj-fluent**: Decision-card-style reference covers `jj commit`, `jj split` (with `-m` semantics explained), `jj squash --from/--into`, bookmarks, push, and recovery — agents shouldn't need to re-read `jj --help` mid-task

## Skills

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `commits` | Auto-invoked | Main skill for all commit operations |
| `commit` | `/commits:commit` | Create a single commit |
| `split` | `/commits:split` | Split changes into atomic commits |
| `review` | `/commits:review [message]` | Review/improve a commit message (peeks at the diff opportunistically) |

## Commit Style Detection

Detection order (canonical algorithm lives in `skills/commits/references/detection.md`):

1. **CLAUDE.md** — explicit declarations win
2. **Auto-detect** — sample the last ~20 subjects; if ≥60% match a conventional type prefix (allows `feat:`, `feat(scope):`, and `feat[scope]:`), use conventional; otherwise freeform

### Supported Styles

- **Conventional**: `feat: add user auth` — type prefix, lowercase, imperative mood
- **Freeform**: `Add user auth` — capitalized, imperative mood, no type prefix

## House Style

Applied to every generated message:

- No `Co-Authored-By:` footers — the commit describes the change, not the author
- No trailing period on the summary
- Imperative mood
- Body ≤5 lines, explains WHY (the diff shows WHAT)
- No issue numbers in the summary (those belong in the PR description)

## Configuration

Add to your repo's CLAUDE.md to skip auto-detection:

```markdown
## VCS
- VCS: jj
- Commit style: conventional
```

Or for freeform / git:

```markdown
## VCS
- VCS: git
- Commit style: freeform
```

If unspecified, the plugin auto-detects both from the repo state.

## Safety Hook

`plugins/commits/hooks/destructive-vcs-guard.sh` is a `PreToolUse`/`Bash` hook that blocks the commands listed under "Safety-first" above. The hook fires only when the plugin is enabled. Override by running the destructive command from your own terminal — Claude can't bypass it.
