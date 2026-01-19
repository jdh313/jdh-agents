---
name: cover-letter-writing
description: >
  Use Skill(job-search:cover-letter-writing) when user needs a cover letter written.
  Triggers: "write cover letter", "draft cover letter for [company]",
  "cover letter for [job posting]", "application letter".
user-invokable: true
context: fork
allowed-tools:
  - WebFetch
  - Read
  - Glob
  - Grep
  - AskUserQuestion
  - mcp__CodeMCP__Obsidian__obsidian_simple_search
  - mcp__CodeMCP__Obsidian__obsidian_get_file_contents
  - mcp__openmemory__search_memory
---

# Cover Letter Writing Skill

Generate tailored, evidence-backed cover letters that complement resumes and demonstrate genuine fit.

## Core Principles

- **Every claim must be verifiable** — sourced from resume or marked with `[PLACEHOLDER]`
- **Engineer-to-engineer tone** — professional but not corporate-speak
- **Show, don't tell** — metrics and specifics over buzzwords
- **250-400 words** — respect the reader's time

---

## Phase 1: Input Gathering

### Required Inputs

| Input | How to Obtain |
|-------|---------------|
| **Job posting** | URL (use WebFetch) or pasted content |
| **Resume** | Check `~/Projects/resume/jhoehler.yml` first, then ask |
| **Draft (optional)** | User-provided existing draft to refine |

### Locate Resume

Check these paths in order:

```
~/Projects/resume/jhoehler.yml
~/Projects/typst-resume/jhoehler.yml
~/Documents/Resume/resume.yml
```

If not found, use `AskUserQuestion` to request resume path or pasted content.

### Output Location

Cover letters are saved as YAML files for Typst compilation:
- **Output directory**: `~/Projects/resume/cover_letters/`
- **Template**: `~/Projects/resume/cover_letter_template.typ`

### Gathering Missing Inputs

Use `AskUserQuestion` when:
- **No job posting provided** — Ask for URL or pasted content
- **Resume not found** — Ask for file path or offer to accept pasted content
- **Ambiguous role** — Clarify which position if multiple mentioned

Example prompt for job posting:
```
"How would you like to provide the job posting?"
Options:
- "URL to job posting" (provide URL in follow-up)
- "Paste job description" (paste content in follow-up)
```

### Optional Context

Search for additional context:
- **Obsidian job note**: Search `Personal/Career/Job Search/` for company/role
- **OpenMemory**: Search for company name, role type, or similar applications

---

## Phase 2: Job Analysis

Extract structured information from the job posting.

### Success Signals (6-10 items)

Identify what defines success in this role. Look for:
- Key responsibilities and outcomes expected
- Problems they need solved
- Team dynamics and collaboration patterns
- Technical depth required
- Leadership or mentorship expectations

### ATS Keywords (8-15 items)

Extract exact phrases to mirror naturally:
- Technical skills and tools (specific versions/frameworks)
- Domain terminology
- Methodologies (Agile, TDD, etc.)
- Soft skills emphasized
- Company-specific terms

### Output Format

```markdown
## Job Analysis: [Company] - [Position]

### Success Signals
| # | Signal | Evidence Needed |
|---|--------|-----------------|
| 1 | Scale distributed systems to handle 10x traffic | Specific scaling achievements |
| 2 | Lead cross-functional projects | Team coordination examples |
| ... | ... | ... |

### ATS Keywords
`keyword1`, `keyword2`, `keyword3`, `keyword4`, `keyword5`, ...
```

---

## Phase 3: Evidence Mapping

Map resume content to job requirements.

### Evidence Sources

1. **Resume** — Primary source for all claims
2. **Obsidian job note** — Company research, "Why This Role" section
3. **OpenMemory** — Prior work context, achievements, patterns

### Evidence Map Table

For each success signal, find proof:

| Signal | Resume Proof | Metric/Scope | Tech Used |
|--------|-------------|--------------|-----------|
| Scale systems | Migrated monolith to microservices | 50k daily requests | FastAPI, Redis |
| Lead projects | Coordinated data migration | 3 teams, 1.2M records | PostgreSQL |
| ... | ... | ... | ... |

### Handle Gaps

If no direct proof exists:
- Note the gap explicitly
- Look for transferable evidence
- Mark as `[PLACEHOLDER - need: X]` if user must provide

---

## Phase 4: Draft Strategy

### Select Best Proof Points (2-3)

Choose achievements that:
1. **Directly map** to their top requirements
2. **Have metrics** or quantifiable scope
3. **Use their tech stack** or transferable skills

### Identify Company Hook

Research-backed connection to THIS company:
- Recent product launches or features
- Engineering blog posts
- Company mission/values
- Specific team or initiative mentioned
- Tech stack alignment

