# SurrealDB Python SDK Reference

Patterns and examples for using the SurrealDB Python SDK (AsyncSurreal).

---

## Installation

```bash
pip install surrealdb
```

---

## Connection Patterns

### Embedded Database (File-Based)

Local SQLite-style database stored in a file.

```python
from surrealdb import AsyncSurreal

async with AsyncSurreal("file://./data.db") as db:
    await db.use("app", "main")  # namespace and database
    result = await db.query("SELECT * FROM person")
```

### Memory-Only Database

Temporary database useful for testing.

```python
async with AsyncSurreal("mem://") as db:
    await db.use("app", "main")
    # data is lost when connection closes
```

### Remote Server (WebSocket)

Connect to a remote SurrealDB server over the network.

```python
async with AsyncSurreal("ws://localhost:8000") as db:
    await db.signin({
        "username": "root",
        "password": "root"
    })
    await db.use("app", "main")
    result = await db.query("SELECT * FROM person")
```

### Remote Server (HTTPS)

Secure connection with HTTPS instead of WebSocket.

```python
async with AsyncSurreal("https://localhost:8000") as db:
    await db.signin({
        "username": "root",
        "password": "root"
    })
    await db.use("app", "main")
```

---

## CRUD Operations

### CREATE

Create a new record. Returns the created record(s).

```python
# Create with auto-generated ID
record = await db.create("person", {
    "name": "John",
    "age": 30,
    "email": "john@example.com"
})
# Returns: {"id": "person:xyz123", "name": "John", "age": 30, ...}

# Create with specific ID
record = await db.create("person:john", {
    "name": "John",
    "age": 30
})
# Returns: {"id": "person:john", "name": "John", ...}

# Batch create (returns list)
records = await db.create("person", [
    {"name": "Alice", "age": 28},
    {"name": "Bob", "age": 35}
])
# Returns: [{"id": "person:...", "name": "Alice", ...}, ...]
```

### SELECT

Fetch records from a table.

```python
# Select all from a table
people = await db.select("person")
# Returns: [{"id": "person:1", "name": "John", ...}, ...]

# Select specific record by ID
john = await db.select("person:john")
# Returns: {"id": "person:john", "name": "John", ...}

# Returns [] if record doesn't exist (no exception)
missing = await db.select("person:nonexistent")
# Returns: []
```

### UPDATE

Replace all fields of a record (non-null fields overwrite).

```python
# Update a specific record
await db.update("person:john", {
    "name": "John Doe",
    "age": 31
})

# Update specific records (batch)
await db.update("person", {
    "age": 18  # All persons get age=18 (use with caution)
})
```

### MERGE

Update only specific fields (partial update).

```python
# Update only the age field, keep other fields unchanged
await db.merge("person:john", {
    "age": 31
})

# Merge batch
await db.merge("person", {
    "updated_at": time.time()  # Update timestamp for all
})
```

### DELETE

Remove records from a table.

```python
# Delete a specific record
await db.delete("person:john")

# Delete all records in a table
await db.delete("person")
```

---

## Parameterized Queries

Always use parameterized queries to prevent injection and ensure type safety.

```python
# CORRECT: parameterized query
result = await db.query(
    "SELECT * FROM person WHERE age > $min_age AND name = $name",
    {
        "min_age": 25,
        "name": "John"
    }
)

# WRONG: string interpolation (never do this)
result = await db.query(
    f"SELECT * FROM person WHERE age > {min_age} AND name = '{name}'"
)
# Vulnerable to injection and loses type safety
```

### Understanding Query Results

Query results are a list of response objects. Each object contains status and result.

```python
result = await db.query(
    "SELECT * FROM person WHERE age > $age",
    {"age": 25}
)

# result is a list: [{"result": [...], "status": "OK", ...}, ...]
records = result[0]["result"]  # Extract actual data

# Empty result
records = result[0]["result"] if result and result[0]["result"] else []

# Multiple queries in one call
result = await db.query(
    "SELECT COUNT() FROM person; SELECT * FROM person LIMIT 1;",
    {}
)
# result[0] = count result
# result[1] = limit result
```

---

## Graph Traversal

Navigate relationships using traversal queries.

```python
# Outgoing traversal (alice -> manages -> person)
result = await db.query(
    "SELECT ->manages->person FROM person:alice",
    {}
)
reports = result[0]["result"]  # List of persons alice manages

# Incoming traversal (person <- manages <- alice)
result = await db.query(
    "SELECT <-manages<-person FROM person:bob",
    {}
)
managers = result[0]["result"]

# Chained traversal (alice -> manages -> person -> works_at -> company)
result = await db.query(
    """
    SELECT ->manages->person->works_at->company
    FROM person:alice
    """,
    {}
)
companies = result[0]["result"]

# Destructuring within traversal
result = await db.query(
    """
    SELECT {
        name,
        email,
        reports: ->manages->person.{ name, email }
    }
    FROM person:alice
    """,
    {}
)
```

### Creating Edges (RELATE)

Create relationships between records.

```python
# Simple edge (no properties)
await db.query(
    "RELATE person:alice->manages->person:bob",
    {}
)

# Edge with properties
await db.query(
    """
    RELATE person:alice->manages->person:bob
    SET since = $start_date, level = $level
    """,
    {
        "start_date": "2024-01-01",
        "level": "senior"
    }
)

# Batch edges
await db.query(
    """
    RELATE person:alice->manages->person:bob,
           person:alice->manages->person:carol,
           person:alice->manages->person:dave
    """,
    {}
)
```

