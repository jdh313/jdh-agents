---
name: lambda-to-fastapi-documenter
description: Use Skill(lambda-to-fastapi-documenter:lambda-to-fastapi-documenter) when analyzing AWS Lambda functions (Python or Node.js) for migration to FastAPI. Use for extracting configuration fields, documenting CRUD logic, or mapping Lambda handlers to REST API specifications. Triggers include "document this Lambda", "extract config from this Lambda", "analyze this Lambda for FastAPI migration", or "help me understand the configuration logic in this Lambda".
---

# Lambda to FastAPI Documenter

## Overview

Extract and document configuration fields, business logic, and REST API specifications from AWS Lambda CRUD handlers for FastAPI migration. Analyze Lambda functions to produce language-agnostic configuration documentation in structured formats (Markdown tables and YAML).

## When to Use This Skill

Invoke this skill when:
- Analyzing Lambda function code for FastAPI migration
- Documenting configuration fields being read or written
- Extracting CRUD operation logic from Lambda handlers
- Mapping Lambda handlers to REST API specifications
- Understanding data flows between API requests, Lambda logic, and database operations

## Workflow

Follow this sequential process to analyze and document Lambda CRUD operations:

### 1. Identify Lambda Context

Understand the Lambda function's role in the CRUD API:

1. **Locate the handler function** (typically `handler`, `lambda_handler`, or similar export)
2. **Determine the HTTP operation**: GET (read), POST (create), PATCH/PUT (update), DELETE (remove)
3. **Extract the API path pattern**:
   - Check CloudFormation/SAM templates for `AWS::Lambda::Permission` resources
   - Look for path parameters in `event.pathParameters`
   - Identify the endpoint pattern (e.g., `/v1/gateway/{gatewayId}`)
4. **Identify authentication/authorization**:
   - Look for auth middleware or functions (e.g., `authenticateUser()`)
   - Note any token validation, user extraction, or permission checks

**Output**: Record endpoint specification:
```markdown
## Endpoint: GET /v1/gateway/{gatewayId}
- **Lambda**: GatewayConfigGet
- **Authentication**: Required (JWT via authenticateUser)
- **Path Parameters**: gatewayId (gateway MAC address)
```

### 2. Extract Configuration Fields

Analyze how configuration is read and written:

#### For GET Operations (Read)

1. **Locate database queries**: Find SQL SELECT statements or database client calls
2. **Identify field mappings**:
   - Database column names (e.g., `rms_interval`)
   - API response names (e.g., `RMS_CYCLE`)
   - SQL aliases using `AS` keyword
3. **Note transformations**:
   - Type conversions (e.g., `* 1000`, `UPPER()`, `LOWER()`)
   - Calculated fields (e.g., `poll_interval * 1000 as total_window_size`)
   - Default values or null handling
4. **Extract constants**: Look for constant definitions at top of file that map to field values

#### For PATCH/PUT Operations (Write)

1. **Parse request body structure**:
   - Look for `JSON.parse(event.body)` or similar
   - Identify expected field names in the request
2. **Find validation logic**:
   - Validation functions (e.g., `mapConfigSettings`, `checkMinGatewayVer`)
   - Type checks, boundary checks, regex patterns
   - Required field checks
3. **Track database updates**:
   - SQL UPDATE statements or ORM calls
   - Field name mappings (API → database)
   - WHERE clauses (which records are updated)
4. **Identify side effects**:
   - Logging (CloudWatch, application logs)
   - Notifications (Slack, SNS, email)
   - Triggers (Step Functions, EventBridge, IoT messages)
   - Cache invalidation

**Output**: Document each configuration field using the template in `references/config-documentation-template.md`

### 3. Document Business Logic

Capture non-obvious logic and domain rules:

1. **Conditional logic**:
   - Version-dependent features (e.g., `compareVersions(version, '2.0.0')`)
   - Feature flags or enabled/disabled states
   - Client-type specific behavior
