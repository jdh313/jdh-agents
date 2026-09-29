# JUN-444: installed Codex agent lifecycle acceptance

Status on 2026-09-29: **compiler input integrated; runtime acceptance pending**.

Forgejo `main` and `jun-443` now both resolve to
`a79a20057e008548ce9a6ae0c1a48f0c5818611e`. Its ancestry contains both copied-file
mode fixes and the rebased lifecycle work. The prior JUN-443 tip `086aa152`
has equivalent changed-path content and patch ID
`121b5680469af7bd03bbd87038e81539ab2e4521` to the new tip.

The detached build used Bun 1.4.2 and `bun run build`. The standalone executable
is `/tmp/jun-444-build-bwh9mT/bin/agentforge-a79a200-darwin-arm64`, SHA-256
`3b730dfea2c5c6b41f67c2b17949351a945a8c4e5d088135a50ae297a2532d82`.
It reports `1.1.0` from unchanged package metadata, but is an **unreleased local
build**, not the public v1.1.0 binary. All nine lifecycle commands listed below
are present in its executed help. The build passed 28 focused lifecycle tests,
typecheck, lint, and an `env -i PATH=/usr/bin:/bin` standalone help/version probe
outside the source checkout. Evidence is under
`/tmp/jun-444-build-bwh9mT/evidence/` (`provenance.txt`,
`rebase-comparison.txt`, `lifecycle-command-help.txt`, `focused-tests.txt`).

The earlier blocked preflight and independent plan below are retained as
historical evidence; they do not describe the now-integrated compiler input.

## Earlier blocked preflight

