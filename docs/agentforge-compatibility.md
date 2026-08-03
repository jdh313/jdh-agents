# AgentForge compatibility

`MARKETPLACE.yaml` and each plugin's `PACKAGE.yaml` are the authoritative
AgentForge collection definitions. Native Claude and Codex manifests remain
committed at the repository paths consumed by both runtimes, but they are now
generated outputs rather than independently maintained metadata.

The compiler baseline for this enrollment is AgentForge commit `0ebebbb`
(`agentforge` 0.0.1).

## Acceptance-suite ownership

cc-marketplace owns full-corpus acceptance and drift detection against its real
canonical `MARKETPLACE.yaml`. AgentForge retains its focused five-package
compiler fixture as compiler-level coverage; that fixture is not a substitute
for validating all fifteen packages in this repository.

The cc-marketplace suite runs the pinned compiler twice in separate temporary
output roots and compares paths, file types, bytes, and normalized permissions.
It then runs AgentForge's read-only `check` command and exercises drift in five
dimensions: changed content, a missing file, an extra file, changed registry
metadata, and changed permissions. Every drift case fingerprints the generated
tree before and after the check to prove that checking does not repair or
rewrite output.

The merge gate also applies the runtime-native checks that are available:

- `claude plugin validate --strict` validates the complete generated Claude
  publication.
- `uv run marketplace validate --format codex` validates the generated Codex
  marketplace and only its five declared packages. It checks local source
  resolution, manifest identity and semantic versions, required skill metadata,
  explicit-only sidecars, and exact agreement between declared and materialized
  package directories. Codex currently provides marketplace management but no
  non-interactive `plugin validate` command, so this is cc-marketplace's native
  Codex validation boundary.

Full generated publication roots are disposable and live outside the source
repository. `uv run marketplace sync` projects only their native manifest files
into the source tree: two root registries, fifteen Claude package manifests,
and five Codex package manifests. The acceptance suite itself never updates
checked-in output.

AgentForge owns explicit-only skill translation. When a canonical Claude skill
declares `disable-model-invocation: true`, the Codex projection generates a
skill-local `agents/openai.yaml` containing
`policy.allow_implicit_invocation: false`. Supplied sidecars remain subject to
AgentForge's normal collision policy and cannot silently replace generated
policy. cc-marketplace owns verifying those compiler results across the real
15-package corpus and validating the five declared Codex packages; it does not
duplicate the translation in repository tooling.

## Target enrollment

- Claude enrolls all fifteen packages with `all-compatible`.
- Codex enrolls the accepted pilots only: `commit`, `craft`, `feedback`,
  `librarian`, `linear`, and `spec-flow`.
- The other nine packages do not declare Codex support. They must complete a
  native mapping and fresh-runtime acceptance before joining that publication.

`feedback` carries a **native mapping but not yet fresh-runtime acceptance**.
Its Codex projection compiles, validates, and is drift-clean, and its report
format was rewritten to name surfaces by intent rather than by Claude's surface
set. The Codex smoke test in JUN-342 has not been run — no Codex runtime was
available — so under `ndr:v0a3bm` this package is enrolled on the mapping half
of the gate only. Treat its Codex support as unverified until that test runs.

Target omission is an explicit compatibility decision. AgentForge must not emit
an empty or untested package merely because its definition validates.

## Source and payload handling

- Skill `SKILL.md` files are canonical skill artifacts. Nested `scripts/`,
  `references/`, and `assets/` are projected by the skill renderer.
- Package agents, commands, and hooks are declared as their native artifact
  types. Claude preserves those artifacts directly.
- Package-root references, `craft/CONTEXT.md`, and arbitrary skill sidecars are
  supplied payloads.
- The commit guard and Langfuse hook companions are Claude-only payloads.
- Native plugin manifests are represented by canonical defaults and target
  overlays, never copied as payloads.
- Plugin READMEs stay in the source repository but are intentionally excluded
  from runtime payloads.
- Symbolic links are not supported as package payload sources. The enrolled
  inventory contains none.

AgentForge derives executable intent from source mode. The commit guard and
Langfuse tripwire are the only executable payloads and compile as `0755`; all
other compiled files normalize to `0644`.

## Claude compatibility

All fifteen packages compile for Claude and pass `claude plugin validate
--strict`. The canonical marketplace omits three legacy generated metadata
fields—`metadata.homepage`, `metadata.totalPlugins`, and
`metadata.lastUpdated`—because current strict validation reports them as
unknown. Supported `metadata.description` and `metadata.version` remain.

