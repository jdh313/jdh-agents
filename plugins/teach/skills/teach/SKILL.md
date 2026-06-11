---
name: teach
description: Teach the user a new skill or concept over multiple sessions, building a teaching workspace in the Obsidian vault — a mission, resources, HTML lessons, a glossary, and learning records — grounded in the user's documented learning style and high-trust sources. Use when the user says "teach me X", "I want to learn X", or "/teach". Adapted from mattpocock/skills (MIT, © 2026 Matt Pocock).
disable-model-invocation: true
argument-hint: "What would you like to learn about?"
allowed-tools: Bash(obsidian-cli *), Write, Read, mcp__obsidian-mcp__patch_note
upstream:
  repo: mattpocock/skills
  path: skills/productivity/teach
  reviewed_sha: 694fa30311e0
  reviewed: 2026-06-12
  status: reviewed
---

The user has asked you to teach them something. This is a stateful request — they intend to learn the topic over multiple sessions.

This adaptation routes the durable artifacts into the **Obsidian vault** (`~/Loose Ends/`) as real notes, while keeping lessons and cheat sheets as self-contained HTML files inside the workspace folder.

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
- `./lessons/*.html` — a directory of lessons. A **lesson** is a single, self-contained HTML output that teaches one tightly-scoped thing tied to the mission. This is the primary unit of teaching. Titled `0001-<dash-case-name>.html`, the number incrementing each time.
- `./reference/*.html` — print-beautiful HTML cheat sheets, reference algorithms, syntax cards, pose sequences — compressed learnings designed for quick reference. They should be beautiful documents which print out well.

**Tooling:** `.md` notes are created and edited with `obsidian-cli` (`create`, `append`, `property:set`); surgical in-note edits use `mcp__obsidian-mcp__patch_note`; complex restructures are dispatched to `@note-editor`. The `.html` lessons and reference docs are written with the `Write` tool — they are non-markdown vault assets and live inside the workspace folder so their relative anchor links resolve.

### Resolving the context (where the workspace lives)

The vault is **context-first**: folders convey context, and activity is a frontmatter facet, not a folder. There is no top-level `Learning/` folder — instead, place the workspace under the context the topic belongs to, and mark the activity with `type: learning-mission` + `tags: [learning]` so a query can still gather "all my learning" across contexts.

Infer the best-fit context from the topic using the vault's Location Decision Tree (in the vault's `.claude/CLAUDE.md`), **propose a path, and confirm with the user** before creating anything:

- Technical / programming topic → `Reference/Developer/<Topic>/`
- DevOps / infrastructure topic → `Reference/Infrastructure/<Topic>/`
- Hobby topic → `Hobbies/<Area>/<Topic>/`
- Work-tied topic → `Carta/<…>/<Topic>/`
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

## Lessons

A lesson is the main thing you produce — the unit in which knowledge and skills reach the user. Each lesson is one self-contained HTML file, saved to `./lessons/` inside the workspace folder and titled `0001-<dash-case-name>.html` where the number increments each time.

A lesson should be **beautiful** — clean, readable typography and layout — since the user will return to these later to review. Think Tufte.

The lesson should be short, and completable very quickly. Learners' working memory is very small, and we need to stay within it. But each lesson should give the user a single tangible win that they can build on. It should be directly tied to the mission, and should be in the user's zone of proximal development.

If possible, open the lesson file for the user by running a CLI command.

Each lesson should link via HTML anchors to other lessons and reference documents (relative paths within the workspace folder).

Each lesson should recommend a primary source for the user to read or watch. This should be the most high-quality, high-trust resource you found on the topic.

Each lesson should contain a reminder to ask followup questions to the agent. The agent is their teacher, and can assist with anything that's unclear.

## The Mission

Every lesson should be tied into the mission — the reason that the user is interested in learning about the topic.

If the user is unclear about the mission, or `Mission.md` is not populated, your first job should be to question the user on why they want to learn this.

Failing to understand the mission will mean knowledge acquisition is not grounded in real-world goals. Lessons will feel too abstract. You will have no way of judging what the user should do next.

Missions may change as the user develops more skills and knowledge. This is normal — make sure to update `Mission.md` and add a learning record to capture the change. Confirm with the user before changing the mission.

## Zone Of Proximal Development

Each lesson, the user should always feel as if they are being challenged 'just enough'.

The user may specify an exact thing they want to learn. If they don't, figure out their zone of proximal development by:

- Reading their learning records in `./Records/`
- Figuring out the right thing to teach them based on their mission
- Teach the most relevant thing that fits in their zone of proximal development

## Knowledge

Lessons should be designed around a skill the user is going to learn. The knowledge in the lesson should be only what's required to acquire that skill. You teach the knowledge first, then get the user to practice the skills via an interactive feedback loop.

Knowledge should first be gathered from trusted resources. Use `Resources.md` to keep track of them. Lessons should be littered with citations - links to external resources to back up any claim made. This increases the trustworthiness of the lesson.

For acquiring knowledge, difficulty is the enemy. It eats working memory you need for understanding.

## Skills

If knowledge is all about acquisition, skills are about durability and flexibility. Make the knowledge stick.

For skill acquisition, difficulty is the tool. Effortful retrieval is what builds storage strength. Skills should be taught through interactive lessons. There are several tools at your disposal:

- Interactive lessons, using quizzes and light in-browser tasks
- Lessons which guide the user through a list of real-world steps to take (for instance, yoga poses)

Each of these should be based on a **feedback loop**, where the user receives feedback on their performance. This feedback loop should be as tight as possible, giving feedback immediately - and ideally automatically.

For quizzes, each answer should be exactly the same number of words (and characters, if possible). Don't give the user any clues about the answer through formatting.

## Acquiring Wisdom

Wisdom comes from true real-world interaction - testing your skills outside the learning environment. This matters doubly for this user, whose retention depends on real stakes — push them toward it.

When the user asks a question that appears to require wisdom, your default posture should be to attempt to answer - but to ultimately delegate to a **community**.

A community is a place (online or offline) where the user can test their skills in the real world. This might be a forum, a subreddit, a real-world class (budget permitting) or a local interest group.

You should attempt to find high-reputation communities the user can join. If the user expresses a preference that they don't want to join a community, respect it — note that preference in `Mission.md` so future sessions don't keep proposing them.

## Reference Documents

While creating lessons, you should also create reference documents. Lessons can reference these documents — they are useful for tracking raw units of knowledge useful across lessons.

Lessons will rarely be revisited later — reference documents will be. They should be the compressed essence of the lesson, in a format designed for quick reference.

Some learning topics lend themselves to reference:

- Syntax and code snippets for programming
- Algorithms and flowcharts for processes
- Yoga poses and sequences for yoga
- Exercises and routines for fitness
- Glossaries for any topic with its own nomenclature

Print-beautiful cheat sheets, algorithm cards, and pose sequences are HTML, saved to `./reference/`. The **glossary** is the exception — it is a markdown note, `Glossary.md`, because its terms graduate into the vault's wiki. Once a glossary exists, it should be adhered to in every lesson, and durable cross-cutting terms should be promoted to `Reference/` wiki concept notes via the `wiki-create` / `wiki-graduate` skills.
