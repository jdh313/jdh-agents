# Verify

**Never trust a subagent's summary. Verify by diff, every time.** The summary
is a claim; the diff and a test run you did yourself are the evidence.

## Per dispatch

1. **Scope.** List what changed against the base:
   - jj: `jj diff -r '<base>..@' --summary` (`<base>` is usually
     `trunk()` or `main@origin`)
   - git: `git diff --stat <base>...HEAD`

   Anything outside the files the dispatch named is a finding.
2. **The load-bearing claim.** Read the actual code for the one claim the
   change stands on, not the agent's description of it.
3. **Tests.** Re-run the relevant tests yourself. An agent's "all green" is
   not a result.
4. **Done when.** Walk each `Done when` bullet and name the evidence that
   meets it: a test, a command's output, a line of code. A bullet with no
   evidence is not met.

## When sources disagree

When an agent's report contradicts a source document (a ticket, a design doc,
a decision), read both and find out which is wrong. Do not assume the agent
inverted it: a stale summary line in the document is as likely as a mistake in
the report.

## Tooling false alarms

Diagnostics from a type checker or language server that ran in the main
checkout (unresolved imports, missing modules) often do not apply to a
separate workspace. Run the tool inside the workspace before reporting a
defect.

## Before the stop

- **Review fan-out.** If the repo has a pre-PR rule (`.claude/rules/pre-pr.md`
  or similar), follow it. Otherwise, when the `craft` plugin is installed,
  dispatch `craft:house-style-reviewer`, `craft:comment-reviewer`, and
  `craft:copy-reviewer` in one message, plus `/code-review` in a fresh
  context. An empty report is a normal result; do not re-run it hunting for
  output.
- **Dispose of every finding.** Fix it, or state in the PR description why it
  stands. A finding is not resolved by being received.
- **Decisions.** Capture a decision atom (`/capture-decision`, when `ndr` is
  installed) only for a decision the branch actually made. Copying an
  established pattern makes no new decision.
