# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important: Check Latest Documentation

**Claude Code's plugin system is evolving rapidly.** Before making changes to plugins, skills, agents, or commands in this repo:

1. **Always check the latest Claude Code documentation** using `Skill(docs)` or the `claude-code-guide` agent
2. **Verify current plugin.json schema** — fields and requirements change frequently
3. **Test installation** of any modified plugins before committing

Do not rely solely on this CLAUDE.md or existing plugin examples — they may be outdated.

## Project Overview

**jdh-agents** is a personal Claude Code and Codex plugin marketplace with automated validation and synchronization. It provides:
- Authoritative AgentForge marketplace/package definitions in `MARKETPLACE.yaml` and `plugins/*/PACKAGE.yaml`
- Committed generated native manifests for all eighteen Claude packages and the fifteen Codex-enrolled ones
- Generated-output drift detection, native schema validation, and a repo-wide privacy gate
- GitHub Actions CI/CD for marketplace integrity

See `docs/dual-agent-operating-model.md` for Claude/Codex ownership boundaries, runtime mappings, and runtime acceptance.

## High-Level Architecture

### Directory Structure

```
jdh-agents/
├── MARKETPLACE.yaml              # Authoritative collection metadata
├── .claude-plugin/               # COMPILER OUTPUT — remote-install entry point
│   └── marketplace.json          # Root copy of the Claude publication
├── .github/workflows/
│   └── validate.yml              # CI/CD: privacy gate + drift + native validation
├── plugins/                      # AUTHORING SOURCE — edit here
│   └── [plugin-name]/
│       ├── PACKAGE.yaml          # Authoritative package metadata
│       ├── skills/               # Skills (optional)
│       ├── agents/               # Agents (optional)
│       ├── commands/             # Commands (optional)
│       └── README.md
├── marketplaces/                 # COMPILER OUTPUT — committed, never hand-edited
│   ├── claude/                   # Complete Claude marketplace root (18 packages)
│   │   ├── .claude-plugin/marketplace.json
│   │   └── plugins/[name]/       # Compiled manifest + bodies
│   └── codex/                    # Complete Codex marketplace root (15 packages)
│       ├── .agents/plugins/marketplace.json
│       └── plugins/[name]/       # Compiled manifest + bodies + agents/openai.yaml
├── scripts/                      # Automation utilities
│   ├── agentforge.sh             # Pinned-compiler wrapper (version + sha256)
│   ├── privacy-scan.sh           # History privacy gate (pinned Betterleaks)
│   └── tests/                    # Gate self-test + attention-workflow behavior
└── README.md
```

The split is the point: `plugins/` is what a human writes, `marketplaces/` is
what a runtime loads. Nothing under `marketplaces/` survives a `sync` unless the
compiler reproduces it, so an edit made there is discarded without warning. The
same holds for the root `.claude-plugin/marketplace.json`: it is a compiled copy
of the Claude publication, emitted because the Claude publication declares
`root-manifest: true`, and it exists so `marketplace add jdh313/jdh-agents`
resolves remotely. Its package sources point into `marketplaces/claude/`.

### Core Concepts

**Plugin Registry Flow:**
1. Edit `MARKETPLACE.yaml`, `plugins/[plugin-name]/PACKAGE.yaml`, or maintained source content.
2. Run `scripts/agentforge.sh compile MARKETPLACE.yaml --out marketplaces` to compile the AgentForge publications into `marketplaces/`. The compiler stages and publishes by rename, so a failed compile leaves the committed tree untouched and a successful one prunes every stale file.
3. Run `scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native` to compare canonical compilation with committed output without writing, and to run `claude plugin validate --strict` over the Claude publication.
4. Commit canonical source and the regenerated `marketplaces/` tree together.
5. GitHub Actions automatically re-runs all checks on push/PR.

**Plugin Structure:**
- Each plugin has an authoritative `PACKAGE.yaml` containing metadata and runtime target overlays.
- Native `plugin.json` files live only under `marketplaces/`; they are generated and must not be hand-edited.
- Optional subdirectories: `skills/`, `agents/`, `commands/` containing the actual plugin components
- README.md documents the plugin's features and usage

### Marketplace.json Schema

Top-level fields (required):
- `name` (string): Marketplace name
- `description` (string): Marketplace description
- `owner` (object): Marketplace owner with `name` and `email`
- `plugins` (array): List of discovered plugins
- `metadata` (object): Publishing metadata generated for the target runtime

