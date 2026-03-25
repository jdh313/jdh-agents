# Migration Patterns: Source → SurrealDB

Reusable code patterns for migrating data from common sources to SurrealDB using
AsyncSurreal SDK.

---

## YAML → SurrealDB

**When to use:** Migrating from YAML config files, data exports, or document stores.

**Assumptions:**
- YAML files in a directory (e.g., `./data/`)
- Top-level key becomes table name
- Each record under that key is a document
- No schema enforcement initially (SCHEMALESS table)

**Python Pattern:**

```python
import asyncio
import yaml
from pathlib import Path
from surrealdb import AsyncSurreal
import logging

logger = logging.getLogger(__name__)

async def import_yaml(db: AsyncSurreal, yaml_dir: Path, batch_size: int = 100):
    """Import YAML files into SurrealDB.

    Directory structure:
        data/
            users.yaml:
                - id: user1
                  name: Alice
                  email: alice@example.com
            posts.yaml:
                - id: post1
                  title: First Post
                  author_id: user1
    """
    yaml_files = sorted(yaml_dir.glob("*.yaml")) + sorted(yaml_dir.glob("*.yml"))

    for yaml_file in yaml_files:
        table_name = yaml_file.stem  # filename without extension
        logger.info(f"Importing {yaml_file.name} → {table_name}")

        data = yaml.safe_load(yaml_file.read_text())

        if not data:
            logger.warning(f"  {yaml_file.name} is empty, skipping")
            continue

        # Handle both list and dict YAML structures
        records = data if isinstance(data, list) else [data]

        # Import with progress tracking
        for i, record in enumerate(records):
            record_id = record.get("id", f"{table_name}:{i}")
            await db.create(table_name, record, record_id=record_id)

            if (i + 1) % batch_size == 0:
                logger.info(f"  Imported {i + 1}/{len(records)} records to {table_name}")

        logger.info(f"  Completed: {len(records)} records in {table_name}")
```

**Schema Setup:**

```surql
-- Define table as SCHEMALESS initially (flexible for YAML structure)
DEFINE TABLE users SCHEMALESS;

-- Once schema is known, lock it down
DEFINE TABLE users SCHEMAFULL;
DEFINE FIELD id ON users TYPE string ASSERT $value != NONE;
DEFINE FIELD name ON users TYPE string ASSERT $value != NONE;
DEFINE FIELD email ON users TYPE string;
```

---

## Pydantic → SurrealDB

**When to use:** Migrating from Pydantic model instances, FastAPI apps, or Python dataclasses.

**Type Mapping:**

| Pydantic Type | SurrealDB Type | Example |
|---|---|---|
| str | string | `DEFINE FIELD name ON user TYPE string;` |
| int | int | `DEFINE FIELD age ON user TYPE int;` |
| float | float | `DEFINE FIELD score ON user TYPE float;` |
| bool | bool | `DEFINE FIELD is_active ON user TYPE bool;` |
| datetime | datetime | `DEFINE FIELD created_at ON user TYPE datetime;` |
| UUID | string | `DEFINE FIELD id ON user TYPE string;` |
| list[str] | array<string> | `DEFINE FIELD tags ON user TYPE array<string>;` |
| list[int] | array<int> | `DEFINE FIELD scores ON user TYPE array<int>;` |
| Optional[str] | option<string> | `DEFINE FIELD bio ON user TYPE option<string>;` |
| Model (nested) | record<table> OR object | Depends on use case |

**Python Pattern:**

