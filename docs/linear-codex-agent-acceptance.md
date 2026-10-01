# Linear registered Codex agent acceptance

Date: 2026-10-01. Migration order: Linear → Craft → Librarian; only Linear
roles are migrated here. PM receives four caller-contract links and a patch
bump, with no role migration. No branch push or release is authorized.

## Inputs and pre-edit audit

| Layer | Observed input |
|---|---|
| Repository/base | `jdh-agents`, clean JJ working copy on `main` at `cda87cdd28c6aeb8f2adf153e1e832d08bd33c17` |
| Source + generated consumer commit | `6d36cf670dc8025139496f5a4c84d933ca3933bf` |
| Package | Linear 0.8.0 → 0.9.1; PM caller adapters 0.14.0 → 0.14.1 |
| Compiler | Released AgentForge v1.2.0, existing wrapper pin unchanged |
| Verified absolute binary | Absolute resolved repository `.cache/agentforge/1.2.0/agentforge-darwin-arm64`; exact path saved in local evidence |
| Binary SHA-256 | `67107b2a96892a1a3429010bbb8475d61c4100e1ac01783367e23aef402c2d54` |
| Runtime/platform | Codex CLI 0.158.0, Darwin arm64 |
| Runtime test parent settings | `gpt-5.6-luna`, medium; test inputs, not package settings |
| Tracker read | JUN-444 remains In Review; JUN-439–443 are Done; no distinct Linear migration issue established |
| Remote read | GitHub main resolves to `8e296b3533526dcfb4949c3f64c0f0074398f880`; local base is the selected Forgejo `main` lineage, not inferred GitHub parity |

`AGENTS.md`, `CLAUDE.md`, the operating-model, compatibility and JUN-444
acceptance documents, Linear's package/role/skills/references, and Debate's
declaration/settings/dispatch flow were read before edits. A bounded read-only
audit found one Linear role and four PM callers: author, breakdown, chart,
lead. Spec-flow currently writes directly; its stale mention in the role's
description was removed, without migrating its workflows.

The role requires a connected Linear integration and resolves existing teams,
projects, labels, statuses, milestones and cycles. It can create/update/transition
issues, apply declared relations, and comment. These operations affect shared
tracker records; no real write was authorized for this acceptance run.
Missing connector or reference context blocks writes; private data is never
replaced with web search or model memory. Parent links require the caller's
installed PM layer policy and a read confirming that the proposed parent is
not itself a subissue. NDR heads `6x3v6p` and `kpefq4` were resolved live.

## Source and generated output

Only canonical package/role/skill/README sources were edited. All managed
marketplace files and the root Claude manifest were regenerated through
`scripts/agentforge.sh`, with compiler escape hatches unset. The released
compiler initially rejected a package-relative gotchas reference. The final
role requires an exact installed path or verbatim contents supplied by its
caller on both runtimes, including the existing literal Markdown fallback.
No authoring checkout is required by consumers.

The bundle index emits exactly `linear:linear-ops` at
`agents/linear/linear-ops.toml`. It records both model and effort as inherited,
and `tools` as a loss. Generated TOML contains no model, effort, tool filter,
approval or sandbox setting. Claude's `haiku` alias and allowlist stay in
Claude source/output; `list_teams` and `list_comments` were added to support
the advertised resolution and gotchas procedure. Codex connector operation
names remain semantic mappings, not tool grants.

The setup skill's generated sidecar is explicit-only. The Linear skill derives
the installed helper from its active path, checks the selected scope before
each native dispatch in a fresh session, and passes exact `agent_type:
"linear:linear-ops"`. A failed/stale check blocks that dispatch. Both the
existing inline literal procedure and generic child with `agent_type` omitted
remain separate explicitly chosen fallback routes. The four PM callers defer
to this contract and supply the installed reference context.

