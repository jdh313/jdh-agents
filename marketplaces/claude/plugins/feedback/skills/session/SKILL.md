---
name: session
description: >-
  End-of-session feedback report for plugin testers. This skill should be used
  when the user invokes `/feedback:session`, says "session feedback", "wrap up
  this test", "what worked and what didn't", "write up testing feedback", or
  otherwise signals the end of a session spent exercising agent plugins (skills,
  delegates, hooks) and wants a report to hand back to the plugin author.
  Analyzes ONLY the current session record, asks no questions, and emits a
  single copy-pasteable report block — grading each plugin surface that was
  exercised and citing concrete evidence for every claim — in the shared format
  that the `feedback:triage` skill can aggregate.
argument-hint: '[--save]'
allowed-tools:
  - Bash(git rev-parse *)
  - Bash(date *)
---

# Session feedback

You are wrapping up a session in which the user was **testing agent plugins** —
skills, delegates, and hooks. Your job is to turn
the session record into a feedback report the user can hand back to the
plugin author so they can improve the plugins.

The report follows a shared contract so the author can run `feedback:triage`
over many reports at once and cluster findings. **Emit exactly the format in
`../../references/report-format.md`** — the surface table and the per-finding
`[surface] severity/category` tags are load-bearing, not decoration.

## Hard rules

- **Ask no questions.** Work entirely from this session's own record — whatever
  the runtime gives you of the conversation so far. If
  something is ambiguous, say so in the report rather than asking or guessing.
- **Evidence over impression.** Every "worked" claim needs a concrete example
  from the session; every finding needs the actual ask-vs-behavior. No padding,
  no invented verdicts.
- **Honest, not flattering.** The author wants to find problems. Skip praise
  that isn't tied to a specific moment.
- **Scope to the plugins.** Judge the plugin surfaces (skills / delegates /
  hooks), not the underlying model or the runtime hosting them.
- **Tag every surface and finding.** Use the `<plugin>:<surface>` id grammar
  from the reference. If a plugin can't be determined, use `?:<surface>` —
  never drop the prefix, since `triage` groups on it.
- **Output one block, then stop.** End after the fenced report. Nothing else.

## Procedure

1. **Collect session metadata** (no questions — best effort from what's
   available):
   - Current date and time — use the session's `currentDate` if injected by the
     harness, else `date -u +"%Y-%m-%dT%H:%M:%SZ"`.
   - Repo and branch/commit of the repo under test: `git rev-parse --abbrev-ref HEAD`
     and `git rev-parse --short HEAD` (read-only). If not in a git repo, write `n/a`.
   - Tester identity: use the session's known user identity (harness environment
     or earlier in the conversation). If unresolvable, write `[TESTER NAME]` as a
     clearly-marked placeholder.
   - Runtime: which agent this session is running in. Name it as the runtime
     calls itself; write `unknown` rather than guessing.

2. **Inventory what got exercised.** List every plugin surface that was invoked
   or triggered this session, by `<plugin>:<surface>` id — every skill (whether
   the agent chose it or the user invoked it by name), every delegate dispatched
   to its own context, and every hook fired by an event. Also flag any that the
   user clearly expected to fire but didn't (a `trigger` finding), or that fired
   when unwanted.

3. **Judge each surface against what actually happened** and assign a table verdict:
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
`../../references/report-format.md` — including the `Tester:` and session
metadata header fields. Keep it scannable — bullets over prose. After the
block, stop.

## Optional file delivery

After emitting the copy-pasteable block above, **only if the user asked to
save it** (e.g. "save the report", "write it to a file", `--save`):

1. Derive a filename: `<YYYY-MM-DD>-<tester-slug>.md` where `<tester-slug>` is
   the tester name lowercased with spaces replaced by hyphens (e.g.
   `2026-06-18-alice.md`). Use `[tester]` as the slug when the name is unknown.
2. Write the report to `.docs/feedback/<filename>` inside the repo under test.
   Create the `.docs/feedback/` directory if it does not exist.
3. Confirm the path written. The default behavior (no save flag) is always the
   copy-pasteable block only — never write a file silently.

## References

- **`../../references/report-format.md`** — the report contract this skill
  emits and `feedback:triage` parses. Single source of truth for the block
  structure, surface-id grammar, verdicts, and the severity/category tags.
