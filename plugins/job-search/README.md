# Job Search Plugin

A Claude Code plugin that streamlines job search workflows with Obsidian note creation and Todoist task tracking.

## What It Does

Job Search helps you track job applications efficiently by:
- **Creating structured notes** from job posting URLs
- **Extracting skills and requirements** for trend analysis
- **Linking company and role notes** for cross-referencing
- **Creating Todoist tasks** for application deadlines

## Features

### Job Opening Skill

`/job-opening <url>` - Create structured notes from a job posting URL

**What it does:**
1. Fetches and parses the job posting
2. Extracts company info, requirements, tech stack, and compensation
3. Creates or updates a Company note in `70 Career/Job Search/Companies/`
4. Creates a Job Opening note in `70 Career/Job Search/`
5. Links the notes bidirectionally
6. Offers to create a Todoist task for follow-up

**Example:**
```
/job-opening https://careers.stripe.com/job/123456
```

**Result:**
```markdown
## Created Job Opening Notes

**Company Note**: [[Stripe]] (new)
**Opening Note**: [[Stripe - Senior Backend Engineer]]

### Key Details
- **Position**: Senior Backend Engineer
- **Location**: San Francisco, CA
- **Remote**: Hybrid
- **Compensation**: $180k-$250k

### Skills Extracted
- **Required** (8): python, go, distributed-systems, postgresql...
- **Preferred** (4): kubernetes, aws, terraform...

---

**Would you like me to create a Todoist task to track this application?**
```

### Todoist Integration

After creating notes, the skill offers to create a Todoist task:

- **Default**: "Apply to {Company} - {Position}" due in 7 days
- **Custom due date**: Specify when prompted (e.g., "in 3 days", "next Monday")
- **Automatic linking**: Task description includes link to opening note
- **Project detection**: Automatically finds "Job Search" project in Todoist

## Prerequisites

1. **Obsidian** with Local REST API plugin running
2. **Claude Code** with MCP tools configured:
   - Obsidian MCP tools (`mcp__CodeMCP__Obsidian__*`)
   - Todoist MCP tools (`mcp__CodeMCP__Todosit__*`) - optional but recommended
3. **Vault structure**: Notes are created in `70 Career/Job Search/`

## Installation

```bash
/plugin install job-search@cc-marketplace
```

## Usage

### Basic Usage

Provide a job posting URL:
```
/job-opening https://boards.greenhouse.io/company/jobs/123456
```

### With Custom Todoist Due Date

When prompted for Todoist task:
```
Yes, due next Friday
```

Or:
```
Yes, in 3 days
```

### Skip Todoist Task

When prompted:
```
No thanks
```

## Note Structure

### Company Note

Created at: `70 Career/Job Search/Companies/{Company Name}.md`

```yaml
---
company_status: researching
industry: technology
headquarters: San Francisco, CA
---
```

Includes:
- Company overview and what they do
- Culture and reputation tracking
- Dataview query listing all openings at this company

### Job Opening Note

Created at: `70 Career/Job Search/{Company Name} - {Position}.md`

```yaml
---
company_note: "[[Company Name]]"
position: Senior Backend Engineer
status: researching
job_url: https://...
location: San Francisco, CA
remote: hybrid
compensation_range: $180k-$250k
skills_required: [python, go, distributed-systems]
skills_preferred: [kubernetes, aws]
---
```

Includes:
- Collapsible job posting summary
- Questions to ask in interviews
- Pros/cons table
- Compensation breakdown
- Post-mortem section (for after conclusion)

## Skill Extraction

Skills are extracted in kebab-case for consistency:

| Posting Text | Extracted As |
|--------------|--------------|
| "Python 3.10+" | `python` |
| "AWS (EC2, Lambda, S3)" | `aws` |
| "CI/CD pipelines" | `ci-cd` |
| "Machine Learning" | `machine-learning` |
| "Kubernetes/K8s" | `kubernetes` |

This enables tracking skill trends across applications using Obsidian Dataview.

## Workflow Integration

The plugin integrates with a typical job search workflow:

```
1. Find interesting job posting
2. /job-opening <url>
3. Review extracted details
4. Create Todoist task (optional)
5. Fill in "Why This Role" section
6. Research company (Glassdoor, LinkedIn)
7. Apply when ready
8. Update status in note frontmatter
```

## Troubleshooting

### WebFetch fails to parse job posting

Some job boards block automated requests. Solutions:
1. Copy the job posting content manually
2. Paste it when prompted by the skill
3. The skill will extract details from the pasted content

### Todoist project not found

If no "Job Search" project exists:
- The skill offers to create the task in Inbox
- Or create a "Job Search" project in Todoist first

### Notes created in wrong location

Verify your vault has this folder structure:
```
70 Career/
  Job Search/
    Companies/
```

Create these folders if missing.

## Roadmap

Future skills planned for this plugin:
- **Resume Tailor**: Generate tailored resume bullets from job requirements
- **Interview Prep**: Create prep notes with likely questions based on role
- **Application Tracker**: Dashboard view of all applications and statuses

## License

MIT
