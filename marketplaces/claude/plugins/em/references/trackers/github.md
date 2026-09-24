# Tracker: GitHub Issues

Read this when the resolved tracker is `github`. It says **how to address
GitHub Issues**.

## Status of this adapter

**Unverified** against a live Projects board. Plain issue reads via `gh` are
routine.

## Identity

`owner/repo#123`. A bare `#123` is unambiguous only inside its own repository:
qualify it from `.em.toml` `[github] repo`, else from the current repo's
`origin` remote, and record the qualified form.

## Fetch

```bash
gh issue view 123 --repo owner/repo --json title,body,state,labels,assignees,comments,url
```

Linked pull requests and "tracked by" relations come from the issue timeline
(`gh api repos/owner/repo/issues/123/timeline`). Read cross-referenced issues'
titles and states.

## Readiness fields

Headings in the body map onto the slots by meaning: `## Done when`,
`## Acceptance criteria`, or a task list of observable outcomes all count as
the `Done when` slot.

## State changes

A plain issue has two states, `open` and `closed`. There is no in-progress or
in-review state, so those transitions are unmapped: report them as such. Do not
invent a label to stand in for a state.

If the repo uses GitHub Projects (v2), its single-select `Status` field can
express progress. Discover its options through the Projects API rather than
assuming `Todo / In Progress / Done`.

`em` never closes an issue. A `Closes #123` in the pull request body does that
on merge.

Every write (`gh issue edit`, `gh issue comment`, a Projects field) is
outward-facing: confirm it with the user in the same turn. The one exception
is `em:lead` setting the Projects `Status` of the issue it was invoked on to
its in-progress option; invoking it is the consent.
