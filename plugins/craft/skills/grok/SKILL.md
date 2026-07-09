---
name: grok
description: Build durable, supersession-aware understanding of a codebase over multiple sessions — both cold (a repo you're new to) and warm (a subsystem of a repo you already work in). Grounds in the repo's real sources (code, CONTEXT.md, NDR heads, git history) rather than parametric guesses, explains one subsystem at a time sized to what you already grasp, and persists confirmed understanding as records in the vault that graduate into CONTEXT.md and NDR atoms.
when_to_use: Use when the user says "grok this repo", "help me understand the X subsystem", "get me up to speed on this code", or "/grok".
disable-model-invocation: true
effort: high
argument-hint: "Which repo or subsystem do you want to understand?"
allowed-tools: Bash(obsidian-cli *), Write, Read, Grep, Glob, Bash(git log *), Bash(git show *), Bash(git blame *)
disallowed-tools: Edit, Bash(rm *), Bash(trash *), Bash(git push *), Bash(jj abandon *), Bash(jj restore *)
---

The user wants to understand a codebase. This is a **stateful** request — comprehension built over multiple sessions, not a one-shot explanation. (For a one-shot "zoom out and map this area," use the `zoom-out` skill instead; `/grok` is the layer that persists what `zoom-out` surfaces and tracks progress toward an understanding goal.)

This skill borrows the `teach` plugin's machinery — a mission, supersession-aware progress records, one-unit-at-a-time pacing, vault-routed durable artifacts — and points it at a codebase instead of a topic. The durable understanding records live in the **Obsidian vault** (`~/Loose Ends/`); confirmed _shared_ facts graduate out into the **repo's own** durable layer (`CONTEXT.md` and NDR atoms).

## Two entry modes

- **Cold** — a repo the user is new to. No workspace exists. Build one, interview for the goal, do a first orienting pass (high-level map), write the first records.
- **Warm** — a repo the user already works in, wanting to deepen understanding of a specific subsystem. A workspace may or may not exist. If it does, read the records to find the floor and pick the next thing; if not, create one and start from the subsystem the user named.

Same flow either way — resolve the workspace, ground, find the zone of proximal development, explain one thing, record what stuck.

## Before you start: ground in how this user learns

Read `Personal/Manual of Me/Learning/Learning Style.md` first (via `obsidian-cli read` or `@vault-reader`). It documents how this user actually retains material — the two-gate model (learning by **doing** + **real stakes**) and the **AI-as-substitute failure mode** (the risk that an AI explainer becomes a crutch that produces fluency without retention).

Codebase understanding is especially prone to the crutch failure: it is trivially easy to have the agent re-derive a flow every time instead of building a model the user owns. Guard against it:

- **End every session pointing the user at the real code or a real change** — a file to read at `file_path:line`, a small edit to attempt, a flow to trace by hand and check against the record. Not a frictionless answer machine.
- **Tie understanding to a live task** wherever possible. Stakes are what make it stick for this user.

## Ground in the codebase's real sources — never your parametric knowledge

You do not know this codebase. Treat the code and its durable layer as the only high-trust sources:

1. **`/ground`** (ndr plugin) first — surface NDR atoms governing the area so you don't re-explain or contradict settled decisions. Capture the `ndr:` references for the workspace's grounding sources.
2. **`CONTEXT.md`** at the repo root — the project's glossary. Use its vocabulary exactly in every explanation and record. If it's absent, that's fine; if terms keep surfacing that deserve it, route them to `grill-with-docs`.
3. **The code**, via a named `Explore` agent (`subagent_type=Explore`, `name="grok-explorer"`) for fan-out reads — keep it addressable so you can ask follow-ups during a walk. Use `Grep`/`Glob`/`Read` directly for narrow checks.
4. **Git history** — `git log`, `git show`, `git blame` to learn _why_ code is shaped the way it is and who to ask. History is a primary source for a "why," not a footnote.

Use craft's shared vocabulary — **module, interface, implementation, depth, seam, adapter, leverage, locality** — from the `codebase-design` skill (`craft:codebase-design`) — so explanations stay consistent with `improve-codebase-architecture` and `zoom-out`.

## The workspace (in the vault)

Honor the vault conventions in ~/Loose Ends/.claude/CLAUDE.md (frontmatter shape, naming, wikilink style) — read it before the first vault write of a session.

Each repo gets **one** workspace folder in the vault, placed under its best-fit context. Confirm the path with the user before creating anything (vault Location Decision Tree). Default for a dev repo:

```
Reference/Developer/{Repo Name}/
  Understanding.md        # the goal + a map of what's understood — see UNDERSTANDING-FORMAT.md
  Records/0001-*.md       # understanding records — see UNDERSTANDING-RECORD-FORMAT.md
  maps/0001-*.html        # optional set-piece walkthroughs (created lazily)
```

- `Understanding.md` — **one workspace per repo** (not per goal). Holds a moving _current focus_ plus a growing _map_ of what's understood. Use the format in [UNDERSTANDING-FORMAT.md](./UNDERSTANDING-FORMAT.md).
- `Records/*.md` — supersession-aware records of what you genuinely now understand, written on _evidence_ not coverage. Use the format in [UNDERSTANDING-RECORD-FORMAT.md](./UNDERSTANDING-RECORD-FORMAT.md).

**Tooling:** `.md` notes are created and edited with `obsidian-cli` (`create`, `append`, `property:set`) — including surgical in-note edits; complex restructures go to `@note-editor`. The optional `.html` maps are written with `Write` and live inside the workspace folder so their relative anchor links resolve.

**Proprietary repos:** for work repos, the personal vault still holds your personal understanding records, but durable _shared_ facts must **not** leak into the vault — graduate them to the repo's own `CONTEXT.md` or an internal authority, exactly as `grill-with-docs` does.

## The understanding goal

Every explanation should trace back to **why** the user is building this understanding (`Understanding.md` → Why / Current focus). If the goal is unclear or `Understanding.md` is unpopulated, your first job is to interview the user — what are they trying to do with this code?

Without a goal, explanations float free of any real outcome, feel abstract, and you have no way to judge what to explain next. Goals shift as understanding grows; when they do, update `Understanding.md` and write a record capturing the shift. Confirm before changing the stated goal.

## Zone of proximal development

Each session should challenge the user _just enough_. To find the right next thing:

- Read the records in `./Records/` to establish the floor — what's already understood.
- Read the `Map` and `Open questions` in `Understanding.md`.
- Pick the next subsystem/flow that is in reach given that floor and that serves the current focus.

If the user names an exact thing they want to understand, teach that — but still check the records so you build on what's there rather than repeating it.

## Explain one subsystem at a time

The unit of `/grok` is a single, tightly-scoped explanation of one subsystem, flow, or invariant — completable quickly, sized to working memory. Not a wall of architecture docs. Each explanation:

- **Is grounded in the real code** — cite `file_path:line` anchors for every load-bearing claim, the way `teach` lessons cite sources. The user should be able to jump straight to the code.
- **Uses the project's vocabulary** (CONTEXT.md) and craft's module/seam/depth language.
- **Builds a model, not a tour** — favor the _why_ and the invariants (the things that don't show up by reading the code top-to-bottom) over a line-by-line narration.
- **Ends with a real-stakes next step** — the anti-crutch move above.

For a big set-piece (a request lifecycle, a state machine, a data-flow across services), an HTML map in `./maps/` is worth it: a beautiful, print-friendly walkthrough with a diagram (Mermaid renders inline) that the user will return to. Keep these rare — most understanding belongs in records, not set-pieces. If you create one, open it for the user with a CLI command.

## Records — capture what stuck

Write an understanding record when the user (or you, on their behalf) built a durable model of something non-trivial, corrected a wrong model, or confirmed disclosed prior knowledge — see [UNDERSTANDING-RECORD-FORMAT.md](./UNDERSTANDING-RECORD-FORMAT.md) for the full gate. Coverage is not understanding; wait for a model that can be used. Keep records terse — they are decision-grade insights, not a journal.

After writing, update the `Map` in `Understanding.md` to point at the new record.

## Graduation — push shared truth into the repo's durable layer

A record is personal and provisional. When a fact in it turns out to be **shared, stable truth about the repo**, graduate it so the record stops being the canonical home:

- **A name for a thing** → the repo's `CONTEXT.md`, via the `grill-with-docs` skill.
- **A decision with rationale and genuine trade-offs** → an NDR atom, via `/capture-decision` (never write atom files directly).

This is the codebase analogue of `teach` graduating glossary terms into the vault wiki — same move, pointed at the repo's own authority instead of the vault.

## Composition

- **`zoom-out`** — the one-shot explainer; `/grok` persists and tracks what it surfaces.
- **`/ground`** (ndr) — decision grounding before explaining; run it first.
- **`Explore` agent** — codebase fan-out reads, named for follow-ups.
- **`grill-with-docs`** — destination for terms that earn a `CONTEXT.md` entry.
- **`/capture-decision`** (ndr) — destination for rationale-bearing decisions discovered while grokking.
- **`improve-codebase-architecture`** — once a subsystem is understood, the natural next step if it's shallow or tangled; shares the same vocabulary.
