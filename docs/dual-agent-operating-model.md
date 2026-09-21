# Dual-agent operating model

## Status

Enrollment and runtime acceptance are different things, and this document
tracks both. The authoritative enrollment is the `codex` publication in
`MARKETPLACE.yaml`: it runs `mode: all-compatible`, so every package that
declares a `targets.codex` block is compiled and published. That is fifteen
packages today, against eighteen for Claude. Seven of those fifteen — `commit`,
`craft`, `librarian`, `linear`, `spec-flow`, `teach`, and `workspaces` — have passed
fresh-task smoke tests (ndr:v0a3bm); the rest are compiled and enrolled with
runtime acceptance still outstanding. Claude Code remains the default
surface for every plugin, and the only surface for the three Claude-only
packages (`attention-workflow`, `langfuse`, `teardown`).
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
6. Test modified packages in a fresh Codex task and the corresponding Claude
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

## Runtime acceptance

Enrollment and acceptance are separate facts. Every package listed in the Codex
publication is enrolled; the ones below are the subset that has additionally
been exercised on a fresh Codex runtime. The results are dated records of what
was observed then, not standing guarantees, and a later version of the same
package inherits nothing from them.

Six packages have passed fresh-task smoke tests. `librarian` is recorded in
`agentforge/docs/librarian-agent-acceptance.md` and `teach` is recorded below;
the other four:

- `commit`: detected repository conventions and reviewed a message without
  committing.
- `craft`: explicit `zoom-out` invocation mapped the marketplace tooling.
- `linear`: `linear:doctor` used the connected Codex Linear operations and
  resolved the workspace team dynamically; workspace differences remained
  warnings.
- `spec-flow`: routed an existing file-hosted contract without mutation.

Those four were recorded without a version or date pin. They are kept as the
historical record of what was observed, and are not re-dated here; treat them
as evidence about the package as it stood then.

Additional fresh-task Codex acceptance:

- `teach` (0.11.4, 2026-09-16): explicit invocation loaded the installed
  `jdh-agents` copy, read the exact Learning Style note and hidden vault
  Location Decision Tree, disclosed that DEVONthink was unavailable, and
  created then re-read only `Mission.md`, `Resources.md`, and `Glossary.md`
  under the user-confirmed `Reference/Developer/Jujutsu Workspaces/` path.
  The runtime trial caught and fixed two real CLI hazards first: exact reads
  require `path=`, and `obsidian-cli create --help` performs a create rather
  than showing help.

- `teach` (0.11.5, 2026-09-18, codex-cli 0.154.0): a clean reinstall from
  `marketplaces/codex` produced a cache byte-identical to the Codex
  publication, carrying `skills/teach/agents/openai.yaml` with
  `policy.allow_implicit_invocation: false` and a body whose collaborator
  wording is capability-conditional — no named `@vault-reader` or
  `@note-editor`, and no Claude-specific Obsidian patch-tool instruction.
  Those are facts about the installed artifacts; the rest is observed
  behavior. A fresh neutral-directory session on `gpt-5.6-luna`, given a
  natural-language "Teach me…" prompt, taught from model knowledge alone: it
  did not load Teach, touch Obsidian, read vault guidance, or propose a
  workspace, so explicit-only invocation held. Under an explicit `$teach`
  invocation the same build read the exact Learning Style note and the
  complete vault location guidance, said truthfully that DEVONthink was
  unavailable and had not been searched, proposed a workspace, and stopped
  before writing; the proposed folder did not exist until the user confirmed
  it. After confirmation it wrote only under
  `Reference/Developer/Bloom Filters/` — `Mission.md`, `Resources.md`,
  `Glossary.md`, an empty `Records/`, and
  `lessons/0001-bloom-filter-membership.md` — created no global Sources note,
  wiki page, or unearned learning record, and re-read every file it wrote. A
  second fresh Codex session reconstructed that workspace from its own files
  and added only `lessons/0002-bloom-filter-saturation.md`, leaving mission,
  resources, glossary, and `Records/` unchanged. Collaborator steps ran
  through the direct `obsidian-cli` and edit route rather than a named agent
  — the fallback the capability-conditional wording specifies — and no
  unavailable collaborator was invented. An earlier natural-language trial
  inside the jdh-agents source worktree is excluded from this record: it
  discovered canonical Teach source on disk, so it measures the working
  directory rather than the invocation policy. The Codex tool boundary
  remains advisory. These observations record compliance in the sessions
  tested; they are not mechanical tool-filter enforcement, and one passing
  run is not a general guarantee.

- `workspaces` (0.1.1, 2026-09-21, codex-cli 0.155.1, jjx 0.4.0): a clean
  reinstall from the generated local Codex publication loaded the exact skill
  at `~/.codex/plugins/cache/jdh-agents/workspaces/0.1.1`. A fresh
  session in a disposable jj-colocated repository first established the
  sandbox boundary: under `workspace-write`, `jjx open codex-accept` could not
  update repository metadata and failed before creating a usable checkout.
  The skill now tells a sandboxed runtime to request approval for the exact
  `jjx` command rather than treating that denial as a jjx failure or broadly
  bypassing the sandbox. With user-approved `danger-full-access`, a second
  fresh session created
  `/private/tmp/workspaces-acceptance.8gzTOE-spaces/codex-accept`, ran with that
  exact child directory as its cwd, resumed the same path on a second
  `jjx open codex-accept`, created the distinct `codex-accept-2` via
  `jjx open --unique codex-accept`, and created the explicit
  `/private/tmp/workspaces-acceptance-explicit` checkout via `jjx add <path>`.
  `jjx rm` reported all three checkouts trashed; final existence checks found
  all three absent and the original fixture present. This accepts the skill's
  command contract and cleanup behavior, not operation without repository-write
  approval.

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

Expand Codex support plugin by plugin, and keep the two halves of that
expansion distinct. A package enters the Codex publication when it declares
`targets.codex`, its manifest validates, and its platform-specific primitives
have native mappings or declared losses. It reaches runtime acceptance only
after a fresh-task smoke test passes. Eight of the fifteen enrolled packages are
at the first stage and not the second (`ndr:v0a3bm`); publication membership
should not be read as the second.
