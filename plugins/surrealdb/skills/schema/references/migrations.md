# Schema Migrations & Versioning

SurrealDB has no built-in migration framework. This guide covers the recommended approach:
versioned .surql files in a `migrations/` directory, applied in order.

---

## File Naming Convention

Use zero-padded sequence numbers followed by a descriptive slug:

```
migrations/
├── 001_initial_schema.surql
├── 002_add_skills_table.surql
├── 003_add_embedding_index.surql
├── 004_convert_user_schemafull.surql
├── 005_populate_skills_taxonomy.surql
└── 006_rename_legacy_fields.surql
```

**Rationale:** Sequential numbering enforces ordering. Slugs are human-readable.

---

## Migration File Template

Every migration file should include:

1. **Header comments** — migration name, description, date
2. **Forward migration** — the actual schema changes
3. **Rollback comments** — manual steps to revert (if applicable)

### Basic Template

```surql
-- Migration: 002_add_skills_table
-- Description: Add skills table with taxonomy and unique name constraint
-- Date: 2026-03-24
-- Author: Jacob Hoehler

-- ============================================================
-- Forward Migration
-- ============================================================

DEFINE TABLE skill SCHEMAFULL;
DEFINE FIELD name       ON skill TYPE string ASSERT $value != NONE AND string::len($value) >= 1;
DEFINE FIELD category   ON skill TYPE string ASSERT $value IN ["language", "framework", "tool", "infrastructure", "soft"];
DEFINE FIELD aliases    ON skill TYPE option<array<string>>;
DEFINE FIELD created_at ON skill TYPE datetime VALUE time::now();
DEFINE INDEX idx_skill_name ON skill FIELDS name UNIQUE;

-- ============================================================
-- Rollback (manual)
-- ============================================================
-- To revert this migration, run:
-- REMOVE TABLE skill;
```

### Migration with Data Transformation

```surql
-- Migration: 004_convert_user_schemafull
-- Description: Convert user table from SCHEMALESS to SCHEMAFULL; add validation
-- Date: 2026-03-24
-- Author: Jacob Hoehler

-- ============================================================
-- Pre-flight Checks (informational)
-- ============================================================
-- Run this before the migration to verify data:
-- SELECT COUNT() FROM user;  -- should be ~X records
-- SELECT * FROM user WHERE email IS NONE LIMIT 5;  -- check for nulls

-- ============================================================
-- Forward Migration
-- ============================================================

-- Step 1: Define all fields (before converting to SCHEMAFULL)
DEFINE FIELD name       ON user TYPE string;
DEFINE FIELD email      ON user TYPE string;
DEFINE FIELD bio        ON user TYPE option<string>;
DEFINE FIELD created_at ON user TYPE datetime;
DEFINE FIELD updated_at ON user TYPE datetime;

-- Step 2: Backfill missing defaults for required fields
UPDATE user
SET email = string::concat('user_', id)
WHERE email IS NONE;

UPDATE user
SET created_at = time::now()
WHERE created_at IS NONE;

-- Step 3: Convert to SCHEMAFULL (now all fields are defined)
ALTER TABLE user SCHEMAFULL;

-- Step 4: Add assertions and indices
DEFINE FIELD name       ON user TYPE string ASSERT $value != NONE;
DEFINE FIELD email      ON user TYPE string ASSERT string::is::email($value);
DEFINE FIELD bio        ON user TYPE option<string>;
DEFINE FIELD created_at ON user TYPE datetime;
DEFINE FIELD updated_at ON user TYPE datetime;
DEFINE INDEX idx_user_email ON user FIELDS email UNIQUE;

-- ============================================================
-- Rollback (manual)
-- ============================================================
-- To revert this migration, run:
-- ALTER TABLE user SCHEMALESS;
-- REMOVE INDEX idx_user_email FROM user;
```

### Migration Adding Index (Safe, Non-Destructive)

