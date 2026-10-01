# Librarian registered Codex agent acceptance

Date: 2026-10-01. This is the Librarian step after Linear and Craft. No branch
push, release, normal-vault mutation, message, or tracker mutation was
authorized by this migration.

## Inputs and pre-edit boundary

`AGENTS.md`, `CLAUDE.md`, the dual-agent and AgentForge compatibility guides,
Debate/Linear/Craft registration workflows and acceptance records, Librarian's
package, four agent bodies, runtime guidance, and dispatching skills were read
before editing. The repository was at Craft acceptance commit `ddea1316`;
`main` pointed at the equivalent-tree Forgejo merge `db9f221c`. The compiler
pin remained released AgentForge 1.2.0. The available tracker context showed
JUN-444 In Review; no separate Librarian migration ticket was established, so
no tracker status was changed. Current NDR heads `6x3v6p` and `kpefq4` were
resolved before the source changes.

The count was confirmed from `plugins/librarian/agents/*.md`: exactly four
roles. `vault-reader` synthesizes vault notes and is read-only by procedure;
`vault-inspector` reports structural findings without edits; `note-editor`
makes an approved bounded note change; `vault-curator` conducts an interactive
inspect/approve/fix/reinspect cleanup and retains a same-agent handle. The 17
direct dispatching skills are `base-add`, `catalog-evaluate`, `catalog-recheck`,
`event-capture`, `experiment-review`, `experiment-start`, `meeting-followup`,
`meeting-notes`, `meeting-restructure`, `note-capture`, `note-cleanup`, `term`,
`vault-inspect`, `wiki-create`, `wiki-graduate`, `wiki-query`, and
`wiki-refresh`. The Obsidian CLI is the portable read/write route; several
procedures also name unavailable `mcp__obsidian-mcp__*` tools. Some workflows
consult vault rules, templates, Bases and `.claude` configuration; plugin
references are a separate installed resource. External web/source retrieval
appears in wiki/catalog workflows and was not accepted here. None of these
paths grants an external write merely by invoking a skill.

Final package-wide review also found `note-suggester`, which reads the vault
without dispatching an agent. Its Codex path now verifies the actual vault
destination and explicitly selects that vault for searches; if verification
fails it reports the duplicate check as unverified. The 17-role-caller count
does not include this separate skill.

The bounded synthetic fixture was specified **before** source editing in
`/tmp/librarian-preedit-fixture.md`, then materialized by
`/tmp/librarian-fixture-20261001.py` at
`/private/tmp/librarian-codex-20261001/synthetic-vault`. Its 21 initial files
include wiki frontmatter and links, a source note, an unresolved link, an
orphan, a concept template, synthetic `.claude` rules, a Base, a meeting note,
an experiment and two daily check-ins, plus unrelated content. Before hashes
are in `fixture-before-hashes.json` beside the vault. The fixture covers each
role, `wiki-query`, `wiki-create`, `note-cleanup`, `vault-inspect`, and the
reader/editor `experiment-review` handoff. It contains no copied private note.

## Canonical source and generated publication

Librarian `0.20.0` became `0.21.0`; `plugins/librarian/PACKAGE.yaml` opts into
`codex-agent-bundle: true` and includes `RUNTIME.md`. Canonical agent bodies,
all 17 direct callers, `references/architecture.md`, README, and the two
cross-package guides were updated. The source keeps Claude's native routes.
For Codex it requires explicit setup, a fresh current check in the selected
user or project scope immediately before exact namespaced dispatch, and an
independently chosen installed Markdown/procedure fallback without
`agent_type`. Packaged `agents/*.md` files do not register Codex roles.

Codex roles inherit the parent model. Their declared efforts are `medium` for
bounded multi-note reader synthesis, `high` for curator merge/split judgment,
and `low` for mechanical editor changes and rule-bound inspection. These are
task-specific choices, not Claude-alias mappings. Claude `tools`, `model`,
`maxTurns`, `memory`, and skill permission fields were not translated into a
Codex sandbox or tool policy. The runtime mapping requires callers to derive
an absolute canonical installed plugin root from the active skill, pass actual
installed reference paths, and prove the configured vault's destination before
any dependent operation. Every Codex CLI call carries the verified vault name;
an Obsidian connector call must prove an equivalent explicit selection or stop.
Codex shared procedures use the verified `vault_root` even before dispatch,
while Claude keeps its configured vault paths. It never treats CWD or the
authoring checkout as an installed resource or vault locator.

