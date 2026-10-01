# Craft registered Codex agent acceptance

Date: 2026-10-01. Migration order: Linear → Craft → Librarian; this work
migrates Craft only. EM receives a minimal verification-caller adapter and
patch version bump; it remains Claude-only. No push or release is authorized.

## Inputs and pre-edit inventory

| Layer | Input |
|---|---|
| Repository/base | Clean JJ working copy in `jdh-agents`, parent `2a1bd1d2e73539304dc74c9ccd85e3d7beec6e86`, published Linear bookmark |
| Package | Craft 0.15.0 → 0.16.0; EM caller adapter 1.0.0 → 1.0.1 |
| Compiler | Released AgentForge v1.2.0; wrapper pin unchanged |
| Consumer binary | Absolute resolved repository `.cache/agentforge/1.2.0/agentforge-darwin-arm64`; exact path saved locally |
| SHA-256 | `67107b2a96892a1a3429010bbb8475d61c4100e1ac01783367e23aef402c2d54` |
| Runtime/platform | Codex CLI 0.158.0, Darwin arm64 |
| Tracker reads | JUN-439–443 Done; JUN-444 In Review; no distinct Craft migration issue established in that project |
| NDR grounding | Current heads `6x3v6p` and `kpefq4`, resolved through CLI |

`AGENTS.md`, `CLAUDE.md`, the operating model, compiler compatibility,
Debate/Linear source and lifecycle/acceptance records, and Craft's package,
runtime adapter, all agents and their calling procedures were read first.
The count was rechecked: exactly three canonical agents, with emitted names
`craft:house-style-reviewer`, `craft:comment-reviewer`, and
`craft:copy-reviewer`. Each has Claude `model: sonnet` and a repository-reading
tool filter; none requires a connector or bundled runtime resource.

House style reviews naming, placement, error shape, API idioms and test
structure. Comment review expands changed hunks to enclosing declarations,
including unchanged stale comments, and reads history/blame. Copy review
compares changed user-facing strings with the existing product corpus. All
three return grounded advisory reports, never edit, and exclude correctness
and linter-enforced findings. No role authorizes repository, tracker, vault,
message, commit, or publication side effects.

The sole direct named-role caller is `plugins/em/references/verify.md`.
Craft's `derive-conventions` consumes findings but does not dispatch these
roles. Generic callers remain generic: `grill` fact-finding, `grok-explorer`,
`arch-explorer` in `improve-codebase-architecture`, `model-cartographer` in
`interrogate-model`, and the architecture skill's `DESIGN-IT-TWICE.md` fan-out.
The last three named explorer workflows retain addressable follow-ups; those
labels are not packaged registered roles. `infra-review` describes a future
companion and does not dispatch it; `design-by-stories` has an Agent
permission without a dispatch operation.

Craft's wider skills can write convention files, reports, prototypes, tests,
conflict resolutions, vault records, NDRs and Lucid diagrams. Those side effects
are not authorized by migrating the three reviewers. The Lucid skill's MCP
dependency and fallback are unchanged; no live connector write is tested.

## Bounded acceptance fixtures defined before editing

The definition was saved before canonical edits at
`/private/tmp/craft-codex-plan-20261001/pre-edit-fixtures.md`. Separate isolated
user/project/fallback Codex homes and trusted disposable Git projects have
apps disabled and no MCP servers. A committed baseline plus one controlled
working diff supplies three positives:

- House style: `fetchInvoice` against declared snake_case guidance and three
  sibling public functions; naming is not covered by the fixture linter.
- Comments: an unchanged "amount in cents" docstring above a changed body
  returning dollars, with baseline history available for blame.
- Copy: changed `DELETE ACCOUNT NOW!!!` against declared sentence-case/no
  terminal punctuation and existing `Save changes`, `Cancel`, `Delete account`.

The fixture includes unrelated `notes.txt`, guidance, convention and linter
config. Review sessions must preserve repository bytes/modes/mtimes, Git HEAD
and status. Initial fixture commits and deliberate lifecycle edits happen only
in disposable repositories. Native user/project fan-out, a same-reviewer
follow-up, a generic architecture explorer follow-up, separate Markdown child
and inline procedures, and missing/stale-registration refusal are the bounded
runtime tests. Full interactive design, vault, integration, and mutation flows
are excluded. Raw traces stay local rather than being committed.

## Source and compiled output

