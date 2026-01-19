---
name: work-summary
description: >
  Use Skill(job-search:work-summary) when user needs to document work achievements for
  resume, LinkedIn, or interview preparation. Gathers evidence from git/jj commits,
  Obsidian notes, Word transcripts, and Slack exports. Triggers: "summarize my work",
  "document achievements", "update my resume", "prepare for interview".
user-invokable: true
context: fork
allowed-tools:
  - AskUserQuestion
  - Bash(git:*)
  - Bash(jj:*)
  - Bash(textutil:*)
  - Bash(find:*)
  - Read
  - Glob
  - Grep
  - mcp__CodeMCP__Obsidian__obsidian_simple_search
  - mcp__CodeMCP__Obsidian__obsidian_complex_search
  - mcp__CodeMCP__Obsidian__obsidian_get_file_contents
  - mcp__CodeMCP__Obsidian__obsidian_batch_get_file_contents
  - mcp__CodeMCP__Obsidian__obsidian_list_files_in_dir
  - mcp__CodeMCP__Obsidian__obsidian_put_content
  - mcp__CodeMCP__Obsidian__obsidian_patch_content
  - mcp__CodeMCP__Obsidian__obsidian_append_content
---

# Work Summary Skill

Gather evidence from multiple sources and generate formatted achievement documentation for resumes, LinkedIn, and interviews.

## When to Use

- User needs to document work achievements
- User is updating their resume or LinkedIn profile
- User is preparing for an interview
- User wants to summarize contributions over a time period

## Workflow

Execute these 5 phases in order:

### Phase 1: Configuration

Use AskUserQuestion to gather runtime parameters.

**Step 1.1: Date Range**

```
AskUserQuestion(
  question="What date range would you like to summarize?",
  options=["Last 30 days", "Last 90 days", "Last 6 months", "Last year", "Custom range"]
)
```

If "Custom range" selected:
```
AskUserQuestion(
  question="Enter start and end dates (YYYY-MM-DD to YYYY-MM-DD):"
)
```

**Step 1.2: Sources to Scan**

```
AskUserQuestion(
  question="Which sources should I scan for work evidence? (Select all that apply)",
  options=["Git/JJ repositories", "Obsidian notes", "Word transcripts (.docx)", "Slack exports (JSON)"]
)
```

**Step 1.3: Source Paths (asked conditionally based on Step 1.2)**

For Git/JJ repositories:
```
AskUserQuestion(
  question="Enter repository paths to scan (comma-separated, e.g., ~/Projects/api, ~/Projects/frontend):"
)
```

For Obsidian notes:
```
AskUserQuestion(
  question="Which Obsidian folders should I search? Default: 80 Waites/Meetings, 80 Waites/Projects",
  options=["Use defaults", "Custom folders"]
)
```

For Word transcripts:
```
AskUserQuestion(
  question="Enter path to Word transcripts folder (e.g., ~/Documents/Transcripts):"
)
```

For Slack exports:
```
AskUserQuestion(
  question="Enter path to Slack export folder:"
)
```

**Step 1.4: Context**

```
AskUserQuestion(
  question="What is your current role/title? (helps frame achievements)"
)
```

```
AskUserQuestion(
  question="Any specific projects or themes to highlight? (comma-separated, or 'none'):"
)
```

### Phase 2: Data Collection

Collect evidence from each selected source. Handle errors gracefully - if a source fails, log a warning and continue with others.

#### Git/JJ Repositories

For each repository path:

1. **Detect VCS type:**
   ```bash
   [[ -d "$REPO_PATH/.jj" ]] && echo "jj" || echo "git"
   ```

2. **Get commits in date range:**

   For git:
   ```bash
   git -C "$REPO_PATH" log --oneline --since="$START_DATE" --until="$END_DATE" --author="$(git config user.email)" --stat
   ```

   For jj:
   ```bash
   jj log -r "author(email:YOUR_EMAIL) & committer_date(after:\"$START_DATE\") & committer_date(before:\"$END_DATE\")" --no-pager -T 'description ++ "\n"'
   ```

3. **Categorize by type:** Parse commit subjects for feat/fix/refactor/docs/chore prefixes

**Error handling:**
- Invalid path: Log warning "Repository not found: $PATH", skip
- Not a git/jj repo: Log warning "Not a VCS repository: $PATH", skip
- No commits found: Log "No commits in date range for: $REPO_NAME"

#### Obsidian Notes

1. **Search for meeting notes:**
   ```
   obsidian_complex_search(query={
     "and": [
       {"glob": ["*.md", {"var": "path"}]},
       {"regexp": [".*80 Waites/Meetings.*", {"var": "path"}]}
     ]
   })
   ```

