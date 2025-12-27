# GitHub Actions Debugging Guide

## Systematic Debugging Workflow

When a workflow fails, follow this systematic approach:

1. **Syntax Check** - Validate YAML structure
2. **Authentication** - Verify credentials and permissions
3. **Performance/Timeouts** - Check resource limits and execution time
4. **Logic** - Debug conditional expressions and variable interpolation

## 1. Syntax Errors

### Common YAML Syntax Issues

**Indentation errors:**
```yaml
# ❌ BAD - incorrect indentation
jobs:
  build:
  runs-on: ubuntu-latest
    steps:
  - run: echo "hello"

# ✅ GOOD
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "hello"
```

**Missing colons:**
```yaml
# ❌ BAD
steps
  - name: Build

# ✅ GOOD
steps:
  - name: Build
```

**Incorrect string quoting:**
```yaml
# ❌ BAD - unquoted special characters
- run: echo ${{ secrets.TOKEN }}

# ✅ GOOD
- run: echo "${{ secrets.TOKEN }}"
```

**Multi-line syntax:**
```yaml
# Literal block (preserves newlines)
- run: |
    echo "Line 1"
    echo "Line 2"

# Folded block (converts newlines to spaces)
- run: >
    This is a very long command
    that spans multiple lines

# Quoted multi-line
- run: "echo 'hello'\necho 'world'"
```

### Validation Tools

**Local YAML validation:**
```bash
# Using actionlint
brew install actionlint
actionlint .github/workflows/*.yml

# Using yamllint
pip install yamllint
yamllint .github/workflows/
```

**GitHub CLI validation:**
```bash
gh workflow view <workflow-name>
```

**Online validator:**
Use https://rhysd.github.io/actionlint/ for quick validation

### Common Expression Syntax Errors

**Context property access:**
```yaml
# ❌ BAD - missing quotes
if: github.event_name == push

# ✅ GOOD
if: github.event_name == 'push'
```

**Function calls:**
```yaml
# ❌ BAD
if: contains(github.event.head_commit.message 'skip ci')

# ✅ GOOD
if: contains(github.event.head_commit.message, 'skip ci')
```

## 2. Authentication & Secrets Issues

### GITHUB_TOKEN Permissions

**Insufficient permissions error:**
```
Error: Resource not accessible by integration
```

**Solution - Grant explicit permissions:**
```yaml
permissions:
  contents: write
  pull-requests: write
  issues: write
  packages: write
```

**Check required permissions:**
- `contents: write` - Push commits, create releases
- `pull-requests: write` - Comment on PRs, merge
- `issues: write` - Create/update issues
- `packages: write` - Publish packages
- `id-token: write` - OIDC authentication

### Secrets Not Available

**Common causes:**
1. Secret not set in repository/organization settings
2. Secret name mismatch (case-sensitive)
3. Secrets not passed to reusable workflows
4. Secrets not available in forked PRs (security restriction)

**Debug missing secrets:**
```yaml
- name: Check if secret exists
  run: |
    if [ -z "${{ secrets.MY_SECRET }}" ]; then
      echo "Secret MY_SECRET is not set"
      exit 1
    fi
```

**Pass secrets to reusable workflows:**
```yaml
jobs:
  call-workflow:
    uses: ./.github/workflows/reusable.yml
    secrets:
      token: ${{ secrets.MY_TOKEN }}
      # Or pass all secrets
    secrets: inherit
```

### AWS Authentication Issues

**OIDC authentication failure:**
```yaml
# Ensure id-token permission is granted
permissions:
  id-token: write
  contents: read

- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
    aws-region: us-east-1
```

**Check trust policy in IAM role:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
        "token.actions.githubusercontent.com:sub": "repo:YourOrg/YourRepo:ref:refs/heads/main"
      }
    }
  }]
}
```

### Docker Registry Authentication

**Docker Hub rate limits:**
```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

**AWS ECR authentication:**
```yaml
- name: Login to Amazon ECR
  uses: aws-actions/amazon-ecr-login@v2
```

**GitHub Container Registry:**
```yaml
- name: Login to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

## 3. Performance & Timeout Issues

### Job Timeouts

**Default timeout:** 360 minutes (6 hours)

**Symptoms:**
```
Error: The job running on runner <name> has exceeded the maximum execution time of 360 minutes.
```

**Solutions:**

**Increase timeout:**
```yaml
jobs:
  build:
    timeout-minutes: 60  # Set realistic limit
```

**Add step-level timeouts:**
```yaml
steps:
  - name: Long running test
    timeout-minutes: 30
    run: pytest tests/integration/
```

**Break into smaller jobs:**
```yaml
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/unit/

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/integration/
```

### Performance Optimization

**Slow dependency installation:**

**Problem:** Installing dependencies takes 5+ minutes

**Solutions:**
```yaml
# Use caching
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements*.txt') }}

# Use faster package managers
- run: pip install uv && uv pip install -r requirements.txt

# Pre-built Docker images
jobs:
  test:
    container: python:3.11-slim
```

**Slow Docker builds:**

**Problem:** Docker build takes 10+ minutes

**Solutions:**
```yaml
# Enable BuildKit and layer caching
- uses: docker/setup-buildx-action@v3
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max

