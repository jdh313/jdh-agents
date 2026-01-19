# GitHub Actions Expert

Expert guidance for GitHub Actions workflows, CI/CD, and deployment automation.

## What It Does

This plugin provides comprehensive support for:
- Creating and optimizing GitHub Actions workflows
- Setting up CI/CD pipelines for various languages and frameworks
- Debugging workflow failures and authentication issues
- Implementing deployment patterns (AWS, Azure, GCP, Docker)
- Matrix builds, caching strategies, and performance optimization
- Security best practices (OIDC, secrets management, permissions)

## When to Use

Invoke this skill when working on:
- GitHub Actions workflow creation or modification (`.github/workflows/`)
- CI/CD configuration and troubleshooting
- Workflow optimization and performance tuning
- Authentication and deployment setup
- Debugging workflow failures

## Key Triggers

The skill activates on phrases like:
- "GitHub Actions"
- "CI/CD"
- "workflow"
- "GitHub automation"
- "matrix build"
- "Docker deployment"
- "action auth"
- "set up deployment"
- "troubleshoot workflow"

## Contents

### Skill Documentation
- **skills/github-actions-expert.md** - Complete skill documentation with patterns, decision trees, and best practices

### Reference Materials

#### references/best-practices.md
Comprehensive guide covering:
- Caching strategies (pip, npm, Docker, Terraform)
- Security hardening and secret management
- Performance optimization techniques
- Reusable workflow patterns
- Matrix build optimization

#### references/debugging-guide.md
Systematic debugging workflows for:
- YAML syntax errors
- Authentication and permission issues
- Performance and timeout problems
- Conditional logic errors
- Common failure patterns and solutions

#### references/auth-patterns.md
Authentication patterns for:
- GitHub (GITHUB_TOKEN, PAT, GitHub Apps)
- Cloud providers (AWS OIDC, Azure, GCP)
- Docker registries (Docker Hub, GHCR, ECR)
- Secrets management best practices

#### references/common-actions.md
Marketplace actions reference with examples:
- Checkout, setup (Python, Node, Go, etc.)
- Docker builds and pushes
- Release and versioning
- Code quality and testing
- Deployment actions

## Common Use Cases

### Python Testing Across Versions
Use the matrix-python-testing snippet to test on Python 3.9-3.12 across Linux, Windows, and macOS.

### Docker Multi-Platform Builds
Use the docker-build-push snippet for efficient, cached builds with GHCR integration.

### AWS OIDC Deployment
Use the aws-oidc-deploy snippet for secure, temporary credential-based deployments.

### Terraform CI/CD
Use the terraform-deploy snippet for plan review and apply workflows.

### Semantic Versioning
Use the semantic-release snippet for automated version bumps based on conventional commits.

## Code Snippets

The plugin includes reusable YAML workflow snippets in `assets/snippets/`:
- `matrix-python-testing.yml` - Python testing across versions
- `docker-build-push.yml` - Docker builds with caching
- `semantic-release.yml` - Automated versioning
- `terraform-deploy.yml` - Infrastructure automation
- `python-lint-quality.yml` - Code quality checks
- `aws-oidc-deploy.yml` - AWS deployment

## Quick Start

1. **Create a workflow** - Select an appropriate snippet from assets/snippets/
2. **Consult reference materials** - Review relevant documentation for your use case
3. **Apply best practices** - Follow patterns from best-practices.md
4. **Debug issues** - Use debugging-guide.md for systematic problem-solving

## Example Workflow

```bash
# 1. Check the decision tree in the skill documentation
# 2. Select relevant snippet (e.g., matrix-python-testing.yml)
# 3. Customize for your project
# 4. Review best-practices.md for caching and security
# 5. Test the workflow
# 6. Use debugging-guide.md if issues arise
```

## Author

Jacob Hoehler
