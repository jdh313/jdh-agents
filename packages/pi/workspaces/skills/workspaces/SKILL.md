---
name: workspaces
description: >-
  Prepare separate jjx checkouts for Pi work in jj-colocated repos. The opt-in
  native pi-subagents provider binds configured agent types to fresh checkouts
  and retains them on disposal; prompt paths alone do not bind cwd. No workspace
  UI or OS sandbox.
---
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