# Multi-stage builds with dependency caching
# In Dockerfile:
# FROM python:3.11 AS builder
# COPY requirements.txt .
# RUN pip install --user -r requirements.txt
#
# FROM python:3.11-slim
# COPY --from=builder /root/.local /root/.local
```

**Slow test runs:**
```yaml
# Parallelize with matrix
strategy:
  matrix:
    test-group: [unit, integration, e2e]

# Use pytest-xdist
- run: pytest -n auto
```

### Runner Resource Constraints

**Out of disk space:**
```yaml
- name: Free disk space
  run: |
    docker system prune -af
    sudo rm -rf /usr/share/dotnet
    sudo rm -rf /opt/ghc
    df -h
```

**Memory issues:**
```yaml
# Use larger runners (requires GitHub Teams/Enterprise)
runs-on: ubuntu-latest-4-cores

# Or optimize memory usage
- run: pytest --maxfail=1 -x
```

## 4. Conditional Logic & Expressions

### Expression Context Issues

**Common mistake - wrong context:**
```yaml
# ❌ BAD - steps context not available in job-level if
jobs:
  deploy:
    if: steps.build.outcome == 'success'  # FAILS

# ✅ GOOD - use needs context
jobs:
  build:
    outputs:
      status: ${{ job.status }}
  deploy:
    needs: build
    if: needs.build.outputs.status == 'success'
```

### Always() vs Success() vs Failure()

**Execution conditions:**
```yaml
steps:
  - name: Always runs
    if: always()
    run: echo "Cleanup"

  - name: Only if previous steps succeeded
    if: success()
    run: echo "Deploy"

  - name: Only if previous steps failed
    if: failure()
    run: echo "Send failure notification"

  - name: Only if workflow was cancelled
    if: cancelled()
    run: echo "Cleanup after cancel"
```

### Complex Conditionals

**Multiple conditions:**
```yaml
# AND logic
if: github.ref == 'refs/heads/main' && github.event_name == 'push'

# OR logic
if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'

# NOT logic
if: "!contains(github.event.head_commit.message, '[skip ci]')"

# Combining operators
if: |
  (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/heads/release/'))
  && !contains(github.event.head_commit.message, '[skip ci]')
```

### String Comparison

**Case sensitivity:**
```yaml
# Case-sensitive comparison
if: github.ref == 'refs/heads/main'

# Case-insensitive
if: contains(fromJSON('["main", "master"]'), github.ref_name)
```

### Checking for Empty Values

```yaml
# Check if variable is set
if: env.MY_VAR != ''

# Check if secret exists
if: secrets.API_KEY != ''

# Using default values
env:
  MY_VAR: ${{ inputs.value || 'default' }}
```

### Path Filtering Logic

**Run only on specific file changes:**
```yaml
on:
  pull_request:
    paths:
      - 'src/**'
      - '!src/docs/**'

# Or use path-filter action for complex logic
- uses: dorny/paths-filter@v2
  id: filter
  with:
    filters: |
      backend:
        - 'api/**'
      frontend:
        - 'web/**'

- name: Backend tests
  if: steps.filter.outputs.backend == 'true'
  run: pytest api/tests/
```

## Debugging Techniques

### Enable Debug Logging

**Set repository secrets:**
- `ACTIONS_STEP_DEBUG = true` - Detailed step debugging
- `ACTIONS_RUNNER_DEBUG = true` - Runner diagnostic logs

**Or use workflow inputs:**
```yaml
on:
  workflow_dispatch:
    inputs:
      debug:
        type: boolean
        default: false

jobs:
  build:
    env:
      ACTIONS_STEP_DEBUG: ${{ inputs.debug }}
```

### Add Diagnostic Steps

```yaml
- name: Debug context
  if: runner.debug == '1'
  run: |
    echo "Event name: ${{ github.event_name }}"
    echo "Ref: ${{ github.ref }}"
    echo "SHA: ${{ github.sha }}"
    echo "Actor: ${{ github.actor }}"
    env | sort

- name: Dump GitHub context
  run: echo '${{ toJSON(github) }}'

- name: Dump job context
  run: echo '${{ toJSON(job) }}'
```

### Re-run Failed Jobs

```bash
# Via GitHub CLI
gh run rerun <run-id> --failed

# Re-run with debug logging
gh run rerun <run-id> --debug
```

### Use tmate for Interactive Debugging

```yaml
- name: Setup tmate session
  if: failure()
  uses: mxschmitt/action-tmate@v3
  timeout-minutes: 30
```

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Resource not accessible by integration` | Insufficient GITHUB_TOKEN permissions | Add required permissions to job/workflow |
| `Invalid workflow file` | YAML syntax error | Run actionlint or yamllint |
| `Secret not found` | Secret name mismatch or not set | Check repository/org settings |
| `Rate limit exceeded` | Too many API calls | Add authentication, reduce request frequency |
| `No space left on device` | Disk full | Clean up artifacts, use docker prune |
| `Timeout exceeded` | Job/step ran too long | Add timeout-minutes, optimize performance |
| `Context not available` | Wrong context used in expression | Check available contexts for that scope |
