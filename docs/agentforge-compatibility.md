# AgentForge compatibility

`MARKETPLACE.yaml` and each plugin's `PACKAGE.yaml` are the canonical
AgentForge collection definitions. Native Claude and Codex manifests remain in
the repository during enrollment; SC-35 does not cut consumers over to compiled
output or remove those manifests.

The compiler baseline for this enrollment is AgentForge commit `75f9fea`
(`agentforge` 0.0.1).

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
- `craft`: `$ARGUMENTS` remains uninterpreted in `design-by-stories` and
  `interrogate-model`; Claude-only invocation and tool-policy fields are
  stripped where reported.
- `librarian`: `$N`/`$ARGUMENTS` interpolation is not implemented where
  reported; Claude-only policy fields are stripped. Four Claude agents become
  reusable Codex role procedures without Claude model, turn, or tool
  enforcement.
- `linear`: the doctor skill's `allowed-tools` field is stripped.
- `spec-flow`: the verifier becomes a reusable role procedure and the command
  becomes an explicit-invocation skill. Claude argument hints and tool
  restrictions are retained as source evidence but are not enforced by Codex.

Schema validation and deterministic compilation establish collection integrity,
not behavioral equivalence. Generated-output cutover requires fresh-runtime
smoke tests and explicit review of these limitations.