2. **Search for project notes:**
   ```
   obsidian_complex_search(query={
     "and": [
       {"glob": ["*.md", {"var": "path"}]},
       {"regexp": [".*80 Waites/Projects.*", {"var": "path"}]}
     ]
   })
   ```

3. **Filter by date range** using file creation/modification dates in frontmatter

4. **Batch read relevant notes** to extract key content

**Error handling:**
- Obsidian MCP unavailable: Log warning "Obsidian tools not available", skip
- No notes found: Log "No notes found in specified folders"

#### Word Transcripts

1. **Find .docx files:**
   ```bash
   find "$DOCX_PATH" -name "*.docx" -type f -newermt "$START_DATE" ! -newermt "$END_DATE"
   ```

2. **Convert to text (macOS native):**
   ```bash
   textutil -convert txt -stdout "$DOCX_FILE"
   ```

3. **Extract key excerpts** from the converted text

**Error handling:**
- Path not found: Log warning "Word folder not found: $PATH", skip
- textutil fails: Log warning "Could not convert: $FILE", skip file
- No .docx files: Log "No Word documents found in date range"

#### Slack Exports

1. **Locate user ID** from `users.json` in export folder

2. **Find JSON files in date range:**
   ```bash
   find "$SLACK_PATH" -name "*.json" -path "*/channels/*"
   ```

3. **Read and parse JSON**, filter messages by:
   - User ID match
   - Timestamp in date range

4. **Extract meaningful messages** (skip reactions, joins, etc.)

**Error handling:**
- Path not found: Log warning "Slack export folder not found: $PATH", skip
- Invalid JSON: Log warning "Could not parse: $FILE", skip file
- User not found: Log warning "Could not find user in users.json", skip

### Phase 3: Analysis

Process collected evidence to identify themes and achievements.

1. **Categorize commits:**
   - `feat:` - New features
   - `fix:` - Bug fixes
   - `refactor:` - Code improvements
   - `docs:` - Documentation
   - `chore:` - Maintenance
   - `test:` - Testing

2. **Group by project/theme:**
   - Use repository names as project identifiers
   - Cross-reference commits with meeting notes mentioning same project
   - Identify recurring themes across sources

3. **Extract quantifiable metrics:**
   - Number of commits per category
   - Files changed
   - Lines added/removed
   - Projects contributed to

4. **Cross-reference sources:**
   - Link commits to meeting notes discussing those changes
   - Connect Slack discussions to documented decisions
   - Map transcripts to project milestones

5. **Draft impact statements:**
   - For each significant contribution, draft an impact statement
   - Use format: Action verb + What + Quantifiable result

### Phase 3.5: Theme Integration

Integrate identified themes with Career Themes in Obsidian (`Personal/Career/Themes/`).

#### Step 3.5.1: Check existing themes

```
obsidian_list_files_in_dir(dirpath="Personal/Career/Themes")
```

Parse filenames to extract theme names:
- Strip `.md` extension
- Skip `00 Themes Dashboard.md` (folder note)
- Store as list of existing themes

#### Step 3.5.2: Match identified themes to existing notes

For each theme identified in Phase 3:

1. **Normalize theme name** for comparison:
   - Convert to title case
   - Replace special characters: `CI/CD` → `CI-CD`, `&` → `and`
   - Map common abbreviations: `IaC` → `Infrastructure as Code`

2. **Check for match** against existing theme notes (case-insensitive)

3. **Categorize** as `existing` (match found) or `new` (no match)

#### Step 3.5.3: Present theme summary to user

```
AskUserQuestion(
  question="I identified these themes from your work. Which should I update or create?",
  multiSelect=true,
  options=[
    "Update: [Theme Name] (exists)",
    "Update: [Theme Name] (exists)",
    "Create: [New Theme Name] (new)",
    "Skip all theme updates"
  ]
)
```

**Option formatting:**
- Existing themes: `Update: [Theme Name] (exists)`
- New themes: `Create: [Theme Name] (new)`
- Always include: `Skip all theme updates`

If user selects "Skip all theme updates", proceed directly to Phase 4.

#### Step 3.5.4: Update existing theme notes

For each selected existing theme:

1. **Check for duplicate** - Read the theme note and check if an H3 heading for this project already exists under `## Evidence`

2. **If duplicate exists**, skip with message: "Evidence for [Project] already exists in [Theme]"

3. **If no duplicate**, append new evidence section:

