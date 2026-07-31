# Agent Instructions

This project uses **bd** (beads) for issue tracking. Run `bd onboard` to get started.

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id>         # Complete work
bd sync               # Sync with git
```

## Marketplace metadata ownership

`MARKETPLACE.yaml` and each `plugins/*/PACKAGE.yaml` are authoritative for
marketplace and package metadata. The root Claude/Codex marketplace manifests
and per-package `.claude-plugin/plugin.json` / `.codex-plugin/plugin.json`
files are committed generated outputs; never hand-edit them.

Regenerate only those native manifests with the pinned AgentForge checkout:

```bash
env AGENTFORGE_PROJECT=/path/to/agentforge-at-949898a \
  uv run marketplace sync
```

`uv run marketplace check` recompiles to a temporary directory and detects
root, package, missing, extra, and content drift without modifying the working
tree. Skills, agents, commands, hooks, references, and other source content
remain maintained in place. Codex enrollment remains limited to the five
packages declared in `MARKETPLACE.yaml`. Declared hooks are translated into
Codex's handler schema; Codex skips plugin-bundled hooks until the user reviews
and trusts the definition.

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