2. **Field dependencies**:
   - Fields that must be set together
   - Fields that affect other fields
   - Cascading updates or derived values
3. **Domain constants and mappings**:
   - Lookup tables (e.g., `reading_type_to_alert_type`)
   - Status codes (e.g., `STATUS_ACTIVE = 0`)
   - Type enums (e.g., `TACH_TRIGGER_TYPE = 5`)
4. **Error handling**:
   - Validation error responses
   - Database error handling
   - Fallback values

**Output**: Capture logic in structured format:
```yaml
logic:
  description: "Controls RMS measurement cycle interval"
  validation:
    - "Must be positive integer"
    - "Requires gateway version >= 2.0.0"
  side_effects:
    - "Triggers CloudWatch log: GatewayConfigChanges"
    - "Sends Slack notification to #gateway-updates"
    - "Starts Step Function: GatewayCheckerStateMachine"
  dependencies:
    - "Requires alarms_enabled = true"
    - "Mirrors to hfdvue_rms_interval"
```

### 4. Map Data Flow

Trace the path of configuration data:

1. **Request → Lambda**:
   - Path parameters: `event.pathParameters`
   - Query parameters: `event.queryStringParameters`
   - Request body: `event.body`
   - Headers: `event.headers`
2. **Lambda → Database**:
   - Connection details (often from Secrets Manager)
   - SQL queries or ORM operations
   - Database/table names
3. **Database → Response**:
   - Field selection and filtering
   - Response structure and formatting
   - Status codes and error responses

**Output**: Data flow diagram in markdown:
```markdown
## Data Flow: PATCH /v1/gateway/{gatewayId}

Request → Lambda Handler → Validation → Database → Side Effects → Response

1. **Request**: `{ "RMS_CYCLE": 300, "RAW_ENABLED": true }`
2. **Authentication**: Extract user from JWT token
3. **Validation**: `mapConfigSettings()` validates fields
4. **Database Update**:
   - UPDATE gateway SET rms_interval=300, is_fft_enabled=true WHERE serial=?
5. **Side Effects**:
   - CloudWatch log entry created
   - Slack message sent to team
6. **Response**: `{ "statusCode": 200, "body": "{\"message\": \"Config updated\"}" }`
```

### 5. Generate FastAPI Migration Documentation

Produce the final documentation artifacts:

#### Endpoint Summary (Markdown Table)

```markdown
| Endpoint | Method | Lambda Function | Path Params | Auth Required | Description |
|----------|--------|-----------------|-------------|---------------|-------------|
| /v1/gateway/{gatewayId} | GET | GatewayConfigGet | gatewayId | Yes | Retrieve gateway configuration |
| /v1/gateways | PATCH | GatewayConfigPatch | - | Yes | Bulk update gateway configs |
| /v1/gateway/{gatewayId} | PATCH | GatewayConfigPatch | gatewayId | Yes | Update single gateway config |
| /v1/gateway/{gatewayId}/{setting} | DELETE | GatewayConfigDelete | gatewayId, setting | Yes | Delete specific config setting |
```

#### Configuration Fields (YAML)

Export all documented fields following the template format:

```yaml
configuration_fields:
  RMS_CYCLE:
    api_name: "RMS_CYCLE"
    db_column: "rms_interval"
    type: "integer"
    source: "database"
    # ... (complete template)

  RAW_ENABLED:
    api_name: "RAW_ENABLED"
    db_column: "is_fft_enabled"
    type: "boolean"
    source: "database"
    # ... (complete template)
```

#### Business Logic Summary (Markdown)

```markdown
## Key Business Rules

### Validation Rules
- Gateway version must be >= 2.0.0 for advanced features
- RMS_CYCLE must be between 1 and 3600 seconds
- Cannot disable alarms if active alerts exist

### Side Effects
- Config changes trigger CloudWatch logging
- Slack notifications sent for all PATCH operations
- Step Function initiated to verify gateway responds after upgrade

### Field Dependencies
- `RMS_CYCLE` mirrors to `hfdvue_rms_interval`
- `RAW_ENABLED` requires `RAW_CYCLE` to be set
- Firmware update fields depend on corresponding `*_updates_enabled` flags
```

