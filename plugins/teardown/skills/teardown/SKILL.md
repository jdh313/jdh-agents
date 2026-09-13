---
name: teardown
description: >-
  Read a real codebase at source level and land the result as a durable vault
  reference page — a whole-system project note, or a single-concern question
  note that accretes one project at a time into comparison tables and derived
  claims. Use when the user says "teardown", "study X", "how is X
  architected", "how does X do Y", "how do these projects handle Z", "what can
  I learn from X", "add X to that survey", or hands over a repo they want
  understood rather than changed. Requires a local clone; delegates reading to
  `@surveyor` agents and keeps the synthesis for itself.
disable-model-invocation: true
effort: high
argument-hint: "Which project — or which question across projects?"
allowed-tools: Bash(obsidian-cli *), Read, Grep, Glob, Bash(git log *), Bash(git show *), Bash(git blame *), Bash(git status *), Bash(git remote *), Bash(git fetch *), Bash(gh api *), Bash(gh issue *), Bash(gh pr *), Bash(rg *), WebFetch, mcp__obsidian-mcp__patch_note, mcp__obsidian-mcp__search_notes, Edit(~/Loose Ends/Reference/Developer/**), Edit(//private/tmp/**), Edit(//tmp/teardown/**), Agent, Skill(artifact-design), Artifact
disallowed-tools: Bash(rm *), Bash(trash *), Bash(git push *), Bash(git commit *), Bash(git checkout *), Bash(git reset *), Bash(git clean *), Bash(git rebase *), Bash(git stash *)
---

A **teardown** reads a real codebase at source level and lands the result as a durable page in the Obsidian vault (`~/Loose Ends/Reference/Developer/`). The output is a **research instrument**, not a lesson: the audience is future-Jacob and future-Claude reaching for a decided question six months from now. Full delegation of the reading is correct here — this user does not retain material by writing it up, and the vault is where the retention lives instead. Do not quiz, do not teach back, do not close with "now go read the code yourself."

The quality bar is a concrete artifact: `~/Loose Ends/Reference/Developer/Architecture of Stateful CLI Dev Tools.md`. Read it before writing your first teardown. Every structural claim in it carries a `path/file.ext:LINE`; every rationale claim quotes a maintainer verbatim with a short SHA or PR number; absences are reported as findings ("a pickaxe for `os.Rename` on that file returns nothing, ever"); inference is labelled inference; an `## Unverified` section names what could not be confirmed.

## Two note types, and the route between them

The user's question decides which one you are writing.

- **Project note** — whole-system scope. *"How is Home Assistant architected?"* One project, one page. The spine is the **mental model**: the central abstraction, the unit of work, how data moves, and the two or three decisions everything else hangs off. The second half is 3–5 load-bearing decisions with reconstructed rationale. A short pinned navigation block (entry points, the extension seam) sits near the top as scaffolding — it is a map to the code, never the substance of the page.
- **Question note** — single-concern scope. *"How does Home Assistant let users create plugins?"* Born at one project and **accretes** projects over time. Structure is question-sections; inside each, a comparison table with projects as rows. The value concentrates in a handful of bolded derived claims that only exist because several rows sit next to each other.

Route on scope, not on project count. "How is X architected" is a project note even if X is the third such project. "How does X do Y" is a question note even at N=1 — the table has one row, and the page is built to grow.

Both live in `Reference/Developer/`. Both carry `projects_surveyed:`.

## Session open — fast

The user will route around a slow opening. Two things only:

1. **The question**, in their words.
2. **The goal** — what they intend to do with the answer (adopt a pattern, decide a design, satisfy a curiosity that keeps recurring).

Depth is *derived* from those two. A goal of "I'm about to build this seam myself" earns line-level tracing of the seam and its rejected alternatives; a goal of "I keep wondering how these differ" earns one table row per project. There is no depth dial and no gate that refuses to go deeper — the pair above is the whole input.

State back, in one line, what you inferred: note type, target note (new or existing), projects, and depth. Then move.

## Find the existing note before writing a new one

A miss here is the expensive failure. It silently creates a second page on the same question, and two pages on one question never merge — the accretion that makes question notes valuable stops dead. Search both ways before concluding a page does not exist:

- **The read log.** `rg -l 'projects_surveyed:' -A 40 ~/Loose\ Ends/Reference/` and grep the repo name within. `projects_surveyed:` doubles as "have I read this repo before, and where did it land?" across 285+ notes.
- **Semantic.** Dispatch `librarian:vault-reader` with the question in the user's own words. Titles will not match; the concern will.

If both return candidates, or neither returns anything and you suspect a near-miss title, show the user the candidates and ask. A tie you resolve alone is the duplicate you create.

## The corpus

**A local clone is required.** Reading a project through the GitHub web UI produces the citation quality that makes a teardown worthless. Resolve `~/upstream/<name>`:

- **Present.** Check `git status` and whether the branch has diverged from its remote. Then **confirm before pulling**: report the current SHA, what a pull would bring in, and whether the tree is dirty — and ask. Many of these repos back services the user actually runs; a silent `git pull` into `~/upstream` is a change to their machine, not a refresh of your reading material. Never pull automatically. Reading a slightly stale clone is fine, and the SHA you record makes it honest.
- **Absent.** Offer to clone into `~/upstream/<name>`. Say which remote and how large.

Record the **exact SHA read** (`git rev-parse --short HEAD`) for every project. It goes into `projects_surveyed:` and it is what `/teardown-recheck` later re-verifies against.

**If `git` is refused, it is a guard hook, not a broken repo — adapt, don't work around.** A `destructive-vcs-guard` style hook keys on the *session's* working directory, so once the cwd is any jj repo — this marketplace, or the vault itself — it rejects status-shaped `git` commands aimed anywhere, including a plain git clone in `~/upstream`. It reports "This is a jj repo," which is false about the clone and true about the cwd. `allowed-tools` pre-approves a call; it cannot override a hook that refuses one, so the `Bash(git status *)` entry above helps only when no such hook is active.

When that happens:

- Substitute what still runs. `git -C <clone> rev-parse --short HEAD` and `git -C <clone> log` have gone through; `status`, `diff`, and `ls-files -m` are the shapes that get refused. Get the SHA, skip the dirtiness check, and say in the note that you skipped it.
- **Never obfuscate a command to get past the hook** — no Python `subprocess` wrapper, no aliasing, no string-splitting. A surveyor that routes around a safety hook is a worse failure than a teardown missing its archaeology.
- Tell the user, once, that local history digging is degraded and that the GitHub path (issues, PRs, the sibling architecture repo) is carrying that weight instead. It genuinely can — see `references/archaeology.md` — but the note's `## Unverified` section must say so.

**The web is in scope, narrowly.** A clone does not contain the argument that produced the code. Issues, pull requests, discussions, releases, and the project's own documentation are legitimate sources of rationale and are often the only place a maintainer says *why*. Keep to that whitelist. Blog posts, aggregator threads, and third-party explainers are out — they carry no more authority than your own inference and cost more to check.

## Dispatch surveyors

Reading is delegated. Synthesis is not.

Dispatch one **`@surveyor`** per project. Fan out — when accreting several projects into a question note, they run concurrently in a single message. Each surveyor runs two **ordered** phases: current structure first, then history and rationale *with the structure already in hand*.

The order is load-bearing, and the evidence is direct. A trial run against `home-assistant/core` (27,571 files, 115,980 commits) compared one agent doing code-then-history against a reader/digger split:

- The solo agent returned **6 of 6** correct line-number citations. The split reader returned **1 of 5** — it placed `ComponentProtocol` at lines 1774–1802 when it is at `:379` — despite holding a *larger* code budget than the solo agent.
- Commit SHAs from both arms verified correct. **Archaeology survives fan-out; current-code line numbers are what degrade under it.**
- The digger's own method notes named the handoff cost: it burned searches chasing a false-positive 2015 frontend `manifest.json`, and said knowing the current structure first "would have let me scope the very first pickaxe search by path and skip that false start entirely."

So: one agent per project, both phases, never a reader/digger split within one project.

Give each surveyor the question, the goal, the clone path, the SHA, and the depth. Ask it back for **evidence** — cited structure, quoted rationale, explicit absences, labelled inference. Do not ask it for the lesson. The lesson is yours, because only you hold all the projects.

## Synthesis — the part you keep

You return the lesson. Concretely:

- **Derive claims across rows, not within them.** A claim that is true of one project belongs in that project's cell. A claim earns bold only when it says something the rows could not say separately — *"fall back when you moved the goalposts on purpose; migrate when you regressed."*
- **Prefer the contradiction.** A finding that inverts the usual advice is worth more page weight than one that confirms it. The elaborate design generating the bug trail; auto-detection losing to an explicit flag.
- **Report absences as findings.** "No commit, pull request, or code comment anywhere in the project's history proposes or rejects an env-var binary override" is a result. Say what search established it.
- **Keep inference visibly inference,** and put what you could not confirm in `## Unverified` rather than dropping it. A closed uncertainty gets rewritten into the body on a later pass; the section is a worklist, not an apology.

## Accretion — the loop that makes question notes worth having

Adding project N to an existing question note is two steps, and the second one is the point.

1. **Extend the tables.** One new row per question-section, at the same evidence standard as the existing rows. Append the entry to `projects_surveyed:`.
2. **Re-test every standing bolded claim against the new evidence.** Walk them one at a time and mark each:
   - **Confirm** — the new project is another instance. Say so in the claim if it sharpens it.
   - **Complicate** — the claim survives with a stated condition. Rewrite it with the condition; a claim that needs a caveat and does not carry one is worse than no claim.
   - **Break** — the new project is a counterexample. Rewrite or retire the claim, and keep a line saying what broke it. A retired claim that leaves no trace invites its own rediscovery.

**This re-derivation is never delegated.** A surveyor holds one project; the claim is a statement about all of them. Dispatching it is how a survey quietly becomes a list.

The cost is asymmetric by design: the eleventh project is more expensive than the first, because it must be re-tested against ten standing claims rather than none. That is the mechanism working, not a reason to skip step 2.

## Write the note

Templates, exact frontmatter (including the `projects_surveyed:` shape), section skeletons, a worked comparison-table example, and the evidence standards are in [`../../references/note-shapes.md`](../../references/note-shapes.md). Load it before the first write of a session.

Honor the vault's own conventions (`~/Loose Ends/.claude/CLAUDE.md`): `owner: ai`, `type: wiki`, no H1 title, `date created` / `date_modified` left to the Linter plugin, kebab-case hierarchical tags, wikilinks on first mention of anything with its own page.

**Write a new page as a file; use the tools for everything after.** `obsidian-cli create` takes its body through `content=`, which is an escaped single-argument string (`\n` for newlines) — workable for a stub, unusable for a teardown, whose whole substance is pipe tables, code spans, and quoted rationale. Write the file directly to `~/Loose Ends/Reference/Developer/<Title>.md` (pre-approved through the `Edit(...)` path rules in `allowed-tools`; Claude Code checks `Write` against `Edit` path rules, and a `Write(path)` rule is never consulted); Obsidian watches the folder, so the result is identical and the escaping risk disappears. Two related traps: `obsidian-cli create --help` does not print help, it *creates a note named "Untitled"* (the CLI takes `key=value` pairs, not flags) — check `obsidian-cli --help` at the top level instead; and `create` silently does nothing useful if the file exists, so confirm the path is new.

For everything after the first write, use the tools: `obsidian-cli append` and `property:set` for accretion (a new `projects_surveyed:` entry, a new table row), `mcp__obsidian-mcp__patch_note` for surgical in-body replacement when a claim is rewritten, and `librarian:note-editor` for a restructure.

Close by giving the user the note's Obsidian URI, plus one line naming what changed in the derived claims — that is what they came for.

## Composition

- **`@surveyor`** — the per-project reader. Two ordered phases, evidence only.
- **`/teardown-recheck`** — drift re-verification of a note's claims against the SHAs recorded in `projects_surveyed:`. Do not re-verify inline.
- **`librarian:wiki-graduate`** — when a pattern recurs across two or more comparisons and deserves a durable page of its own, graduate it there rather than growing the survey.
- **`librarian:wiki-refresh`** — ordinary staleness refresh of an existing page.
- **`librarian:vault-reader`** — semantic search for the existing note at session open.
- **`/capture-decision`** (ndr) — when a teardown settles a decision about one of the *user's own* projects, record it there. The vault page holds what other people decided; the ledger holds what he decided.