`scripts/agentforge.sh compile MARKETPLACE.yaml --out marketplaces` produced
the root/package manifests, Claude copy and Codex copy. The Codex publication
contains four namespaced TOMLs, bundle index, and explicit setup skill under
`marketplaces/codex/plugins/librarian/`. Managed output was not hand-edited.
`scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces
--claude-native` returned `ok` for 239 Claude and 250 Codex managed files and
validated both Claude manifests; exact output is
`/tmp/librarian-check-output-20261001.txt`. The compiler warns that Claude
role policies are stripped and that some `${CLAUDE_PLUGIN_ROOT}` and Obsidian
MCP tokens remain in bodies. `PACKAGE.yaml` declares these losses, and Codex
callers/roles use the explicit installed-root and CLI route. The compiler's
generic inferred-procedure notice does not prove role registration; the
bundle, selected-scope receipt and fresh dispatch are separate evidence.

## Consumer installation and lifecycle

The pinned verified consumer binary was
`$REPO/.cache/agentforge/1.2.0/agentforge-darwin-arm64`
(`agentforge 1.2.0`, SHA-256
`67107b2a96892a1a3429010bbb8475d61c4100e1ac01783367e23aef402c2d54`).
Codex was `/opt/homebrew/Caskroom/codex/0.158.0/bin/codex` (`0.158.0`).
Consumer PATH was `/usr/bin:/bin:/usr/sbin:/sbin`, excluding Bun and any
AgentForge checkout. Every lifecycle invocation supplied and validated its
absolute isolated `CODEX_HOME`; project commands also validated and passed
the disposable trusted project root. No bare user-scope cleanup ran.

The lifecycle harness committed the compiled output in a **disposable** Git
fixture, `/private/tmp/librarian-lifecycle-20261001/source-final-005`, commit
`b5828e736ea4aba4a618345491b7424f9a0fe3bb`. The source and Codex
marketplace archives have SHA-256
`0946374a05a3ad412c2331c8bc520a3ac72c78cb3a3c28c1cb43c10cc4760200`
and `effc63b626d256e4309e36fad3a1f2879d9d3c6d62cb06a2e0315f4375ba5565`.
All 47 current compiled Librarian plugin files matched that committed fixture
byte-for-byte and by mode. Exact commands, environment, outputs, exits and
hashes are in `/private/tmp/librarian-lifecycle-20261001/run-005/evidence/`;
`acceptance-summary-run-005.md` beside that run reports 74 commands, `PASS`.

Native `codex plugin marketplace add` and `codex plugin add
librarian@jdh-agents` installed the committed marketplace into separate
isolated user and project homes. Both installed caches matched the 47 compiled
files by byte and mode; see
`/private/tmp/librarian-runtime-final-20261001/native-install-records.json`.
For both scopes, the lifecycle run covered missing registration, setup, repeat
no-op, drift check, content update, rename/deletion, edited-file conflict
refusal, plugin and marketplace removal, receipt cleanup, repeat cleanup and
unrelated-file preservation. Expected nonzero exits were the missing and
edited-file refusals. This direct harness does not establish skill activation,
model behavior or ordinary Codex sandbox acceptance.

## Pre-correction fresh sessions: activation, checks and dispatch

The traces in this section exercised the first 0.21.0 build. A final review
then tightened explicit vault selection in all roles/callers and guarded the
separate `note-suggester` search. These traces establish observed behavior of
that earlier build only; final-build role behavior remains pending a fresh
session rerun. The final build's current 47-file installed cache and direct
scope registration are separate results above and below.

Raw commands, JSONL events, exits and child rollouts live under
`/private/tmp/librarian-runtime-20261001/{user,project,fallback}/`; these are
local evidence, not committed notes. Runtime configs disabled apps and MCP.
The ordinary **outer** nested Codex launcher failed with
`sandbox-exec: sandbox_apply: Operation not permitted` before it read the
installed skill. An explicitly approved unrestricted **outer launcher** then
started fresh child sessions that still declared `workspace-write`. Its result
is not ordinary outer-sandbox acceptance.

