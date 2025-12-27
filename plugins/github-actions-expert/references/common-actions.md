# Common GitHub Actions (Marketplace)

## Essential Actions

### actions/checkout@v4
**Purpose:** Clone repository into the runner

**Common usage:**
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Full history for git operations
    submodules: recursive  # Include submodules
    token: ${{ secrets.GITHUB_TOKEN }}  # Use custom token
```

**When to use:** Nearly every workflow needs this to access code

### actions/setup-python@v5
**Purpose:** Set up Python environment

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'  # Cache pip dependencies
```

**Matrix example:**
```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']
steps:
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python-version }}
```

### actions/setup-node@v4
**Purpose:** Set up Node.js environment

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'  # Or 'yarn', 'pnpm'
```

### actions/cache@v4
**Purpose:** Cache dependencies and build outputs

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      .pytest_cache
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

### actions/upload-artifact@v4
**Purpose:** Upload build artifacts

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: build-artifacts
    path: dist/
    retention-days: 7
    if-no-files-found: error
```

### actions/download-artifact@v4
**Purpose:** Download artifacts from previous jobs

```yaml
- uses: actions/download-artifact@v4
  with:
    name: build-artifacts
    path: ./downloaded
```

## Docker Actions

### docker/setup-buildx-action@v3
**Purpose:** Set up Docker Buildx (multi-platform builds, caching)

```yaml
- uses: docker/setup-buildx-action@v3
```

### docker/login-action@v3
**Purpose:** Login to Docker registry

```yaml
- uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### docker/build-push-action@v5
**Purpose:** Build and push Docker images

```yaml
- uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: |
      ghcr.io/${{ github.repository }}:latest
      ghcr.io/${{ github.repository }}:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
    platforms: linux/amd64,linux/arm64
```

### docker/metadata-action@v5
**Purpose:** Generate Docker image tags and labels

```yaml
- uses: docker/metadata-action@v5
  id: meta
  with:
    images: ghcr.io/${{ github.repository }}
    tags: |
      type=ref,event=branch
      type=semver,pattern={{version}}
      type=sha
```

## Cloud Provider Actions

### aws-actions/configure-aws-credentials@v4
**Purpose:** Configure AWS credentials (OIDC or access keys)

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
    aws-region: us-east-1
```

### aws-actions/amazon-ecr-login@v2
**Purpose:** Login to Amazon ECR

```yaml
- uses: aws-actions/amazon-ecr-login@v2
  id: login-ecr
```

### google-github-actions/auth@v2
**Purpose:** Authenticate to Google Cloud

```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: 'projects/123/locations/global/workloadIdentityPools/pool/providers/provider'
    service_account: 'github-actions@project.iam.gserviceaccount.com'
```

### azure/login@v1
**Purpose:** Login to Azure

```yaml
- uses: azure/login@v1
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

## Infrastructure as Code

### hashicorp/setup-terraform@v3
**Purpose:** Set up Terraform CLI

```yaml
- uses: hashicorp/setup-terraform@v3
  with:
    terraform_version: 1.6.0
    terraform_wrapper: false
```

### aws-actions/aws-cloudformation-github-deploy@v1
**Purpose:** Deploy CloudFormation stacks

```yaml
- uses: aws-actions/aws-cloudformation-github-deploy@v1
  with:
    name: my-stack
    template: template.yaml
    no-fail-on-empty-changeset: '1'
