# Project Profile: cc-marketplace

Personal Claude Code plugin marketplace with automated validation and synchronization. Hosts 16 plugins (skills/agents/commands/hooks) discovered via .claude-plugin/plugin.json files; validate_schema.py + lint_plugins.py + sync_marketplace.py form the merge gate.

> Last updated: 2026-05-31T01:15:14Z | Version: 1

## Goals

- **tooling**: Scaffold, validate, version-bump, sync, and commit a plugin with minimum friction — plugin.json + auto-discovery + the three Python scripts as the spine.
- **maintenance**: Track upstream schema/frontmatter changes (e.g. allowed-tools -> tools, manifest field churn) and apply fixes across all 16 plugins as the platform evolves.
- **quality**: Every change must pass validate_schema.py, lint_plugins.py, and produce no diff from sync_marketplace.py. CI enforces this on push/PR.
- **onboarding**: Stand up the babysitter profile, skills, agents, and processes locally before tackling any specific pain points. Structure first; remediation later.

## Tech Stack

### Languages

- Python v3.11 (primary)
- Markdown vn/a (content (skills, agents, commands, docs))
- JSON vn/a (manifests)
- YAML vn/a (GitHub Actions workflows + skill/agent frontmatter)

### Infrastructure

- GitHub Actions [ci]
- jj (Jujutsu, colocated with git) [vcs]

## Architecture

**Pattern:** plugin-marketplace
**Data flow:** Each plugin author maintains plugins/<name>/.claude-plugin/plugin.json with metadata. sync_marketplace.py rglobs all plugin.json files, builds a sorted plugin list with auto-generated source paths (./plugins/<name>), and rewrites .claude-plugin/marketplace.json (bumping metadata.lastUpdated only when the plugin set changed). validate_schema.py checks marketplace.json required fields and verifies each plugin source path resolves to a real .claude-plugin/plugin.json. lint_plugins.py walks every file under plugins/, validates JSON, flags unusual extensions, checks empty/short markdown. CI runs all three on push/PR and fails if sync produces a diff.

### Modules

| Module | Path | Description |
|--------|------|-------------|
| scripts | `scripts/` | Python automation for plugin discovery, schema validation, and linting |
| marketplace-registry | `.claude-plugin/marketplace.json` | Auto-generated central registry of all plugins (16 plugins) |
| plugins | `plugins/` | Independent Claude Code plugins (coach, commits, compass, craft, debate, doing, homelab-ops, job-search, librarian, linear, ndr, permissions-manager, pm, python-dev, shake-tune, spec-flow); each has .claude-plugin/plugin.json plus optional skills/, agents/, commands/, hooks/, references/ |
| ci | `.github/workflows/` | GitHub Actions: validate.yml (schema+lint+sync check) and plugin-review.yml |
| agent-instructions | `CLAUDE.md + AGENTS.md` | Architecture docs for Claude Code agents and beads (bd) workflow guidance |

**Entry points:** `scripts/sync_marketplace.py`, `scripts/validate_schema.py`, `scripts/lint_plugins.py`

## Team

- **Jacob Hoehler** (owner-maintainer): plugin authoring, marketplace maintenance, CI

## Workflows

### development

Solo trunk-based development on main (jj-colocated). Edit plugin or scripts, run validate + lint + sync locally, commit with type[scope]: subject (vX.Y.Z) format. CI gate re-runs the three checks on push.
**Triggers:** manual

1. edit plugin files or scripts
2. bump plugin.json version if a plugin changed
3. python scripts/sync_marketplace.py
4. python scripts/validate_schema.py
5. python scripts/lint_plugins.py
6. commit with type[scope]: subject (vX.Y.Z)

### plugin-add

Add a new plugin to the marketplace
**Triggers:** manual

1. mkdir -p plugins/<name>/
2. create .claude-plugin/plugin.json
3. add skills/agents/commands/README.md
4. python scripts/sync_marketplace.py
5. python scripts/validate_schema.py
6. python scripts/lint_plugins.py
7. commit plugin files + updated marketplace.json

### plugin-update

Update an existing plugin
**Triggers:** manual