## Resources

### references/config-documentation-template.md

Complete YAML template for documenting configuration fields. Use this template to structure all extracted fields consistently. The template includes:
- Field metadata (names, types, sources)
- Validation rules
- Business logic and side effects
- Endpoint-specific behavior
- Common patterns to recognize in Lambda code

Load this reference when beginning field documentation to ensure completeness.

## Common Patterns

### Pattern: Database Field Mapping

Lambda functions often map database columns to different API names:

```javascript
// SQL query with AS aliases
rms_interval as RMS_CYCLE,
is_fft_enabled as RAW_ENABLED,
UPPER(cloud_logging_level) as cloud_logging_level
```

**Action**: Document both names in field template:
- `db_column: "rms_interval"`
- `api_name: "RMS_CYCLE"`

### Pattern: Environment Variables for Config

Lambda functions read database credentials and settings from environment:

```javascript
host: process.env.DB_HOST || prodSecrets.replica_host,
stepFuncArn: process.env.GW_CHECK_STEPFUNC_ARN
```

**Action**: Note environment dependencies in documentation

### Pattern: Secrets Manager Integration

Credentials retrieved at Lambda initialization:

```javascript
const sm = new SecretsManagerClient()
const response = await sm.send(new GetSecretValueCommand({
    SecretId: 'waiteswireless-rds1/gateway_config'
}))
const prodSecrets = JSON.parse(response.SecretString)
```

**Action**: Document secret dependencies for FastAPI migration

### Pattern: Side Effect Functions

Watch for functions called after database operations:

```javascript
await cloudWatchLogEvent(logMsg)
await send_slack_msg(gwMacs, configData, user)
await stepfunctions.send(new StartExecutionCommand({...}))
```

**Action**: Document all side effects in logic section

## Analysis Checklist

Before completing documentation, verify:

- [ ] Endpoint path, method, and parameters identified
- [ ] Authentication/authorization requirements documented
- [ ] All configuration fields extracted and templated
- [ ] Field name mappings (API ↔ database) captured
- [ ] Data types and validation rules documented
- [ ] Business logic and conditional rules explained
- [ ] Side effects and integrations noted
- [ ] Field dependencies and relationships mapped
- [ ] Error responses and handling documented
- [ ] Constants, enums, and lookup tables extracted
- [ ] Data flow from request to response traced
- [ ] Migration-specific concerns noted (secrets, env vars, external services)

## Examples

### Example 1: Simple GET Endpoint

**User request**: "Document the GatewayConfigGet Lambda for FastAPI migration"

**Skill workflow**:
1. Identify: GET /v1/gateway/{gatewayId}, reads from database
2. Extract: 50+ configuration fields from SQL SELECT with AS aliases
3. Document: Each field with db_column ↔ api_name mapping
4. Map: Database query → field transformations → JSON response
5. Generate: Markdown table + YAML field definitions

### Example 2: PATCH with Validation

**User request**: "Analyze the config update logic in GatewayConfigPatch"

**Skill workflow**:
1. Identify: PATCH /v1/gateways, authenticated endpoint
2. Extract: Request body fields, validation functions, database UPDATE
3. Document: Validation rules from mapConfigSettings() and checkMinGatewayVer()
4. Capture: Side effects (CloudWatch, Slack, Step Functions)
5. Generate: Business logic summary + field templates

### Example 3: Complex Business Logic

**User request**: "Extract the configuration fields and explain the alert type mappings"

**Skill workflow**:
1. Locate: Constants at top of file (reading_type_to_alert_type, condition_to_type)
2. Extract: Lookup table logic and enum definitions
3. Document: Enum values and mapping logic in business rules
4. Generate: YAML documentation with enum constraints and logic descriptions
