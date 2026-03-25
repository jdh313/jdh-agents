# SurrealQL Syntax Cheatsheet

Comprehensive reference for common SurrealQL patterns. Use this alongside official docs
for the latest syntax.

---

## CRUD Operations

### CREATE

Create a new record. Returns the created record with auto-generated ID.

```surql
-- Create with auto-generated ID
CREATE person SET name = "John", age = 30, email = "john@example.com";

-- Create with specific ID
CREATE person:john SET name = "John", age = 30;

-- Create with return clause
CREATE person:alice SET name = "Alice", age = 28 RETURN id, name;

-- Create with multiple records at once
CREATE person:bob, person:carol SET age = 25;
```

### SELECT

Fetch records from a table with optional filtering and sorting.

```surql
-- Select all from a table
SELECT * FROM person;

-- Select specific record by ID
SELECT * FROM person:john;

-- Select specific fields
SELECT name, age, email FROM person;

-- With WHERE clause
SELECT * FROM person WHERE age > 25;
SELECT * FROM person WHERE age > 25 AND city = "NYC";
SELECT * FROM person WHERE name CONTAINS "john";

-- With ORDER BY and LIMIT
SELECT * FROM person ORDER BY age DESC LIMIT 10;
SELECT * FROM person ORDER BY created_at DESC LIMIT 10 START 20;  -- pagination

-- With GROUP BY and aggregate functions
SELECT name, COUNT() AS count FROM person GROUP BY name;
SELECT department, AVG(salary) AS avg_salary FROM employee GROUP BY department;

-- Destructuring: fetch nested record links
SELECT { name, email, manager: { name AS manager_name } } FROM person;
```

### UPDATE

Modify existing records. Use UPDATE (replace all fields) or MERGE (update specific fields).

```surql
-- Replace all fields
UPDATE person:john SET name = "John Doe", age = 31;

-- Update specific fields (MERGE)
UPDATE person:john MERGE { age: 31, email: "john.doe@example.com" };

-- Update with WHERE clause
UPDATE person SET age += 1 WHERE age < 30;

-- Update record links
UPDATE post:post1 MERGE { author: person:alice };

-- Return updated record
UPDATE person:john SET age = 31 RETURN *;
```

### DELETE

Remove records from a table.

```surql
-- Delete specific record
DELETE person:john;

-- Delete with WHERE clause
DELETE person WHERE age < 18;
DELETE post WHERE author = person:alice;

-- Delete all (use with caution)
DELETE person;
```

---

## Graph Traversal

Navigate relationships between records using edge notation.

### Basic Traversal

```surql
-- Outgoing: traverse edges starting from a record
SELECT ->manages->person FROM person:alice;
-- Returns: all persons that alice manages

-- Incoming: traverse edges pointing to a record
SELECT <-manages<-person FROM person:bob;
-- Returns: all persons who manage bob (bob's managers)

-- Bidirectional: traverse both directions
SELECT <->manages<->person FROM person:alice;
-- Returns: people alice manages AND people who manage alice
```

### Chained Traversal (Multiple Levels)

```surql
-- 2-level traversal
SELECT ->manages->person->works_at->company FROM person:alice;
-- Returns: companies where alice's reports work

-- 3-level traversal
SELECT ->likes->post<-likes<-person->follows->person FROM person:alice;
-- Complex: persons who like posts that alice likes, whose posts are liked by people who follow alice

-- With nested selection
SELECT ->manages->person.{ name, email, team: ->works_at->company.name }
FROM person:alice;
-- Nested destructuring within traversal
```

### RELATE: Create Edges

Create relationship edges with properties.

```surql
-- Simple edge (no properties)
RELATE person:alice->manages->person:bob;

-- Edge with properties
RELATE person:alice->manages->person:bob SET since = "2024-01-01", level = "senior";

-- Edge with return
RELATE person:alice->manages->person:bob SET since = "2024-01-01" RETURN *;

-- Multiple edges at once
RELATE person:alice->manages->person:bob, person:alice->manages->person:carol;
```

### Deleting Edges

```surql
-- Delete a specific edge
DELETE person:alice->manages->person:bob;

-- Delete all outgoing edges of a type
DELETE person:alice->manages;

-- Delete all edges (any type)
DELETE person:alice->;
```

---

## Filtering & Operators

### Comparison Operators

