---
name: session
description: >-
  End-of-session feedback report for plugin testers. This skill should be used
  when the user invokes `/feedback:session`, says "session feedback", "wrap up
  this test", "what worked and what didn't", "write up testing feedback", or
  otherwise signals the end of a session spent exercising Claude Code plugins
  (skills, slash commands, subagents, hooks) and wants a report to hand back to
  the plugin author. Analyzes ONLY the current session transcript, asks no
  questions, and emits a single copy-pasteable report block — grading each
  plugin surface that was exercised and citing concrete evidence for every
  claim — in the shared format that the `feedback:triage` skill can aggregate.
argument-hint: ""
---

# Session feedback

You are wrapping up a session in which the user was **testing Claude Code
plugins** — skills, slash commands, subagents, and hooks. Your job is to turn
the session transcript into a feedback report the user can hand back to the
plugin author so they can improve the plugins.

The report follows a shared contract so the author can run `feedback:triage`
over many reports at once and cluster findings. **Emit exactly the format in
`../../references/report-format.md`** — the surface table and the per-finding
`[surface] severity/category` tags are load-bearing, not decoration.

## Hard rules

- **Ask no questions.** Work entirely from this session's transcript. If
  something is ambiguous, say so in the report rather than asking or guessing.
- **Evidence over impression.** Every "worked" claim needs a concrete example
  from the session; every finding needs the actual ask-vs-behavior. No padding,
  no invented verdicts.
- **Honest, not flattering.** The author wants to find problems. Skip praise
  that isn't tied to a specific moment.
- **Scope to the plugins.** Judge the plugin surfaces (skills / commands /
  subagents / hooks), not the underlying model.
- **Tag every surface and finding.** Use the `<plugin>:<surface>` id grammar
  from the reference. If a plugin can't be determined, use `?:<surface>` —
  never drop the prefix, since `triage` groups on it.
- **Output one block, then stop.** End after the fenced report. Nothing else.

## Procedure

1. **Inventory what got exercised.** List every plugin skill, slash command,
   subagent, or hook that was invoked or triggered this session, by
   `<plugin>:<surface>` id. Also flag any that the user clearly expected to fire
   but didn't (a `trigger` finding), or that fired when unwanted.

2. **Detect the environment** (no questions — best effort from what's already
   available):
   - If the cwd is a git repo, capture `<repo-name> @ <short-sha>` from the
     session's git context or a `git rev-parse --short HEAD`.
   - Note the repos whose plugins were exercised when discernible (a surface's
     repo is often visible in its file paths or the plugin id).
   - If none of this is determinable, write `unknown`.

3. **Judge each surface against the transcript** and assign a table verdict:
   - `✅` worked — triggered at the right time; output correct, useful, and in
     the expected shape; saved steps.
   - `⚠️` mixed — worked but with rough edges, or only sometimes.
   - `❌` broke — misfired, produced wrong/confusing output, or the user
     corrected it, re-prompted, or abandoned it.

4. **Write each finding** as a tagged line. Pick the severity (`blocker` /
   `major` / `minor`) and the category (`trigger` / `output` / `defaults` /
   `friction` / `docs` / `missing`) per the reference, then cite the concrete
   moment after the `—`. Capture friction, not just features: where the user
   repeated themselves, re-clarified, fought the tool, or where the agent
   guessed intent wrong.

5. **Note what worked well** — tied to specific moments — and add **Suggested
   fixes** only where the fix is obvious from the failure.

## Output

Emit exactly one fenced report block in the format defined by
`../../references/report-format.md`. Keep it scannable — bullets over prose.
After the block, stop.

## References

- **`../../references/report-format.md`** — the report contract this skill
  emits and `feedback:triage` parses. Single source of truth for the block
  structure, surface-id grammar, verdicts, and the severity/category tags.
