---
name: teardown-recheck
description: >-
  Audit a teardown note's pinned claims against what actually changed in the
  studied repo since the commit SHA recorded in its `projects_surveyed:`
  frontmatter — confirm the local clone is current, diff cited files since the
  recorded SHA, and verify cited `file.py:LINE` citations still point at what
  the note claims. Use when the user says "recheck this teardown", "is this note
  still accurate", "has X changed since I read it", or "teardown drift".
  Distinct from `librarian:wiki-refresh`, which rewrites a page with newer
  information in general and has no notion of a pinned commit or cited source
  files.
argument-hint: '[note name or project]'
disable-model-invocation: true
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(git -C * status *)
  - Bash(git -C * log *)
  - Bash(git -C * diff *)
  - Bash(git -C * show *)
  - Bash(git -C * fetch *)
  - Bash(git -C * pull *)
  - Bash(git -C * rev-parse *)
  - Bash(obsidian-cli *)
  - mcp__obsidian-mcp__search_notes
  - mcp__obsidian-mcp__read_note
  - mcp__obsidian-mcp__get_frontmatter
---

# Teardown Recheck

`projects_surveyed:` pins a commit SHA per repo on every teardown note. Without
something that reads that pin back, it is inert bookkeeping — the note keeps
citing `router.py:142` forever, whether or not `router.py` still has 142
lines. This skill is the read: it turns the pin into a live drift check
against the repo as it stands today.

Distinct from `librarian:wiki-refresh`: refresh rewrites a page with newer
information, with no notion of a pinned commit or cited source files.
`teardown-recheck` verifies *pinned claims* against a *diff since a pinned
commit* and tells you exactly which citations broke — refresh cannot do that.

## Workflow

### 1. Resolve the target note

If a note name or project is given, look it up directly. Otherwise, find
candidates by grepping `projects_surveyed:` frontmatter across
`~/Loose Ends/Reference/Developer/` (via `@vault-reader` or
`obsidian-cli search`) and ask which one, or offer the most recently surveyed
if there's an obvious single match.

Read the full note: its `projects_surveyed:` list (repo, SHA, date per
entry) and its body, including every `file.py:LINE`-shaped citation. The
note's own citations are the input to step 4 — extract them verbatim, one
per claim, keeping the surrounding sentence so you know what each citation is
claiming.

If the note has no `projects_surveyed:` entries, stop: there is nothing
pinned to recheck against. Offer `librarian:wiki-refresh` instead if the
note just seems stale.

### 2. Confirm each clone is current — never silent

For each repo in `projects_surveyed:`, at `~/upstream/<name>`:

- If the clone doesn't exist, stop and say so — there's nothing to diff
  against. Do not offer to clone it as part of this skill's own action;
  that's `/teardown`'s setup step.
- Check `git status` for a clean tree and `git fetch` to see what's behind.
  If the local branch is behind its remote, **show what would change**
  (`git log HEAD..@{u} --oneline`, capped to a reasonable count) and ask
  before pulling. If the tree is dirty, stop and surface that instead of
  guessing which state to diff from.
- Only after an explicit yes, pull. This mirrors `/teardown`'s own
  confirm-before-pull rule — several of these repos back services the user
  runs, and a silent fast-forward is a silent behavior change to something
  running.

### 3. Diff since the recorded SHA

For each repo, run:

```
git -C ~/upstream/<name> log <recorded-sha>..HEAD --oneline -- <cited files>
```

restricted to the file paths pulled from the note's citations in step 1 (not
the whole repo — a repo can have moved a great deal that never touches what
this note actually cites). Note which cited files have zero commits in
range (cheap wins: those claims are very likely still accurate) versus which
changed at all (candidates for step 4's closer look).

### 4. Verify each citation

For every `file.py:LINE` citation, whether or not step 3 flagged its file:

- Read the file at HEAD and at the recorded SHA (`git show <sha>:<path>`).
- Check whether the cited line still contains what the note's claim
  describes. Line numbers drift even when the underlying logic hasn't
  moved far — a function gaining a docstring above it shifts everything
  below by a fixed offset, which is the single most common silent failure
  here: the code is fine, the pointer is wrong.
- Classify each claim:
  - **still-true** — cited line (or its near neighborhood) still shows what
    the note claims.
  - **line-drifted** — the claim is still true, but the line number no
    longer matches; find and report the current line.
  - **substantively-changed** — the code the claim describes actually
    changed in a way that makes the claim wrong or incomplete.
  - **cannot-verify** — file deleted/renamed with no clear successor, or the
    claim is too vague to check against a specific location.

### 5. Report, ranked by how load-bearing the claim is

Order findings by weight, not by file order: a broken **bolded derived
claim** (the sentence a QUESTION note's comparison row exists to make, or a
PROJECT note's mental-model anchor) matters far more than a shifted line
number in a table's citation cell. Lead with anything substantively-changed
or cannot-verify; group still-true and line-drifted lower since they need
less attention.

For each finding, cite the note's claim, the citation, and the concrete
evidence (commit, diff hunk, or current line number).

### 6. Propose fixes — never apply unattended

Recheck never edits the note itself. For each finding that needs action,
propose exactly one route and let the user choose:

- **Line-drifted** — propose the corrected line number as a direct edit; low
  risk, but still surfaced rather than applied silently.
- **Substantively-changed** — propose re-verifying via a scoped `@surveyor`
  dispatch (limited to the specific area that changed, not a full re-survey)
  before touching the note, since the fix should reflect what the code does
  now, not a guess from the diff alone.
- **Cannot-verify** — propose either a scoped `@surveyor` dispatch to relocate
  the claim, or superseding the citation with a note that the referenced code
  no longer exists.

After the user picks a route and the note is corrected, bump the touched
`projects_surveyed:` entry's SHA and date to reflect the recheck.

## What this skill does NOT do

- Does not pull a clone without explicit confirmation.
- Does not edit the note directly — every fix is proposed, never applied
  unattended.
- Does not re-survey the whole project when only a few cited files moved;
  scope any `@surveyor` follow-up to just the area in question.
- Does not replace `librarian:wiki-refresh` for a general content-freshness
  pass with no pinned citations in play.