Local JJ commit `90c9ff49e8fcf278014e8e7839a195f36bd5a6cf` contains the
canonical Craft and EM caller edits together with the generated marketplace
output. Craft declares `codex-agent-bundle: true` at 0.16.0. The generated
Codex bundle index and three TOMLs are under
`marketplaces/codex/plugins/craft/.agentforge/codex-agent-bundle/`;
the index hashes match the TOMLs. Root/package manifests and Claude/Codex
marketplaces were regenerated with `scripts/agentforge.sh`, not hand-edited.
The wrapper pin remains AgentForge v1.2.0. Its released Darwin arm64 binary
had the SHA-256 above and was used by absolute path for all consumer runs;
the consumer PATH excluded Bun and an AgentForge checkout.

No Codex model or effort is pinned. The Claude `sonnet` aliases and read-only
tool lists remain Claude source only. Codex roles inherit the parent model,
effort and available tools; approval/sandbox behavior is runtime-selected,
not translated from Claude permission settings. This is a deliberate policy
loss: the Claude per-role tool allowlists are not enforced by the Codex TOMLs.
Each compiled reviewer has a focused advisory instruction body and explicit
no-edit/no-external-side-effect language. Packaged `agents/*.md` alone never
registers a Codex role.

## Native installation and lifecycle

`/private/tmp/craft-codex-lifecycle-20261001/evidence/summary.json` records
74 completed native/AgentForge commands and `PASS`. The harness archived the
committed compiled marketplace, installed it with `codex plugin` into isolated
user/project `CODEX_HOME` directories, and used the verified released compiler
for selected-scope operations. Both scopes covered missing registration,
setup, repeat no-op (including mode/mtime stability), drift check, content
update, rename/deletion update, an edited managed file and same-name
registration conflict that refused update, plugin removal, receipt preview
and cleanup, repeated cleanup, and preservation of unrelated state. The
0.16.1/0.16.2 update variants were authored and compiled only in disposable
Git repositories. These direct lifecycle results do not establish model
behavior or ordinary Codex project-setup sandbox success.

The fresh runtime fixture independently native-installed the committed Craft
0.16.0 plugin into three isolated homes. Per-scope byte/mode snapshots show
installed cache equal to committed compiled plugin output:
`/private/tmp/craft-codex-runtime-20261001/evidence/{user,project,fallback}-cache-equality.json`.
Before setup there was no Craft registration in any scope. The installed
setup skill and helper, rather than an authoring checkout, supplied subsequent
setup/check commands. `/private/tmp/craft-codex-runtime-20261001/evidence/`
holds commands, raw JSONL session events and rollout metadata; the local
`runtime-evidence-summary.json` indexes them. Raw traces are intentionally
outside the commit.

## Skill activation, scope checks and dispatch

| Fresh session | Observed result |
|---|---|
| User setup, ordinary child `workspace-write` | Explicitly read installed `$craft:setup-codex-agents`; guarded `install user` exit 0 registered exactly three roles, then `check user` exit 0 reported five current managed paths. An added writable directory was limited to the isolated user home. |
| Project setup, ordinary child `workspace-write` | Explicitly read the installed setup skill; `install project` exited 1 with `EPERM` creating disposable `project/.codex`. It stopped before check or dispatch. This is a failed ordinary sandbox acceptance. |
| Project setup, approved unrestricted control | After explicit approval for one control, the constrained `project/setup-control` child ran only guarded installed-skill `install project` and `check project`; both exited 0 and the latter reported five current managed paths. The control is separate from ordinary acceptance. |
| User native review fan-out | Four `check user` calls exited 0, immediately before each exact native spawn and before the same-agent follow-up. The three role IDs were `01a0f841-d261-7020-971d-a9a68035885d`, `01a0f841-f8eb-7732-9aea-a0a1c69982e5`, `01a0f842-1f83-7fc1-a812-3e538ee01cc3`. |
| Project native review fan-out | Three `check project` calls exited 0 immediately before exact native spawns. IDs were `01a0f84a-6680-7941-a449-ccf445f43a8e`, `01a0f84a-9223-7dc2-a4d6-d32c62246b35`, `01a0f84a-ba72-7211-987d-940095220dd4`. |
| Registration negatives | A fresh unregistered home returned `missing: 5 managed paths`; a disposable edited role returned `edited: 5 managed paths`. Both model sessions stopped with zero spawns and no automatic fallback. The edited role was restored byte-for-byte before cleanup. |

The parent rollout tool inputs contain exact `agent_type` values
`craft:house-style-reviewer`, `craft:comment-reviewer` and
`craft:copy-reviewer`, with no child model/effort/tool/permission override.
Each corresponding child `session_meta.agent_role` equals the requested
name. This is dispatch evidence distinct from compiled TOML and cache bytes.
Initial nested launcher attempts failed with `sandbox-exec: sandbox_apply:
Operation not permitted` before executing repository commands; they are not
counted as acceptance. The later outer launcher used approved execution
outside that nesting while Codex children still declared explicit read-only
or `workspace-write` sandboxes. Only the one project setup control used child
`danger-full-access`.