For the final build, direct installed-helper `install` and `check` commands
ran in the ordinary outer sandbox for both isolated user and project scopes;
each returned zero and `current: 6 managed paths`, recorded at
`/private/tmp/librarian-runtime-final-20261001/direct-setup-records.json`.
Fresh ordinary nested Codex setup sessions in both scopes were attempted
afterward. Their process exits were zero because the model reported a block,
but every shell command was rejected *before execution* with
`sandbox-exec: sandbox_apply: Operation not permitted`; neither session read
the installed skill or ran its helper. Their traces are
`/private/tmp/librarian-runtime-final-20261001/{user,project}/setup-control.events.jsonl`.
The final-build outer launcher control requires separate approval and has not
yet run.

The user setup session explicitly read the installed
`$librarian:setup-codex-agents` skill and cache helper, verified the released
binary, ran `install user`, then `check user`: both operations succeeded; the
check reported six current managed paths. One wrapper exited nonzero after a
successful first install because it assigned zsh's read-only `status`
variable; the corrected no-op wrapper and check exited zero. The ordinary
project `workspace-write` setup also read the installed skill but failed
`EPERM` creating disposable `project/.codex`; it stopped. After separate
explicit approval, one unrestricted **child project-setup control** ran only
guarded `install project` and `check project` with isolated homes; both exited
zero and the check reported six current managed paths. This is not a pass for
ordinary project setup. The exact traces are `user/setup-control.events.jsonl`,
`project/setup-control.events.jsonl`, and
`project/setup-unrestricted-control.events.jsonl` under the runtime root.

Two initial user role sessions stopped before dispatch because their login
shell did not find the mock CLI. The isolated test home's `.zprofile` and
`.zshenv` were adjusted; the successful session verified that
`command -v obsidian-cli` was `/tmp/librarian-mock-bin/obsidian-cli` and that
the named mock vault resolved to the synthetic root before dependent reads.
No normal shell configuration was changed. The project sessions performed the
same CLI/destination validation. Every exact native spawn had a preceding
successful selected-scope `check` in its parent trace: three user checks for
reader, same-reader follow-up and inspector; three project checks for editor,
curator and same-curator follow-up; three more project checks for the
`experiment-review` reader, same-reader follow-up and editor. The first
project check included a `permission denied` diagnostic for an attempted
compiler invocation; the helper's selected-scope check still returned
`current: 6 managed paths` with exit zero. These are trace observations, not
an inference from TOML files.

| Role and trace | Exact dispatch and observed behavior | Child runtime metadata |
|---|---|---|
| `user/roles-read3.events.jsonl` | `librarian:vault-reader` ID `01a0f8f2-8deb-7cf3-8229-33c105d17fed` synthesized payment/invoice reconciliation from three synthetic cited paths; the follow-up resumed the **same** ID. | `agent_role=librarian:vault-reader`; `gpt-5.6-luna`, `medium` on both turns; `workspace-write`. |
| `user/roles-read3.events.jsonl` | `librarian:vault-inspector` ID `01a0f8f3-b8cc-7ad0-ba78-6b434b11046e` reported installed-rule findings, including an unresolved link, without editing. | Exact `agent_role`; `gpt-5.6-luna`, `low`; `workspace-write`. |
| `project/roles-write.events.jsonl` | `librarian:note-editor` ID `01a0f8f7-3b98-7a11-a10e-47c8cfbea1d0` created only the preapproved `Reference/Developer/Reconciliation.md`, with frontmatter/links/sources, and read it back. | Exact `agent_role`; `gpt-5.6-luna`, `low`; `workspace-write`. |
| `project/roles-write.events.jsonl` | `librarian:vault-curator` ID `01a0f8f8-9943-7723-8244-f33b4da26e01` inspected an orphan, resumed on the **same** ID after approval, appended only an approved link in `Accounting.md`, and reinspected Found 1 / Fixed 1 / Remaining 0. | Exact `agent_role`; `gpt-5.6-luna`, `high` on both turns; `workspace-write`. |
| `project/roles-experiment.events.jsonl` | `experiment-review` orchestrated reader ID `01a0f8ff-6c6e-7202-b448-218366107801`, same-ID follow-up across experiment and daily backlinks, then one-shot editor ID `01a0f900-c93e-7b23-a0a0-a1110e32351c` to append the approved inconclusive verdict. | Exact `agent_role` values; reader `gpt-5.6-luna`/`medium` twice, editor `gpt-5.6-luna`/`low`; `workspace-write`. |

All values above came from each child's `session_meta.agent_role` and
`turn_context` rather than requested settings. Backend routing beyond the
reported model, per-tool restrictions, and actual Claude policy enforcement
are unknown. Read-only roles behaved read-only in this fixture, but Codex did
not mechanically enforce a per-role read-only tool filter.

