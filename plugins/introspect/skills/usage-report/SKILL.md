---
name: usage-report
description: Summarize how you (or whoever runs it) work with Claude Code in a repo — which skills, slash commands, subagents, and MCP tools you use, how you kick off tasks, plan-mode usage, and activity over time. Use when someone says "claude usage report", "how do I use Claude here", "analyze my Claude Code workflow", "summarize my sessions", or is asked by a teammate to share their workflow stats. Runs from Claude Code or Codex, but reads only Claude Code's local transcripts. Privacy-safe by default (names + counts only; no prompt text leaves the machine).
---

# Claude Code usage report

## Supported runtime scope

This skill can be invoked from either Claude Code or Codex. In both cases it
inspects Claude Code transcripts under `~/.claude/projects/` only. It does not
parse Codex rollout files under `~/.codex/sessions/`, and it makes no claim that
the Claude metrics describe Codex usage or provide token-cost accounting.

Reconstruct a person's Claude Code workflow in a repo from their **local** session
transcripts, then narrate it. The deterministic crunching is done by the bundled
`scripts/claude-usage-report.py` (stdlib-only, read-only, no network); your job is to run
it and turn the numbers into a short, honest read of how they work.

## When to run

- A teammate asked the user to share how they drive Claude in a repo.
- The user wants to see their own patterns ("how do I use Claude here").
- Onboarding or workflow-comparison across a team.

## Privacy contract — state this up front

This reads the user's **own** transcripts under `~/.claude/projects/`. It is per-user and
per-machine — it cannot see anyone else's sessions. By default the report contains only
**names, counts, and dates** — never prompt text, command arguments, skill arguments, or
subagent prompts. The `--include-args` flag opts into surfacing (truncated) argument
strings, which CAN contain ticket context and prose. Only pass it if the user explicitly
wants that and understands the output may be shared. Confirm before using `--include-args`.

## Procedure

1. **Scope.** By default the parser scopes to the **current directory's name** (matched as a
   case-insensitive substring against slugified project-dir names under `~/.claude/projects/`),
   so running it from inside the target repo Just Works. Pass `--repo <keyword>` to override, or
   `--all` to span every project.

2. **Run the parser** — from inside the repo being analyzed, no flags needed:

   Resolve [the bundled script](scripts/claude-usage-report.py) relative to this
   loaded `SKILL.md` file. Run `python3` with that absolute path, quoted for
   spaces, while keeping the analyzed repository as the working directory.
   The path comes from the loaded skill location, not a shell environment variable.

   By default it **saves** to the analyzed repo's `.claude/usage-reports/usage-report.md`
   (repo root inferred from the sessions' own `cwd`) and drops a `.gitignore` there so the
   report is never committed. It prints the saved path — read that file for the full report.

   Useful flags:
   - `--repo <keyword>` — override the scope (default: current directory name).
   - `--since YYYY-MM-DD` — scope to a recent window.
   - `--all` — every project dir, ignoring `--repo`.
   - `--json` — full structured payload (nested dicts) for programmatic use.
   - `--csv` — tidy long-format CSV (`section,key,metric,value`); one file that pivots cleanly in pandas/Excel.
   - `--stdout` — print to the terminal instead of saving a file.
   - `--out PATH` — save to an explicit path instead of the in-repo default.
   - `--projects-dir PATH` — if history lives somewhere other than `~/.claude/projects`.
   - `--include-args` — ONLY after explicit user consent (see privacy contract).

3. **Read** the saved markdown report (the path printed in step 2).

4. **Narrate** — write a tight summary (do NOT just re-dump the tables). Cover:
   - **Kickoff style:** ratio of bare-prompt vs slash-command vs plan-mode starts. What is
     their typical opening move?
   - **Skill fingerprint:** which skills dominate by *depth* (`attributionSkill` — actions
     performed under a skill), not just invocation count. This is the truest signal of how
     they actually work (e.g. heavy `spec-flow:*` = contract-driven; heavy `ndr:*` =
     decision-grounded).
   - **Subagent habits:** do they delegate (which agent types) or work solo?
   - **Tooling & MCP:** Linear-driven? Figma? Context7? Web research?
   - **Cadence:** active days, sessions/day, worktree usage, branches touched.
   - **One-paragraph characterization** of their workflow in plain language.

5. **Offer next steps:** save the narrative alongside the raw report, or (with consent)
   re-run with `--include-args` for a deeper look. If sharing with a teammate, the markdown
   file is the artifact to send back.

## Notes

- No dependencies, no network calls — safe to run anywhere Python 3.9+ exists.
- Subagent-internal tool calls are read from each parent session's
  `subagents/*.jsonl` files. The tool table separates main-thread and subagent calls, and
  the per-agent table counts unique assistant turns by `agentId`.
- The parser intentionally excludes prompt text, command bodies, tool inputs and
  outputs, hidden reasoning, and model token usage from its default report.
- If "No transcripts found" prints, history may be under a different path — pass
  `--projects-dir` or try `--all` to confirm what exists.