```surql
WHERE age = 30           -- equals
WHERE age != 25          -- not equals
WHERE age > 25           -- greater than
WHERE age < 50           -- less than
WHERE age >= 18          -- greater than or equal
WHERE age <= 65          -- less than or equal

WHERE age > 25 AND city = "NYC"      -- AND logic
WHERE age > 25 OR city = "LA"        -- OR logic
WHERE NOT (age < 18)                 -- NOT logic
WHERE (age > 25 AND city = "NYC") OR income > 100000  -- complex boolean
```

### String Matching

```surql
WHERE name CONTAINS "john"           -- substring match (case-sensitive)
WHERE name ~ /^J.*/                  -- regex pattern match
WHERE string::lowercase(name) = "alice"  -- compare after transformation

-- Full-text search (requires FTS index)
SELECT * FROM post WHERE post @@ "cloud native";
```

### Array Operations

```surql
WHERE "python" IN skills             -- element in array
WHERE "python" NOT IN skills         -- element not in array
WHERE array::len(skills) > 3         -- array length
WHERE "admin" IN roles AND "verified" IN verified_badges  -- multiple arrays

-- Array filtering
SELECT skills[WHERE @@ "python"] FROM developer;  -- fetch only python skills
```

### Record Link Filtering

Query record links directly.

```surql
-- Filter by linked record field
WHERE author.name = "Alice"

-- Filter by linked record ID
WHERE author = person:alice

-- Exists check (record link is set)
WHERE author IS NOT NONE

-- Fetch linked record details
SELECT *, author.{ name, email } FROM post;
```

### Null/None Checks

```surql
WHERE email IS NOT NONE               -- field is set
WHERE email IS NONE                   -- field is not set
WHERE email != NONE                   -- equivalent to IS NOT NONE
```

### Type Checking

```surql
WHERE type::is::string(field)         -- is field a string?
WHERE type::is::number(field)         -- is field numeric?
WHERE type::is::array(field)          -- is field an array?
WHERE type::is::record(field)         -- is field a record link?
WHERE type::is::object(field)         -- is field an object?
```

---

## Common Functions

### String Functions

```surql
string::concat(first, ' ', last)      -- concatenate strings
string::len(name)                      -- string length
string::lowercase(name)                -- convert to lowercase
string::uppercase(name)                -- convert to uppercase
string::trim(name)                     -- trim whitespace
string::starts_with(email, "admin")    -- check prefix
string::ends_with(email, "@example.com")  -- check suffix
string::split(tags, ",")               -- split into array
string::is::email(email)               -- validate email format
string::is::uuid(id)                   -- validate UUID format
string::is::numeric(value)             -- check if numeric string
```

### Array Functions

```surql
array::len(items)                      -- array length
array::add(items, "new_item")          -- append element
array::distinct(tags)                  -- remove duplicates
array::flatten(nested)                 -- flatten nested arrays
array::reverse(items)                  -- reverse order
array::sort(scores)                    -- sort array
array::contains(items, "apple")        -- check if contains element
array::intersect(a, b)                 -- intersection of two arrays
array::union(a, b)                     -- union of two arrays
```

### Math Functions

```surql
math::sum(values)                      -- sum of array
math::mean(scores)                     -- average
math::min(values)                      -- minimum
math::max(values)                      -- maximum
math::round(3.14159, 2)                -- round to N decimals
math::abs(-5)                          -- absolute value
math::sqrt(16)                         -- square root
math::ceil(3.2)                        -- round up
math::floor(3.8)                       -- round down
```

### Aggregate Functions (use in SELECT)

```surql
COUNT()                                -- count records
SUM(field)                             -- sum of field values
AVG(field)                             -- average of field values
MIN(field)                             -- minimum field value
MAX(field)                             -- maximum field value
GROUP_CONCAT(field)                    -- concatenate field values
```

### Time Functions

```surql
time::now()                            -- current timestamp (RFC 3339)
time::year(date)                       -- extract year
time::month(date)                      -- extract month
time::day(date)                        -- extract day
time::hour(date)                       -- extract hour
time::minute(date)                     -- extract minute
time::second(date)                     -- extract second
time::format(date, "%Y-%m-%d")         -- format as string
time::format(date, "%Y-%m-%d %H:%M:%S")  -- datetime format
```

### Type Functions

