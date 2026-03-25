# SurrealDB Overview

Teaching document for projects using SurrealDB with the official Python SDK.

## Mental Model

**Hierarchy:** Namespace → Database → Table → Record

- **Namespace** — logical database cluster (allows multi-tenancy)
- **Database** — schema isolation within a namespace
- **Table** — collection of records (can be SCHEMAFULL or SCHEMALESS)
- **Record** — JSON-like document with typed fields and a unique ID

**Record IDs:**
- Format: `table:id` (e.g., `person:john`, `order:12345`)
- Auto-generated as UUID or custom string
- Primary key replacement in SurrealDB
- Can be referenced directly in links and RELATE statements

**Records are documents:**
- Flexible, JSON-like structure with nested objects
- Can contain array fields, record links, and computed values
- Validation via SCHEMAFULL tables or runtime assertions

## Multi-Model Overview

### Document Model

Schemaless, flexible records with nested objects. Best for data with variable structure or frequent schema evolution.

**Characteristics:**
- SCHEMALESS or flexible SCHEMAFULL
- Nested objects: `{ address: { street: "Main St", city: "Springfield" } }`
- No required fields
- Fast iteration on schema

**When to use:** Early-stage projects, content management, user preferences, configuration storage.

### Graph Model

Records linked to other records via direct references. Enables traversal queries without JOINs.

**Characteristics:**
- Record links: `{ manager: person:alice }`
- Traversal syntax: `->` (outgoing) and `<-` (incoming)
- RELATE statement for explicit edges with properties: `RELATE person:alice->manages->person:bob SET since = 2024`
- Natural for hierarchies, org charts, social networks

**When to use:** Organization structures, social graphs, recommendation engines, hierarchy navigation.

### Relational Model

Strongly typed tables with schemas, assertions, and indices. Most similar to SQL.

**Characteristics:**
- SCHEMAFULL with typed fields
- Assertions for data validation
- Unique and composite indices
- Foreign keys via record links
- No JOINs needed (use graph traversal instead)

**When to use:** Business applications, structured data, strict compliance requirements, complex validation rules.

### Vector Model

Embeddings with HNSW (Hierarchical Navigable Small World) similarity search. Fast approximate nearest neighbors.

**Characteristics:**
- `VECTOR(dimension)` field type (e.g., VECTOR(384) for 384-dimensional embeddings)
- Distance metrics: cosine, euclidean, manhattan
- Index type: HNSW with configurable M and ef parameters
- Returns similarity score alongside results

**When to use:** RAG systems, semantic search, recommendation engines, similarity clustering.

### Time-Series Model

Temporal data optimized for time-based queries and aggregations.

**Characteristics:**
- Timestamp fields with indices
- Time-bucketing queries (group by hour, day, week)
- Range queries (between two timestamps)
- Compatible with vector model for temporal embeddings

**When to use:** Metrics, logs, financial time-series, event tracking, monitoring data.

### Key-Value Model

Simple record ID lookups with minimal structure. Fast retrieval by ID.

**Characteristics:**
- SCHEMALESS tables with minimal validation
- Fast direct ID lookups: `SELECT * FROM cache:session_12345`
- Optional value expiration
- Good for caches and sessions

**When to use:** Session storage, caching, rate limiting, temporary data.

### Geospatial Model

Geometry types and distance-based queries.

**Characteristics:**
- Geometry types: POINT, LINESTRING, POLYGON, etc.
- Distance functions: `distance::haversine()` for lat/lon, `distance::euclidean()` for points
- Containment queries: `INSIDE()` checks if point is within polygon
- Optional spatial indices for faster queries

**When to use:** Maps, location services, proximity searches, geographic data analysis.

### Full-Text Search Model

Text indices with analyzers and tokenizers for natural language search.

**Characteristics:**
- ANALYZER support: BYTE, SIMPLE, SNOWBALL
- TOKENIZE options: none, blank, class, camelcase
- Index type: FULL TEXT with scoring
- MATCHES operator for keyword search

**When to use:** Document search, content discovery, article indexing, user-facing search.

## Connection Modes

| Mode | String | Use Case | Performance |
|------|--------|----------|-------------|
| Embedded in-memory | `mem://` | Testing, prototyping | Very fast, no persistence |
| Embedded file | `file://./mydb.db` | Single-machine apps, SQLite-like | Fast, local only |
| Remote WebSocket | `ws://localhost:8000` | Local development server | Moderate |
| Remote HTTP | `http://localhost:8000` | Production server | Slower than WebSocket |

