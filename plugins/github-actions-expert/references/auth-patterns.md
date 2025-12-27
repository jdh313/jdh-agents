# Authentication Patterns for GitHub Actions

## GitHub Authentication

### GITHUB_TOKEN (Built-in)

**Automatic token available in every workflow:**
```yaml
steps:
  - name: Create issue comment
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    run: gh issue comment ${{ github.event.issue.number }} --body "Done!"
```

**Permissions model:**
```yaml
permissions:
  # Read-only by default for forked PRs
  contents: read

  # Grant write permissions as needed
  pull-requests: write
  issues: write
  packages: write
  deployments: write
```

**Use cases:**
- Checkout private repositories
- Create/update issues and PRs
- Publish packages to GitHub Packages
- Create releases
- Post commit statuses

**Limitations:**
- Cannot trigger new workflow runs (prevents recursive workflows)
- Limited to repository scope
- For cross-repository or elevated access, use a Personal Access Token (PAT) or GitHub App

### Personal Access Token (PAT)

**When to use:**
- Cross-repository access
- Triggering workflows from workflows
- Elevated permissions beyond GITHUB_TOKEN

**Fine-grained PAT (recommended):**
```yaml
# Store as repository secret: MY_PAT

- uses: actions/checkout@v4
  with:
    token: ${{ secrets.MY_PAT }}

- name: Trigger workflow in another repo
  env:
    GH_TOKEN: ${{ secrets.MY_PAT }}
  run: |
    gh workflow run deploy.yml \
      --repo OrgName/OtherRepo \
      --ref main
```

**Security best practices:**
- Use fine-grained PATs with minimal permissions
- Set expiration dates
- Scope to specific repositories
- Store as encrypted secrets
- Rotate regularly

### GitHub App Authentication

**Most secure for automation:**

```yaml
- name: Generate GitHub App token
  id: generate-token
  uses: actions/create-github-app-token@v1
  with:
    app-id: ${{ secrets.APP_ID }}
    private-key: ${{ secrets.APP_PRIVATE_KEY }}
    owner: ${{ github.repository_owner }}

- name: Use app token
  env:
    GH_TOKEN: ${{ steps.generate-token.outputs.token }}
  run: gh api /repos/${{ github.repository }}/issues
```

**Advantages:**
- Granular permissions per installation
- Can trigger workflows (unlike GITHUB_TOKEN)
- Audit logs show app identity
- No user account dependency

## AWS Authentication

### OIDC (Recommended - No long-lived credentials)

**Setup trust relationship in AWS IAM:**
1. Create OIDC identity provider for GitHub
2. Create IAM role with trust policy
3. Configure workflow

**Workflow configuration:**
```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
          aws-region: us-east-1
          role-session-name: GitHubActions-${{ github.run_id }}
```

**IAM role trust policy:**
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
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:OrgName/RepoName:*"
      }
    }
  }]
}
```

**Restrict by branch:**
```json
"Condition": {
  "StringEquals": {
    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
    "token.actions.githubusercontent.com:sub": "repo:OrgName/RepoName:ref:refs/heads/main"
  }
}
```

**Restrict by environment:**
```json
"Condition": {
  "StringLike": {
    "token.actions.githubusercontent.com:sub": "repo:OrgName/RepoName:environment:production"
  }
}
```

### Access Keys (Legacy - Less secure)

**Only if OIDC not available:**
```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-east-1
```

**Security considerations:**
- Store in encrypted secrets
- Use least-privilege IAM policies
- Rotate regularly
- Consider using temporary credentials via STS

### AWS Authentication for Specific Services

**ECR (Elastic Container Registry):**
```yaml
- name: Login to Amazon ECR
  id: login-ecr
  uses: aws-actions/amazon-ecr-login@v2

- name: Build and push
  env:
    ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
  run: |
    docker build -t $ECR_REGISTRY/my-app:${{ github.sha }} .
    docker push $ECR_REGISTRY/my-app:${{ github.sha }}
```

**S3 operations:**
```yaml
- name: Upload to S3
  run: |
    aws s3 sync ./dist s3://my-bucket/path/ \
      --delete \
      --cache-control "max-age=3600"
```

**Lambda deployment:**
```yaml
- name: Update Lambda function
  run: |
    aws lambda update-function-code \
      --function-name my-function \
      --zip-file fileb://function.zip
```

## Azure Authentication

### OIDC for Azure (Recommended)

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Azure login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

### Service Principal (Legacy)

```yaml
- name: Azure login
  uses: azure/login@v1
  with:
    creds: ${{ secrets.AZURE_CREDENTIALS }}
```

**AZURE_CREDENTIALS format:**
```json
{
  "clientId": "<client-id>",
  "clientSecret": "<client-secret>",
  "subscriptionId": "<subscription-id>",
  "tenantId": "<tenant-id>"
}
```

## GCP Authentication

### Workload Identity Federation (Recommended)

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: 'projects/123456789/locations/global/workloadIdentityPools/github/providers/github-provider'
          service_account: 'github-actions@my-project.iam.gserviceaccount.com'

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy my-service \
            --image gcr.io/my-project/my-image:${{ github.sha }} \
            --region us-central1
```

