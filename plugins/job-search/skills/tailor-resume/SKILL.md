---
name: tailor-resume
description: >
  Use Skill(job-search:tailor-resume) when the user wants to tailor their resume
  for a specific job opening. Triggers: "tailor resume for", "customize resume",
  "adapt resume to", "match resume to job". Analyzes job posting requirements
  against current resume and suggests YAML modifications.
user-invokable: true
context: fork
allowed-tools:
  - Read
  - Glob
  - Grep
  - mcp__CodeMCP__Obsidian__obsidian_simple_search
  - mcp__CodeMCP__Obsidian__obsidian_get_file_contents
---

# Tailor Resume Skill

Analyze a job posting against the user's resume and generate specific YAML modifications to optimize fit.

## When to Use

- User wants to tailor resume for a specific job
- User provides a job opening note link or URL
- User asks to "customize resume for [company/role]"
- Before applying to a specific position

## Invocation

```
/tailor-resume [[Company - Position]]
```

Or: "Tailor my resume for the Lila Sciences role"

## Workflow

### Step 1: Gather Inputs

**1.1 Locate Job Opening Note**

If user provides Obsidian link (e.g., `[[Company - Position]]`):
```
obsidian_get_file_contents(filepath="Personal/Career/Job Search/[note-name].md")
```

If user provides company/role name, search:
```
obsidian_simple_search(query="[company] [role]", context_length=200)
```

Filter results to `Personal/Career/Job Search/` folder.

**1.2 Read Current Resume**

```
Read(file_path="~/Projects/typst-resume/jhoehler.yml")
```

### Step 2: Extract Requirements

From the job opening note, extract:

1. **Required skills** — From `skills_required` frontmatter field
2. **Preferred skills** — From `skills_preferred` frontmatter field
3. **Responsibilities** — From "Responsibilities" section in note
4. **Requirements text** — From "Requirements" section in note
5. **Keywords/themes** — From "Keywords/Themes" section

Create a requirements list:

```markdown
## Job Requirements Analysis

### Required Skills
- python
- fastapi
- aws
- kubernetes

### Preferred Skills
- ml-ops
- terraform

### Key Themes
- Scalability
- ML integration
- Cross-team collaboration
```

### Step 3: Gap Analysis

Compare job requirements against current resume:

**3.1 Skills Match**

| Required Skill | In Resume? | Evidence Location |
|---------------|------------|-------------------|
| python | ✅ Yes | skills.Languages, work highlights |
| fastapi | ✅ Yes | Waites highlights |
| kubernetes | ❌ No | Not mentioned |
| terraform | ✅ Yes | skills.Tools & Infrastructure |

**3.2 Experience Match**

For each key requirement, identify matching highlights:

| Requirement | Best Matching Highlight | Strength |
|-------------|------------------------|----------|
| "Design high-performance services" | "Architected FastAPI backend..." | Strong |
| "Collaborate with ML researchers" | "Built MLflow deployment..." | Moderate |
| "Manage complex backend challenges" | "Data migration strategy for 1.2M records" | Strong |

**3.3 Gaps Identified**

List skills/experience mentioned in posting but absent from resume:
- Kubernetes (mentioned in posting, not in skills)
- ML/LLM experience (preferred, limited evidence)

### Step 4: Generate Recommendations

Output specific YAML modifications organized by section:

#### 4.1 Skills Section Updates

```yaml
# Suggested additions to skills section
skills:
  - category: Languages
    skills:
      - Python  # Keep - required
      - TypeScript  # Add if posting mentions
      - SQL
      - PostgreSQL
      - Bash
      # Remove: LaTeX (not relevant to this role)

  - category: Tools & Infrastructure
    skills:
      - Git
      - GitHub Actions
      - Docker
      - Kubernetes  # ADD - mentioned in requirements
      - Terraform
      - AWS CDK
      # Consider adding: Helm, ArgoCD if you have experience
```

#### 4.2 Highlight Reordering

```yaml
# Suggested highlight order for Waites position
# Prioritize highlights matching job requirements

positions:
  - position: Senior Software Engineer
    highlights:
      # PRIORITY 1: Direct matches to requirements
      - Architected FastAPI backend consolidating legacy NodeJS services with distributed tracing  # Matches: high-performance services
      - Built production infrastructure for ML team's model management platform during company hackathon  # Matches: ML collaboration

      # PRIORITY 2: Strong secondary matches
      - Designed and tested data migration strategy for 1.2M IoT configuration records  # Matches: scalability
      - Built API comparison testing framework enabling automated parity validation  # Matches: quality/testing

      # PRIORITY 3: Good but less relevant
      - Diagnosed and fixed critical SQS batch processing bug causing 85% data loss  # Shows debugging skills

      # Consider removing for this application:
      # - Extended Terraform infrastructure... (less relevant unless DevOps focus)
```

#### 4.3 Summary Suggestion (if appropriate)

If the role is senior and a summary would help:

```yaml
summary: >
  Senior Software Engineer with [X] years building high-performance backend systems
  in Python and cloud infrastructure. Experience collaborating with ML teams,
  designing scalable APIs, and leading technical migrations. Passionate about
  [specific match to company mission].
```

### Step 5: Present Results

Output format:

```markdown
## Resume Tailoring: [Company] - [Position]

### Match Score: [X/10]

**Strong matches:**
- [List 2-3 strong alignments]

**Gaps to address:**
- [List any significant gaps]

---

### Recommended Changes

#### Skills Section

[YAML snippet with additions/removals]

#### Experience Highlights

**Waites - Senior Software Engineer**
[Reordered highlights with rationale]

**Synthetik - R&D Engineer**
[Any relevant reordering]

#### Summary (Optional)

[Suggested summary if appropriate]

---

### Application Notes

- **Keywords to emphasize**: [list]
- **Talking points for interview**: [2-3 bullets]
- **Potential concerns to address**: [if any gaps]

### Next Steps

1. [ ] Review and apply YAML changes
2. [ ] Rebuild resume: `typst compile template.typ resume.pdf`
3. [ ] Write cover letter using `/write-cover-letter`
4. [ ] Update job opening note status to "applying"
```

## Error Handling

| Error | Handling |
|-------|----------|
| Job note not found | Ask user to provide job posting URL or paste details |
| Resume file not found | Check path, ask user to confirm location |
| No skills_required in note | Extract from job posting summary section |
| Minimal overlap | Flag as potential stretch role, suggest which gaps are learnable |

## Remember

- Output YAML snippets ready to paste into jhoehler.yml
- Preserve existing YAML structure and formatting
- Never remove achievements entirely — suggest commenting out
- Prioritize required skills over preferred
- Suggest summary only for senior roles or when significant repositioning needed
- Connect each recommendation to specific job requirements
