# Schema Patterns & Reference

Quick lookup for field types, assertions, and index patterns when designing SurrealDB schemas.

## SCHEMAFULL vs SCHEMALESS Decision Matrix

| Factor | SCHEMAFULL | SCHEMALESS |
|--------|-----------|------------|
| Data integrity | Strict — undefined fields silently dropped | Flexible — any field accepted |
| Development speed | Slower — must define all fields upfront | Faster — evolve structure on the fly |
| Query safety | Fields are typed and validated at write time | No type guarantees; validation in app code |
| Storage overhead | Minimal (schema enforced at DB level) | Higher (every record carries full field set) |
| Best for | Core business entities, user data, audited systems | Config, logs, external API responses, evolving domains |
| Risky to add fields later? | No — add DEFINE FIELD anytime | No — fields appear in existing records automatically |
| Risky to remove fields? | Yes — existing data is hidden but retained | Yes — data lingers in records, can be queried |
| Migration to SCHEMAFULL | Hard — must define ALL fields or data drops | Define all fields before converting |

**Rule of thumb:**
- **SCHEMAFULL:** "I know what this data looks like and it won't change often."
- **SCHEMALESS:** "This data structure varies or evolves frequently."

---

## Field Type Reference

### Scalar Types

```surql
string              -- Text; no length limit unless asserted
int                 -- 64-bit signed integer
float               -- IEEE 754 double precision
bool                -- true or false
datetime            -- ISO 8601 timestamp; VALUE time::now() for defaults
duration            -- Time span (e.g., 1h, 30m, 2d)
decimal             -- Fixed-point decimal for currency
```

### Complex Types

```surql
array<T>            -- Ordered list; T can be any type (e.g., array<string>, array<record<user>>)
set<T>              -- Unique unordered list; automatically deduplicates
object              -- Nested document; fields are untyped
record<table>       -- Link to another record (foreign key); table can be single table or multiple like record<user|company>
geometry            -- Geospatial (point, line, polygon, multipoint, etc.)
```

### Nullability

```surql
TYPE string         -- Required (null is invalid)
TYPE option<string> -- Optional (null is valid)

-- In assertions, check with $value != NONE for required fields
DEFINE FIELD name ON user TYPE string ASSERT $value != NONE;

-- option<T> automatically allows null, no assertion needed
DEFINE FIELD bio ON user TYPE option<string>;
```

---

## Assertion Patterns

Assertions validate data at write time. SurrealDB provides math, string, array, and type-checking functions.

### String Assertions

```surql
-- Non-empty
DEFINE FIELD name ON user TYPE string ASSERT $value != NONE AND string::len($value) >= 1;

-- Email validation
DEFINE FIELD email ON user TYPE string ASSERT string::is::email($value);

-- Length constraints
DEFINE FIELD password ON user TYPE string ASSERT string::len($value) >= 12;

-- Allowed values (enum)
DEFINE FIELD status ON order TYPE string ASSERT $value IN ["pending", "processing", "completed", "cancelled"];

-- Contains substring
DEFINE FIELD code ON coupon TYPE string ASSERT string::contains($value, "-");
```

### Numeric Assertions

```surql
-- Range validation
DEFINE FIELD age ON person TYPE int ASSERT $value >= 0 AND $value <= 150;
DEFINE FIELD rating ON product TYPE float ASSERT $value >= 0.0 AND $value <= 5.0;

-- Positive numbers
DEFINE FIELD quantity ON inventory TYPE int ASSERT $value > 0;

-- Percentage (0-100)
DEFINE FIELD completion ON task TYPE float ASSERT $value >= 0 AND $value <= 100;
```

### Array Assertions

```surql
-- Array length
DEFINE FIELD tags ON post TYPE array<string> ASSERT array::len($value) <= 10;

-- All elements match condition
DEFINE FIELD skills ON profile TYPE array<string>
    ASSERT array::all($value, |$v| $v != NONE);

-- Array contains specific element
DEFINE FIELD permissions ON role TYPE array<string>
    ASSERT array::contains($value, "admin") IF $this.is_superuser;
```

### Record Link Assertions

```surql
-- Link must exist and is required
DEFINE FIELD author ON post TYPE record<user> ASSERT $value != NONE;

-- Link to one of multiple tables
DEFINE FIELD owner ON asset TYPE record<user|company>;
```

### Datetime Assertions

