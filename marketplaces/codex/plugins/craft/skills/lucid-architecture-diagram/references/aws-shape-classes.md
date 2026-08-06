# AWS 2024 Shape Class Catalog

Reference for `block_type` values when calling `lucid_add_block` with AWS service icons.

Lucid uses the AWS 2024 icon set. All classes follow the pattern:

```
aws2024-<category>-Arch<ServiceName>AWS2024
```

Some resources (sub-icons of a service) use `Res` instead of `Arch`:

```
aws2024-<category>-Res<ResourceName>AWS2024
```

And data-catalog-style icons sometimes use:

```
aws2024-<category>-ResAWS<Name>AWS2024
```

Resolve unknown classes by: (a) fetching a page that already contains the desired icon to read its `shapeType` from the JSON, or (b) asking the user to drag one in, then re-fetching.

## Category names (the `<category>` slot)

Observed in practice:

| Category | AWS service area |
|---|---|
| `compute` | EC2, Lambda, ECS, EKS, Batch |
| `containers` | ECR, ECS, EKS, Fargate |
| `database` | RDS, Aurora, DynamoDB, ElastiCache |
| `storage` | S3, EBS, EFS, FSx |
| `networkingandcontentdelivery` | Route 53, ELB, CloudFront, API Gateway, VPC sub-resources |
| `networkingcontentdelivery` | Alternative spelling — some classes use this without the "and" |
| `securityidentityandcompliance` | IAM, Secrets Manager, ACM, KMS, WAF, Cognito |
| `managementandgovernance` | CloudWatch, CloudFormation, Systems Manager, Organizations |
| `analytics` | Athena, Glue, Kinesis, QuickSight, EMR |
| `generalresources` | Users, generic icons |

If a class isn't ready, try the alternative spelling of `networkingandcontentdelivery` ↔ `networkingcontentdelivery`. Both have appeared in real diagrams.

## Common shape classes — Phase 2 CRUD app stack

These are verified-working classes encountered in real diagrams:

### Compute & Containers

| Service | Class |
|---|---|
| Lambda | `aws2024-compute-ArchAWSLambdaAWS2024` |
| ECS (cluster icon) | `aws2024-containers-ArchAmazonElasticContainerServiceAWS2024` |
| ECR | `aws2024-containers-ArchAmazonElasticContainerRegistryAWS2024` |

### Database

| Service | Class |
|---|---|
| Aurora | `aws2024-database-ArchAmazonAuroraAWS2024` |

### Storage

| Service | Class |
|---|---|
| S3 | `aws2024-storage-ArchAmazonSimpleStorageServiceAWS2024` |

### Networking & Content Delivery

| Service | Class |
|---|---|
| Route 53 | `aws2024-networkingandcontentdelivery-ArchAmazonRoute53AWS2024` |
| Elastic Load Balancing | `aws2024-networkingandcontentdelivery-ArchElasticLoadBalancingAWS2024` |
| NAT Gateway (resource) | `aws2024-networkingandcontentdelivery-ResAmazonVPCNATGatewayAWS2024` |

### Security, Identity & Compliance

| Service | Class |
|---|---|
| Secrets Manager | `aws2024-securityidentityandcompliance-ArchAWSSecretsManagerAWS2024` |
| Certificate Manager (ACM) | `aws2024-securityidentityandcompliance-ArchAWSCertificateManagerAWS2024` |

### Management & Governance

| Service | Class |
|---|---|
| CloudWatch | `aws2024-managementandgovernance-ArchAmazonCloudWatchAWS2024` |

### Analytics

| Service | Class |
|---|---|
| Athena | `aws2024-analytics-ArchAmazonAthenaAWS2024` |
| QuickSight | `aws2024-analytics-ArchAmazonQuickSightAWS2024` |
| Glue Data Catalog (resource) | `aws2024-analytics-ResAWSGlueDataCatalogAWS2024` |

### General Resources

| Item | Class |
|---|---|
| Users icon | `aws2024-generalresources-ResUsers48LightAWS2024` |

## Container shapes (for nesting)

These are containers, not service icons. They appear in `flowcharts[].nodes[]` with `childrenIds`.

| Container | Shape type |
|---|---|
| AWS Cloud | `Amazon Cloud` (also seen as `AWSCloudAWS2024` in `BlockClass`) |
| Region | `aws-2k-shape-library-region` |
| VPC | `Virtual private cloud (VPC)` |
| Public subnet | `aws-2k-shape-library-public-subnet` |
| Private subnet | `aws-2k-shape-library-private-subnet` |
| GCP container (cross-cloud) | `gcp-2021-google-cloud-container` |

Container containers (Region, VPC, subnets) typically come pre-populated with `assistedLayoutEnabled: true` — see Gotcha 2 in SKILL.md.

## Generic shapes (always work, no library registration needed)

When AWS shapes aren't ready or icons aren't critical, fall back to generic shapes:

| Need | Class |
|---|---|
| Rectangle | `RectangleBlock` or `plugin-geometricshapes-shape-rectangle` |
| Default placeholder | `plugin-default-block-name` (square) |
| Text | `plugin-flowchart-shape-text` |

Style with `fill_color` and `line_color` (hex `#RRGGBB`) to convey service category at a glance.

## Resolving an unknown class

When asked to add a service not in this catalog:

1. **Fetch a page that already has the icon** (e.g. another diagram in the same doc, page 1 of the current doc) and grep the JSON for the service name in `shapeType` fields.
2. **Ask the user to drag the shape onto the page**, then re-fetch and read its `shapeType`. Add the class to this catalog after confirming it works.
3. **Try the obvious construction** from the pattern, plus the `networkingandcontentdelivery` ↔ `networkingcontentdelivery` variant. If both fail, fall back to a styled generic rectangle.
