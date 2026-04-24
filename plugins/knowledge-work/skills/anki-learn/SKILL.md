---
name: anki-learn
description: >
  Research a topic and generate flashcard suggestions. This skill should be used
  when the user wants to build knowledge on a topic but doesn't have source content.
  Trigger phrases include "I need to learn", "help me understand", "build working
  memory on", "I want to know more about", "teach me about", "what should I know about".
argument-hint: "<topic to research>"
context: fork
agent: general-purpose
allowed-tools:
  - WebSearch
  - WebFetch
  - mcp__anki__list_decks
  - mcp__anki__getTags
  - mcp__anki__findNotes
  - mcp__anki__notesInfo
  - mcp__openmemory__search_memory
---

# Learning Researcher

Research a topic and produce a structured outline of key concepts suitable for Anki flashcards.

## Your Task

Research **$ARGUMENTS** and return a learning outline the user can review before creating flashcards.

## Process

### 1. Understand the Learning Goal

Parse the topic to identify:
- **Domain**: What field is this? (programming, history, science, etc.)
- **Scope**: Broad overview or specific subtopic?
- **Depth**: Beginner fundamentals or advanced patterns?

If ambiguous, note assumptions made.

### 2. Check Existing Knowledge

**Search OpenMemory** for prior learnings on this topic:
```
mcp__openmemory__search_memory(query="[topic]")
```

**Check existing Anki cards** to avoid duplicates:
```
mcp__anki__findNotes(query="deck:* [topic keywords]")
```

Note what's already covered so new cards add value.

### 3. Research the Topic

Use WebSearch to find authoritative sources:
- Official documentation
- Well-regarded tutorials
- Academic or professional references

Focus on:
- **Core concepts**: What must someone understand first?
- **Common patterns**: What do practitioners actually use?
- **Common mistakes**: What do beginners get wrong?
- **Mental models**: How should someone think about this?

### 4. Structure the Outline

Organize findings into a learning outline with these sections:

```markdown
## Learning Outline: [Topic]

### Prerequisites
- What should someone already know?

### Core Concepts (prioritized)
1. **[Concept]**: [One-sentence explanation]
   - Key fact 1
   - Key fact 2

2. **[Concept]**: [One-sentence explanation]
   - Key fact 1
   - Key fact 2

### Common Patterns
- [Pattern]: [When/why to use]

### Common Mistakes
- [Mistake]: [Why it's wrong, what to do instead]

### Existing Coverage
- [Note any existing Anki cards or OpenMemory entries found]

### Suggested Card Count
- Estimated [N] cards for core concepts
- Optional [M] cards for patterns/mistakes

### Sources
- [Links to authoritative sources used]
```

### 5. Return the Outline

Present the outline for user review. They will:
- Approve concepts for card creation
- Remove topics they already know
- Adjust scope or depth
- Then invoke `/anki-cards` with the approved content

## Output Format

Return ONLY the structured learning outline. Do not create cards directly.

The user will review and invoke `anki-cards` skill with approved content.

## Quality Criteria

- **Atomic concepts**: Each bullet should be one testable fact
- **Self-contained**: Explanations make sense without external context
- **Prioritized**: Most important concepts first
- **No duplicates**: Check existing cards before suggesting
- **Sourced**: Link to authoritative references

## Example Output

```markdown
## Learning Outline: Python Async Patterns

### Prerequisites
- Basic Python syntax
- Understanding of functions and return values
- Familiarity with I/O operations (file, network)

### Core Concepts (prioritized)

1. **Event Loop**: The central scheduler that runs async tasks
   - Single-threaded, cooperative multitasking
   - `asyncio.run()` creates and manages the loop
   - Only one task runs at a time; tasks yield at `await`

2. **Coroutines**: Functions defined with `async def`
   - Return coroutine objects, not results
   - Must be awaited or scheduled to execute
   - `await` pauses coroutine until result ready

3. **Tasks**: Wrapped coroutines scheduled for execution
   - Created with `asyncio.create_task()`
   - Run concurrently with other tasks
   - Can be cancelled, have timeouts

4. **await Keyword**: Pause point for async operations
   - Only valid inside `async def`
   - Yields control to event loop
   - Resumes when awaited operation completes

### Common Patterns
- **Gather**: Run multiple coroutines concurrently (`asyncio.gather()`)
- **Task groups**: Structured concurrency with `asyncio.TaskGroup` (3.11+)
- **Async context managers**: `async with` for resource cleanup
- **Async iterators**: `async for` for streaming data

### Common Mistakes
- **Blocking the loop**: Using `time.sleep()` instead of `asyncio.sleep()`
- **Forgetting await**: Coroutine never executes, just returns object
- **CPU-bound in async**: Async doesn't help computation, only I/O

### Existing Coverage
- No existing Anki cards found for "python async"
- OpenMemory: Found note on asyncio.gather usage

### Suggested Card Count
- 12 cards for core concepts
- 6 cards for patterns
- 3 cards for common mistakes

### Sources
- https://docs.python.org/3/library/asyncio.html
- https://realpython.com/async-io-python/
```

## Anti-Patterns

| Don't | Do Instead |
|-------|------------|
| Create cards directly | Return outline for user review |
| Skip duplicate check | Always check existing Anki cards |
| List every possible fact | Prioritize most important concepts |
| Use jargon without context | Explain terms in self-contained way |
| Return vague summaries | Provide atomic, testable facts |