## Pre-correction fallback and vault effects

`fallback/fallback-procedure.events.jsonl` ended with exit zero. Its selected
user-scope check reported missing registration and there was no namespaced
spawn. The installed `wiki-query` and `vault-reader.md` were read; generic
child `01a0f904-2643-7223-8b85-7f9e8883237b` ran **without** `agent_type`
and synthesized the same three-note reconciliation. An inline
`vault-inspector` procedure separately identified installed rule `S-3` for
`[[Missing Concept]]`, with no inspector child. The first mock vault probe
used an unsupported argument shape and failed safely; the session recovered
with the correct named mock path. An attempted `git diff` preservation check
also ran outside a Git repository and is not preservation evidence; the
content-hash comparison below is the evidence. Fallback role registration,
runtime effort and generic-child role continuity are not claimed.

The real `obsidian-cli` could not resolve the named disposable vault:
`vault='Librarian Acceptance 20261001' vault info=path` returned
`Vault not found`. No real CLI write followed. No Obsidian MCP tool was
available. Subsequent role sessions used the constrained mock
`/tmp/librarian-mock-bin/obsidian-cli`, whose destination is hardcoded to the
synthetic vault; its operations are in
`/private/tmp/librarian-codex-20261001/mock-cli-operations.jsonl`. This tests
procedure behavior against synthetic data, **not** real Obsidian integration.
No normal-vault note was read because no content was specifically authorized
for a live probe. No private content, external service, tracker, or message
was used as a fixture source.

Comparing SHA-256 for all 21 original synthetic files after the role and
fallback sessions showed exactly two modified originals:
`Reference/Developer/Accounting.md` and
`Experiments/Synthetic Focus Trial.md`. One file was added:
`Reference/Developer/Reconciliation.md`. All other original files, including
the unrelated sentinel, remained byte-identical. The experiment verdict was
appended directly below its check-ins heading without a blank spacer; the
meaning and approved text match, but formatting polish was not demonstrated.
The earlier inspector's rendered heading counted eight issues while its table
had ten rows; that discrepancy is superseded by the final trace's consistent
10-issue heading and ten rows. No delete/merge branch or live
integration write was exercised.

## Final-build fresh runtime acceptance

The final compiled marketplace was archived from disposable fixture commit
`b5828e736ea4aba4a618345491b7424f9a0fe3bb` and native-installed into
fresh `/private/tmp/librarian-runtime-final-20261001/{user,project,fallback}`
homes. Its committed-marketplace archive SHA-256 is
`c4cb71be07c02da05bd36c4bb11e483a8d1862c9fd702090724640942495c7cf`.
`native-install-records.json` there reports three successful native plugin
installs and 47-file byte/mode equality in each cache. The final synthetic
vault was freshly made from the same 21-file fixture specification at
`/private/tmp/librarian-codex-final-20261001/synthetic-vault`, with before
hashes next to it. Its CLI mock rejects both an omitted and a wrong vault
selector (exit 1), while the named fixture selector succeeds (exit 0). All 52
logged mock operations used the exact fixture vault name. This is a mock
boundary, not evidence that the real CLI can target the disposable vault.

Ordinary outer nested Codex launches in both scopes again failed with
`sandbox-exec: sandbox_apply: Operation not permitted` before reading the
installed setup skill. Following explicit approval for the **final outer
launcher**, fresh child sessions ran at `workspace-write`, with apps and MCP
disabled. The user and project `setup-final-control.events.jsonl` traces under
the final runtime root explicitly read the installed setup skill, derived its
cache helper, verified the released binary, and returned exit 0 for install
and check; each check reported six current managed paths. User setup's first
wrapper exited 1 after successful install because it assigned zsh's read-only
`status` variable; corrected install and check were 0. Project setup was a
warm repeat after ordinary direct-helper registration had created the
disposable `.codex`; it does not overturn the earlier cold child `EPERM`.
The direct installed-helper commands and their validated absolute
`CODEX_HOME`/project roots are in `direct-setup-records.json`.

