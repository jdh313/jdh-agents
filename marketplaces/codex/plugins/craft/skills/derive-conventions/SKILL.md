---
name: derive-conventions
description: >-
  Derives a host repository's unwritten conventions — naming, error-handling
  shape, docstring format, CLI voice — from its own code, presents each inferred
  rule with its evidence for accept/edit/reject, and writes the approved set to
  CONVENTIONS.md so craft's review agents stop re-deriving them every run. Never
  writes an unreviewed rule; the human adjudicates every entry.
---

# derive-conventions

## Overview

This is the **write side** of the convention loop that `house-style-reviewer`,
`comment-reviewer`, and `copy-reviewer` read from. Those three agents are
read-only and advisory: every run they sample sibling files and infer a
convention at a ≥60%-of-sample agreement threshold, then report findings
against it. That's deliberately cheap and deliberately non-authoritative —
a single bad sample self-corrects next run because nothing persists.

This skill breaks that safety property on purpose, in the one place it's
safe to break: it runs the *same* derivation once, **interactively**, shows
every inferred rule with its evidence, and writes only what a human
approved to `CONVENTIONS.md`. The agents then treat that file as a
higher-precedence tier and skip re-deriving whatever it covers.

Never let the agents write this file themselves. If an agent could author
its own convention cache, a bad 60% sample stops being a soft, self-healing
guess and becomes a permanent, self-confirming rule — every later run would
cite the cache as ground truth instead of re-checking the code. The human
adjudication step in this skill is what keeps an inference from silently
becoming an authority.

```
detect mode ──► read higher-precedence tiers ──► derive candidates per lane
   ──► ADJUDICATE (batches of ≤5, STOP each batch) ──► write CONVENTIONS.md
   ──► offer a CLAUDE.md/AGENTS.md pointer (ask first)
```

## When to use

- No `CONVENTIONS.md` exists yet and the user wants to pin down the repo's
  unwritten style so the review agents stop re-deriving it every run.
- `CONVENTIONS.md` exists but has gone stale — code has moved on from a
  `derived` entry, or the user wants a periodic refresh.
- One of `house-style-reviewer` / `comment-reviewer` / `copy-reviewer` just
  surfaced a finding worth pinning permanently rather than re-inferring
  next time.

**Do NOT use** to:

- Review a diff or recent edits — that's the three review agents' job. This
  skill never reports findings against code; it only builds the reference
  file they read.
- Declare a rule the human already knows and wants to state outright. Write
  that directly into `CONVENTIONS.md` as a `declared` entry, or say it in
  `CLAUDE.md`/`AGENTS.md` — no derivation needed, and this skill's
  evidence-gathering machinery is wasted effort on an already-known fact.
- Promote an approved `derived` entry to `declared`. That's a separate,
  explicit act — see "declared vs. derived" below.

## Modes

Detect the mode from whether `CONVENTIONS.md` already exists at the repo
root:

- **`derive`** (no file yet): full pass over the requested lanes, starting
  from nothing.
- **`refresh`** (file exists): re-sample only the existing `derived`
  entries (never touch `declared` ones), show what's drifted, and propose
  updates. Never silently overwrite a `derived` entry — drift is itself a
  candidate that goes through adjudication like any other.

**Lane scoping:** the argument names a lane — `style` (maps to
`house-style-reviewer`'s dimensions), `comments` (maps to
`comment-reviewer`'s), `copy` (maps to `copy-reviewer`'s), or `all`
(default). A path argument instead of, or alongside, a lane narrows the
sampling universe to that subtree — e.g. `style src/api/` derives only
naming/error-handling/test-structure conventions and only from files under
`src/api/`.

## Workflow

### 1. Establish the sampling universe

Detect VCS: `test -d .jj && echo jj || echo git`. Find the repo root.
Exclude vendored code, generated files, `node_modules`, build output, and
lockfiles from sampling — none of them carry the repo's own style, and
sampling them would pollute the majority.

### 2. Read the higher-precedence tiers first — do not re-derive what they already settle

Work through these, in order, before deriving anything:

1. `CLAUDE.md` / `AGENTS.md` — any convention already stated outright.
   Never propose a candidate that duplicates a declared rule.
2. Existing `CONVENTIONS.md` (refresh mode only) — read the current
   `declared` and `derived` sections and the `## Rejected` log.
3. Linter/formatter/prose-linter config — `.editorconfig`, `ruff.toml` /
   `pyproject.toml [tool.ruff]`, `.eslintrc*`, `rustfmt.toml`,
   `.golangci.yml`, prettier config, `.pydocstyle`, `eslint-plugin-jsdoc`,
   Vale/alex prose-lint config for copy.

Anything a tool in tier 3 already enforces is recorded as **excluded**, not
as a rule — file the config path and the key that enforces it under
`## Excluded (tool-enforced)` in the output file. This is what keeps the
review agents' output additive instead of restating lint failures; get it
wrong here and every downstream run inherits noise.