```surql
-- Migration: 003_add_embedding_index
-- Description: Add HNSW vector index for semantic search on posts
-- Date: 2026-03-24
-- Author: Jacob Hoehler

-- ============================================================
-- Forward Migration
-- ============================================================

-- Add embedding field if not present
DEFINE FIELD embedding ON post TYPE option<array<float>>;

-- Add vector index (builds asynchronously in background)
DEFINE INDEX idx_post_embedding ON post FIELDS embedding
    HNSW DIMENSION 384 DIST COSINE TYPE F32;

-- ============================================================
-- Rollback (manual)
-- ============================================================
-- To revert this migration, run:
-- REMOVE INDEX idx_post_embedding FROM post;
-- REMOVE FIELD embedding FROM post;  -- optional if field is still needed
```

---

## Safe vs. Risky Operations

### Safe Operations (Always Reversible)

| Operation | Why Safe | Rollback |
|-----------|----------|----------|
| Add field to SCHEMALESS table | Existing records unaffected | Remove field |
| Add field to SCHEMAFULL table | New records get null/default | Remove field |
| Add index | Only reads are affected | Remove index |
| Add computed field | No data written | Remove field |
| Add table | No data yet | Remove table |
| Loosen assertion (expand allowed values) | Existing data not revalidated | Tighten assertion |
| Remove assertion | Relaxes validation | Re-add assertion |
| Add `option<T>` (nullable) | Allows null | Change to `T` (required) |

### Risky Operations (Requires Backfill)

| Operation | Why Risky | Mitigation |
|-----------|-----------|-----------|
| Remove field from SCHEMAFULL | Field hidden; data retained (cannot undo) | Accept permanence; verify no queries depend on it |
| Rename field | No RENAME command | Copy to new field; migrate data; drop old field |
| Change field type | Existing data may not match new type | Validate/transform data first; backfill |
| Add unique constraint to field with duplicates | Constraint fails | Deduplicate data first |
| Add required assertion to field with nulls | Assertion fails | Backfill nulls with valid values |
| Convert SCHEMALESS to SCHEMAFULL without defining all fields | Fields not in DEFINE list are silently dropped | Define ALL fields before conversion |
| Change vector HNSW DIMENSION | Index mismatch with actual embeddings | Rebuild embeddings; reindex |

---

## Migration Pattern: Renaming a Field

SurrealDB has no built-in RENAME. Use this pattern instead:

```surql
-- Migration: 006_rename_user_name_to_display_name
-- Description: Rename user.name to user.display_name
-- Date: 2026-03-24

-- ============================================================
-- Forward Migration
-- ============================================================

-- Step 1: Add new field with same definition and value
DEFINE FIELD display_name ON user TYPE string
    VALUE $this.name;

-- Step 2: Populate new field from old field
UPDATE user SET display_name = name;

-- Step 3: Verify new field is populated
-- SELECT COUNT() FROM user WHERE display_name IS NOT NONE;  -- should match total count

-- Step 4: Drop old field
REMOVE FIELD name FROM user;

-- ============================================================
-- Rollback (manual)
-- ============================================================
-- To revert, run:
-- DEFINE FIELD name ON user TYPE string VALUE $this.display_name;
-- UPDATE user SET name = display_name;
-- REMOVE FIELD display_name FROM user;
```

---

## Migration Pattern: Adding an Index

Indices build asynchronously and don't block writes.

```surql
-- Migration: 007_add_post_published_index
-- Description: Add index for filtering posts by published status
-- Date: 2026-03-24

-- ============================================================
-- Forward Migration
-- ============================================================

DEFINE INDEX idx_post_published ON post FIELDS published;

-- ============================================================
-- Validation Query (run after migration)
-- ============================================================
-- Verify the index exists:
-- INFO FOR TABLE post;

-- ============================================================
-- Rollback (manual)
-- ============================================================
-- REMOVE INDEX idx_post_published FROM post;
```

---

## Migration Pattern: Safe Schema Evolution

When adding a required field to an existing table with data:

```surql
-- Migration: 008_add_user_role_required
-- Description: Add role field (required) to user; assign default role
-- Date: 2026-03-24

-- ============================================================
-- Forward Migration
-- ============================================================

-- Step 1: Add field as optional first
DEFINE FIELD role ON user TYPE option<string>;

-- Step 2: Backfill with default value
UPDATE user SET role = "user" WHERE role IS NONE;

-- Step 3: Convert to required (now all records have a value)
DEFINE FIELD role ON user TYPE string
    ASSERT $value IN ["admin", "moderator", "user"];

DEFINE INDEX idx_user_role ON user FIELDS role;

-- ============================================================
-- Rollback (manual)
-- ============================================================
-- DEFINE FIELD role ON user TYPE option<string>;
-- REMOVE INDEX idx_user_role FROM user;
```

---

## Python Migration Runner Example

This is a common pattern for CI/CD integration. Not required for SurrealDB, but
useful for tracking applied migrations.

```python
from pathlib import Path
from surrealdb import Surreal

async def run_migrations(db: Surreal, migrations_dir: Path):
    """
    Run pending .surql migrations in order.

    Args:
        db: Connected SurrealDB client
        migrations_dir: Path to migrations/ directory
    """
    # Get list of applied migrations
    applied = await db.select("migration")
    applied_names = {m["name"] for m in applied}

    # Find all migration files and sort by sequence number
    migration_files = sorted(migrations_dir.glob("*.surql"))

    for migration_file in migration_files:
        migration_name = migration_file.stem  # e.g., "001_initial_schema"

        if migration_name in applied_names:
            print(f"✓ {migration_name} (already applied)")
            continue

        # Read and execute migration
        schema = migration_file.read_text()
        try:
            await db.query(schema)
            print(f"✓ {migration_name} (applied)")
        except Exception as e:
            print(f"✗ {migration_name} (failed: {e})")
            raise

        # Record migration as applied
        await db.create("migration", {
            "name": migration_name,
            "applied_at": "time::now()",
            "file": str(migration_file),
        })

# Usage:
# async with Surreal() as db:
#     await db.connect("ws://localhost:8000")
#     await db.use("namespace", "database")
#     await run_migrations(db, Path("migrations/"))
```

### Migration Tracking Table Schema

Create this table in your base schema to track applied migrations:

```surql
-- Track applied migrations for idempotency
DEFINE TABLE migration SCHEMAFULL;
DEFINE FIELD name       ON migration TYPE string ASSERT $value != NONE;
DEFINE FIELD applied_at ON migration TYPE datetime VALUE time::now();
DEFINE FIELD file       ON migration TYPE option<string>;
DEFINE INDEX idx_migration_name ON migration FIELDS name UNIQUE;
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Out-of-order migration execution | Enforce sequential naming (001, 002, 003...) and run in order |
| No rollback documentation | Always include manual rollback comments (even if "not reversible") |
| Migration assumes data exists | Add pre-flight checks; use UPDATE ... WHERE to handle missing data |
| Applying migration twice | Track applied migrations in a `migration` table; use idempotency check |
| Mixing data and schema in one file | Keep schema changes and data backfills separate (or clearly comment) |
| No validation before/after | Add SELECT COUNT() or sample queries as comments to verify results |
| Vector index without matching DIMENSION | Verify HNSW DIMENSION matches actual embedding model output size |
| Converting SCHEMALESS to SCHEMAFULL incompletely | Define ALL fields first or data is silently dropped |

---

## Best Practices

1. **One concern per migration file** — separate schema changes from data backfills
2. **Always include rollback comments** — even if reverting is manual
3. **Test on a copy of production data** — catch data transform issues early
4. **Add pre-flight checks** — queries to validate assumptions (in comments)
5. **Track applied migrations** — use a `migration` table for idempotency
6. **Name files sequentially** — 001, 002, 003... ensures consistent ordering
7. **Include descriptive slugs** — "006_rename_user_name_to_display_name" beats "006"
8. **Document transformations** — why the change (in header comments)
9. **Backfill before constraints** — add field, populate, then add assertions
10. **Lock table during risky changes** — use transactions for multi-step changes (if supported in your SurrealDB version)
