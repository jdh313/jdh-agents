# Card Creation Principles

Detailed reference for creating effective Anki flashcards.

## The Minimum Information Principle

The most important rule in flashcard creation: **one fact per card**.

### Why It Matters

- Smaller cards are easier to schedule (Anki can target weak spots)
- Simpler recall = faster review = more consistent practice
- Failed cards don't drag unrelated knowledge down with them

### Breaking Down Complex Ideas

| Complex Idea | Atomic Cards |
|--------------|--------------|
| "The French Revolution started in 1789, overthrew the monarchy, and established a republic" | Card 1: "When did the French Revolution begin?" → "1789" |
| | Card 2: "What form of government did the French Revolution overthrow?" → "Monarchy" |
| | Card 3: "What form of government did the French Revolution establish?" → "Republic" |

### Formula Example

Instead of: "What is the quadratic formula?"

Create:
1. "In the quadratic formula, what appears under the square root?" → "b² - 4ac"
2. "In the quadratic formula, what is the denominator?" → "2a"
3. "What is the discriminant in a quadratic equation?" → "b² - 4ac"

## Self-Contained Context

Each card must provide enough context to understand the question without external reference.

### Context Checklist

Before finalizing a card, verify:
- [ ] A stranger could understand what's being asked
- [ ] No pronouns without antecedents ("What is it?")
- [ ] Domain is clear if ambiguous terms exist
- [ ] Time period/location specified if relevant

### Examples

| Needs Context | Self-Contained |
|---------------|----------------|
| "When was it founded?" | "When was the United Nations founded?" |
| "What causes it?" | "What causes tides on Earth?" |
| "Who wrote it?" | "Who wrote '1984'?" |
| "Define synthesis" | "In chemistry, define synthesis reaction" |

## Unambiguous Questions

Questions should have exactly one correct answer.

### Ambiguity Types to Avoid

**Subjective questions:**
- Bad: "Why is democracy important?"
- Good: "What document established democracy in Athens?" → "Reforms of Cleisthenes (508 BC)"

**Multiple valid answers:**
- Bad: "Name a programming language"
- Good: "What programming language was created by Guido van Rossum?" → "Python"

**Vague scope:**
- Bad: "What are the effects of caffeine?"
- Good: "What neurotransmitter does caffeine block?" → "Adenosine"

## Card Type Selection

### Basic Cards

Use when:
- Term → definition relationships
- Question → single answer
- Concept → explanation
- Cause → effect (one direction)

### Basic (and reversed)

Use when:
- Bidirectional recall is valuable
- Vocabulary/translations
- Symbol ↔ meaning
- Name ↔ face

Avoid when:
- Answer is a long explanation (awkward as a question)
- Relationship is inherently one-directional

### Cloze Deletions

Use when:
- Memorizing definitions in exact wording
- Formulas or equations
- Sequences or ordered lists
- Fill-in-the-blank style recall

#### Cloze Best Practices

**One deletion per card (usually):**
```
Good: "The {{c1::mitochondria}} is the powerhouse of the cell"
Creates: 1 card

Problematic: "{{c1::Mitochondria}} are {{c2::organelles}} that produce {{c3::ATP}}"
Creates: 3 cards, but c2 and c3 lack helpful context when hidden
```

**Multiple deletions only when tightly related:**
```
Acceptable: "The {{c1::heart}} has {{c2::four}} chambers"
Both deletions test related facts, and each has enough context
```

**Keep surrounding context meaningful:**
```
Bad:  "{{c1::X}} is {{c2::Y}}" — no context helps recall
Good: "In cellular biology, {{c1::mitochondria}} are known as the powerhouses of the cell"
```

## ADHD-Aware Adaptations

These principles help maintain focus and prevent overwhelm.

### Externalized Context

Every card must be self-contained because working memory may not hold prior context:
- Never assume "you know what I mean"
- State full context even if it feels redundant
- Treat each card as if reviewed in isolation (because it will be)

### Clear Stopping Points

Batches of 5-10 cards provide natural breaks:
- Prevents perfectionism spiral ("just one more card...")
- Allows progress assessment
- Enables clean session boundaries

### Action Over Analysis

Generate cards promptly rather than over-optimizing:
- Good enough > perfect
- First draft can be edited later
- Momentum matters more than perfection

### Guided Structure

Present choices rather than open-ended decisions:
- "Add to [Deck A] or [Deck B]?" not "Which deck?"
- "These 7 cards look ready. Approve or edit?" not "What do you think?"
- Default recommendations with override option

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Testing multiple facts | Hard to schedule, partial failures | Split into atomic cards |
| Vague questions | Multiple valid answers | Add specificity |
| No context | Can't understand without external ref | Include context in question |
| Too many cloze deletions | Cards become guessing games | One deletion per card |
| Overly long answers | Hard to recall verbatim | Break into pieces or rephrase |
| Testing trivia | Low value, high volume | Focus on meaningful knowledge |
