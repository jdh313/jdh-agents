# Commit

Format-aware atomic commits for git and jj (Jujutsu).

## What It Does

- **Auto-detects VCS**: Checks for `.jj/` to determine git vs jj
- **Auto-detects commit style**: Analyzes recent commits to match the repo's convention (conventional or freeform); explicit CLAUDE.md config wins
- **Atomic splitting**: Groups changes by logical coupling, not by file co-location — including two logical changes inside one file (edit-split-restore, no interactive staging)
- **Retrofit lane**: "this belongs in an earlier commit" via `jj absorb` (hunk-precise, auto-targeted) or `git commit --fixup` + non-interactive autosquash
- **Message review**: Checks a draft message against the repo's style AND against the actual diff (type match, scope honesty, hidden bundling)
- **Safety-first**: A `PreToolUse` hook hard-blocks destructive operations (`git reset --hard`/`--merge`, `git restore` without `--staged` or with `--worktree`, `git checkout <rev|.> -- <path>`/`git checkout .`, `git stash drop`/`clear`, `jj restore`, `jj abandon`) — including when global flags like `git -C <path>` or `jj -R <path>` sit between the binary and the subcommand — so changes aren't accidentally discarded
- **jj-fluent**: Decision-card-style reference covers `jj commit`, `jj split` (with `-m` semantics explained), `jj squash --from/--into`, `jj absorb`, stacked-change hygiene, bookmarks, push, and recovery — agents shouldn't need to re-read `jj --help` mid-task

## One Skill

A single `commit` skill handles everything. It's invoked automatically for any commit-shaped request, or explicitly via `/commit`. Internally it routes between four workflows:

| Workflow | Trigger |
|----------|---------|
| Single commit | "commit this", "write a commit message" |
| Split and compose | "split these into atomic commits" |
| Review and improve | "review my commit message" (checks the diff, not just the style) |
| Retrofit | "this belongs in the last commit", fixup/absorb requests |

The skill body is VCS-agnostic; after detection it loads exactly one VCS recipe (`git-workflow.md` or `jj-workflow.md`) and one style reference (`conventional-commits.md` or `freeform-commits.md`).

## Commit Style Detection

Detection order (canonical algorithm lives in `skills/commit/references/detection.md`):

1. **CLAUDE.md** — explicit declarations win
2. **Auto-detect** — sample the last ~20 subjects; if ≥60% match a conventional type prefix (allows `feat:`, `feat(scope):`, and `feat[scope]:`), use conventional; otherwise freeform

### Supported Styles

- **Conventional**: `feat: add user auth` — type prefix, lowercase, imperative mood
- **Freeform**: `Add user auth` — capitalized, imperative mood, no type prefix

## House Style

Applied to every generated message:

- `Co-Authored-By:` trailers: the AI attribution line your runtime or guidance supplies (e.g. Claude Code's "End git commit messages with" reminder) is kept verbatim unless the repo declares `strip`; human co-author trailers (`Co-Authored-By: Name <email>`) are added only when the policy is `keep` and two people genuinely paired — see Configuration
- No trailing period on the summary
- Imperative mood
- Body ≤5 lines, explains WHY (the diff shows WHAT)
- Issue refs follow the detected placement (default PR-only) — see Configuration

## Team Usage

When working in a shared repo with multiple committers:

- **Human pairing:** if you and a teammate wrote a commit together (mob session, live pair coding), add one `Co-Authored-By: Name <email>` line after the body — one line per co-author. Omit it for commits you authored alone, even if a teammate reviewed it.
- **Rewrite safety:** before amending or retrofitting into an existing commit, the skill checks the target commit's author. If it belongs to a teammate, it will prompt for confirmation before rewriting. This prevents silently rewriting another person's history.

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

Two more optional keys control message conventions:

```markdown
## VCS
- Co-Authored-By: keep   # keep | strip (human trailers default strip; strip here also drops the AI trailer)
- Issue refs: summary    # summary | pr (default pr)
```

- **`Co-Authored-By`** — `keep` adds human pairing trailers; `strip` removes every `Co-Authored-By:` trailer, including the AI attribution one.
- **`Issue refs`** — `summary` keeps a ticket key like `(TEAM-153)` / `#123` in the subject (useful when a Linear/Jira integration parses it); `pr` keeps refs out of the subject.

If unspecified, the plugin auto-detects all four from the repo state: it samples recent commits and keeps human trailers / in-summary refs when ≥60% of history uses them. **Precedence: repo CLAUDE.md > user CLAUDE.md (and the runtime's attribution instruction) > history.** History never removes the AI attribution trailer; only a repo `strip` declaration does.

## Pi

Install the local package (loaded in place, without copying):

```bash
pi install ~/Projects/jdh-agents/plugins/commit
```

Requires `jq` on `PATH`. Restart Pi after installation. The extension guards
Pi's built-in `bash` tool by passing its command to the unchanged safety hook;
the shell script remains the single source of destructive-VCS rules.

Pi fails closed if the guard is missing, not executable, exceeds five seconds,
or exits unexpectedly, unlike Codex's fail-open hook behavior. The script's
own malformed-input behavior is unchanged; the extension supplies valid JSON.
User shell commands entered with `!` / `!!` are not intercepted.

## Safety Hook

`plugins/commit/hooks/destructive-vcs-guard.sh` is a `PreToolUse`/`Bash` hook that blocks the commands listed under "Safety-first" above, including when a recognized global flag (`git -C`/`-c`/`--git-dir`/`--work-tree`, `jj --repository`/`-R`) separates the binary from the subcommand. It fails open (allows) if the hook input isn't parseable JSON. The hook fires only when the plugin is enabled. Override by running the destructive command from your own terminal — Claude can't bypass it.
