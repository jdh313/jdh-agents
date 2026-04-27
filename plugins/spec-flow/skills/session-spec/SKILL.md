---
name: session-spec
description: This skill should be used when the user wants to scaffold a dated working-session planning note in their Obsidian vault. Trigger phrases include "start working session", "scaffold session note", "plan today's session", "daily plan", "what am I working on today", "set up today's plan", or when the user is starting a new day on a project and wants the canonical Goal / Tiers / Components / Non-goals / Risks / Artifacts / Reflection template scaffolded for them. Detects project context from the current directory; prompts for the vault project folder if not detectable. Includes the `Decisions to promote to ADRs:` line in the Reflection section as the drift-prevention nudge that bridges session-scoped planning to the durable ADR layer.
---

# session-spec

Scaffold a dated working-session note in the user's Obsidian vault under the appropriate project folder. The note follows the template at `references/working-session-template.md` and is dated to today.

## Required skills

- **Skill(obsidian:obsidian-cli)** — for note creation and frontmatter handling

## When to invoke

- User starts a new day on a project and wants the day's plan scaffolded
- User says "let's start a working session", "scaffold today's plan", "daily plan", or similar
- User explicitly invokes after reading the previous session's reflection and wants today's note ready to fill

Do NOT invoke for:
- Per-task planning during agent work — that's plan mode's job
- Multi-month roadmaps or project-level planning — session notes are *daily* containers, not long-range plans
- Filling out an existing session note — direct edits are sufficient; this skill creates new notes

## Workflow

### 1. Determine project context

Check the current working directory for project signals:

```bash
# Look for a CLAUDE.md that references a vault project folder
rg -l "Loose Ends/[A-Za-z]+/Projects/" CLAUDE.md 2>/dev/null

# Or check for explicit project hint in repo root
test -f .spec-flow.toml && cat .spec-flow.toml
```

If detection succeeds, propose the detected project folder as the default. If it fails, ask the user:

- **Vault root** — usually `~/Loose Ends`, but confirm.
- **Project folder** — relative to vault root. Examples: `Carta/Projects/CartaOS`, `Personal/Projects/WireViz-ng`, `Hobbies/Lighthouse Audit`.

### 2. Compose the filename

```
<YYYY-MM-DD> Working Session.md
```

Use today's date. If the user is filing for a different date (catching up on yesterday, planning ahead), confirm the date explicitly before writing.

If a session note for that date already exists at the target path, **stop and ask** whether to:
- Open the existing note for editing instead (preferred — don't overwrite a real session)
- Append a suffix to differentiate (`<YYYY-MM-DD> Working Session — afternoon.md`)
- Cancel

Never silently overwrite.

### 3. Gather framing context (one short message)

Ask for or confirm:

- **One-line framing** — what today is for, in one sentence. Goes into the opening paragraph below the frontmatter.
- **Continuity from yesterday** — did yesterday end with a clear next step? If yes, surface it so it lands in the Goal section.
- **Single-thread or parallel-thread day** — affects how Components are structured. Default single-thread.

Keep this gathering tight: one message, propose defaults, accept terse answers. If the user says "just scaffold it, I'll fill in the details," skip straight to step 4 with placeholders intact.

### 4. Read the template

Read `references/working-session-template.md` (in this skill's plugin) for the canonical body. The template uses `{{TOKEN}}` placeholders that the skill substitutes:

- `{{TODAY}}` → ISO date `YYYY-MM-DD`
- `{{PROJECT}}` → project folder leaf name (e.g. `CartaOS`)
- `{{ONE_LINE_FRAMING}}` → user-provided framing sentence

Other placeholders (`{{Component one}}`, etc.) stay as literal placeholders for the user to fill in.

### 5. Show the draft

Present the full draft as a fenced code block before writing. Surface any judgment calls — date interpretation, project-folder ambiguity, single-vs-parallel thread choice — so the user can correct.

Wait for user approval. Iterate on feedback if needed.

### 6. Write via obsidian CLI

```bash
obsidian create path="<project-folder>/<YYYY-MM-DD> Working Session.md" content="..."
```

Use `obsidian create` rather than direct file write — it handles frontmatter consistency and triggers vault indexing.

### 7. Report

Tell the user:

- File path written (full vault-relative path)
- Date used
- Whether continuity from yesterday was carried forward
- Reminder of the Reflection section's `Decisions to promote to ADRs:` line — that's the drift-prevention bridge to the ADR layer at end of day

## Conventions to preserve

- **No H1 in the body.** The filename is the title. Body starts with the frontmatter, then the framing paragraph, then `## Goal`. (User-level vault convention.)
- **`(none)` markers, not blank bodies.** If a section has nothing to record, write `(none)` rather than leaving the heading bare. Matches `meeting-notes` skill convention.
- **Reflection section stays empty at scaffold time.** The placeholder *To be filled* is correct — the user fills it at end of day. Don't pre-populate.
- **Promotion line is non-negotiable.** The `Decisions to promote to ADRs:` line is the entire reason this skill exists alongside ADR tooling. Never omit it, even when the user asks for a "minimal" template.

## Non-goals

- Doesn't track or surface previous sessions — that's a vault-search task, not this skill's job.
- Doesn't write ADRs — promotion-line items are surfaced at end of day; an ADR-creation skill (deferred) handles the conversion.
- Doesn't validate that the project folder exists — `obsidian create` will surface that error if it does.
- Doesn't replace plan mode for in-task planning. Session notes are the day-level container around plan-mode work.
