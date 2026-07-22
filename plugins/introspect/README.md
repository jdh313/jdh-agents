# introspect

Introspection tooling for Claude Code itself.

## `usage-report`

Reconstruct how a person works with Claude Code in a given repo — from their **local**
session transcripts under `~/.claude/projects/`. Surfaces:

- **Task-kickoff style** — bare prompt vs slash command vs plan mode, per session.
- **Skill fingerprint** — both invocation counts and `attributionSkill` *depth* (how many
  actions were performed under each skill).
- **Slash commands** typed (workflow vs session-management).
- **Subagents** spawned, by type.
- **MCP tools** and overall tool-usage distribution.
- **Models** used, and **activity** over time (sessions/day, branches touched, worktree use).

### Privacy

Per-user and per-machine — it cannot see anyone else's sessions. Default output is **names,
counts, and dates only**. No prompt text, command arguments, skill arguments, or subagent
prompts are included unless you explicitly pass `--include-args` (which truncates and is
opt-in). The parser is read-only and makes no network calls.

### Use

Invoke the skill (`/introspect:usage-report`, or just describe the goal — "analyze my Claude
Code workflow"), or run the bundled script directly:

```sh
python3 plugins/introspect/skills/usage-report/scripts/claude-usage-report.py --repo <keyword>
```

Flags: `--repo <substring>` (default `cartaos`), `--all`, `--since YYYY-MM-DD`, `--json`,
`--out FILE`, `--projects-dir PATH`, `--include-args`.

Sharing a teammate's workflow: have them run it locally and send back the generated markdown.
No third-party dependencies — Python 3.9+ standard library only.