### 3. Derive candidates per requested lane

Use the exact same discipline the review agents use, because the threshold
has to match what they'll later use to *rebut* a `derived` entry:

- Sample 3-5 files per dimension from the relevant neighborhood (same
  directory or same architectural layer).
- Require ≥60% of the sample to agree before asserting a convention.
  Below that, there is no candidate for that dimension — say nothing rather
  than force a majority that isn't there.
- Every candidate carries its evidence: the files sampled, the agreement
  count (e.g. "7 of 9"), and one verbatim example line with a file:line
  anchor.

Lane → dimension mapping (mirrors the three agents so their `declared`
lookups line up 1:1 with what this skill produces):

| Lane | Dimensions |
|---|---|
| `style` | naming, placement, error-handling shape, API surface idiom, test structure |
| `comments` | docstring format (Google/NumPy/reST/JSDoc/TSDoc), WHY-comment expectations |
| `copy` | CLI/error/UI string voice, tone, terminology |

### 4. ADJUDICATE — the load-bearing step

Present candidates in batches of **at most 5** via `AskUserQuestion`, each
with its evidence inline. For every candidate the human can:

- **accept** as written,
- **edit** the wording (the edited wording is what gets written, not the
  original derivation),
- **reject** — record it under `## Rejected` with a one-line reason so a
  later run does not re-propose the same candidate.

STOP after presenting each batch and wait for the response — never
batch-accept on the human's behalf, and never infer approval from silence
or from an unrelated reply. A candidate the human hasn't seen must never
reach the file.

In `refresh` mode, a `derived` entry whose live re-sample now disagrees is
itself a candidate here: show the old rule, the drift evidence, and let the
human accept the update, keep the old wording, or reject and drop the
entry entirely.

### 5. Write CONVENTIONS.md

Match the location `house-style-reviewer` / `comment-reviewer` /
`copy-reviewer` already resolve by, so the file this skill writes is the
file they'll actually find: nearest-wins, the same rule those three agents
apply to `CLAUDE.md`/`AGENTS.md` — walk up from a changed file and take the
nearest `CONVENTIONS.md`, so a file beside the code shadows one at the repo
root for everything beneath it.

- **Default (no path argument):** write to `CONVENTIONS.md` at the repo
  root.
- **Path argument given, or a subtree whose conventions genuinely diverge
  from the root** (a vendored SDK, a differently-authored package): offer
  writing a scoped `CONVENTIONS.md` in that subtree instead of the root
  file. State plainly that it will shadow the root file for every changed
  file beneath it, since the review agents stop climbing at the nearest
  match.
- **Refresh mode:** update whichever file already exists where it already
  exists. Never relocate it — a refresh that moves the file from root to a
  subtree (or back) silently changes what shadows what for every other
  changed file in the repo, without the human asking for that.
- **Prefer a `scope:` glob in the root file over a second, nearer file**
  when the divergence is narrow enough to state as one entry's `scope:` —
  it keeps a single reviewable surface instead of splitting the corpus
  across files a reader has to know to look for. Reach for a nearer file
  only when the subtree's house style diverges broadly enough (multiple
  dimensions, not one rule) that a single `scope:`-qualified entry would
  undersell how different that subtree really is.

Preserve every existing `declared` entry **byte-for-byte** — this skill
never touches human-authored rules. Only `derived` entries get rewritten,
and only the ones that went through adjudication this run.

### 6. Offer, don't assume, a CLAUDE.md/AGENTS.md pointer

Ask before editing `CLAUDE.md` or `AGENTS.md` — it's the user's instruction
surface, not this skill's. A one-line pointer ("House conventions: see
CONVENTIONS.md") is a convenience, nothing more: the three review agents
already look for `CONVENTIONS.md` by name regardless of whether anything
points at it. If the user declines, say that plainly and move on — no
pointer is not a broken setup.

## The `declared` vs. `derived` distinction

The three review agents' precedence chain depends on this being exact:

- **`derived`** — this skill inferred it from sampling, and a human
  approved it (accepted or accepted-with-edits) in step 4. Carries
  `evidence` (files + counts + example) and a `sampled` date. **Rebuttable**
  — an agent that finds ≥3 counter-examples in its own live sampling
  reports the stale *entry* as a finding, not the code that disagrees with
  it.
- **`declared`** — a human wrote the rule directly, or explicitly promoted
  a `derived` entry. Authoritative: the review agents never re-derive over
  it and never rebut it, no matter how much counter-evidence accumulates.

**Human approval of a derived candidate in step 4 does NOT promote it to
`declared`.** Approval only means "yes, write this inferred rule with its
evidence attached." Promotion — stripping the evidence trail and making the
rule unrebuttable — is a separate, explicit act the human has to ask for by
name (e.g. "promote the AppError rule to declared"). The reason for keeping
these apart: the evidence trail is what makes a wrong `derived` rule
auditable and self-correcting. Collapsing "the human clicked accept" into
"this is now beyond question" launders an inference into an authority —
exactly the failure this skill exists to prevent.

