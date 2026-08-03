# Follow-up mode: transcript arrived after restructure

When a transcript arrives for a meeting whose note is already in the slim log shape, run the pipeline in diff-and-correct mode rather than treating the transcript as a fresh restructure input.

## Preconditions

- Meeting note is already reshaped: `## Topics covered` contains at least one `→ [[Destination#Section]]` outbound link. Absent that, treat the input as a fresh restructure and use the main workflow.
- Transcript is filed at `Sources/YYYY-MM-DD Transcript — ...md` following the schema in the `meeting-notes` skill's `references/transcript-sources.md`. If provided inline, file it first via `meeting-notes` before continuing.

## Workflow

### 1. Build E (already-extracted set)

Walk the meeting note's `## Topics covered`. For each `[[Destination#Section]]`:

- Read the destination, locate the section.
- Collect bullets and prose carrying this meeting's footnote ID (and any topic-variant IDs such as `2026-04-21-ops-tool`).
- These are the already-extracted claims. Capture each verbatim — they become set E.

Also capture the meeting note's `## Quotable` block — quotes already preserved verbatim shouldn't get re-canonicalized.

### 2. Compute T − E (new facts) — subagent pass #1

Dispatch a foreground `general-purpose` subagent:

```
Given (a) a transcript and (b) a set of claims already extracted from
an earlier pass, classify each durable fact in the transcript as:
- already-represented — semantically covered by an E-claim (cite which)
- new-candidate — durable fact not in E
- ephemeral — not worth extracting

Return only new-candidates, each with the transcript line(s) that
support it. Do not propose destinations — that's the main agent's job.

Transcript: <absolute path>
E (already-extracted claims):
1. "<verbatim claim>" — cited by [^<id>] on [[<page>#<section>]]
2. ...
```

Semantic, not textual. "Each hospital deployment has its own AWS account" in E is equivalent to "we spin up a fresh AWS account per hospital" in T.

### 3. Compute drift within E (corrections) — subagent pass #2

Dispatch a second foreground subagent (separate from pass #1 — different operation, different stopping conditions):

```
For each claim in E, find the transcript line(s) that support it.
Verdicts:
- matches — faithful
- certainty-drift — hedge ("maybe", "hoping to", "might") disappeared
- attribution-drift — person cited in footnote didn't actually say it
- precision-drift — numbers/dates/names/quantifiers diverged
- unsupported — no transcript line supports the claim

Return the table. Do not propose rewrites.

Transcript: <absolute path>
E: [same list as pass #1]
```

### 4. Assemble the delta map — pause for approval

Present three panels:

```markdown
## Delta map

### New facts
| Transcript evidence | Destination | Section | Flags |
|---|---|---|---|
| "00:05 Stevie: non-free Zoom for >40min calls" | [[People/Stevie Nicks]] | ## Onboarding notes | minor — consider skipping |

### Corrections
| Page#Section | Current prose | Transcript evidence | Proposed rewrite | Verdict |
|---|---|---|---|---|
| [[Lighthouse#Roadmap]] | "Move to open-source models later in 2026" | "hoping to move... depends on Bedrock capacity" | "Plan to move to open-source models later in 2026, contingent on Bedrock capacity." | certainty-drift |

### Already represented (audit — no action)
- per-hospital AWS account → [[Lighthouse#Architecture]]
- <200 cases/month → [[Lighthouse#Usage]]
```

The audit panel is how the user sanity-checks that pass #1 didn't over-filter.

Flags to surface on new-facts rows:

- **minor** — borderline durable, user may want to skip.
- **re-classification** — already-represented but on the wrong page; propose the move.
- **expands topic** — topic already on canonical page; the new fact extends rather than duplicates.

Scope guard: if corrections outnumber new facts, surface that up front — the original extraction was probably rushed and the user may want to re-review the whole meeting rather than drown in per-row approvals. If new facts > 10 or corrections > 5, propose staging into rounds.

Wait for approval before editing.

### 5. Apply — two gates

- **New facts** apply as a batch after user approval. Same rules as main step 4 (Edit over Write, canonical-reference tone, destination clustering). Reuse the existing footnote ID for this meeting — do not invent a new one.
- **Corrections** apply per-row with per-row approval. Touching already-distributed prose is higher-stakes than appending; the note-taker's original phrasing may have been a deliberate editorial choice.

### 6. Upgrade footnote bodies (once per destination page)

Rewrite each destination's footnote body to cite both sources:

```markdown
[^2026-04-21-bruce]: Per [[Bruce Springsteen]] in [[Work/Meetings/2026-04-21 Intro with Bruce Springsteen]] (transcript [[Sources/2026-04-21 Transcript — Intro with Bruce Springsteen]]).
```

The footnote ID does not change — only the body. Existing references keep working.

### 7. Cross-link the transcript on the meeting note

Add to the meeting note frontmatter if missing:

```yaml
transcript: "[[Sources/2026-04-21 Transcript — Intro with Bruce Springsteen]]"
```

Bump `date_updated` on the meeting note.

### 8. Verify

Main step-7 checklist, plus:

- [ ] Transcript linked from meeting note via `transcript:` frontmatter.
- [ ] Every footnote body on touched destination pages cites both meeting note and transcript.
- [ ] Corrections landed as Edits that preserve surrounding prose (not rewrites of entire sections).

## Edge cases

- **Unsupported-in-transcript is not always wrong.** Could mean (a) note-taker fabricated, (b) side conversation outside recording, (c) transcript incomplete. Flag, don't auto-remove.
- **Relay upgrades.** Transcript may reveal the cited speaker was relaying someone else. Keep person-in-the-room as the footnote attribution (main workflow rule), but surface the relay in body: "Per [[Bruce]] (relaying [[Freddie]]): …"
- **Quotable drift.** Verbatim quotes in the meeting note's `## Quotable` must be corrected literally when transcript disagrees — that's the one case where prose should match exactly.
- **Entirely-missed topics.** If the transcript contains a thread absent from `## Topics covered`, that's bulk new material. Also offer to add a bullet to the meeting note's `## Topics covered` so the log reflects the thread existed.
