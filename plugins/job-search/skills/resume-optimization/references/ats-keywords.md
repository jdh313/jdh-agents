# ATS Keyword Optimization

Strategies for optimizing resume keywords to pass Applicant Tracking Systems.

## How ATS Keyword Matching Works

1. **Exact match priority**: "Python" matches "Python", not "python programming"
2. **Phrase matching**: "machine learning" as a phrase vs separate words
3. **Synonym handling**: Varies by ATS — some recognize "ML" = "Machine Learning", many don't
4. **Density scoring**: More occurrences (natural, not stuffed) can improve ranking
5. **Section weighting**: Skills section often weighted higher than body text

## Keyword Extraction Process

When analyzing a job posting:

### Step 1: Identify Required Skills

Look for sections labeled:
- "Requirements"
- "Required qualifications"
- "Must have"
- "You have" / "You bring"

Extract exact phrases:
- Technology names: "Python 3.x", "PostgreSQL", "Kubernetes"
- Frameworks: "FastAPI", "React", "Django"
- Methodologies: "Agile", "CI/CD", "TDD"
- Soft skills: "cross-functional collaboration", "technical leadership"

### Step 2: Identify Preferred Skills

Look for sections labeled:
- "Nice to have"
- "Preferred qualifications"
- "Bonus points"
- "Ideally you have"

These are secondary keywords — include if you have them.

### Step 3: Extract Action Phrases

Note recurring themes in responsibilities:
- "Design and implement" → use in highlights
- "Collaborate with stakeholders" → mention cross-functional work
- "Optimize performance" → quantify performance improvements

## Keyword Placement Strategy

### Skills Section (Highest Weight)

Place exact keyword matches here:
```yaml
skills:
  - category: Languages
    skills:
      - Python  # Exact match to "Python" in posting
      - TypeScript  # Exact match
      - SQL
```

### Experience Highlights (Context + Keywords)

Embed keywords naturally in achievements:
```yaml
highlights:
  - Architected FastAPI backend with distributed tracing, consolidating 3 legacy services
  #          ^^^^^^^ keyword embedded naturally
```

### Summary Section (If Used)

Front-load with high-priority keywords:
```yaml
summary: >
  Senior Software Engineer with expertise in Python, cloud infrastructure (AWS),
  and distributed systems. Passionate about API design and developer productivity.
```

## Common Keyword Transformations

| Job Posting Says | Include Both Forms |
|-----------------|-------------------|
| CI/CD | CI/CD, continuous integration |
| ML / Machine Learning | ML, Machine Learning |
| K8s / Kubernetes | Kubernetes (spell out) |
| AWS | AWS, Amazon Web Services |
| JS / JavaScript | JavaScript, TypeScript |
| DBs / Databases | PostgreSQL, MySQL (be specific) |

## Keywords by Role Type

### Backend Engineer
- Python, Go, Java, Node.js
- REST API, GraphQL, gRPC
- PostgreSQL, Redis, MongoDB
- Docker, Kubernetes, AWS/GCP
- CI/CD, GitHub Actions, Jenkins
- Microservices, distributed systems

### DevOps / Platform Engineer
- Terraform, Pulumi, CloudFormation
- Kubernetes, Helm, ArgoCD
- AWS, GCP, Azure
- CI/CD, GitHub Actions, GitLab CI
- Monitoring: Datadog, Prometheus, Grafana
- IaC, GitOps, SRE

### Full-Stack Engineer
- React, Vue, Angular (frontend)
- Node.js, Python, Go (backend)
- TypeScript, JavaScript
- PostgreSQL, MongoDB
- Docker, Kubernetes
- REST API, GraphQL

### Data Engineer
- Python, SQL, Spark
- Airflow, Dagster, Prefect
- AWS (S3, Glue, Redshift), GCP (BigQuery)
- ETL, ELT, data pipelines
- dbt, pandas, numpy

## Avoiding Keyword Stuffing

ATS and humans both penalize obvious stuffing:

❌ **Bad (stuffed)**:
```
Python Python developer with Python experience in Python programming
```

✅ **Good (natural)**:
```
Developed Python microservices processing 50k requests/day with 99.9% uptime
```

**Rule**: Each keyword should appear 1-3 times max, always in meaningful context.

## Testing Keyword Coverage

Before submitting, verify:

1. [ ] All required skills from posting appear in Skills section
2. [ ] Technical keywords appear in at least one highlight
3. [ ] Action verbs match posting language ("design", "implement", "lead")
4. [ ] No keyword appears more than 3 times
5. [ ] Keywords read naturally, not forced