```surql
-- After a specific date
DEFINE FIELD expiry ON voucher TYPE datetime
    ASSERT $value > time::now();

-- Within valid range
DEFINE FIELD event_date ON booking TYPE datetime
    ASSERT $value > time::now() AND $value < time::now() + 1y;
```

---

## Index Types

### Standard Index

Speeds up WHERE queries on a field.

```surql
DEFINE INDEX idx_user_email ON user FIELDS email;

-- Query that benefits:
SELECT * FROM user WHERE email = 'alice@example.com';
```

### Unique Index

Enforces uniqueness and speeds up lookups.

```surql
DEFINE INDEX idx_user_email ON user FIELDS email UNIQUE;

-- Attempting duplicate throws error:
UPDATE user SET email = 'taken@example.com' -- fails if email already exists
```

### Composite Index

Speeds up compound WHERE clauses (order matters).

```surql
DEFINE INDEX idx_post_author_published ON post FIELDS author, published;

-- Queries that benefit:
SELECT * FROM post WHERE author = user:alice AND published = true;
SELECT * FROM post WHERE author = user:alice AND published = false;

-- This query does NOT benefit (wrong order):
SELECT * FROM post WHERE published = true AND author = user:alice;
```

### Full-Text Search Index

Enables keyword search on text fields.

```surql
DEFINE INDEX idx_post_content ON post FIELDS content
    SEARCH ANALYZER ascii BM25;

-- Query that benefits:
SELECT * FROM post WHERE content @@ 'python surrealdb';
```

### Vector Index (HNSW)

Enables semantic similarity search on embeddings. HNSW = Hierarchical Navigable Small World.

```surql
-- DIMENSION must match your embedding model's output size
-- DIST can be COSINE, EUCLIDEAN, or MANHATTAN
-- TYPE can be F32 (32-bit float) or F64 (64-bit float)
DEFINE INDEX idx_post_embedding ON post FIELDS embedding
    HNSW DIMENSION 384 DIST COSINE TYPE F32;

-- Query that benefits:
SELECT * FROM post WHERE embedding <| {vector}, 10 |>;  -- top 10 similar posts
```

**Vector Index Config Quick Reference:**

| Model | DIMENSION | DIST | Notes |
|-------|-----------|------|-------|
| OpenAI text-embedding-3-small | 1536 | COSINE | Default for most text |
| OpenAI text-embedding-3-large | 3072 | COSINE | High-res, more expensive |
| Hugging Face all-MiniLM-L6-v2 | 384 | COSINE | Lightweight, good baseline |
| Cohere embed-english-v3.0 | 1024 | COSINE | Task-specific tuning |

---

## Computed Fields

Computed fields generate values on read. Useful for aggregations, concatenations, and back-references.

### Concatenation

```surql
DEFINE FIELD full_name ON user
    VALUE string::concat($this.first_name, ' ', $this.last_name);

-- Query:
SELECT full_name FROM user WHERE id = user:alice;
-- Result: "Alice Smith"
```

### Count Aggregation

```surql
DEFINE FIELD post_count ON user
    VALUE (SELECT COUNT() FROM post WHERE author = $this);

-- Query:
SELECT post_count FROM user WHERE id = user:alice;
-- Result: 42
```

### Back-Reference (Reverse Link)

```surql
DEFINE FIELD posts ON user
    VALUE (SELECT id, title FROM post WHERE author = $this);

-- Query:
SELECT posts FROM user WHERE id = user:alice;
-- Result: [{ id: "post:1", title: "..." }, ...]
```

### Conditional Value

```surql
DEFINE FIELD is_overdue ON task
    VALUE ($this.due_date < time::now());

-- Query:
SELECT is_overdue FROM task WHERE id = task:urgent;
-- Result: true
```

---

## Common Patterns

### Email Field (Required, Unique)

```surql
DEFINE FIELD email ON user TYPE string
    ASSERT string::is::email($value);
DEFINE INDEX idx_user_email ON user FIELDS email UNIQUE;
```

### Timestamp Fields (Auto-set)

```surql
DEFINE FIELD created_at ON post TYPE datetime VALUE time::now();
DEFINE FIELD updated_at ON post TYPE datetime VALUE time::now();
```

### Status Field (Enum with Assertion)

