# teardown

> **Requires an Obsidian vault.** Skills in this plugin read and write notes in an
> Obsidian vault, defaulting to `~/Loose Ends/`. That default is an example, not a
> requirement — point it at your own vault by editing the paths in the skill and
> agent bodies (search for `Loose Ends`). Without a vault, this plugin will not work.

Study foreign open-source projects to extract transferable architectural lessons
into the Obsidian vault. `teardown` is a reference instrument, not a learning
one — its output serves future-Jacob and future-Claude as lookup: "how does
project X solve problem Y," answered by a note you can open in two seconds
instead of a repo you have to re-read.

## Premise

Reading someone else's codebase to steal a good idea is valuable and easy to
lose. Without a place to put it, the lesson lives in scrollback for a day and
is gone. `teardown` gives that reading session a fixed output shape, a
required local clone so the reading is against real code rather than
remembered impressions, and a pinned commit SHA so a note's claims can be
checked against drift later instead of trusted forever.

## Two note types

Both live in `~/Loose Ends/Reference/Developer/`.

- **QUESTION note** — single-concern ("How does X let users create plugins?").
  Born at one project, then **accretes** more projects over time as you study
  others that answer the same question. Structured as question-sections
  holding comparison tables, one row per project, with value concentrated in
  a few bolded derived claims rather than spread evenly across prose. Reach
  for this when the thing you learned is comparable across projects.
- **PROJECT note** — whole-system ("How is X architected?"). One note per
  project, with the mental model as its spine — the shape you'd draw on a
  whiteboard to explain the system to someone else. Reach for this when the
  lesson is the system's overall design, not one comparable facet of it.

A single teardown session can write to either or both: a session on a new
project might add a row to three existing QUESTION notes and also produce its
first PROJECT note.

Both note types carry `projects_surveyed:` frontmatter — a list of entries
recording, per repo, the commit SHA that was read and the date. This is the
index **and** the read log; there is no separate log artifact. It's also the
thing `/teardown-recheck` reads to know what to check for drift.

## Session flow (`/teardown`)

1. Find the existing note first, by the repo slug recorded in
   `projects_surveyed:` (`repo: owner/name`), before touching any code.
2. Pin a SHA. Use a local clone if one exists (found by remote URL, not folder
   name) and **always confirm before pulling** it; with no clone, surveyors
   fetch each file they cite at the pinned SHA.
3. Descend one layer at a time — **system map**, then **domain model**, then
   **code** — with the user picking each next layer. Per layer, `surveyor`
   agents (one per project, or one per concern in a large repo) run two
   ordered phases, current structure then history and rationale, and each
   writes its evidence to a file.
4. Spot-check 3 citations per surveyor file and every anomaly claim before
   writing anything.
5. Add the layer's findings to the vault note (with a `projects_surveyed:`
   entry for the SHA read), then add a tab to one interactive Artifact page
   when the Artifact tool is available. The note is the durable record; the
   page is the explorable view of it.

## Keeping notes honest (`/teardown-recheck`)

`projects_surveyed:` is bookkeeping nobody reads unless something closes the
loop. `/teardown-recheck` is that loop: given a note, it confirms the local
clone is current (same confirm-before-pull rule as above), diffs each cited
file between the recorded SHA and HEAD, and checks whether the note's own
`file.py:LINE` citations still point at what the note claims. It reports
each claim as still-true, line-drifted, substantively-changed, or
cannot-verify, ranked by how load-bearing the claim is, and proposes fixes
without applying them — the user adjudicates every change.

This is distinct from `librarian:wiki-refresh`: refresh rewrites a page with
newer information in general; `teardown-recheck` verifies *pinned claims*
against a *diff since a pinned commit*, and can tell you exactly which
citations broke. Refresh has no notion of a pinned commit or cited source
files.

## Composes with

- **librarian** (external — personal setup, not published) — `wiki-graduate`
  splits an overgrown QUESTION or PROJECT note into an `expands:` child page
  once it's accumulated too much; `wiki-refresh` handles a plain
  content-freshness update when no pinned-citation drift is involved.
- **ndr** (external — ships from its own separate marketplace) — when a
  teardown session prompts a decision about the *user's own* projects (e.g.
  "we should adopt this pattern in `homelab`"), route it to
  `/capture-decision`. `teardown` notes record what other projects do; ndr
  atoms record what the user decided to do about it.
- **`craft:grok`** — the sibling for repos the user **owns and intends to
  change**: stateful, supersession-aware comprehension that graduates into
  `CONTEXT.md` and NDR atoms for that repo. `teardown` is for repos the user
  does **not** own and has no intention of modifying — the boundary is
  ownership and intent to change, not project size or language. If you're
  about to edit the code, you want `grok`; if you're borrowing an idea from
  code you'll never send a PR to, you want `teardown`.

## Assumptions

- An Obsidian vault (default `~/Loose Ends/`) with a `Reference/Developer/`
  location for both note types.
- A local clone under `~/upstream/` when one exists; otherwise `gh` and `curl`
  to fetch source files at a pinned SHA. Citations always come from files
  opened at that SHA, never from rendered pages or memory.
- Claude Code's `Artifact` tool for the interactive page. Without it, the
  vault note is produced alone and is complete on its own.