Plugin entry schema (in marketplace.json):
- `name` (string, required): Plugin name
- `source` (string, required): Path to plugin directory (e.g., `./plugins/my-plugin`)
- `description` (string, required): Plugin description
- `version` (string, required): Semantic version (e.g., "0.1.0")
- `author` (object, required): Author with required `name` field; optional `email`, `url`
- `keywords` (array, optional): Search keywords
- `homepage` (string, optional): Plugin homepage URL
- `repository` (string, optional): Repository URL

**Note:** The complete native marketplace manifest is generated by `agentforge compile`. Do not manually edit it.

### Public export (retired)

This repo used to be a private source of truth that exported an allowlisted
subset one-way to `jdh313/shared-claude-plugins` (marketplace name `jdh`). That
existed only because this repo could not be installed from directly.

It can now: the repo is public and the Claude publication declares
`root-manifest: true`, so `marketplace add jdh313/jdh-agents` resolves and
serves all packages. The export mechanism -- `export/public.json`, the
`export-public.yml` workflow, the `export` subcommand, and the
allowlist-manifest builder behind it -- has been removed.

The privacy scanner it introduced outlived it, and is now the repo-wide gate:
`scripts/privacy-scan.sh`, run by the prek pre-push hook and by CI.

`jdh313/shared-claude-plugins` still exists and no longer receives updates.
Prefer `marketplace add jdh313/jdh-agents`.

## Common Development Tasks

### Adding a New Plugin

```bash
# 1. Create plugin directory
mkdir -p plugins/my-plugin

# 2. Add authoritative metadata in plugins/my-plugin/PACKAGE.yaml
# 3. Add plugin files (skills/, agents/, commands/, README.md, etc.)
# 4. Regenerate committed native manifests with the pinned compiler
scripts/agentforge.sh compile MARKETPLACE.yaml --out marketplaces

# 5. Verify the committed tree
scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native
scripts/privacy-scan.sh

# 6. Commit PACKAGE.yaml, source content, and the regenerated publications
#    This is a jj repo -- there is no staging area, so the working copy is
#    already the change. Describe it and start a new one.
jj commit -m "feat[my-plugin]: add my-plugin (v0.1.0)"
```

Canonical source and the regenerated `marketplaces/` tree belong in the **same**
commit. Splitting them leaves a revision where the compiled output disagrees
with its source, which is exactly the drift `agentforge check` exists to catch.

### The compiler pin, and one environment trap

**`scripts/agentforge.sh` fetches its own pinned compiler — there is nothing to set up.** The pin lives in that script as `AGENTFORGE_VERSION` plus a per-platform `sha256_for` map taken from the release's own `SHA256SUMS`. On first use it downloads the matching release binary, verifies the hash before executing a single byte, and caches it under `.cache/agentforge/<version>/` (gitignored). The hash is re-verified on every run, so a corrupted or tampered cache is replaced rather than trusted. CI runs this same code path — there is no separate CI pin, and no worktree dance.

To bump the compiler: change `AGENTFORGE_VERSION`, replace the hash map from the new release's `SHA256SUMS`, re-run `compile`, and commit the regenerated tree.

**`AGENTFORGE_PROJECT` is for working *on* AgentForge, and is never the merge gate.** It runs a source checkout as-is via `bun`, deliberately without asserting any revision — that is the point of the escape hatch. It prints a warning naming the checked-out revision every time, because a compile from unreleased source can succeed or fail for reasons that have nothing to do with your change. `AGENTFORGE_BIN` similarly names an arbitrary executable and skips verification. Neither is what CI runs. If a result surprises you, re-run with both unset.

**The two runtimes disagree about whether the working tree is live, and the disagreement runs opposite ways.**

`~/.claude/plugins/known_marketplaces.json` points `jdh-agents` at `<repo>/marketplaces/claude`, and Claude resolves installed plugins straight out of that directory rather than a version-bucketed cache. So **an uncommitted change under `marketplaces/claude/` is immediately live to every Claude session on the machine** — including one produced by a `scripts/agentforge.sh compile` you ran to test something. Checking out a branch re-points every installed plugin. `--plugin-dir` is the honest way to name what you are testing, but it is not what isolates you.

Codex is the inverse. `codex plugin add` **copies** into `~/.codex/plugins/cache/jdh-agents/<plugin>/<version>/`, so the working tree is *not* live there — and because the cache is keyed by version, an unchanged version number means it is never invalidated. A Codex plugin can serve months-old bytes while `codex plugin list` prints the current marketplace path for it, which is indistinguishable from being up to date. Re-run `codex plugin add <name>@jdh-agents` after any change you expect Codex to see.

