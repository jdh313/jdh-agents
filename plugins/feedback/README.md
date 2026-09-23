# feedback

A two-sided loop for improving agent plugins from real test sessions. Runs in
any runtime that hosts the plugin — reports name surfaces by what they are for
(`skill` / `delegate` / `hook`), so a Claude Code session and a Codex session
produce the same shape and triage the same way.

- **Testers** run `/feedback:session` to emit one copy-pasteable report.
- **Anyone** runs `/feedback:jot` to file a quick note or idea about a
  single surface mid-session — a plugin surface, or setup outside plugins
  (rules, `CLAUDE.md`, user-level skills, settings).
- **The author** runs `/feedback:triage` over a pile of those reports to get a
  prioritized, routed action plan.

All three skills agree on one contract — `references/report-format.md` — so the
report a tester sends is the same structure the author aggregates. That shared
format is what makes the loop work: the tester gets a clean block, the author
gets something machine-clusterable instead of prose to read by hand.

## Skills

### `session` — `/feedback:session` (tester side)

End-of-session feedback report. Analyzes **only the current session
record**, asks no questions, and emits a single fenced report block that
grades each plugin surface (skill / delegate / hook) the tester
exercised and cites concrete evidence for every claim.

**Use it at the end of a test session.** A tester runs `/feedback:session`,
copies the block, and sends it to the plugin author.

The report contains:

- **A surfaces table** — each surface as a `plugin:surface` id, its kind, repo,
  and a `✅ worked / ⚠️ mixed / ❌ broke` verdict
- **Findings** — each tagged `[surface] severity/category` (severity ∈
  blocker/major/minor; category ∈ trigger/output/defaults/friction/docs/missing)
  with the actual ask-vs-behavior
- **Worked well** — claims tied to concrete moments
- **Suggested fixes** — only where the fix is obvious

It works across plugins from multiple repos and records which repo a surface
came from when discernible, plus an `Environment` line so the author knows which
version was tested.

### `jot` — `/feedback:jot` (either side)

Quick capture for one surface. `/feedback:jot spec-flow:capture asks too many
questions` writes a *jot*: a short note shaped by the Obsidian vault's
conventions, not a report block. Frontmatter carries every triage field
(`type: agent-feedback`, `owner: ai`, `status`, `surface`, `kind`, `repo`,
`version`, `severity`, `category`, runtime/environment metadata, and a topic
tag, and a one-sentence `summary`); the body renders the summary with
`` `= this.summary` `` as meeting notes do, then `## User Feedback` with the
user's words in full (any fix they propose included), and `## Context` with
what was happening in the session when it came up. It asks no questions: the
surface comes from the argument or from what just ran, and an idea files as a
`minor/missing` finding.

`/feedback:triage <jot folder>` reads jots from their frontmatter, skipping any
whose `status` is no longer `open`.

**Where jots go** is the plugin option `jot_dir` (Claude Code `userConfig`), an
absolute path set per machine in `pluginConfigs["feedback@jdh-agents"].options`
of the user `settings.json`, or through `/config`. Point it at a synced folder
(an Obsidian vault folder works) to collect jots from several machines in one
place. Unset, and always on Codex (which has no `userConfig`), jots land in
`.docs/feedback/jots/` under the current repo.

### `triage` — `/feedback:triage` (author side)

Turns many reports into one action plan. Ingests reports from a directory of
`.md` files, a single file, or blocks pasted into the conversation; parses them
against the shared format; clusters findings by surface and category; ranks by
severity × corroboration; and routes each cluster to a concrete actuator:

| Finding category | Routed to |
| --- | --- |
| `trigger` | `description:` trigger tuning, or a `hookify` rule |
| `output` | `skill-improver` loop, or a targeted body edit |
| `defaults` | a specific body edit |
| `friction` | fewer questions / better defaults in the body |
| `docs` | `description:` / README / `argument-hint` edit |
| `missing` | a new skill via `plugin-dev:create-plugin`, or a feature |

It **proposes** the plan and offers handoffs (run skill-improver, draft the
edits, write the hook, open tickets) — it never applies fixes on its own.

## The loop

1. Tester exercises plugins, runs `/feedback:session`, sends the block.
2. Author collects reports (drop them in a folder).
3. Author runs `/feedback:triage <folder>`, reviews the punch list.
4. Author picks fixes; triage hands the top item off to the right tool.

## Team usage

When multiple testers share a repo, each tester runs `/feedback:session`
independently at the end of their own session. The report header identifies
the tester by name so reports arriving out of order are still distinguishable.

To leave a persistent record, ask to save the report:
`/feedback:session` then "save the report" (or `--save`). Reports land at
`.docs/feedback/<date>-<tester>.md`, which is collision-free across testers
and committable. Designate one tester per round, or have each tester save and
commit their own file.

## Requirements

Testers need this plugin installed and enabled for `/feedback:session` to
appear. If it isn't, the same workflow can be pasted in as a plain prompt. The
author needs it for `/feedback:triage`.