## CONVENTIONS.md format

A repo may hold more than one `CONVENTIONS.md`: a root file plus, rarely, a
nearer one in a subtree with a genuinely separate house style. The review
agents resolve nearest-wins from the changed file up, so a nearer file
shadows the root file for everything beneath it — narrow divergences
belong in the root file's `scope:` glob instead (see step 5); reach for a
second file only when a subtree's style diverges broadly.

```markdown
# Conventions

Read by craft's review agents. Entries marked `declared` are authoritative;
entries marked `derived` were inferred from this repo and approved by a human,
and are rebuttable by counter-evidence.

## Style

### Errors wrap in AppError
- status: derived
- rule: Raise `AppError` (or a subclass), never a bare builtin exception.
- scope: `src/api/**/*.py`
- evidence: 7 of 9 files in `src/api/` raise `AppError`; `src/api/users.py:41`
- sampled: 2026-08-25

### Test files are `test_<module>.py`
- status: declared
- rule: Test files mirror the module they cover, one-to-one, no exceptions.
- scope: `tests/**`

## Comments

### Docstrings are Google-style
- status: derived
- rule: `Args:` / `Returns:` / `Raises:` sections, no NumPy-style underlines.
- scope: `src/**/*.py`
- evidence: 5 of 5 sampled files in `src/billing/` use Google-style
- sampled: 2026-08-25

## Copy

### Error messages address the user, not the system
- status: derived
- rule: CLI error strings phrase the fix as an instruction to the user
  ("Run `foo init` first"), never a system-state description
  ("foo was not initialized").
- scope: `cli/errors/*.py`
- evidence: 4 of 6 sampled error strings follow this shape;
  `cli/errors/setup.py:12`
- sampled: 2026-08-25

## Excluded (tool-enforced)
- Line length, import order — enforced by `ruff.toml` `[lint] select = ["E501","I"]`
- Docstring presence (not content) — enforced by `pyproject.toml`
  `[tool.ruff.lint] select = ["D"]`

## Rejected
- "Prefer f-strings over .format()" — rejected 2026-08-25: mixed corpus
  (5 of 9), no majority.
- "CLI errors end with a trailing period" — rejected 2026-08-25: human
  judged it noise, not a real convention.
```

Omit a lane's subsection entirely if this run produced no candidates for
it (no `(0)` headers) — same convention the review agents already follow
for empty dimensions.

## Failure modes to avoid

- **Writing a rule the human never saw.** Every entry in the file traces
  back to a specific `AskUserQuestion` batch and an explicit accept/edit.
  If you can't point to that batch, don't write the entry.
- **Promoting `derived` to `declared` without being asked.** Approval of a
  candidate is not a promotion request. Wait for the explicit ask.
- **Re-proposing a previously rejected rule.** Read `## Rejected` before
  deriving; a candidate that matches a prior rejection (same rule, same
  scope) is skipped, not re-surfaced, unless the human asks for a re-check.
- **Recording a tool-enforced rule as a convention instead of as excluded.**
  Check linter/formatter/prose-linter config *before* sampling a dimension
  — if a tool already enforces it, it goes under `## Excluded`, never under
  a lane.
- **Letting the file go stale with no `sampled` dates.** Every `derived`
  entry needs one; a `refresh` run without dates can't tell what needs
  re-checking.
- **Deriving from a corpus too small or too inconsistent to support a
  majority.** Below the 60%-of-3-to-5-file threshold, or with fewer than 3
  candidate files, report nothing for that dimension — do not lower the
  bar to manufacture a candidate.
- **Relocating an existing CONVENTIONS.md on refresh.** Update it where it
  already lives. Moving it between root and a subtree changes what shadows
  what for every other file in the repo — that's a location decision, not
  a refresh, and needs its own explicit ask.
- **Splitting a narrow divergence into a second file instead of a `scope:`
  glob.** A nearer file is for a subtree whose style diverges broadly; one
  divergent rule belongs in the root file, scoped.
- **Batch-accepting on the human's behalf.** Auto Mode or not, this skill's
  entire reason to exist is the STOP-and-wait in step 4. Never skip it.

## Related

- `house-style-reviewer`, `comment-reviewer`, `copy-reviewer` (craft
  agents) — read-only, diff-scoped reviewers that consult `CONVENTIONS.md`
  as their second-highest precedence tier and fall back to live sampling
  for whatever it doesn't cover.
- Precedence chain shared by all three agents and this skill:
  `CLAUDE.md`/`AGENTS.md` declarations > `CONVENTIONS.md` (`declared` then
  rebuttable `derived`) > linter/formatter config (exclusions only) > live
  sampling.
- `interrogate-model` — the closest structural sibling for the
  interactive-STOP-and-adjudicate shape this skill follows.
- `grill-with-docs` — the house precedent for promoting an inferred fact
  into a repo file with the human in the loop, applied there to `CONTEXT.md`
  vocabulary instead of style.
