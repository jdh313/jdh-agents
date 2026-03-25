# SurrealDB: Graph Model

## When to Use

Use the graph model when:
- Entities are connected and you follow those connections in queries
- Relationships have their own metadata (dates, weights, roles)
- You answer questions like "find all X connected to Y through Z"
- You would otherwise write a multi-table JOIN in SQL
- The domain has hierarchies, org charts, networks, or chains of ownership

SurrealDB's graph model eliminates JOINs entirely. Instead of joining tables at
query time, you follow pre-computed links stored in the records themselves.

---

## Record Links (Direct References)

A record link is a field whose value is a record ID. The link is stored in the
record and resolved on traversal — no JOIN required.

```surql
DEFINE TABLE role SCHEMAFULL;
DEFINE FIELD title   ON role TYPE string;
DEFINE FIELD company ON role TYPE record<company>;  -- direct reference

-- Create with a link
CREATE role:acme_senior SET
    title = "Senior Engineer",
    company = company:acme;

-- Traverse the link in a query (dot notation)
SELECT title, company.name, company.industry FROM role;

-- Returns:
-- { title: "Senior Engineer", company: { name: "Acme Corp", industry: "Tech" } }
```

Record links are the right choice when:
- The relationship is one-to-one or many-to-one
- No metadata on the relationship itself
- You access the related record frequently as part of the parent

---

## RELATE: Edge Records with Metadata

Use `RELATE` when the relationship itself carries data (dates, weights, roles)
or when you need to query the relationship independently.

```surql
-- Relate accomplishment to skill with edge metadata
RELATE accomplishment:abc->demonstrates->skill:python
    SET proficiency = "advanced",
        years_experience = 3,
        last_used = time::now();

-- The edge record is stored in a table named "demonstrates"
-- It has: in (accomplishment:abc), out (skill:python), plus any SET fields

-- Query: what skills does this accomplishment demonstrate?
SELECT ->demonstrates->skill.name AS skills FROM accomplishment:abc;

-- Query: which accomplishments demonstrate Python at advanced level?
SELECT <-demonstrates[WHERE proficiency = "advanced"]<-accomplishment.*
FROM skill:python;

-- Query: find all skills across all accomplishments in a given role
SELECT ->demonstrates->skill.name AS skills
FROM accomplishment
WHERE role = role:acme_senior;
```

RELATE is the right choice when:
- The relationship has metadata (proficiency, dates, weight)
- You query the relationship itself
- Many-to-many with non-trivial edge data

---

## Traversal Syntax

| Operator | Direction | Meaning |
|----------|-----------|---------|
| `->relation->table` | Outgoing | Follow edge FROM current record TO related |
| `<-relation<-table` | Incoming | Follow edge TO current record FROM related |
| `<->relation<->table` | Bidirectional | Follow edge in either direction |

Traversals can be chained:

```surql
-- Company → Roles → Accomplishments → Skills
SELECT ->role->accomplishment->demonstrates->skill.name AS all_skills
FROM company:acme;

-- Find all companies where accomplishments demonstrate Python
SELECT <-accomplishment<-role<-company.name AS companies
FROM skill:python;
```

---

## Computed Graph Fields

Define a virtual field on a table that automatically computes a graph traversal:

```surql
-- Add a computed "employers" field to person that lists company names
DEFINE FIELD employers ON person
    VALUE SELECT VALUE <-employs<-company.name FROM ONLY $this;

-- Now every person record includes employers without a separate query
SELECT name, employers FROM person:alice;
-- Returns: { name: "Alice", employers: ["Acme Corp", "Globex"] }
```

Computed fields are recalculated on every read. Use them for frequently-accessed
derived data that would otherwise require a separate query.

---

## Destructuring: Selective Field Extraction

Fetch specific fields from a graph traversal result without selecting the full record:

```surql
-- Fetch person with only name + linked company names
SELECT user:alice.{
    name,
    companies: ->worked_at->company.name
};
```

---

## Example: Company → Role → Accomplishment Chain

This is the resift domain modeled as a graph:

```surql
-- Tables
DEFINE TABLE company SCHEMAFULL;
DEFINE FIELD name     ON company TYPE string ASSERT $value != NONE;
DEFINE FIELD industry ON company TYPE string;

DEFINE TABLE role SCHEMAFULL;
DEFINE FIELD title   ON role TYPE string ASSERT $value != NONE;
DEFINE FIELD company ON role TYPE record<company>;  -- record link
DEFINE FIELD start   ON role TYPE datetime;
DEFINE FIELD end     ON role TYPE option<datetime>;

DEFINE TABLE accomplishment SCHEMALESS;
DEFINE FIELD description ON accomplishment TYPE string;
DEFINE FIELD role        ON accomplishment TYPE record<role>;  -- record link

DEFINE TABLE skill SCHEMAFULL;
DEFINE FIELD name     ON skill TYPE string ASSERT $value != NONE;
DEFINE FIELD category ON skill TYPE string;

-- Edge table for accomplishment → skill (many-to-many with metadata)
DEFINE TABLE demonstrates SCHEMAFULL;
DEFINE FIELD in          ON demonstrates TYPE record<accomplishment>;
DEFINE FIELD out         ON demonstrates TYPE record<skill>;
DEFINE FIELD proficiency ON demonstrates TYPE option<string>;

-- Insert data
CREATE company:acme SET name = "Acme Corp", industry = "Technology";
CREATE role:acme_sr SET title = "Senior Engineer", company = company:acme,
    start = d"2021-01-01";
CREATE accomplishment:ab123 SET
    description = "Reduced API latency by 40% with caching layer",
    role = role:acme_sr;
CREATE skill:python SET name = "Python", category = "programming";
RELATE accomplishment:ab123->demonstrates->skill:python
    SET proficiency = "advanced";

-- Traversal: all skills used at Acme
SELECT ->role->accomplishment->demonstrates->skill.name AS skills
FROM company:acme;

-- Traversal: all accomplishments demonstrating Python
SELECT <-demonstrates<-accomplishment.description
FROM skill:python;
```

---

## Record Links vs. RELATE: Decision Guide

| Criterion | Record Link | RELATE |
|-----------|-------------|--------|
| Relationship cardinality | Many-to-one or one-to-one | Many-to-many |
| Edge metadata needed | No | Yes |
| Query the edge itself | No | Yes |
| Traversal depth | One hop, direct | Chained, multi-hop |
| Example | `role.company` | `accomplishment->demonstrates->skill` |

---

## Anti-Patterns

- **Writing JOINs when graph traversal exists.** If you find yourself doing
  `SELECT * FROM role WHERE id IN (SELECT role FROM accomplishment WHERE ...)`,
  use graph traversal instead.

- **Using RELATE for one-to-one or many-to-one relationships.** A record link
  field is simpler and faster than a RELATE edge when the relationship is direct
  and has no metadata.

- **Unbounded traversal without LIMIT.** Chained traversals (`->a->b->c->d`) can
  fan out exponentially on large datasets. Always add `LIMIT` and filter early.

---

## When NOT to Use

- When you have no relationships between entities — use document or relational
- When all access is by direct record ID — use key-value
- When the "relationship" is just a foreign key with no traversal queries — use a
  relational record link field, not RELATE
- When graph depth is always exactly one hop — a record link field is sufficient
