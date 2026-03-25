---
name: surrealdb:schema
description: >-
  Use when the user says "/sdb:schema", "define SurrealDB schema", "evolve my schema",
  "add a field to SurrealDB", "schema migration", "SurrealDB migration",
  "version my schema", "SCHEMAFULL vs SCHEMALESS", or when designing or modifying
  SurrealDB table definitions. Guides schema design decisions and manages schema
  evolution with versioned .surql migration scripts.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Write
  - AskUserQuestion
---

# /sdb:schema -- SurrealDB Schema Designer & Migration Manager

Designs and evolves SurrealDB schemas. Helps decide SCHEMAFULL vs SCHEMALESS for tables,
defines fields with types and assertions, creates indices, and manages schema changes via
versioned migration scripts.

Read `references/schema-patterns.md` before starting for field types, assertions, and index
patterns. Load `references/migrations.md` when writing migration scripts.

---

## Flow

Execute these steps in order. Do not skip steps or combine them unless the user
explicitly asks for a faster pass.

### Step 1: Assess Current State

Determine if this is a greenfield schema or an evolution of existing structure.

**If the user is designing a new schema:**
Ask about the primary entity and what it connects to. Example:
> What's the core entity (e.g., post, user, product), and what does it relate to?

After one response, proceed — do not wait for a complete domain model.

**If the user is evolving an existing schema:**
- Ask: "Do you have an existing .surql schema file or Pydantic model?"
- If yes, read the files using Bash/Read/Glob tools
- Extract table names, field definitions, indices, and record links
- Identify what's changing (new table, new field, renamed field, index changes, type changes)

**If you can't find existing schema:**
Treat as greenfield and ask the scoping question.

---

### Step 2: Decide SCHEMAFULL vs SCHEMALESS

For each table, decide the strictness level. Read `references/schema-patterns.md` for
the decision matrix.

Ask these questions per table:

1. **Is the structure well-defined and stable?** (Yes → SCHEMAFULL; No → SCHEMALESS)
2. **Is it a core business entity?** (Yes → SCHEMAFULL; external API responses → SCHEMALESS)
3. **Will a field mismatch cause silent data loss?** (Yes → SCHEMAFULL; No → SCHEMALESS)

Present your recommendations in a table:

```
| Table | SCHEMAFULL | Rationale |
|-------|-----------|-----------|
| user  | ✓         | Core entity; all users have name, email, created_at |
| post  | ✓         | Structured; title + content + published_at required |
| event | ✗         | External event data; structure varies by event type |
| config | ✗        | Application config; fields added dynamically |
```

Ask: "Does this match your intent? Any tables you'd flip?"

After confirmation, move to Step 3.

---

### Step 3: Define Fields, Types, and Assertions

For each table, list the fields with:
- Type (string, int, float, bool, datetime, array, record, etc.)
- Required vs. optional (option<T> for nullable)
- Assertions (validation rules)

Load `references/schema-patterns.md` for assertion patterns and field type reference.

Output complete DEFINE statements:

```surql
-- User table (SCHEMAFULL, core identity entity)
DEFINE TABLE user SCHEMAFULL;
DEFINE FIELD name       ON user TYPE string ASSERT $value != NONE AND string::len($value) >= 1;
DEFINE FIELD email      ON user TYPE string ASSERT string::is::email($value) UNIQUE;
DEFINE FIELD bio        ON user TYPE option<string>;
DEFINE FIELD created_at ON user TYPE datetime VALUE time::now();
DEFINE FIELD updated_at ON user TYPE datetime VALUE time::now();

-- Post table (SCHEMAFULL, requires title and content)
DEFINE TABLE post SCHEMAFULL;
DEFINE FIELD title      ON post TYPE string ASSERT $value != NONE AND string::len($value) <= 200;
DEFINE FIELD content    ON post TYPE string ASSERT $value != NONE;
DEFINE FIELD author     ON post TYPE record<user> ASSERT $value != NONE;
DEFINE FIELD published  ON post TYPE bool VALUE false;
DEFINE FIELD created_at ON post TYPE datetime VALUE time::now();

-- Event table (SCHEMALESS, structure varies)
DEFINE TABLE event SCHEMALESS;
DEFINE FIELD type       ON event TYPE string;
DEFINE FIELD timestamp  ON event TYPE datetime VALUE time::now();
DEFINE FIELD data       ON event TYPE option<object>;
```

Ask: "Do these fields and assertions capture your requirements? Anything to add or remove?"

---

### Step 4: Define Indices

Indices speed up queries and enforce uniqueness. Read `references/schema-patterns.md`
for index types.

For each table, identify indexed fields:

1. **Unique constraints** (user.email, post title if required to be unique)
2. **Query filters** (post.author for "find all posts by user")
3. **Full-text search** (post.content for keyword search)
4. **Vector similarity** (embedding fields for semantic search)

Output DEFINE INDEX statements:

```surql
-- Standard index for WHERE queries
DEFINE INDEX idx_post_author ON post FIELDS author;

-- Unique index (enforces uniqueness + indexes)
DEFINE INDEX idx_user_email ON user FIELDS email UNIQUE;

-- Composite index (speed up compound WHERE)
DEFINE INDEX idx_post_author_published ON post FIELDS author, published;

-- Full-text search index
DEFINE INDEX idx_post_content ON post FIELDS content SEARCH ANALYZER ascii BM25;

-- Vector HNSW index (for embeddings)
DEFINE INDEX idx_post_embedding ON post FIELDS embedding HNSW DIMENSION 384 DIST COSINE TYPE F32;
```