## Python SDK Basics

Install with `pip install surrealdb`:

```python
from surrealdb import AsyncSurreal

# Embedded file-based database
async with AsyncSurreal("file://./mydb.db") as db:
    await db.use("namespace", "database")

    # Create a record
    person = await db.create("person", {
        "name": "John",
        "age": 30,
        "email": "john@example.com"
    })

    # Select all records from table
    people = await db.select("person")

    # Query with parameters (parameterized queries)
    result = await db.query(
        "SELECT * FROM person WHERE age > $min_age",
        {"min_age": 25}
    )

    # Update a record
    updated = await db.update("person:john", {
        "age": 31
    })

    # Delete a record
    await db.delete("person:john")

    # Delete entire table
    await db.delete("person")
```

**Parameterized queries:**
Always use `$variable` syntax to pass parameters. Protects against injection and enables query optimization.

```python
result = await db.query(
    "SELECT * FROM person WHERE name = $name AND age > $min_age",
    {"name": "John", "min_age": 25}
)
```

## Key Differences from SQL

| Aspect | SQL | SurrealDB |
|--------|-----|-----------|
| **Primary key** | Auto-increment integer | Record ID (table:id format) |
| **Foreign keys** | Foreign key constraints | Direct record links (no JOIN) |
| **JOINs** | Required for related data | Graph traversal with `->` and `<-` |
| **Schema** | Strict CREATE TABLE | DEFINE TABLE with SCHEMAFULL or SCHEMALESS |
| **Relationships** | JOINs in queries | Pre-computed links in records |
| **Flexibility** | Fixed schema | Mix SCHEMAFULL and SCHEMALESS |
| **Edges** | Not first-class | RELATE creates explicit edge records |
| **Parameterization** | `?` placeholders | `$variable` syntax |
| **Data models** | One relational model | Eight: document, graph, relational, vector, time-series, key-value, geospatial, full-text |

### Query Examples: SQL vs SurrealDB

**Find person and their manager:**

SQL:
```sql
SELECT p.name, m.name as manager
FROM persons p
LEFT JOIN persons m ON p.manager_id = m.id
WHERE p.name = 'John'
```

SurrealDB:
```sql
SELECT name, manager->name as manager FROM person WHERE name = 'John'
```

**Find all direct and indirect reports:**

SQL:
```sql
-- Requires recursive CTE
WITH RECURSIVE reports AS (...)
```

SurrealDB:
```sql
SELECT * FROM person WHERE <-manages.from = person:john
```

**Similarity search (vector):**

SQL:
```sql
-- Not natively supported; use extensions
```

SurrealDB:
```sql
SELECT *, vector::distance(embedding, $query_vector) as similarity
FROM documents
WHERE vector::distance(embedding, $query_vector) < 0.3
ORDER BY similarity ASC
LIMIT 10
```

## Record ID Naming Conventions

**Best practices:**

- Use UUIDs for distributed systems: `user` table generates `user:8e5ae8a3...`
- Use semantic IDs for human readability: `user:alice`, `session:xyz`, `order:2024-03-24-001`
- Composite IDs: `audit:person_alice_2024-03-24` for audit logs
- Timestamps: `event:2024-03-24T14:30:00Z` for time-series data
- Hyphens and underscores are safe; avoid special characters

## Connection Lifecycle

```python
async with AsyncSurreal("file://./mydb.db") as db:
    # Context manager auto-connects on __enter__
    # Use db here
    # Context manager auto-closes on __exit__
```

For manual control:

```python
db = AsyncSurreal("file://./mydb.db")
await db.connect()
await db.use("namespace", "database")

# ... use db ...

await db.close()
```

## Transactions (Optional)

SurrealDB supports transactions for atomic multi-statement operations:

```python
await db.query("""
    BEGIN;
    CREATE person:alice SET age = 30;
    CREATE person:bob SET age = 25;
    RELATE person:alice->knows->person:bob;
    COMMIT;
""")
```

## Debugging Tips

**Check SurrealDB server logs:**
```bash
surreal start --log info
```

**Inspect query execution:**
Use `EXPLAIN` to see the query plan (supported in SurrealDB 1.0+):

```sql
EXPLAIN SELECT * FROM person WHERE age > 25
```

**Verify indices are used:**
SurrealDB automatically uses indices when available. Check with:

```sql
INFO TABLE person
```

**Parameterization errors:**
If query fails with undefined variable errors, ensure all `$variables` are passed in the params dict.
