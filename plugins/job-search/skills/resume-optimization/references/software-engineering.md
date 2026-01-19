# Software Engineering Resume Best Practices

Guidance specific to software engineering roles — what to highlight, how to present technical work, and common mistakes.

## What Makes SWE Resumes Different

Software engineering resumes must demonstrate:
1. **Technical depth** — You can build complex systems
2. **Impact** — Your work moved business/product metrics
3. **Growth** — You've increased scope and responsibility
4. **Collaboration** — You work effectively with others

## Key Sections for SWE Resumes

### Technical Skills Section

**Structure by category:**
```yaml
skills:
  - category: Languages
    skills: [Python, TypeScript, Go, SQL]
  - category: Frameworks & Libraries
    skills: [FastAPI, React, Django, SQLAlchemy]
  - category: Infrastructure & Tools
    skills: [AWS, Kubernetes, Docker, Terraform]
  - category: Databases
    skills: [PostgreSQL, Redis, DynamoDB]
  - category: Practices
    skills: [CI/CD, TDD, Agile, Code Review]
```

**What to include:**
- Languages you're proficient in (not just "familiar with")
- Frameworks you've used in production
- Cloud platforms with specific services (AWS: EC2, Lambda, S3)
- Databases you've designed schemas for
- DevOps/Infrastructure tools

**What to exclude:**
- Basic tools everyone knows (Git, VS Code, Jira)
- Languages you haven't used in 2+ years
- Technologies you only used in tutorials
- Soft skills (save for highlights)

### Experience Highlights

**Strong SWE achievement formula:**
```
[Action verb] + [Technical what] + [Scale/complexity] + [Business impact]
```

**Examples by category:**

| Category | Weak | Strong |
|----------|------|--------|
| **Performance** | Improved database performance | Reduced API latency from 800ms to 120ms by implementing query optimization and Redis caching, improving user conversion by 15% |
| **Scale** | Built data pipeline | Architected event-driven pipeline processing 2M daily events with exactly-once delivery, enabling real-time analytics for 50k users |
| **Cost** | Reduced cloud costs | Cut AWS spend by $180k/year through Reserved Instance planning, Spot Fleet adoption, and right-sizing underutilized resources |
| **Reliability** | Improved system reliability | Designed circuit breaker pattern reducing cascading failures by 90%, achieving 99.95% uptime SLA |
| **Leadership** | Led team project | Led 4-engineer team delivering authentication rewrite in 8 weeks, reducing login failures by 60% |

### Projects Section (If Early Career)

Include if you have <3 years experience or significant side projects:

```yaml
projects:
  - name: Project Name
    url: https://github.com/...
    description: What it does
    highlights:
      - Technical achievement with metrics
      - Technologies used in meaningful context
```

**Good projects to include:**
- Open source contributions (especially to known projects)
- Side projects with real users
- Hackathon winners
- Technical blog with substantial content

**Skip:**
- Tutorial follow-alongs
- Incomplete projects
- School assignments (unless exceptional)

## Role-Specific Emphasis

### Backend Engineer

**Prioritize:**
- API design and scalability
- Database design and optimization
- Distributed systems experience
- Performance improvements with metrics
- Reliability/observability work

**Keywords:** REST, GraphQL, microservices, message queues, caching, database optimization, load balancing, rate limiting

### Full-Stack Engineer

**Prioritize:**
- End-to-end feature ownership
- Both frontend and backend achievements
- User-facing impact metrics
- Cross-functional collaboration

**Keywords:** React/Vue/Angular, Node/Python/Go, responsive design, API integration, full lifecycle development

### Platform/Infrastructure Engineer

**Prioritize:**
- Infrastructure as Code achievements
- Cost optimization with dollar amounts
- Deployment pipeline improvements
- Developer experience/productivity gains
- Incident response and reliability

**Keywords:** Terraform, Kubernetes, CI/CD, GitOps, observability, SRE, platform engineering, developer productivity

### Data Engineer

**Prioritize:**
- Pipeline scale (records/day, latency)
- Data quality improvements
- Cost optimization
- Enabling downstream teams