The trap that follows from the pair: a smoke test that passes under Claude proves nothing about Codex, because Claude read your edit and Codex read its cache.

### Validating Changes Locally

Before pushing, always run the full validation suite:

```bash
scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native
scripts/privacy-scan.sh
```

`check` covers output drift, managed-output content, managed `.json` parsing,
skill frontmatter, manifest parity, and plugin path resolution; `--claude-native`
adds `claude plugin validate --strict`. The privacy scan is separate because
AgentForge only ever sees files a publication declares. To regenerate rather
than verify:

```bash
scripts/agentforge.sh compile MARKETPLACE.yaml --out marketplaces
```

### Updating an Existing Plugin

1. Edit plugin files in `plugins/[plugin-name]/`
2. **Bump the version** in `PACKAGE.yaml` (see below)
3. Recompile: `scripts/agentforge.sh compile MARKETPLACE.yaml --out marketplaces`
4. Verify: `scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native`
5. Commit changes

### Version Bumping

**Always bump the version in `PACKAGE.yaml` when modifying a plugin:**

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| New feature/skill | Minor | 0.1.0 → 0.2.0 |
| Bug fix | Patch | 0.1.0 → 0.1.1 |
| Breaking change | Major | 0.1.0 → 1.0.0 |

Then re-run `scripts/agentforge.sh compile MARKETPLACE.yaml --out marketplaces` to regenerate native manifests.

### Reviewing Plugin Changes

**Generated plugin.json review:**
- Check required fields are present (name, version, description, author.name)
- Verify `source` path exists relative to `plugins/` directory
- Ensure version follows semantic versioning (major.minor.patch)

**Common issues (caught by `agentforge check`):**
- A managed `.json` output that does not parse
- Skill frontmatter that fails its target's schema
- A declared plugin whose source path does not resolve
- Manifest parity drift between a registry entry and the materialized package
- Managed output containing an absolute home path or a declared redaction

## CI/CD Pipeline

**Workflow:** `.github/workflows/validate.yml` runs on every push and PR:
1. Checks out code
2. Runs `scripts/tests/test_privacy_gate.sh`, then `scripts/privacy-scan.sh` over committed history (checkout needs `fetch-depth: 0`)
3. Runs `scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native`

**Common CI failures:**
- **"Native manifests are OUT OF SYNC"** → Run `scripts/agentforge.sh compile MARKETPLACE.yaml --out marketplaces` and commit the changes
- **"Validation failed: Missing required X field"** → Fix `MARKETPLACE.yaml` or the affected `PACKAGE.yaml`, then regenerate
- **Linting issues** → Fix JSON syntax or markdown formatting in plugin files

## Plugin Development Patterns

### Agent `tools:` vs. Skill `allowed-tools:` — different semantics

These two fields look similar but behave differently. Getting them wrong causes silent breakage: an agent that documents using a tool it cannot actually call, or a skill that prompts for approval on every invocation.

**Agent `tools:` is a filter (allowlist)** — restricts an inherited set.
- Default behavior (no `tools:` field): the agent inherits **all** tools available in the parent session, including MCP tools.
- If `tools:` is set, it becomes an allowlist. Tools not listed are blocked even if the user has them authorized at session level.
- To grant MCP tool access in an agent, either:
  1. List the specific MCP tool names explicitly (e.g. `mcp__obsidian-mcp__patch_note`), or
  2. Omit `tools:` entirely and use `disallowedTools:` for a deny-list approach.
- Plugin agents **cannot** declare `mcpServers:`, `hooks:`, or `permissionMode:` in frontmatter — those fields are ignored for security reasons. The MCP server must be connected at the user level.

**Skill `allowed-tools:` is pre-approval, not a filter** — does NOT restrict tool use.
- Tools listed in `allowed-tools:` are pre-approved (no permission prompt) while the skill is active.
- Tools NOT listed remain callable — the user is just prompted at call time per their normal permission settings.
- So `allowed-tools:` is a UX optimization, not a correctness requirement.
- Skills should list tools the skill itself invokes inline. Dispatched-agent tool use does NOT count — agents have their own permission scope (their `tools:` filter).

