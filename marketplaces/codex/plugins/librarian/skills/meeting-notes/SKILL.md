---
name: meeting-notes
description: >-
  This skill should be used when the user wants to format rough meeting notes
  and file them into the Obsidian vault. Trigger phrases include "format these
  meeting notes", "add these meeting notes to Obsidian", "I have notes from a
  meeting", "file these notes", or when the user pastes raw meeting notes with
  any context about participants, time, or topic. Also handles timestamped
  transcripts (e.g. from Zoom, Meet, Otter) — detects `HH:MM Speaker` patterns,
  saves the transcript verbatim to `Sources/`, and extracts the meeting note
  from it. Handles filename conventions, frontmatter, action-item cleanup, stub
  creation for new people and projects, and daily-note linking.
---

# Meeting Notes

## Overview

Transform rough meeting notes into a structured note in the user's
Obsidian vault at `~/Loose Ends/`. File meeting notes under
`${active_work_context}/Meetings/`, create stubs for any new people or
projects referenced, and ensure the daily note's Dataview query picks
them up via matching frontmatter.

This skill drafts interactively in the main session (metadata gathering,
action-item normalization, approval gate); `@vault-reader` performs
existence checks and `@note-editor` executes all writes.

## Configuration

Path references use `${active_work_context}` as a placeholder for the
top-level work-context folder. Before any vault write, read
`~/Loose Ends/.claude/librarian.local.md` and extract
`active_work_context` from its frontmatter. Substitute that value for
`${active_work_context}` everywhere below. Default to `Carta` if the
config file or key is missing. See
`${CLAUDE_PLUGIN_ROOT}/references/work-context-config.md` for full
substitution rules.

## Design contract

A meeting note must answer, without falling back to the transcript:

- **What was decided** — separable from stances that were held but not adopted.
- **Who owns each follow-up** — every open action item has an owner.
- **By when** — every open action item has a `by:` date or an explicit `open` marker. No exceptions.
- **What's empty vs. what's missing** — sections with nothing to record carry a literal `(none)` marker, never a blank body.

Drafts that fail these rules do not pass the approval gate in step 4. The transcript is a fallback for verbatim phrasing and context, not a retrieval crutch for binding facts.

## Vault tool usage

Use `obsidian-cli create name='...' content='...'` for the meeting note and any new people/project stub pages. Use `obsidian-cli backlinks file=<person>` to check existing pages before creating stubs. Use `obsidian-cli append file=<daily-note> content='...'` to add the meeting link to the daily note.

## When to Invoke

- User pastes raw meeting notes, bullet dumps, or voice-to-text output
  and asks to format/file them
- User mentions "I had a meeting with X" and wants it captured
- User asks for help turning a rough list into a proper note
- User pastes a timestamped transcript (`HH:MM Speaker\n<prose>`) from
  Zoom, Meet, Otter, or similar — handle as transcript input (see
  **Input Formats** below)

Do NOT invoke for:
- Quick single-line thoughts — use `note-capture` instead
- Formatting existing well-structured notes — user just needs direct edits
- Meeting *preparation* (agendas) — this skill is for post-meeting capture

## Input Formats

Two raw-input shapes are supported:

- **Rough notes** — freeform bullets, prose, or voice-to-text output.
  Existing workflow applies as-is.
- **Transcript** — timestamped speaker-split text, recognizable by
  repeated `HH:MM Speaker\n<prose>` blocks. The transcript is saved
  verbatim to `Sources/` as a citable reference, and the meeting note
  is extracted from it.

Detection heuristic: three or more consecutive `HH:MM <Name>\n` lines
indicate a transcript. Both formats converge at the draft-review gate
in step 4 — one review, regardless of input.

## Workflow

Follow this sequence. Do not skip the approval checkpoint — the user
reviews every draft before it's written.

### 1. Gather metadata

Ask for (or confirm) each of the following, in one message. Propose
defaults when possible:

- **Date and time range** — default to today if obvious from context
- **Participants** — names of everyone in the meeting
- **Meeting type** — 1:1, project sync, kickoff, onboarding call, etc.
- **Context/project** — which work area this ties to (used for `up:`
  or related links later)

### 2. Search the vault for existing references

For each participant and project/topic mentioned, dispatch to
`@vault-reader`:

```markdown
## Intent
check existence of people and projects referenced in this meeting

## Constraints
- People: search `People/` by first name and full name
- Projects: search `${active_work_context}/Projects/`
- Broader vault search by alias if unsure

## Input
- people: [<list of names>]
- projects: [<list of project/topic strings>]

## Output shape
For each input: {name, status: exists|missing, path?: <path>, aliases?: [...]}.
```

Report findings back and ask the user how to handle unresolved names
or projects (create stub now, leave as unresolved wikilink, or skip).

