# Archaeology — digging out history and rationale

Technique for [`surveyor`](../agents/surveyor.md)'s Phase 2. Run this only
after Phase 1 has produced a file map — every technique below is scoped by
that map, and scoping is what makes it fast instead of a fishing expedition.

Every command names the clone with `-C <repo_path>`. The clone is never the
session's working directory, so a bare `git log` reads the wrong repository.

## Find what introduced something

```
git -C <repo_path> log --diff-filter=A --follow -- <path>
```

Gets you the commit that first added the file. Read that commit's message
and diff before going further — it's often the single richest source of
rationale you'll find, especially in a project with no ADR directory.

For a symbol or block inside a file that already existed, don't stop at the
file-add commit — walk forward from there with
`git -C <repo_path> log -p -- <path>` or jump straight to pickaxe (below) on
the specific term.

## Pickaxe, scoped to one file

```
git -C <repo_path> log -S<term> -- <path/to/one/file.ext>
```

**Never run pickaxe unscoped against the whole tree.** A project with
100,000+ commits makes an unscoped `-S` search either time out or return so
many hits it's useless. Scope it to the one file Phase 1 told you owns the
mechanism. This is the direct payoff of doing Phase 1 first: you already
know which file to point at before you write your first pickaxe command.

## Search string fragments, not identifiers

Pickaxe matches diff content as a substring, so search on words a human
would plausibly have typed in a commit message or comment, not on variable
or function names:

```
git -C <repo_path> log -S"cause stability problems" -- <path>
```

A phrase fragment like this found the exact introducing commit on the first
try in practice — a search for a symbol name on the same file did not, when
the actual rationale was that specific sentence in a code comment. Think
about how a maintainer would phrase the *reason*, not what they'd name the
*thing*.

## Line-wrapped strings dodge pickaxe

Pickaxe matches literal diff content. A logical sentence that's wrapped
across multiple source lines (a long code comment, a multi-line string
literal) will not match a search for the full sentence, because no single
diff line contains it as a substring. If a plausible-sounding fragment
search returns nothing, don't conclude the rationale doesn't exist — retry
with a shorter fragment short enough to plausibly sit on one physical line
before giving up. This cost real search budget in practice: two failed
searches before narrowing to a fragment that matched.

## Check for an ADR/decision directory first, always

Before spending pickaxe budget, check once:

```
git -C <repo_path> ls-files | rg -i 'adr|decision-record|architecture-decision|docs/decisions|docs/architecture'
```

If nothing turns up, the project keeps its rationale in commit messages and
PR/issue threads instead — know that up front so you route your remaining
budget there instead of re-checking for a decisions directory every time a
search comes up empty. A project with no ADR directory isn't a project with
no rationale; it's a project whose rationale lives in a different place.

**Check for a sibling architecture repo before concluding there are no ADRs.**
A large project often splits governance out of the code repository, so the
search above returns nothing while a full ADR corpus exists one repo over. Home
Assistant is the worked example: `home-assistant/core` has no ADR directory,
and a survey that stopped there reported "no ADR corpus, all rationale lives
in commit messages" — wrong. The ADRs live in `home-assistant/architecture`,
and they carried better rationale than pickaxe would have found, including
ADR 0010's reason for retiring YAML config for device integrations, which is
partly a contributor-retention argument no commit message would ever state.

So when the in-repo search is empty, spend one `WebSearch` on
`<owner>/architecture`, `<owner>/rfcs`, `<owner>/decisions`, or
`<project> ADR` before falling back. The cost is one search; the miss costs
you the best-cited section of the teardown.

## Beware false-positive filename history

A file's full history can span unrelated eras. A path like `manifest.json`
can exist in a codebase for years as something completely unrelated (e.g. a
browser extension's PWA manifest) before being repurposed for the thing
you're actually investigating (e.g. a plugin-system manifest introduced
years later). `git -C <repo_path> log --diff-filter=A -- manifest.json` will
show you the *first* addition, which may be the wrong era entirely.

Guard against this the same way Phase 1 protects Phase 2 generally: scope
your first search by the path *and the era* Phase 1's structural read
actually pointed you to, not just the bare filename. If a file's early
history reads as unrelated to the mechanism you're studying, say so
explicitly as a finding — a false-positive filename match is worth reporting
as a gotcha, not silently discarding.

## Escalating to GitHub

A local clone contains commits and their messages — it does not contain PR
review comments or issue discussion unless a later commit happens to quote
them back verbatim. When a commit message alone doesn't explain a design
choice, use the `repo` slug (`owner/repo`) you were given:

- Find the PR that introduced a commit:
  `gh api repos/<owner>/<repo>/commits/<sha>/pulls`, or if the commit message
  references `#NNN`, fetch that PR/issue directly.
- `WebFetch` a specific PR/issue URL once you have a number — cheaper and
  more precise than `WebSearch`.
- `WebSearch` when you have a topic but no number yet (e.g. "home-assistant
  core integration manifest introduced").

Quote what you find the same way you'd quote a commit message: verbatim,
with the PR or issue number attached. A PR discussion thread is often where
the *rejected alternatives* live — commit messages describe what shipped,
PR threads describe what was argued about first.