```surql
DEFINE FIELD status ON order TYPE string
    ASSERT $value IN ["pending", "processing", "shipped", "delivered", "cancelled"];
DEFINE INDEX idx_order_status ON order FIELDS status;  -- for filtering
```

### Record Link (Required)

```surql
DEFINE FIELD author ON post TYPE record<user>
    ASSERT $value != NONE;
DEFINE INDEX idx_post_author ON post FIELDS author;
```

### Embedding Field (Optional, with Vector Index)

```surql
DEFINE FIELD embedding ON post TYPE option<array<float>>;
DEFINE INDEX idx_post_embedding ON post FIELDS embedding
    HNSW DIMENSION 384 DIST COSINE TYPE F32;
```

### Array of Primitives (Bounded)

```surql
DEFINE FIELD tags ON post TYPE array<string>
    ASSERT array::len($value) <= 10 AND array::all($value, |$v| string::len($v) >= 1);
```

### Array of Records (Many-to-Many Alternative)

```surql
-- Simple: if no edge metadata needed
DEFINE FIELD skill_ids ON profile TYPE array<record<skill>>;

-- Better: if you need edge data (e.g., proficiency level)
-- Use a RELATE table instead:
DEFINE TABLE has_skill SCHEMAFULL;
DEFINE FIELD in ON has_skill TYPE record<profile>;
DEFINE FIELD out ON has_skill TYPE record<skill>;
DEFINE FIELD proficiency ON has_skill TYPE string ASSERT $value IN ["beginner", "intermediate", "advanced"];
```

---

## Migration Patterns

See `references/migrations.md` for versioned migration scripts.

### Safe Evolution

1. **Add field** — Always safe. Existing records get null/default.
2. **Add index** — Safe. Built asynchronously.
3. **Add computed field** — Safe. No data changes.
4. **Remove SCHEMALESS field** — Safe; data stays in records.
5. **Rename field** — Not directly supported. Copy → migrate → drop old.
6. **Remove SCHEMAFULL field** — Field hidden; data retained in records.
7. **Change field type** — Risky. Validate/backfill first.

### Risky Operations

- **Convert SCHEMALESS to SCHEMAFULL without defining all fields** → Data silently dropped
- **Unique constraint on existing field with duplicates** → Fails
- **Strict assertion on existing data** → Fails if data doesn't satisfy assertion
- **Required field (not option<T>) with no default** → New records require value

---

## Assertion Function Reference

Quick lookup for functions used in assertions.

```surql
-- String functions
string::is::email($value)          -- True if valid email
string::is::url($value)            -- True if valid URL
string::is::numeric($value)        -- True if numeric string
string::contains($value, "text")   -- True if contains substring
string::len($value)                -- Length of string
string::lowercase($value)          -- Lowercase
string::uppercase($value)          -- Uppercase

-- Array functions
array::len($value)                 -- Length
array::contains($value, item)      -- True if contains item
array::all($value, |$v| cond)      -- True if all match condition
array::any($value, |$v| cond)      -- True if any match condition

-- Math functions
math::abs($value)                  -- Absolute value
math::min(a, b)                    -- Minimum
math::max(a, b)                    -- Maximum

-- Type checking
type::is::string($value)           -- True if string
type::is::number($value)           -- True if number
type::is::array($value)            -- True if array
type::is::object($value)           -- True if object

-- Time functions
time::now()                        -- Current timestamp
time::format($value, "%Y-%m-%d")   -- Format datetime
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `DEFINE FIELD status ON order TYPE string ASSERT status IN [...]` | Use `$value` not field name: `ASSERT $value IN [...]` |
| `DEFINE INDEX idx ON table FIELDS field1, field2` then query by field2 only | Composite index is field-order dependent; create separate index for field2 |
| `DEFINE FIELD link ON post TYPE record<user>` but user table doesn't exist | Ensure table exists before creating link; or use record<user\|company> for multiple tables |
| `DEFINE FIELD embedding ON post TYPE array<float>` without HNSW index | Vector queries are slow without index; add `DEFINE INDEX idx_embedding ON post FIELDS embedding HNSW DIMENSION 384 DIST COSINE TYPE F32` |
| `DEFINE FIELD created_at ON post TYPE datetime` (no VALUE) | Existing records have null; use `VALUE time::now()` for new records to auto-set |
| Converting SCHEMALESS to SCHEMAFULL with incomplete DEFINE FIELD list | Undefined fields are silently dropped; define ALL fields first |
