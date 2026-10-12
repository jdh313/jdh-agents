---
name: workspaces
description: Give parallel or isolated subagents their own full checkout of the current repo to work in — reach for this before concluding that running multiple agents on separate copies of a repo isn't possible, or reaching for a plain `git worktree` in a jj-colocated repo. Creates or resumes a jj workspace via `jjx open <slug>`, a sibling checkout that shares the repo's full history, so each subagent gets an isolated working directory with no risk of two agents editing the same files. Use when asked to run subagents in parallel on isolated copies of a repo, spin up an isolated checkout or worktree per agent, parallelize edits across a repo without agents stepping on each other, or fan out work that needs its own working directory. jj-repos only (`jj root` succeeds) — for a plain git repo, ordinary `git worktree` is the right tool.
allowed-tools:
  - Bash(jjx:*)
  - Bash(jj:*)
  - Bash(jj root)
  - Agent
  - Read
targets:
  pi:
    description: Prepare separate jjx checkouts for Pi work in jj-colocated repos. The opt-in native pi-subagents provider binds configured agent types to fresh checkouts and retains them on disposal; prompt paths alone do not bind cwd. No workspace UI or OS sandbox.
    body: |
      # Workspaces in Pi

      `jjx` manages full sibling checkouts sharing repository history. The
      standalone `workspaces-pi` package includes an opt-in native provider
      for `@gotgenes/pi-subagents` 23.4.0 / Pi 1.1.0, jjx 0.6.x / jj 0.46.x.
      It ships no Claude hooks or workspace UI and is not an OS sandbox.
      Default policy is none: creation guidance alone does not bind cwd.

      ## Native provider (explicit operator opt-in)

      Load pi-subagents first and this extension second; never also load the
      Git worktrees provider (only one WorkspaceProvider can register).
      Use `--jjx-workspaces '{"Worker":{},"Reviewer":{"from":"root()"}}'`
      with exact agent type names. No policy is inferred from task prompts.
      Loading a peer dependency does not activate its extension. Programmatic
      callers must check `requireWorkspaceService()` before using its captured
      service; a missing/conflicting adapter is not successful isolation.

      Configured children get fresh `jjx open --unique` checkouts at admission
      time with explicit baseCwd. Preparation failure throws, never falls back
      to parent cwd. The existing provider seam binds child tools/context;
      this package does not introduce a spawner. Disposable tests cover real
      jjx creation and Pi builtin tool factories, not a complete model-driven
      foreground/background session or permission integration. See the package
      README for supported loading, readiness, and remaining acceptance.

      Disposal retains BOTH directory and jj registration. An ask-back may
      hold the live lease for core-supported resume, but ordinary completed
      children cannot resume after lease disposal. Retaining files does not
      restore a session; do not promise same-agent verification resume.

      Check `jj root` first. This workflow applies only in a jj-colocated repo;
      if that fails, use ordinary `git worktree add` for a plain git repo,
      not `jjx`. The invoking tool's actual working directory matters: an
      absolute path mentioned in a prompt does not change it.

      ## Create or resume a checkout

      ```sh
      ws_path=$(jjx open auth-fix)
      ```

      `jjx open <slug>` creates a workspace or resumes an intact existing one
      untouched. It prints only the absolute path on stdout; informational
      output goes to stderr. The path is `<repo>-spaces/<slug>`, a sibling of
      the repo. It has full history and local files seeded from `.jjx.toml`
      (`[seed.copy]`, `[seed.link]`, `[seed.hooks]`; `.worktree-copy.toml` is
      legacy fallback), plus a best-effort git index shim. Review seed hooks
      and links before opting in: hooks execute shell commands, links share
      writable resources, and hook failure need not fail creation.

      - **Default base:** forks the invoking workspace's current state. It
        freezes the caller's uncommitted work into a commit (`jj new`, no
        message), so the child inherits it. Inspect caller state and confirm
        this is intended before creating a workspace.
      - **`--from <revset>`:** uses an explicit local revision, such as
        `main@origin` or `trunk()`, without freezing caller work. `jjx` does
        no network I/O; run `jj git fetch` first only if a current remote base
        is needed and network access is authorized.
      - **`--unique`:** creates a fresh workspace even when the slug exists,
        suffixing `-2`, `-3`, etc. Use for distinct checkouts per task.
      - Forking from a secondary workspace names the child
        `<parent>__<slug>`; `__` marks parentage and `-N` disambiguation.

      If the runtime denies sibling-directory or jj/Git metadata writes,
      request authorization for the exact command through the available
      permission mechanism. Do not bypass sandbox restrictions broadly.

      ## Isolation boundary

      Creating a checkout is not the same as placing an agent in it. This
      native provider supplies cwd for configured pi-subagents children only.
      Outside that supported path, independently establish that the chosen
      runtime can bind each worker's cwd and file tools to its own workspace.
      Do not assume Claude's `Agent` or `isolation: "worktree"` exists in Pi.

      For a separate Pi process, launch it from the intended checkout, for
      example `cd "$ws_path" && pi`, and verify its actual cwd and resolved
      read/edit/write paths before edits. If using another collaboration
      implementation, use its documented cwd control and verify the same
      boundary; a workspace path in its spawn prompt is only an instruction,
      not runtime binding or a filesystem fence. Shared jj metadata and
      absolute paths remain accessible. Extensions using `process.cwd()`
      instead of session cwd can still act on the parent. Serialize shared
      integration/destructive VCS operations through the parent.

      For manually placed sessions, after placement is independently verified
      (the native provider creates configured children automatically):

      1. Create a distinct checkout per task with
         `ws_path=$(jjx open --unique <task-slug>)` and capture each path.
      2. State the absolute path and edit boundary in each task prompt as
         supplemental guidance, not as the placement mechanism.
      3. Inspect finished work with `jj log`; commits share the same repo.
         Integrate by rebase or squash only after reviewing the changes.
      4. Review/integrate before manual `jjx rm <path>`. The adapter never
         runs it. jjx can forget registration while retaining a directory
         with unsaved/unmerged work and exit successfully. Inspect BOTH
         registration and path afterward; ignored files are not guaranteed
         protected. Surviving `<workspace>__*` children do not cascade.

      ## Other commands

      - `jjx add <path>` adds an existing checkout as a jj workspace; unlike
        `open`, it does not create/resume a managed sibling by slug.
      - `jjx seed <path> [--root <dir>]` applies reviewed `.jjx.toml` seed
        config (legacy fallback supported) without creating a workspace.
      - `jjx gitshim [init|sync|rm]` manages the git index shim; jj 0.46 owns
        linked Git worktree/HEAD. Old lock/unlock guidance does not apply.

      ## Claude path remains separate

      Claude Code's existing `Agent` tool with `isolation: "worktree"` routes
      through its configured `WorktreeCreate` hook to `jjx open` on this
      machine. That Claude path is unchanged; this Pi package does not ship
      or activate it. No Claude workspace-placement mod or UI is ported here.
      Pi skill metadata does not enforce tool permissions.
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
jjx open <slug>
```

Creates the workspace, or **resumes** an existing intact one for that slug
untouched — idempotent, safe to call again. Prints the workspace's absolute
path on stdout **and nothing else** (everything informational goes to
stderr), so callers can capture stdout directly as the path:

```sh
ws_path=$(jjx open auth-fix)
```

The workspace lands at `<repo>-spaces/<slug>` — a sibling of the repo, not
nested inside it. It's a full checkout: same repo history, seeded local files
(`.env` and similar, from `.worktree-copy.toml`), and a working git shim so
editor gutters function.

Sandboxed runtimes may require approval for the exact `jjx` command because it
writes jj/Git repository metadata and creates a sibling checkout outside the
current workspace root. If that write is denied, request elevated permission
for the command; do not treat the denial as a jjx failure or bypass the runtime
sandbox broadly.

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
   ws=$(jjx open --unique <task-slug>)
   ```
   Every workspace shares the same underlying jj repo, so nothing needs
   merging at the filesystem level.
2. Spawn each subagent with the runtime's collaboration tool and a prompt that
   states its absolute workspace path explicitly and instructs it to make
   **all** edits inside that path — never outside it.
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

- `jjx add <path>` — add an existing checkout at an explicit path as a jj
  workspace. This is distinct from `jjx open <slug>`, which creates or resumes
  a managed sibling checkout by slug.
- `jjx seed <path> [--root <dir>]` — (re-)seed a directory from
  `.worktree-copy.toml` without creating a workspace.
- `jjx gitshim [init|sync|lock|unlock] [dir]` — manage the read-only git
  worktree shim that makes editor gutters work in a workspace.

## Claude Code's own worktree hook

On this machine, Claude Code's `Agent` tool with `isolation: "worktree"`
already routes through a `WorktreeCreate` hook straight to `jjx open`
for jj repos — so that path also gives you an isolated checkout, no manual
`jjx` call needed. Reach for the explicit workflow above when you need
control over the base revision (`--from`) or explicit naming, or when
orchestrating several workspaces by hand rather than through that tool
parameter.
