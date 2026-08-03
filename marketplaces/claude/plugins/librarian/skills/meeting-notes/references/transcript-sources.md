# Transcript Sources

When the input is a transcript, save the verbatim text to `Sources/` with this frontmatter:

```yaml
---
owner: ai
type: source
source_type: transcript
source_meeting: "[[${active_work_context}/Meetings/YYYY-MM-DD <Title>]]"
source_participants:
  - "[[Jacob Hoehler|Me]]"
  - "[[Other Person]]"
date_ingested: YYYY-MM-DD
tags:
  - type/transcript
  - context/carta
---
```

## Filename

`Sources/YYYY-MM-DD Transcript — <meeting-note-title>.md`
(e.g. `2026-04-22 Transcript — Zoom Account Setup.md`). Title exactly matches the paired meeting note's filename title, prefixed with `Transcript — `. Generic meeting titles are fine — the prefix disambiguates.

## Tags

`type/transcript` plus the paired meeting note's context tag (e.g. `context/carta`). Do not mirror the paired note's topical tags — transcripts are source records, not topical content.

## Body structure

No H1 — the filename is the title.

Expected shape (all three are required):

1. **A one-line framing paragraph** linking to the paired meeting note. Without it the transcript file has no context outside its frontmatter. Examples:
   - 1:1: `Verbatim transcript of the 1:1 with [[Person]] on YYYY-MM-DD. Extracted meeting note: [[${active_work_context}/Meetings/...]].`
   - Multi-participant: `Verbatim transcript of the <topic> meeting with [[Person A]] and [[Person B]] on YYYY-MM-DD. Extracted meeting note: [[${active_work_context}/Meetings/...]].`
2. **A `## Transcript` H2.**
3. **The verbatim timestamped turns** below the H2.

The verbatim rule applies to the content *under* `## Transcript`: do not reformat the `HH:MM Speaker` lines, do not collapse whitespace, do not rewrite awkward phrasing. The framing paragraph above the H2 is not transcript content.

The source note is the citable record of what was literally said; the meeting note is the extraction.

## Scope — not wiki content

Transcripts are not wiki content and should not be routed through `wiki-create` (ingest mode). They live in `Sources/` but are not connected to the wiki hierarchy — no `up:`, no derived wiki page. The rationale: a transcript is a primary record of a conversation, not encyclopedic knowledge; its durable claims get extracted into the meeting note and then (optionally) restructured into canonical pages, which is where wiki-style content lives.

## Bidirectional link

- Meeting note frontmatter: `transcript: "[[Sources/YYYY-MM-DD Transcript — ...]]"`
- Transcript source frontmatter: `source_meeting: "[[${active_work_context}/Meetings/YYYY-MM-DD ...]]"`

Both directions allow backlink navigation and let `meeting-restructure`'s follow-up mode find the transcript by reading the meeting note's frontmatter alone.
