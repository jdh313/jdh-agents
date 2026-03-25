# SurrealDB: Key-Value Model

## When to Use

Use the key-value model when:
- You always access records by their exact ID — no filtering or sorting needed
- The data is ephemeral or configuration-like (sessions, feature flags, app settings)
- Query simplicity matters more than schema enforcement or relational structure
- You want to avoid the overhead of defining a full schema for simple lookups
- Examples: application configuration, feature flags, rate limit counters, session tokens,
  user preferences (a single JSON blob per user)

The key-value model in SurrealDB is not a separate mode — it is the natural behavior
of direct record ID access, which bypasses the query engine entirely.

---

## Direct Record ID Access

The fastest way to fetch a record in SurrealDB is by its full ID:

```surql
-- No WHERE clause, no index scan — direct lookup
SELECT * FROM config:app_settings;

-- Equivalent Python SDK call (even faster — bypasses query parser)
settings = await db.select("config:app_settings")
```

From Python, `db.select("table:id")` resolves to a direct record fetch. No query
planning, no index selection — O(1) lookup by ID.

---

## Schema Design

Key-value records are typically SCHEMALESS with minimal or no field declarations:

```surql
DEFINE TABLE config SCHEMALESS;

-- Store any shape — no schema required
CREATE config:app_settings SET
    feature_flags = {
        new_dashboard = true,
        beta_search = false,
        vector_search = true
    },
    rate_limits = {
        api_calls_per_minute = 60,
        embedding_calls_per_hour = 1000
    },
    version = "2.1.0";

-- Read back
SELECT * FROM config:app_settings;
-- or
SELECT feature_flags.new_dashboard FROM config:app_settings;

-- Update a specific field
UPDATE config:app_settings SET feature_flags.beta_search = true;
```

---

## Naming Conventions

Choose record IDs that are semantic and stable:

```surql
-- Application-wide configuration
config:app_settings
config:rate_limits
config:feature_flags

-- Per-user preferences (user ID embedded in record ID)
user_prefs:alice
user_prefs:bob

-- Session tokens
session:abc123xyz

-- Rate limit counters (composite ID)
rate_limit:["api", "alice", "2024-03-24T14:00"]
```

Composite IDs using arrays are supported for multi-key lookups:
`SELECT * FROM rate_limit:[​"api", "alice", "2024-03-24T14:00"]`

---

## Example: App Configuration

```surql
DEFINE TABLE config SCHEMALESS;
DEFINE TABLE session SCHEMALESS;

-- Store application-level config
CREATE config:resift SET
    embedding_model = "all-MiniLM-L6-v2",
    embedding_dimension = 384,
    max_results_per_query = 20,
    similarity_threshold = 0.7;

-- Store a session token
CREATE session:tok_abc123 SET
    user = user:alice,
    created_at = time::now(),
    expires_at = time::now() + 24h,
    scopes = ["read", "write"];

-- Check if session is still valid
SELECT user, scopes FROM session:tok_abc123
WHERE expires_at > time::now();

-- Update a config value
UPDATE config:resift SET max_results_per_query = 30;

-- Delete a session on logout
DELETE session:tok_abc123;
```

---

## Counters and Accumulators

SurrealDB supports atomic increment/decrement:

```surql
DEFINE TABLE counter SCHEMALESS;

-- Initialize
CREATE counter:api_calls SET value = 0;

-- Atomic increment
UPDATE counter:api_calls SET value += 1;

-- Read current count
SELECT value FROM counter:api_calls;
```

Note: SurrealDB does not have native TTL/expiry on records. Implement expiry via a
scheduled cleanup query or background job.

---

## Trade-offs

| Aspect | Upside | Downside |
|--------|--------|---------|
| Direct ID access | O(1) lookup, no query overhead | Must know exact ID at call time |
| SCHEMALESS | No upfront schema design | No type safety or validation |
| Simple update | `UPDATE table:id SET field = value` | No transactions on single-record operations by default |
| Fits any shape | Works for config, sessions, caches | No query/filter/sort without a full scan |

---

## When to Use a Document Table Instead

Consider a document table (SCHEMALESS + queries) when:
- You sometimes need to list all records of this type
- You filter by field values, not just by ID
- Records need to be queried by time range (use time-series conventions)
- You have more than a few hundred records and need pagination

The key-value pattern only pays off when **direct ID lookup is the exclusive access pattern**.
If you ever write `SELECT * FROM config WHERE ...`, use a document table with an index instead.

---

## When NOT to Use

- When you filter, sort, or paginate records — use a document table with indices
- When records are related to other entities and you traverse those relationships —
  use graph model instead
- When field types and required fields matter — use relational (SCHEMAFULL)
- When data volume is large (>100k records) and you need range scans — add indices
  and use document or time-series model
- When you need TTL/expiry natively — SurrealDB lacks built-in expiry; use an
  external cache (Redis) for that use case
