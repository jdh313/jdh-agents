---
name: github-actions-expert
description: INVOKE for ANY GitHub Actions workflow task. Do NOT use generic task agents for CI/CD work. Triggers: "GitHub Actions", "CI/CD", "workflow", "GitHub automation", "matrix build", "Docker deployment", "action auth", "set up deployment", "troubleshoot workflow". Provides comprehensive patterns for workflow creation, authentication, debugging, performance optimization, and deployment strategies.
allowed-tools: Read, Grep, Glob, Write, Edit, WebSearch, WebFetch, mcp__CodeMCP__Context7__*, Bash(gh:*)
---

# GitHub Actions Expert

## Overview

Provide expert guidance on GitHub Actions workflows, including creation, optimization, debugging, and best practices. Leverage up-to-date documentation through Context7 and web search, combined with curated reference materials and reusable workflow snippets.

## When to Use This Skill

Trigger this skill when the user requests:

- **Creating workflows** - "Create a GitHub Actions workflow to test Python with pytest", "Set up CI/CD for Docker builds"
- **Improving workflows** - "Optimize this workflow for faster builds", "Add caching to reduce runtime"
- **Debugging workflows** - "Why is my workflow failing?", "Fix authentication errors in GitHub Actions"
- **Implementing patterns** - "Set up matrix builds", "Add semantic versioning", "Configure AWS OIDC authentication"
- **Automation tasks** - "Automate releases", "Deploy to AWS/Azure/GCP", "Run Terraform in CI"

## Core Capabilities

### 1. Research Live Documentation

Always fetch current GitHub Actions documentation when needed using Context7 or WebSearch:

**Context7 library ID:** `/websites/github_en_actions`

**Fetch GitHub Actions docs:**
```
Use Context7 to fetch documentation:
- Library ID: /websites/github_en_actions
- Topic: Specific feature needed (e.g., "matrix builds", "caching", "OIDC authentication")
```

**When to fetch:**
- User requests specific GitHub Actions features
- Syntax or API questions
- New features or recently updated functionality
- Marketplace action documentation

**Prefer live docs for:**
- Syntax references
- New/changed features
- Marketplace action details
- API changes

### 2. Workflow Creation & Improvement

Follow this systematic approach:

**Creating new workflows:**

1. **Understand requirements:**
   - What triggers the workflow? (push, PR, schedule, manual)
   - What environment/OS? (Ubuntu, Windows, macOS, containers)
   - What tools/languages? (Python, Node.js, Docker, Terraform)
   - What outputs? (artifacts, deployments, releases)

2. **Select appropriate patterns:**
   - Check `assets/snippets/` for relevant starting templates
   - Review `references/best-practices.md` for optimization patterns
   - Consult `references/common-actions.md` for marketplace actions

3. **Implement with best practices:**
   - Use caching for dependencies
   - Set appropriate timeouts
   - Add proper permissions (least privilege)
   - Include error handling
   - Use secrets securely

4. **Validate:**
   - Check YAML syntax
   - Verify permissions
   - Test conditional logic
   - Ensure proper authentication

**Improving existing workflows:**

1. **Analyze current workflow:**
   - Identify bottlenecks (slow steps, no caching)
   - Check security issues (hardcoded secrets, excessive permissions)
   - Find reliability problems (missing timeouts, no error handling)

2. **Apply optimizations:**
   - Add/improve caching (see `references/best-practices.md`)
   - Implement concurrency control
   - Optimize Docker builds (layer caching, BuildKit)
   - Use path filters to skip unnecessary runs

3. **Enhance reliability:**
   - Add timeout limits
   - Implement retry logic for flaky steps
   - Use matrix builds for comprehensive testing
   - Add proper status checks

### 3. Debugging Workflows

Follow the systematic debugging workflow from `references/debugging-guide.md`:

**Step 1: Syntax validation**
- YAML structure errors
- Missing colons, incorrect indentation
- Expression syntax issues