1. edit plugin files
2. bump version in plugin.json (semver)
3. python scripts/sync_marketplace.py
4. python scripts/validate_schema.py && python scripts/lint_plugins.py
5. commit

### weekly-review

Automated weekly review of plugins via Claude Code against current best practices; creates GitHub issue with findings
**Triggers:** schedule, workflow_dispatch

1. scheduled cron (Mon 9am UTC)
2. run claude -p review prompt
3. write review-results.md
4. create issue via peter-evans/create-issue-from-file@v5

## Tools

### Linting

- custom-python-linter (`scripts/lint_plugins.py`)

## Services

- **Anthropic API** (ai) - api.anthropic.com

## CI/CD

**Provider:** github-actions
**Config files:** `.github/workflows/validate.yml`, `.github/workflows/plugin-review.yml`

### Pipelines

- **validate** (trigger: push|pull_request)
  Stages: checkout -> setup-python@3.11 -> validate_schema.py -> lint_plugins.py -> sync_marketplace.py + git diff check
- **plugin-review** (trigger: schedule(cron:0 9 * * 1)|workflow_dispatch)
  Stages: checkout -> setup-bun -> install @anthropic-ai/claude-code -> claude -p review of plugins/ -> create-issue-from-file@v5

## Pain Points

- **low** [ci]: Easy to forget running sync_marketplace.py after plugin edits — drift causes CI failure on push; explicit idempotency-fix commit suggests recurring lastUpdated noise
  - Remediation: Pre-commit/pre-push hook that runs sync_marketplace.py + validate + lint, or a babysitter process that wraps the plugin-update workflow. Documented but not active priority (user chose build-structure-first).
- **low** [workflow]: Per-plugin version bump in plugin.json is manual and easy to miss; CLAUDE.md devotes a section to it
  - Remediation: Babysitter process or skill that detects plugin file changes and prompts/automates the version bump before sync. Documented but not active priority.
- **low** [testing]: No unit tests for the Python scripts; regressions only caught by CI on real plugin data
  - Remediation: Add a tests/ directory with pytest covering sync_marketplace.py / validate_schema.py / lint_plugins.py against fixture plugin trees. Documented but not active priority.
- **medium** [workflow]: Several fix commits learning the plugin.json schema the hard way: explicit-paths-vs-auto-discovery, category field unsupported, source path prefix — schema is not stable upstream
  - Remediation: Skill or agent that fetches the latest Claude Code plugin schema docs (via Context7 or docs skill) before authoring/editing plugin.json. CLAUDE.md already calls this out. Documented but not active priority.
- **low** [workflow]: Installed-plugin cache can get stuck with broken manifest, requiring manual reset (documented in CLAUDE.md troubleshooting)
  - Remediation: Reset helper script or babysitter process that performs the documented full-reset procedure (delete cache, remove registry entry, restart, reinstall). Documented but not active priority.

## Bottlenecks

- .claude-plugin/marketplace.json touched on every plugin change (auto-regenerated); top churn file with 40 hits in last 3 months at .claude-plugin/marketplace.json (every plugin change (~40/3mo))
  Impact: low
