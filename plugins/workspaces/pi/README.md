# Workspaces in Pi — bounded native provider

Standalone `../PACKAGE.pi.yaml` packages the canonical skill's Pi-only override
plus one native extension and its helper. Independent Pi version **0.1.0**;
Claude/Codex `workspaces` 0.2.0 content and hooks remain unchanged. No `/spaces`
UI, generic spawner, cleanup command, or upstream patch is included.

## Supported surface and explicit opt-in

- Pi **1.1.0**, `@gotgenes/pi-subagents` **23.4.0**, Node >=22, external
  `jjx` **0.6.x** / `jj` **0.46.x**, jj-colocated repository.
- Load pi-subagents **first**, this extension **second**. Declaring an optional
  peer does not install or activate core. Runtime core imports are type-only;
  registration uses its published process-global Symbol bridge, so compiled
  local packages do not depend on resolving another package's module tree.
- Exactly one WorkspaceProvider can register, even with policy none. Do not
  also load `@gotgenes/pi-subagents-worktrees` or another provider.
- **Default policy: none.** With no flag (or `{}`), `prepare` returns undefined,
  leaving core's normal parent-cwd behavior unchanged. Opt in exact agent types:

  ```sh
  pi --jjx-workspaces '{"general-purpose":{},"Explore":{"from":"root()"}}'
  ```

  This flag is available only when the extension is loaded. No wildcard,
  prompt parsing, per-call path override, or automatic settings/trust edit.
  `from` is the only optional field: a bounded local jj revision passed as
  one argv value. Unknown fields and malformed policies fail visibly.
- Use **one root CLI Pi session per process**, launched at the intended parent
  cwd. SDK parents whose cwd differs from process.cwd(), multiple roots, and
  programmatic dispatch without readiness checks are unsupported here.

### Registration, readiness, and inherited children

The extension captures the parent service once and owns a Symbol-backed lease
with an identity token. Inherited child factories observing that lease do
nothing, register no shutdown handler, and cannot unregister the parent.
Only the owner releases registration. Preparation objects retain their own
synchronous disposal callbacks after provider unregistration.

Missing/misordered core and provider conflicts produce session-start errors
and **block the `subagent` tool** (including nested tool execution). Pi may
continue after extension errors: an error is never proof of isolated success.
Opted-in preparation failures throw; they never return parent cwd.

Programmatic `service.spawn()` does not pass through `tool_call`. Callers must
import `requireWorkspaceService` from `pi/extension.ts`, check it before every
dispatch, and use the returned **captured parent service**. It throws when the
adapter is absent, unavailable, or policy invalid. It does not create a new
spawner or intercept third-party spawn calls. Calling core's raw service after
a registration error bypasses the guard and is **not supported isolation**.

Core 23.4.0 itself can republish its global service during child loading and
unpublish it during child shutdown. Our captured reference remains usable,
but this adapter does **not** repair the global publication for other service
consumers. Avoid consumers that repeatedly look up that symbol after child
binding. Where package-based deployments require a stable public bridge,
explicitly review core's `excludedExtensionPackages` in `subagents.json`:
entries must match the configured package **source string exactly**, e.g.
`npm:@gotgenes/pi-subagents@23.4.0` only if that is the actual source. Excluding
that package's extensions in children prevents its child initialization; it
does not exclude the core's parent-created child protocol. CLI ephemeral
extension paths are not inherited like package settings. No exclusion is
written automatically, and this setup has not been end-to-end accepted here.
**Do not exclude the permission-system package.**

## Prepare, binding, preservation

- Each configured admitted child uses explicit `ctx.baseCwd` for version/repo
  probes and `jjx open --unique [--from REV] pi-TYPE-ID-NONCE`. Slugs are bounded
  safe ASCII, with random nonce plus jjx collision suffixes. No shell expansion.
- Commands have a **30-second timeout each**, **256 KiB output bound**, and
  separate stderr. There is no provider AbortSignal. Timeout kills the direct
  child; arbitrary seed-hook descendants may survive. This is not a process
  sandbox or a total preparation deadline. Queuing behind another creation
  also takes time. Seed hooks must be reviewed before opt-in.
- Shared-repo identity is canonicalized through `.jj/repo`. Creation and result
  validation are serialized per shared repo **within this process**; external
  jjx calls, other processes, and parent jj edits are not locked. Parent/child
  workspace paths must be real directories without unexpected symlink targets;
  returned root, repo identity, expected sibling location/name, and registration
  root are checked before the Workspace is returned. Failures report diagnostics
  and possible partial artifacts; they never auto-delete anything.
- Default jjx behavior freezes a nonempty caller `@` with `jj new` then forks
  its state. An empty `@` skips the extra freeze. Lazy admission uses state at
  **prepare time**, not spawn time. For identical fan-out bases, establish an
  immutable revision first and configure `from`; no fetch is performed.
- Existing core provider binding rebuilds child's cwd-based tools/context.
  Relative file tools therefore target the checkout. Absolute paths and shared
  jj metadata remain accessible; extensions using process.cwd() can still act
  on the parent. This is checkout separation, **not an OS sandbox**. Serialize
  integration/rebase/squash/bookmark/destructive jj operations through the parent.