**Step 2: Authentication/secrets**
- GITHUB_TOKEN permissions insufficient
- Missing or incorrect secrets
- AWS/cloud authentication failures
- Docker registry access

**Step 3: Performance/timeouts**
- Job or step timeouts
- Resource constraints (disk, memory)
- Slow dependency installation or builds

**Step 4: Logic issues**
- Conditional expressions not evaluating correctly
- Wrong context used (`steps`, `needs`, `github`)
- Path filtering not working

**For each category, consult the detailed debugging guide:**
```
Read references/debugging-guide.md for:
- Common error patterns
- Solutions and workarounds
- Diagnostic techniques
```

### 4. Authentication Patterns

Consult `references/auth-patterns.md` for detailed patterns covering:

**GitHub authentication:**
- GITHUB_TOKEN (built-in, scoped)
- Personal Access Tokens (cross-repo, elevated)
- GitHub Apps (most secure for automation)

**Cloud providers:**
- **AWS**: OIDC (recommended), access keys (legacy)
- **Azure**: OIDC, service principals
- **GCP**: Workload Identity Federation, service account keys

**Docker registries:**
- Docker Hub
- GitHub Container Registry (GHCR)
- Amazon ECR
- Multi-registry authentication

**Always prefer:**
- OIDC over long-lived credentials
- Secrets over hardcoded values
- Least-privilege permissions
- Environment protection for production

### 5. WaitesWireless Custom Actions

> **Note:** This section is customized for WaitesWireless. Adapt repository references for your organization.

**Repository:** https://github.com/WaitesWireless/aws-github-actions

**Purpose:** Reusable workflows and actions for AWS deployments and common automation tasks

**When to use:**
```yaml
jobs:
  deploy:
    uses: WaitesWireless/aws-github-actions/.github/workflows/deploy.yml@main
    with:
      environment: production
    secrets: inherit
```

**When to suggest adding new actions to this repo:**

Create a reusable workflow/action in `WaitesWireless/aws-github-actions` when:
- Pattern is repeated across 3+ repositories
- AWS-specific deployment workflow
- Common IoT/gateway deployment task
- Shared validation or testing workflow

**Recommendation format:**
```
This pattern could be added to WaitesWireless/aws-github-actions as a reusable workflow:

Name: <descriptive-name>
Purpose: <what it does>
Inputs: <required/optional inputs>
Benefits: <why reusable>
```

### 6. Matrix Builds

Use matrix builds to test across multiple configurations:

**Common matrix patterns:**
```yaml
strategy:
  fail-fast: false
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']
    os: [ubuntu-latest, windows-latest, macos-latest]
```

**Advanced matrix with include/exclude:**
See `assets/snippets/matrix-python-testing.yml`

**When to use matrices:**
- Multi-version testing (Python 3.9-3.12, Node 16-20)
- Cross-platform testing (Linux, Windows, macOS)
- Parallel test execution
- Multiple deployment targets

### 7. Versioning and Releases

**Semantic versioning with conventional commits:**

Use `assets/snippets/semantic-release.yml` for automated versioning based on commit messages:
- `feat:` → minor version bump
- `fix:` → patch version bump
- `BREAKING CHANGE:` → major version bump

**Manual tagging and releases:**
```yaml
on:
  push:
    tags: ['v*']

- uses: softprops/action-gh-release@v1
  with:
    files: dist/*
    generate_release_notes: true
```

### 8. Performance Optimization

**Caching strategies:**
Consult `references/best-practices.md` for comprehensive caching patterns:
- Python dependencies (`~/.cache/pip`)
- Node.js dependencies (`~/.npm`)
- Docker layers (`type=gha`)
- Terraform plugins

**Concurrency control:**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Path filters:**
```yaml
on:
  push:
    paths:
      - 'src/**'
      - '.github/workflows/**'
```

## Resources

### references/

**best-practices.md** - Caching strategies, security hardening, performance optimization, reusable workflows, matrix build patterns

**debugging-guide.md** - Systematic debugging workflow covering syntax errors, authentication issues, timeouts, and conditional logic problems