Current official documentation describes standalone custom-agent TOMLs and
inherited model/reasoning settings; it does not make the retained plugin
Markdown register a role. Runtime observation remains the acceptance evidence.
[OpenAI subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents),
[Claude plugin manifest reference](https://code.claude.com/docs/en/plugins-reference).

## Installed native lifecycle

The reproducible direct-CLI matrix is
`scripts/tests/run_linear_codex_lifecycle.py`. It archives the exact committed
source and compiled Codex publication, creates separate isolated homes and
trusted disposable projects, installs through native `codex plugin marketplace
add` / `codex plugin add`, and compares every installed plugin file's bytes and
mode with the committed archive. Every native/lifecycle invocation explicitly
sets and validates the fixture `CODEX_HOME`; lifecycle scope and project-root
arguments must exactly match the fixture. Consumer PATH is
`/usr/bin:/bin:/usr/sbin:/sbin`, and the verified binary is absolute. Bun and an
AgentForge checkout are absent from the consumer boundary.

```sh
LINEAR_REPO="$(pwd -P)"
python3 scripts/tests/run_linear_codex_lifecycle.py \
  --agentforge-bin "$LINEAR_REPO/.cache/agentforge/1.2.0/agentforge-darwin-arm64" \
  --codex-bin /opt/homebrew/bin/codex \
  --source-repo "$LINEAR_REPO" \
  --source-commit 6d36cf670dc8025139496f5a4c84d933ca3933bf \
  --run-root /private/tmp/linear-codex-lifecycle-091-20261001
```

The matrix passed 74 recorded commands. Both scopes passed missing detection,
install/check, repeat no-op including file modes/mtimes, canonical content
update, rename/deletion, edited-definition and edited-registration refusal,
conflict-preserving removal after native plugin/cache removal, restoration of
the deliberate fixture edits, final receipt-only cleanup, and repeat cleanup.
Unrelated config/trust/agent/marker hashes were preserved. The derived 0.9.2
fixture adds one synthetic role solely to exercise deletion while 0.9.3 renames
the real role and deletes the synthetic one. Both fixtures edit canonical
source, recompile, and commit source/output in a separate disposable authoring
repository; they are not versions proposed for release.

Evidence: `/private/tmp/linear-codex-lifecycle-091-20261001/evidence/` contains
inputs, exact commands/environments/stdout/stderr/exits, committed archive
hashes, cache equality snapshots, scope snapshots and `summary.json`/`.txt`.
`auth-link-cleanup.txt` and parent checks confirm both unread disposable auth
symlinks are absent. This direct-CLI matrix does not establish model sandbox
acceptance or skill activation.

## Fresh sessions and connector effects

Final runtime evidence is at `/private/tmp/linear-codex-final-20261001/`.
Setup was tested against committed `5f08466d455c73497207943f69260dda61d977ff`
(0.9.0). Native reinstall/update then used committed
`6d36cf670dc8025139496f5a4c84d933ca3933bf` (0.9.1), which fixes initial-write
parent placement. `reviewed-cache-equality.json` in each scope confirms ten
installed Linear files match that commit in bytes and modes. The setup skill
and helper are unchanged between these versions; the role and bundle index
changed. Both registered scopes passed update/check before fresh dispatch.
PM 0.14.1 was installed to provide its actual layer policy. The fallback home
had no registered role.

`scripts/tests/run_linear_codex_probe.py` records each exact command, isolated
environment, prompt, JSONL stream, stderr, final message and process exit.
Outer exit zero alone never counts as tool success. Launching outside the
parent sandbox avoids nested `sandbox-exec` failures while retaining the
child's specified sandbox. The explicit setup-skill activation evidence is
its installed `SKILL.md` read followed by helper invocations, rather than
inferred discovery or a skill-picker UI event.

Mock sessions disable apps and expose exactly one network-free stdio MCP
fixture, `scripts/tests/linear_mock_mcp.py`. Its local log/state contain all
simulated writes. `--mock-writes` preapproves only that fixture's `save_issue`
and `save_comment` with `approval_mode="approve"`, after validating the isolated
configuration; it does not change product policy or the normal installation.
The earlier `auto` setting did not preapprove writes and those runs are excluded
from write acceptance. The correct value follows the explicit per-tool MCP
configuration documented by [OpenAI](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

| Probe | Observed result / evidence stem |
|---|---|
| Initial nested setup | User/project tool exit 71, `sandbox-exec: sandbox_apply: Operation not permitted`; no acceptance. Initial user retry additionally used a wrong executable-bit preflight for the 0644 shell helper and falsely claimed success after exit 1; excluded. Evidence retained in `linear-codex-acceptance-20261001`. |
| Ordinary user setup | `user/setup.*`: explicitly activated installed setup skill, install/check tool exits 0, `current: 3 managed paths`. |
| Ordinary project setup | `project/setup.*`: EPERM creating project `.codex`; failed, no ordinary sandbox acceptance. |
| Explicitly approved project control | `project/setup-control.*`: user's one unrestricted control, apps/mock/live access disabled; installed skill read, project install/check exits 0 and current. This is control evidence, not ordinary sandbox acceptance. |
| User registered role | `user/dispatch-preapproved.*`: six sequential exact `linear:linear-ops` children; six selected-scope checks exit 0 before dispatch. Parent does not read/embed role Markdown/TOML or override child settings. |
| Project registered role | `project/dispatch-preapproved.*`: one exact native child following a current project check; create and read-back succeed. |
| Fallback | `fallback/procedure-verified.*`: generic child with `agent_type` omitted and verbatim installed role/reference content, followed by the inline literal procedure; both create/read-back succeed, no registration. Earlier generic fallback correctly blocked on unreadable reference context and is retained separately. |
| Live read-only connector | `linear-codex-live-20261001/user/doctor.*`: fresh explicit installed doctor activation and six native Linear reads: teams, team, labels, statuses, users, cycles. Zero tracker writes. Tested 0.9.0 doctor/gotchas bytes, unchanged in 0.9.1. |

`mock-assertions.json` confirms the user fixture wrote exactly three issues and
one comment: normal create, deliberately dropped label, and validated parent
handoff. All descriptions equal the supplied full body. Missing body, unknown
label and nested-parent intents returned blocked without writes. The dropped
`backend` label was reported after read-back with no blind retry. `FIX-PARENT`
was read before the handoff create and `parentId` was on the initial
`save_issue`; exactly one `@fixture-other` comment followed. Project performed
one create. The two verified fallback routes preserved their explicitly
supplied one-line descriptions. An earlier inline probe with ambiguous nested
body headings is retained but excluded from verbatim-body acceptance.

`runtime-observations.json` saves filtered child metadata, turn settings and
actual parent spawn calls. All seven native children report exact role
`linear:linear-ops`, model `gpt-5.6-luna`, effort `medium`, and read-only
filesystem sandbox. The verified generic child has no named role. Parent final
text called runtime settings unknown; the child turn traces separately expose
them. These are observed inherited fixture settings, not a package pin or a
claim about backend routing. Backend model identity and effective mechanical
connector/tool enforcement beyond observed calls remain **unknown**.

The live doctor reported missing `database` label and otherwise read the team,
states, users and current cycle; no workspace correction was attempted. Earlier
parent tracker issue/project reads were also read-only. Mock effects are never
live tracker acceptance. No tracker status/comment was changed: JUN-444 remains
In Review and no distinct Linear migration issue was established.

## Gates, cleanup, Git and remaining surfaces

Released compiler/native strict validation, privacy gate self-test (six checks),
Python syntax checks and the lifecycle/mock assertions passed. The ten probe
guard checks passed without spawning Codex (`probe-guard-tests.json`), including
wrong compiler, wrong MCP command, additional server, enabled apps, modified
mock source, and symlinked mock root. The probe harness requires Python 3.11+
and the verified Darwin arm64 binary; consumer setup itself uses shell and the
released binary. Source/generated
scope and whitespace were reviewed. The final history privacy scan is recorded
in the local evidence after the acceptance commit.

Guarded cleanup removes each isolated native plugin/cache first, then previews
and removes receipt-owned roles with the verified absolute compiler. Every
invocation sets and validates its fixture `CODEX_HOME` and project root, even
for user-scope cleanup; none is a bare user cleanup. Local cleanup records
preserve commands/exits. All disposable auth links are removed without reading
or modifying their targets. `cleanup-evidence.json` in the initial, final and
live fixture roots confirms receipt cleanup and no remaining Linear roles. The normal Codex configuration/plugin installation's original 1,318-file
byte/mtime baseline (excluding credentials) passed with zero differences after probes; result recorded in
`normal-install.after.json` / `normal-install-comparison.json`.

Local JJ commits keep canonical source and managed output together:
`5f08466d` adds the bundle, caller adapters and harnesses (0.9.0);
`6d36cf67` fixes initial parent placement (0.9.1); a final acceptance commit
contains this record, the fixture-only approval correction, and strict parsed
MCP/verified compiler guards. The review found no remaining Linear source
defect; fixture guards now reject arbitrary MCP commands and unverified binaries. The local
bookmark is `linear-codex-agents`. Narrow JJ metadata authority was needed for
protected `.git` writes. No push, release, or tracker mutation occurred.
The exact final commit IDs are supplied in the handoff and local Git evidence;
the record cannot embed its own content-addressed commit ID.

The remaining environmental blocker is ordinary sandbox project setup (EPERM).
Approved control proves installation and dispatch, not normal-sandbox setup.
Untested surfaces: desktop/skill-picker discovery, other platforms, mechanical
Codex tool-policy enforcement, end-to-end PM planning/approval flows, spec-flow's
direct writes, live mutations, arbitrary comment/block/related-to/update/
transition intent paths, and same-agent continuation. The one required handoff
comment is mock-tested. Linear's single-operation workflow does not require
Debate's multi-round follow-up. Craft and Librarian migrations have not started.