```python
import asyncio
from typing import Type
from pydantic import BaseModel
from surrealdb import AsyncSurreal
import logging

logger = logging.getLogger(__name__)

async def import_pydantic(
    db: AsyncSurreal,
    table_name: str,
    model_class: Type[BaseModel],
    records: list,
    batch_size: int = 100
):
    """Import Pydantic model instances into SurrealDB.

    Args:
        db: AsyncSurreal connection
        table_name: Target SurrealDB table name
        model_class: Pydantic model class (for validation)
        records: List of model instances or dicts
        batch_size: Records per batch for progress logging
    """
    logger.info(f"Importing {len(records)} {model_class.__name__} records → {table_name}")

    for i, record in enumerate(records):
        # Validate and convert to dict
        if isinstance(record, dict):
            validated = model_class(**record)
        else:
            validated = record

        # Convert to dict (excludes pydantic metadata)
        data = validated.model_dump(exclude_none=True)

        # Use id field as record ID if present, else use table:uuid
        record_id = data.pop("id", None)

        await db.create(table_name, data, record_id=record_id)

        if (i + 1) % batch_size == 0:
            logger.info(f"  Imported {i + 1}/{len(records)} records")

    logger.info(f"Completed: {len(records)} records in {table_name}")

# Example usage with FastAPI/SQLAlchemy data
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UserModel(BaseModel):
    id: str
    name: str
    email: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    bio: Optional[str] = None

# Load from database or API
users = [
    UserModel(id="user:1", name="Alice", email="alice@example.com"),
    UserModel(id="user:2", name="Bob", email="bob@example.com"),
]

# Import
# await import_pydantic(db, "user", UserModel, users)
```

**Schema from Pydantic:**

```python
# Helper: generate DEFINE FIELD statements from Pydantic model
def pydantic_to_surrealdb_type(field_type: Type) -> str:
    """Convert Pydantic field type to SurrealDB type hint."""
    import typing

    origin = typing.get_origin(field_type)
    args = typing.get_args(field_type)

    # Handle Optional[X] → option<X>
    if origin is typing.Union:
        # Optional is Union[X, None]
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            inner = pydantic_to_surrealdb_type(non_none_args[0])
            return f"option<{inner}>"

    # Handle list[X] → array<X>
    if origin is list:
        inner = pydantic_to_surrealdb_type(args[0]) if args else "any"
        return f"array<{inner}>"

    # Scalar types
    mapping = {
        str: "string",
        int: "int",
        float: "float",
        bool: "bool",
        datetime: "datetime",
    }

    return mapping.get(field_type, "any")
```

---

## SQL / SQLAlchemy → SurrealDB

**When to use:** Migrating from PostgreSQL, MySQL, SQLite, or SQLAlchemy ORM.

**Type Mapping:**

| SQL Type | SurrealDB Type |
|---|---|
| VARCHAR, TEXT | string |
| INT, BIGINT | int |
| FLOAT, DECIMAL | float |
| BOOLEAN | bool |
| TIMESTAMP, DATETIME | datetime |
| UUID | string |
| ARRAY, JSON | array<type> or object |
| FOREIGN KEY (id) | record<table> |
| PRIMARY KEY | uses record ID |

**Python Pattern:**

```python
import asyncio
import sqlalchemy as sa
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from surrealdb import AsyncSurreal
import logging

logger = logging.getLogger(__name__)

async def import_sql(
    db: AsyncSurreal,
    sql_connection_string: str,
    table_names: list[str],
    batch_size: int = 100
):
    """Import tables from SQL database to SurrealDB.

    Args:
        db: AsyncSurreal connection
        sql_connection_string: SQLAlchemy connection string
            Examples:
            - "postgresql://user:pass@localhost/dbname"
            - "sqlite:///./data.db"
            - "mysql+pymysql://user:pass@localhost/dbname"
        table_names: List of table names to import
        batch_size: Records per batch
    """
    # Synchronous engine for introspection and data reading
    engine = create_engine(sql_connection_string)
    inspector = inspect(engine)

    for table_name in table_names:
        logger.info(f"Importing SQL table: {table_name}")

        # Read all rows (consider pagination for large tables)
        with engine.connect() as conn:
            rows = conn.execute(sa.text(f"SELECT * FROM {table_name}")).fetchall()

        if not rows:
            logger.warning(f"  {table_name} is empty")
            continue

        # Get column names
        columns = inspector.get_columns(table_name)
        column_names = [col["name"] for col in columns]

        for i, row in enumerate(rows):
            # Convert row to dict
            data = dict(zip(column_names, row))

            # Extract PK as record ID (assumes 'id' or 'id' field exists)
            pk_columns = inspector.get_pk_constraint(table_name)["constrained_columns"]
            record_id = None
            if pk_columns:
                if len(pk_columns) == 1:
                    pk_col = pk_columns[0]
                    record_id = f"{table_name}:{data[pk_col]}"
                    data.pop(pk_col, None)  # Remove from data to avoid duplication

            await db.create(table_name, data, record_id=record_id)

            if (i + 1) % batch_size == 0:
                logger.info(f"  Imported {i + 1}/{len(rows)} records")

        logger.info(f"Completed: {len(rows)} records in {table_name}")

# Example: migrate from SQLite
# await import_sql(
#     db,
#     "sqlite:///./myapp.db",
#     table_names=["users", "posts", "comments"]
# )
```

