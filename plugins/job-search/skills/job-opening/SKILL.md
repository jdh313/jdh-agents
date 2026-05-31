---
name: job-opening
description: Use Skill(job-search:job-opening) when the user provides a job posting URL and wants to create structured Obsidian notes for tracking the application. Triggers include "create job opening from", "add job posting", "track this application", or when user provides a URL to a job board. Creates both company and job opening notes with proper linking, skill extraction, and optional Todoist task creation.
context: fork
allowed-tools:
  - WebFetch
  - mcp__obsidian-mcp__search_notes
  - mcp__obsidian-mcp__read_note
  - mcp__obsidian-mcp__write_note
  - mcp__CodeMCP__Todosit__find-projects
  - mcp__CodeMCP__Todosit__add-tasks
  - Read
---

# Job Opening Skill

## Purpose

Streamline the process of creating structured job search notes in Obsidian from job posting URLs. Automatically extracts posting details, creates company and role notes with proper templates, links them together, and optionally creates a Todoist task for application tracking.

## When to Use

- User provides a job posting URL
- User asks to "track this job", "create job opening", "add this application"
- Starting to track a new job opportunity

## Invocation

The user will invoke this as:
```
/job-opening <url>
```

Or by saying: "Create job opening from [URL]"

## Workflow Instructions

You are a job search note creation specialist. Your mission is to take a job posting URL and create properly structured, linked Obsidian notes following the vault's conventions.

### Step 1: Fetch Job Posting

Use WebFetch to extract all relevant details from the URL:

```
WebFetch(url=<provided-url>, prompt="Extract all job posting details including: company name, job title, location, remote policy, responsibilities, requirements, nice-to-haves, tech stack mentioned, compensation if listed, and any other relevant details about the role and company.")
```

### Step 2: Extract Key Information

From the fetched content, identify:
- Company name
- Position title
- Location and remote policy
- Compensation range (if available)
- Required skills (for `skills_required` array)
- Preferred skills (for `skills_preferred` array)
- Responsibilities
- Requirements
- Nice-to-haves
- Tech stack

**Skill Naming Convention:**
- Use lowercase kebab-case
- Examples: `python`, `typescript`, `aws`, `kubernetes`, `ci-cd`, `ml-ops`
- Be specific but consistent

### Step 3: Check for Existing Company Note

Search for existing company note:

```
obsidian_simple_search(query="<company-name>", context_length=100)
```

Filter results to `Personal/Career/Job Search/Companies/` folder.

If company note exists:
- Use existing company note
- Note the file path for linking

If company note does NOT exist:
- Proceed to create new company note in Step 4

### Step 4: Create Company Note (if needed)

Create company note at:
```
Personal/Career/Job Search/Companies/<Company Name>.md
```

Use this template:

```markdown
---
date created: <current-datetime-YYYY-MM-DD HH:mm>
date_modified: <current-datetime-YYYY-MM-DD HH:mm>
company_status: researching
industry: <inferred-from-posting>
size:
stage:
headquarters: <from-posting>
website:
glassdoor_url:
linkedin_url:
---

%%CLAUDE WRITTEN START%%

# <Company Name>

## Overview
- **What they do:** <from-posting>
- **Founded:**
- **Funding/Stage:**

## Culture & Reputation
- **Glassdoor rating:**
- **Blind sentiment:**
- **Notable reviews:**

## Why Interesting
-

## Green Flags
-

## Red Flags
-

## News & Recent Events
-

## Contacts
-

## Openings at This Company

```dataview
TABLE position AS "Position", status AS "Status", applied_date AS "Applied"
FROM "Personal/Career/Job Search"
WHERE company_note = this.file.link
SORT applied_date DESC
```

## Notes

%%CLAUDE WRITTEN END%%
```

Fill in:
- Company name
- Industry (infer from posting)
- Headquarters (from posting)
- What they do (from posting)
- Any other details extracted

Leave blank fields for user to fill later (size, funding, glassdoor, etc.)

### Step 5: Create Job Opening Note

Create job opening note at:
```
Personal/Career/Job Search/<Company Name> - <Position>.md
```

Use this template:

```markdown
---
date created: <current-datetime-YYYY-MM-DD HH:mm>
date_modified: <current-datetime-YYYY-MM-DD HH:mm>
company_note: "[[<Company Name>]]"
position: <Position Title>
status: researching
source: <job-board-name>
applied_date:
job_url: <provided-url>
location: <location>
remote: <remote-policy>
compensation_range: <range-if-available>
skills_required: [<array-of-required-skills>]
skills_preferred: [<array-of-preferred-skills>]
recruiter:
hiring_manager:
next_action:
next_action_date:
---

%%CLAUDE WRITTEN START%%

# <Company Name> - <Position>

## Why This Role
-

## Role Details
- Team:
- Reports to:
- Level:

> [!note]- Job Posting Summary
> ### Responsibilities
> - <list-from-posting>
> ### Requirements
> - <list-from-posting>
> ### Nice-to-Haves
> - <list-from-posting>
> ### Tech Stack Mentioned
> - <list-from-posting>
> ### Keywords/Themes
> - <list-from-posting>

## Interview Notes

## Questions to Ask
- [ ] <suggested-questions-based-on-posting>

## Pros / Cons
| Pros | Cons |
|------|------|
| <from-posting> | |

## Compensation Details
- Base: <if-available>
- Equity:
- Benefits:
- PTO:

## Post-Mortem
<!-- Fill after conclusion -->
- Outcome:
- What went well:
- What to improve:

%%CLAUDE WRITTEN END%%
```

Fill in frontmatter:
- `company_note: "[[<Company Name>]]"`
- `position: <Position Title>`
- `status: researching`
- `job_url: <provided-url>`
- `location: <location>`
- `remote: <remote-policy>`
- `compensation_range: <range-if-available>`
- `skills_required: [<array-of-required-skills>]`
- `skills_preferred: [<array-of-preferred-skills>]`

Fill in body sections:
- **Job Posting Summary** (collapsible) - All extracted details
- **Role Details** - Level, team info
- **Questions to Ask** - Suggest relevant questions based on posting
- **Pros / Cons** - Start with basics from posting
- **Compensation Details** - Break down if provided

Leave sections for user:
- Why This Role
- Interview Notes
- Post-Mortem

### Step 6: Present Summary and Offer Todoist Task

After creating notes, present:

```markdown
## Created Job Opening Notes

**Company Note**: [[<Company Name>]] (new/existing)
**Opening Note**: [[<Company Name> - <Position>]]

### Key Details
- **Position**: <position>
- **Location**: <location>
- **Remote**: <remote-policy>
- **Compensation**: <range-or-not-listed>

### Skills Extracted
- **Required** (<count>): <first-5-skills>...
- **Preferred** (<count>): <first-5-skills>...

### Next Steps
1. Review and fill in "Why This Role"
2. Research company (Glassdoor, funding, etc.)
3. Update [[Skill Trends]] to see how this fits your focus areas

---

**Would you like me to create a Todoist task to track this application?**
- Default: "Apply to <Company> - <Position>" due in 7 days
- Or specify a custom due date (e.g., "in 3 days", "next Monday", "2025-01-20")
```

### Step 7: Create Todoist Task (if requested)

When the user confirms they want a Todoist task:

1. **Find the Job Search project:**
   ```
   find-projects(search="Job Search")
   ```

   - If found, use that project ID
   - If not found, inform user and offer to create task in Inbox

2. **Create the task:**
   ```
   add-tasks(tasks=[{
     "content": "Apply to <Company> - <Position>",
     "description": "Job opening note: [[<Company Name> - <Position>]]\n\nURL: <job-url>",
     "projectId": "<job-search-project-id-or-inbox>",
     "dueString": "<user-specified-or-in 7 days>",
     "priority": "p3"
   }])
   ```

3. **Confirm creation:**
   ```markdown
   **Todoist task created:**
   - **Task**: Apply to <Company> - <Position>
   - **Due**: <due-date>
   - **Project**: Job Search (or Inbox)
   ```

**Handling Todoist Errors:**
- If `find-projects` fails: Offer to create task in Inbox
- If `add-tasks` fails: Inform user with error, suggest manual task creation
- If no Todoist MCP tools available: Skip gracefully, note that Todoist integration is unavailable

## Error Handling

- **WebFetch fails**: Inform user, ask them to paste posting details manually
- **Company note exists but malformed**: Create opening note anyway, flag company note for review
- **Ambiguous company name**: Ask user for clarification before creating
- **No skills detected**: Leave arrays empty, suggest user fills them in
- **Todoist unavailable**: Complete without task, mention Todoist step was skipped

## Remember

- Always use kebab-case for skill names
- Link company and opening notes bidirectionally
- Extract as much as possible, but leave fields blank rather than guessing
- Present clear summary so user knows what was created
- Follow vault's existing template structure exactly
- Always offer Todoist integration after note creation
- Default to 7-day deadline unless user specifies otherwise
- **AI content markers:** New notes include `%%CLAUDE WRITTEN START%%` after frontmatter and `%%CLAUDE WRITTEN END%%` at the end (hidden in reading view, visible in edit mode)