### 3. Draft the note

**If input is a transcript:**

1. **Verify the transcript's date.** Default to today, but scan the
   body for relative time references ("tomorrow we meet with X",
   "next Monday", "yesterday we decided...") that can be cross-checked
   against already-filed notes. If the transcript describes as
   *future* an event that has already happened (and has its own
   meeting note), the transcript is from an earlier date. Surface the
   inferred date at the approval gate — do not silently correct it.

2. **Check for an existing meeting note** matching this
   date/participants combo — search `${active_work_context}/Meetings/YYYY-MM-DD*.md`.
   Two sub-branches:

   - **A. No existing note (fresh meeting):** save transcript to
     `Sources/` (schema in `references/transcript-sources.md`),
     extract the meeting note (summary, topics, action items,
     verbatim quotes under `## Quotable` with timestamps like
     `> 00:15 Andrew: "..."`), add
     `transcript: "[[Sources/...]]"` to the new meeting note
     frontmatter, then continue with the standard drafting flow
     below.

   - **B. Existing note (late transcript):** Before writing, present
     the plan for approval — the `Sources/` path, the planned
     `transcript:` line (insert directly beneath `summary:` in the
     existing meeting note's frontmatter; beneath `participants:` if
     no `summary:`), and any judgment calls. Two calls matter most:
     **(a) inferred transcript date disagrees with user's stated
     date** — surface both with the evidence for each, ask which
     wins; **(b) pairing ambiguity** when multiple same-day meetings
     exist — disambiguate by participant overlap and topic keywords,
     never by date alone. After approval, dispatch to `@note-editor`:

     ```markdown
     ## Intent
     attach late transcript to existing meeting note

     ## Constraints
     - Write `Sources/<filename>.md` first (so `source_meeting:` exists
       before the forward link is added)
     - Then add `transcript: "[[Sources/<filename>]]"` to the existing
       meeting note's frontmatter, inserted directly beneath `summary:`
       (or beneath `participants:` if no `summary:`)
     - DO NOT modify the existing meeting note body (topics, quotable,
       action items, open questions). Body enrichment is
       `meeting-restructure` follow-up mode's job.

     ## Input
     - transcript source content (full): <verbatim>
     - existing meeting note path: <path>

     ## Output shape
     Confirm both files modified with paths and the line inserted.
     ```

     After the agent reports, surface the handoff to the user:
     "Transcript filed and linked. Run `meeting-restructure` next if
     you want to pull additional facts into canonical pages."

**When drafting a new meeting note** (rough-notes input, or
transcript sub-branch A) — use the template at
`assets/meeting-note-template.md` as a starting point. Fill in:

- Frontmatter (see Frontmatter Conventions below)
- Summary — 1–2 sentences, what was covered at a high level
- Topical sections — if the meeting had distinct topics, break into
  H2 sections per topic rather than one dump
- Action Items — split into **Open**, **Done**, and **Dropped**
  (see Action Item Handling below)

Present the full draft as a fenced code block for user review before
writing. **When the draft includes a transcript source file,
abbreviate its body as `[... full transcript verbatim,
00:00–HH:MM, N timestamped turns ...]`** — the structural review is
what matters; reviewing hundreds of speaker turns in a code block is
useless. (A "turn" is one `HH:MM Speaker` block, counted
unambiguously.) Call out any judgment calls (filename, time format,
merges, dropped items, inferred date) so the user can flag them.

### 4. Get approval

Before presenting the draft, run the validation checklist:

- [ ] Frontmatter has all required fields: `type`, `date`,
  `date_created`, `participants`, `summary`, `tags`.
  (`date_modified` is auto-managed by the vault's frontmatter
  plugin — do not write it manually.)
- [ ] Every standard H2 section has content or a literal `(none)`
  marker — no blank bodies.
- [ ] Every **Open** action item has `[owner:]` and `[by:]` (date or
  the literal `open`). `[src:]` present when a transcript exists.
- [ ] Every **Done** action item has `[owner:]` and `[src:]` (when
  transcript exists).
- [ ] Dates inside `[by:]` are absolute (`YYYY-MM-DD`) or the literal
  `open` — never "next week", "tomorrow", etc.

If any check fails, fix the draft before surfacing it to the user.
Do not shift the validation burden onto review.

Present the fixed draft. Wait for user approval before writing
anything. Iterate on the draft based on feedback, re-running the
checklist after each iteration.

### 5. Dispatch the writes

Hand the approved drafts to `@note-editor`:

```markdown
## Intent
file meeting note and any required stubs

## Constraints
- Write order: people stubs → project stubs → meeting note
- People stubs: use `~/Loose Ends/Templates/Person Note.md`, write to `People/<Full Name>.md`
- Project stubs: write to `${active_work_context}/Projects/<Project Name>.md`
- Meeting note: write to `${active_work_context}/Meetings/YYYY-MM-DD <Descriptive Title>.md`
- Schema: per `~/Loose Ends/.claude/rules/wiki.md`; meeting frontmatter per this skill's Frontmatter Conventions section

## Input
- people_stubs: [<full drafted content per stub>]
- project_stubs: [<full drafted content per stub>]
- meeting_note: <full drafted frontmatter + body>
- transcript_source: <full drafted content, if applicable>

## Output shape
Confirm each file created with its full path; list any unresolved wikilinks.
```

### 6. Daily note integration

The daily note at `Daily Notes/YYYY-MM-DD.md` contains a Dataview
query that auto-pulls any note with `type: meeting` and matching
`date`. As long as the meeting note has correct frontmatter, it will
appear automatically — no manual linking needed.

If the daily note doesn't yet exist for the meeting's date, that's
fine; the query will pick up the meeting when the daily note is
created.

### 7. Summarize & surface capturable decisions

After the writes complete, dispatch the drafted meeting body to
`@ndr:ndr-extractor` to spot any decisions worth capturing as ndr
atoms. Reusing the same extractor `/capture-decision` uses means one
canonical judgment — surfacing here and capture later see the same
candidates.

```markdown
## Intent
spot capturable decisions in a freshly filed meeting note

## Constraints
- Source is the drafted meeting body only (frontmatter + sections)
- Read-only — do not invoke the rest of the ndr pipeline
- Empty result is acceptable; many meetings produce no atom-worthy
  decisions

## Input
- source: <meeting note frontmatter + body, verbatim>

## Output shape
Standard ndr-extractor `{candidates: [{title, gist, quotes,
suggested_area, suggested_topic}]}`.
```

Then report:

- Files created (full paths)
- Files updated
- Unresolved wikilinks the user should know about
- **Capturable decisions** — only if the extractor returned a
  non-empty list. Surface titles only:

  ```
  Decision-shaped statements in this meeting:
    1. <candidate title>
    2. <candidate title>

  Run /capture-decision to formalize as ndr atoms — they're already
  recorded in the meeting note.
  ```

  Quotes and area/topic suggestions are held in the extractor's output
  but not shown; `/capture-decision` re-extracts if the user opts in.
  Empty list → omit the section entirely. Silence beats noise.

## Frontmatter Conventions

```yaml
---
type: meeting
date: YYYY-MM-DD
date_created: YYYY-MM-DD
participants:
  - "[[Jacob Hoehler|Me]]"
  - "[[Other Person]]"
summary: "One-line summary with [[Principal]] wikilinked; names the threads."
tags:
  - type/meeting
  - context/carta
---
```

> Do not write `date_updated` or `date_modified` manually — the
> vault's frontmatter plugin auto-maintains `date_modified` on every
> save. Downstream staleness checks (vault-inspect, meeting-restructure)
> read `date_modified` when present.

All fields above are required. Specifically:

- `type: meeting` — the Dataview query and `Meetings.base` both filter
  on this.
- `date:` — `YYYY-MM-DD` format to match `this.file.day` in the
  Dataview query.
- `date_created:` — set to the date the note is first written. Never
  changes after creation. The vault plugin may rewrite it to a
  long-form timestamp (e.g. `Friday, April 24th 2026, 5:21:47 pm`);
  preserve that form on subsequent edits — do not normalize it back
  to `YYYY-MM-DD`.
- `date_modified:` — auto-managed by the vault frontmatter plugin.
  Never write it manually; never bump it manually. Staleness checks
  read this field.
- `participants:` — list of wikilinks; always include
  `[[Jacob Hoehler|Me]]` first.
- `summary:` — one-line summary with principals wikilinked. Echoed as
  the first body line via `` `= this.summary` `` when the note is
  restructured. Required at creation so downstream consumers don't
  need to read the full body to get a headline.
- `context/carta` tag is standard for current work notes.

## Filename Conventions

- Format: `YYYY-MM-DD <Descriptive Title>.md`
- Title should be concise and topical (3–5 words typically)
- Examples:
  - `2026-04-20 Day 1 with Andrew.md`
  - `2026-04-20 Meeting with Matthew.md`
  - `2026-05-03 CartaOS Architecture Review.md`
- Avoid generic titles like "Meeting Notes" or "Standup"

## Body Conventions

### Time format

Use 24-hour: `**Time:** 14:00–15:00`. This is unambiguous and matches
the user's preference.

### Topical split

When a meeting covers distinct topics (e.g., project vision then dev
setup), use H2 sections per topic rather than one mixed bullet list.
If all action items/notes belong clearly to one topic, scope them
under that H2.

