# Review Dimensions & Findings Structure

The architecture pass is high-freedom judgment work — these are checklists to
reason against, not a script. Lead with the reconstructed topology; then walk
the dimensions; then sort findings into the two tiers.

---

## Reconstruct the topology FIRST

Before judging anything, state the resource graph the change implies, in plain
terms. This is the core principle of the review — the plan text, not the HCL
diff, is the source of truth for what actually changes.

From the plan text + HCL diff, name:
- **Compute** added/changed/removed (ECS services/tasks, Lambdas, EC2, ASGs).
- **Data stores** (RDS/Aurora, DynamoDB, S3, ElastiCache, EFS) — and which are
  **stateful** (data loss on destroy).
- **Network paths** (VPCs, subnets, SGs, NACLs, NAT, ALB/NLB, route tables,
  VPC endpoints) — what can now reach what.
- **IAM trust edges** (roles, assume-role/trust policies, attached policies,
  PassRole) — who can now act as what.

Write a **before → after** topology sentence per project. Example:
> Before: ALB → ECS service (2 tasks) → Aurora (single-AZ). After: same, plus a
> new Lambda triggered by an SQS queue with no DLQ, granted `s3:*` on the
> reports bucket.

If truncation (see `plan-parsing.md`) left a project partial, say the topology
is **reconstructed from incomplete plan output** and mark it `unverifiable`.

---

## Dimensions

### Plan-level hazards (highest signal)
- **Destroy-and-recreate (`-/+`) on a stateful resource** — RDS/Aurora, EBS/EFS
  volume, S3 bucket, stateful endpoint. This is the top hazard: silent data
  loss. Quote the `# forces replacement` cause.
- **Plan scope vs diff scope mismatch** — plan changes resources the diff didn't
  obviously touch (drift, or a shared-module edit rippling), or the diff touches
  a dir with no plan. Both are drift signals.
- **Plan summary sanity** — does `N to add, M to change, K to destroy` match the
  PR's stated intent? A "rename a tag" PR that destroys 4 resources is suspect.

### Security
- IAM **wildcards** (`Action: "*"`, `Resource: "*"`) and **PassRole** scope
  overreach (can pass any role → privilege escalation).
- `0.0.0.0/0` **ingress** (and over-broad **egress**) on SGs/NACLs.
- Secrets in HCL or committed to state (plaintext `password`, tokens, keys).
- Encryption flags at rest and in transit on sensitive resources (RDS storage,
  S3 SSE, EBS, TLS on listeners).

### Change safety
- `prevent_destroy` / `deletion_protection` present on critical resources?
- **Blast radius of shared-module edits** — a change to a module N stacks consume
  affects all N. Name the dependents if discoverable.
- Provider/module **version pinning** vs uncontrolled upgrade risk.

### Architecture & resilience
- **SPOFs**: single NAT gateway, single-AZ RDS, single ALB path, one-replica
  anything load-bearing.
- **Failure modes of async glue**: SQS/SNS/EventBridge without a **DLQ**;
  non-idempotent retries; missing visibility/logging.
- **Trust boundaries & data flow** — and in this healthcare context, the **PHI
  path** explicitly: does PHI cross a new boundary, land unencrypted, or become
  reachable from a broader network?
- **Service fitness** — is the chosen service right for the use case and the
  team's operational maturity?
- **Cost & scaling shape** vs the deployment profile (fed by infracost).
- **Operability**: CloudWatch alarms, backup/snapshot retention, runbook refs.

### One-way vs two-way doors
Flag changes that are **hard to reverse** (data store replace, account-level
settings, public DNS/endpoint changes, IAM trust to external principals) vs
easily-rolled-back tweaks. Reversibility belongs in every design concern.

### Intent check
- PR description / linked ticket vs the **actual** resource changes — does the
  implementation match what it claims to do? Under- and over-reach both count.
- Rationale against **recorded decisions** — if NDR grounding (conditional
  phase) returned heads, treat them as ground truth. A change that contradicts a
  current head is a finding; cite the `ndr:` reference.

---

## Findings structure — two tiers

### Tier 1 — Design concerns (escalate to humans)
For each: the reconstructed **before/after**, the **risk**, **reversibility**
(one-way/two-way), and a **recommendation**. These need human judgment — plan
hazards, security overreach, SPOFs, PHI-path changes, intent mismatches,
decision contradictions.

### Tier 2 — Mechanical issues (inline-comment candidates)
Specific, localized, `file:line` + resource address. Linter/policy findings,
missing encryption flag, unpinned version. Each phrased so it can be posted as
an inline PR comment verbatim.

Mark every finding's **confidence** (high/medium/low). Plain-text plan parsing
is lossy; a low-confidence finding is better stated-with-caveat than dropped or
overclaimed.
