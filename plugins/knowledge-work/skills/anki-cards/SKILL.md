---
name: anki-cards
description: >
  This skill should be used when creating Anki flashcards from content.
  Trigger phrases include "create flashcards", "make anki cards", "add to anki",
  "flashcard this", "turn into cards", "help me remember this", "I want to
  remember this", "remember this", "memorize this".
argument-hint: "[content to turn into flashcards]"
allowed-tools:
  - mcp__anki__list_decks
  - mcp__anki__modelNames
  - mcp__anki__modelFieldNames
  - mcp__anki__getTags
  - mcp__anki__addNote
  - mcp__anki__findNotes
  - mcp__anki__sync
  - AskUserQuestion
---

# Anki Flashcard Creator

Create quality Anki flashcards from content using the minimum information principle.

## Scope

This skill handles **card creation only**. Review sessions are a separate workflow.

## MCP Tools

| Tool | Purpose |
|------|---------|
| `list_decks` | Discover available decks for card placement |
| `modelNames` | List available note types (Basic, Cloze, etc.) |
| `modelFieldNames` | Get fields required for a note type |
| `getTags` | Check existing tags for consistency |
| `addNote` | Create the flashcard |
| `findNotes` | Verify cards were created |
| `sync` | Push changes to AnkiWeb |

## Card Types

| Type | Use Case | Example |
|------|----------|---------|
| **Basic** | Conceptual understanding, comparisons, "why" questions | "What is X?" → "X is..." |
| **Basic (and reversed)** | Bidirectional recall needed | Vocabulary, translations |
| **Cloze** | Sequences, syntax recall, ordered lists, fill-in-the-blank definitions | "Phases: {{c1::timers}} → {{c2::poll}} → {{c3::check}}" |

**Selection rule:** If the answer requires explanation or nuance, use Basic. If testing recall of a specific term/sequence within known context, use Cloze.

## Card Creation Principles

See `assets/card-principles.md` for detailed guidance. Key rules:

### Minimum Information Principle

One fact per card. Break complex ideas into atomic, testable units.

| Bad | Good |
|-----|------|
| "Explain the water cycle" | "What drives evaporation in the water cycle?" → "Heat from the sun" |
| "List the planets" | "How many planets are in our solar system?" → "8" |

### Self-Contained Context

Each card must be understandable without external reference. Include enough context to trigger recall.

| Bad | Good |
|-----|------|
| "What is it?" | "What is the capital of France?" |
| "When did this happen?" | "When did World War II end?" |

### Unambiguous Questions

Questions should have a single, clear correct answer.

| Bad | Good |
|-----|------|
| "Why is Python popular?" (many valid answers) | "What year was Python first released?" → "1991" |

### Cloze Guidelines

- Use for definitions, formulas, sequences
- One deletion per card unless items are closely related
- Keep surrounding context meaningful

```
Good: "{{c1::Mitochondria}} are the powerhouses of the cell"
Bad:  "{{c1::Mitochondria}} are the {{c2::powerhouses}} of the {{c3::cell}}"
```

### Supplemental Information Styling

Separate core knowledge (must remember) from optional context (helpful but not tested) using a horizontal rule and styled div:

```html
[Core answer - the testable fact]
<hr>
<div style="color: gray; font-size: 0.9em;">
[Emoji] [Supplemental info]
</div>
```

**Emoji prefixes:**
| Prefix | Use For |
|--------|---------|
| 💡 | Tips, best practices, performance hints |
| 🧠 | Mnemonics, memory aids, analogies |
| ⚠️ | Gotchas, common mistakes, warnings |

**Example:**
```html
In the <b>check phase</b> of the next event loop iteration.
<hr>
<div style="color: gray; font-size: 0.9em;">
⚠️ Despite the name, it's actually <i>less</i> immediate than <code>nextTick()</code>.
</div>
```

## Workflow

### 1. Analyze Content

Extract key concepts worth remembering. Identify:
- Facts (dates, definitions, formulas)
- Relationships (cause/effect, comparisons)
- Procedures (ordered steps)

### 2. Check Available Decks

```
Use: list_decks
```

Infer the appropriate deck from content topic. Present suggestion with alternatives.

### 3. Confirm Deck Selection

Ask user to confirm deck choice before proceeding:

```
The content appears to be about [topic]. I suggest adding these cards to:
- **[Suggested Deck]** (recommended based on content)

Other options:
- [Alternative 1]
- [Alternative 2]
- Create a new deck

Which deck should I use?
```

### 4. Check Existing Tags

```
Use: getTags
```

Maintain tag consistency by reusing existing tags where appropriate.

### 5. Propose Card Batch

Present draft cards (max 10 per batch) for review before creating:

```markdown
## Proposed Cards for [Deck Name]

### Card 1 (Basic)
**Front:** What is [question]?
**Back:** [Answer]
**Tags:** existing-tag, topic-tag
**Rationale:** Basic card chosen because [reason]

### Card 2 (Cloze)
**Text:** The {{c1::term}} is [definition]
**Tags:** existing-tag
**Rationale:** Cloze chosen for definition recall

---
Approve these cards? (or suggest edits)
```

### 6. Create Cards

After approval, use `addNote` for each card:

```
Use: addNote with:
- deckName: [confirmed deck]
- modelName: "Basic" or "Cloze"
- fields: { "Front": "...", "Back": "..." } or { "Text": "..." }
- tags: [approved tags]
```

### 7. Report Results

```markdown
## Created Cards

✅ Created 5 cards in [Deck Name]

| # | Type | Front/Text Preview | Tags |
|---|------|-------------------|------|
| 1 | Basic | "What is X?" | tag1, tag2 |
| 2 | Cloze | "The {{c1::term}}..." | tag1 |

Cards synced to AnkiWeb.
```

### 8. Offer Continuation

If content remains:

```
There's more content that could become flashcards. Continue with the next batch, or stop here?
```

This provides a clear stopping point.

## Batching Guidelines

- **Max 10 cards per batch** — prevents overwhelm, provides natural stopping points
- **Propose before creating** — user reviews and approves each batch
- **Clear continuation prompt** — explicit choice to continue or stop after each batch

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Create cards without showing drafts first | Always propose and get approval |
| Put multiple facts in one card | Split into atomic cards |
| Use vague questions ("What is it?") | Include full context in question |
| Create 20+ cards at once | Batch into groups of 5-10 |
| Assume deck without asking | Suggest and confirm deck choice |
| Invent new tags | Check existing tags first with `getTags` |
| Create both Basic and Cloze for same concept | Choose one format per concept (Basic for understanding, Cloze for syntax) |
| Use multiple unrelated cloze deletions (c1, c2) | Keep deletions closely related or use single deletion |
| Add redundant tags like "cloze" | Anki tracks card type automatically |