This record contains independent source planning and prerequisite evidence for
[JUN-444](https://linear.app/junglelan/issue/JUN-444/jdh-agents-installed-codex-agent-lifecycle-acceptance).
The required compiler status is **unreleased local build**. No qualifying
binary has been built, and this record makes no public-release acceptance claim.

## Compiler prerequisite

Fresh Forgejo ref inspection at 2026-09-29T17:18:35Z found:

| Input | Commit |
|---|---|
| `origin/main`, copied-file mode fixes | `31cd8df4c2126b83fc09a68691595bfdaad403d0` |
| `origin/jun-443`, lifecycle consumer work | `086aa152516571bb359fb3f29b24c543323e8fe4` |
| Common ancestor | `af325e0bdf272e2afda72d77f8f82a4755a3e8e0` |

Both directions of `git merge-base --is-ancestor` returned 1. Neither input
contains the other. No integrated revision was found among inspected remote
and local refs. The mode fixes are `cef06a8e49d25cfac440315dba0aa797f1cc246c`
(`fix(materializer): normalize copied output modes`) and `31cd8df4`
(`fix(check): expect normalized copied file modes`).

Reproduce from an AgentForge checkout whose `origin` is Forgejo:

```sh
git ls-remote origin 'refs/heads/*'
git merge-base --is-ancestor 086aa152516571bb359fb3f29b24c543323e8fe4 31cd8df4c2126b83fc09a68691595bfdaad403d0
git merge-base --is-ancestor 31cd8df4c2126b83fc09a68691595bfdaad403d0 086aa152516571bb359fb3f29b24c543323e8fe4
git merge-base 31cd8df4 086aa152
```

Full command evidence is saved locally at
`/tmp/jun-444-preflight-20260929/compiler-input.log`; this scratch file is not
a committed artifact and may expire. The essential hashes and results are
preserved above.

The next prerequisite is one committed integration containing JUN-443 and both
mode fixes, with upstream tests passing. Recheck ancestry or equivalent patch
content if integration rewrites commits. Neither branch alone qualifies.
The source-declared build command is `bun run build`; it has **not** been run
for acceptance. Integrated commit, binary path, binary SHA-256, build result,
and executed `--help` output are all **unavailable**.

Source inspection at `086aa152` identifies these expected commands, pending
confirmation from the integrated binary's help:

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

## Independent consumer source plan

Debate 0.4.1 is suitable: all four roles take their context in prompts;
advocate, fact-checker, and devil's advocate use web research, while synthesizer
uses only supplied evidence. Optional vault context and decision-record writes
must be excluded from the disposable acceptance fixture and disclosed as
unexercised. The synthesizer offers a deterministic instruction-behavior probe
without external resources; Deep-mode advocates provide the follow-up probe.

Planned changes, **not implemented** while compiler integration is blocked:

1. In `plugins/debate/PACKAGE.yaml`, bump 0.4.1 to 0.5.0 and add
   `codex-agent-bundle: true` under `targets.codex`. This opt-in schema is
   present at `086aa152`. Preserve the declared `agent-tools-filter` loss.
2. In `plugins/debate/skills/debate/SKILL.md`, replace the inferred
   “sonnet-equivalent”/“opus-equivalent” guidance with explicit Codex behavior.
   Require successful registration checking and runtime role availability
   before dispatch. The expected exact identities are `debate:advocate`,
   `debate:fact-checker`, `debate:devils-advocate`, and `debate:synthesizer`;
   confirm them against emitted definitions before using `agent_type`.
3. Direct explicit setup through generated `debate:setup-codex-agents` and
   open a fresh session after registration. Packaged `agents/*.md` alone never
   registers a role. Preserve the separate procedure path, embedding the
   installed Markdown instructions in a bounded generic child. Deep mode must
   record agent IDs and use the runtime's actual follow-up primitive; if a
   fresh child is necessary, disclose the fallback and pass prior output.
4. Choose Codex model/effort only after inspecting available runtime metadata.
   Claude aliases provide no model mapping. A target model can be authored in
   agent frontmatter as `targets: { codex: { model: <verified-model> } }`.
   No model is selected yet. Medium effort for research/verification and high
   for adversarial synthesis are candidates based on work complexity, not
   acceptance results. Record applied values from child metadata or `unknown`.
5. Update the Debate README, operating-model mapping, compatibility/loss rows,
   and this record; compile managed output once with the integrated binary.
   Commit source and generated output together. Keep the public wrapper pin
   at v1.1.0 pending a separately reviewed release/pin change.

Policy grounding: AgentForge's `ndr:bqyqfd` resolves in its own ledger (it is
absent from this repository's ledger). Claude `tools`, `disallowedTools`, and
`permissionMode` must not become Codex sandbox policy. This repository's
`ndr:6x3v6p` requires behavioral boundaries in prose, and `ndr:kpefq4` favors
shared portable instructions. Turn limits and Claude model aliases must also
remain visible as unsupported or separately configured behavior.

## Pending acceptance matrix

Run every lifecycle row for **both** isolated user and trusted project scope.
Install committed compiled marketplace output through native Codex plugin
commands. Use an absolute path to the hashed unreleased binary; the consumer
environment must have neither Bun nor an AgentForge checkout. Keep the user's
normal Codex configuration and plugin cache outside the fixture.

| Probe | Required evidence | Current result |
|---|---|---|
| Setup and repeat | Missing registration, successful setup, repeat no-op | Not run |
| Drift check | Clean check and exact registered definitions | Not run |
| Update | Updated owned bytes and receipt; unrelated markers unchanged | Not run |
| Rename/deletion | Old owned role removed and new role registered | Not run |
| Edited-file conflict | Edited definition/config preserved; mutation refused | Not run |
| Removal | Native plugin removed first; receipt-based cleanup succeeds without bundle; repeat no-op | Not run |
| Fresh setup session | Explicit installed setup-skill activation trace | Not run |
| Fresh role session | Exact `agent_type`, instruction behavior, applied model/effort metadata | Not run |
| Deep follow-up | Same advocate ID across rounds, or disclosed fallback | Not run |
| Procedure path | Separate installed Markdown procedure run | Not run |

Save exact commands, exit codes, stdout/stderr, before/after hashes, native
cache version/path, and sanitized session traces. Keep evidence for compiled
output, installed cache, skill activation, dispatch, runtime behavior, and Git
outcome distinct. Applied model/effort are currently **unknown**. CLI lifecycle
and desktop behavior are both **unverified**.

## Repository baseline verification

Baseline: jdh-agents `8e296b35`, Debate 0.4.1, Darwin arm64,
Codex CLI 0.158.0, Claude Code 2.1.284. Initial JJ working copy was clean.
Only this planning record is added; package source and compiled publications
are unchanged.

| Command | Observed result |
|---|---|
| `env -u AGENTFORGE_BIN -u AGENTFORGE_PROJECT scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native` | Exit 0 on existing output using pinned public v1.1.0 |
| `scripts/tests/test_privacy_gate.sh` | Exit 0, six checks passed |
| `scripts/privacy-scan.sh` | Exit 0, no leaks found |

Local logs are under `/tmp/jun-444-preflight-20260929/`: `pinned-check.log`,
`privacy-self-test.log`, and `privacy.log`. These baseline results do not
validate new bundle output. No local-binary compile/check was run. Once the
input exists, run compile/check with `AGENTFORGE_BIN` set to its absolute path,
then independently run the unchanged pinned gate and record its exact result.
If v1.1.0 rejects the opt-in schema or output, keep that as an outstanding CI
gate; propose a reviewed compiler release/pin update without publishing it.

JUN-444 remains incomplete; its Linear status is unchanged. No branch push or
public release is authorized. The blocker is compiler integration, followed by
the entire installed-runtime matrix above, not a failed runtime trial.
