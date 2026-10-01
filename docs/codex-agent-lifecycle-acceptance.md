# JUN-444: installed Codex agent lifecycle acceptance

Linear's subsequent migration uses this implementation as its reference and
records its own inputs and limits in
[Linear Codex agent acceptance](linear-codex-agent-acceptance.md). Debate's
historical results below do not establish acceptance for Linear.

Craft's subsequent migration is recorded separately in
[Craft Codex agent acceptance](craft-codex-agent-acceptance.md); neither
Debate nor Linear's runtime results establish acceptance for Craft.

Date: 2026-09-29. Original result: **unreleased local build; scoped local acceptance passed**.
[JUN-444](https://linear.app/junglelan/issue/JUN-444/jdh-agents-installed-codex-agent-lifecycle-acceptance)
initially encountered a compiler-pin gate; the released v1.2.0 recheck below supersedes that blocker.
No public AgentForge release or branch push was performed by this work.

## Pinned inputs and build

| Input | Observed value |
|---|---|
| AgentForge commit | `a79a20057e008548ce9a6ae0c1a48f0c5818611e` |
| Forgejo refs | Both `main` and `jun-443` resolve to that commit |
| Build | Detached clean checkout; Bun 1.4.2; `bun install --frozen-lockfile`, `bun run build` |
| Binary | `/tmp/jun-444-build-bwh9mT/bin/agentforge-a79a200-darwin-arm64` |
| SHA-256 | `3b730dfea2c5c6b41f67c2b17949351a945a8c4e5d088135a50ae297a2532d82` |
| Embedded version | `1.1.0`; this is unchanged source metadata, **not** public v1.1.0 acceptance |
| Consumer source + generated commit | `d873a4a4116135ea734e72d843bbbd540853b4ba` |
| Plugin / runtime / platform | Debate 0.5.0; Codex CLI 0.158.0; Darwin arm64 |
| Native Claude validator | Claude Code 2.1.284 |

The earlier preflight found separate `31cd8df4` and `086aa152` branches and
correctly stopped before building. That blocker is now resolved: `a79a2005`
contains `cef06a8e` and `31cd8df4` (copied-file materialization/check mode fixes)
in ancestry, followed by the rebased lifecycle changes. Its JUN-443 changed-path
content matches the prior tip `086aa152`; both patches have ID
`121b5680469af7bd03bbd87038e81539ab2e4521`.

Exact build/provenance evidence is in `/tmp/jun-444-build-bwh9mT/evidence/`:
`provenance.txt`, `rebase-comparison.txt`, `build.txt`, `SHA256SUMS`,
`lifecycle-command-help.txt`, and `standalone-probe.txt`. The standalone probe
ran outside the checkout with `env -i PATH=/usr/bin:/bin`. All nine lifecycle
commands below were observed in the executable's help, not inferred from a
version string:

```text
preview-codex-agent
install-codex-agent
check-codex-agent
preview-codex-agent-update
update-codex-agent
preview-codex-agent-remove
remove-codex-agent
repair-codex-agent-update
repair-codex-agent-remove
```

Upstream verification: 28 focused lifecycle tests passed; typecheck and lint
passed (lint retains the existing Biome schema-version informational notice).

## Consumer implementation and losses

Debate is self-contained at the agent boundary: each role receives its context
in the dispatch prompt. Synthesizer consumes supplied evidence; advocate,
fact-checker, and devil's advocate research on the web. No role requires bundled
references, scripts, or assets. Optional vault context and decision-record
writing were excluded from the acceptance fixture and remain unexercised.

`plugins/debate/PACKAGE.yaml` opts into `codex-agent-bundle: true` and bumps
0.4.1 to 0.5.0. AgentForge emits a v2 bundle index, four role TOMLs, and the
explicit-only `setup-codex-agents` skill alongside retained Markdown procedures.
A native plugin install exposes the skill; it does not register the roles.
The visible helper invokes the central lifecycle CLI for the chosen scope,
which owns v3 receipts. A fresh session and current selected-scope check precede
exact namespaced dispatch. A deliberately chosen generic Markdown procedure
remains a separate path.

| Role | Authored Codex model | Authored effort | Runtime probe |
|---|---|---|---|
| `debate:advocate` | Inherit | Inherit | Luna / medium, both follow-up rounds |
| `debate:fact-checker` | Inherit | Inherit | Not dispatched; applied values unknown |
| `debate:devils-advocate` | Inherit | Existing canonical high | Not dispatched; applied values unknown |
| `debate:synthesizer` | `gpt-5.6-terra` | Existing canonical high | Terra / high, both scopes |

Terra is an explicit choice for the bounded supplied-evidence synthesis pilot,
using the model already exercised by the integrated upstream role probe. High
effort serves evidence comparison and independent synthesis. This is not a
Claude `opus` mapping or a claim of optimal model selection. Other roles do
not gain a model pin from Claude `sonnet`/`opus`. The old equivalence wording
has been removed.

The declared `agent-tools-filter` loss remains. Claude tool allowlists,
permission semantics, and turn limits are not converted into Codex sandbox
policy. Repeated prose boundaries guide the child but do not mechanically
restrict tools. No tool use was observed for the supplied-evidence synthesis
probes; that does not establish enforcement. Unobserved settings remain
unknown. Grounding: AgentForge `ndr:bqyqfd`; jdh-agents `ndr:6x3v6p` and
`ndr:kpefq4`.

## Installed cache and fresh sessions

The runtime fixture exported `marketplaces/codex` with `git archive` from the
committed consumer revision above. For each scope it created a separate Codex
home and a disposable trusted project, linked the existing authentication file
without copying or printing it, and ran native installation:

```sh
CODEX_HOME=/tmp/jun-444-runtime/user/codex-home \
  /opt/homebrew/bin/codex plugin marketplace add \
  /tmp/jun-444-runtime/marketplaces/codex --json
CODEX_HOME=/tmp/jun-444-runtime/user/codex-home \
  /opt/homebrew/bin/codex plugin add debate@jdh-agents --json
```

The project-scope fixture uses `project/codex-home` instead of `user/codex-home`.
Both caches were byte-identical to the committed plugin, including the bundle,
helper, and explicit-only sidecar (`user/cache-equality.json` and
`project/cache-equality.json`). The normal Codex config and plugin installation
were not changed.

`/tmp/jun-444-runtime/run_probe.py` saved each exact command/environment in
`<scope>/<probe>.command.json`, the prompt in `.prompt.txt`, streamed output in
`.events.jsonl`, stderr in `.stderr`, and process status in `.exit`. Commands
used isolated `CODEX_HOME`, absolute `AGENTFORGE_BIN`, and
`PATH=/usr/bin:/bin:/usr/sbin:/sbin`; `allow_login_shell = false` preserved that
PATH. `consumer-path-probe.txt` confirms Bun and PATH-resolved AgentForge are
absent. Consumer CWDs contain no AgentForge checkout; no consumer invokes Bun
or compiles source.

Explicit setup activation means an explicit `$debate:setup-codex-agents`
request with its installed path, followed by the model reading and following
that installed `SKILL.md`. This tests CLI execution; skill-picker UI discovery
and desktop behavior were not tested.

| Probe | Evidence relative to `/tmp/jun-444-runtime` | Result |
|---|---|---|
| Initial nested sandbox attempts | `{user,project}/setup.events.jsonl` | `sandbox-exec: sandbox_apply: Operation not permitted`, exit 71 before reads; no setup |
| Explicit user setup | `user/setup-native.events.jsonl` | Child `workspace-write`: install and check exit 0, four roles, six managed paths |
| Explicit project setup | `project/setup-native.events.jsonl` | Child `workspace-write`: install exit 1, `EPERM` creating project `.codex`; stopped without dispatch |
| Project write-access control | `project/setup-control.events.jsonl` | Child `danger-full-access` within the parent environment: install/check exit 0; not normal-sandbox write acceptance |
| Fresh native user dispatch | `user/dispatch.events.jsonl` | Selected-scope check passes; exact `debate:synthesizer` dispatch |
| Fresh native project dispatch | `project/dispatch.events.jsonl` | Selected-scope check passes; exact `debate:synthesizer` dispatch |
| Separate procedure path | `user/procedure.events.jsonl` | Generic child, `agent_type` omitted, installed Markdown embedded |
| Same-agent follow-up | `user/followup.events.jsonl` | `debate:advocate` re-engaged through `send_input`; same ID in both rounds |

The nested sandbox retry launched Codex outside the parent sandbox so its own
sandbox could start. User setup then passed normally; project setup exposed the
separate protected `.codex` boundary. No denial was counted as successful setup.

Both native synthesizers returned the supplied fixture's Room A verdict,
conditioned on confirming the private door, with the complete role-specific
verdict, reasoning, evidence, trade-offs, conditions, and confidence breakdown.
Their spawn prompts did not embed the role instructions or set model/effort.
The generic procedure child independently returned the same fixture choice.
The advocate performed bounded official SQLite research, accepted the
connection/transaction caveat in Round 2, addressed application-only validation,
and reduced confidence from 90% to 87% using the same child ID.

Child metadata establishes applied values via `turn_context.model` and
`turn_context.effort`; `session_meta.agent_role` records the role. No separate
`thread_settings_applied` event is claimed for these runs.

| Probe | Child ID | Applied model / effort |
|---|---|---|
| User synthesizer | `01a0ee68-5e1e-7a23-bbf8-6fd771132494` | `gpt-5.6-terra` / high |
| Project synthesizer | `01a0ee68-850d-7f90-bbb2-f4772ff5064d` | `gpt-5.6-terra` / high |
| Generic procedure | `01a0ee69-7066-7cf3-9899-94ab1975883b` | `gpt-5.6-luna` / medium |
| Advocate, both rounds | `01a0ee69-3ba7-7e60-826a-3ad5d8d6f25a` | `gpt-5.6-luna` / medium |

Rollouts are in each isolated Codex home’s `sessions/2026/09/29/` directory,
with each child ID in its filename. `evidence/evidence-summary.json` records exact relative trace
paths and field evidence; `evidence/analysis.md` summarizes observations.

## Lifecycle matrix

Final accepted run: `/tmp/jun-444-lifecycle/run-a79a200-finalproof2/evidence/`.
The reproducible harness is `/tmp/jun-444-lifecycle/run.sh`. Each operation has
an ordinal `.command`, `.stdout`, `.stderr`, and `.exit` file; `summary.txt`
records all results. `consumer-boundary.txt`, `snapshot-*.sha256`, and
`bundle-bytes-*.txt` record environment, preservation, and installed digests.

Every lifecycle bundle argument comes from the `installedPath` returned by a
fresh native `codex plugin add --json`, never from authoring source or compiled
publication directories. Both scopes finish each version phase before native
plugin removal and installation of the next version. Codex owns the cache;
AgentForge updates existing external registrations explicitly.

| Probe, run for both scopes | Observed result |
|---|---|
| Initial check, preview, setup | Missing check exits 1 as expected; preview/install exit 0; current check reports six managed paths |
| Repeat setup | Exit 0; full before/after scope snapshots identical |
| Content update 0.5.0 → 0.5.1 | Preview/update/check exit 0; installed TOML digests match the new native cache index |
| Rename/deletion 0.5.1 → 0.6.0 | Synthesizer renamed to `synthesizer-renamed`; devil's advocate deleted; old definitions absent, renamed definition present; check current with five paths |
| Deliberately edited role and registration | Check/update exit 1; both edited byte hashes unchanged |
| Native plugin removal | Installed cache version directory absent before receipt cleanup |
| Conflict-aware removal | Exit 0 with unresolved edited role retained for review; no false full-cleanup claim from exit status |
| Receipt cleanup after resolving fixture edits | Restore only deliberate edits; remove by package ID without bundle; no owned registrations, definitions, or receipt remain; repeated remove exits 0 |
| Unrelated content | User/project sibling agents and project files retain hashes; unrelated models/trust config remain |

The two derived fixture versions were authored from committed Debate source,
regenerated through `AGENTFORGE_BIN`, checked, and committed with all managed
output including the root Claude manifest. No generated fixture was hand-edited:

- Content fixture 0.5.1: `78164576d201369fdf479dfaab3d603589af62d5`.
- Rename/deletion fixture 0.6.0: `700d1a268e80cb911390c61766b6e6bcb5de97e1`.

These are disposable local test commits, not published Debate versions. The
real package at that revision was 0.5.0. The shared script's invocation is reproducible from
this repository with a new unused run directory:

```sh
AGENTFORGE_BIN=/tmp/jun-444-build-bwh9mT/bin/agentforge-a79a200-darwin-arm64 \
SOURCE_REPO="$PWD" \
SOURCE_COMMIT=d873a4a4116135ea734e72d843bbbd540853b4ba \
BASE_MARKETPLACE="$PWD/marketplaces/codex" \
CODEX_BIN=/opt/homebrew/bin/codex \
RUN_ROOT=/tmp/jun-444-lifecycle/reproduce \
  bash /tmp/jun-444-lifecycle/run.sh
```

The harness uses the authoring checkout only to compile/commit fixture updates;
consumer commands run from `/private/tmp` with the restricted PATH and the
standalone binary's absolute path. The final native cache is removed before
receipt operations. Main-thread review independently inspected final config,
role directories, and receipts rather than accepting the worker's summary.

The first CLI harness run is excluded from installed acceptance: it installed a
plugin but invoked lifecycle operations against compiled publication/authoring
paths, and its attempted 0.5.1/0.6.0 version edits did not match the package's
JSON-style defaults. Review caught both errors before acceptance reporting.
The next attempt consumed native caches but restored a whole pre-removal config
while resolving a deliberate conflict, resurrecting already removed registrations.
That attempt is also excluded. Final acceptance must assert absence of owned
registrations, definitions, and receipt rather than relying on a zero exit.

Independent cleanup of the completed model-session fixtures passed in both
scopes: native plugin removal deleted the installed cache first, then preview,
receipt-based removal, and repeat removal succeeded. Assertions confirmed no
owned role blocks, definitions, or receipt remained and project guidance was
unchanged. Exact commands/results are in
`/tmp/jun-444-runtime/{user,project}/cleanup.json`. Authentication symlinks in
those two homes were removed after the runs.

## Original unreleased verification and historical gate

```sh
AGENTFORGE_BIN=/tmp/jun-444-build-bwh9mT/bin/agentforge-a79a200-darwin-arm64 \
  scripts/agentforge.sh compile MARKETPLACE.yaml --out marketplaces
AGENTFORGE_BIN=/tmp/jun-444-build-bwh9mT/bin/agentforge-a79a200-darwin-arm64 \
  scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native
```

Both commands passed. The compiler also normalized the two generated Introspect
`conversation-analysis.py` copies from 0755 to 0644; their bytes are unchanged,
and their skill invokes them through `uv run` or `python3`. These are
reproducible compiler-owned mode changes, not hand edits or new source policy.

The independent normal merge-gate command was:

```sh
env -u AGENTFORGE_BIN -u AGENTFORGE_PROJECT \
  scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native
```

It exited 1 under the then-current public v1.1.0 pin:

```text
plugins/debate/PACKAGE.yaml: invalid definition (targets.codex: Unrecognized key: "codex-agent-bundle")
```

That failure happens before output comparison. A local-binary check is not the
normal CI merge gate. The reviewable path forward is a separately authorized
AgentForge release containing this integration, verification of its downloaded
binary, and a reviewed wrapper version/hash update followed by compile/check
and CI. Nothing in this acceptance authorizes that release or a branch push.

Other checks: `scripts/tests/test_privacy_gate.sh` passed six checks;
`UV_CACHE_DIR=/tmp/jun-444-verification/uv-cache uv run
scripts/tests/test_introspect_usage_report.py` passed two tests;
`scripts/privacy-scan.sh` passed on committed history. An initial direct Python
unittest invocation failed because pytest was absent; the script's documented
`uv run` entry point resolved its declared dependency and passed.
`git diff --check` passed. Logs are in `/tmp/jun-444-verification/`.

## Evidence and Git outcome boundaries

Compiled output is committed at `d873a4a4`; native cache equality, explicit skill
activation, namespaced dispatch, observed behavior/settings, and lifecycle
mutation results are separate evidence above. Review found no blocking source
or generated-output defect. The initial planning record is local commit
`9736865f`; the consumer source and generated output are together in
`d873a4a4`. No branch was pushed and no public release was published by this work.

Scratch traces and the build are local files under `/tmp`, not committed raw
session data; their retention is not guaranteed. Essential results, full input
hashes, commands, and trace identities are retained here. Unverified surfaces:
Codex desktop, skill-picker UI, full end-to-end Deep pipeline, vault integration,
new Claude runtime behavior, and non-Darwin platforms. The original trial did
not exercise a downloaded release; the follow-up below records that separately.

References: [Codex configuration](https://learn.chatgpt.com/docs/config-file/config-reference)
defines role config files and trusted project configuration;
[Claude manifest validation](https://code.claude.com/docs/en/plugins-reference#validate-the-manifest)
documents the independent native validation used here.

## Published v1.2.0 follow-up (2026-09-30)

The user reported that AgentForge had been updated on GitHub. Release v1.2.0
is commit `2d32dc3aca76dc08344d62f0725f69c0ed356e73`, published at
`2026-09-30T01:20:04Z`. It contains the original integration and lifecycle
hardening commit `10265934edf3c94b334f710fd8e52e4f2a795175`.
The downloaded Darwin arm64 binary SHA-256 is
`67107b2a96892a1a3429010bbb8475d61c4100e1ac01783367e23aef402c2d54`,
matching published `SHA256SUMS` and the release API asset digest.

The wrapper pin is explicitly updated to v1.2.0 with all three platform hashes.
Regeneration moves the four bundled definitions into `agents/debate/`, with
unchanged role contents. Debate is bumped to 0.5.1 to invalidate native caches.
The original unreleased trial above remains evidence for its exact input.
The released-binary follow-up uses committed source/output
`b3faa19ca9dbd339d5626e99cda63d46926cace7` and fresh native plugin caches.
Release evidence and command logs are under `/tmp/jun-444-release/`.

```sh
env -u AGENTFORGE_BIN -u AGENTFORGE_PROJECT \
  scripts/agentforge.sh compile MARKETPLACE.yaml --out marketplaces
env -u AGENTFORGE_BIN -u AGENTFORGE_PROJECT \
  scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native
```

These commands pass locally with the downloaded release, clearing the compiler
schema blocker. Hosted CI has not run for these unpushed commits. This work did
not publish the AgentForge release and does not authorize a branch push.

### Released lifecycle matrix

```sh
AGENTFORGE_BIN=/tmp/jun-444-release/bin/agentforge-1.2.0-darwin-arm64 \
SOURCE_REPO="$PWD" \
SOURCE_COMMIT=b3faa19ca9dbd339d5626e99cda63d46926cace7 \
BASE_MARKETPLACE="$PWD/marketplaces/codex" \
CODEX_BIN=/opt/homebrew/bin/codex \
RUN_ROOT=/tmp/jun-444-release/lifecycle-b3faa19c \
  bash /tmp/jun-444-release/run-lifecycle.sh
```

Both scopes passed setup, repeat no-op (identical snapshots), check, content
update 0.5.1 → 0.5.2, rename/deletion at 0.6.0, edited-file/registration conflict
preservation, and receipt-only removal after native plugin removal. Missing
checks and edited check/update refusals returned 1 as expected; successful
operations and partial conflict-preserving removal returned 0. Final removal
and repeat removal left no owned definitions, registrations, or receipt.
Unrelated config, trust, agent files, and marker hashes were preserved.

Exact commands, stdout, stderr, exits, cache/source hashes and final snapshots
are in `/tmp/jun-444-release/lifecycle-b3faa19c/evidence/`; `summary.txt` records
all phases. Lifecycle processes use `/private/tmp` and a system-only PATH with
the absolute binary above, without Bun or an AgentForge checkout. The fixture
authoring clone is separate from that consumer boundary. Parent review also
confirmed the final scope configs retain only unrelated settings and trust.

The lifecycle matrix reached PASS before its shell cleanup trap failed because
`/usr/bin/unlink` is absent on this host. The trap was corrected to `/bin/rm -f`
for its one known disposable auth symlink. The link was removed separately;
`parent-cleanup-verification.json` confirms its absence and only unrelated agent
files remain in both scopes. This harness cleanup failure did not change any
lifecycle result or touch the normal authentication file.

Release follow-up checks: privacy gate self-test passed six checks; Introspect
behavior tests passed two tests; history privacy scan passed 410 commits at
`b3faa19c`. Logs are `privacy-self-test.log`, `introspect-tests.log`, and
`privacy-scan.log` under the release evidence root. Source and output review
confirmed only version metadata and the four byte-identical role moves changed.
Current consumer documentation now names v1.2.0; historical unreleased evidence
retains its original version and limitations.

### Released runtime follow-up

The native user-scope cache for Debate 0.5.1 is byte-identical to the committed
plugin (`/tmp/jun-444-release/runtime/user/cache-equality.json`). Explicit setup
activation reads the installed setup skill; install and check return 0 with
four roles and six current paths. A separate fresh read-only session reads the
installed Debate skill, checks registration, and dispatches exact
`agent_type: debate:synthesizer`. Child session
`01a0f2ab-24d7-7b43-bd6b-3488b7e9d841` records `agent_role` as
`debate:synthesizer` and `turn_context` model `gpt-5.6-terra`, effort `high`.
It returns the supplied fixture's Room A verdict, evidence, trade-offs,
conditions, and confidence breakdown. The parent independently checked these
metadata fields. This does not establish tool-policy enforcement.

Saved user evidence is under `/tmp/jun-444-release/runtime/user/`:
`setup.events.jsonl`, `dispatch.events.jsonl`, paired `.command.json`,
`.prompt.txt`, `.stderr`, `.last.txt`, and `.exit` files. Child metadata lives
in that isolated Codex home's `sessions/2026/09/30/` directory. The runner
`/tmp/jun-444-release/runtime/run_probe.py` records the exact command and
isolated environment, with the released binary's absolute path and no Bun.
The historical Markdown-procedure and same-agent follow-up probes above were
not rerun with the release; their results remain scoped to the unreleased trial.

### Follow-up cleanup targeting incident

The first released runtime user-cleanup attempt omitted `CODEX_HOME` from
three direct AgentForge invocations: `preview-codex-agent-remove debate --scope
user`, `remove-codex-agent debate --scope user`, and repeat removal. They
therefore targeted the normal Codex home. Native plugin removal itself had the
correct isolated environment. Work stopped when the wrong target was noticed;
this attempt is invalid isolation evidence and is not counted as fixture cleanup.

The saved `user/cleanup-preview.stdout` contains only `ready: remove`, with no
actions; removal logs print the normal home, both exit 0. Read-only inspection
found no normal Debate receipt or lifecycle lock. The normal config target's
mtime and ctime are `2026-09-29T17:14:38Z`, before the erroneous removal log at
`2026-09-30T14:16:38Z`. Exact release source inspection shows a missing receipt
produces an empty ready plan and the materializer returns before writing;
the CLI prints its removal success text even for this no-op. These observations
support that these commands made no lifecycle-managed writes in the normal
Codex home; a pre-operation byte snapshot was not taken.
No reconstruction or writes to normal configuration were attempted. Evidence:
`runtime/evidence/normal-home-incident-stat.json` and
`normal-home-incident-timestamps.json`, plus the original cleanup logs.
Remaining mutations require an explicit isolated `CODEX_HOME` guard.

The released project-scope cache also matches committed output
(`runtime/project/cache-equality.json`). Automatic approval review initially
rejected its `danger-full-access` setup control because of unrestricted
filesystem access. The user explicitly approved that one disposable setup
session before retry. It then read the installed setup skill and installed and
checked four roles/six paths successfully. This is an approved write-access
control, not evidence that ordinary `workspace-write` can mutate project
`.codex` (the earlier denial remains applicable).

A fresh project `read-only` dispatch checked registration and selected
`debate:synthesizer`. Child `01a0f2b0-6ea7-7da0-a449-b3225986690b` records that
exact role with `turn_context` model `gpt-5.6-terra` and effort `high`, confirmed
independently by the parent. It returned Room A with the required reasoning,
evidence, trade-offs, conditions, and confidence breakdown. Project command,
prompt, event, result, and exit files mirror the user layout under
`/tmp/jun-444-release/runtime/project/`. Setup and dispatch each exited 0.

Initial released user probes also exposed missing authentication (401 before
setup) and a mistaken project-scope selection (EPERM at project `.codex`).
Neither is accepted as user setup. Their original isolated rollouts are saved
as `runtime/evidence/user-setup-auth-401.rollout.jsonl` and
`user-setup-rejected-wrong-scope.rollout.jsonl`. The successful user retry used
an explicit user-only prompt and an unread temporary authentication symlink.
The symlink points to existing credentials; credentials were not copied into
the fixture or recorded in evidence.

Final released runtime cleanup succeeded after native plugin removal in both
scopes. `cleanup-isolated.*` records explicit guarded `CODEX_HOME` and project
root arguments; each `cleanup-isolated.json` confirms receipt, definitions,
and registrations absent. Both auth symlinks were removed without reading
referents (`runtime/evidence/auth-links-cleanup.txt`). Parent verification also
confirms plugin cache removal and auth-link absence in
`runtime/evidence/parent-final-cleanup.json`. The summary and copied parent/child
rollouts are in `runtime/evidence/`; these remain local, disposable trace paths.

The v1.2.0 follow-up clears the former compiler-pin blocker locally. The original
unreleased-build acceptance and this narrower release follow-up are separate;
this is not a broad public-release or desktop acceptance claim. Hosted CI and
remote review remain pending a user-authorized jdh-agents branch push. No push
or AgentForge publication was performed by this work.
