---
name: em-scope
description: >-
  Scope one tracked ticket read-only in Pi; fetch all comments, ground
  decisions, inspect code, ask only genuine forks, and stop at an approval
  brief. Use /skill:em-scope for a plan without execution.
---
# EM scope in Pi

Read `../../pi/runtime.md` and `../../pi/trackers.md` first. Their Pi
capability and tracker procedures govern this workflow; do not use
Claude tool names or assume a plugin is installed from its source tree.

**Read-only:** write no code, config, decisions, report files, or tracker
state; do not dispatch editing workers. Produce the brief in chat.

1. Resolve the supplied ticket using `../../references/config.md`
   (reference form, then repo-root `.em.toml`, then ask in chat).
   Follow the resolved tracker procedure in `../../pi/trackers.md`:
   title, full body, every comment, and linked/blocking titles/states.
   Unresolved reference or unavailable reads: report the gap and stop.
2. Ground in current decisions using the available NDR procedure per
   `../../pi/runtime.md`; keep governing `ndr:` references. When absent,
   explicitly note skipped grounding.
3. Read touched symbols, surrounding conventions and tests, root and
   applicable nested `AGENTS.md` / `CLAUDE.md`, and applicable repository
   rules (including `.claude/rules/*.md`; Pi does not auto-load these).
4. Ask only questions the ticket/comments, current decisions, governing
   rules, and code precedent cannot answer. Genuine product/scope forks,
   externally visible design choices, destructive calls, and requirements
   gaps qualify. Recommend an option first; zero questions is normal.
5. Present files/symbols, approach, sequencing, defensible defaults taken,
   Done when bullets (label derived criteria), and grounding references.
6. **Stop for approval.** On go-ahead, load the available `em-lead` skill
   by its advertised path, or hand off the brief; do not implement here.

When lead scopes inline, it performs steps 1–5 without this final stop;
genuine forks still require an answer before execution.
