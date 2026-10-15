# Langfuse human follow-up contract (`human-followup` v1)

A **human follow-up observation** records one genuine human submission together with the exchange it reacts to: the preceding human request and the assistant's last text response before the submission. A shared Langfuse evaluator reads these observations to judge, from the person's next message, how the previous answer landed.

Several harnesses export it. This document fixes the shape they share, so one evaluation rule per harness can map every exporter onto the same evaluator variables. It is a repo-level document; it is not compiled into any plugin.

## Required fields

| Field | Value |
|-------|-------|
| Observation type | `SPAN`, the root of its own trace (no parent observation) |
| Observation name and trace name | Per harness, see the mappings below |
| `metadata.source` | Per harness, see the mappings below |
| `input` | `{"preceding_user_request": string, "assistant_response": string}` |
| `output` | `{"latest_user_message": string}` |
| `metadata.schema_version` | `1` |
| `metadata.max_chars_per_field` | The per-field truncation limit, `20000` |
| `metadata.truncation` | `{preceding_user_request, assistant_response, latest_user_message}`, each `{original_chars, exported_chars, truncated}` |
| Trace session | The harness session ID |
| Start/end time | The submission time of the follow-up |
| Environment | The SDK's normal environment; smoke runs use `<source>-smoke` |

**Masking happens before truncation.** Each of the three strings has the configured public and secret key values, and anything matching `\b[sp]k-lf-[\w-]+\b`, replaced with `[redacted-langfuse-secret]`. The masked string is then cut to 20,000 characters; `original_chars` counts the masked string. No other content redaction is applied. Character counts are the harness language's native string length (UTF-16 units in TypeScript, code points in Python), so they can differ for text outside the Basic Multilingual Plane.

**Harness identity** is carried by `metadata.harness` plus a harness trace tag. A consumer that must distinguish harnesses filters on `metadata.source`, which every conforming exporter sets.

## Semantic window

- **The follow-up** is a message a person typed and submitted in an interactive session. Programmatic sessions, subagents, teammate/peer messages, notifications, tool results, injected skill bodies, compaction summaries, and harness-generated continuation messages are never follow-ups.
- **The preceding request** is the nearest earlier human submission on the follow-up's own conversation path (its ancestry), never the physically previous row of a log. Rewound or abandoned branches do not count. If that nearest submission cannot be exported (for example, it is image-only), the follow-up is skipped rather than paired with an older request.
- **The assistant response** is the last assistant message with non-empty visible text between the preceding request and the follow-up. Thinking and tool calls are excluded.
- **Skips.** No observation is exported when there is no preceding request (first message), when no assistant text lies between the request and the follow-up (the exporter must not reach past the preceding request to an older exchange), or when the preceding exchange belongs to another session.

## Dedupe and delivery

- Each human submission produces at most one observation. Two identical messages submitted separately are two observations.
- Delivery is **at-most-once**. Langfuse v4 does not merge a resent observation into an earlier one, so a retry would show up as a duplicate; an exporter that cannot confirm delivery drops the observation instead of resending.

## Claude Code mapping

Exporter: the `langfuse` plugin's Stop hook (`plugins/langfuse/hooks/langfuse_hook.py`), opt-in via `CC_LANGFUSE_FOLLOWUP_ENABLED`, self-hosted Langfuse only.

| Contract field | Claude Code value |
|----------------|-------------------|
| Name | `Claude Code Human Follow-up` |
| `metadata.source` | `claude-code-feedback` |
| `metadata.harness` | `claude-code` |
| Trace tags | `claude-code`, `claude-code-feedback` |
| `metadata.contract` / `contract_version` | `human-followup` / `1` |
| `metadata.capture_semantics` | `transcript-ancestry` |
| Smoke environment | `claude-code-feedback-smoke` |

Additional metadata: `harness_version`, `agent_model`, `session_id`, `followup_entry_id`, `preceding_user_entry_id`, `assistant_entry_id`, `assistant_message_id`, `submission_kind` (`prompt` or `slash_command`), `submitted_at`, `interrupted_before_followup`.

How the window maps onto the transcript:

- **Genuine human row:** `type == "user"`, `origin.kind == "human"`, not `isMeta` / `isSidechain` / `isCompactSummary`, no `toolUseResult` or `tool_result` block, `entrypoint` in `cli` / `claude-desktop`, in the hook's session, with non-empty text after `<system-reminder>` blocks are removed. A typed plugin or skill command renders as `/name args` with `submission_kind = slash_command`.
- **Ancestry** follows `parentUuid`, and `logicalParentUuid` across a `compact_boundary` row.
- **Response** is the last `message.id` group with text on the path; its text blocks are joined in order.
- **Session boundary:** a session's start is recorded at `SessionStart`. A preceding request timestamped before it is copied history from a resume or fork, so the first follow-up after a resume is skipped.
- **Delivery:** Stop-triggered. A per-session timestamp cursor plus a ledger of recent entry IDs is persisted *before* emitting, which is what makes delivery at-most-once.

## Pi mapping

Exporter: the Pi `human-followup-observation` extension, which posts OTLP directly when the person submits input.

| Contract field | Pi value |
|----------------|----------|
| Name | `Pi Human Follow-up` |
| `metadata.source` | `pi-feedback` |
| Trace tags | `pi`, `pi-feedback` |
| `metadata.capture_semantics` | `input-submission` |
| Smoke environment | `pi-feedback-smoke`, per the `<source>-smoke` convention |

Pi conforms to v1 except that it does not set `metadata.harness` (nor `metadata.contract`, `contract_version`, or `submission_kind`). Its harness is implied by `source = pi-feedback`, so rules keyed on `metadata.source` work for both. Pi takes the request and response from the active branch at submission time, which is its equivalent of ancestry.

## Codex: not implemented

No Codex exporter exists, and under Codex the shared hook's follow-up pass is a no-op. Activation needs, in order:

1. Verified exporter samples from a real Codex rollout, not a synthetic fixture.
2. A genuine-human detector for Codex rollout rows that excludes injected and programmatic input, equivalent to `origin.kind == "human"`.
3. A separate evaluation rule for the Codex source, written only after 1 and 2 hold. No speculative rule is created ahead of the exporter.

## Evaluation rule template

One rule per harness. Placeholders in angle brackets; no instance IDs are kept in this repository.

| Setting | Claude Code value |
|---------|-------------------|
| Evaluator | `<EVALUATOR_ID>` |
| Target | Observations |
| Filter: name | any of [`Claude Code Human Follow-up`] |
| Filter: type | any of [`SPAN`] |
| Filter: `metadata.source` | `= claude-code-feedback` |
| Filter: `metadata.submission_kind` | `= prompt` |
| Filter: environment | none of [`claude-code-feedback-smoke`] |
| Variable mapping | `context` <- observation `input`; `followup` <- observation `output` |
| Sampling | `1` |

The Pi rule has the same shape with name `Pi Human Follow-up`, source `pi-feedback`, and environment none of [`pi-feedback-smoke`], minus the `submission_kind` filter, which Pi does not set.
