# Dual-agent operating model

## Status

Codex support is limited to the pilot plugins `commit`, `craft`, `linear`, and
`spec-flow`. Claude Code remains the default surface for every other plugin.
The repository publishes both runtimes from one source: `marketplaces/claude/`
is what a Claude install resolves (remotely, via the root manifest) and
`marketplaces/codex/` is what a Codex install resolves from a local clone.

## Ownership model

- `plugins/<name>/skills/`, references, scripts, and other workflow content are
  canonical shared bodies. Do not fork substantive instructions by runtime.
- `marketplaces/claude/plugins/<name>/.claude-plugin/plugin.json` is the Claude
  manifest, and `marketplaces/codex/plugins/<name>/.codex-plugin/plugin.json` is
  the Codex one. Both are compiler output; neither is hand-edited, and neither
  lives beside the canonical source any more.
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

- Claude publication root: `marketplaces/claude/`, registry at
  `.claude-plugin/marketplace.json`
- Codex publication root: `marketplaces/codex/`, registry at
  `.agents/plugins/marketplace.json`
- Shared canonical source: `plugins/<name>/`

Each publication is a separate, self-contained marketplace root, so the two
runtimes no longer share a directory and cannot resolve each other's files.
That separation replaces the earlier colocation, under which pointing Codex at
the repository root made it install canonical Claude sources. Codex validation
checks its catalog entries, manifest metadata, strict semantic versions, path
containment, Claude/Codex name and version parity, and skill YAML frontmatter.

## Install

Point each runtime at its own publication root, never at the repository.

Claude Code:

```bash
/plugin marketplace add /path/to/jdh-agents/marketplaces/claude
```

Codex local development marketplace:

```bash
codex plugin marketplace add /path/to/jdh-agents/marketplaces/codex
codex plugin add commit@jdh-agents
codex plugin add craft@jdh-agents
codex plugin add linear@jdh-agents
codex plugin add spec-flow@jdh-agents
```

Open a new task after installation or update so Codex reloads plugin skills.

## Change workflow

1. Edit the shared skill body or reference once.
2. Update only the runtime manifest or adapter whose contract changed.
3. Keep Claude and Codex manifest names and versions equal.
4. Run `scripts/agentforge.sh compile MARKETPLACE.yaml --out marketplaces`
   when manifest metadata changes.
5. Run `scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces
   --claude-native` and `scripts/privacy-scan.sh`.
6. Test modified pilots in a fresh Codex task and the corresponding Claude
   workflow before release.

## Validation and CI

`scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces
--claude-native` is the merge gate:

1. Output drift across both publications: missing, extra, changed, permissions.
2. Managed-output content and managed `.json` parsing.
3. Manifest parity and declared plugin path resolution.
4. Skill frontmatter against each target's schema.
5. `claude plugin validate --strict` over the Claude publication.

GitHub Actions runs that command plus `scripts/privacy-scan.sh`. Codex
exposes no non-interactive validator, so the Codex publication is gated by the
compiler's own checks; CI does not depend on a user-installed Codex skill.

## Pilot acceptance

The four pilots passed fresh-task smoke tests:

- `commit`: detected repository conventions and reviewed a message without
  committing.
- `craft`: explicit `zoom-out` invocation mapped the marketplace tooling.
- `linear`: `linear:doctor` used the connected Codex Linear operations and
  resolved the workspace team dynamically; workspace differences remained
  warnings.
- `spec-flow`: routed an existing file-hosted contract without mutation.

Additional fresh-task Codex acceptance:

- `teach` (0.11.4, 2026-09-16): explicit invocation loaded the installed
  `jdh-agents` copy, read the exact Learning Style note and hidden vault
  Location Decision Tree, disclosed that DEVONthink was unavailable, and
  created then re-read only `Mission.md`, `Resources.md`, and `Glossary.md`
  under the user-confirmed `Reference/Developer/Jujutsu Workspaces/` path.
  The runtime trial caught and fixed two real CLI hazards first: exact reads
  require `path=`, and `obsidian-cli create --help` performs a create rather
  than showing help.

Fresh Claude regression evidence:

- `teach` (0.11.5, 2026-09-16): a fresh Claude Code process loaded the
  generated plugin with `--plugin-dir`, invoked `/teach:teach`, read all 661
  lines of the canonical vault guidance before proposing a path, and waited
  for confirmation of `Reference/Developer/Jujutsu Templates/`. It created
  five Markdown notes inside that workspace; `Mission.md` correctly omitted
  both an unverified `up` link and the folder-redundant `context/developer`
  tag. The run made no repository change and used no destructive command or
  subcommand `--help`. Its scratch jj validation left one per-repository config
  directory under `~/.config/jj/repos/`; that non-vault side effect remains an
  explicit cleanup item rather than being silently deleted.

Expand Codex support plugin by plugin. A plugin joins the Codex catalog only
after its manifest validates, platform-specific primitives have native
mappings, and a fresh-task smoke test passes.
