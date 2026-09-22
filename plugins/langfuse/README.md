# langfuse

Forked from [langfuse/Claude-Observability-Plugin](https://github.com/langfuse/Claude-Observability-Plugin) v1.0.0 (upstream HEAD ea5eca1dfa26 as of 2026-07-06).

Sends Claude Code and Codex session traces to [Langfuse](https://langfuse.com) via a Stop hook. Each turn becomes a Langfuse trace containing the user prompt, assistant generations, and tool observations with accurate backdated timestamps.

## Requirements

[`uv`](https://docs.astral.sh/uv/) on `PATH`. The hook runs via `uv run` and pins its own `langfuse` dependency via a PEP 723 script header — no separate `pip install` step. First invocation per machine builds a cached venv (~1–2 s); subsequent runs are fast (~50 ms overhead) and well under the existing 5 s flush cap.

## Changes from upstream

The shared hook accepts Claude Code transcript rows and Codex rollout rows. Six trace-metadata QoL improvements are applied to `hooks/langfuse_hook.py`:

- **(a) Richer tags + user_id** — `propagate_attributes` now receives `user_id` (from `LANGFUSE_USER_ID` env var or `$USER`) and runtime, working-directory, and permission-mode tags.
- **(b) Trace name with content preview** — Trace name format changes from `"Claude Code - Turn N"` to `"[Turn N] <60-char snippet>"` (or `"[/cmd] [Turn N] <snippet>"` for slash-command turns), making the Langfuse dashboard scannable at a glance.
- **(c) Leaner trace metadata** — Dropped redundant `session_id` and `user_text` keys from the trace metadata dict; kept `source`, `turn_number`, `transcript_path`, and `assistant_message_count`.
- **(d) `as_type="agent"` for orchestration tools** — Tool observations for `Skill`, `Agent`, and `Task` tool calls are tagged as `"agent"` observations instead of `"tool"` so they render correctly in the Langfuse UI.
- **(e) `level="ERROR"` on failed tools** — Tool observations are automatically flagged `ERROR` when the result has `is_error=true`, contains `"Error: "` in the output string, or the output starts with an HTTP 4xx/5xx status code.
- **(f) `release=` on Langfuse constructor** — Passes the active CLI version (`claude --version` or `codex --version`, cached per process) as the `release` field. Override with `LANGFUSE_RELEASE`.

## userConfig

The `userConfig` surface is identical to upstream — existing `pluginConfigs` work without changes:

| Key | Required | Description |
|-----|----------|-------------|
| `LANGFUSE_SECRET_KEY` | Yes | Project secret key (`sk-lf-...`) |
| `LANGFUSE_PUBLIC_KEY` | Yes | Project public key (`pk-lf-...`) |
| `LANGFUSE_BASE_URL` | No | Defaults to `https://us.cloud.langfuse.com` |
| `CC_LANGFUSE_DEBUG` | No | Write verbose logs to `~/.claude/state/langfuse_hook.log` |

## Codex setup and trust

Codex does not expose Claude's `userConfig` form. Set `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and optionally `LANGFUSE_BASE_URL` in the environment inherited by Codex. The hook writes state and logs under `$CODEX_HOME/state` (default `~/.codex/state`).

Codex treats bundled hooks as untrusted code. After installation, inspect and explicitly trust the Langfuse `Stop` and `SessionStart` commands with `/hooks`; until then Codex skips them. Trust does not replace consent: once enabled, the Stop hook exports prompts, model responses, and tool inputs/outputs to the configured Langfuse endpoint. The SessionStart tripwire exports the session ID, runtime/mode classification, session source, and hostname; it deliberately redacts the ancestor command line because non-interactive prompts can appear there.

## Optional env vars (not in userConfig)

| Var | Description |
|-----|-------------|
| `LANGFUSE_USER_ID` | Override the user identity on traces (defaults to `$USER`) |
| `LANGFUSE_RELEASE` | Override the release string (defaults to the active CLI's `--version` output) |
