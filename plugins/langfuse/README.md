# langfuse

Forked from [langfuse/Claude-Observability-Plugin](https://github.com/langfuse/Claude-Observability-Plugin) v1.0.0.

Sends Claude Code session traces to [Langfuse](https://langfuse.com) via a Stop hook. Each turn in a conversation becomes a Langfuse trace containing the user prompt, assistant generations, and tool observations with accurate backdated timestamps.

## Changes from upstream

Six trace-metadata QoL improvements applied to `hooks/langfuse_hook.py`:

- **(a) Richer tags + user_id** — `propagate_attributes` now receives `user_id` (from `LANGFUSE_USER_ID` env var or `$USER`) and tags `["claude-code", "cwd:<basename>", "<mode>"]` so traces are filterable by working directory and permission mode.
- **(b) Trace name with content preview** — Trace name format changes from `"Claude Code - Turn N"` to `"[Turn N] <60-char snippet>"` (or `"[/cmd] [Turn N] <snippet>"` for slash-command turns), making the Langfuse dashboard scannable at a glance.
- **(c) Leaner trace metadata** — Dropped redundant `session_id` and `user_text` keys from the trace metadata dict; kept `source`, `turn_number`, `transcript_path`, and `assistant_message_count`.
- **(d) `as_type="agent"` for orchestration tools** — Tool observations for `Skill`, `Agent`, and `Task` tool calls are tagged as `"agent"` observations instead of `"tool"` so they render correctly in the Langfuse UI.
- **(e) `level="ERROR"` on failed tools** — Tool observations are automatically flagged `ERROR` when the result has `is_error=true`, contains `"Error: "` in the output string, or the output starts with an HTTP 4xx/5xx status code.
- **(f) `release=` on Langfuse constructor** — Passes the Claude CLI version (via `claude --version`, cached per process) as the `release` field so traces are grouped by Claude release in Langfuse. Override with `LANGFUSE_RELEASE` env var.

## userConfig

The `userConfig` surface is identical to upstream — existing `pluginConfigs` work without changes:

| Key | Required | Description |
|-----|----------|-------------|
| `LANGFUSE_SECRET_KEY` | Yes | Project secret key (`sk-lf-...`) |
| `LANGFUSE_PUBLIC_KEY` | Yes | Project public key (`pk-lf-...`) |
| `LANGFUSE_BASE_URL` | No | Defaults to `https://us.cloud.langfuse.com` |
| `CC_LANGFUSE_DEBUG` | No | Write verbose logs to `~/.claude/state/langfuse_hook.log` |

## Optional env vars (not in userConfig)

| Var | Description |
|-----|-------------|
| `LANGFUSE_USER_ID` | Override the user identity on traces (defaults to `$USER`) |
| `LANGFUSE_RELEASE` | Override the release string (defaults to `claude --version` output) |
