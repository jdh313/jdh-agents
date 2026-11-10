---
id: "ccnvte"
title: Export slash-command follow-ups flagged, and score only prompts
status: current
decision_date: 2026-10-15
author: Jacob Hoehler
conviction: strong
project: jdh-agents
labels:
  - scope
binds:
  - docs/langfuse-human-followup-contract.md
supersedes: []
superseded_by: []
derived_from:
  - Claude Code session a7c25421-a3b6-4e7d-a9db-f93dd575e9e0 (2026-10-15)
informed_by: []
---

# ccnvte — Export slash-command follow-ups flagged, and score only prompts

## Decision

The Claude Code exporter exports a typed slash command as a follow-up, rendered as `/name args` with `metadata.submission_kind = slash_command`. A plain typed message carries `submission_kind = prompt`. The Claude Code evaluation rule scores only `prompt` follow-ups.

## Scope

- Binds: the Claude Code follow-up exporter and the Claude Code evaluation rule.
- Does not bind: Pi, which does not set `submission_kind`.

## Commitments

- Slash-command detection keys on text that starts with `<command-message>` or `<command-name>`. A transcript format change would silently reclassify commands as `prompt` and send them to scoring.
- Any rule that scores Claude Code follow-ups filters on `metadata.submission_kind = prompt`.

## Revisit if

- A review of exported `slash_command` rows shows they carry feedback on the preceding answer as often as prompts do.
- Claude Code changes how typed commands appear in the transcript.

## Context

- Claude Code records a typed plugin or skill command as a human-origin user row wrapped in `<command-message>` / `<command-name>` tags.
- A typed command usually starts a workflow, such as a plugin update or a decision capture, rather than reacting to the previous answer.
- The evaluator judges how the previous answer landed by reading the person's next message.
- On 2026-11-10 the follow-up exporter moved to transponder, and this repository stopped carrying it when the `langfuse` plugin was retired (JUN-668).

## Why

Command invocations carry little signal about the preceding answer, so scoring them would add noise to the intervention rates. Dropping them at export would also be costly. Changing what gets exported requires a plugin release, while changing what gets scored is a rule-filter edit in Langfuse. Exporting every human submission with a flag keeps the full record and leaves the scoring choice at the rule, the cheaper place to change it.

## Alternatives

- **Skip slash commands at export** — rejected: re-including them later needs a plugin release, and the skipped period stays missing.
- **Score slash commands like prompts** — rejected: most command invocations are not reactions to the previous answer, so they would skew the rates.