Ask: "Do these indices match your query patterns? Any missing?"

---

### Step 5: Define Record Links and Computed Fields

Record links (record<table>) connect tables and enable graph traversal.

For each record link:
- Show the DEFINE FIELD
- Explain what queries it enables

Example:

```surql
-- Link post to author (enables "find all posts by user")
DEFINE FIELD author ON post TYPE record<user> ASSERT $value != NONE;

-- Computed field: count of posts by author (enables "author.post_count")
DEFINE FIELD post_count ON user VALUE (
  SELECT COUNT() FROM post WHERE author = $this
);

-- Backward reference: fetch authors of posts (enables "post<-author<-user")
-- (no DEFINE needed — SurrealDB infers the back-reference)
```

Load `references/schema-patterns.md` for computed field patterns.

Ask: "Are there any computed fields or backward references you'd like?"

---

### Step 6: Output Complete Schema File

Consolidate all DEFINE statements into a single .surql file. Structure it as:

**For greenfield schemas:** Create `schema/base_schema.surql`

```surql
-- ============================================
-- SurrealDB Base Schema
-- Version: 1.0.0
-- Description: Core tables and relationships
-- ============================================

-- User table (SCHEMAFULL)
DEFINE TABLE user SCHEMAFULL;
DEFINE FIELD name       ON user TYPE string ASSERT $value != NONE;
DEFINE FIELD email      ON user TYPE string ASSERT string::is::email($value);
DEFINE INDEX idx_user_email ON user FIELDS email UNIQUE;

-- Post table (SCHEMAFULL)
DEFINE TABLE post SCHEMAFULL;
DEFINE FIELD title      ON post TYPE string ASSERT $value != NONE;
DEFINE FIELD content    ON post TYPE string;
DEFINE FIELD author     ON post TYPE record<user>;
DEFINE FIELD created_at ON post TYPE datetime VALUE time::now();
DEFINE INDEX idx_post_author ON post FIELDS author;

-- Event table (SCHEMALESS)
DEFINE TABLE event SCHEMALESS;
DEFINE FIELD timestamp  ON event TYPE datetime VALUE time::now();
```

**For evolving schemas:** Create versioned migration file `migrations/NNN_description.surql`

Load `references/migrations.md` for migration file templates and patterns.

```surql
-- Migration: 003_add_embedding_index
-- Description: Add vector index for semantic search on posts
-- Date: 2026-03-24

-- Forward migration
DEFINE FIELD embedding ON post TYPE option<array<float>>;
DEFINE INDEX idx_post_embedding ON post FIELDS embedding HNSW DIMENSION 384 DIST COSINE TYPE F32;

-- Rollback (manual — run if reverting this migration)
-- REMOVE FIELD embedding FROM post;
-- REMOVE INDEX idx_post_embedding FROM post;
```

Present the file(s) to the user and ask: "Does this schema match your requirements?"

---

### Step 7: Review for Pitfalls

Before finalizing, check for common issues:

- **Missing indices on queried fields** — if you filter by a field in WHERE, index it
- **Overly strict assertions** — will they reject valid data during evolution?
- **Orphaned record links** — linking to tables that don't exist in the schema
- **SCHEMAFULL missing required fields** — fields not explicitly DEFINE'd are silently dropped
- **Vector indices without proper config** — DIMENSION and DIST are required; mismatch with actual embedding size will fail
- **No rollback statements in migrations** — always include manual rollback comments

Fix any issues found. Explain what was changed and why.

---

### Step 8: Confirm and Offer Next Steps

Ask:

> Does this schema capture your requirements? Any fields to add, remove, or assertions
> to adjust?

After confirmation, offer:

```
Next steps:
- /sdb:migrate   -- plan migration from existing storage (SQLite, JSON, etc.) to this schema
- /sdb:query     -- write SurrealQL queries against this schema
- /sdb:model     -- revisit data model if requirements change
```

---

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| Converting SCHEMALESS to SCHEMAFULL | Must define ALL fields first or data is silently dropped. Provide a backfill + validation strategy. |
| Renaming a field | SurrealDB has no RENAME. Show copy pattern: create new field, copy data, drop old field. |
| Removing a field | In SCHEMAFULL, field is hidden but data retained in records. Acknowledge this if irreversible deletion is the goal. |
| Changing field type | Risky. Ask: "What should happen to existing data?" Validate before/after or backfill with transformation. |
| Vector embedding field without model | Warn: specify DIMENSION (must match model output) and DIST (cosine/euclidean/manhattan). |
| Circular record links | Allowed (e.g., person → person for manager relationships). Explicitly call out and validate graphs don't cause query loops. |
| Many fields on one table | Review SCHEMAFULL vs SCHEMALESS — consider splitting into multiple tables or using embedded objects. |
| Migrations on prod schema | Warn about rollback readiness. Include pre-flight checks (count affected records, validate sample data). |

---

## What This Skill Does NOT Do

- Write application code (use /sdb:query)
- Tune performance (use /sdb:migrate for migration-specific perf)
- Populate schema with seed data (that goes in migrations/seed/)
- Execute migrations (migrations are scripts for manual or CI/CD execution)
- Decide domain model (use /sdb:model first)
- Enforce naming conventions (that's up to you; we suggest snake_case for fields/indices)
