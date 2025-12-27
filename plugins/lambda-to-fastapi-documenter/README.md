# Lambda to FastAPI Documenter

## Overview

Extract and document configuration fields, business logic, and REST API specifications from AWS Lambda CRUD handlers for FastAPI migration. Analyze Lambda functions to produce language-agnostic configuration documentation in structured formats (Markdown tables and YAML).

## What It Does

This plugin analyzes AWS Lambda functions (Python or Node.js) and generates comprehensive documentation for FastAPI migration, including:

- **Configuration Field Extraction**: Maps API names to database columns with type information
- **Business Logic Documentation**: Captures validation rules, side effects, and field dependencies
- **API Endpoint Specifications**: Documents HTTP operations, authentication, and path parameters
- **Data Flow Analysis**: Traces configuration data from request through Lambda to database and response
- **FastAPI Migration Artifacts**: Produces endpoint summaries, field definitions, and business rules documentation

## When to Use

Invoke this plugin when:
- Analyzing Lambda function code for FastAPI migration
- Documenting configuration fields being read or written
- Extracting CRUD operation logic from Lambda handlers
- Mapping Lambda handlers to REST API specifications
- Understanding data flows between API requests, Lambda logic, and database operations

## Key Triggers

The plugin activates on these phrases:
- "Lambda migration"
- "Document this Lambda"
- "Extract config from Lambda"
- "Analyze this Lambda for FastAPI migration"
- "Help me understand the configuration logic in this Lambda"

## Usage Instructions

### Basic Workflow

1. **Identify Lambda Context**: Understand the Lambda function's role (GET/POST/PATCH/DELETE operation)
2. **Extract Configuration Fields**: Analyze how configuration is read and written
3. **Document Business Logic**: Capture validation rules, side effects, and dependencies
4. **Map Data Flow**: Trace the path of configuration data through the system
5. **Generate FastAPI Documentation**: Produce endpoint summaries, field definitions, and business rules

### Example: Document a GET Endpoint

```
User: "Document the GatewayConfigGet Lambda for FastAPI migration"

Plugin workflow:
1. Identifies: GET /v1/gateway/{gatewayId} endpoint
2. Extracts: 50+ configuration fields from SQL SELECT with AS aliases
3. Documents: Each field with db_column ↔ api_name mapping
4. Maps: Database query → field transformations → JSON response
5. Generates: Markdown table + YAML field definitions
```

### Example: Analyze PATCH with Validation

```
User: "Analyze the config update logic in GatewayConfigPatch"

Plugin workflow:
1. Identifies: PATCH /v1/gateways authenticated endpoint
2. Extracts: Request body fields, validation functions, database UPDATE
3. Documents: Validation rules from validation functions
4. Captures: Side effects (CloudWatch, Slack, Step Functions)
5. Generates: Business logic summary + field templates
```

## Output Formats

The plugin produces documentation in multiple formats:

### Endpoint Summary (Markdown Table)
```markdown
| Endpoint | Method | Lambda Function | Path Params | Auth Required | Description |
|----------|--------|-----------------|-------------|---------------|-------------|
| /v1/gateway/{gatewayId} | GET | GatewayConfigGet | gatewayId | Yes | Retrieve gateway configuration |
```

### Configuration Fields (YAML)
```yaml
configuration_fields:
  RMS_CYCLE:
    api_name: "RMS_CYCLE"
    db_column: "rms_interval"
    type: "integer"
    source: "database"
```

### Business Logic Summary (Markdown)
```markdown
## Key Business Rules

### Validation Rules
- Gateway version must be >= 2.0.0 for advanced features
- RMS_CYCLE must be between 1 and 3600 seconds

### Side Effects
- Config changes trigger CloudWatch logging
- Slack notifications sent for all PATCH operations
```

## Common Patterns Recognized

- **Database Field Mapping**: Maps SQL aliases (AS) to API names
- **Environment Variables**: Identifies configuration from process.env
- **Secrets Manager Integration**: Documents credential dependencies
- **Side Effect Functions**: Captures logging, notifications, and triggers

## Resources Included

- **SKILL.md**: Complete workflow documentation and analysis checklist
- **references/config-documentation-template.md**: YAML template for field documentation
- **scripts/**: Helper scripts for analyzing Lambda code patterns
- **assets/**: Reference materials and examples

## Requirements

- AWS Lambda function code (Python or Node.js)
- Understanding of Lambda handler structure
- Knowledge of CRUD operations (GET, POST, PATCH, DELETE)

## Analysis Checklist

Before completing documentation, verify:

- Endpoint path, method, and parameters identified
- Authentication/authorization requirements documented
- All configuration fields extracted and templated
- Field name mappings (API ↔ database) captured
- Data types and validation rules documented
- Business logic and conditional rules explained
- Side effects and integrations noted
- Field dependencies and relationships mapped
- Error responses and handling documented
- Data flow from request to response traced