```

## Release & Publishing

### softprops/action-gh-release@v1
**Purpose:** Create GitHub releases

```yaml
- uses: softprops/action-gh-release@v1
  if: startsWith(github.ref, 'refs/tags/')
  with:
    files: |
      dist/*
      checksums.txt
    generate_release_notes: true
    draft: false
```

### pypa/gh-action-pypi-publish@release/v1
**Purpose:** Publish to PyPI

```yaml
- uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.PYPI_API_TOKEN }}
    packages-dir: dist/
```

## Code Quality & Testing

### codecov/codecov-action@v4
**Purpose:** Upload test coverage to Codecov

```yaml
- uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    files: ./coverage.xml
    fail_ci_if_error: true
```

### github/super-linter@v5
**Purpose:** Run multiple linters

```yaml
- uses: github/super-linter@v5
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    VALIDATE_ALL_CODEBASE: false
    DEFAULT_BRANCH: main
```

### pre-commit/action@v3.0.0
**Purpose:** Run pre-commit hooks

```yaml
- uses: pre-commit/action@v3.0.0
```

## Versioning & Changelog

### cycjimmy/semantic-release-action@v4
**Purpose:** Automated versioning and releases (conventional commits)

```yaml
- uses: cycjimmy/semantic-release-action@v4
  with:
    branch: main
    extra_plugins: |
      @semantic-release/changelog
      @semantic-release/git
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### mathieudutour/github-tag-action@v6.1
**Purpose:** Auto-increment version tags

```yaml
- uses: mathieudutour/github-tag-action@v6.1
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    default_bump: minor
```

## Notifications & Integrations

### slackapi/slack-github-action@v1
**Purpose:** Send Slack notifications

```yaml
- uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Deployment to production completed"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## Security Scanning

### github/codeql-action/init@v3
**Purpose:** Initialize CodeQL analysis

```yaml
- uses: github/codeql-action/init@v3
  with:
    languages: python, javascript

- uses: github/codeql-action/analyze@v3
```

### aquasecurity/trivy-action@master
**Purpose:** Container vulnerability scanning

```yaml
- uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'ghcr.io/${{ github.repository }}:${{ github.sha }}'
    format: 'sarif'
    output: 'trivy-results.sarif'
```

## Utility Actions

### dorny/paths-filter@v2
**Purpose:** Detect which files changed

```yaml
- uses: dorny/paths-filter@v2
  id: filter
  with:
    filters: |
      backend:
        - 'api/**'
      frontend:
        - 'web/**'
      docs:
        - 'docs/**'

- name: Backend tests
  if: steps.filter.outputs.backend == 'true'
  run: pytest
```

### peter-evans/create-pull-request@v5
**Purpose:** Create PRs from workflow changes

```yaml
- uses: peter-evans/create-pull-request@v5
  with:
    commit-message: 'chore: auto-update dependencies'
    title: 'Auto-update dependencies'
    branch: auto-update-deps
    delete-branch: true
```

### actions/github-script@v7
**Purpose:** Run JavaScript using GitHub API (octokit)

```yaml
- uses: actions/github-script@v7
  with:
    script: |
      const issue = await github.rest.issues.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        title: 'Automated issue',
        body: 'Created from workflow'
      })
```

### mxschmitt/action-tmate@v3
**Purpose:** Interactive debugging via SSH

```yaml
- uses: mxschmitt/action-tmate@v3
  if: failure()
  timeout-minutes: 30
```

### webfactory/ssh-agent@v0.8.0
**Purpose:** Set up SSH agent with private keys

```yaml
- uses: webfactory/ssh-agent@v0.8.0
  with:
    ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
```

### actions/create-github-app-token@v1
**Purpose:** Generate installation token for GitHub App

```yaml
- uses: actions/create-github-app-token@v1
  id: app-token
  with:
    app-id: ${{ secrets.APP_ID }}
    private-key: ${{ secrets.APP_PRIVATE_KEY }}
```

## WaitesWireless Custom Actions

### WaitesWireless/aws-github-actions
**Purpose:** Reusable workflows and actions for AWS deployments

**Repository:** https://github.com/WaitesWireless/aws-github-actions

**Usage pattern:**
```yaml
# Call reusable workflow
jobs:
  deploy:
    uses: WaitesWireless/aws-github-actions/.github/workflows/deploy.yml@main
    with:
      environment: production
    secrets: inherit
```

**When to suggest additions:**
- Repeated patterns across multiple repositories
- AWS-specific deployment workflows
- Common IoT/gateway deployment tasks
- Shared validation or testing workflows

## Action Version Pinning Strategies

### Mutable tags (least secure, most convenient)
```yaml
- uses: actions/checkout@v4
```

### Immutable SHA (most secure)
```yaml
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1
```

### Semantic versioning (balanced)
```yaml
- uses: actions/checkout@v4.1.1
```

**Recommendation:** Use SHA pinning for production workflows, mutable tags for development workflows. Always add version comments when using SHAs.