```
obsidian_patch_content(
  filepath="Personal/Career/Themes/[Theme Name].md",
  operation="append",
  target_type="heading",
  target="Evidence",
  content="""

### [Project Name] ([Date Range])
- [Brief evidence bullet 1]
- [Brief evidence bullet 2]
- [[YYYY-MM-DD Work Summary Raw|Full details]]
"""
)
```

**Evidence content guidelines:**
- 2-4 brief bullets summarizing key contributions
- Link to raw work summary for full details
- Keep bullets action-oriented

#### Step 3.5.5: Create new theme notes

For each selected new theme:

1. **Generate overview** based on evidence context and identified patterns

2. **Auto-suggest related themes** by analyzing:
   - Shared keywords/technologies with existing themes
   - Overlapping project references
   - Select 2-3 most relevant existing themes

3. **Create theme note:**

```
obsidian_put_content(
  filepath="Personal/Career/Themes/[Theme Name].md",
  content="""---
date created: YYYY-MM-DD HH:mm
date_modified: YYYY-MM-DD HH:mm
type: career-theme
status: active
---

%%CLAUDE WRITTEN START%%

# [Theme Name]

## Overview
[Generated overview based on evidence context - 2-3 sentences describing this competency area]

## Evidence

### [Project Name] ([Date Range])
- [Brief evidence bullet 1]
- [Brief evidence bullet 2]
- [[YYYY-MM-DD Work Summary Raw|Full details]]

## Impact Statements
- [Draft impact statement from Phase 3]

## Related
- [[Related Theme 1]]
- [[Related Theme 2]]

%%CLAUDE WRITTEN END%%
"""
)
```

#### Step 3.5.6: Track theme actions

Store a record of all theme actions for use in Phase 4 and 5:

| Theme | Status | Action |
|-------|--------|--------|
| [Theme Name] | Existing | Updated |
| [Theme Name] | New | Created |
| [Theme Name] | Existing | Skipped (duplicate) |
| [Theme Name] | Existing | Skipped (user choice) |

### Phase 4: Raw Output

Create raw evidence note in Obsidian.

**File path:** `Personal/Career/Achievements/YYYY-MM-DD Work Summary Raw.md`

**Template:**

```markdown
---
date created: YYYY-MM-DD HH:mm
type: work-summary-raw
date_range: START_DATE to END_DATE
sources: [list of sources used]
status: raw
---

%%CLAUDE WRITTEN START%%

# Work Summary Raw - DATE_RANGE

## Data Collection Summary

| Source | Items Found | Status |
|--------|-------------|--------|
| Git/JJ | X commits | Success/Partial/Skipped |
| Obsidian | X notes | Success/Partial/Skipped |
| Word | X transcripts | Success/Partial/Skipped |
| Slack | X messages | Success/Partial/Skipped |

## Git/JJ Commits

### Repository: repo-name

#### Features (feat)
- commit-hash: description (files changed)
- ...

#### Bug Fixes (fix)
- commit-hash: description
- ...

#### Refactoring (refactor)
- ...

#### Other
- ...

## Obsidian Notes

### Meeting Notes
- [[Meeting Note 1]] - Key points extracted
- ...

### Project Notes
- [[Project Note 1]] - Relevant excerpts
- ...

## Word Transcripts

### transcript-name.docx
> Key excerpt 1...

> Key excerpt 2...

## Slack Messages

### #channel-name
- [timestamp] Message content
- ...

## Identified Themes

### Theme 1: [Name]
**Evidence:**
- Commit: ...
- Meeting: ...
- Transcript: ...

**Draft Impact:** [Initial impact statement]

### Theme 2: [Name]
...

## Metrics Summary

| Metric | Count |
|--------|-------|
| Total commits | X |
| Features added | X |
| Bugs fixed | X |
| Projects touched | X |
| Meeting notes referenced | X |

## Themes Referenced

Career themes updated or created from this work summary.

| Theme | Status | Action |
|-------|--------|--------|
| [[CI-CD Pipeline Automation]] | Existing | Updated |
| [[New Theme Name]] | New | Created |
| [[Skipped Theme]] | Existing | Skipped |

%%CLAUDE WRITTEN END%%
```

Use `obsidian_put_content` to create the note.

### Phase 5: Formatted Output

Create formatted achievement note in Obsidian.

**File path:** `Personal/Career/Achievements/YYYY-MM-DD Work Summary.md`

**Template:**

