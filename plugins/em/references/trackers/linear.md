# Tracker: Linear

Read this when the resolved tracker is `linear`. It says **how to address
Linear**. Ticket conventions (team, labels, priority, status vocabulary, MCP
gotchas) belong to the `linear` plugin; read its skill when it is installed
rather than restating it here.

## Identity

`TEAM-123`. A `https://linear.app/<org>/issue/TEAM-123/...` URL carries the
same identity: record the key, keep the URL alongside it.

## Fetch

1. `mcp__linear-server__get_issue` for the key: title, description, state,
   labels, assignee, parent.
2. `mcp__linear-server__list_comments` for the issue. Read every comment; a
   scope change often lives in one.
3. Relations (blocks, blocked by, related, duplicate) from the issue record.
   Fetch each blocking and related issue's title and state. Scope boundaries
   between sibling tickets are often deliberate.

## Readiness fields

The body follows the `pm` plugin's issue-body spec when it was authored there:
an aim line, then optional `## Why now`, `## Sketch`, `## Done when`,
`## Context`. Tickets written by hand may use `## Acceptance criteria` instead
of `## Done when`; treat the two as the same slot.

## State changes

Never hardcode a state name; states are team-scoped. Resolve at write time with
`mcp__linear-server__list_issue_statuses`, matching case-insensitively. Write
with `mcp__linear-server__save_issue(id, state)`: one field per call, never a
whole description.

`em` never writes a completed-type state (Done, Canceled). Where merge
automation is wired, merging does that.

## Writes go through `linear-ops` when present

If the `linear` plugin is installed, dispatch its `linear-ops` agent for every
write so its identifier lookups and silent-failure workarounds apply. Every
Linear write is outward-facing: confirm it with the user in the same turn. The
one exception is `em:lead` marking the ticket it was invoked on as in
progress; invoking it is the consent. That single-field write calls
`save_issue` directly (pre-approved in `lead`) rather than dispatching
`linear-ops`, which would cost a subagent for one field.

## A trap

A branch name containing a ticket key can auto-transition that ticket (push to
In Review, merge to Done) when the team has the GitHub integration on. Never
name a branch after a ticket it does not close.