**Keywords:** ETL/ELT, data pipelines, Spark, Airflow, data modeling, data quality, real-time processing

## Common SWE Resume Mistakes

### Technical Mistakes

| Mistake | Fix |
|---------|-----|
| Listing every technology ever touched | Focus on production experience, 10-15 key skills |
| No metrics on technical work | Add scale, performance, cost, or time metrics |
| Generic descriptions ("worked on backend") | Specific achievements ("reduced latency 40%") |
| Only listing technologies, not impact | Show what you built AND why it mattered |
| Outdated skills prominently featured | Lead with current, relevant technologies |

### Framing Mistakes

| Mistake | Fix |
|---------|-----|
| Task-focused ("responsible for...") | Achievement-focused ("delivered...", "reduced...") |
| Solo contributor framing | Show collaboration and leadership even as IC |
| No business context | Connect technical work to user/business outcomes |
| Underselling scope | Quantify: team size, user count, data scale |
| Missing the "so what" | Every bullet should answer "why does this matter?" |

## Seniority Signals

### Junior (0-2 years)
- Learning velocity: "Ramped up on [tech] in X weeks to deliver..."
- Ownership of features: "Independently implemented..."
- Code quality: "Reduced bug rate by X% through..."
- Include relevant projects section

### Mid-Level (3-5 years)
- Technical leadership: "Led design of...", "Mentored..."
- Cross-team impact: "Collaborated with X team to..."
- System ownership: "Owned and maintained..."
- Scope expansion: Show increasing complexity

### Senior (6+ years)
- Architectural decisions: "Designed...", "Architected..."
- Org-wide impact: "Established standards for..."
- Multiplier effect: "Enabled X teams to...", "Reduced onboarding time..."
- Strategic thinking: Connect work to business strategy
- Consider adding brief summary section

### Staff+ (8+ years)
- Technical strategy: "Defined technical roadmap..."
- Cross-org influence: "Drove adoption of..."
- Industry impact: Open source, talks, publications
- Summary section recommended

## Metrics Cheat Sheet

When you don't have exact numbers, use reasonable estimates:

| Metric Type | How to Estimate |
|-------------|-----------------|
| **Users** | DAU, MAU, or total users affected |
| **Scale** | Requests/day, records processed, data volume |
| **Performance** | Before/after latency, throughput |
| **Cost** | Monthly/annual savings, % reduction |
| **Time** | Development time saved, deployment frequency |
| **Quality** | Bug reduction %, test coverage, uptime |
| **Team** | Team size led, engineers mentored |

**Estimation guidelines:**
- Round to clean numbers (50k not 47,382)
- Use ranges if uncertain ("50-100k users")
- Percentages work when absolutes aren't available
- "X% improvement" requires knowing the before state

## Technical Resume Red Flags (Avoid These)

1. **Buzzword stuffing** — Listing AI/ML/blockchain without substance
2. **No version control mention** — Implies you don't use it
3. **Only solo work** — Software is collaborative
4. **No production experience** — Only tutorials/courses
5. **Stale technology emphasis** — jQuery prominently featured in 2025
6. **Missing cloud experience** — Most roles require it now
7. **No testing mentioned** — Quality is expected
8. **Vague scale** — "Large-scale" without numbers

## Resume Review Checklist for SWE

Before submitting, verify:

**Content:**
- [ ] Every highlight has a metric or concrete outcome
- [ ] Technical skills match the job posting keywords
- [ ] Achievements show increasing scope over time
- [ ] Business impact is clear (not just technical tasks)
- [ ] Recent/relevant technologies are prominent

**Format:**
- [ ] Clean, ATS-friendly format (no tables/columns)
- [ ] 1-2 pages depending on experience
- [ ] Consistent date formatting
- [ ] No typos in technical terms (PostgreSQL not Postgres SQL)
- [ ] Links work (GitHub, LinkedIn, portfolio)

**Tailoring:**
- [ ] Skills section mirrors job posting requirements
- [ ] Most relevant highlights are first under each role
- [ ] Technologies mentioned in posting appear in resume
- [ ] Seniority signals match target role level
