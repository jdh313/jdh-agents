# SurrealDB: Document Model

## When to Use

Use the document model when:
- Field structure varies between records of the same type
- You are iterating quickly on schema and it changes frequently
- Records contain deeply nested objects with non-uniform shapes
- You are migrating from MongoDB, DynamoDB, or a YAML/JSON store
- The entity is used for early-stage prototyping before the schema stabilizes

The document model is the **default** starting point for unknown or evolving domains.
Graduate to SCHEMAFULL (relational) when the schema stabilizes and type safety matters.

---

## SCHEMALESS Tables

A SCHEMALESS table accepts any field without prior declaration:

```surql
DEFINE TABLE job_posting SCHEMALESS;

-- These both succeed even though fields differ
CREATE job_posting SET
    title = "Senior Engineer",
    requirements = ["Python", "SurrealDB"],
    remote = true;

CREATE job_posting SET
    title = "Data Analyst",
    preferred_skills = { python: "required", sql: "preferred" },
    salary_range = { min: 80000, max: 120000 };
```

No schema enforcement means no errors on insert — and no automatic type validation.

---

## Nested Objects and Arrays

SurrealDB stores nested objects natively. Access nested fields with dot notation:

```surql
CREATE job_posting SET
    title = "ML Engineer",
    location = {
        city = "San Francisco",
        remote_allowed = true,
        timezone = "America/Los_Angeles"
    },
    requirements = [
        { skill = "Python", level = "required" },
        { skill = "PyTorch", level = "preferred" }
    ];

-- Access nested fields
SELECT title, location.city, requirements[0].skill FROM job_posting;

-- Filter on nested field
SELECT * FROM job_posting WHERE location.remote_allowed = true;

-- Filter within arrays
SELECT * FROM job_posting WHERE requirements[WHERE level = "required"].skill CONTAINS "Python";
```

---

## Example: Job Postings Domain

Job postings are a canonical use case — requirements vary per role, compensation
structures differ (salary, equity, hourly), and the schema changes as the business
evolves.

```surql
DEFINE TABLE job_posting SCHEMALESS;

-- Create a posting with variable structure
CREATE job_posting:acme_ml_2024 SET
    title = "Senior ML Engineer",
    company = company:acme,
    posted_at = time::now(),
    requirements = {
        required: ["Python", "PyTorch", "CUDA"],
        preferred: ["TensorRT", "MLflow"]
    },
    compensation = {
        type = "salary",
        min = 180000,
        max = 240000,
        equity_percent = 0.15
    },
    description = "Build production ML systems at scale...",
    remote = "hybrid";

-- Query: find hybrid or fully remote postings requiring Python
SELECT title, compensation.min, compensation.max
FROM job_posting
WHERE remote IN ["hybrid", "remote"]
    AND requirements.required CONTAINS "Python";
```

---

## Partially Enforced Documents

SCHEMALESS does not mean zero validation. You can define specific fields with
types and assertions while leaving others open:

```surql
DEFINE TABLE job_posting SCHEMALESS;

-- Enforce only the fields you care about
DEFINE FIELD title    ON job_posting TYPE string ASSERT $value != NONE;
DEFINE FIELD company  ON job_posting TYPE record<company>;
DEFINE FIELD posted_at ON job_posting TYPE datetime VALUE $value OR time::now();

-- All other fields are still accepted without declaration
```

This pattern is useful for migrating from fully schemaless to relational incrementally.

---

## Trade-offs

| Aspect | Upside | Downside |
|--------|--------|---------|
| Schema flexibility | No migrations needed for new fields | No type guarantees on read |
| Rapid iteration | Add fields freely during development | Inconsistent data if fields drift |
| Nested objects | Natural for hierarchical data | Harder to query deeply nested paths |
| No required fields | Easy inserts | Missing required data only found at read time |

**When to graduate to SCHEMAFULL:**
- Multiple consumers depend on consistent field shapes
- You need assertion-based validation (format checks, range constraints)
- The schema has been stable for several weeks
- Type errors in application code are appearing due to missing/unexpected fields

---

## Anti-Patterns

- **Using documents when you need referential integrity.** If you need to guarantee
  that `job_posting.company` always points to a valid company record, use a
  SCHEMAFULL field with `TYPE record<company>` instead of a free-form field.

- **Deeply nested mutation.** SurrealDB does not support partial deep updates on
  nested objects natively. Update at the record level or use explicit dot-notation
  patching. Deeply nested schemas that mutate frequently are painful to maintain.

- **Storing embeddings in SCHEMALESS without an index.** An embedding field without
  an HNSW index degrades to a full table scan on similarity queries. Define the
  field explicitly and add the index even in a SCHEMALESS table.

---

## When NOT to Use

- When all field names and types are known and stable — use SCHEMAFULL (relational)
- When you need guaranteed uniqueness or format validation across all records
- When the entity is canonical reference data shared by many others (e.g., skill names)
- When the primary query pattern is "give me record X by ID" with no complex field
  access — consider key-value instead
