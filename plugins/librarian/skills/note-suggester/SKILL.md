---
name: note-suggester
description: >
  Use Skill(note-suggester) during coding sessions to recognize
  reusable knowledge worth capturing. Suggests note captures inline when: debugging
  approaches work, patterns emerge, decisions are made with rationale, or techniques
  could apply elsewhere. Batches suggestions for end-of-session summary.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(obsidian-cli *)
---

Apply the runtime mappings in [`../../RUNTIME.md`](../../RUNTIME.md).

# Note Suggester

You help the user build their knowledge base by recognizing when something
is worth capturing in Obsidian.

## What's Worth Capturing?

Suggest a note when you encounter:

1. **Decisions with rationale** — "We chose X because Y"
2. **Debugging approaches that worked** — Steps that solved a tricky problem
3. **Patterns or techniques** — Reusable code patterns, architectural approaches
4. **Gotchas or surprises** — Things that weren't obvious, edge cases
5. **Cross-project knowledge** — Something useful beyond this specific task

## What's NOT Worth Capturing?

Skip suggesting for:
- Routine refactors following existing patterns
- Typo fixes or formatting changes
- Single-use solutions specific to one context
- Things already documented in the vault
- Minor configuration tweaks

## How to Suggest

### Inline (During Work)

When you notice something capture-worthy during active work, add a brief,
non-interrupting suggestion at the end of your response:

```
[Your main response here...]

---
> This debugging approach might be worth capturing in `50 Developer Notes/Patterns/`.
```

**Keep inline suggestions:**
- Brief (one line)
- Non-blocking (don't interrupt flow)
- Actionable (suggest location)

### Batch Tracking

Mentally track potential captures throughout the session. At natural breakpoints
or session end, present them together:

```markdown
## Session Captures

During this session, these items seemed worth noting:

| # | Topic | Type | Suggested Location |
|---|-------|------|-------------------|
| 1 | Lambda cold start mitigation | Pattern | `50 Developer Notes/Patterns/` |
| 2 | Gateway API 429 retry behavior | Gotcha | `80 Waites/Repos/Gateway Config API.md` (append) |
| 3 | Decision: chose Pydantic over attrs | Decision | `80 Waites/ADRs/` |

Want me to draft any of these?
```

## Size Guidance

Determine the right capture type based on content size:

| Content Size | Capture Type | Destination |
|--------------|--------------|-------------|
| 1-3 sentences | Quick capture | Daily note under `## Captured` |
| 1 paragraph + example | Mini note | Daily note or append to existing |
| Multi-paragraph with structure | Proper note | Appropriate folder with template |

## Capture Categories

### 1. Debugging Wins

When a debugging approach solves a tricky problem:

```
> This debugging sequence (check logs → verify config → restart service)
> solved the Lambda timeout. Worth capturing in `50 Developer Notes/Patterns/`?
```

### 2. Patterns Discovered

When you identify a reusable pattern:

```
> The repository pattern we implemented here could apply to other services.
> Suggest adding to `50 Developer Notes/Patterns/Repository Pattern.md`?
```

### 3. Decisions Made

When a decision is made with clear rationale:

```
> The decision to use JWT over session tokens (for scalability) would make
> a good ADR in `80 Waites/ADRs/`.
```

### 4. Gotchas Found

When you discover something non-obvious:

```
> This FastAPI dependency injection gotcha (order matters!) should probably
> be added to your FastAPI notes.
```

### 5. Cross-Project Knowledge

When something applies beyond the current project:

```
> This AWS Lambda pattern (provisioned concurrency + warming) is useful
> across projects. Worth a note in `50 Developer Notes/`?
```

## Before Suggesting

Always consider:

1. **Is it already documented?** — Quick vault search first
2. **Is it truly reusable?** — Would this help in other contexts?
3. **Is now the right time?** — Don't interrupt critical debugging
4. **What's the right size?** — Quick capture vs. proper note

## Search Before Capture

Before suggesting a new note, search the vault:

```bash
obsidian-cli search query="topic keywords" format=json
```

If related content exists:
- Suggest appending instead of creating
- Reference the existing note path
- Explain what would be added

## Presenting Suggestions

**ADHD-Friendly Format:**
- One suggestion at a time (inline)
- Batched summary at breakpoints
- Clear location recommendations
- Easy yes/no decisions

**Example Batch Summary:**
```markdown
## Session Captures (3 items)

### 1. Lambda Cold Start Pattern
- **What:** Provisioned concurrency + pre-warming approach
- **Why capture:** Useful across AWS projects
- **Where:** `50 Developer Notes/Patterns/Lambda Cold Start Mitigation.md`
- **Size:** Proper note (needs code examples)

### 2. Gateway Rate Limiting Gotcha
- **What:** 429 responses need exponential backoff, not fixed retry
- **Why capture:** Easy to forget, bit us twice
- **Where:** Append to `80 Waites/Repos/Gateway Config API.md`
- **Size:** Quick capture (2-3 sentences)

---
Draft any of these? (1, 2, both, or skip)
```

## Always Remember

- **Ask before writing** — Never create/edit without explicit consent
- **Check existing notes first** — Extend rather than duplicate
- **Suggest location + template** — Make approval easy
- **Respect flow** — Batch when possible, don't interrupt critical work
- **Quality over quantity** — Better to suggest 2 good captures than 10 mediocre ones
