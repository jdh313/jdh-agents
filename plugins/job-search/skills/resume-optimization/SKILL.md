---
name: resume-optimization
description: >
  This skill should be used when the user asks "how can I improve my resume",
  "make my resume better", "resume tips", "resume advice", "what's wrong with my resume",
  "resume best practices", "ATS optimization", "resume formatting", "quantify achievements",
  "resume keywords", or needs general guidance on creating effective resumes.
  Provides knowledge about ATS systems, achievement quantification, and modern
  resume standards (2025-2026).
---

# Resume Optimization Skill

Provide guidance on creating effective, ATS-optimized resumes that pass automated screening and impress hiring managers.

## Core Principles

### ATS Optimization

Applicant Tracking Systems scan resumes before humans see them. Critical rules:

1. **Standard section headers**: Use "Experience", "Education", "Skills" — not creative alternatives
2. **No graphics/tables/columns**: ATS cannot parse complex layouts
3. **Simple formatting**: Standard fonts (Arial, Calibri, Times New Roman), 10-12pt
4. **Keywords from job posting**: Mirror exact phrases from requirements
5. **File format**: PDF or DOCX (check posting preference)
6. **No headers/footers**: ATS may skip content in these areas

### Achievement Quantification

Transform responsibilities into measurable accomplishments:

| Weak (Responsibility) | Strong (Achievement) |
|----------------------|---------------------|
| Responsible for API development | Built REST API serving 50k daily requests with 99.9% uptime |
| Managed team projects | Led 5-person team delivering 3 major features ahead of schedule |
| Improved system performance | Reduced query latency by 40% through index optimization |
| Worked on cloud infrastructure | Cut AWS costs by $15k/month via Spot Instance migration |

**Quantification formula**: Action verb + What + Measurable result

### Action Verbs by Category

| Category | Verbs |
|----------|-------|
| **Leadership** | Led, Directed, Managed, Coordinated, Supervised |
| **Technical** | Developed, Architected, Implemented, Engineered, Built |
| **Improvement** | Optimized, Streamlined, Enhanced, Reduced, Increased |
| **Analysis** | Analyzed, Evaluated, Diagnosed, Investigated, Assessed |
| **Communication** | Presented, Documented, Collaborated, Mentored, Trained |

## Resume Structure (2025-2026)

### Recommended Sections (in order)

1. **Contact Info**: Name, phone, email, LinkedIn, location (city/state only)
2. **Summary** (optional): 2-3 sentences for senior roles, skip for entry-level
3. **Experience**: Reverse chronological, 3-5 bullets per role
4. **Skills**: Technical skills matching job requirements
5. **Education**: Degrees, certifications (GPA only if 3.9+ or requested)

### Length Guidelines

| Experience Level | Length |
|-----------------|--------|
| Entry-level (0-3 years) | 1 page |
| Mid-level (4-10 years) | 1-2 pages |
| Senior (10+ years) | 2 pages max |

## Skills-First Hiring Trend

70% of recruiters prioritize skills over credentials. Lead with capabilities:

- **Required skills first**: Match exact keywords from job posting
- **Group logically**: Languages, Frameworks, Tools, Cloud, etc.
- **Be specific**: "PostgreSQL" not just "SQL", "FastAPI" not just "Python frameworks"
- **Show proficiency through achievements**: Don't just list — demonstrate usage

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Generic resume for all jobs | Tailor keywords and highlights per posting |
| Dense paragraphs | Use bullet points, 1-2 lines each |
| "Responsible for..." | Start with action verbs |
| No metrics | Add numbers: %, $, time saved, scale |
| Personal pronouns (I, me) | Remove — understood from context |
| Outdated skills | Remove irrelevant/obsolete technologies |
| References section | Remove — provide when asked |

## User's Resume Context

The user's resume is a Typst document with YAML data:

- **Template**: `~/Projects/typst-resume/template.typ` (imprecv package)
- **Data file**: `~/Projects/typst-resume/jhoehler.yml`
- **Schema**: imprecv CV schema (JSON schema validated)

When suggesting resume changes:
1. Output changes as YAML snippets matching the schema
2. Never modify the `.typ` template
3. Follow existing field structure (highlights arrays, skills arrays, etc.)
4. Use ISO 8601 dates (YYYY-MM-DD)

## Additional Resources

### Reference Files

For detailed guidance, consult:
- **`references/software-engineering.md`** — SWE-specific resume best practices, role-specific emphasis, seniority signals, common mistakes
- **`references/ats-keywords.md`** — Keyword optimization strategies
- **`references/yaml-schema.md`** — User's resume YAML structure

### Related Skills

- **`tailor-resume`** — Generate specific resume modifications for a job posting
- **`work-summary`** — Gather achievement evidence from work history
