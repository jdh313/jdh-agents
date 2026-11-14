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
  with no execution, use `em:scope`.
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
targets:
  pi:
    name: em-lead
    description: Engineering-manager orchestration for tracked work in Pi; check observable readiness, scope inline if needed, dispatch available workers, verify diffs and tests, and stop before push/PR/merge. Use /skill:em-lead.
    body: |
      # EM lead in Pi

      The user prioritizes; you orchestrate. Decide shape, agent, model, slices,
      blockers and review dispositions; escalate only genuine forks or calls
      binding future work. Stay quiet during runs; report multi-item state in
      a table (landed, in flight, next). Flag your mistakes immediately. Do not
      implement directly except edits too small to justify dispatch.

      Read `../../pi/runtime.md`, `../../pi/trackers.md`, and
      `../../pi/dispatch-verify.md` before work. These are executable Pi adapters,
      not promises that Claude tools, roles, or hooks exist.

      ## Hard boundaries

      Require the user's approval **in the same turn**, separately for push,
      opening/commenting on a PR, merge, tracker writes, infra applies, cloud
      or production mutations, and destructive actions (prefer trash to rm).
      The only tracker exception: lead invoked on a named ticket authorizes
      that ticket's one-field in-progress transition just before work starts.
      For an invoked milestone, this applies to its resolved tickets one at a
      time as each begins, not unrelated discovered work. Never move backwards
      or complete/cancel/close an issue. Permissions are not consent; Pi skill
      metadata enforces none of these boundaries. Pass them to every child.

      1. With no work reference, ask which work in chat. Otherwise resolve via
         `../../references/config.md` and fetch full records/comments/relations
         per `../../pi/trackers.md`. For a milestone/project, read its open
         tickets and order by blocking relations.
      2. Read readiness from the body: an aim line plus a Done when/Acceptance
         criteria heading or equivalent tracker field with at least one bullet
         means **shaped**. Go straight to preparation; do not ask answered
         questions. Otherwise read `../em-scope/SKILL.md` and run steps 1–5
         inline, without its final stop. Ask genuine forks before continuing.
         Too large for one sonnet session/several surfaces: recommend slicing
         first, using available PM breakdown content per runtime adapter; do
         not create/slice tickets yourself.
      3. Ground decisions and read governing instructions. Before editing,
         establish isolation/readiness and a fresh base per runtime adapter.
         Do not move a checkout another session is writing. Immediately before
         first dispatch/inline edit, resolve and set only the authorized
         ticket's in-progress field per tracker adapter, or explain the skip.
      4. Choose a shape from evidence: inline (one file/few lines/known cause),
         one coherent worker, parallel disjoint-file lanes, test-first (all
         criteria testable and a repo test command: failing tests from criteria
         alone, then implementation), or read-only diagnosis before a fix.
         Give the reason in one line. Isolation is mandatory for editing work;
         missing readiness is a blocker, not permission to use parent cwd.
      5. Settle design calls before any implementation dispatch: list choices
         with more than one defensible answer that change what an implementer
         writes. One the brief, ticket, comments or a current ndr head answers
         is settled (cite it) and never a reason for a stronger worker. Settle
         open ones inline (small) or via one design-only worker, read-only
         except the design file (large); ask the user on a genuine fork. Write
         each answer and source to `<TICKET>-design.md` in the session scratch
         path, never the repo; name it in every implementation dispatch; route
         calls binding future work to NDR capture. Size implementers by the
         remaining work.
      6. Dispatch and collect per `../../pi/dispatch-verify.md`. Parallel lanes
         run in the background with separate provider-bound checkouts. Never
         dispatch whole-repo generators/formatters concurrently.
      7. Verify actual diff/code, rerun relevant tests yourself, match every
         criterion to evidence, and dispose of review findings. Correction of
         a completed workspace child must follow the explicit stop/manual
         recovery in that adapter, not an invented same-agent resume.
      8. Report files/revisions, criterion evidence, findings/dispositions,
         captured decisions and blocked checks. **Stop before push, PR, merge,
         or any further tracker write.** Request separate same-turn approval.
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
- **Not shaped:** run `../scope/SKILL.md` steps 1 to 6 inline, then continue.
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

## 5. Settle design calls

Settle every design call before any implementation dispatch, so a worker is
picked for the work that remains, not for the design.

1. **List the design calls** the work contains: choices with more than one
   defensible answer that change what an implementer writes, such as module
   layout, interface shape, where a lock goes, or refusal order.
2. **A call is settled** when the brief, the ticket, its comments, or a current
   `ndr` head already answers it. Cite the source. A settled call is never a
   reason to pick a stronger worker.
3. **Settle each open call** before dispatching:
   - A small call: settle it yourself, inline.
   - A large one: dispatch one design-only worker (per
     `../../references/dispatch.md`), read-only except for the design file,
     whose deliverable is the design file.
   - A genuine fork with no defensible default is not yours to settle: ask the
     user, per operating rule 2.
4. **Write the result** to `<TICKET>-design.md` in the session scratchpad (where
   dispatch report files go), never the repo. Give each call its answer and its
   source. Every implementation dispatch names that file as an input. A call
   that binds future work also goes to `/capture-decision`.
5. **Then pick implementers per lane**, sized by the remaining work.

## 6. Dispatch

Write every dispatch per `../../references/dispatch.md`: goal, inputs,
governing rules, workspace, guardrails, done criteria, and a report file.

## 7. Verify

Per `../../references/verify.md`: scope diff, the load-bearing claim, tests
re-run yourself, and each `Done when` bullet matched to evidence. A failed
check goes back to the same agent with the evidence, or to a stronger one if
the cause is beyond it.

Then run the review fan-out and dispose of every finding, per the same file.

## 8. Stop before anything outward-facing

Report the state: what landed (commits, files), how each `Done when` bullet is
met, findings and their disposition, and the decisions captured. Then ask
before pushing, opening a PR, or moving the ticket. Pushing and PR-opening are
always the user's to authorize.
