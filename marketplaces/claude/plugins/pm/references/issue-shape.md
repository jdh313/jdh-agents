# Issue shape

What a well-formed ticket carries **around** its body: the fields that must be
set for it to be workable. Source of truth for the Missing-fields bucket in
`pm:groom`.

The body itself is `issue-body.md`. Defers to `linear` (linear plugin) for
title shape, label values, priority semantics, and status flow.

## Required fields

A ticket is "well-formed" when it has all six:

1. **Title** — per `linear` conventions (`Area: noun-phrase` or bare noun-phrase)
2. **Project** — assigned to the active phase project (rotates per phase)
3. **Priority** — set to one of `urgent` / `high` / `medium` / `low`; not `None`
4. **Surface label** — exactly one of `pipeline`, `backend`, `frontend`, `infra`, `database`
5. **Type label** — exactly one of `Bug`, `Feature`, `Improvement`, `Docs`, `Chore`, `Decision`, `Spike`
6. **Body** — conforming to `issue-body.md`

A ticket missing any of #1–6 lands in `pm:groom`'s Missing-fields bucket.

## What the body check covers

`issue-body.md` defines five slots. Only two carry obligation, and only these
two are audited:

- **The aim** — an unlabeled one-line first line. Expected on every ticket.
- **`## Done when`** — expected at status `Todo` or beyond. A Backlog ticket
  may omit it.

The heading spelling is literal: the audit matches `## Done when`. The other
three slots (`## Why now`, `## Sketch`, `## Context`) are optional by design
and are never flagged as missing.

**This is a review prompt, not a gate.** `pm:groom` proposes; a human applies.
A ticket that cannot state its finish condition is usually one whose scope is
not yet settled — that is a finding worth surfacing, not a lint failure to
block on.

## Anti-conventions

- **No PR or branch links in titles or labels.** Solo direct-to-main workflow —
  tracking happens in the tracker, not in branch names.
- **No `D# — phrase` titles.** Use the `Decision` label; the label carries the
  marker.
- **No conventional-commit prefixes (`feat:`, `fix:`, `chore:`) in titles.**
  House style is noun-phrase, and the type label already says which it is.
- **No tracker issue IDs inside source code, comments, docstrings, ADRs, or
  NDRs.** References go ticket → code, not code → ticket.

## How the PM skills use this file

| Skill | Use |
|---|---|
| `pm:groom` | Missing-fields bucket checks #1–6. The body half of #6 is checked against `issue-body.md`'s two obligated slots. |
| `pm:breakdown` | Sets #1–5 on each published slice; composes the body per `issue-body.md`. |

## See also

- **`issue-body.md`** — what goes inside the body. Tracker-agnostic.
- **`layer-policy.md`** — the layers above a ticket (milestones, projects).
- **`linear`** (linear plugin) — Linear-specific mechanics: label values,
  status flow, priority semantics, MCP call patterns.
