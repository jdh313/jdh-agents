# SurrealDB

Multi-model database design and query assistant for SurrealDB. Helps you choose the right data model, design schemas, plan migrations from other data layers, and write SurrealQL queries using the official Python SDK.

## Skills

### `/sdb:model` -- Data Model Advisor

Choose between SurrealDB's eight data models based on your use case:

- **Document** — Schemaless JSON-like records with nested objects
- **Graph** — Linked records with traversal queries
- **Relational** — Typed schemas with assertions and indices
- **Vector** — Embeddings with HNSW similarity search
- **Time-series** — Temporal data with time-based queries
- **Key-value** — Direct record ID lookups
- **Geospatial** — Geometry types, distance and containment queries
- **Full-text search** — Text indices with analyzers and tokenizers

Evaluates your data structure, query patterns, and access patterns to recommend the best fit (or combination).

### `/sdb:schema` -- Schema Designer

Design a SurrealDB schema for your model:

1. **Gather context** — understand your data structure and relationships
2. **Propose schema** — SCHEMAFULL table definitions with typed fields, assertions, and indices
3. **Review alternatives** — tradeoffs between flexibility (SCHEMALESS) and validation (SCHEMAFULL)
4. **Output code** — ready-to-use DEFINE statements for the Python SDK

### `/sdb:migrate` -- Migration Planner

Plan a migration from another data layer (SQL, MongoDB, Redis, etc.) to SurrealDB:

1. **Source audit** — understand current schema or document structure
2. **Target design** — propose SurrealDB schema and model choice
3. **Migration strategy** — data mapping, record ID assignment, link transformation
4. **Implementation checklist** — step-by-step migration with rollback steps

### `/sdb:query` -- SurrealQL Query Writer

Write and optimize SurrealQL queries:

- Execute SELECT, CREATE, UPDATE, DELETE, and RELATE statements
- Debug query syntax and error messages
- Optimize for performance (index usage, traversal depth)
- Support parameterized queries with variables

## Agents

### schema-reviewer

Audit an existing SurrealDB schema for:

- Consistency with the chosen data model
- Missing indices on frequently queried fields
- Record ID naming conventions
- SCHEMAFULL vs SCHEMALESS decisions

### query-debugger

Diagnose failing or slow SurrealQL queries:

- Trace execution path through records and links
- Identify missing indices or inefficient traversals
- Suggest rewrites using graph, vector, or full-text alternatives
- Performance profiling recommendations

## Target Use Case

Python projects using the official `surrealdb` SDK. Assumes basic familiarity with databases but not prior SurrealDB experience.

## References

- `surrealdb-overview.md` — SurrealDB mental model, multi-model overview, connection modes, Python SDK basics, key differences from SQL
