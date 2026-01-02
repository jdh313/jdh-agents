---
name: meeting-followup
description: >
  INVOKE when working on a project to surface relevant unchecked action items
  from recent meeting notes. Searches meeting notes in 80 Waites/Meetings/ for
  open tasks related to the current work context. Presents contextually without
  interrupting flow.
allowed-tools:
  - mcp__CodeMCP__Obsidian__obsidian_simple_search
  - mcp__CodeMCP__Obsidian__obsidian_complex_search
  - mcp__CodeMCP__Obsidian__obsidian_get_file_contents
  - mcp__CodeMCP__Obsidian__obsidian_batch_get_file_contents
  - mcp__CodeMCP__Obsidian__obsidian_list_files_in_dir
---

# Meeting Follow-up

You help surface relevant action items from meeting notes when they're
contextually relevant to the current work.

## When to Activate

Search for meeting action items when:

1. **Starting work on a project** — Check for related tasks
2. **Discussing a topic covered in recent meetings** — Surface relevant notes
3. **User mentions a meeting or action item** — Find the source
4. **Working on Waites-related code** — Check for project-related tasks

## How to Search

### Find Meeting Notes with Open Action Items

```python
# Search for unchecked action items in meeting notes
obsidian_complex_search({
  "and": [
    {"glob": ["**/80 Waites/Meetings/**/*.md", {"var": "path"}]},
    {"regexp": ["- \\[ \\]", {"var": "content"}]}
  ]
})
```

### Filter by Project/Topic

```python
# Find action items related to specific project
obsidian_complex_search({
  "and": [
    {"glob": ["**/Meetings/**/*.md", {"var": "path"}]},
    {"regexp": ["- \\[ \\].*Gateway", {"var": "content"}]}
  ]
})
```

### Recent Meetings Only

```python
# Get recent meeting notes
obsidian_list_files_in_dir("80 Waites/Meetings")
# Then filter by date in filename (e.g., 2025-01-*)
```

## What to Surface

### Relevant Action Items

Surface action items that match:
- Current project being worked on
- Technology/service being discussed
- Person mentioned in conversation
- Recent meetings (last 2 weeks)

### How to Present

**Contextual insertion** (preferred):
```markdown
---
> 📋 **Related action item** from Meeting 2025-01-02:
> - [ ] Update Gateway API rate limiting documentation
>
> This seems relevant to what we're working on. Address now or skip?
---
```

**Batch summary** (at natural breakpoints):
```markdown
## Relevant Meeting Actions

Found 3 open items related to current work:

| Meeting | Action Item | Assigned |
|---------|-------------|----------|
| 2025-01-02 | Update rate limiting docs | You |
| 2024-12-28 | Review API error codes | You |
| 2024-12-20 | Add monitoring for timeouts | Team |

Address any of these? (1-3, all, or skip)
```

## Integration Points

### With Current Work Context

When Claude is working on code:
1. Identify the project/repo being modified
2. Search for related meeting notes
3. Check for unchecked action items
4. Present relevant ones contextually

### With Repo Notes

If working on a known repo (e.g., Gateway Config API):
```python
# Check the repo note for linked meetings
repo_note = obsidian_get_file_contents("80 Waites/Repos/Gateway Config API.md")
# Extract linked meetings from [[Meeting Links]]
# Check those meetings for open action items
```

## Presentation Style

### Non-Interrupting

- Don't stop the flow for minor items
- Add as a note at the end of a response
- Batch multiple items together

### Actionable

- Show the exact checkbox text
- Include meeting date for context
- Offer to mark as complete if done

### ADHD-Friendly

- One surfaced item at a time (inline)
- Batch at natural breakpoints
- Clear skip option
- No nagging for ignored items

## Example Scenarios

### Scenario 1: Working on Gateway API

```
User: "Let's work on the Gateway API rate limiting"

Claude: [Does the work...]

---
> 📋 Found a related action item from your 1-on-1 on 2025-01-02:
> - [ ] Update Gateway API rate limiting documentation
>
> Since we're touching this code, want to update the docs too?
```

### Scenario 2: Starting a Work Session

```
User: "What should I work on today?"

Claude: Let me check your recent meetings for open items...

## Open Action Items (from recent meetings)

| Priority | Item | From Meeting |
|----------|------|--------------|
| High | Deploy Gateway fix to staging | 2025-01-02 Standup |
| Medium | Review PR #123 | 2025-01-02 1-on-1 |
| Low | Update onboarding docs | 2024-12-28 Team sync |

Which would you like to tackle first?
```

### Scenario 3: Completing Related Work

```
User: "I just finished updating the rate limiting"

Claude: Great! I noticed you had an action item related to this:
- [ ] Update Gateway API rate limiting documentation

Since you just completed the code changes, should I:
1. Mark this action item as complete in the meeting note?
2. Help draft the documentation update?
3. Skip for now
```

## Marking Items Complete

When user completes an action item:

```python
# Update the meeting note
obsidian_patch_content(
  filepath="80 Waites/Meetings/2025-01-02 1-on-1.md",
  operation="replace",
  target_type="block",
  target="action-item-block-id",  # or use heading
  content="- [x] Update Gateway API rate limiting documentation"
)
```

## Remember

- **Be helpful, not annoying** — Only surface truly relevant items
- **Context matters** — Don't show action items unrelated to current work
- **Respect flow** — Batch at breakpoints, don't interrupt
- **Easy to dismiss** — "Skip" is always an option
- **Track completion** — Offer to mark items done when work is complete
