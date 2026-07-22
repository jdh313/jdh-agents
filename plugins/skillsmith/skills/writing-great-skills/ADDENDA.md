# Addenda — authoring in cc-marketplace

Repo-specific conventions that [`SKILL.md`](SKILL.md)'s generic reference doesn't cover. Reach here when authoring or editing a skill **in this marketplace**; the vocabulary and principles in SKILL.md still govern — this only adds the local mechanics.

## Layout & discovery

- A skill is a directory `plugins/<plugin>/skills/<skill-name>/` with a `SKILL.md`. Disclosed **reference** (glossaries, format files, addenda) sits beside it as sibling `.md` files.
- **Auto-discovery** finds `skills/`, `agents/`, `commands/`, `hooks/hooks.json` — do **not** list explicit component paths in `plugin.json` (e.g. `"skills": "./skills/"`), and never add a `category` field. Both break installation.
- Paths in a skill are relative to the skill directory, not `.claude-plugin/`.

## Tool declarations — two different meanings

- **Skill `allowed-tools:`** is *pre-approval*, not a filter. Tools listed skip the permission prompt while the skill is active; tools not listed remain callable (just prompted). List only what the skill itself invokes **inline** (a `Skill()` dispatch counts; a tool used by a dispatched agent does not — that belongs to the agent).
- **Agent `tools:`** is an *allowlist filter*. Omit it to inherit all parent tools (including MCP); set it and unlisted tools are blocked. To grant an MCP tool to an agent, name it explicitly. Plugin agents cannot declare `mcpServers:`, `hooks:`, or `permissionMode:`.

## Provenance (this plugin's own convention)

Any skill adapted from upstream pins its source in `SKILL.md` frontmatter (`upstream:` block) and records intentional divergences in a sibling `UPSTREAM.md` ledger. `UPSTREAM.md` is read only by `skillsmith:upstream-review` — never reference it from `SKILL.md`, so it doesn't load at runtime. `reviewed_sha` is the last upstream commit touching the pinned `path`, not repo HEAD. See this plugin's README for the full convention.

## Verify & commit

- Verify loop / merge gate: `uv run marketplace check` (sync-drift + schema + lint), then `uv run pytest`. Run `uv run marketplace sync` first if you added or renamed a plugin, and commit the regenerated `.claude-plugin/marketplace.json`.
- Commit format: `type[scope]: subject (vX.Y.Z)` — the version suffix is mandatory on plugin-changing commits and tracks that plugin's own `plugin.json` version. Bump the version before syncing (feature → minor, fix → patch, breaking → major).
