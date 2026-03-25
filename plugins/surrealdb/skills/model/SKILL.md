---
name: surrealdb:model
description: >-
  Use when the user says "/sdb:model", "model my domain for SurrealDB", "which SurrealDB
  model should I use", "design SurrealDB schema for X", "data model for SurrealDB",
  "how should I structure this in SurrealDB", or when analyzing domain entities for
  SurrealDB storage. Analyzes domain concepts and recommends which SurrealDB data model
  (graph, document, relational, vector, time-series, key-value, geospatial, full-text
  search) fits each entity, with rationale and DEFINE statement output.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Write
  - AskUserQuestion
---

# /sdb:model -- SurrealDB Data Model Advisor

Analyzes a domain (described in words or extracted from existing code) and recommends
the right SurrealDB data model for each entity and relationship. Outputs a proposed
schema with DEFINE statements and explains trade-offs.

Read `references/decision-tree.md` before starting. Load specific model reference files
as each model is recommended.

---

## Flow

Execute these steps in order. Do not skip steps or combine them unless the user
explicitly asks for a faster pass.

### Step 1: Understand the Domain

Determine how the user wants to describe their domain:

**If the user describes entities in natural language:**
Extract entities, relationships, and notable properties from their description.
Ask clarifying questions only if critical information is missing (e.g., "Does a Role
belong to one Company or multiple?").

**If the user points to existing code (Pydantic models, YAML, SQL schema, ORM models):**
Read the source files using the Read/Glob/Grep tools. Extract:
- Entity names and field types
- Relationships between entities (foreign keys, nested objects, references)
- Any existing indices or constraints
- Field optionality (required vs. nullable)

**If the user has no existing code (greenfield):**
Ask one question to establish scope:
> What is the core entity in your domain, and what does it connect to?

Then proceed with what they give you. Do not require a complete domain model upfront.

After gathering inputs, present a brief entity summary for confirmation:

```
Entities identified:
- Company (name, industry, location)
- Role (title, level, company → Company)
- Accomplishment (description, impact, role → Role)
- Skill (name, category)
- Accomplishment ↔ Skill (many-to-many)
```

Ask: "Does this capture the domain? Anything missing or different?"

---

### Step 2: Apply the Decision Tree

Read `references/decision-tree.md` and work through it for each entity and relationship.

For each entity, determine the primary model(s). Record your reasoning internally —
you will share it in Step 3.

Key questions per entity:
1. Does it need traversal queries (following links)? → Graph
2. Is its structure variable or unknown in advance? → Document
3. Does it need strict typing and validation? → Relational
4. Does it store embeddings for similarity search? → Vector
5. Is it primarily time-stamped event data? → Time-series
6. Is it simple lookup by ID with no query needs? → Key-value
7. Does it store location/geometry data? → Geospatial
8. Does it need keyword search? → Full-text search

Remember: models are not mutually exclusive. A single table can combine multiple.

---

### Step 3: Present Recommendations

For each entity and relationship, present a table like this:

```
| Entity / Relationship   | Primary Model     | Combines With    | Rationale                                              |
|------------------------|-------------------|------------------|--------------------------------------------------------|
| Company                | Relational        | —                | Fixed schema; strict name/industry fields required     |
| Role                   | Relational        | Graph            | Typed fields + record link to Company                  |
| Accomplishment         | Document          | Graph + Vector   | Variable description; links to Role; embedding field   |
| Skill                  | Relational        | —                | Canonical list; name + category validated              |
| accomplishment→skill   | Graph (RELATE)    | —                | Many-to-many with edge metadata (proficiency)          |
| job_posting            | Document          | Vector + FTS     | Variable requirements; semantic + keyword search       |
```

For each row with a non-obvious recommendation, include a 1–2 sentence rationale.

Load the relevant model reference files (`references/document-model.md`,
`references/graph-model.md`, etc.) and cite specific SurrealDB features that
justify the recommendation.

---

### Step 4: Output Proposed Schema

Generate DEFINE statements for each entity and relationship. Use the model reference
files for correct syntax.

Structure the output as:

```surql
-- ===========================
-- Company (Relational)
-- ===========================
DEFINE TABLE company SCHEMAFULL;
DEFINE FIELD name       ON company TYPE string ASSERT $value != NONE;
DEFINE FIELD industry   ON company TYPE string;
DEFINE FIELD location   ON company TYPE string;
DEFINE INDEX company_name_idx ON company FIELDS name UNIQUE;

-- ===========================
-- Role (Relational + Graph)
-- ===========================
DEFINE TABLE role SCHEMAFULL;
DEFINE FIELD title      ON role TYPE string ASSERT $value != NONE;
DEFINE FIELD level      ON role TYPE string;
DEFINE FIELD company    ON role TYPE record<company> ASSERT $value != NONE;
DEFINE FIELD start_date ON role TYPE datetime;
DEFINE FIELD end_date   ON role TYPE option<datetime>;

-- ===========================
-- Accomplishment (Document + Graph + Vector)
-- ===========================
DEFINE TABLE accomplishment SCHEMALESS;
DEFINE FIELD description ON accomplishment TYPE string ASSERT $value != NONE;
DEFINE FIELD impact      ON accomplishment TYPE option<string>;
DEFINE FIELD role        ON accomplishment TYPE record<role> ASSERT $value != NONE;
DEFINE FIELD embedding   ON accomplishment TYPE option<array<float>>;
DEFINE INDEX accomplishment_vector_idx ON accomplishment
    FIELDS embedding HNSW DIMENSION 384 DIST COSINE TYPE F32;

-- ===========================
-- Skill (Relational)
-- ===========================
DEFINE TABLE skill SCHEMAFULL;
DEFINE FIELD name     ON skill TYPE string ASSERT $value != NONE;
DEFINE FIELD category ON skill TYPE string;
DEFINE INDEX skill_name_idx ON skill FIELDS name UNIQUE;

-- ===========================
-- accomplishment→skill (Graph edge via RELATE)
-- ===========================
DEFINE TABLE demonstrates SCHEMAFULL;
DEFINE FIELD in          ON demonstrates TYPE record<accomplishment>;
DEFINE FIELD out         ON demonstrates TYPE record<skill>;
DEFINE FIELD proficiency ON demonstrates TYPE option<string>;
```

Adjust the schema to match the actual domain the user described.

---

### Step 5: Explain Trade-offs and Alternatives

After the schema, present a brief trade-offs section:

```
Trade-offs considered:
- Accomplishment as Document vs. Relational: chose Document because description
  structure varies and strict typing would require frequent schema changes as
  the domain evolves. Graduated to SCHEMAFULL later with /sdb:schema when stable.

- accomplishment→skill as RELATE edge vs. array field: chose RELATE because
  the relationship needs metadata (proficiency) and enables graph traversal
  queries ("find all skills demonstrated by accomplishments in senior roles").

- Full-text search on job_posting: combined with vector search so users can
  filter by exact keywords (Python, AWS) while also finding semantically similar
  postings. Not either/or.
```

Tailor this section to the actual choices made.

---

### Step 6: Confirm and Offer Next Steps

Ask:

> Does this model match how you think about your domain? Any entities you'd
> add, split, or model differently?

After confirmation, offer:

```
Next steps:
- /sdb:schema  -- expand this into a complete schema file with all DEFINE statements,
             migrations, and seed data
- /sdb:query   -- write SurrealQL queries against this model
- /sdb:migrate -- plan a migration from your existing storage (YAML, ChromaDB, SQLite)
              to this SurrealDB schema
```

---

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| Single entity, no relationships | Still walk the decision tree; at minimum choose between document/relational |
| User gives SQL schema | Read it, translate FK → record links, JOIN → graph traversal |
| User gives Pydantic models | Extract fields and Optional[] annotations; Optional = `option<type>` in SurrealDB |
| Mixed models on one table | Call it out explicitly in the table and schema comments |
| User wants just one model | Focus on that entity; note what's deferred |
| Many-to-many relationship | Always evaluate RELATE vs. array field; lean toward RELATE when edge metadata exists |
| Embedding + text on same record | Show combined DEFINE with both HNSW index and SEARCH ANALYZER index |
| Greenfield with no existing code | Ask the single scoping question; proceed after first response |
| User disagrees with recommendation | Accept their preference, note the trade-off in a comment, proceed with their choice |

---

## What This Skill Does NOT Do

- Write production-ready migration scripts (use /sdb:migrate)
- Populate the schema with seed data (use /sdb:schema)
- Write application queries (use /sdb:query)
- Make irreversible decisions — all recommendations are confirmed before output
- Require the user to have existing code or a complete domain model
