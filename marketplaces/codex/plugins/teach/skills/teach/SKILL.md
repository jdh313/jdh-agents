---
name: teach
description: >-
  Teach the user a new skill or concept over multiple sessions, building a
  teaching workspace in the Obsidian vault — a mission, resources, markdown
  lessons, a glossary, and learning records — grounded in the user's documented
  learning style and high-trust sources. Use when the user says "teach me X", "I
  want to learn X", or "/teach". Adapted from mattpocock/skills (MIT, © 2026
  Matt Pocock).
---

The user has asked you to teach them something. This is a stateful request — they intend to learn the topic over multiple sessions.

This adaptation routes every teaching artifact — including lessons and reference sheets — into the **Obsidian vault** (`~/Loose Ends/`) as real notes. There is no HTML in this skill: a lesson is a `type: lesson` markdown note, and it participates in the graph the same as any other note (frontmatter, wikilinks, Breadcrumbs, query). This is what makes depth-matching possible in the first place — see [Entry altitude](#entry-altitude-question-altitude--graph-density) and [the calibration gate](#the-calibration-gate--mandatory-not-advisory) below.

## Before you start: ground in how this user learns

Read `Personal/Manual of Me/Learning/Learning Style.md` first (via `obsidian-cli read` or `@vault-reader`). It documents how the user actually retains material — the two-gate model (learning by **doing** + **real stakes**) and the **AI-as-substitute failure mode** (the risk that an AI tutor becomes a crutch that produces fluency without retention).

Let it steer every choice:

- **Bias hard toward real-stakes practice and real-world application.** Do not lean on flashcards or recall drills as the primary mechanism — they build fluency strength (an illusion of mastery), not the storage strength this user retains through.
- **Guard against being the crutch.** Your job is to push the user out to *do the thing*, not to be a frictionless answer machine. Design lessons that end with the user doing something real.

## The teaching workspace (in the vault)

Each topic gets a **self-contained workspace folder in the vault**, placed under its best-fit *context* (see "Resolving the context" below). Inside it:

- `Mission.md` — a `type: learning-mission` note capturing the _reason_ the user is interested in the topic. This grounds all teaching. It also holds teaching preferences — things to keep in mind about how the user wants to be taught (the upstream `NOTES.md` is folded in here). Use the format in [MISSION-FORMAT.md](./MISSION-FORMAT.md).
- `Resources.md` — a curated index of high-trust sources to ground your teaching. Material worth ingesting (articles, videos, transcripts) is saved to the vault's global `Sources/` via the wiki-ingest flow (the `wiki-create` skill); `Resources.md` links into those source notes by `[[wikilink]]`. Use the format in [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md).
- `Glossary.md` — the canonical terminology for this workspace (markdown). Building it is itself part of learning. Durable, cross-cutting terms **graduate** to `Reference/` wiki concept notes (`type: wiki, page_type: concept`) — the vault's wiki _is_ the long-term glossary. Use the format in [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md).
- `./Records/*.md` — learning records: `type: learning-record` notes titled `0001-<dash-case-name>.md`, the number incrementing each time. These are the teaching equivalent of architectural decision records — they capture non-obvious lessons and key insights that drive future sessions and let you calculate the zone of proximal development. Use the format in [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md).
- `./lessons/*.md` — a directory of lessons. A **lesson** is a single `type: lesson` markdown note that teaches one tightly-scoped thing tied to the mission. This is the primary unit of teaching. Titled `0001-<dash-case-name>.md`, the number incrementing each time. See [Lessons](#lessons) below for what a lesson contains and how it relates to the wiki.

Reference material — cheat sheets, algorithm notes, syntax cards — is **not** a workspace artifact anymore. It's ordinary wiki content; see [Reference material](#reference-material) below for where it lives.

**Tooling:** every artifact above is a `.md` note, created and edited with `obsidian-cli` (`create`, `append`, `property:set`); surgical in-note edits use whichever targeted note-patch tool the runtime offers (Claude's Obsidian MCP integration); complex restructures are dispatched to `@note-editor`.

### Resolving the context (where the workspace lives)

The vault is **context-first**: folders convey context, and activity is a frontmatter facet, not a folder. There is no top-level `Learning/` folder — instead, place the workspace under the context the topic belongs to, and mark the activity with `type: learning-mission` + `tags: [learning]` so a query can still gather "all my learning" across contexts.

Infer the best-fit context from the topic using the vault's Location Decision Tree (in the vault's `.claude/CLAUDE.md`), **propose a path, and confirm with the user** before creating anything:

- Technical / programming topic → `Reference/Developer/<Topic>/`
- DevOps / infrastructure topic → `Reference/Infrastructure/<Topic>/`
- Hobby topic → `Hobbies/<Area>/<Topic>/`
- Work-tied topic → `Work/<…>/<Topic>/` (your employer/client context folder)
- A standalone personal interest with no clean home (a language, an instrument) → propose your best guess and let the user redirect

Topic folders use **Title Case with spaces** (`Postgres MVCC`). The user owns the namespace call — when in doubt, ask.

## Philosophy

To learn at a deep level, the user needs three things:

- **Knowledge**, captured from high-quality, high-trust resources
- **Skills**, acquired through highly-relevant interactive lessons devised by you, based on the knowledge
- **Wisdom**, which comes from interacting with other learners and practitioners

Before the `Resources.md` is well-populated, your focus should be to find high-quality resources which will help the user acquire knowledge. Never trust your parametric knowledge.

Some topics may require more skills than knowledge. Learning more about theoretical physics might be more knowledge-based. For yoga, more skills-based.

### Fluency vs Storage Strength

You should be careful to split between two types of learning:

- **Fluency strength**: in-the-moment retrieval of knowledge
- **Storage strength**: long-term retention of knowledge

Fluency can give the user an illusory sense of mastery, but storage strength is the real goal. Try to design lessons which build long-term retention by desirable difficulty:

- Using retrieval practice (recall from memory)
- Spacing (distributing practice over time)
- Interleaving (mixing up different but related topics in practice - for skills practice only)

## Altitude: what a lesson binds to

Learning a concept *through* a real codebase — e.g. learning auth via the stack the user's project actually uses — is the productive default. The user learns only the approaches that fit their work, not generic alternatives that don't. But it sets a trap: if a lesson binds to volatile implementation detail, it rots every time the code moves. Avoid the trap by pitching every lesson at the right **altitude**. Three layers:

- **Concept** — the durable idea being taught (how token verification works; per-request scope resolution; RBAC). This is the *subject*. Lessons **always** bind here.
- **Stack lens** — the specific technologies and patterns the user chose to learn through (Okta + OIDC; role-based authz; FastAPI + dependency injection). Semi-durable: it moves only on *major* changes (migrating off Okta; RBAC → ABAC). Lessons bind here too — it is the productivity win, and it is recorded in `Mission.md` (the `stack_lens:` field) so every lesson stays grounded in it and off-stack approaches stay out of scope.
- **Wiring** — the exact code: which file, which line, which provider, a field's signature, an enum's member count. Volatile; changes on any refactor. Lessons **never** bind here. Wiring appears only as pinned, illustrative snapshots (see "Citing a live codebase") — there to make the concept concrete, never as the thing being taught.

**The test:** if a fact would be falsified by a refactor that does *not* change the approach, it is wiring — keep it out of the lesson's load-bearing claims. A lesson should remain correct after the code is reorganised, as long as the stack lens still holds.

This is also the boundary of the skill. `teach` is for **concept + stack lens** (durable). Understanding *how the current code does it today* — onboarding to a codebase, or digesting a specific PR — is **wiring-altitude** and perishable; that belongs in a code-grounded session or review tooling that reads `HEAD`, not in stored lessons. Don't route wiring-level "how does our code work right now" jobs into `teach`.

## Lessons

A lesson is the main thing you produce — the unit in which knowledge and skills reach the user. Each lesson is one `type: lesson` markdown note, saved to `./lessons/` inside the workspace folder and titled `0001-<dash-case-name>.md` where the number increments each time. There is no HTML anywhere in this skill.

### The wiki owns content; the lesson owns pedagogy

A lesson and a wiki concept page can cover the same thing, but they differ by **tense**, not scope:

- **Wiki page = state.** "What is true about X." Optimized for re-reading, returned to.
- **Lesson = process.** "Get from not-understanding X to understanding it." Ordered by prerequisite and effortful retrieval, rarely revisited.

So prose lives **once**, on the wiki page — never copied into the lesson. The lesson **transcludes** it and wraps it in the teaching apparatus:

```
Reference/Developer/.../Postgres MVCC.md   ← the thing. Prose lives here.
<Workspace>/lessons/0007-mvcc.md           ← type: lesson
    ![[Postgres MVCC#Gist]]                ← transcluded, not copied
    + quiz (pure CSS)
    + practice / real-stakes prompt
    + links onward
```

If the concept the lesson needs doesn't have a wiki page yet, create one first (via `wiki-create`) — the lesson is not the place for durable prose to originate. A lesson that restates wiki content instead of transcluding it will drift the moment either side changes; a lesson that *is* the wiki page permanently pollutes reference material with quiz scaffolding. Neither is acceptable.

**Constraint — transclude only from canonical headings.** Heading embeds (`![[Page#Heading]]`) break silently on rename: no error, just a note that renders empty. To keep that risk bounded, lessons may embed only from a small canonical heading set — `## Gist` and its established peers — never an arbitrary heading picked for one lesson. If the wiki page doesn't yet have a `## Gist` section, add one rather than embedding something else.

**Known limitation:** a lesson cannot stage an explanation (simplify first, complicate later) unless the wiki page itself carries that staged structure — a single `## Gist` embed is one altitude. Accepted for now; revisit if it bites.

### Composing the lesson

A lesson should be **clear and scannable** — since the user will return to these later to review. Compose it from the shared **lesson design system** ([LESSON-DESIGN-SYSTEM.md](./LESSON-DESIGN-SYSTEM.md)) — the transclusion pattern above, a pure-CSS self-grading quiz, native collapsed callouts for reveals, and the vault's existing visual-vocabulary callouts (`key-idea`, `gotcha`, `good`, `bad`, `test`) rather than inventing lesson-specific ones. The system is a starting skeleton, **not a cage**: override or break it whenever a topic genuinely calls for something bespoke.

The lesson should be short, and completable very quickly. Learners' working memory is very small, and we need to stay within it. But each lesson should give the user a single tangible win that they can build on. It should be directly tied to the mission, and should be in the user's zone of proximal development.

If possible, open the lesson note for the user by running a CLI command.

Each lesson should link via wikilinks to other lessons, the wiki concept(s) it transcludes, and anything else relevant — the whole point of moving into the vault is that these links are real, queryable graph edges, not anchor-tag dead ends.

Each lesson should recommend a primary source for the user to read or watch. This should be the most high-quality, high-trust resource you found on the topic.

Each lesson should contain a reminder to ask followup questions to the agent. The agent is their teacher, and can assist with anything that's unclear.

## The Mission

Every lesson should be tied into the mission — the reason that the user is interested in learning about the topic.

If the user is unclear about the mission, or `Mission.md` is not populated, your first job should be to question the user on why they want to learn this.

Failing to understand the mission will mean knowledge acquisition is not grounded in real-world goals. Lessons will feel too abstract. You will have no way of judging what the user should do next.

Missions may change as the user develops more skills and knowledge. This is normal — make sure to update `Mission.md` and add a learning record to capture the change. Confirm with the user before changing the mission.

When the topic serves a **real project the user already has** — a vault project page or a Linear project — tether the mission to it (the `project:` field in [MISSION-FORMAT.md](./MISSION-FORMAT.md)). This anchors the "why" in a concrete deliverable and lets a query answer "what am I learning for project X." But only link a project that genuinely exists — **never invent one just to have something to link.** A standalone personal interest needs no project, and a forced tie is worse than none.

If the user is learning a concept *through a particular stack* (see [Altitude](#altitude-what-a-lesson-binds-to)) — "teach me auth the way Meridian does it" — record that choice in the mission's `stack_lens:` field. It names the technologies and patterns lessons should teach *through* (and, by implication, the off-stack alternatives that stay out of scope). Every lesson then stays grounded in the approach that fits the user's work, and a stack-lens change becomes the trigger for a freshness pass.

## Zone Of Proximal Development

Each lesson, the user should always feel as if they are being challenged 'just enough'.

The user may specify an exact thing they want to learn. If they don't, figure out their zone of proximal development by:

- Reading their learning records in `./Records/`
- Figuring out the right thing to teach them based on their mission
- Teach the most relevant thing that fits in their zone of proximal development

### Entry altitude: question altitude × graph density

This is a separate question from the concept/stack-lens/wiring altitude above — it's about how deep *in* to start a new topic, not what a lesson's claims bind to. Two signals set the starting point:

1. **The question's own altitude.** "What is a database" is a gist request. "How does Postgres sync" names a descent.
2. **Density of the surrounding graph.** A sparse neighborhood (few notes, no `expands:` chains) means start at the gist. A dense neighborhood with existing `expands:` chains means the question is likely at the frontier — teach there, not from scratch.

Worked example: *"what is a database"* against an empty neighborhood earns a gist, not Postgres replication internals. The same question against a dense distributed-systems neighborhood may well be asking about the sync engine.

### The calibration gate — mandatory, not advisory

Graph density is a real signal, but it has a sharp edge: **a note existing means the agent taught it, not that the user knows it.** Left unchecked, the agent bootstraps itself into believing the user is advanced because it wrote a lot of notes — the AI-as-substitute crutch that `Personal/Manual of Me/Learning/Learning Style.md` already names, in a new costume.

So the rule has three parts, and all three matter:

- Graph density sets **entry altitude** only — a fair proxy for familiarity and vocabulary, nothing more.
- `Records/` remains the **only** gate on claims of demonstrated understanding. A concept with a lesson but no learning record backing it is not "known" — it's "taught," which is a different fact.
- Where the two disagree — dense graph, thin or absent records — **ask**. Open the session with a one-line calibration check: _"you have six notes here and a JWKS descent — am I right that scope resolution is the frontier?"_

**Run this check before writing lessons, every time it's warranted — this is not a nice-to-have.** It's the guard that keeps the graph from becoming a self-confirming model of the user's knowledge: the agent inferring mastery from its own prior output rather than from evidence the user actually retained anything.

## Knowledge

Lessons should be designed around a skill the user is going to learn. The knowledge in the lesson should be only what's required to acquire that skill. You teach the knowledge first, then get the user to practice the skills via an interactive feedback loop.

Knowledge should first be gathered from trusted resources. Use `Resources.md` to keep track of them. Lessons should be littered with citations - links to external resources to back up any claim made. This increases the trustworthiness of the lesson.

For acquiring knowledge, difficulty is the enemy. It eats working memory you need for understanding.

### Owned textbooks (DEVONthink)

Before reaching for the web — and certainly before trusting your parametric knowledge — **survey the textbooks the user already owns in DEVONthink.** These are the highest-trust source class available: the user paid for them, chose to keep them, and they are *stable* (a textbook doesn't drift the way a live codebase or a moving web page does), so a citation into one stays valid.

When gathering or expanding resources for a topic:

- **Search DEVONthink first.** Use `mcp__devonthink__search_records` / `mcp__devonthink__lookup_records` (and `get_databases` to see what's available) to find textbooks relevant to the topic. Surface what you found to the user and let them confirm which are worth grounding lessons in.
- **Pull content to ground lessons, not to replace them.** Use `get_record_text` / `extract_record_content` to read the relevant passages and ground your explanations in what the book actually says — then cite it. Quote sparingly; the lesson teaches, the book is the authority behind the claim.
- **Cite by DEVONthink item link.** Record the textbook in `Resources.md` under Knowledge with its DEVONthink item link (`x-devonthink-item://<UUID>`, from `get_record_properties`) plus a page/chapter pointer where you can. See [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md).
- **Read-only.** Never create, move, tag, or modify records in the user's DEVONthink library — it is their reference collection, not a teaching workspace.

If no owned textbook covers the topic, say so and fall back to web sources via the normal ingest flow.

### Citing a live codebase

When a lesson references a codebase the user works in (e.g. `atlas-app`), treat it differently from an external article. An external article is stable; a live path is a **moving target** — the file gets renamed, the function gets refactored, the line numbers shift, and a lesson that was a perfect reference today rots into a stale one. A lesson is a durable artifact the user returns to; a bare `path/to/file.ts:42` citation breaks that promise.

So when you cite live code, **snapshot and pin**:

- **Snapshot inline.** Quote the relevant code directly in the lesson so it is self-contained. The embedded snippet — not the live file — is the reference. The user should never need to open the repo to understand the lesson.
- **Pin to an immutable ref.** Cite a commit SHA or permalink, never a live path on the default branch. Resolve the current SHA at authoring time (e.g. `git -C <repo> rev-parse --short HEAD`).
- **Stamp it as-of.** Label the snapshot with the repo, SHA, and date — e.g. `atlas-app@a1b2c3d (2026-06-15)` — so a future reader knows it is a snapshot and can diff against current code if they need to.

The pinned link is provenance; the inline snapshot is what the lesson teaches from. This keeps the lesson valid even after the path moves. Code snapshots are **wiring-altitude** (see [Altitude](#altitude-what-a-lesson-binds-to)): they illustrate the concept, they are never the lesson's load-bearing claim.

## Skills

If knowledge is all about acquisition, skills are about durability and flexibility. Make the knowledge stick.

For skill acquisition, difficulty is the tool. Effortful retrieval is what builds storage strength. Skills should be taught through interactive lessons. There are several tools at your disposal:

- Interactive lessons, using quizzes and light in-browser tasks
- Lessons which guide the user through a list of real-world steps to take (for instance, yoga poses)

Each of these should be based on a **feedback loop**, where the user receives feedback on their performance. This feedback loop should be as tight as possible, giving feedback immediately - and ideally automatically.

For quizzes, each answer should be exactly the same number of words (and characters, if possible). Don't give the user any clues about the answer through formatting.

### Calibrated real-stakes application

This user retains through **real stakes**, not sandbox drills (see the learning-style grounding above). So the strongest end-of-lesson move is to push them to apply the skill where it has a real consequence. But "real stakes" must be **calibrated** — for a work topic, sending them to make production edits mid-lesson would derail their actual throughput, which is a worse outcome than slightly weaker practice.

Pick the lightest rung that still carries a real consequence:

1. **Predict-then-verify** against real artifacts — "what will this function return / this pose feel like / this conjugation be? Now check." Real material, zero blast radius.
2. **Review, don't author** — have them critique a real open PR, a real config, a real recipe, against what the lesson taught. Judgment under real conditions without shipping anything.
3. **Explain to a real person** — the protégé effect; teaching a colleague or peer is high-stakes retrieval.
4. **Capture, don't execute** — if applying the skill surfaces real work, file a follow-up (e.g. a Linear ticket / a `/spec-flow capture`) instead of doing it now. The stake is real; the timing stays under the user's control.
5. **Do the thing** — a real edit, a real session, a real attempt — when the topic *is* the work and doing it now doesn't blow up something else.

**Only escalate the rung when the topic is genuinely work-tied and the action won't derail other work.** For non-work topics (a language, an instrument, a pose), rungs 3 and 5 are usually the real-stakes path. Match the rung to the topic; don't force a work-tie where none exists.

**Delivery — boxed task vs. teacher dialogue.** The rungs above choose *what* real-stakes action to pick; they don't dictate *how* the doing-gate is delivered. A common and often-better delivery — especially for learners who retain through pairing — is **in-chat dialogue**: the lesson closes with one or two free-response questions the learner answers *back to the teacher in the conversation*, and the teacher grades them and firms up gaps before the next lesson. This keeps the effortful-retrieval feedback loop tight while shedding the worksheet feel of a boxed assignment (which some learners simply skip — coverage is not retention). In-lesson multiple-choice quizzes still serve recognition; the closing dialogue serves recall. When a learner expresses this preference, record it in their `Mission.md` teaching preferences so every future lesson inherits it.

## Acquiring Wisdom

Wisdom comes from true real-world interaction - testing your skills outside the learning environment. This matters doubly for this user, whose retention depends on real stakes — push them toward it.

When the user asks a question that appears to require wisdom, your default posture should be to attempt to answer - but to ultimately delegate to a **community**.

A community is a place (online or offline) where the user can test their skills in the real world. This might be a forum, a subreddit, a real-world class (budget permitting) or a local interest group.

You should attempt to find high-reputation communities the user can join. If the user expresses a preference that they don't want to join a community, respect it — note that preference in `Mission.md` so future sessions don't keep proposing them.

## Reference material

While creating lessons, you should also build up reference material. Lessons can transclude from it — it's useful for tracking raw units of knowledge useful across lessons.

Lessons will rarely be revisited later — reference material will be. It should be the compressed essence of the lesson, in a format designed for quick reference.

Some learning topics lend themselves to reference:

- Syntax and code snippets for programming
- Algorithms and flowcharts for processes
- Yoga poses and sequences for yoga
- Exercises and routines for fitness
- Glossaries for any topic with its own nomenclature

**All of it is wiki content now — there is no `./reference/` workspace directory.** Under the wiki/lesson split (see [Lessons](#lessons)), a cheat sheet is unambiguously *state* — the most-returned-to artifact there is — so keeping it outside the graph as HTML would leave exactly the wrong content unlinked. Cheat sheets, algorithm cards, pose sequences, and syntax cards are `Reference/` wiki pages (`type: wiki, page_type: concept` or a suitable sibling `page_type`), created and maintained via `wiki-create` / `wiki-graduate` the same way any other wiki concept is. The **glossary** stays the workspace's own staging area, `Glossary.md` — a markdown note whose terms graduate into those wiki pages once they're durable and cross-cutting. Once a glossary exists, it should be adhered to in every lesson.

Print quality for these pages is a **rendering** concern, not a storage one — deliberately deferred (see `UPSTREAM.md`); if export quality matters later, the answer is a print CSS snippet plus an exporter, never a second stored copy.

### Keeping the durable layer fresh

Lessons are ephemeral — they're "rarely revisited later," so a stale lesson costs little. **Reference wiki pages are the opposite**: they exist *to be returned to*, so a stale one actively misleads the user every time they reach for it. The freshness obligation lives here, on the durable layer — not on lessons.

When a reference wiki page carries pinned code citations (per "Citing a live codebase"), it can silently rot as the codebase moves past the pinned ref. So run a **freshness check** — modeled on the same posture as a decision/code drift audit. Calibrate it to altitude (see [Altitude](#altitude-what-a-lesson-binds-to)): most citation drift is *wiring* and is cheap to absorb; the case that actually demands attention is a **stack-lens move**.

- **When:** at the start of a session that will lean on an existing reference page, or on demand ("is this cheat sheet still accurate?", "re-pin the trace map").
- **What:** re-resolve each pinned citation against the codebase's current `HEAD` and classify the drift by altitude:
  - **Wiring drift** (file moved, lines shifted, a provider relocated, a signature changed) — re-pin to the new SHA + bump the as-of stamp. Safe to do directly; the teaching is unaffected.
  - **Stack-lens move** (the *approach* changed — a new auth provider, RBAC → ABAC) — this is the real signal. It may mean the concept-level teaching is now taught through the wrong approach. **Do not silently rewrite** — surface it and let the user decide whether the reference page (and the mission's `stack_lens:`) needs updating.
- **Posture:** read-only and advisory. A freshness pass may re-pin wiring quietly, but must never quietly change what a page *claims*. Trigger a full pass on major (stack-lens) change, not on every refactor.