---

## Filtering and Complex Queries

Use parameterized WHERE clauses.

```python
# Filter with comparison operators
result = await db.query(
    "SELECT * FROM person WHERE age > $min_age AND city = $city",
    {"min_age": 25, "city": "NYC"}
)

# String matching
result = await db.query(
    "SELECT * FROM person WHERE name CONTAINS $search",
    {"search": "john"}
)

# Array operations
result = await db.query(
    "SELECT * FROM person WHERE $skill IN skills",
    {"skill": "python"}
)

# Sorting and limiting
result = await db.query(
    "SELECT * FROM person ORDER BY age DESC LIMIT $limit",
    {"limit": 10}
)

# Pagination
result = await db.query(
    "SELECT * FROM person LIMIT $limit START $offset",
    {"limit": 10, "offset": 20}
)
```

---

## Subqueries & LET Bindings

Use variables for complex queries.

```python
# LET binding with subquery
result = await db.query(
    """
    LET $active_users = SELECT id FROM user WHERE active = true;
    SELECT * FROM post WHERE author IN $active_users;
    """,
    {}
)
posts = result[1]["result"]  # Second query result

# Parameterized subquery
result = await db.query(
    """
    LET $threshold = $min_value;
    SELECT * FROM order WHERE total > $threshold;
    """,
    {"min_value": 1000}
)

# Nested computation
result = await db.query(
    """
    SELECT id, name, post_count: (
        SELECT COUNT() FROM post WHERE author = $this
    )
    FROM person;
    """,
    {}
)
```

---

## Transactions

Execute multiple operations atomically.

```python
# Simple transaction
result = await db.query(
    """
    BEGIN;
    CREATE order:new SET total = $total, customer = person:alice;
    RELATE customer:alice->placed->order:new;
    UPDATE customer:alice SET order_count += 1;
    COMMIT;
    """,
    {"total": 500}
)

# Transaction with LET binding
result = await db.query(
    """
    BEGIN;
    LET $order = CREATE order SET total = $amount;
    CREATE payment SET order = $order.id, amount = $amount, status = "pending";
    UPDATE customer:alice MERGE { last_order: $order.id };
    COMMIT;
    """,
    {"amount": 250}
)
```

---

## Error Handling

Catch and handle SurrealDB exceptions.

```python
from surrealdb import SurrealException

try:
    result = await db.query(
        "SELECT * FROM nonexistent_table",
        {}
    )
except SurrealException as e:
    print(f"Query failed: {e}")
    # Handle error (log, retry, return default, etc.)
    return []

# Connection errors
try:
    async with AsyncSurreal("ws://localhost:8000") as db:
        await db.signin({"username": "root", "password": "wrong"})
except SurrealException as e:
    print(f"Authentication failed: {e}")
```

---

## Common Patterns

### Batch Create with Validation

```python
async def create_people(db: AsyncSurreal, people_data: list[dict]) -> list[dict]:
    """Create multiple people, returning created records."""
    try:
        result = await db.create("person", people_data)
        return result if isinstance(result, list) else [result]
    except SurrealException as e:
        print(f"Batch create failed: {e}")
        return []
```

### Query with Retry Logic

```python
import asyncio

async def query_with_retry(
    db: AsyncSurreal,
    query: str,
    params: dict,
    max_retries: int = 3
) -> list:
    """Execute query with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            result = await db.query(query, params)
            return result[0]["result"] if result else []
        except SurrealException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # exponential backoff
            print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)
```

### Fetch with Default

```python
async def get_person_or_default(
    db: AsyncSurreal,
    person_id: str
) -> dict:
    """Fetch person, return default if not found."""
    result = await db.select(f"person:{person_id}")
    if result:
        return result
    return {
        "id": f"person:{person_id}",
        "name": "Unknown",
        "age": None
    }
```

### Bulk Update with Verification

```python
async def bulk_update_verified(
    db: AsyncSurreal,
    table: str,
    updates: dict,
    condition: str,
    params: dict
) -> int:
    """Update with condition, return count of affected records."""
    # First, count matching records
    count_result = await db.query(
        f"SELECT COUNT() FROM {table} WHERE {condition}",
        params
    )
    count = count_result[0]["result"][0]["count"] if count_result[0]["result"] else 0

    if count == 0:
        print(f"No records match condition for {table}")
        return 0

    # Perform update
    await db.query(
        f"UPDATE {table} MERGE $updates WHERE {condition}",
        {**params, "updates": updates}
    )

    return count
```

---

## Context Manager Pattern

Always use async context manager for safe connection handling.

```python
# Safe pattern
async with AsyncSurreal("file://./data.db") as db:
    await db.use("app", "main")
    result = await db.query("SELECT * FROM person")
    # Connection automatically closed

# Avoid: manual connection (not recommended)
db = AsyncSurreal("file://./data.db")
# ... need to manually close
```

---

## Type Hints for Type Safety

Use type hints in async functions.

```python
from typing import Optional

async def fetch_person(
    db: AsyncSurreal,
    person_id: str
) -> Optional[dict]:
    """Fetch a person record, return None if not found."""
    result = await db.select(f"person:{person_id}")
    return result if result else None

async def create_post(
    db: AsyncSurreal,
    title: str,
    content: str,
    author_id: str
) -> dict:
    """Create a post, return created record."""
    return await db.create("post", {
        "title": title,
        "content": content,
        "author": f"person:{author_id}"
    })
```