```surql
type::is::string(value)                -- check if string
type::is::number(value)                -- check if number
type::is::bool(value)                  -- check if boolean
type::is::array(value)                 -- check if array
type::is::object(value)                -- check if object
type::is::record(value)                -- check if record link
type::is::null(value)                  -- check if null/none
type::of(value)                        -- get type name as string
```

### Vector Functions (for embeddings)

```surql
-- Vector distance for similarity search
vector::distance::euclidean(a, b)      -- Euclidean distance
vector::distance::cosine(a, b)         -- Cosine distance
vector::distance::manhattan(a, b)      -- Manhattan distance

-- KNN similarity search (requires HNSW index)
SELECT id, embedding, vector::distance::cosine(embedding, $query_embedding) AS dist
FROM documents
WHERE embedding <|5|> $query_embedding   -- fetch 5 nearest neighbors
ORDER BY dist LIMIT 5;
```

---

## Subqueries & LET Bindings

Use LET to define variables and subqueries.

```surql
-- Define variable for reuse
LET $active_users = SELECT id FROM user WHERE active = true;
SELECT * FROM post WHERE author IN $active_users;

-- Multiple LET bindings
LET $threshold = 1000;
LET $premium_users = SELECT id FROM user WHERE revenue > $threshold;
SELECT * FROM order WHERE customer IN $premium_users;

-- Nested subquery in SELECT
SELECT id, name, post_count: (SELECT COUNT() FROM post WHERE author = $this)
FROM person;

-- Subquery with parameters
SELECT *
FROM post
WHERE author IN (SELECT id FROM user WHERE created_at > $start_date);
```

---

## Transactions

Group multiple operations into atomic transactions.

```surql
-- Simple transaction
BEGIN;
CREATE order:123 SET total = 100, customer = person:alice;
RELATE customer:alice->placed->order:123;
UPDATE customer:alice SET order_count += 1;
COMMIT;

-- Rollback on error (manual)
BEGIN;
CREATE invoice SET total = 50;
-- If this fails, manually CANCEL instead of COMMIT
CANCEL;

-- Nested updates within transaction
BEGIN;
LET $order = CREATE order:new SET total = 500;
CREATE payment SET order = $order.id, amount = 500;
UPDATE customer:alice MERGE { last_order: $order.id };
COMMIT;
```

---

## Schema Inspection

Query the database schema and metadata.

```surql
-- List all tables
INFO FOR DB;

-- Table details (fields, indices, events)
INFO FOR TABLE person;

-- Field details
INFO FOR FIELD name ON person;

-- Index details
INFO FOR INDEX idx_person_email ON person;
```

---

## Vector Search (Embeddings)

Semantic similarity search using vector embeddings.

```surql
-- KNN search with distance
SELECT id, name, embedding, vector::distance::cosine(embedding, $query_vector) AS dist
FROM documents
WHERE embedding <|10|> $query_vector   -- fetch 10 nearest neighbors
ORDER BY dist LIMIT 10;

-- With filtering
SELECT id, name
FROM documents
WHERE embedding <|10|> $query_vector
AND category = "news"
ORDER BY dist LIMIT 5;

-- Multiple distance metrics
-- Cosine (recommended for embeddings): <|N|>
-- Euclidean: <|[N]>
-- Manhattan: <|{N}>
```

---

## Advanced Patterns

### Computed Fields (in SELECT)

```surql
SELECT id, name, email: string::concat(first, "@example.com") FROM person;
SELECT id, name, age_group: CASE WHEN age < 18 THEN "minor" ELSE "adult" END FROM person;
```

### CASE Expressions

```surql
SELECT
  id,
  name,
  status: CASE
    WHEN age < 18 THEN "minor"
    WHEN age < 65 THEN "adult"
    ELSE "senior"
  END
FROM person;
```

### Distinct Results

```surql
SELECT DISTINCT city FROM person;
SELECT DISTINCT category, COUNT() FROM product GROUP BY category;
```

### LIMIT and OFFSET (Pagination)

```surql
-- Fetch 10 records starting at position 0
SELECT * FROM person LIMIT 10;

-- Fetch 10 records starting at position 20
SELECT * FROM person LIMIT 10 START 20;

-- Alternative syntax (OFFSET)
SELECT * FROM person LIMIT 10 OFFSET 20;
```

