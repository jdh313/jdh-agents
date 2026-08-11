# Host: GitHub Issues

Read this when `issue.host` is `github`. It says **how to address GitHub**.
*When* to project is in SKILL.md; *whether* is in the grant.

## Status of this host

**Unverified.** No GitHub projection has been exercised as part of this pilot.

## Identity

`owner/repo#123`. A bare `#123` is only unambiguous inside its own repository —
record the qualified form so the identity survives a change of working
directory.

## What GitHub Issues can express

Very little, and being honest about that is the point of this file.

An issue has exactly two states: `open` and `closed`. There is **no in-progress
state and no in-review state**. So:

| Phase | Projection |
|---|---|
| implement | unmapped — nothing to write |
| verify | unmapped — nothing to write |

Leave both empty in config and report each transition as unmapped. Do not
invent a `status: in progress` label to stand in for a state. A label is a
label; representing it as a workflow state misreports what the tracker knows.

## When the repository uses Projects

GitHub Projects (v2) adds a per-project single-select `Status` field, which
*can* express in-progress and in-review. If a project uses one, discover the
field's options via the Projects API rather than assuming the default
`Todo / In Progress / Done`, then cache the resolved names:

```bash
python3 "$HELPER" config-set --state "github:implement=<discovered option>"
```

This is a per-repository fact, so it belongs in that project's config, not here.

## What this workflow never writes here

`closed`. Closing an issue is terminal and usually belongs to a merge — a
`Closes #123` in the pull request body does it without this workflow taking
the action. That is a `terminal_owner` of `merge-automation`.

## Writing

`gh issue edit` or `gh api` for the Projects field. Commenting is
`gh issue comment`, which is the only projection plain GitHub Issues supports
without a Project board.
