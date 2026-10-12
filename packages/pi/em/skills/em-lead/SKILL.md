---
name: em-lead
description: >-
  Engineering-manager orchestration for tracked work in Pi; check observable
  readiness, scope inline if needed, dispatch available workers, verify diffs
  and tests, and stop before push/PR/merge. Use /skill:em-lead.
---
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
5. Dispatch and collect per `../../pi/dispatch-verify.md`. Parallel lanes
   run in the background with separate provider-bound checkouts. Never
   dispatch whole-repo generators/formatters concurrently.
6. Verify actual diff/code, rerun relevant tests yourself, match every
   criterion to evidence, and dispose of review findings. Correction of
   a completed workspace child must follow the explicit stop/manual
   recovery in that adapter, not an invented same-agent resume.
7. Report files/revisions, criterion evidence, findings/dispositions,
   captured decisions and blocked checks. **Stop before push, PR, merge,
   or any further tracker write.** Request separate same-turn approval.
