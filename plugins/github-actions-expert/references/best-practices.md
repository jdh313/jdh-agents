# GitHub Actions Best Practices

## Performance Optimization

### Caching Strategies

**Python Dependencies:**
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

**Node.js Dependencies:**
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

**Docker Layers:**
```yaml
- uses: docker/setup-buildx-action@v3
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Terraform:**
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.terraform.d/plugin-cache
      .terraform
    key: ${{ runner.os }}-terraform-${{ hashFiles('**/.terraform.lock.hcl') }}
```

### Workflow Optimization

**Concurrency Control (prevent duplicate runs):**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Conditional Job Execution:**
```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

**Path Filters (skip unnecessary runs):**
```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'tests/**'
      - '.github/workflows/**'
```

## Security Best Practices

### Secrets Management

**Never hardcode secrets:**
```yaml
# ❌ BAD
env:
  API_KEY: "sk-1234567890abcdef"

# ✅ GOOD
env:
  API_KEY: ${{ secrets.API_KEY }}
```

**Use environment protection rules for production:**
```yaml
jobs:
  deploy-prod:
    environment:
      name: production
      url: https://prod.example.com
    steps:
      - run: deploy.sh
```

**Least privilege for GITHUB_TOKEN:**
```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
```

### Dependency Security

**Pin action versions by SHA (most secure):**
```yaml
# ❌ Less secure (mutable tags)
- uses: actions/checkout@v4

# ✅ More secure (immutable SHA)
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
```

**Use Dependabot for action updates:**
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### Artifact Security

**Set retention policies:**
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: build-artifacts
    path: dist/
    retention-days: 7
```

## Reliability Patterns

### Retry Logic for Flaky Steps

```yaml
- name: Run flaky test
  uses: nick-invision/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    command: pytest tests/integration/
```

### Timeout Protection

```yaml
jobs:
  build:
    timeout-minutes: 30
    steps:
      - name: Long running task
        timeout-minutes: 20
        run: ./build.sh
```

### Job Dependencies

```yaml
jobs:
  build:
    runs-on: ubuntu-latest

  test:
    needs: build
    runs-on: ubuntu-latest

  deploy:
    needs: [build, test]
    runs-on: ubuntu-latest
```

## Matrix Build Patterns

### Python Multi-version Testing

```yaml
strategy:
  fail-fast: false
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']
    os: [ubuntu-latest, windows-latest, macos-latest]
    exclude:
      - os: macos-latest
        python-version: '3.9'
```

### Include/Exclude Variations

```yaml
strategy:
  matrix:
    node-version: [16, 18, 20]
    include:
      - node-version: 20
        experimental: true
    exclude:
      - node-version: 16
```

## Reusable Workflows

### Calling a Reusable Workflow

```yaml
jobs:
  call-workflow:
    uses: WaitesWireless/aws-github-actions/.github/workflows/deploy.yml@main
    with:
      environment: production
    secrets:
      aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
```

### Creating a Reusable Workflow

```yaml
# .github/workflows/reusable-build.yml
on:
  workflow_call:
    inputs:
      target:
        required: true
        type: string
    outputs:
      artifact-url:
        value: ${{ jobs.build.outputs.url }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      url: ${{ steps.upload.outputs.artifact-url }}
```

## Self-Hosted Runners

### Runner Labels and Selection

```yaml
jobs:
  build:
    runs-on: [self-hosted, linux, x64, gpu]
```

### Cleanup After Jobs

```yaml
- name: Cleanup
  if: always()
  run: |
    docker system prune -af
    rm -rf ${{ github.workspace }}/*
```

## Debugging Tips

**Enable debug logging:**
```bash
# Set repository secrets:
ACTIONS_STEP_DEBUG = true
ACTIONS_RUNNER_DEBUG = true
```

**Conditional debug steps:**
```yaml
- name: Debug info
  if: runner.debug == '1'
  run: |
    env
    pwd
    ls -la
```
