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

Flags: `--repo <substring>` (default `acmeos`), `--all`, `--since YYYY-MM-DD`, `--json`,
`--out FILE`, `--projects-dir PATH`, `--include-args`.

Sharing a teammate's workflow: have them run it locally and send back the generated markdown.
No third-party dependencies — Python 3.9+ standard library only.

## `conversation-temperature`

Read your own **authored register** across your whole Claude Code history — not what you
worked on, but how you come across. Three axes:

- **Terseness** — message-length distribution.
- **Heat** — friction markers: profanity, shouting, strong corrections, exclamations.
- **Warmth** — affect markers: gratitude, praise, politeness.

Output leads with marker rates per 1,000 messages and *real quoted messages*, with the
composite indices treated as directional arrows rather than scores. Per-project and monthly
cuts answer "hotter in one repo than another?" and "warmer since June?". Markers are lexical,
not semantic, so the read always ships with a contamination caveat.

Only analyzes the local user — it has no view of anyone else's sessions. Unlike
`usage-report`, this one **quotes your own message text back to you** — that is the point of
it, since the marker counts are only trustworthy against their examples. Nothing leaves the
machine either way.

### Use

```sh
python3 plugins/introspect/skills/conversation-temperature/scripts/conversation-analysis.py --temperature --examples 6
```

Flags: `--temperature` (tone section only, to stdout), `--examples N` (quoted examples per
category, default 6). With no flags the script emits the full conversation-analysis report —
including this tone section — to a dated file under `.docs/` in the current directory.

Stdlib-only, read-only, no network calls. Requires Python 3.13+ (`uv run` also works).
