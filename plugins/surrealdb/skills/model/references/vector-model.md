# SurrealDB: Vector Model

## When to Use

Use the vector model when:
- Records store embeddings (arrays of floats) generated from text, images, or other inputs
- You need to find the K most similar records to a query vector
- Semantic search is a primary access pattern (meaning, not just keywords)
- You are migrating from ChromaDB, Pinecone, Weaviate, or a similar vector store
- You want to combine vector search with graph traversal or structured filtering

SurrealDB's vector model is built into the core engine. No separate service or
extension needed — embeddings live on the same records as all other fields.

---

## HNSW Index

Hierarchical Navigable Small World (HNSW) is the index type for approximate
nearest neighbor (ANN) search. Define it on any field that stores a float array:

```surql
DEFINE TABLE accomplishment SCHEMALESS;
DEFINE FIELD embedding ON accomplishment TYPE option<array<float>>;
DEFINE INDEX accomplishment_vector_idx ON accomplishment
    FIELDS embedding
    HNSW DIMENSION 384    -- must match your embedding model's output dimension
    DIST COSINE           -- distance metric: COSINE, EUCLIDEAN, or MANHATTAN
    TYPE F32;             -- storage precision: F32 (float) or I16 (quantized)
```

**Dimension** must match the embedding model exactly:
- `all-MiniLM-L6-v2` (sentence-transformers) → 384
- `text-embedding-ada-002` (OpenAI) → 1536
- `nomic-embed-text` → 768
- `mxbai-embed-large` → 1024

**Distance metrics:**
- `COSINE` — most common for text embeddings; measures angle, not magnitude
- `EUCLIDEAN` — geometric distance; better for spatial or normalized numeric data
- `MANHATTAN` — L1 norm; rarely used for embeddings

---

## Storing Embeddings from Python

```python
from surrealdb import AsyncSurreal
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")  # 384-dimensional

async with AsyncSurreal("file://./resift.db") as db:
    await db.use("resift", "main")

    text = "Reduced API latency by 40% through Redis caching layer"
    embedding = model.encode(text).tolist()  # convert numpy → list[float]

    await db.create("accomplishment", {
        "description": text,
        "role": "role:acme_senior",
        "embedding": embedding
    })
```

Always convert numpy arrays to Python lists before inserting. SurrealDB's Python
SDK does not automatically serialize numpy arrays.

---

## KNN Queries

Find the K nearest records to a query vector using the `<|K|>` operator:

```surql
-- Find 5 accomplishments most similar to the query embedding
SELECT id, description,
    vector::similarity::cosine(embedding, $query_vector) AS score
FROM accomplishment
WHERE embedding <|5|> $query_vector
ORDER BY score DESC;
```

The `<|K|>` operator activates the HNSW index. Without it, the query degrades
to a full table scan — avoid this in production.

From Python:

```python
query_text = "caching systems for performance"
query_vector = model.encode(query_text).tolist()

results = await db.query(
    """
    SELECT id, description,
        vector::similarity::cosine(embedding, $qv) AS score
    FROM accomplishment
    WHERE embedding <|10|> $qv
    ORDER BY score DESC
    """,
    {"qv": query_vector}
)
```

---

## Similarity and Distance Functions

| Function | Returns | Use when |
|----------|---------|---------|
| `vector::similarity::cosine(a, b)` | 0.0–1.0, higher = more similar | Text embeddings (most common) |
| `vector::distance::euclidean(a, b)` | 0.0–∞, lower = more similar | Spatial or normalized numeric data |
| `vector::distance::manhattan(a, b)` | 0.0–∞, lower = more similar | Sparse vectors |
| `vector::distance::knn()` | Distance to k-nearest neighbor | Used inside index-accelerated queries |

---

## Combining Vector with Structured Filtering

Vector and structured filters can be combined in the same query:

```surql
-- Find 10 accomplishments similar to query, only from senior roles
SELECT id, description, score
FROM (
    SELECT id, description,
        vector::similarity::cosine(embedding, $qv) AS score
    FROM accomplishment
    WHERE embedding <|20|> $qv
) WHERE role IN (
    SELECT id FROM role WHERE level = "senior"
)
ORDER BY score DESC
LIMIT 10;
```

The inner query uses HNSW for speed, the outer applies the structured filter.
Fetch more than you need from the vector query (20 above), then filter down.

---

## Example: Job Matching Domain (resift)

```surql
DEFINE TABLE job_posting SCHEMALESS;
DEFINE FIELD title       ON job_posting TYPE string;
DEFINE FIELD company     ON job_posting TYPE record<company>;
DEFINE FIELD description ON job_posting TYPE string;
DEFINE FIELD embedding   ON job_posting TYPE option<array<float>>;
DEFINE INDEX job_posting_vector_idx ON job_posting
    FIELDS embedding HNSW DIMENSION 384 DIST COSINE TYPE F32;

-- Match a resume profile against job postings
LET $profile_vector = $profile_embedding;

SELECT title, company.name,
    vector::similarity::cosine(embedding, $profile_vector) AS match_score
FROM job_posting
WHERE embedding <|20|> $profile_vector
ORDER BY match_score DESC
LIMIT 10;
```

---

## HNSW Parameters

| Parameter | Default | Effect |
|-----------|---------|--------|
| `DIMENSION N` | Required | Must match embedding model output |
| `DIST metric` | Required | Cosine, Euclidean, or Manhattan |
| `TYPE F32` | Recommended | F32 = float precision; I16 = quantized (smaller, less accurate) |

HNSW also supports `M` and `EF_CONSTRUCTION` parameters for tuning recall vs.
build time. Leave at defaults unless you have measured a specific recall problem.

---

## Trade-offs

| Aspect | Upside | Downside |
|--------|--------|---------|
| HNSW index | Fast approximate search | Index build time; memory overhead |
| Same record as text | One query for text + embedding | Larger record size |
| No external service | Simpler ops, one DB to manage | Less tuning knobs than dedicated vector DBs |
| Cosine similarity | Works well for text | Not appropriate for non-normalized vectors |

---

## When NOT to Use

- When keyword matching is sufficient — use full-text search instead (faster, cheaper)
- When you have fewer than ~1,000 records and can afford a full scan — HNSW index
  overhead is not worth it at small scale
- When the embedding model dimension is unknown or variable — dimension must be fixed
  at index creation time
- When you need exact nearest neighbor (not approximate) — HNSW is ANN by design;
  for exact search, scan without the index (costly at scale)
