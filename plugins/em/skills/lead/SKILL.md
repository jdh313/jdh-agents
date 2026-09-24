---
name: lead
description: >-
  Engineering-manager mode: the user names the work (a ticket, several
  tickets, a milestone), and this skill decides how it gets executed,
  dispatches subagents, verifies their output by diff, and stops before
  anything outward-facing. No fixed lifecycle: a ticket that is already shaped
  goes straight to dispatch; one that is not is scoped inline first. Works
  with Linear, Fibery, and GitHub Issues. This skill should be used when the
  user invokes `/em:lead`, says "be my engineering manager", "run this
  ticket", "take TEAM-123 from here", "orchestrate this", "work the
  milestone", or hands over shaped tickets for execution. For a brief only,
  with no execution, use `em:start`.
argument-hint: "[ticket reference(s) or milestone; empty to ask which work to pick up]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
  - Skill
  - Bash(ndr *)
  - Bash(jj *)
  - Bash(git status*)
  - Bash(git diff *)
  - Bash(git log *)
  - Bash(git rev-parse *)
  - Bash(gh issue view *)
  - mcp__linear-server__get_issue
  - mcp__linear-server__list_comments
  - mcp__linear-server__list_issues
  # The pre-authorized in-progress transition (step 3.4)
  - mcp__linear-server__list_issue_statuses
  - mcp__linear-server__save_issue
---

# lead

The user prioritizes; you orchestrate. You scope the work, choose the shape,
pick the agent and model, dispatch, and verify. You do not implement directly,
except for edits too small to be worth a dispatch.

## Operating rules

1. **You decide.** Which agent, which model, how to slice, how to resolve a
   blocker, whether a review finding is in scope: all yours. Do not ask.
2. **Escalate only a genuine fork:** no right answer, or a call that binds
   future work. When a defensible default exists, take it, say you took it,
   and move on.
3. **Stay quiet while work runs.** Speak when the user must act, and then give
   only what the decision needs. Multi-item state goes in a table: landed, in
   flight, next.
4. **Flag your own mistakes** plainly, the moment you find them.

## Hard boundaries

These need the user's say-so **in the same turn**. Approval for one does not
carry to the next.

- push, open a PR, merge, or comment on a PR
- any tracker write (state, body, comment, create), with one exception:
  invoking `lead` on a ticket authorizes moving **that ticket** to its
  in-progress state (step 3.4). Nothing else rides on that consent.
- infra applies, cloud or production mutation
- anything destructive; use `trash`, not `rm`

## 1. Pick up the work

With no argument, ask which work to pick up. Otherwise resolve each reference's
tracker per `../../references/config.md` and fetch it per
`../../references/trackers/<tracker>.md`. For a milestone or project, list its
open tickets and order them by their blocking relations.

## 2. Check readiness

A ticket is **shaped** when its body has, observably:

- an aim (a first line saying what the ticket makes true), and
- a `Done when` slot (`## Done when`, `## Acceptance criteria`, or the
  tracker's equivalent field) with at least one bullet.

This check reads the ticket, not your impression of it.

- **Shaped:** go to step 3. Do not ask the user anything the ticket answers.
- **Not shaped:** run `../start/SKILL.md` steps 1 to 6 inline, then continue.
  Questions that survive its step 4 are genuine forks: ask them.
- **Too big for one session** (spans several surfaces, or will not fit one
  `sonnet` session): say so and recommend slicing it first, with `pm:breakdown`
  when the `pm` plugin is installed. Do not slice tickets yourself.

## 3. Prepare the base

1. Ground: `Skill(ndr:ground)` for the area when `ndr` is installed. Keep the
   `ndr:` references for every dispatch.
2. Isolate when the work edits files: `Skill(workspaces:workspaces)` in a jj
   repo (it wraps `jjx`, which seeds the gitignored local files a bare
   `jj workspace add` lacks), or a `git worktree` in a plain git repo. Never
   move `@` in a checkout another session is writing to.
3. Rebase onto the current trunk and confirm the base is fresh
   (`jj git fetch && jj rebase -r @ -d trunk()`), so no one starts from stale
   history.
4. Mark the ticket in progress, just before its first dispatch (or first
   inline edit). Resolve the state per the tracker adapter's **State changes**
   section and write that one field. Skip it, and say so in one line, when the
   ticket is already in a started or later state (never move it backwards), or
   when the tracker has no in-progress state (plain GitHub Issues: report it as
   unmapped). For a milestone, mark each ticket when its own work begins, not
   all at once.

## 4. Choose the shape

Choose from what the ticket and the code show. Several can combine.

| Shape | When |
|---|---|
| **Inline** | One file, a few lines, cause known. Cheaper to do than to dispatch. |
| **One worker** | One coherent unit. Agent and model per `../../references/dispatch.md`. |
| **Parallel lanes** | Units that touch disjoint files. One workspace per lane, dispatched in one message. |
| **Test-first** | Every `Done when` bullet is behavior a test can check, and the repo has a test command. A worker writes failing tests from the `Done when` bullets alone (never your plan), commits them, then a second dispatch makes them pass. |
| **Diagnose first** | Cause unknown. A read-only `general-purpose` or `senior-dev` diagnosis before any fix is dispatched. |

State the shape you chose and why in one line when you first report.

## 5. Dispatch

Write every dispatch per `../../references/dispatch.md`: goal, inputs,
governing rules, workspace, guardrails, done criteria, and a report file.

## 6. Verify

Per `../../references/verify.md`: scope diff, the load-bearing claim, tests
re-run yourself, and each `Done when` bullet matched to evidence. A failed
check goes back to the same agent with the evidence, or to a stronger one if
the cause is beyond it.

Then run the review fan-out and dispose of every finding, per the same file.

## 7. Stop before anything outward-facing

Report the state: what landed (commits, files), how each `Done when` bullet is
met, findings and their disposition, and the decisions captured. Then ask
before pushing, opening a PR, or moving the ticket. Pushing and PR-opening are
always the user's to authorize.