```markdown
---
date created: YYYY-MM-DD HH:mm
type: work-summary
raw_note: "[[YYYY-MM-DD Work Summary Raw]]"
role: USER_ROLE
date_range: START_DATE to END_DATE
status: formatted
---

%%CLAUDE WRITTEN START%%

# Work Summary - DATE_RANGE

> Raw evidence: [[YYYY-MM-DD Work Summary Raw]]

## Resume Bullets

Use these achievement statements on your resume. Each follows the format: Action Verb + What + Impact/Result.

### Project/Theme 1
- **Bullet:** Developed [specific feature] using [technologies], resulting in [quantifiable impact]
- **Evidence:** [Link to raw note section]

### Project/Theme 2
- **Bullet:** Led [initiative] that improved [metric] by [percentage/amount]
- **Evidence:** [Link to raw note section]

### Project/Theme 3
- ...

## LinkedIn Summary

Use this narrative summary for LinkedIn posts or profile updates.

---

Over the past [time period], I [high-level summary of contributions].

Key highlights include:
- [Achievement 1 with context]
- [Achievement 2 with context]
- [Achievement 3 with context]

Technologies and skills applied: [comma-separated list]

#hashtag1 #hashtag2 #hashtag3

---

## STAR Stories

Use these structured stories for behavioral interview questions.

### Story 1: [Title]

**Situation:** [Context and background]

**Task:** [What needed to be accomplished]

**Action:** [Specific steps you took]

**Result:** [Quantifiable outcome]

**Best for questions about:** [List relevant interview question types]

### Story 2: [Title]
...

## Quick Stats

| Metric | Value |
|--------|-------|
| Time Period | DATE_RANGE |
| Commits | X |
| Features Shipped | X |
| Bugs Fixed | X |
| Projects | X |

## Theme Contributions

This summary contributed evidence to these career themes:

- [[CI-CD Pipeline Automation]] — Updated with [project] evidence
- [[New Theme Name]] — Created new theme

See [[Personal/Career/Themes/00 Themes Dashboard|Themes Dashboard]] for all themes.

## Next Steps

- [ ] Review and refine resume bullets
- [ ] Select 2-3 STAR stories for upcoming interviews
- [ ] Update LinkedIn profile/post
- [ ] Add additional context to evidence notes

%%CLAUDE WRITTEN END%%
```

Use `obsidian_put_content` to create the note.

## Completion Summary

After creating both notes, present:

```markdown
## Work Summary Complete

**Date Range:** START_DATE to END_DATE
**Role:** USER_ROLE

### Created Notes
- **Raw Evidence:** [[YYYY-MM-DD Work Summary Raw]]
- **Formatted Summary:** [[YYYY-MM-DD Work Summary]]

### Sources Processed
| Source | Status | Items |
|--------|--------|-------|
| Git/JJ | ... | ... |
| Obsidian | ... | ... |
| Word | ... | ... |
| Slack | ... | ... |

### Key Achievements Identified
1. [Top achievement 1]
2. [Top achievement 2]
3. [Top achievement 3]

### Theme Updates
| Theme | Action |
|-------|--------|
| CI-CD Pipeline Automation | Updated |
| New Theme Name | Created |
| Skipped Theme | Skipped |

### Next Steps
1. Review raw evidence for additional context
2. Refine resume bullets in formatted note
3. Practice STAR stories for interviews
4. Review theme notes for accuracy
```

## Error Handling Summary

| Error | Handling |
|-------|----------|
| Source path not found | Log warning, skip source, continue |
| No data in date range | Log info, continue with other sources |
| MCP tool unavailable | Log warning, skip dependent source |
| File parse failure | Log warning for specific file, continue |
| All sources fail | Report error, suggest manual data entry |
| Obsidian folder missing | Create folder before writing |
| Theme folder missing | Create `Personal/Career/Themes/` before operations |
| Theme patch target not found | Log warning, skip theme update |
| Duplicate project evidence | Skip with message, don't duplicate |

## Remember

- Always use AskUserQuestion for runtime configuration
- Skip unavailable sources gracefully with warnings
- Create both raw and formatted notes
- Link formatted note back to raw evidence
- Use kebab-case for any extracted skills
- Present clear completion summary
- Handle all error cases without crashing
- **AI content markers:** New notes include `%%CLAUDE WRITTEN START%%` after frontmatter and `%%CLAUDE WRITTEN END%%` at the end (hidden in reading view, visible in edit mode)
- **Theme integration:** Always run Phase 3.5 after analysis to integrate with Career Themes
- **Theme name normalization:** Use filesystem-safe names (`CI-CD` not `CI/CD`, `and` not `&`)
- **Duplicate prevention:** Check for existing project H3 under Evidence before appending
- **Related themes:** Auto-suggest 2-3 related themes for new theme notes based on keyword overlap
