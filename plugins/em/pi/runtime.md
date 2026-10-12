# Pi runtime adapter — capabilities and isolation

This reference maps EM's Claude Agent/Skill/AskUserQuestion concepts to Pi
1.1.0 and `@gotgenes/pi-subagents` 23.4.0. Use actual session tool schemas and
advertised resources, not Claude identifiers. It supplies procedures, not
permission enforcement or full runtime parity.

## Capability preflight

- Load a skill by reading the **advertised SKILL.md path** with `read`; operator
  invocation is `/skill:name`. Pi has no required `Skill` tool. Do not guess
  names from Claude's `plugin:skill` namespaces or invoke unknown slash commands.
- Ask the user in ordinary chat, recommended option first, then wait for the
  answer where required. There is no assumed `AskUserQuestion` tool.
- For delegation, require actual `subagent`, `get_subagent_result`, and
  `steer_subagent` tools. Missing core: stop delegated execution and report the
  prerequisite; a trivial inline edit still needs verified isolation.
- Read the available types in the subagent tool description and applicable
  definitions in `<cwd>/.pi/agents/` / `$PI_CODING_AGENT_DIR/agents/` (default
  `~/.pi/agent/agents/`). Filenames define types; check `enabled`, tools, model
  and `locked` fields. Source plugin agents are NOT automatically installed
  Pi types. Unknown types silently fall back to general-purpose in core: avoid
  speculative dispatch and inspect any substitution/lock advisories.
- Optional NDR: if an advertised grounding skill and repo `.ndr.toml` exist,
  read its content and follow its available Pi/CLI procedure scoped to the
  ticket. Read returned current heads, retaining `ndr:` references. A source
  checkout alone is not a loaded skill. Without a usable procedure, say NDR
  grounding was skipped; if repository rules require it, stop and obtain it.
  Capture only decisions actually made, via available capture instructions and
  their confirmation step, never during read-only scope.
- Optional PM: read the advertised breakdown skill before recommending its
  Pi invocation for oversized work. If absent, recommend user-led slicing;
  do not invent a PM agent or author tracker children yourself.
- Optional Linear operations and Craft reviews: see `trackers.md` and
  `dispatch-verify.md`. Neither bundled Claude agents nor Codex registration
  contracts establish Pi availability. Generic specialist fallback needs the
  actual corresponding installed Markdown procedure and explicit selection
  where its contract requires it; otherwise report the missing capability.
- A child does not automatically get extension tools. Its agent `tools` must
  admit the actual gateway/tool names. Omitted tools means seven builtins, not
  MCP. Check child needs before delegation; keep tracker reads/writes in parent
  if no authorized child can perform them. Never broaden tooling silently.

## Isolation readiness BEFORE editing dispatch

Require the operator's reviewed Workspaces setup/preflight evidence for this
session: supported versions, core loaded **before** Workspaces, one provider,
valid exact-type policy, intended launch cwd, no startup registration/policy
errors, reviewed seed config and context/trust/permission setup. Ask for the
missing evidence and stop if uncertain. Merely finding extension files or a
flag in a help subprocess does not prove the active provider is registered.
`requireWorkspaceService()` is an exported **programmatic** accessor, NOT a
model tool. Do not call a nonexistent readiness tool or import TypeScript in
bash and claim it checked the active session. Programmatic consumers must use
that accessor and captured service; EM uses the model tools.

Supported native path: one root CLI Pi session per process in a jj-colocated
repo, jjx 0.6.x, jj 0.46.x, Workspaces Pi 0.1.0. Operator config example:

```sh
pi --jjx-workspaces '{"general-purpose":{"from":"IMMUTABLE_REV"},"Explore":{"from":"IMMUTABLE_REV"}}'
```

Replace IMMUTABLE_REV with a reviewed local immutable commit ID before launch;
use exact **resolved** agent types, including any generic substitution. Default
policy is none; no wildcard or automatic opt-in. Only one WorkspaceProvider
may register: do not also load pi-subagents-worktrees. Read the Workspaces Pi
README in its reviewed installed package for setup/lifecycle constraints.

1. Inspect parent status and ownership; establish a fresh trunk base before
   launch/dispatch. Fetch only when network access is authorized. In an owned
   isolated jj session the canonical refresh is `jj git fetch` then
   `jj rebase -r @ -d 'trunk()'`; do not rebase shared active checkouts. Resolve
   the immutable base with `jj log -r 'trunk()' --no-graph -T 'commit_id ++ "\n"'`.
   If remote freshness cannot be checked, disclose it and stop or get approval
   for the known base. Record the exact ID, not a moving revset for fan-out.
2. Operator must set `from` in the launch policy to that ID for identical lane
   bases. This CLI flag cannot be changed per subagent call. If the loaded
   policy is wrong, stop for a reviewed restart; do not pretend a prompt can
   override it. Without `from`, default jjx may freeze nonempty parent WIP and
   forks state at admission time (including queued admission), not spawn time.
3. The provider automatically creates **one fresh checkout per opted-in
   child** and core binds tools/context there. Do NOT manually create a
   workspace first and then dispatch an opted-in child (double workspaces).
   `subagent` has no `cwd` parameter; a path in the prompt is not placement.
4. Require each child to report actual `pwd`, `jj root` (or git root), base
   commit and instruction paths before edits and in its report. On wrong
   binding, error or unknown-type fallback, stop/steer away from edits; no
   parent-cwd fallback is accepted. Check retained checkout and revision from
   the result rather than guessing its generated name.
5. Serialize parent integration/rebase/squash/bookmark operations. Checkout
   separation is not an OS sandbox: absolute paths, shared jj metadata, seed
   links and extensions using process.cwd() can still affect other work.

Plain git is **not supported by this native jj adapter**. A manual fallback
requires a reviewed separate `git worktree` and an independently launched Pi
session (`cd /verified/worktree && pi`), checking actual cwd, git root, base,
and relative read/edit/write binding before editing. Likewise a manually
isolated inline session must be independently verified. Do not dispatch a
normal subagent and assume a prompt binds it to that worktree. If no verified
separate-session path is available, stop; do not install another provider as
an implicit fallback.

## Completion and correction limitation

Workspaces disposal releases a lease but retains BOTH checkout and jj
registration. No automatic cleanup, commit or integration occurs. Ordinary
completed workspace children cannot resume after disposal, even while their
files exist. Only a still-live ask-back lease may resume when the result
explicitly offers a valid continuation; retention expiry/refusal still wins.

After verification failure, record the exact retained path, immutable result
revision, base and failure evidence. This provider has **no per-call existing
workspace binding**, and fresh opted-in dispatch would create a new checkout
from its launch policy, not the failed child's revision. Do not use that as a
correction flow, or use `resume` to bypass disposal. **Stop for operator-led
recovery:** preserve the retained checkout; launch a fresh separate Pi session
from that exact path, verify cwd/root/revision and file-tool binding, then hand
it the failure evidence and same guardrails. If that binding cannot be
verified, correction remains blocked. Even changing a new session's `from`
would fork a new checkout, not re-enter the retained one.

Inspect and integrate only after diff/test review. Cleanup is manual and
requires the destructive-action approval; inspect both `jj workspace list`
and the directory after any approved removal. No resumability or safety claim
follows merely from retention.
