# SurrealDB Model Decision Tree

Use this reference when analyzing a domain entity or relationship to determine
which SurrealDB data model(s) to apply. Models are NOT mutually exclusive — a
single table often combines two or three.

---

## Quick Reference: Model Selection Matrix

| Question | Yes → | No → |
|----------|-------|------|
| Does it have relationships you need to traverse (follow links between records)? | Graph | Continue |
| Is the structure flexible, variable, or unknown in advance? | Document | Continue |
| Does it need strict typing, validation, or referential integrity? | Relational | Continue |
| Does it store vector embeddings for similarity/semantic search? | Vector | Continue |
| Is it primarily timestamped event data (logs, metrics, history)? | Time-series | Continue |
| Is it a simple lookup by ID with no complex query needs? | Key-value | Continue |
| Does it store latitude/longitude, geometry, or area data? | Geospatial | Continue |
| Does it need full-text keyword search? | Full-text search | Continue |
| None of the above | Document (default) | — |

Apply this matrix per entity. If multiple questions answer "Yes", combine models.

---

## Model Descriptions (Summary)

### Graph

Entity relationships that you traverse in queries. Use when:
- You follow links between records (`->`, `<-`, `<->`)
- Relationships have their own metadata (use RELATE with edge records)
- You answer queries like "find all skills demonstrated across roles at a company"

Mechanism: Record links (`role: role:acme_engineer`) or RELATE edges
(`RELATE accomplishment:abc->demonstrates->skill:python`).

### Document

Flexible, variable-structure records. Use when:
- Fields differ between records of the same type
- Schema evolves frequently during development
- Nested objects are deep and non-uniform (e.g., job posting requirements)

Mechanism: `DEFINE TABLE t SCHEMALESS` — any field accepted without declaration.

### Relational

Strict, validated records with known schema. Use when:
- All fields and types are known and stable
- Data integrity matters (required fields, validated formats)
- Records are canonical reference data (e.g., skill names, company records)

Mechanism: `DEFINE TABLE t SCHEMAFULL` + `DEFINE FIELD f ON t TYPE ...`

### Vector

Embedding storage and similarity search. Use when:
- Records have an embedding field (array of floats)
- You query "find K nearest records to this embedding"
- Semantic similarity (not just keyword) search is needed

Mechanism: `DEFINE INDEX ... HNSW DIMENSION N DIST COSINE TYPE F32`

### Time-series

Event or metric data keyed on time. Use when:
- Records represent events, state changes, or audit entries
- You query by time range or aggregate over time windows
- Records are append-only (rarely updated)

Mechanism: `datetime` fields with indices; time-bucketing in queries.

### Key-value

Direct ID lookups with minimal query needs. Use when:
- You always access records by their exact ID
- No filtering, sorting, or joining is needed
- Records are ephemeral (sessions, caches, feature flags)

Mechanism: `SELECT * FROM config:app_settings` — no WHERE clause needed.

### Geospatial

Location or geometry data. Use when:
- Records have lat/lon, polygons, or other geometry
- You query by proximity (`geo::distance`) or containment
- Maps or physical location is part of the domain

Mechanism: `geometry` type + `DEFINE INDEX ... MTREE` for spatial queries.

### Full-text Search

Keyword search within text fields. Use when:
- Users search by words or phrases (not meaning)
- You need result scoring and highlighting
- Keyword matching complements or replaces vector search

Mechanism: `DEFINE INDEX ... SEARCH ANALYZER ... BM25`

---

## Combination Patterns

These combinations appear frequently in real domains. Recognize them early.

| Pattern | Models Combined | Example |
|---------|----------------|---------|
| Typed entity with links | Relational + Graph | `role` with `company: record<company>` field |
| Flexible entity with links | Document + Graph | `accomplishment` with `role: record<role>` field |
| Semantic search record | Document + Vector | Job posting with `embedding` field and HNSW index |
| Search + semantic | Full-text + Vector | Job posting with both SEARCH and HNSW index |
| Audit log | Relational + Time-series | `application_event` with `created_at` and typed status |
| Location entity | Relational + Geospatial | `office` with typed fields + `location: geometry` |
| Relationship with metadata | Graph (RELATE) | `demonstrates` edge with `proficiency` field |
| Config/settings | Key-value | `config:app_settings` accessed by exact ID |

---

## Combining vs. Separating: When to Split a Table

**Combine** when the data is always fetched together and shares the same record lifecycle:
- A job posting with its embedding — always stored and retrieved as one unit
- An accomplishment with its links to skills — the links are part of the accomplishment

**Separate** when:
- Record lifecycles differ (one is updated frequently, one is rarely touched)
- Queries access one part without the other most of the time
- One part is canonical/shared (e.g., skill names are shared across accomplishments)
- One part has much stricter schema requirements than the other

**Rule of thumb:** Start combined. Separate when you observe a concrete performance
or maintainability problem — not in anticipation of one.

---

## RELATE vs. Array Field: When to Use Each

For many-to-many relationships, choose between:

**RELATE (graph edge records):**
- The relationship itself has metadata (e.g., proficiency, date, weight)
- You traverse the relationship in queries
- You need to query the relationship itself (e.g., "find all demonstrations of Python")

**Array field (embedded list of record links):**
- No metadata on the relationship
- You always access the related records as a unit with the parent
- Traversal depth is shallow (one hop, not chained)

```surql
-- RELATE (edge with metadata)
RELATE accomplishment:abc->demonstrates->skill:python
    SET proficiency = "advanced", years = 3;

-- Array field (simple list)
DEFINE FIELD skills ON accomplishment TYPE array<record<skill>>;
```

When in doubt, use RELATE. It is easier to simplify later than to add metadata
to an array field after the fact.

---

## Common Mistakes to Avoid

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Using Document when schema is actually stable | Schema drift, inconsistent data | Graduate to SCHEMAFULL |
| Using JOINs instead of graph traversal | Complex SurrealQL, slow queries | Use record links + `->` syntax |
| Separate embedding table | Extra round trip per query | Store embedding on the same record as the text |
| RELATE when array field would do | Overengineered schema | Use array field if edge has no metadata and no traversal |
| All entities as documents | No type safety | Relational for canonical/reference data |
