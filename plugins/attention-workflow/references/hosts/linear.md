# Host: Linear

Read this when `issue.host` is `linear`. It says **how to address Linear**.
*When* to project is in SKILL.md; *whether* is in the grant.

## Identity

`TEAM-123`. An issue URL of the form `https://linear.app/<org>/issue/TEAM-123/...`
carries the same identity — record the key, keep the URL alongside it.

## Conventions live in the `linear` plugin

Team, status vocabulary, label rules, priority defaults, and comment shape are
that plugin's, not this one's. Read its skill rather than restating it here; a
second copy of a vocabulary drifts from the first. This file covers only what
that plugin does not: how a workflow phase reaches a Linear state.

## Resolving a state name

Never hardcode a state. States are team-scoped, so resolve at write time:

1. `mcp__linear-server__list_issue_statuses` for the issue's team.
2. Match this project's configured name case-insensitively.
3. On no match, fall back to the first status whose type is `started` (for the
   implement projection) and to nothing at all for review.
4. Record what resolved, so a later card reports the real state name.

The configured names come from `config.json` and default to Linear's own:

| Phase | Configured name |
|---|---|
| implement | `In Progress` |
| verify | `In Review` |

## What Linear can express

- **In Progress** — a `started`-type state. Available on every team.
- **In Review** — `In Review` in the default vocabulary; some teams use
  `Code Review` or `Ready for Review`. Resolution handles the variants.
- **A comment** — for the exception and outcome projections.

## What this workflow never writes here

`Done`, `Canceled`, or any `completed`-type state. Linear advances to Done on
merge into main where that automation is wired, and this workflow's delivery
boundary is commit or push, not merge — so writing Done at Close would mark an
issue complete while the branch is still open. If a project genuinely has no
merge automation, that is a `terminal_owner` of `manual`, not a reason to write
it from here.

## Writing

`mcp__linear-server__save_issue(id="TEAM-123", state="<resolved name>")`.

One field, one call. Never send a whole description back — that is the
contract-document path in `spec-flow`, and it is not what a status projection
does.
