---
name: contextual-search
description: >
  INVOKE automatically during: (1) topic exploration - search for existing notes
  on the topic, (2) debugging/stuck - search for similar past problems or solutions,
  (3) decision points - search for prior art, past decisions, or related context.
  Weave findings into responses naturally without asking permission to search.
allowed-tools:
  - mcp__CodeMCP__Obsidian__obsidian_simple_search
  - mcp__CodeMCP__Obsidian__obsidian_complex_search
  - mcp__CodeMCP__Obsidian__obsidian_get_file_contents
  - mcp__CodeMCP__Obsidian__obsidian_batch_get_file_contents
  - mcp__CodeMCP__Obsidian__obsidian_get_recent_periodic_notes
---

# Contextual Search

You automatically search the user's Obsidian vault when context is relevant.

**IMPORTANT:** Do NOT ask permission to search — reads are automatic. Just search and weave findings into your response naturally.

## When to Search

### 1. Topic Exploration
User is researching or exploring a topic.

**Triggers:**
- "How does X work?"
- "What's the best way to..."
- "I'm looking into..."
- "Tell me about..."

**Action:** Search for existing notes on the topic

**Example:**
```
User: "How does Python's attrs library work?"
You: [Automatically search vault for "attrs" or "Python attrs"]
Response: "Based on your notes in '50 Developer Notes/Python attrs Library.md',
you've documented that attrs simplifies class creation by..."
```

### 2. Stuck/Debugging
User is blocked on a problem.

**Triggers:**
- "This isn't working"
- "I'm getting an error"
- "Why is this failing?"
- "How do I fix..."

**Action:** Search for similar problems, debugging approaches, past incidents

**Example:**
```
User: "Lambda is timing out on cold starts"
You: [Search for "Lambda" and "cold start" or "timeout"]
Response: "Your notes from the SQS incident (AWS SQS Lambda Data Loss Incident
Post-Mortem.md) mention cold start mitigation using provisioned concurrency..."
```

### 3. Decision Points
User needs to make a choice or design decision.

**Triggers:**
- "Should we use X or Y?"
- "What's the best approach?"
- "How did we handle this before?"
- "What do you think about..."

**Action:** Search for prior decisions, ADRs, related context

**Example:**
```
User: "Should we use FastAPI or Django for this API?"
You: [Search for "FastAPI", "Django", "ADR", or "API decision"]
Response: "Looking at your ADRs in '80 Waites/ADRs/', you chose FastAPI for the
Gateway Config API because of automatic OpenAPI generation and async support..."
```

## Search Strategy

### Step 1: Identify Keywords
Extract key terms from the user's question or context.

**Examples:**
- "Lambda cold start" → search for "Lambda cold start"
- "How do I set up Git hooks?" → search for "Git hooks" or "hooks setup"
- "Gateway API authentication" → search for "Gateway" and "authentication"

### Step 2: Start Broad
Use `obsidian_simple_search` for initial keyword search:

```
obsidian_simple_search(
  query="keyword or phrase",
  context_length=200
)
```

Returns matching notes with surrounding context.

### Step 3: Narrow if Needed
If too many results or need specific scope, use `obsidian_complex_search` with JsonLogic:

**Search specific folder:**
```json
{
  "and": [
    {"glob": ["**/80 Waites/**/*.md", {"var": "path"}]},
    {"regexp": ["keyword", {"var": "content"}]}
  ]
}
```

**Search by tag:**
```json
{
  "and": [
    {"regexp": ["#topic/dev/patterns", {"var": "content"}]},
    {"regexp": ["keyword", {"var": "content"}]}
  ]
}
```

**Search recent daily notes:**
```
obsidian_get_recent_periodic_notes(
  period="daily",
  limit=7,
  include_content=True
)
```

### Step 4: Read Relevant Hits
If search finds promising notes, read them to get full context:

```
obsidian_get_file_contents(
  filepath="path/to/relevant/note.md"
)
```

Or batch read multiple:
```
obsidian_batch_get_file_contents(
  filepaths=["note1.md", "note2.md", "note3.md"]
)
```

### Step 5: Weave Into Response
Reference findings naturally in your response:

**Good:**
- "Based on your notes about..."
- "According to your Gateway Config API repo note..."
- "Your ADR from October mentions..."
- "In your debugging notes for the Lambda timeout issue..."

**Avoid:**
- "I found these notes: [list]" (too mechanical)
- "Search results: ..." (too explicit)
- Asking permission to search (just do it)

## Search Patterns by Topic Area

### Work-Related (Waites, Gateway, Projects)
```json
{
  "glob": ["**/80 Waites/**/*.md", {"var": "path"}]
}
```

### Technical Patterns/Reference
```json
{
  "glob": ["**/50 Developer Notes/**/*.md", {"var": "path"}]
}
```

### Recent Activity (Last Week)
```
obsidian_get_recent_periodic_notes(period="daily", limit=7, include_content=True)
```

### Meeting Notes with Action Items
```json
{
  "and": [
    {"glob": ["**/Meetings/**/*.md", {"var": "path"}]},
    {"regexp": ["- \\[ \\]", {"var": "content"}]}
  ]
}
```

### Specific Technology/Tool
```json
{
  "and": [
    {"glob": ["**/*.md", {"var": "path"}]},
    {"regexp": ["Lambda|FastAPI|Docker", {"var": "content"}]}
  ]
}
```

## What to Do With Results

### Relevant Hit Found
- Quote or summarize the relevant part
- Link to the note using `path:line` format when specific
- Incorporate the knowledge into your response
- If appropriate, suggest updating the note with new findings

**Example:**
```
"Your note on Python attrs (50 Developer Notes/Python attrs Library.md:42-56)
covers the @define decorator. You might want to add this new frozen=True pattern
we just discovered."
```

### No Hits
- Proceed without mentioning the search
- Don't say "I didn't find anything" unless it's relevant
- Offer to help create a note if the topic seems worth documenting

### Partial Match
- Use what's relevant
- Note if the existing note could be expanded
- Suggest capture if this is new knowledge worth adding

**Example:**
```
"Your Gateway API note mentions rate limiting but doesn't cover the 429 retry
behavior we just discovered. Want to add this?"
```

## Common Scenarios

### Scenario: User Debugging
```
User: "Why is my Lambda function failing?"
Actions:
1. Search for "Lambda" + "error" or "failure"
2. Check recent daily notes for Lambda work
3. Look for repo notes if specific to a known project
4. Reference any debugging patterns found
```

### Scenario: Architecture Decision
```
User: "Should we add caching to the API?"
Actions:
1. Search for "caching" or "cache"
2. Search ADRs in 80 Waites/ADRs/
3. Search for similar API patterns in developer notes
4. Reference past decisions and rationale
```

### Scenario: Learning New Concept
```
User: "I'm learning about asyncio in Python"
Actions:
1. Search for "asyncio" or "async Python"
2. Check if there are existing notes
3. If found, reference them to build on existing knowledge
4. If not found, offer to create a note after the discussion
```

## Remember

- **Search is automatic** — No permission needed for reads
- **Be natural** — Weave findings into responses, don't just list them
- **Search early** — Better to search and find nothing than miss relevant notes
- **Read full context** — Don't rely on search snippets; read the full note if promising
- **Suggest updates** — If you find notes that could be enhanced with new info, mention it
