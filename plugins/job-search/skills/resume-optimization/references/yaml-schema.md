# User Resume YAML Schema

The user's resume uses the imprecv Typst package with YAML data.

## File Locations

- **Template**: `~/Projects/typst-resume/template.typ`
- **Data**: `~/Projects/typst-resume/jhoehler.yml`
- **Output**: `~/Projects/typst-resume/resume.pdf`

## Schema Structure

```yaml
personal:
  name: string
  email: string
  phone: string
  url: string | null
  titles:
    - string  # Job titles (e.g., "Software Engineer")
  location:
    city: string
    region: string
    country: string
  profiles:
    - network: string  # "LinkedIn", "GitHub"
      username: string
      url: string

summary: string | null  # Optional professional summary

work:
  - organization: string
    url: string
    location: string
    positions:
      - position: string
        startDate: YYYY-MM-DD
        endDate: YYYY-MM-DD | "present"
        highlights:
          - string  # Achievement bullets

education:
  - institution: string
    url: string
    area: string  # Field of study
    studyType: string  # "Bachelor of Science", "Master of Science"
    startDate: YYYY-MM-DD
    endDate: YYYY-MM-DD
    location: string
    honors: string | null
    courses: [string] | null
    highlights: [string] | null

skills:
  - category: string  # "Languages", "Tools & Infrastructure"
    skills:
      - string  # Individual skills

# Optional sections (usually null)
affiliations: null
awards: null
certificates: null
publications: null
projects: null
languages: null
interests: null
references: null
```

## Current Resume Highlights

The user's current work experience includes:

### Waites (Senior Software Engineer, 2025-01 to 2026-01)
Key achievements:
- SQS batch processing bug fix (85% data loss prevention)
- MLflow deployment on ECS during hackathon
- Data migration strategy for 1.2M IoT records
- FastAPI backend consolidation with distributed tracing
- API backward compatibility for 2,000+ IoT gateways
- API comparison testing framework
- Multi-region Terraform infrastructure

### Synthetik Applied Technologies (R&D Engineer, 2022-01 to 2025-01)
Key achievements:
- Synthetic asset generation pipeline (Python/Blender)
- AWS Batch containerization
- 40% cloud cost reduction
- GitHub migration leadership
- Inventory tracking system (90% overhead reduction)

### UDRI (PNT Engineer + Grad Research, 2018-2022)
Key achievements:
- Sensor drivers development
- High-rate data processing (20k msg/min)
- REST API development (Express.js)
- Data automation (Python/MATLAB)

## Skills Categories

Current skills structure:
- **Languages**: Python, JavaScript, SQL, PostgreSQL, Bash, LaTeX
- **Tools & Infrastructure**: Git, GitHub Actions, Docker, Ansible, Terraform, Pulumi, AWS CDK

## Modification Guidelines

When suggesting YAML changes:

1. **Preserve structure**: Match existing indentation and field order
2. **Use correct types**: Arrays for highlights, strings for single values
3. **Date format**: ISO 8601 (YYYY-MM-DD)
4. **Null for unused**: Use `null` not empty strings for unused fields
5. **Comments**: Preserve existing `# todo:` comments
6. **Highlights format**: Start with action verb, include metrics

### Example: Adding a highlight

```yaml
# Before
highlights:
  - Existing achievement bullet

# After
highlights:
  - Existing achievement bullet
  - New achievement bullet with quantified impact
```

### Example: Reordering for relevance

```yaml
# Reorder highlights to prioritize relevant experience
highlights:
  - Most relevant achievement for target role
  - Second most relevant achievement
  - Third achievement
  # Less relevant items can be commented out:
  # - Less relevant achievement
```