### Handle Unemployment (If Applicable)

If user is unemployed, use ONE neutral sentence maximum:
- "After my role at [Company] concluded..."
- "Since my last position ended..."
- "Following a company restructuring..."

Never apologize, over-explain, or draw attention to gaps.

---

## Phase 5: Generation

### Output Format: YAML

Cover letters are output as YAML files for the Typst template system.

**File naming**: `{company-slug}-{position-slug}.yml`
- Example: `stripe-senior-backend-engineer.yml`

### YAML Structure

```yaml
recipient:
  name: "Hiring Manager"      # Or specific name if known
  title: ""                   # Optional: "Engineering Manager"
  company: "Company Name"
  address: ""                 # Optional

position: "Position Title"

body:
  - |
    PARAGRAPH 1 — HOOK (3-4 sentences)
    State role applying for, why THIS company (specific, researched),
    and one proof-backed fit hook.

  - |
    PARAGRAPH 2 — PROOF (3-4 sentences)
    Two proof points with impact/scope. Prefer numbers over adjectives.
    Connect achievements directly to their stated needs.

  - |
    PARAGRAPH 3 — SENIOR SIGNAL
    In my first 30 days, I would focus on [learning/absorbing].
    By 60 days, I'd aim to [early contribution].
    Within 90 days, I expect to [meaningful impact].

  - |
    PARAGRAPH 4 — CLOSE (2-3 sentences)
    Confident call-to-action and thanks.
```

### Paragraph Guidelines

| Paragraph | Content | Length |
|-----------|---------|--------|
| 1 - Hook | Role + why this company + proof-backed fit | 3-4 sentences |
| 2 - Proof | 2 achievements with metrics, connected to needs | 3-4 sentences |
| 3 - Senior Signal | Micro 30/60/90 plan | 3-6 lines |
| 4 - Close | Call-to-action + thanks | 2-3 sentences |

**Optional 5th paragraph**: Problem hypothesis based ONLY on job page facts ("I noticed you're focusing on X, which often means Y challenge...")

### Tone Guidelines

| Do | Don't |
|----|-------|
| "I built systems handling 50k requests" | "I'm passionate about scalability" |
| "Led 3-team migration of 1.2M records" | "Experienced team player" |
| "Your work on [specific] aligns with..." | "I've always admired your company" |
| Direct, factual statements | Buzzwords without examples |

### Keyword Integration

Naturally incorporate 6-10 ATS keywords:
- Mirror their exact phrasing where possible
- Distribute throughout (not clustered)
- Never force awkward usage

### Length Target

**250-400 words** — no more than ¾ page

---

## Phase 6: Quality Gates

### Truth Check (Required)

Before finalizing, verify:

```markdown
## Truth Check

- [ ] **No placeholders remain** (or explicitly flagged)
- [ ] **Every claim sourced** from resume/verified context
- [ ] **No invented metrics, titles, employers, or tech**
```

### Quality Checklist

| Check | Status |
|-------|--------|
| Company name correct throughout | ☐ |
| Role title matches posting | ☐ |
| 250-400 words | ☐ |
| 6-10 ATS keywords included | ☐ |
| No buzzwords without examples | ☐ |
| Micro 30/60/90 included | ☐ |
| Maximum 2 links (prefer 1) | ☐ |
| No generic opening ("I am writing to apply...") | ☐ |

---

## Required Output

Every cover letter generation must include:

```markdown
## A. Job Success Signals (6-10 bullets)
[Table from Phase 2]

## B. ATS Keywords
[List from Phase 2]

## C. Evidence Map
[Table from Phase 3]

## D. Draft Critique (if draft provided)
[Max 8 bullets on existing draft]

## E. Cover Letter YAML

Save to: `~/Projects/resume/cover_letters/{company}-{position}.yml`
```

```yaml
recipient:
  name: "Hiring Manager"
  title: ""
  company: "Company Name"
  address: ""

position: "Position Title"

body:
  - |
    [Paragraph 1: Hook]

  - |
    [Paragraph 2: Proof with metrics]

  - |
    [Paragraph 3: 30/60/90 plan]

  - |
    [Paragraph 4: Close]
```

**Build command:**
```bash
typst compile cover_letter_template.typ cover_letter.pdf --input letter=cover_letters/{filename}.yml
```

```markdown
## F. Truth Check
- [Statement 1]
- [Statement 2]
- [Statement 3]
```

---

## Additional Resources

### Reference Templates

For structure examples by company type:
- **`references/templates.md`** — 5 templates (startup, enterprise, mission-driven, career transition, referral)

### Related Skills

- **`job-opening`** — Create job notes with company research
- **`tailor-resume`** — Ensure resume and cover letter align
- **`work-summary`** — Generate achievement documentation
