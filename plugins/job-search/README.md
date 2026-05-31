# Job Search Plugin

A comprehensive Claude Code plugin for managing your entire job search workflow — from tracking applications to optimizing resumes and preparing for interviews.

## What It Does

Job Search helps you through every stage of the job hunt:

- **Track applications** with structured Obsidian notes and Todoist tasks
- **Prepare for interviews** with gap analysis and STAR stories
- **Document achievements** from git commits, notes, and transcripts

## Components

| Type | Name | Trigger |
|------|------|---------|
| **Skill** | `job-opening` | `/job-opening <url>` or "create job opening from..." |
| **Skill** | `work-summary` | `/work-summary` or "summarize my work..." |
| **Agent** | `resume-reviewer` | "Review my resume" or "score my fit" |

## Features

### Job Opening Skill

`/job-opening <url>` - Create structured notes from a job posting URL

**What it does:**
1. Fetches and parses the job posting
2. Extracts company info, requirements, tech stack, and compensation
3. Creates or updates a Company note in `Personal/Career/Job Search/Companies/`
4. Creates a Job Opening note in `Personal/Career/Job Search/`
5. Links the notes bidirectionally
6. Offers to create a Todoist task for follow-up

**Example:**
```
/job-opening https://careers.stripe.com/job/123456
```

### Work Summary Skill

`/work-summary` - Gather work evidence and generate achievement documentation

**What it does:**
1. Asks for date range (30/90 days, 6 months, year, or custom)
2. Collects evidence from multiple sources:
   - Git/JJ commits from specified repositories
   - Obsidian meeting and project notes
   - Word transcripts (.docx files)
   - Slack exports (JSON format)
3. Analyzes and categorizes contributions
4. Integrates with Career Themes in your vault
5. Creates raw evidence note + formatted note with resume bullets

**Result:** Two notes in `Personal/Career/Achievements/`:
- Raw evidence note with all collected data
- Formatted note with resume bullets, LinkedIn summary, and STAR stories

### Resume Reviewer Agent

Autonomous agent that scores your resume fit against a job posting.

**Triggers:** "review my resume", "score my fit", "how does my resume match"

**Output:**
- Overall fit score (X/10)
- Skills match analysis (required + preferred)
- Experience alignment mapping
- Gap identification with mitigation suggestions
- Interview preparation tips

## Vault Structure

The plugin uses this Obsidian vault structure:

```
Personal/Career/
├── Job Search/
│   ├── 00 Dashboard.md
│   ├── Companies/           # Company research notes
│   └── [Job opening notes at root level]
├── Achievements/            # Work summary outputs
└── Themes/                  # Career themes for evidence
```

**Bases:**
- `Bases/Job Openings.base` — Pipeline view of all applications
- `Bases/Companies.base` — All tracked companies

## Prerequisites

1. **Obsidian** vault available at `~/Loose Ends/` (or wherever your vault lives)
2. **Claude Code** with MCP tools configured:
   - Obsidian MCP tools (`mcp__obsidian-mcp__*`) — the canonical marketplace Obsidian server
   - Todoist MCP tools (`mcp__claude_ai_Todoist__*`) — optional

## Installation

```bash
/plugin install job-search@cc-marketplace
```

## Workflow Example

Complete job application workflow:

```
1. Find job posting
2. /job-opening <url>                    # Create tracking notes
3. "Review my resume for this job"       # Get fit score
4. Apply and update status in note
```

## Troubleshooting

### WebFetch fails to parse job posting

Some job boards block automated requests:
1. Copy the job posting content manually
2. Paste it when prompted
3. The skill will extract details from pasted content

### Todoist project not found

Create a "Job Search" project in Todoist, or tasks will go to Inbox.

## Changelog

### v0.7.0
- Removed `resume-optimization` and `tailor-resume` skills (now maintained separately in resume project)

### v0.6.0
- Removed `cover-letter-writing` skill (now maintained separately in resume project)

### v0.5.0
- Enhanced `cover-letter-writing` skill (now removed in v0.6.0)

### v0.4.2
- Updated vault paths from `70 Career/` to `Personal/Career/`
- Job openings now created at root of Job Search folder (not in Openings subfolder)

### v0.4.1
- Enhanced resume skills (now removed in v0.7.0)

### v0.4.0
- Added `resume-reviewer` agent for fit scoring
- Updated keywords and description

### v0.3.x
- Initial release with `job-opening` and `work-summary` skills
- Career Themes integration

## License

MIT
