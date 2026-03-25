---
name: surrealdb:query
description: >-
  Use when the user says "/sdb:query", "write a SurrealQL query", "help with SurrealQL",
  "debug this query", "SurrealQL syntax", "how do I query SurrealDB", "convert SQL
  to SurrealQL", or when writing, debugging, or explaining SurrealQL queries. Helps
  write correct SurrealQL, generates equivalent Python SDK code, and explains query
  execution for complex traversals.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Write
  - AskUserQuestion
---

# /sdb:query -- SurrealQL Query Writer & Debugger

Writes, fixes, and explains SurrealQL queries. Handles CRUD operations, graph traversal,
filtering, subqueries, transactions, and vector search. Generates equivalent Python SDK code
with parameterized queries and error handling.

Read `references/surql-cheatsheet.md` for syntax patterns. Load `references/python-sdk.md`
when generating Python code.

---

## Flow

Execute these steps in order. Do not skip or combine steps unless the user explicitly asks
for a faster pass.

### Step 1: Determine Intent

Identify what the user is trying to do. Ask a focused question if unclear.

**If writing a new query:**
Ask: "What data do you need to fetch? What table(s) and filters?"

**If debugging a failing query:**
Ask: "What's the error message? Can you paste the query?"

**If converting from SQL:**
Ask: "Paste the SQL query — I'll convert it to SurrealQL."

**If explaining a query:**
Ask: "Paste the SurrealQL — I'll walk through what it does."

After one user response, proceed — do not wait for exhaustive details.

---

### Step 2: Load References

Load the appropriate reference file(s) into context:
- `references/surql-cheatsheet.md` — syntax for all operations
- `references/python-sdk.md` — SDK patterns and examples

---

### Step 3: Write or Fix the Query

Produce the SurrealQL query with these principles:

**For new queries:**
1. Start with the simplest form (SELECT FROM table WHERE ...)
2. Add filters, ordering, and limits
3. Add graph traversal if needed
4. Nest subqueries if the query is complex

**For fixing broken queries:**
1. Identify the error (syntax, missing table, wrong field name, etc.)
2. Show the corrected query
3. Explain what was wrong and why the fix works

**For SQL-to-SurrealQL conversion:**
1. Identify the core structure (SELECT / WHERE / ORDER BY / LIMIT)
2. Map SQL constructs to SurrealQL:
   - INNER JOIN → graph traversal (->edge->)
   - LEFT JOIN → with COALESCE for missing data
   - GROUP BY / aggregate → SurrealQL group syntax
   - Subqueries → LET bindings or nested SELECT
3. Explain key differences (SurrealDB is document-oriented, not relational)

**Present the query in a code block with SurrealQL syntax highlighting:**

```surql
SELECT * FROM person WHERE age > 25 ORDER BY name LIMIT 10;
```

Ask: "Does this match what you need?"

---

### Step 4: Explain (If Complex)

For graph traversals, subqueries, or queries the user might not understand, explain:

**Graph traversal explanation template:**
- What edge is being traversed (->manages->, <-manages<-, etc.)
- Direction (outgoing, incoming, or chained)
- What data is returned (target records, computed fields, etc.)
- Performance note (indices used if applicable)

**Example:**
```surql
SELECT ->manages->person FROM person:alice;
```

This traverses outgoing **manages** edges from alice, fetching the managed persons.
If alice manages 3 people, you get 3 records.

---

### Step 5: Generate Python SDK Code

Provide equivalent Python code using AsyncSurreal. Load `references/python-sdk.md` for patterns.

**Key principles:**
- Use parameterized queries (never f-strings or string concatenation)
- Include error handling with try/except SurrealException
- Show connection setup (embedded or remote)
- Explain result structure (result[0]["result"] contains records)

**Template:**

```python
from surrealdb import AsyncSurreal, SurrealException

async def fetch_people_over_age(db: AsyncSurreal, min_age: int):
    try:
        result = await db.query(
            "SELECT * FROM person WHERE age > $min_age ORDER BY name",
            {"min_age": min_age}
        )
        return result[0]["result"] if result else []
    except SurrealException as e:
        print(f"Query failed: {e}")
        return []
```

Ask: "Does this code work for your use case?"

---

### Step 6: Offer Next Steps

After the user confirms the query works, offer:

```
Next steps:
- /sdb:schema   -- design or update the schema this query uses
- /sdb:model    -- revisit data model if query structure isn't right
- Paste output + ask for filtering/sorting help
```

---

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| User pastes broken SQL or pseudo-code | Ask for clarification or show typical SurrealQL pattern for that use case |
| Query returns empty results | Help diagnose: "Try SELECT * FROM [table] first — does the table exist? Check field names match schema." |
| Nested graph traversal (3+ levels) | Explain the traversal step-by-step; consider whether a subquery or LET binding is clearer |
| Combining vector search with graph traversal | Show vector similarity + filtering example; explain index requirements |
| Subqueries and LET bindings | Explain variable scoping and how LET creates a local binding |
| Transactions (BEGIN/COMMIT) | Explain atomicity; show when transactions are needed (multi-step changes) |
| Batch operations | Suggest looping over results vs. RELATE for creating multiple edges |
| Performance concerns | Note which filters should be indexed; explain index usage |
| Type mismatches | If query compares string to number, show type coercion or explicit casting |

---

## What This Skill Does NOT Do

- Write application code beyond query examples (use your app framework)
- Design the schema (use /sdb:schema for that)
- Populate data (use INSERT or CREATE; that's your responsibility)
- Execute queries (you run the query yourself; we just write it)
- Optimize existing slow queries without seeing performance data
- Enforce naming conventions (that's your project choice)
- Decide data model (use /sdb:model first if uncertain)

