# JUN-444: installed Codex agent lifecycle acceptance

Date: 2026-09-29. Status: **unreleased local build; scoped local acceptance passed, CI blocked**.
[JUN-444](https://linear.app/junglelan/issue/JUN-444/jdh-agents-installed-codex-agent-lifecycle-acceptance)
remains incomplete while the normal CI compiler cannot validate the new source.
No public AgentForge release or branch push was performed.

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
real package remains 0.5.0. The shared script's invocation is reproducible from
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

## Verification and remaining gate

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

The independent normal merge-gate command remains:

```sh
env -u AGENTFORGE_BIN -u AGENTFORGE_PROJECT \
  scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native
```

It exits 1 under the unchanged public v1.1.0 pin:

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
`d873a4a4`. No branch was pushed and no public release was published.

Scratch traces and the build are local files under `/tmp`, not committed raw
session data; their retention is not guaranteed. Essential results, full input
hashes, commands, and trace identities are retained here. Unverified surfaces:
Codex desktop, skill-picker UI, full end-to-end Deep pipeline, vault integration,
new Claude runtime behavior, non-Darwin platforms, and downloaded public-release
acceptance. JUN-444's Linear status is unchanged while the remaining gate is
open.

References: [Codex configuration](https://learn.chatgpt.com/docs/config-file/config-reference)
defines role config files and trusted project configuration;
[Claude manifest validation](https://code.claude.com/docs/en/plugins-reference#validate-the-manifest)
documents the independent native validation used here.
