# Job Search Plugin

A comprehensive Claude Code plugin for managing your entire job search workflow — from tracking applications to optimizing resumes and preparing for interviews.

## What It Does

Job Search helps you through every stage of the job hunt:

- **Track applications** with structured Obsidian notes and Todoist tasks
- **Optimize your resume** for ATS systems and specific job postings
- **Write tailored cover letters** that complement your resume
- **Prepare for interviews** with gap analysis and STAR stories
- **Document achievements** from git commits, notes, and transcripts

## Components

| Type | Name | Trigger |
|------|------|---------|
| **Skill** | `job-opening` | `/job-opening <url>` or "create job opening from..." |
| **Skill** | `work-summary` | `/work-summary` or "summarize my work..." |
| **Skill** | `tailor-resume` | `/tailor-resume [[Job Note]]` or "tailor resume for..." |
| **Skill** | `resume-optimization` | Auto-triggered for resume questions |
| **Skill** | `cover-letter-writing` | `/cover-letter` or "write cover letter for..." |
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

### Tailor Resume Skill

`/tailor-resume [[Company - Position]]` - Customize resume for a specific job

**What it does:**
1. Reads your job opening note from Obsidian
2. Reads your resume YAML (`~/Projects/typst-resume/jhoehler.yml`)
3. Analyzes skill matches and gaps
4. Generates specific YAML modifications:
   - Skills to add/remove
   - Highlight reordering for relevance
   - Optional summary suggestions
5. Outputs ready-to-paste YAML snippets

**Example:**
```
/tailor-resume [[Lila Sciences - Senior Full Stack Engineer]]
```

### Resume Optimization Skill

Auto-triggered when discussing resume best practices, ATS optimization, or achievement quantification.

**Provides guidance on:**
- ATS keyword optimization
- Achievement quantification (Action + What + Metrics)
- Skills-first hiring trends (2025-2026)
- Your specific Typst/YAML resume structure

### Cover Letter Writing Skill

`/cover-letter` - Generate a tailored cover letter for a job posting

**What it does:**
1. Gathers job posting (URL or pasted content) and resume
2. Analyzes success signals and extracts ATS keywords
3. Maps your resume evidence to job requirements
4. Generates cover letter with micro 30/60/90 plan
5. Verifies all claims against resume (Truth Check)

**Output includes:**
- Job success signals (6-10 items)
- ATS keywords to mirror (8-15 items)
- Evidence map (resume proof → job requirements)
- Final cover letter (250-400 words)
- Truth Check verification

### Resume Reviewer Agent

Autonomous agent that scores your resume fit against a job posting.

**Triggers:** "review my resume", "score my fit", "how does my resume match"

**Output:**
- Overall fit score (X/10)
- Skills match analysis (required + preferred)
- Experience alignment mapping
- Gap identification with mitigation suggestions
- Interview preparation tips

## Resume Setup

This plugin is configured for a Typst resume with YAML data:

| File | Purpose |
|------|---------|
| `~/Projects/typst-resume/template.typ` | Typst template (imprecv package) |
| `~/Projects/typst-resume/jhoehler.yml` | Resume data (YAML) |
| `~/Projects/typst-resume/resume.pdf` | Compiled output |

All resume suggestions are output as YAML snippets matching your schema.

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

1. **Obsidian** with Local REST API plugin running
2. **Claude Code** with MCP tools configured:
   - Obsidian MCP tools (`mcp__CodeMCP__Obsidian__*`)
   - Todoist MCP tools (`mcp__CodeMCP__Todosit__*`) - optional
3. **Typst resume** at `~/Projects/typst-resume/` (for resume features)

## Installation

```bash
/plugin install job-search@cc-marketplace
```

## Workflow Example

Complete job application workflow:

```
1. Find job posting
2. /job-opening <url>                    # Create tracking notes
3. /tailor-resume [[Company - Position]] # Get YAML changes
4. Edit jhoehler.yml with suggestions
5. typst compile template.typ resume.pdf # Rebuild resume
6. /cover-letter                         # Generate tailored cover letter
7. "Review my resume for this job"       # Get fit score
8. Apply and update status in note
```

## Troubleshooting

### WebFetch fails to parse job posting

Some job boards block automated requests:
1. Copy the job posting content manually
2. Paste it when prompted
3. The skill will extract details from pasted content

### Resume file not found

Ensure your resume is at `~/Projects/typst-resume/jhoehler.yml` or update the path in skill files.

### Todoist project not found

Create a "Job Search" project in Todoist, or tasks will go to Inbox.

### Job note not found for tailor-resume

Run `/job-opening <url>` first to create the job note, or search your vault for existing notes.

## Changelog

### v0.5.0
- Converted `cover-letter-writing` to user-invokable skill
- Added structured workflow: job analysis → evidence mapping → generation
- Includes ATS keyword extraction and 30/60/90 micro plan
- Added Truth Check verification for all claims

### v0.4.2
- Updated vault paths from `70 Career/` to `Personal/Career/`
- Job openings now created at root of Job Search folder (not in Openings subfolder)

### v0.4.1
- Added software engineering-specific resume guidance
- Improved skill triggers for general resume questions

### v0.4.0
- Added `tailor-resume` skill for YAML-based resume customization
- Added `resume-optimization` skill with ATS and best practices knowledge
- Added `cover-letter-writing` skill with templates
- Added `resume-reviewer` agent for fit scoring
- Updated keywords and description

### v0.3.x
- Initial release with `job-opening` and `work-summary` skills
- Career Themes integration

## License

MIT