**Practical rules for this repo:**
- When adding an MCP tool reference to an agent's operational guidance, also add it to that agent's `tools:` array — or the agent will document a capability it can't use.
- When auditing skills, only add to `allowed-tools:` what the skill calls in the main session. Tool calls inside `@vault-reader` / `@note-editor` dispatches belong to those agents, not the skill.

Source: https://code.claude.com/docs/en/sub-agents.md, https://code.claude.com/docs/en/skills.md (verified 2026-05-25).

### Renaming an adapted skill

A skill adapted from upstream carries **two** names: its local identity, and
upstream's name for the skill it came from. A rename changes only the first.
Upstream's name is load-bearing in four kinds of place, and must survive:

- the `upstream:` block's `path:` — the provenance link, and what drift review
  resolves against
- `UPSTREAM.md` — every row describing what *upstream* does
- `THIRD-PARTY-NOTICES.md` — the attribution row, which is a license notice
- any credit for a borrowed idea (e.g. spec-flow's contract template)

**A bulk find-and-replace across those files is the hazard**, because they
legitimately contain both names. A sweep rewrites the sentences describing
upstream too, silently turning a true statement into a fabricated attribution —
the exact failure `skillsmith:upstream-review` exists to catch, arriving via the
tool used to do the rename. This is not hypothetical; it happened during the
`wayfinder` -> `chart` rename and had to be repaired.

Rename by hand, protect the upstream path with a sentinel if you must script it,
and re-read every ledger row afterwards asking: does this still say what upstream
actually does?

### Canonical Obsidian tooling

Plugins that touch the Obsidian vault should converge on these names:

- **MCP server:** `mcp__obsidian-mcp__*` is the canonical Obsidian MCP server across the marketplace.
- **CLI binary:** `obsidian-cli` is the canonical CLI binary name in allowed-tools and agent `tools:` entries. The bare `obsidian` binary is the desktop app launcher, not a CLI — `Bash(obsidian read *)` etc. will not work as expected.

Canonical tool names on `mcp__obsidian-mcp__*`:

| Read | Write | Search | Frontmatter | Tags / files |
|------|-------|--------|-------------|--------------|
| `read_note`, `read_multiple_notes` | `write_note`, `patch_note`, `delete_note` | `search_notes` | `get_frontmatter`, `update_frontmatter` | `manage_tags`, `move_note`, `move_file`, `list_directory` |

`patch_note` covers both surgical body replacement and append operations (use the `operation` arg).

For shell access, default to `Bash(obsidian-cli *)` rather than bare `Bash`.

### Plugin.json Metadata

The examples below describe generated Claude output for review and
troubleshooting only. Express these fields in `PACKAGE.yaml`; do not author the
JSON directly.

Minimal example:
```json
{
  "name": "simple-plugin",
  "version": "1.0.0",
  "description": "Brief description",
  "author": {
    "name": "Your Name"
  }
}
```

Full example with all optional fields:
```json
{
  "name": "comprehensive-plugin",
  "version": "2.1.0",
  "description": "Detailed description of what the plugin does",
  "author": {
    "name": "Your Name",
    "email": "you@example.com",
    "url": "https://github.com/yourusername"
  },
  "keywords": ["openapi", "fastapi", "documentation"],
  "homepage": "https://github.com/yourusername/comprehensive-plugin",
  "repository": "https://github.com/yourusername/comprehensive-plugin"
}
```

**Important:** Do not include a `category` field in plugin.json - Claude Code does not support it and installation will fail.

## Key Files and Responsibilities

| File | Purpose | Responsibility |
|------|---------|-----------------|
| `MARKETPLACE.yaml` | Marketplace identity, publications, enrollment | Authoritative maintained metadata |
| `plugins/[name]/PACKAGE.yaml` | Package metadata and target overlays | Authoritative maintained metadata |
| `.claude-plugin/marketplace.json` | Root copy of the Claude publication — what `marketplace add jdh313/jdh-agents` reads | Generated and committed by `agentforge compile` |
| `marketplaces/claude/` | Complete Claude marketplace root — the directory a local install is pointed at | Generated and committed by `agentforge compile` |
| `marketplaces/codex/` | Complete Codex marketplace root — the directory Codex is pointed at | Generated and committed by `agentforge compile` |
| `scripts/agentforge.sh` | Pinned-compiler wrapper: version + per-platform sha256, fetch, verify, exec | The only way to run the compiler; CI runs this same script |
| `.betterleaks.toml` | Privacy-gate rules: inherited default ruleset + two repo rules | Top-level keys must stay above every `[table]` header |
| `scripts/privacy-scan.sh` | Privacy gate over committed history | Pinned Betterleaks; `--log-opts HEAD` is load-bearing in a jj repo |
| `.betterleaks-baseline.json` | Ten pre-existing findings, accepted once | Should not grow; fix or `betterleaks:allow` instead |
| `scripts/tests/test_privacy_gate.sh` | Plants violations, requires rejection | Guards against a silently-inert gate |
| `.github/workflows/validate.yml` | CI/CD pipeline | Automated validation on push/PR |

## Troubleshooting Broken Plugins

### Symptom: Plugin shows "installed" but can't be used or uninstalled

**Diagnosis:**
1. Check debug logs for errors like:
   ```
   [ERROR] Plugin X has an invalid manifest file... Validation errors: agents: Invalid input: must end with ".md"
   ```
2. Check if cache exists and has all components:
   ```bash
   ls -laR ~/.claude/plugins/cache/jdh-agents/[plugin-name]/
   ```

**Common Causes:**

1. **Explicit component paths in plugin.json pointing to directories instead of files**
   - Wrong: `"agents": "./agents/"` or `"skills": "./skills/"`
   - Fix: Remove explicit paths entirely (use auto-discovery) OR specify individual `.md` files
   - Auto-discovery finds: `skills/`, `agents/`, `commands/`, `hooks/hooks.json` automatically

2. **Stale cache with old/broken plugin.json**
   - Cache retains old version even after source is fixed
   - Fix: Bump version in plugin.json, push, then update plugin

3. **Orphaned registry entry (cache deleted but registry remains)**
   - Symptoms: Shows installed, can't uninstall, can't use
   - Fix: Remove entry from `~/.claude/plugins/installed_plugins.json`

4. **Incomplete cache (only plugin.json, missing skills/agents/commands)**
   - Check with: `tree ~/.claude/plugins/cache/jdh-agents/[plugin-name]/`
   - Fix: Delete cache dir and remove registry entry

**Full Reset Procedure:**
```bash
# 1. Delete the broken cache
rm -rf ~/.claude/plugins/cache/jdh-agents/[plugin-name]

# 2. Remove from registry (edit JSON to remove the plugin entry)
# File: ~/.claude/plugins/installed_plugins.json

# 3. Restart Claude Code

# 4. Reinstall fresh
/plugin install [plugin-name]@jdh-agents
```

### Generated plugin.json rules

**DO:**
- Edit `PACKAGE.yaml`, then regenerate.
- Review generated native manifests and keep them committed.
- Bump the version in `PACKAGE.yaml` when package behavior changes.

**DON'T:**
- Hand-edit root or package native manifests.
- Expand Codex enrollment without native mapping and fresh-runtime acceptance.
- Pre-authorize Codex hook trust, or imply a translated hook runs before the
  user reviews it.
- Add a Claude-only construct to a Codex-enrolled package without declaring the
  resulting loss under `targets.codex.losses`.

## Notes for Future Development

- **Manifest projection:** `agentforge compile` republishes the whole `marketplaces/` tree by rename and prunes every stale file; maintained source content under `plugins/` stays in place.
- **Manifest stability:** Never manually edit generated JSON. Update canonical YAML and re-run `scripts/agentforge.sh compile`.
- **Determinism:** Re-running sync without canonical changes must leave the repository clean.
- **Semantic versioning:** Enforce semantic versioning (major.minor.patch) for all plugin versions to maintain marketplace stability.
- **Parallelizing plugin work:** Give each agent its own worktree, not just its own plugin directory. `agentforge compile` reads the *whole* marketplace and hard-fails (exit 2) on any package's undeclared loss, so agents editing disjoint `plugins/<name>/` directories in one checkout still fail each other's compile probes — and each failure looks like the agent's own bug. Disjoint file ownership is not enough when the verification command is whole-tree. Merge the branches at the end; the diffs genuinely are disjoint.
- **One compile per batch:** `agentforge compile` regenerates all of `marketplaces/`. Parallel agents must never run it; the orchestrator runs it once after collecting their changes.

## Commit format

`type[scope]: subject (vX.Y.Z)` — e.g. `feat[ndr]: worthiness rubric for
capture-decision skill (v0.6.0)`. The version suffix is mandatory on
plugin-changing commits and tracks that plugin's own `PACKAGE.yaml` version;
there are no repo-level tags. The `commit` plugin's `commits` skill encodes
this style.