### Service Account Key (Legacy)

```yaml
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    credentials_json: ${{ secrets.GCP_SA_KEY }}
```

## Docker Registry Authentication

### Docker Hub

```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

### GitHub Container Registry (GHCR)

```yaml
- name: Login to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### Multi-registry authentication

```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}

- name: Login to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}

- name: Build and push to multiple registries
  run: |
    docker build -t myapp:${{ github.sha }} .
    docker tag myapp:${{ github.sha }} dockerhub-user/myapp:latest
    docker tag myapp:${{ github.sha }} ghcr.io/${{ github.repository }}:latest
    docker push dockerhub-user/myapp:latest
    docker push ghcr.io/${{ github.repository }}:latest
```

## Secrets Management Best Practices

### Repository Secrets

**Create secrets via UI:**
Settings → Secrets and variables → Actions → New repository secret

**Access in workflow:**
```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}
```

### Organization Secrets

**Share secrets across repositories:**
- Organization settings → Secrets and variables → Actions
- Select repositories that can access the secret

### Environment Secrets

**Environment-specific secrets with protection rules:**
```yaml
jobs:
  deploy-prod:
    environment:
      name: production
      url: https://prod.example.com
    steps:
      - name: Deploy
        env:
          PROD_API_KEY: ${{ secrets.PROD_API_KEY }}
        run: ./deploy.sh
```

**Protection rules:**
- Required reviewers
- Wait timer
- Deployment branches restriction

### Secrets in Composite Actions

**Cannot directly access secrets:**
```yaml
# ❌ BAD - secrets not available in composite actions
runs:
  using: composite
  steps:
    - run: echo ${{ secrets.MY_SECRET }}  # FAILS
```

**Pass as inputs:**
```yaml
# Composite action definition
inputs:
  api-key:
    required: true

runs:
  using: composite
  steps:
    - run: echo "${{ inputs.api-key }}"
      shell: bash

# Calling the action
- uses: ./.github/actions/my-action
  with:
    api-key: ${{ secrets.API_KEY }}
```

### Secrets Security Guidelines

**Do:**
- Use secrets for all sensitive data
- Rotate secrets regularly
- Use least-privilege principles
- Audit secret access
- Use environment protection for production secrets

**Don't:**
- Log secrets (even accidentally)
- Pass secrets in URLs
- Store secrets in code or config files
- Use the same secret across multiple environments
- Share secrets between unrelated repositories

**Prevent secret leakage:**
```yaml
# GitHub automatically redacts registered secrets in logs
# But be careful with:

# ❌ BAD - may expose secret
- run: curl https://api.example.com?token=${{ secrets.API_KEY }}

# ✅ GOOD - use headers or POST body
- run: |
    curl https://api.example.com \
      -H "Authorization: Bearer ${{ secrets.API_KEY }}"
```

## SSH Key Authentication

### Deploy keys

**For repository-specific access:**
```yaml
- name: Setup SSH key
  uses: webfactory/ssh-agent@v0.8.0
  with:
    ssh-private-key: ${{ secrets.SSH_DEPLOY_KEY }}

- name: Clone private repo
  run: git clone git@github.com:OrgName/PrivateRepo.git
```

### SSH agent with multiple keys

```yaml
- uses: webfactory/ssh-agent@v0.8.0
  with:
    ssh-private-key: |
      ${{ secrets.SSH_KEY_1 }}
      ${{ secrets.SSH_KEY_2 }}
```

## API Token Patterns

### Scoped tokens

**Create separate tokens for different purposes:**
```yaml
# PyPI publishing
PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}

# NPM publishing
NPM_TOKEN: ${{ secrets.NPM_TOKEN }}

# Documentation deployment
DOCS_TOKEN: ${{ secrets.DOCS_TOKEN }}
```

### Token validation

**Check token before use:**
```yaml
- name: Validate token
  run: |
    if [ -z "${{ secrets.API_TOKEN }}" ]; then
      echo "Error: API_TOKEN not set"
      exit 1
    fi
    # Test token works
    curl -f -H "Authorization: Bearer ${{ secrets.API_TOKEN }}" \
      https://api.example.com/validate
```

## Third-Party Service Authentication

### Slack notifications

```yaml
- name: Send Slack notification
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Deployment completed: ${{ github.sha }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### Datadog

```yaml
- name: Send metrics to Datadog
  env:
    DD_API_KEY: ${{ secrets.DD_API_KEY }}
  run: |
    curl -X POST "https://api.datadoghq.com/api/v1/series" \
      -H "DD-API-KEY: ${DD_API_KEY}" \
      -d @metrics.json
```

### Terraform Cloud

```yaml
- name: Setup Terraform
  uses: hashicorp/setup-terraform@v3
  with:
    cli_config_credentials_token: ${{ secrets.TF_API_TOKEN }}
```