Skill names are leaf identifiers in canonical source. Claude applies the plugin
namespace at runtime, so `skills/today` declares `name: today` and is invoked as
`coach:today` after installation.

## Codex compatibility

The five-pilot publication compiles and passes cc-marketplace's Codex-native
validator. Compilation diagnostics are reviewed limitations, not parity claims:

- `commit`: `allowed-tools` is stripped. The PreToolUse hook is translated into
  Codex's handler schema and the executable guard ships with it at `0755`;
  `${CLAUDE_PLUGIN_ROOT}` becomes the native `${PLUGIN_ROOT}`. Codex skips
  plugin-bundled hooks until the user reviews and trusts the definition, so the
  guard is present but inert until then.
- `craft`: Claude-only invocation and tool-policy fields are stripped where
  reported.
- `feedback`: two fields are stripped, and neither is a declarable loss —
  the `session` skill's `argument-hint` and `allowed-tools`, and the `triage`
  skill's `argument-hint`. Disposition: **accepted, no behavioral gap worth
  gating.** The `allowed-tools` entries (`Bash(git rev-parse *)`, `Bash(date *)`)
  are a permission-prompt convenience, not a capability — a Codex tester is
  prompted where a Claude tester is not. The `argument-hint` values document the
  optional `--save` flag and triage's path argument; both are restated in each
  skill's body, so the guidance survives even though the autocomplete hint does
  not. No `targets.codex.losses` entries: the package declares zero Claude-only
  constructs, which is the whole reason it was picked as the M2 opener.
- `librarian`: Claude-only policy fields are stripped. Four Claude agents
  become reusable Codex role procedures without Claude model, turn, or tool
  enforcement.
- `linear`: the doctor skill's `allowed-tools` field is stripped.
- `spec-flow`: the verifier becomes a reusable role procedure. The `spec-flow`
  dispatcher is a user-invocable skill, so its `disable-model-invocation` flag
  is translated rather than lost. Claude argument hints and tool restrictions
  are retained as source evidence but are not enforced by Codex.

Constructs that would otherwise be lost with nothing reported must be declared
in canonical YAML under `targets.codex.losses`, and compilation fails
against the declaration when one is missing. Three constructs are gated today:
an agent `tools:` filter (`librarian`, `spec-flow`), an `mcp__*` tool reference
(`librarian`, `linear`, `spec-flow`), and a `$ARGUMENTS` body template variable
(`spec-flow`). A skill's own `allowed-tools` is not among them — it is stripped
with a warning, not a declared loss, so converting a command to a skill trades
a gated construct for a reported one. A construct that is translated rather
than lost — `disable-model-invocation`, or a hook
handler's `args` folded into `command` — reports a warning instead; see the
JUN-341 companion for that narrowing.

Declaring a loss does not buy silence. Every declaration that matches a
detected construct emits a `declared-loss` note on each compile and check,
carrying the author's statement of what a Codex user does not get.

Schema validation and deterministic compilation establish collection integrity,
not behavioral equivalence.

## Reproducing the gate

Use a checkout at the recorded compiler baseline:

```bash
export AGENTFORGE_PROJECT=/path/to/agentforge-at-0ebebbb
uv run marketplace sync
uv run marketplace check
uv run pytest -q

generated_root=/tmp/cc-marketplace-agentforge
bun run "$AGENTFORGE_PROJECT/src/cli.ts" compile MARKETPLACE.yaml --out "$generated_root"
bun run "$AGENTFORGE_PROJECT/src/cli.ts" check \
  MARKETPLACE.yaml --out "$generated_root" --claude-native
uv run marketplace validate \
  --format codex \
  --manifest "$generated_root/codex/.agents/plugins/marketplace.json" \
  --plugins-root "$generated_root/codex/plugins"
```

CI checks out `jdh313/agentforge` at full commit
`0ebebbb8f0cf23f9223792a4b625ca302c9d655d`. Since that repository is private,
the workflow requires the `AGENTFORGE_DEPLOY_KEY` repository secret with read
access and fails closed when it is not configured. The runner toolchain pins
Bun `1.3.14` and Claude Code `2.1.216`, the versions used for the local
acceptance run.

Runtime references: [Claude plugin validation](https://code.claude.com/docs/en/plugin-marketplaces#validation-and-testing)
and [Codex plugin and marketplace structure](https://developers.openai.com/codex/plugins/build/).