**Handling Foreign Keys:**

```python
async def map_foreign_keys(
    db: AsyncSurreal,
    foreign_key_map: dict
):
    """Update record references after initial import.

    Args:
        foreign_key_map: {
            "posts": {
                "author_id": "users"  # posts.author_id → users.{id}
            }
        }
    """
    for table, fks in foreign_key_map.items():
        for fk_field, fk_table in fks.items():
            logger.info(f"Mapping {table}.{fk_field} → {fk_table}")

            await db.query(f"""
                UPDATE {table} SET {fk_field} = {fk_table}:{fk_field};
            """)
```

---

## ChromaDB → SurrealDB

**When to use:** Migrating from ChromaDB vector collections.

**Pattern:**

```python
import asyncio
import chromadb
from surrealdb import AsyncSurreal
import logging

logger = logging.getLogger(__name__)

async def import_chromadb(
    db: AsyncSurreal,
    chroma_path: str,
    batch_size: int = 100
):
    """Import ChromaDB collections to SurrealDB vector tables.

    Args:
        db: AsyncSurreal connection
        chroma_path: Path to ChromaDB persistent data directory
        batch_size: Records per batch
    """
    # Load ChromaDB client
    client = chromadb.PersistentClient(path=chroma_path)

    for collection in client.list_collections():
        collection_name = collection.name
        logger.info(f"Importing ChromaDB collection: {collection_name}")

        # Get collection metadata (e.g., embedding dimension)
        metadata = collection.metadata or {}
        dimension = metadata.get("hnsw:space", "cosine")
        embedding_dim = metadata.get("dimension", 384)  # Default to 384

        # Create SurrealDB table with vector index
        logger.info(f"  Creating table {collection_name} with HNSW index (dim={embedding_dim})")

        await db.query(f"""
            DEFINE TABLE {collection_name} SCHEMAFULL;
            DEFINE FIELD content ON {collection_name} TYPE string;
            DEFINE FIELD embedding ON {collection_name} TYPE array<float>;
            DEFINE FIELD metadata ON {collection_name} TYPE option<object>;
            DEFINE INDEX idx_{collection_name}_embedding ON {collection_name}
                FIELDS embedding HNSW DIMENSION {embedding_dim} DIST COSINE TYPE F32;
        """)

        # Fetch all data from ChromaDB
        results = collection.get(include=["documents", "embeddings", "metadatas", "ids"])

        doc_ids = results.get("ids", [])
        documents = results.get("documents", [])
        embeddings = results.get("embeddings", [])
        metadatas = results.get("metadatas", [])

        # Import in batches
        total = len(doc_ids)
        for i, doc_id in enumerate(doc_ids):
            record = {
                "content": documents[i] or "",
                "embedding": embeddings[i] if embeddings else [],
                "metadata": metadatas[i] if metadatas else {}
            }

            await db.create(collection_name, record, record_id=f"{collection_name}:{doc_id}")

            if (i + 1) % batch_size == 0:
                logger.info(f"  Imported {i + 1}/{total} documents")

        logger.info(f"Completed: {total} documents in {collection_name}")

# Example usage
# await import_chromadb(db, "./chroma_data")
```

