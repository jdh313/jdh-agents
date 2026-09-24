# em

Engineering-manager skills for executing tracked work. You name the work; em
scopes it, picks how to execute it, dispatches subagents, verifies their output
by diff, and stops before anything outward-facing.

There is no fixed lifecycle and no draft artifact. The ticket is the state: a
ticket that is already shaped goes straight to execution.

## Skills

| Skill | Use it for |
|---|---|
| `em:start` | Scope one ticket and stop at a brief: fetch, ground in decisions, read the touched code, ask only the questions nothing else can answer. |
| `em:lead` | Execute one or more tickets, or a milestone: check readiness, choose a shape, dispatch, verify by diff, run the review fan-out, stop before push. |

Either skill is a valid entry point. `lead` runs `start`'s scoping inline when
a ticket is not shaped, so you never need to run `start` first.

## Readiness

A ticket is **shaped** when its body has an aim line and a `Done when` slot
(`## Done when`, `## Acceptance criteria`, or the tracker's equivalent field)
with at least one bullet. That is the body the `pm` plugin writes. The check
reads the ticket, not the agent's impression of it.

## Execution shapes

`lead` picks per task from what the ticket and code show: **inline** for a
trivial edit, **one worker**, **parallel lanes** in separate workspaces,
**test-first** when every `Done when` bullet is testable, or **diagnose first**
when the cause is unknown. See `skills/lead/SKILL.md`.

## Trackers

| Tracker | Adapter | Status |
|---|---|---|
| Linear | `references/trackers/linear.md` | Uses the `linear` plugin's conventions and `linear-ops` agent when installed |
| Fibery | `references/trackers/fibery.md` | Unverified; discovers the workspace schema at runtime |
| GitHub Issues | `references/trackers/github.md` | Reads via `gh`; Projects status unverified |

The tracker comes from the reference form (`TEAM-123`, a Fibery URL,
`owner/repo#N`), else from a repo-local `.em.toml`, else one question. See
`references/config.md`.

## Composes with

All optional; each step that uses one is skipped when it is absent.

- **pm**: shapes the tickets em executes; `lead` recommends `pm:breakdown` for
  a ticket too big for one session.
- **linear**: Linear conventions and the `linear-ops` write agent.
- **ndr**: decision grounding before code, capture after.
- **workspaces**: isolated jj checkouts for parallel lanes.
- **craft**: the pre-PR reviewer fan-out.

## What it never does without asking in the same turn

Push, open or comment on a PR, merge, write to a tracker, apply infra, or
mutate anything outside the working copy.

One tracker write is pre-authorized: invoking `em:lead` on a ticket moves that
ticket to its in-progress state just before work on it begins. It never moves
a ticket backwards, and it skips trackers with no such state (plain GitHub
Issues).
