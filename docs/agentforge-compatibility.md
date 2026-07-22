# AgentForge compatibility

`MARKETPLACE.yaml` and each plugin's `PACKAGE.yaml` are the authoritative
AgentForge collection definitions. Native Claude and Codex manifests remain
committed at the repository paths consumed by both runtimes, but they are now
generated outputs rather than independently maintained metadata.

The compiler baseline for this enrollment is AgentForge commit `7568c45`
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
- Codex enrolls the accepted pilots only: `commit`, `craft`, `librarian`,
  `linear`, and `spec-flow`.
- The other ten packages do not declare Codex support. They must complete a
  native mapping and fresh-runtime acceptance before joining that publication.

Target omission is an explicit compatibility decision. AgentForge must not emit
an empty or untested package merely because its definition validates.

## Source and payload dispositions

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

- `commit`: `allowed-tools` is stripped. The Claude hook and executable guard
  are unsupported and absent from Codex output.
- `craft`: Claude-only invocation and tool-policy fields are stripped where
  reported.
- `librarian`: Claude-only policy fields are stripped. Four Claude agents
  become reusable Codex role procedures without Claude model, turn, or tool
  enforcement.
- `linear`: the doctor skill's `allowed-tools` field is stripped.
- `spec-flow`: the verifier becomes a reusable role procedure and the command
  becomes an explicit-invocation skill. Claude argument hints and tool
  restrictions are retained as source evidence but are not enforced by Codex.

Schema validation and deterministic compilation establish collection integrity,
not behavioral equivalence. The cutover does not change these reviewed
limitations or claim unsupported Codex hooks.

## Reproducing the gate

Use a checkout at the recorded compiler baseline:

```bash
export AGENTFORGE_PROJECT=/path/to/agentforge-at-7568c45
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
`7568c45df856a7e6447ab9f1491e826591018f1b`. Since that repository is private,
the workflow requires the `AGENTFORGE_DEPLOY_KEY` repository secret with read
access and fails closed when it is not configured. The runner toolchain pins
Bun `1.3.14` and Claude Code `2.1.216`, the versions used for the local
acceptance run.

Runtime references: [Claude plugin validation](https://code.claude.com/docs/en/plugin-marketplaces#validation-and-testing)
and [Codex plugin and marketplace structure](https://developers.openai.com/codex/plugins/build/).
