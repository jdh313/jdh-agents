# Teardown note shapes

The two vault artifacts a teardown produces, and the evidence bar both are held to. Both land in `~/Loose Ends/Reference/Developer/` as ordinary wiki pages (`owner: ai`, `type: wiki`), so the vault's own rules apply on top of what follows: no H1 title (the text above the first `##` is the intro), `date created` / `date_modified` are Linter-managed and never hand-set, tags are hierarchical and kebab-case, wikilink the first mention of anything with its own page.

## `projects_surveyed:` — the read log

One field, on both note types, carrying one entry per project read into this page. There is no separate log artifact: this **is** the record of what was read, at what revision, when.

```yaml
projects_surveyed:
  - repo: home-assistant/core
    sha: 3f2a91c4d
    read: 2026-08-29
  - repo: jj-vcs/jj
    sha: 8c0117e21
    read: 2026-08-20
```

- **`repo`** — `owner/name` as GitHub spells it, so one grep finds it regardless of where the clone lives.
- **`sha`** — short SHA of the commit actually read (`git rev-parse --short HEAD`). This is what `/teardown-recheck` re-verifies against, so it must be the revision the citations came from, not the revision the remote is at now.
- **`read`** — `YYYY-MM-DD`, the date of the session that added the entry.

Entries append in read order and are never rewritten in place: re-reading a project at a newer SHA adds a second entry for the same `repo`. The history of when a page's claims were last grounded is part of the page's value.

Finding a prior read is then one command:

```bash
rg -l 'repo: home-assistant/core' ~/Loose\ Ends/Reference/
```

## Question note

Single-concern, multi-project, built to accrete. Filename is the question turned into a noun phrase — `Plugin and Extension Boundaries in Home Automation Platforms.md`, not `How do platforms do plugins.md`.

```yaml
---
owner: ai
type: wiki
page_type: concept
date_created: YYYY-MM-DD
date_updated: YYYY-MM-DD
sources: []
aliases:
  - "{a shorter handle someone might search}"
tags:
  - topic/software-architecture
  - topic/{domain}
up: "[[{topic area, if this is a specialization of one}]]"
related:
  - "[[{sibling survey over the same project pool}]]"
projects_surveyed:
  - repo: {owner}/{name}
    sha: {short}
    read: YYYY-MM-DD
template: "[[Wiki Concept]]"
template_version: "1.0"
---
```

`up:` points at a topic area (a cross-project question is a different topic from any one project, not a deeper layer of it). Use `expands:` instead only when the page genuinely descends from a broader page of the same material.

### Skeleton

```markdown
{One or two sentences defining the concern and naming its scope. Neutral, no
first person. Say how the projects were read — "at source level rather than from
their documentation" — because that is the page's whole claim to authority.}

Projects surveyed: {a, b, c, …}.

## 1. {First sub-question, phrased as the thing being compared}

| Project | {axis} | {axis} | {axis} |
|---|---|---|---|
| … | … | … | … |

{Prose beneath the table, carrying the derived claims. This is where the page's
value lives — the table is evidence, the prose is the finding.}

## 2. {Second sub-question}

…

## Recurring patterns

{Bolded claims that hold across sub-questions, one short paragraph each. A claim
here has survived every row in every table above.}

## Gotchas

> [!note] Findings that contradict the usual advice
> - …

## Unverified

{Claims that could not be confirmed in source, per project. A worklist, not an
apology — later passes close entries and move them into the body.}

## See also

- [[…]] — one line of commentary on why it is here
```

Numbered sub-question headings are worth it: they give a stable target for cross-references and make "extend every table" a countable operation during accretion.

### Worked micro-example

A single question-section, at the standard the rest of the page must hold:

> ## 2. Write atomicity and concurrent invocation
>
> | Tool | Write path | Stale-lock detection |
> |---|---|---|
> | restic | temp + rename (`internal/repository/…`) | Wall clock (30 min) + same-host PID liveness + refresh heartbeat (`lock_file.go:244-278`, `lock.go:124-248`) |
> | borg | temp + rename | Process liveness only, no timeout anywhere in history (`d490292b`, PR #1674) |
> | gh | Bare `O_TRUNC\|O_CREATE\|O_RDWR` (`config.go:329-344`) | None — no lock at all |
>
> **Stale-lock detection is where the real fork lies, and the result inverts the usual advice.** The heartbeat design — generally considered the more robust of the two — is the one with the production bug trail. Restic's changelog records four separate incidents: standby/suspend causing false *"failed to refresh lock in time"* errors (#4274), lock files accumulating when refresh deletion failed (#2452, #2473, #2562), SIGTERM skipping cleanup in containers (PR #4703), and stale-lock removal breaking on `chmod`-incapable filesystems as recently as 0.19.0 (#5595). Borg's simpler scheme has no comparable trail — though that may reflect a differently shaped user base rather than proving robustness.

Three things make it work, and all three are checkable: every cell that asserts structure carries a `file:LINE`; the claim in bold is a statement no single row could make; the hedge at the end is real ("may reflect a differently shaped user base") rather than decorative.

## Project note

Whole-system, one project, one page. Filename is `{Project} Architecture.md` when a top-level page for the project already exists, otherwise the project's own name.

```yaml
---
owner: ai
type: wiki
page_type: concept
date_created: YYYY-MM-DD
date_updated: YYYY-MM-DD
sources: []
aliases: []
tags:
  - topic/software-architecture
  - topic/{domain}
expands: "[[{Project}]]"
projects_surveyed:
  - repo: {owner}/{name}
    sha: {short}
    read: YYYY-MM-DD
template: "[[Wiki Concept]]"
template_version: "1.0"
---
```

`expands:` points at the project's gist hub (a Software Catalog entry, or a plain topic page) — the architecture page is a deeper layer of the same material. Omit both edge fields only if no page for the project exists yet.

### Skeleton

```markdown
{One or two sentences: what the system is and what shape it takes. The claim the
rest of the page defends.}

## Navigation

{Short. Entry point, the loop or dispatcher everything passes through, the
extension seam, the test corpus — each as one line with a `file:LINE`. This is
scaffolding for finding the code, and stays under about six lines. It is never
the substance of the page.}

## The mental model

{The spine. Four things, in whatever order the system makes natural:}

- **The central abstraction** — the one type or protocol the rest is written
  against, and what it costs to be outside it.
- **The unit of work** — what one thing the system does looks like end to end.
- **How data moves** — what crosses which boundary, in what shape, and what the
  boundary refuses to carry.
- **What everything hangs off** — the two or three decisions that, once made,
  determined most of the rest.

## Load-bearing decisions

{3–5 of them. Each gets its own `###`: what was chosen, what it displaced, and
the maintainer's own words for why, quoted with a short SHA or PR number. A
decision with no recoverable rationale is still worth a section — say that the
archaeology came back empty and what you searched.}

## Gotchas

> [!note] …

## Unverified

…

## See also

- [[…]]
```

The mental model is the reason the page exists. A reader who takes only that section away should be able to predict, roughly, where a given piece of behavior lives — that is the test for whether it is written well enough.

## Evidence standards

These apply to both note types, to every surveyor return, and to every line you write yourself.

- **Every structural claim carries `path/file.ext:LINE`** — repo-relative, at the SHA in `projects_surveyed:`. A range (`config.c:1546-1580`) where the claim spans one; a bare filename where genuinely no line applies. A structural claim with no citation is not a finding, it is a memory.
- **Quote maintainer rationale verbatim**, in italics, with a short SHA (`21cf32279`), a PR number (`PR #5806`), or an issue number. Paraphrasing a rationale destroys the thing that made it worth recording — that a human said it in those words. Prefer commit messages and maintainer comments over documentation; documentation says what the project wants to be true.
- **Report absences explicitly, with the search that established them.** *"A pickaxe for `os.Rename` and `atomic` on that file returns nothing, ever — no temp-and-rename alternative was ever discussed."* An unqualified "no rationale found" is unfalsifiable and therefore worthless; naming the search makes it checkable and re-runnable.
- **Flag inference as inference.** "The reading that unprotected config writes are deliberate-by-omission is inference; no comment, test, or issue confirms it." Then put it in `## Unverified` rather than the body, unless the body says out loud that it is inferred.
- **Distinguish "was decided against" from "was never considered."** These read identically in a codebase and mean opposite things. Only a history search separates them, and the answer is usually the more interesting of the two findings.
- **Negative results are results.** "uv has no extension surface at all. This is a negative search result, not a documented non-goal." Both halves of that sentence are load-bearing.