**auth-patterns.md** - Authentication patterns for GitHub, AWS, Azure, GCP, Docker registries, and secrets management

**common-actions.md** - Frequently used marketplace actions with usage examples (checkout, setup-python, docker/build-push-action, etc.)

### assets/snippets/

Reusable YAML workflow snippets:

**matrix-python-testing.yml** - Python testing across versions and operating systems

**docker-build-push.yml** - Multi-platform Docker builds with caching and GHCR

**semantic-release.yml** - Automated versioning and releases using conventional commits

**terraform-deploy.yml** - Terraform validation, plan, and apply with PR comments

**python-lint-quality.yml** - Code quality checks with Ruff and type checking

**aws-oidc-deploy.yml** - AWS deployment using OIDC authentication (no long-lived credentials)

## Workflow Decision Tree

Use this decision tree to guide workflow creation:

**1. What's the trigger?**
- Code changes → `on: [push, pull_request]`
- Schedule → `on: schedule: cron`
- Manual → `on: workflow_dispatch`
- Release tags → `on: push: tags`

**2. What's being built/tested?**
- Python → Use `assets/snippets/matrix-python-testing.yml` or `python-lint-quality.yml`
- Docker → Use `assets/snippets/docker-build-push.yml`
- Infrastructure → Use `assets/snippets/terraform-deploy.yml`
- Multiple languages → Combine patterns

**3. Where's it deploying?**
- AWS → Use `assets/snippets/aws-oidc-deploy.yml`, consult `references/auth-patterns.md`
- Container registry → Use Docker snippets
- Not deploying → Focus on testing/validation

**4. What authentication is needed?**
- Cloud providers → Prefer OIDC patterns from `references/auth-patterns.md`
- Docker registries → See `references/common-actions.md` for login actions
- GitHub API → Use GITHUB_TOKEN or GitHub App

**5. Performance concerns?**
- Slow builds → Add caching from `references/best-practices.md`
- Long test runs → Use matrix builds to parallelize
- Large Docker images → Optimize with layer caching

## Best Practices Checklist

Before finalizing a workflow, verify:

- Uses appropriate caching (dependencies, build outputs)
- Has timeout limits (job and step level)
- Uses least-privilege permissions
- Stores secrets properly (no hardcoded values)
- Includes error handling where needed
- Uses concurrency control if applicable
- Has path filters to skip unnecessary runs
- Follows security best practices (OIDC, secret scanning)
- Includes appropriate status checks
- Is well-documented with comments

## Common Pitfalls to Avoid

1. **Missing permissions** - Always explicitly set `permissions:` for jobs using GITHUB_TOKEN
2. **Hardcoded secrets** - Use `${{ secrets.NAME }}`, never literal values
3. **No caching** - Results in slow, expensive workflows
4. **Mutable action versions** - Pin by SHA for security-critical workflows
5. **No timeouts** - Jobs can run indefinitely, wasting resources
6. **Wrong context** - Using `steps` context at job level, or `needs` in wrong scope
7. **Forgetting `persist-credentials: false`** - Can leak credentials in checkouts
8. **Not using `fail-fast: false`** - Matrix builds stop at first failure
9. **Overly broad triggers** - Workflows run on every file change
10. **Missing `if` conditions** - Deploy steps run on PRs

## Quick Start Examples

**"Create a Python testing workflow":**
1. Use `assets/snippets/matrix-python-testing.yml` as template
2. Adjust Python versions and OS matrix as needed
3. Add project-specific test commands

**"Set up Docker builds with GHCR":**
1. Use `assets/snippets/docker-build-push.yml`
2. Configure GITHUB_TOKEN permissions
3. Adjust platforms if needed

**"Debug authentication errors":**
1. Consult `references/debugging-guide.md` section 2
2. Check `references/auth-patterns.md` for proper configuration
3. Enable debug logging if needed

**"Optimize slow workflow":**
1. Review `references/best-practices.md` caching section
2. Add concurrency control
3. Implement path filters
4. Use matrix builds for parallelization
