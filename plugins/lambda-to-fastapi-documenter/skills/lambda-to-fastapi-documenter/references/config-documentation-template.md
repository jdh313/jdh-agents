# Configuration Field Documentation Template

Use this template when documenting configuration fields extracted from Lambda functions.

## Field Documentation Format

```yaml
field_name:
  # Basic Information
  api_name: "field_name"              # Name used in API requests/responses
  db_column: "db_column_name"         # Database column name (if different)
  type: "string|integer|boolean|float|array|object"

  # Source & Access
  source: "request_body|path_param|query_param|env_var|database"
  required: true|false
  read_only: false                    # Set true if only returned, never set
  write_only: false                   # Set true if only accepted, never returned

  # Validation Rules
  validation:
    min: null                         # Minimum value (numbers) or length (strings/arrays)
    max: null                         # Maximum value (numbers) or length (strings/arrays)
    pattern: null                     # Regex pattern for strings
    enum: []                          # List of allowed values
    custom: ""                        # Custom validation logic description

  # Default Values & Transformations
  default: null                       # Default value if not provided
  transformation: ""                  # Any transformation logic (e.g., "multiply by 1000", "uppercase")

  # Business Logic
  logic:
    description: ""                   # What this field controls/represents
    side_effects: []                  # Side effects when this field is set (e.g., triggers, notifications)
    depends_on: []                    # Other fields this depends on
    affects: []                       # Other fields affected by this field

  # Context
  endpoint_operations:
    - operation: "GET|POST|PATCH|DELETE"
      path: "/api/path"
      behavior: ""                    # How this field behaves in this operation

  notes: ""                           # Additional implementation notes
```

## Example: Gateway Configuration Field

```yaml
RMS_CYCLE:
  api_name: "RMS_CYCLE"
  db_column: "rms_interval"
  type: "integer"

  source: "database"
  required: false
  read_only: false
  write_only: false

  validation:
    min: 1
    max: 3600
    pattern: null
    enum: []
    custom: "Must be positive integer representing seconds"

  default: null
  transformation: "Database stores interval, API returns as RMS_CYCLE"

  logic:
    description: "Controls the RMS (Root Mean Square) measurement cycle interval in seconds"
    side_effects:
      - "Affects sensor data collection frequency"
      - "May trigger gateway config refresh"
    depends_on:
      - "gateway version must support RMS measurements"
    affects:
      - "hfdvue_rms_interval (mirrors this value)"

  endpoint_operations:
    - operation: "GET"
      path: "/v1/gateway/{gatewayId}"
      behavior: "Retrieved from gateway table via SQL query"
    - operation: "PATCH"
      path: "/v1/gateway/{gatewayId}"
      behavior: "Updated with validation, triggers CloudWatch log and Slack notification"

  notes: "This field is used by HFD Vue sensors for vibration monitoring"
```

## Analysis Checklist

When documenting fields, ensure you capture:

- [ ] Field name mappings (API ↔ database)
- [ ] Data type and structure
- [ ] Source of the data (where it comes from)
- [ ] Validation rules (explicit and implicit)
- [ ] Default values or transformations
- [ ] Business logic and side effects
- [ ] Relationships with other fields
- [ ] Endpoint-specific behavior
- [ ] Version constraints or feature flags
- [ ] Security/authorization requirements

## Common Patterns to Recognize

### 1. Field Name Transformations
```javascript
// Lambda often maps database columns to different API names:
db_column: "rms_interval"  →  api_name: "RMS_CYCLE"
db_column: "is_rms_enabled" →  api_name: "RMS_ENABLED"
```

### 2. Type Conversions
```javascript
// Database stores in one unit, API expects another:
poll_interval * 1000 as total_window_size  // milliseconds conversion
UPPER(cloud_logging_level)                 // case normalization
```

### 3. Conditional Logic
```javascript
// Fields that depend on versions or feature flags:
if (compareVersions(version, '2.0.0') >= 0) {
  // field is supported
}
```

### 4. Constants & Enums
```javascript
// Look for constant definitions at top of file:
const STATUS_ACTIVE = 0
const STATUS_INACTIVE = 1
const TACH_TRIGGER_TYPE = 5
```

### 5. Side Effects
```javascript
// Watch for operations triggered by field updates:
- CloudWatch logging: cloudWatchLogEvent()
- Slack notifications: send_slack_msg()
- Step Functions: stepfunctions.send(StartExecutionCommand)
- IoT messages: IoTDataPlane.publish()
```

### 6. Validation Functions
```javascript
// Extract validation logic:
- checkMinGatewayVer()
- mapConfigSettings()
- Custom regex patterns
- Boundary checks
```
