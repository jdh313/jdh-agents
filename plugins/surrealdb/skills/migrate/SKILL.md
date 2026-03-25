---
name: surrealdb:migrate
description: >-
  Use when the user says "/sdb:migrate", "migrate to SurrealDB", "convert YAML to SurrealDB",
  "move from SQL to SurrealDB", "import data into SurrealDB", "migrate from PostgreSQL",
  "ChromaDB to SurrealDB", "Pydantic models to SurrealDB", or when planning a data
  migration from an existing data layer to SurrealDB. Reads existing data sources, maps
  entities to SurrealDB models, and generates migration plans with Python import scripts.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Write
  - AskUserQuestion
---

# /sdb:migrate -- SurrealDB Migration Planner

Plans and executes data migrations FROM existing data layers (YAML, SQL, ChromaDB,
Pydantic models, Django models, JSON) TO SurrealDB. Reads source data, maps entities
to SurrealDB models, generates schema creation scripts, and produces complete Python
import code using the official AsyncSurreal SDK.

Read `references/migration-patterns.md` before starting. Reference specific patterns
as each source type is handled.

---

## Flow

Execute these steps in order. Do not skip or combine unless the user explicitly asks
for a faster pass.

### Step 1: Identify Source Data Layer

Determine what data layer the user is migrating FROM. Ask if unclear:

> What is your current data storage? (Choose one: YAML files, Pydantic models, SQL/SQLAlchemy,
> Django models, ChromaDB, raw JSON files, other ORM)

**Auto-detect patterns if source code is available:**

```bash
# For Pydantic: look for `from pydantic import BaseModel`
rg "class.*\(BaseModel\)" --type py

# For SQLAlchemy: look for `declarative_base` or `Column`
rg "declarative_base|class.*\(Base\)" --type py

# For Django: look for `models.Model`
rg "class.*\(models\.Model\)" --type py

# For ChromaDB: look for chromadb imports
rg "import chromadb|from chromadb" --type py

# For YAML: check file structure
ls -la *.yaml *.yml
```

After identifying the source, ask clarifying questions:
- Are there any one-to-many or many-to-many relationships?
- What is the approximate data volume (rows/documents)?
- Are there any special data types (vectors/embeddings, dates, UUIDs)?
- Is the source data in sync with your application, or is it a snapshot?

---

### Step 2: Analyze Source Schema

Read and extract the schema from the source data layer.

**For YAML:**
```bash
# Read YAML files to understand structure
cat path/to/*.yaml | head -50
```
Extract: top-level keys, field types, nested objects, arrays.

**For Pydantic models:**
```bash
# Read Python models file
cat path/to/models.py
```
Extract: class names, field types (str, int, list, Optional), nested models, relationships.

**For SQL/SQLAlchemy:**
```bash
# Read models or schema definition
cat path/to/models.py
# OR
cat path/to/migrations/*.py
```
Extract: table names, column types, foreign keys, indices, constraints.

**For Django:**
```bash
# Read Django models
cat path/to/models.py
```
Extract: model names, field types, relationships (ForeignKey, ManyToManyField), constraints.

**For ChromaDB:**
```bash
# Inspect ChromaDB instance metadata
python -c "import chromadb; client = chromadb.PersistentClient(path='./chroma_data');
[print(c.name, c.metadata) for c in client.list_collections()]"
```
Extract: collection names, metadata, expected dimensions, document structure.

**For JSON:**
```bash
# Read sample JSON files
cat path/to/*.json | jq '.[0]' | head -30
```
Extract: root object structure, array fields, nested objects.

After extraction, present a schema summary:

```
Source Schema Analysis:
- Table/Collection: users
  - id (string, primary key)
  - name (string, required)
  - email (string, unique)
  - created_at (datetime)

- Table/Collection: posts
  - id (string, primary key)
  - title (string)
  - content (string)
  - author_id (FK → users.id)
  - created_at (datetime)

Relationships:
- posts → users (many-to-one via author_id)
```

Ask for confirmation: "Does this match your source structure? Any missing or different?"

---

### Step 3: Map to SurrealDB Models