- Per-plugin plugin.json files churn alongside content edits because version bump is required on every change at plugins/*/.claude-plugin/plugin.json (every functional plugin change)
  Impact: low
- Plugin/skill renames produce 30+ file path-rewrite commits; jj handles cleanly but commit signal-to-noise dips at plugins/<renamed>/** (rare but heavy when it happens)
  Impact: low

## Conventions

### Naming

- **plugins:** kebab-case directory names matching plugin.json name
- **skills:** kebab-case subdir under plugins/<name>/skills/ each containing SKILL.md with YAML frontmatter
- **agents:** kebab-case <agent-name>.md files under plugins/<name>/agents/ with YAML frontmatter
- **commands:** files under plugins/<name>/commands/
- **manifests:** plugin.json always lives in .claude-plugin/ relative to each plugin root

### Git

- **commitStyle:** type[scope]: subject (vX.Y.Z) — e.g. feat[ndr]:, refactor[librarian]:, feat[spec-flow]:; version suffix on plugin-changing commits
- **messageFormat:** type[scope]: subject (bracketed-scope conventional commits; type(scope): paren form also used in older commits)
- **branchStrategy:** trunk-based (jj-colocated, work lands on main; no feature branches)
- **mergeStrategy:** linear / fast-forward (jj rebase semantics; zero merge commits in last 100)
- **vcsHost:** github
- **noteJjColocated:** true
- **codeReviewProcess:** self-review (solo); CI gate (validate + lint + sync) is the merge gate
- **releaseCadence:** continuous, per-plugin semver in plugin.json; no repo-level tags

**Import order:** stdlib only (json, sys, datetime, pathlib, typing); no third-party imports in scripts/

**Error handling:** Scripts return int exit codes from main(); catch JSONDecodeError and KeyError explicitly with warning to stderr in sync; collect errors into a list and print all before non-zero exit

**Testing:** No tests/ directory or pytest config present; CI relies on the three validation scripts as the test suite

### Additional Rules

- plugin.json should be minimal; let auto-discovery find skills/agents/commands/hooks
- Do NOT add a 'category' field to plugin.json
- Do NOT set 'source' in plugin.json — sync_marketplace.py generates it
- Always bump plugin.json version on any plugin change, then re-run sync_marketplace.py
- Commit plugin.json change and updated marketplace.json together in the same commit
- Encode version in commit subject suffix: '(vX.Y.Z)'
- Agent 'tools:' is an allowlist filter; Skill 'allowed-tools:' is pre-approval (different semantics)
- Plugin agents cannot declare mcpServers/hooks/permissionMode in frontmatter (ignored)
- Scratch artifacts go in .docs/ (gitignored)
- New plugins introduced via 'feat[name]: new plugin —' commits
- Work lands on main; no feature branches (jj-colocated trunk-based)
- No repo-level git tags — versioning lives inside each plugin.json
- CI (.github/workflows/validate.yml) is the gate: validate_schema + lint_plugins + sync_marketplace must all pass

## Repositories

- **undefined** - git@github.com:jdh313/cc-marketplace.git [`/Users/jacob/Projects/cc-marketplace`]

## CLAUDE.md Instructions

- Methodology is 'Everything Claude Code' — compose Claude Code primitives directly; no external methodology (TDD/spec-driven/agile) imposed.
- Verify loop / merge gate: python scripts/sync_marketplace.py && python scripts/validate_schema.py && python scripts/lint_plugins.py
- Commit format: type[scope]: subject (vX.Y.Z) — version suffix mandatory on plugin-changing commits; use the `commits` skill.
- Before editing plugin.json, dispatch the claude-code-guide agent to fetch the current upstream schema — it churns frequently.
- Project profile lives at .a5c/project-profile.json; run history under .a5c/runs/ — both should be gitignored.
- Trunk-based jj-colocated workflow on main; no feature branches. Detect .jj/ before any commit workflow.
- Per-plugin semver in each plugin.json; no repo-level git tags.
- Planned workflows custom/plugin-author and custom/plugin-update are not yet built — author/update by hand for now, following the documented verify loop.

## Installed Extensions

- Skills: methodologies/gsd/skills/gsd-tools, methodologies/gsd/skills/template-scaffolding, methodologies/gsd/skills/frontmatter-parsing, methodologies/gsd/skills/verification-suite, methodologies/gsd/skills/git-integration, commits, claude-code-guide, plugin-dev:plugin-structure, plugin-dev:skill-development, plugin-dev:agent-development, plugin-dev:command-development
- Agents: methodologies/gsd/agents/gsd-planner, methodologies/gsd/agents/gsd-executor, methodologies/gsd/agents/gsd-verifier, methodologies/gsd/agents/gsd-codebase-mapper, code-reviewer, sdk-api-documenter, claude-code-guide, tech-lead, general-purpose
- Processes: methodologies/gsd/plan-phase, methodologies/gsd/execute-phase, methodologies/gsd/verify-work, methodologies/gsd/new-project, methodologies/gsd/iterative-convergence, cradle/project-install, specializations/cli-mcp-development/plugin-architecture-implementation, specializations/cli-mcp-development/cli-documentation-generation, specializations/devops-sre-platform/cicd-pipeline-setup, specializations/technical-documentation/style-guide-enforcement, custom/plugin-author, custom/plugin-update
