---
name: workspaces
description: Give parallel or isolated subagents their own full checkout of the current repo to work in — reach for this before concluding that running multiple agents on separate copies of a repo isn't possible, or reaching for a plain `git worktree` in a jj-colocated repo. Creates or resumes a jj workspace via `jjx add --name <slug>`, a sibling checkout that shares the repo's full history, so each subagent gets an isolated working directory with no risk of two agents editing the same files. Use when asked to run subagents in parallel on isolated copies of a repo, spin up an isolated checkout or worktree per agent, parallelize edits across a repo without agents stepping on each other, or fan out work that needs its own working directory. jj-repos only (`jj root` succeeds) — for a plain git repo, ordinary `git worktree` is the right tool.
allowed-tools:
  - Bash(jjx:*)
  - Bash(jj:*)
  - Bash(jj root)
  - Agent
  - Read
---

# Workspaces

`jjx` is a Rust CLI, installed and on `PATH`, that manages jj workspaces (jj's
equivalent of a git worktree — a second working directory checked out from the
same repo, sharing its full commit history). Use it to give each parallel
subagent its own isolated directory instead of one shared working tree.

**This only applies inside a jj-colocated repo.** Check with `jj root`; if
that fails, this repo is plain git and ordinary `git worktree add` is correct
instead — do not reach for `jjx`.

## The core command

```
jjx add --name <slug>
```

Creates the workspace, or **resumes** an existing intact one for that slug
untouched — idempotent, safe to call again. Prints the workspace's absolute
path on stdout **and nothing else** (everything informational goes to
stderr), so callers can capture stdout directly as the path:

```sh
ws_path=$(jjx add --name auth-fix)
```

The workspace lands at `<repo>-spaces/<slug>` — a sibling of the repo, not
nested inside it. It's a full checkout: same repo history, seeded local files
(`.env` and similar, from `.worktree-copy.toml`), and a working git shim so
editor gutters function.

### Basing the workspace

- **Default** — forks from the invoking workspace's current state. Any
  uncommitted work in the caller gets frozen into a commit (`jj new`, no
  message) and the child is based on that, so the child inherits what the
  parent has written but not yet committed.
- **`--from <revset>`** — base on an explicit revision instead (e.g.
  `main@origin`, `trunk()`), skipping the freeze. `jjx` does no network I/O:
  `--from main@origin` uses whatever `jj` already has locally, so run
  `jj git fetch` first if the base needs to be current.
- **`--unique`** — always create a distinct new workspace rather than
  resuming one, suffixing `-2`, `-3`, ... on a name collision. Use this for
  fan-out, where each subagent needs its own workspace even if a prior run
  left one at the same slug.

### Naming

Forking from a secondary workspace names the child `<parent>__<slug>` (e.g.
forking `tests` off workspace `alpha` gives `alpha__tests`) — `__` marks
parentage, `-N` marks disambiguation. Forking from the main workspace gives a
bare slug.

## The parallel-subagent workflow

1. Create one workspace per subagent up front, capturing each path:
   ```sh
   ws=$(jjx add --name <task-slug> --unique)
   ```
   Every workspace shares the same underlying jj repo, so nothing needs
   merging at the filesystem level.
2. Spawn each subagent (Task/Agent tool) with a prompt that states its
   absolute workspace path explicitly and instructs it to make **all** edits
   inside that path — never outside it.
3. Let them run in parallel; one workspace each means no two agents write the
   same file.
4. When a subagent finishes, its commits are ordinary jj commits in the
   shared repo — inspect them from anywhere with `jj log`, and integrate
   (rebase, squash) as usual.
5. Clean up with `jjx rm <path>`. It refuses to delete a checkout holding
   unsaved or unmerged work and leaves it on disk with a warning instead — it
   won't silently discard a subagent's work. It also lists any surviving
   `<workspace>__*` children on stderr; cleanup doesn't cascade to them.

## Also useful

- `jjx seed <path> [--root <dir>]` — (re-)seed a directory from
  `.worktree-copy.toml` without creating a workspace.
- `jjx gitshim [init|sync|lock|unlock] [dir]` — manage the read-only git
  worktree shim that makes editor gutters work in a workspace.

## Claude Code's own worktree hook

On this machine, Claude Code's `Agent` tool with `isolation: "worktree"`
already routes through a `WorktreeCreate` hook straight to `jjx add --name`
for jj repos — so that path also gives you an isolated checkout, no manual
`jjx` call needed. Reach for the explicit workflow above when you need
control over the base revision (`--from`) or explicit naming, or when
orchestrating several workspaces by hand rather than through that tool
parameter.
