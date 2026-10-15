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

The `userConfig` surface is upstream's plus one opt-in switch — existing `pluginConfigs` work without changes:

| Key | Required | Description |
|-----|----------|-------------|
| `LANGFUSE_SECRET_KEY` | Yes | Project secret key (`sk-lf-...`) |
| `LANGFUSE_PUBLIC_KEY` | Yes | Project public key (`pk-lf-...`) |
| `LANGFUSE_BASE_URL` | No | Defaults to `https://us.cloud.langfuse.com` |
| `CC_LANGFUSE_DEBUG` | No | Write verbose logs to `~/.claude/state/langfuse_hook.log` |
| `CC_LANGFUSE_FOLLOWUP_ENABLED` | No | Opt in to human follow-up observations (Claude Code only, self-hosted Langfuse only; see below). Default `false` |

## Human follow-up observations (Claude Code only)

An opt-in second pass in the same Stop hook exports one Langfuse observation per genuine human submission, so an evaluator can judge how the person reacted to the previous answer. It conforms to the `human-followup` v1 contract in [`docs/langfuse-human-followup-contract.md`](../../docs/langfuse-human-followup-contract.md).

**What is exported**, per follow-up, as its own trace named `Claude Code Human Follow-up` (observation type `SPAN`, tags `claude-code` and `claude-code-feedback`, `metadata.source = claude-code-feedback`):

- input: `{"preceding_user_request", "assistant_response"}` — the previous human request and the last text the assistant gave before the follow-up
- output: `{"latest_user_message"}` — the follow-up itself; a typed slash command is rendered as `/name args`
- each field has Langfuse keys masked, then is truncated to 20,000 characters, with the counts in `metadata.truncation`

**Switches.** It runs only when all of these hold:

- `CC_LANGFUSE_FOLLOWUP_ENABLED` is `true` (default `false`)
- the kill switch `LANGFUSE_CLAUDE_FEEDBACK_ENABLED` is not `false`/`0`, and `LANGFUSE_TRACING_ENABLED` is not `false`/`0`
- both keys are set and nothing is an unresolved `op://` reference
- the base URL is a plain `http`/`https` URL without credentials, query, or fragment, **and is self-hosted**: any `langfuse.com` host, including the default `https://us.cloud.langfuse.com`, disables it

**Smoke runs.** Set `LANGFUSE_TRACING_ENVIRONMENT=claude-code-feedback-smoke`; the contract's evaluation rule excludes that environment.

**State.** `~/.claude/state/langfuse_followup_state.json` (own lock, independent of turn state) records each session's start, a timestamp cursor, and the last 200 processed entry IDs. A second `SessionStart` command (`langfuse_hook.py --session-start`) records the session start and prints nothing.

**Limitations:**

- Stop-triggered: a follow-up is exported when the turn it starts ends, not when it is typed. The last follow-up of a session that ends without another completed turn is lost.
- The first follow-up after a resume or fork is skipped: its preceding exchange is copied history from another session.
- Requires `origin.kind == "human"` on transcript rows (Claude Code >= ~2.1.291); older transcripts produce nothing. Subagents, programmatic (`sdk-cli`) sessions, teammate messages, and notifications are excluded.
- At-most-once delivery: a candidate is marked processed before it is sent and is never retried, because Langfuse would duplicate a resent observation rather than merge it.
- Codex is not implemented; under Codex the pass is a no-op. Codex still lists the extra `SessionStart` command for hook review.

## Codex setup and trust

Codex does not expose Claude's `userConfig` form. Set `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and optionally `LANGFUSE_BASE_URL` in the environment inherited by Codex. The hook writes state and logs under `$CODEX_HOME/state` (default `~/.codex/state`).

Codex treats bundled hooks as untrusted code. After installation, inspect and explicitly trust the Langfuse `Stop` and `SessionStart` commands with `/hooks`; until then Codex skips them. Trust does not replace consent: once enabled, the Stop hook exports prompts, model responses, and tool inputs/outputs to the configured Langfuse endpoint. The SessionStart tripwire exports the session ID, runtime/mode classification, session source, and hostname; it deliberately redacts the ancestor command line because non-interactive prompts can appear there.

## Optional env vars (not in userConfig)

| Var | Description |
|-----|-------------|
| `LANGFUSE_USER_ID` | Override the user identity on traces (defaults to `$USER`) |
| `LANGFUSE_RELEASE` | Override the release string (defaults to the active CLI's `--version` output) |