### Wikilinks

- Link the first mention of any person, project, tool, or concept
  that has (or could plausibly have) its own note
- For repeated mentions within a section, linking once is enough
- When a note name is long, use display-alias form:
  `[[Zed Editor|Zed]]`

### Callouts

Use sparingly, with strict meanings:
- `> [!warning]` — severe or hard to reverse
- `> [!note]` — a surprise or caveat
- `> [!tip]` — optional enhancement

### Empty sections — `(none)` marker

Any standard section present in a meeting note must either contain
content or carry a literal `(none)` marker. Never leave a heading
with a blank body or a bare empty bullet.

```markdown
## Open questions

(none)
```

Acceptable variants when more specific wording adds signal:
`(none raised in this meeting)`, `(none — covered in
[[2026-04-20 Day 1 with Andrew]])`. The point is unambiguous: the
author considered this section and had nothing to file, versus the
author forgot.

This applies to every standard H2 section: `## Summary`,
`## Open questions`, `## Action items`, any topic sections, and any
new sections added later (e.g. `## Decisions`, `## Cadence &
rhythm`). If a section has no content and no reason to exist, delete
the heading entirely rather than marking it `(none)`.

## Action Item Handling

Raw meeting notes often mix:
- Items already done during the meeting
- Open TODOs
- Items that were asked-about-and-answered (no longer TODOs)
- Duplicates (same item listed twice)

Normalize into three buckets with required metadata:

```markdown
**Open:**
- [ ] Item to do [owner: @person] [by: YYYY-MM-DD | open] [src: MM:SS]

**Done:**
- [x] Item already completed [owner: @person] [src: MM:SS]

**Dropped:**
- ~~Original item~~ — reason it's no longer needed
```

### Required metadata on action items

Every **Open** item must carry all three tags:

- `[owner: @person]` — the participant responsible. Use the same
  handle as the `@speaker` attribution convention elsewhere in the
  note. If the item is jointly owned, list both: `[owner: @jacob
  @andrew]`.
- `[by: YYYY-MM-DD | open]` — absolute date or the literal word
  `open`. **Never empty, never omitted.** `open` is the explicit
  marker for "no deadline was set" and must be used deliberately, not
  as a default. If the source used relative phrasing ("by Monday",
  "end of next week"), convert to absolute dates based on the
  meeting's `date:` field.
- `[src: MM:SS]` — timestamp in the paired transcript, if one exists.
  Omit only when no transcript is available for this meeting.

**Done** items require `[owner:]` and `[src:]` but not `[by:]` —
they're already complete. **Dropped** items need no metadata; the
strikethrough plus reason is enough.

### Approval-gate validation

Before presenting the draft for approval, verify:

- [ ] Every open item has `[owner:]`.
- [ ] Every open item has `[by:]` — either a date or the literal
  `open`. Missing `[by:]` is a blocker.
- [ ] Every item linked to a transcript has `[src:]`.

If any check fails, fix the draft before showing it to the user — do
not surface an invalid draft and ask the user to fill gaps. If a
deadline genuinely cannot be determined (not stated, not inferrable),
mark it `[by: open]` and flag the item in the judgment-calls block so
the user can set a date if they know one.

### Other rules

- Merge duplicates.
- If a question-as-TODO was answered during the meeting, drop it and
  capture the answer in a Notes section instead.
- If an item depends on someone else's action, note that inline after
  the metadata tags.
- Preserve original wording unless it's ambiguous out of context.

## Stub Creation

### New person

Use `~/Loose Ends/Templates/Person Note.md` and write to
`People/<Full Name>.md`. Fill in `company`, `title` from context if
known; leave other fields blank.

### New project

Lean stub at `${active_work_context}/Projects/<Project Name>.md`:

```markdown
---
type: project
tags:
  - context/carta
  - type/project
created: YYYY-MM-DD
---

# <Project Name>

<One-sentence description.>

## Related

- [[${active_work_context}/Meetings/...]]
```

Add more sections only if the user asks. The stub should not
speculate beyond what was said in the meeting.

## Template

See `assets/meeting-note-template.md` for the skeleton. Use it as a
starting point — delete sections that don't apply for this meeting.

## Transcript Sources

When the transcript branch fires in step 3, see
`references/transcript-sources.md` for the full `Sources/` frontmatter
schema, filename convention, verbatim-body rule, and
bidirectional-link pattern between the transcript and its paired
meeting note.

## Non-Goals

- This skill does not track open action items over time — that's the
  `meeting-followup` skill's job
- This skill does not draft agendas for upcoming meetings
- This skill does not transcribe audio — user pastes their own notes
  or a transcript from Zoom/Meet/Otter/etc.