| Final trace | Dispatch and behavior | Observed child metadata |
|---|---|---|
| `user/roles-read-final.events.jsonl` | Three successful current user checks preceded exact reader ID `01a0f930-4d64-7093-af92-4368db80723b`, the same-ID follow-up, and exact inspector ID `01a0f931-8636-7350-b0d0-589f2e894883`. The reader cited the three payment/invoice/source fixtures and noted gaps; the inspector reported installed S-1/S-3/S-4 findings, including `[[Missing Concept]]`. All 21 fixture files were unchanged afterward. | `session_meta.agent_role` was respectively `librarian:vault-reader` and `librarian:vault-inspector`; `turn_context` reported `gpt-5.6-luna` with `medium` twice and `low` once, all `workspace-write`. |
| `project/roles-write-final.events.jsonl` | Three successful current project checks preceded exact editor ID `01a0f933-e87e-7473-a4a0-d464eb21439e`, exact curator ID `01a0f934-ee75-7180-9981-d6801f1b7be2`, and same-ID curator follow-up. The editor created only approved `Reconciliation.md`; curator appended only the approved link to `Accounting.md`, reinspected and reported Found 1 / Fixed 1 / Remaining 0. | Exact `librarian:note-editor` and `librarian:vault-curator` roles; `gpt-5.6-luna` with `low` once and `high` twice; `workspace-write`. |
| `project/roles-experiment-final.events.jsonl` | Three more successful current project checks preceded reader ID `01a0f938-4ef0-7cf3-bcba-f396649505b3`, same-ID follow-up over two daily check-ins, then one-shot editor ID `01a0f939-7936-76a2-85d2-a95919bbc8e3` for the approved inconclusive verdict. | Exact reader/editor roles; `gpt-5.6-luna` with `medium` twice and `low` once; `workspace-write`. |

The parent event streams contain each exact `agent_type` spawn without a
per-dispatch model, effort, tool or permission override. Child rollouts under
each final isolated home contain the matching `session_meta.agent_role` and
applied model/effort. The backend's routing beyond that metadata is unknown.
The first reader pre-dispatch check had a malformed shell invocation and no
spawn; a corrected current check succeeded before dispatch. No other failed
check was treated as permission to spawn. The role-specific read-only behavior
was observed; Codex did not mechanically enforce a read-only tool filter.

`fallback/fallback-procedure-final.events.jsonl` in the final runtime home
reported a missing user-scope registration (corrected check exit 1, six
missing paths) and made no namespaced spawn. Generic child
`01a0f93c-5829-7cd0-b791-2ba215c74c7b` used the **installed**
`vault-reader.md` body without `agent_type`, cited the three permitted fixture
notes, and returned the payment-identifier answer. A separate inline
inspection used installed S-3 to find the unresolved `[[Missing Concept]]`;
there was no inspector child. An initial wrapper again used zsh's read-only
`status` variable, then the corrected missing check returned exit 1. This
fallback did not register a role or establish generic-child role settings.

Final before/after SHA-256 comparison of the 21 original fixture files found
only `Reference/Developer/Accounting.md` and
`Experiments/Synthetic Focus Trial.md` changed; one approved
`Reference/Developer/Reconciliation.md` file was added. Every other original,
including the unrelated sentinel and daily notes, remained byte-identical.
The experiment verdict still lacks a blank spacer after the check-ins heading;
this formatting edge is unproven, though the approved text is present. No
normal vault, live Obsidian write, connector, external source, tracker or
message was involved.

## Gates, Git and remaining limits

The normal compiler/native validation gate passed, as did
`scripts/privacy-scan.sh`, the six-check privacy-gate self-test, and 104
repository Python tests (97 attention-workflow, two introspect-report, five
Langfuse-hook). The Python tests used `XDG_CACHE_HOME=/tmp/librarian-uv-cache`
after the ordinary `~/.cache/uv` sandbox path was denied. `git diff --check`
passed. Source and generated diffs were reviewed for Librarian scope; raw
runtime traces and synthetic fixture stay outside the repository. Local JJ
change `rqkvqnmu` is based on `main` merge `db9f221c` and carries canonical
source, generated output, guides and this record together on bookmark
`librarian-codex-agents`. Nothing has been pushed or published.

The material remaining blocker is real Obsidian acceptance: the integration
did not resolve the disposable vault, so live read/write destination safety
could not be established. Cold project setup under child `workspace-write`
was denied (`EPERM`) before the disposable `.codex` existed; the separately
approved unrestricted control and the final warm repeat do not turn that cold
case into ordinary sandbox acceptance.
Untested surfaces include actual Obsidian MCP/CLI note writes, full wiki and
catalog external-source flows, every one of the 17 callers beyond the
representative workflows, Claude runtime parity, and mechanical enforcement
of read-only procedures. Any unobserved setting is unknown, not inferred.
