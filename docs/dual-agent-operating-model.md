# Dual-agent operating model

## Status

Codex support is private and limited to the pilot plugins `commit`, `craft`,
`linear`, and `spec-flow`. Claude Code remains the default surface for every
other plugin. Public export policy is unchanged; exported pilot directories may
contain Codex manifests, but the public registry remains Claude-native.

## Ownership model

- `plugins/<name>/skills/`, references, scripts, and other workflow content are
  canonical shared bodies. Do not fork substantive instructions by runtime.
- `plugins/<name>/.claude-plugin/plugin.json` is the Claude manifest.
- `plugins/<name>/.codex-plugin/plugin.json` is the Codex manifest.
- Claude agents and commands remain native Claude surfaces. Codex uses shared
  procedures plus runtime subagents; files under `agents/` do not register
  named Codex agents.
- Small runtime mappings may live beside shared content, such as
  `plugins/craft/RUNTIME.md` or skill-local `agents/openai.yaml` policy files.
- Preserve behavioral parity, not identical structure or tool spelling.

## Runtime mappings

| Intent | Claude Code | Codex |
|---|---|---|
| Repository guidance | `CLAUDE.md` | Applicable `AGENTS.md`; non-conflicting `CLAUDE.md` facts are supporting documentation |
| Invoke a skill | `Skill(plugin:skill)` or slash command | Installed namespaced skill or its `SKILL.md` procedure |
| Independent role | Registered agent via Agent tool | Spawn a bounded runtime subagent with the shared role procedure |
| User adjudication | `AskUserQuestion` | Structured user input when available; otherwise one concise question |
| Workflow tracking | `TodoWrite` | Runtime plan/checklist tool |
| Linear data/actions | `mcp__linear-server__*` | Connected Linear app or MCP operation with equivalent schema |

Connected integrations own authentication and private data access. Skills own
workflow conventions. Never replace a missing connector with web search or
model memory.

## Marketplace layout

- Claude registry: `.claude-plugin/marketplace.json`
- Codex registry: `.agents/plugins/marketplace.json`
- Shared plugin roots: `plugins/<name>/`

Claude discovery reads only `.claude-plugin/plugin.json`, so colocated Codex
manifests cannot duplicate Claude registry entries. Codex validation checks its
four catalog entries, manifest metadata, strict semantic versions, path
containment, Claude/Codex name and version parity, and skill YAML frontmatter.

## Install

Claude Code:

```text
/plugin marketplace add jdh313/cc-marketplace
```

Codex local development marketplace:

```bash
codex plugin marketplace add /path/to/cc-marketplace
codex plugin add commit@cc-marketplace
codex plugin add craft@cc-marketplace
codex plugin add linear@cc-marketplace
codex plugin add spec-flow@cc-marketplace
```

Open a new task after installation or update so Codex reloads plugin skills.

## Change workflow

1. Edit the shared skill body or reference once.
2. Update only the runtime manifest or adapter whose contract changed.
3. Keep Claude and Codex manifest names and versions equal.
4. Run `uv run marketplace sync` when Claude manifest metadata changes.
5. Run `uv run marketplace check` and `uv run pytest -q`.
6. Validate a Codex-only failure with
   `uv run marketplace validate --format codex`.
7. Test modified pilots in a fresh Codex task and the corresponding Claude
   workflow before release.

## Validation and CI

`uv run marketplace check` is the merge gate:

1. Claude registry drift check.
2. Claude marketplace validation.
3. Codex marketplace, manifest, parity, and skill-frontmatter validation.
4. Plugin lint.

GitHub Actions runs that command plus `uv run pytest -q`. The repository owns
the Codex validator; CI does not depend on a user-installed Codex skill.

## Pilot acceptance

The four pilots passed fresh-task smoke tests:

- `commit`: detected repository conventions and reviewed a message without
  committing.
- `craft`: explicit `zoom-out` invocation mapped the marketplace tooling.
- `linear`: `linear:doctor` used the connected Codex Linear operations and
  resolved the workspace team dynamically; workspace differences remained
  warnings.
- `spec-flow`: routed an existing file-hosted contract without mutation.

Expand Codex support plugin by plugin. A plugin joins the Codex catalog only
after its manifest validates, platform-specific primitives have native
mappings, and a fresh-task smoke test passes.
