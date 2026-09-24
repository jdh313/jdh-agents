# Dispatch

How `lead` hands a unit of work to a subagent. Assume an agent will do anything
the dispatch did not forbid.

## Picking the agent

| Work | Agent |
|---|---|
| Bounded fix, known cause, at most three files, or a change that copies an existing pattern | `junior-dev` |
| Four or more files, a design call, a migration, or an unknown cause | `senior-dev` |
| Diagnosis or review with no edits | `general-purpose` |
| Bulk reading where only the conclusion matters | `bulk-reader` when installed, else `Explore` |

If a named agent is not installed, use `general-purpose` with the same
guardrails. Say which substitution you made.

## Picking the model

**`haiku` is the default, not the fallback.** Reach for `sonnet` only when the
unit genuinely needs judgment: an unknown cause, a design call, cross-cutting
work. Go past `sonnet` only when the user says so. Verification by diff is what
makes the cheap default safe, so never skip it because the model was cheap.

## Every dispatch prompt names

1. **The goal:** one outcome, stated as what becomes true.
2. **Inputs:** the ticket's `Done when` bullets verbatim, the files and symbols
   involved, and the `ndr:` references from grounding.
3. **Governing rules:** read the repo's `.claude/rules/*.md` that cover the
   area yourself, and paste the relevant constraint into the prompt. A rule the
   agent was not told about is a rule it will break.
4. **Where to work:** the workspace path, when the work is isolated.
5. **Guardrails:** what not to touch (files, directories, other tickets'
   scope), what not to run (push, open or comment on a PR, merge, infra
   applies, any cloud or tracker mutation), and what to escalate instead of
   deciding.
6. **Done criteria:** the checks the agent runs before reporting.
7. **The deliverable is a file.** Name a report path (in the session
   scratchpad when one exists). Tell the agent to write its full report there
   and reply in at most 8 lines: status, commits, one-line summary, report
   path. State the reason: long final messages get lost.

## Parallel work

Send independent dispatches in one message so they run concurrently. Two
agents that edit the same files will overwrite each other; give each its own
workspace (the `workspaces` plugin's `jjx open <slug>` in a jj repo, a
`git worktree` in a plain git repo), and never let a parallel agent run a
whole-repo generator or formatter.

## When a report does not arrive

Check the report file and the VCS log before chasing: the work is usually
done. If a chase is needed, say "resend, do not redo" and name what you want.
If the agent goes idle again, send: `write it to <path>, then reply with one
line`. No verdict is better than an invented one.