**Verify Vector Search:**

```surql
-- Test vector similarity after migration
-- Assumes: test_embedding is provided as parameter
SELECT id, vector::similarity::cosine(embedding, $test_embedding) AS score
FROM documents
WHERE embedding <|1|> $test_embedding
LIMIT 5;
```

---

## Batch Import Pattern

**Use this for large datasets (>100k records).**

```python
import asyncio
from typing import List, Dict, Any
from surrealdb import AsyncSurreal
import logging

logger = logging.getLogger(__name__)

async def batch_import(
    db: AsyncSurreal,
    table: str,
    records: List[Dict[str, Any]],
    batch_size: int = 100,
    progress_interval: int = 1000
):
    """Import records in batches with progress tracking.

    Args:
        db: AsyncSurreal connection
        table: Target table name
        records: List of records (dicts) to import
        batch_size: Number of records per batch (controls concurrency)
        progress_interval: Log progress every N records
    """
    total = len(records)
    logger.info(f"Starting batch import: {total} records → {table}")

    # Process in batches
    for batch_start in range(0, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        batch = records[batch_start:batch_end]

        # Import batch concurrently
        tasks = [
            db.create(table, record)
            for record in batch
        ]

        await asyncio.gather(*tasks)

        # Log progress
        if (batch_end % progress_interval == 0) or (batch_end == total):
            logger.info(f"Imported {batch_end}/{total} records ({100*batch_end//total}%)")

    logger.info(f"Batch import complete: {total} records in {table}")
```

---

## Validation Queries

**Run these after migration to verify data integrity.**

```surql
-- Count records per table
SELECT count() FROM company GROUP ALL;
SELECT count() FROM person GROUP ALL;
SELECT count() FROM relationship GROUP ALL;

-- Check for missing record links (NULL FK values)
SELECT id FROM person WHERE company == NONE;

-- Verify edges exist for relationships
SELECT count() FROM relationship WHERE in == NONE OR out == NONE;

-- Test vector search (if applicable)
SELECT id, vector::similarity::cosine(embedding, $test_vector) AS score
FROM documents
WHERE embedding <|5|> $test_vector;

-- Check unique constraints (duplicates)
SELECT email, count() as cnt FROM user GROUP BY email HAVING cnt > 1;

-- Sample data from each table
SELECT * FROM company LIMIT 3;
SELECT * FROM person LIMIT 3;

-- Verify relationship counts
SELECT -> as target, count() FROM relationship GROUP BY -> LIMIT 5;
```

---

## Rollback Procedure

```surql
-- Drop all tables in reverse dependency order
DROP TABLE likes;
DROP TABLE posts;
DROP TABLE users;

-- Or drop entire database
DROP DATABASE app;
DROP NAMESPACE migration;
```

**Python rollback helper:**

```python
async def rollback(db: AsyncSurreal, tables: list[str]):
    """Drop tables in reverse order (respecting dependencies)."""
    for table in reversed(tables):
        try:
            await db.query(f"DROP TABLE {table};")
            logger.info(f"Dropped table: {table}")
        except Exception as e:
            logger.error(f"Failed to drop {table}: {e}")
```

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|---|---|---|
| Import hangs | Batch size too large; timeout on connection | Reduce batch_size; increase connection timeout |
| FK references are NULL | Foreign keys not mapped after import | Use `map_foreign_keys()` before validation |
| Vector search returns no results | Embedding dimensions mismatch | Verify HNSW DIMENSION matches embedding size |
| Duplicate records | Record ID collision | Ensure unique IDs; use UUIDs or composite keys |
| Type mismatch (string vs int) | Source data inconsistency | Normalize types during import (convert to string) |
| Import timeout on large batch | Network/DB overload | Reduce batch_size; add retry logic |
| Memory exhaustion | Loading entire source into memory | Stream records; load in chunks from source |
