# SurrealDB: Relational Model

## When to Use

Use the relational model (SCHEMAFULL) when:
- The entity's field names and types are known and stable
- Data integrity matters — required fields must always be present
- You need validation rules (format checks, range constraints, enum values)
- Records are canonical or shared reference data (e.g., skills, companies, users)
- Multiple consumers depend on consistent field shapes
- Type errors in application code are appearing from missing or unexpected fields

The relational model is **not mutually exclusive with the graph model**. SCHEMAFULL
tables can have record link fields that enable graph traversal.

---

## SCHEMAFULL Tables

A SCHEMAFULL table rejects any field not explicitly defined:

```surql
DEFINE TABLE skill SCHEMAFULL;
DEFINE FIELD name     ON skill TYPE string ASSERT $value != NONE;
DEFINE FIELD category ON skill TYPE string;
DEFINE FIELD aliases  ON skill TYPE option<array<string>>;

-- This succeeds
CREATE skill:python SET name = "Python", category = "programming";

-- This fails: "tags" field is not defined
CREATE skill:python SET name = "Python", tags = ["scripting"];
-- Error: Found changed value for field 'tags', with value...
```

SCHEMAFULL enforces structure at insert/update time, not just at query time.

---

## Field Types

| Type | Example | Notes |
|------|---------|-------|
| `string` | `"Alice"` | UTF-8 text |
| `int` | `42` | 64-bit integer |
| `float` | `3.14` | 64-bit float |
| `bool` | `true` | Boolean |
| `datetime` | `d"2024-01-01T00:00:00Z"` | ISO 8601 timestamp |
| `duration` | `1y2h30m` | Time duration |
| `array<T>` | `["a", "b"]` | Typed array |
| `object` | `{ k: v }` | Nested object |
| `record<table>` | `company:acme` | Record link (graph traversal) |
| `option<T>` | `NONE` or value | Nullable field |
| `geometry` | GeoJSON point | Geospatial type |
| `any` | Any value | Escape hatch — avoid for stable fields |

---

## Assertions: Runtime Validation

Add `ASSERT` clauses to enforce constraints beyond type checking:

```surql
DEFINE TABLE user SCHEMAFULL;

-- Required non-empty string
DEFINE FIELD name ON user TYPE string
    ASSERT $value != NONE AND string::len($value) > 0;

-- Valid email format
DEFINE FIELD email ON user TYPE string
    ASSERT string::is_email($value);

-- Non-negative salary
DEFINE FIELD salary ON user TYPE option<float>
    ASSERT $value == NONE OR $value >= 0;

-- Enum-style constraint
DEFINE FIELD status ON user TYPE string
    ASSERT $value IN ["active", "inactive", "suspended"];

-- Range constraint
DEFINE FIELD years_experience ON user TYPE option<int>
    ASSERT $value == NONE OR ($value >= 0 AND $value <= 60);
```

Assertions fire on `CREATE` and `UPDATE`. Failed assertions return an error —
the record is not written.

---

## Default Values

Set field defaults with `VALUE`:

```surql
DEFINE TABLE role SCHEMAFULL;
DEFINE FIELD created_at ON role TYPE datetime
    VALUE $value OR time::now();  -- set on create, immutable after
DEFINE FIELD updated_at ON role TYPE datetime
    VALUE time::now();            -- recalculates on every update
DEFINE FIELD active ON role TYPE bool
    VALUE $value OR true;         -- default true
```

---

## Unique Indices

Enforce uniqueness at the index level:

```surql
-- Single-field unique index
DEFINE INDEX skill_name_idx ON skill FIELDS name UNIQUE;

-- Compound unique index
DEFINE INDEX role_company_title_idx ON role FIELDS company, title UNIQUE;
```

Attempting to insert a duplicate will raise an error.

---

## Example: User Profiles

```surql
DEFINE TABLE user SCHEMAFULL;
DEFINE FIELD name        ON user TYPE string ASSERT $value != NONE;
DEFINE FIELD email       ON user TYPE string ASSERT string::is_email($value);
DEFINE FIELD created_at  ON user TYPE datetime VALUE $value OR time::now();
DEFINE FIELD updated_at  ON user TYPE datetime VALUE time::now();
DEFINE FIELD role        ON user TYPE string
    ASSERT $value IN ["admin", "editor", "viewer"]
    VALUE $value OR "viewer";
DEFINE FIELD active      ON user TYPE bool VALUE $value OR true;

DEFINE INDEX user_email_idx ON user FIELDS email UNIQUE;

-- Insert
CREATE user:alice SET
    name = "Alice Chen",
    email = "alice@example.com",
    role = "editor";

-- Query: all active editors
SELECT name, email FROM user WHERE active = true AND role = "editor";
```

---

## Combining Relational + Graph

SCHEMAFULL tables with record link fields give you both type safety and traversal:

```surql
DEFINE TABLE role SCHEMAFULL;
DEFINE FIELD title       ON role TYPE string ASSERT $value != NONE;
DEFINE FIELD level       ON role TYPE string
    ASSERT $value IN ["junior", "mid", "senior", "staff", "principal"];
DEFINE FIELD company     ON role TYPE record<company> ASSERT $value != NONE;
DEFINE FIELD start_date  ON role TYPE datetime ASSERT $value != NONE;
DEFINE FIELD end_date    ON role TYPE option<datetime>;
DEFINE FIELD description ON role TYPE option<string>;

-- Graph traversal from a typed table
SELECT title, company.name, company.industry
FROM role
WHERE level = "senior" AND end_date = NONE;  -- current senior roles
```

---

## Trade-offs

| Aspect | Upside | Downside |
|--------|--------|---------|
| Type enforcement | Catches bad data at write time | Requires upfront schema design |
| Assertions | Server-side validation without app code | More DEFINE statements to maintain |
| Unique indices | Prevents duplicates reliably | Index overhead on insert |
| Stable schema | Predictable reads, no missing fields | Schema migrations needed for new fields |

---

## When NOT to Use

- When field structure varies significantly between records — use Document (SCHEMALESS)
- When you are still exploring the domain and expect schema to change frequently
- When the entity is ephemeral (sessions, caches, temporary state) — use Key-value
- When the data is append-only event logs — use Time-series conventions instead

Adding `SCHEMAFULL` prematurely is the most common mistake for new SurrealDB users
migrating from flexible stores. Start SCHEMALESS, add field definitions incrementally,
and graduate to full SCHEMAFULL when the schema has been stable for a while.