For each entity in the source, determine the best SurrealDB model. Reference the
decision tree from `/sdb:model` skill (`references/decision-tree.md`).

Create a mapping table:

```
| Source Entity | Source Type | SurrealDB Table | SurrealDB Model | Rationale |
|---|---|---|---|---|
| users | Table | user | Relational | Fixed schema; ID → record ID; FK → record link |
| posts | Table | post | Document + Graph | Variable content; FK links; optional full-text search |
| ChromaDB vectors | Collection | embeddings | Vector + Relational | Vectors + HNSW index; metadata as object field |
```

For relationships:
- SQL FOREIGN KEY → SurrealDB record link field
- SQL JOIN → SurrealDB graph traversal (->)
- SQL many-to-many → SurrealDB RELATE edge table
- Self-referential FK → record link to same table

---

### Step 4: Generate SurrealDB Schema

Create DEFINE statements for all tables and indices. Order them to respect dependencies:
- Tables with no record links first
- Tables with record links second (must link to existing tables)
- RELATE edge tables last

Example structure:

```surql
-- Base tables (no dependencies)
DEFINE TABLE user SCHEMAFULL;
DEFINE FIELD id ON user TYPE string ASSERT $value != NONE;
DEFINE FIELD name ON user TYPE string ASSERT $value != NONE;
DEFINE FIELD email ON user TYPE string;
DEFINE INDEX user_email_idx ON user FIELDS email UNIQUE;

-- Tables with record links (depends on user)
DEFINE TABLE post SCHEMAFULL;
DEFINE FIELD id ON post TYPE string ASSERT $value != NONE;
DEFINE FIELD title ON post TYPE string ASSERT $value != NONE;
DEFINE FIELD content ON post TYPE string;
DEFINE FIELD author ON post TYPE record<user> ASSERT $value != NONE;
DEFINE FIELD created_at ON post TYPE datetime;

-- Edge tables (RELATE)
DEFINE TABLE likes SCHEMAFULL;
DEFINE FIELD in ON likes TYPE record<post> ASSERT $value != NONE;
DEFINE FIELD out ON likes TYPE record<user> ASSERT $value != NONE;
DEFINE FIELD created_at ON likes TYPE datetime;
```

---

### Step 5: Create Migration Plan

Generate a numbered checklist for the migration:

```
Migration Plan:

1. Schema Preparation
   [ ] Create SurrealDB instance or connect to existing
   [ ] Run DEFINE statements to create all tables and indices
   [ ] Verify tables created: SELECT * FROM $tables;

2. Data Import (in dependency order)
   [ ] Import users (X records) — run batch_import_users.py
   [ ] Import posts (Y records) — run batch_import_posts.py
   [ ] Import likes (Z records) — run batch_import_likes.py

3. Validation
   [ ] User count: SELECT count() FROM user GROUP ALL;
   [ ] Post count: SELECT count() FROM post GROUP ALL;
   [ ] Check FK integrity: SELECT * FROM post WHERE author == NONE;
   [ ] Check edge count: SELECT count() FROM likes GROUP ALL;

4. Rollback Strategy
   If any step fails:
   - Drop all tables: DROP TABLE user, post, likes;
   - Fix source or mapping issue
   - Re-run schema creation and import from Step 1
```

---

### Step 6: Generate Python Migration Code

Create complete, runnable Python scripts using AsyncSurreal SDK.

**Structure:**
1. Connection and initialization
2. Schema setup function (runs DEFINE statements)
3. Data import functions (per table, batch support)
4. Validation queries
5. Main entry point with error handling

Reference `references/migration-patterns.md` for patterns matching the source type.

Example scaffold:

```python
import asyncio
from surrealdb import AsyncSurreal, AsyncRecordIdBuilder
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection settings
DB_URL = "ws://localhost:8000"
DB_USER = "root"
DB_PASS = "root"
DB_NAMESPACE = "migration"
DB_DATABASE = "app"

async def setup_schema(db: AsyncSurreal):
    """Create tables and indices."""
    await db.query("""
        DEFINE TABLE user SCHEMAFULL;
        DEFINE FIELD id ON user TYPE string ASSERT $value != NONE;
        DEFINE FIELD name ON user TYPE string ASSERT $value != NONE;
        ...
    """)
    logger.info("Schema setup complete")

async def import_data(db: AsyncSurreal):
    """Import data from source."""
    # Implementation per source type
    pass

async def validate_migration(db: AsyncSurreal):
    """Check data integrity post-migration."""
    user_count = await db.query("SELECT count() FROM user GROUP ALL;")
    logger.info(f"User records: {user_count}")
    # Additional validation queries

async def main():
    db = AsyncSurreal(DB_URL)
    try:
        await db.connect()
        await db.signin({"user": DB_USER, "pass": DB_PASS})
        await db.use(DB_NAMESPACE, DB_DATABASE)

        logger.info("Connected to SurrealDB")

        await setup_schema(db)
        await import_data(db)
        await validate_migration(db)

        logger.info("Migration complete")
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        raise
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())
```

Generate specific functions for each source type using patterns from reference file.

---

### Step 7: Write Complete Migration Scripts

For each table or related group, generate a complete, ready-to-run script file.

Files to create:
- `00_schema.surql` — SurrealQL schema (DEFINE statements)
- `01_import_base_tables.py` — Import tables with no dependencies
- `02_import_linked_tables.py` — Import tables with record links
- `03_import_edges.py` — Import RELATE edges
- `04_validate.py` — Validation queries and integrity checks
- `05_rollback.surql` — DROP statements for cleanup

Each file should be:
- Runnable in isolation (with appropriate setup)
- Well-commented with assumptions
- Include error handling and logging
- Reference the migration plan from Step 5

---

### Step 8: Verification and Next Steps

Ask for confirmation:

> Ready to proceed with migration? I've generated:
> - Schema definition (00_schema.surql)
> - Import scripts (01_, 02_, 03_)
> - Validation suite (04_validate.py)
> - Rollback plan (05_rollback.surql)
>
> Next steps:
> 1. Review the schema — make any adjustments to table/field structure
> 2. Test locally: run 00_schema.surql in your SurrealDB instance
> 3. Run import scripts in order: 01, 02, 03
> 4. Run validation: python 04_validate.py
> 5. If successful, data is in SurrealDB
> 6. If failure, run 05_rollback.surql and fix the source/sdb:schema

Offer:
- `/sdb:schema` — expand or modify the generated schema
- `/sdb:query` — write SurrealQL queries to verify the migrated data
- Help debugging if any import script fails

---

## Edge Cases

| Situation | Behavior |
|---|---|
| Source has no schema (unstructured YAML) | Ask user to describe entity types; infer structure from sample data |
| Source has FK cycles (A→B→A) | Handle in RELATE edges last; note in migration plan |
| Source has composite primary keys | Use array fields or concatenation; reference as record ID |
| Source has enums/constraints | Map to string + note valid values in ASSERT |
| Source has JSON/JSONB fields | Store as object or nested document; extract and structure if needed |
| Source has large BLOBs | Import with `? as $data` syntax; consider chunking if >100MB |
| ChromaDB with multiple collections | Create one SurrealDB table per collection; preserve collection name |
| Django signals/hooks | Note in comments that these don't migrate; recommend app-side handling |
| Many-to-many with metadata | Map to RELATE edge table; store metadata in edge fields |
| Self-referential relationships | Show record link to same table; test with sample queries |
| Data volume > 1M rows | Recommend batch size tuning; show progress tracking |
| Source uses soft deletes | Add is_deleted field; optionally filter during import |
| Inconsistent field types (string vs. int for ID) | Standardize during import; show type conversion code |

---

## What This Skill Does NOT Do

- Execute the migration without user confirmation
- Modify the source data layer
- Handle bidirectional syncing (one-way import only)
- Optimize indices for production (generate basic indices; use `/sdb:schema` for tuning)
- Provide backup/rollback beyond DROP TABLE statements
- Handle real-time CDC (change data capture) — this is snapshot migration
- Generate Kubernetes/CI manifests (manual deployment step)