## Observed behavior and applied settings

Both scopes' house-style reviewers identified `src/accounts.py:1`
`fetchInvoice` against the fixture's snake_case convention. Both comment
reviewers identified the stale unchanged `src/money.py:2` cents docstring
above a changed division-by-100 body. Both copy reviewers identified the
all-caps/exclamation `DELETE ACCOUNT NOW!!!` against the sentence-case
product corpus. They returned advisory findings; no code was edited. The
user house-style reviewer continued on the **same** ID
`01a0f841-d261-7020-971d-a9a68035885d`, checked `pyproject.toml`'s Ruff
`E4`/`F` selection, and retained the naming finding as outside that linter
configuration. This bounded fan-out exercised EM's Craft review-caller
contract as supplied context; a full EM verification or `/code-review` was
not run.

All six registered child rollouts report `gpt-5.6-luna` and `medium` in
`turn_context`, inherited from the test parent, with read-only child sandbox.
The user house-style continuation has a second turn context with the same
values. These are observed runtime metadata, not package pins. Backend model
routing beyond the reported runtime values is unknown. The CLI reported
0.158.0. No Claude per-role tool filter can be inferred from these traces.

## Separate Markdown and generic paths

In an unregistered isolated home, an explicitly selected procedure fallback
read each installed `agents/*.md` body, spawned three **generic** bounded
children without `agent_type`, and got the same three grounded review
categories. It separately ran the comment procedure inline with no child.
Generic IDs were `01a0f848-e6fc-7920-ac3b-9885ae58950a`,
`01a0f849-8cc8-73f0-80b6-33d4ad942a42`, and
`01a0f84a-4b59-7043-9fd9-8def6248d302`. No registration was installed.
An installed `improve-codebase-architecture` excerpt used one generic
`arch-explorer` child, ID `01a0f849-4deb-72b0-b4e9-cbd62af184e6`, for
source-only exploration and a follow-up on that **same** ID. Its second
response correctly identified the stated output unit and unspecified input
unit in `money.py`; the parent shortened this inaccurately to “docstring
leaves units unspecified.” The child trace is the evidence. Full architecture
design/report creation and other Craft write-capable skills were not tested.

## Effects, cleanup and Git outcome

Runtime configs had `features.apps = false` and no MCP server configuration.
No live connector, tracker, vault, message, or external write was exercised;
these surfaces remain untested. In the runtime/lifecycle probes, source/Git
writes occurred only in disposable fixture repositories for preparation or
synthetic lifecycle variants. Every runtime session's post-snapshot matched
its fixture's files, HEAD, refs, reflog and status; see
`*-fixture-after.json`. Native plugin
removal followed by scoped receipt cleanup passed separately for user,
project and unregistered fallback homes, removed each cache/auth link, and
left no Craft role registration. No bare user-scope cleanup command ran.

The normal Codex installation retained the same 1,402 paths, bytes and modes
in `agents`, `plugins`, `skills`, and `config.toml`; ten remote-plugin install
metadata files had mtime-only changes after the initial baseline. These were
left untouched and are recorded in `evidence/normal-install-after.json`.
JUN-444 was read as In Review; no tracker status or record was changed because
this Craft migration has no established separate ticket and ordinary project
setup remains denied. Local bookmark `craft-codex-agents` contains the
source/generated commit above; the acceptance commit is recorded below after
final gates. Neither bookmark nor a release has been pushed/published.

## Final gate and local commit

The pinned `scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces
--claude-native` passed: 238 Claude and 241 Codex managed files matched,
and both native Claude manifests validated. The Craft native lifecycle matrix
passed 74 commands. The probe guard self-test passed, including poisoned
environment, path-traversal, wrong-control-mode and MCP/app rejection cases;
`python3 -m py_compile` passed for both harnesses. The privacy-gate self-test
passed six checks, `scripts/privacy-scan.sh` found no leaks across 420 scanned
commits, and `git diff --check` passed. Scoped review found only the Craft
migration and its minimal EM caller adapter in the source/generated commit,
plus this acceptance record and the guarded project-control harness change in
the follow-up JJ change `zvyrnpwk`.

The remaining blocker is ordinary project-scope setup under the tested Codex
`workspace-write` sandbox (`EPERM` on `.codex`). The approved unrestricted
control proves project registration and read-only dispatch only under that
separate condition. Full EM verification, `/code-review`, other Craft workflows,
connector-backed skills, write-capable skills, and external effects remain
untested. No Craft tracker status was changed. Local commits only; no push or
release.