- Review `.jjx.toml` seed copy/link/hook rules (legacy `.worktree-copy.toml`
  fallback), tracked `.pi` resources, and ignored context before opting in.
  Links share writable data; hooks run shell commands and best-effort failures
  do not necessarily fail creation. Provider subprocesses are extension code,
  not permission-gated model tool calls. Child project-resource discovery is
  not a guaranteed new interactive trust ceremony. Copy needed ignored
  instructions deliberately; do not blindly link all `.pi` state.

### Disposal is lease release, not removal or resumability

`dispose` is synchronous and idempotent. It records release and appends the
checkout path with inspection/integration guidance. **Both checkout and jj
registration are retained** for completed/error/aborted/stopped outcomes; no
Git commit, `jjx rm`, `jj workspace forget`, or automatic garbage collection.
In-memory records belong to the provider instance and are not crash-persistent.
Recover manually with `jj workspace list` and sibling directories.

Core may hold the lease while an ask-back awaits an answer and resume that
same live session. Ordinary completed children are disposed immediately:
core marks their bracket disposed and refuses subsequent resume even though
the directory exists. **Do not promise same-agent verification resume.**
Inspect with the parent or start separately reviewed new work. Ask-back,
retention expiry, turn exhaustion, and cancellation are core-owned behavior,
not reimplemented or fully runtime-accepted by this adapter's tests.

After review/integration, removal is manual. `jjx rm` can forget registration
while leaving dirty/unmerged directories and exit successfully. Check **both
registration and directory** afterward; ignored files are not guaranteed
protected. Removal does not cascade to child workspaces.

## Compile/check without activation

Use local AgentForge **2.1.0**, not the unchanged pinned 1.3.0 wrapper:

```sh
OUT="$(mktemp -d "${TMPDIR:-/tmp}/workspaces-pi-package.XXXXXX")"
bun run "$HOME/Projects/agentforge/src/cli.ts" package compile \
  plugins/workspaces/PACKAGE.pi.yaml --target pi --out "$OUT"
bun run "$HOME/Projects/agentforge/src/cli.ts" package check \
  plugins/workspaces/PACKAGE.pi.yaml --target pi --out "$OUT"
```

Exactly five files: generated `package.json`, projected
`skills/workspaces/SKILL.md`, `pi/extension.ts`, `pi/provider.ts`, `pi/README.md`.
Only extension.ts activates; helper and tests never auto-register. Tests are
excluded by the explicit payload allowlist. No hook/UI/generated marketplace
files or npm runtime dependencies. Reviewed warning: `stripped allowed-tools`;
Pi skill metadata is not permission enforcement.

Compilation replaces its whole owned output snapshot. Do not provision
node_modules into managed output. Any separately reviewed activation via
`pi install "$OUT"` registers the local path without copying it; preserve a
durable output directory. Avoid duplicate canonical/unprojected skill loading.
No activation or live settings mutation is part of verification here.

## Verification and remaining acceptance

Verified on 2026-10-12 against the installed versions above:

- 11 tests passed, including the disposable real jjx/Pi-tool fixture; no model calls.
- Strict TypeScript checking passed against installed public APIs.
- Local AgentForge 2.1.0 compile/check produced the five declared files;
  repeated compilation was byte-identical.
- Complete Claude/Codex skill projections remained unchanged.
- The actual Pi extension loader imported the compiled adapter; simulated
  inherited adapter loading and captured-owner shutdown checks passed.
- Repository marketplace/native validation and the history privacy gate passed.

These checks do not establish the full child-session scenarios listed below.

```sh
# Deterministic fake runner/provider/service tests; real test is skipped by default
bun test plugins/workspaces/pi/tests

# Explicit already-installed fixture API roots; disposable repo only, no model calls
WORKSPACES_TEST_PI_ROOT=/path/to/pi-coding-agent \
WORKSPACES_TEST_SUBAGENTS_ROOT=/path/to/pi-subagents \
  bun test plugins/workspaces/pi/tests
```

Covered: policy none/errors, safe slugs, argv/baseCwd, same-repo serialization,
unique paths, malformed/foreign/symlink/missing-registration rejection, partial
artifact retention, synchronous idempotent disposal, parent service capture,
inherited adapter no-op, registration errors, tool guard versus direct API
bypass. Disposable real jjx tests cover main/secondary concurrent creation,
WIP/default and explicit bases, invalid revision failure, seven **actual Pi
builtin tool factories** at returned cwd, parent/sibling bytes unchanged,
actual core WorkspaceBracket disposed state, and registered retained checkouts.

Not established: complete foreground/background/queued child session binding,
model prompt/context rebuilding, repeated ask-back/resume, fake-clock retention,
construction failure/abort-during-prepare/timeout lifecycle, real child package
reload/service identity, permission forwarding/path rules, trust behavior,
crash recovery, cross-process concurrency, older/newer core compatibility.
The source seam supports cwd binding; factory-level evidence is not full
subagent-session acceptance. Require a zero-cost fixture SDK/model harness for
those paths before asserting broad parallel or permission parity.
