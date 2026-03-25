# SurrealDB: Full-Text Search Model

## When to Use

Use full-text search when:
- Users search by specific keywords or phrases within text fields
- You need ranked results with scoring and relevance
- Exact word matching is more important than semantic meaning
- Examples: searching job titles, filtering accomplishment descriptions by technology
  keywords, finding companies by name fragments

Full-text search and vector search are complementary — use both when you need both
keyword accuracy and semantic similarity. They can be combined in a single query.

---

## Search Analyzer

An analyzer defines how text is tokenized and normalized before indexing:

```surql
-- Define a custom analyzer
DEFINE ANALYZER simple_text
    TOKENIZERS blank    -- split on whitespace
    FILTERS lowercase,  -- normalize case
            ascii;      -- strip accents/diacritics

-- Or use a language-aware stemming analyzer
DEFINE ANALYZER english_text
    TOKENIZERS blank
    FILTERS lowercase,
            snowball(english);  -- stem words (running → run)
```

| Tokenizer | Splits on | Best for |
|-----------|-----------|---------|
| `blank` | Whitespace | General prose, code |
| `class` | Character class boundaries (alpha/digit) | Mixed text/code |
| `camelcase` | CamelCase boundaries | Code identifiers |
| `none` | Does not split | Single-token exact matching |

| Filter | Effect | Use when |
|--------|--------|---------|
| `lowercase` | Normalize case | Almost always |
| `ascii` | Strip diacritics | Multi-language content |
| `snowball(lang)` | Stem words | Natural language prose |

---

## Full-Text Search Index

```surql
DEFINE TABLE job_posting SCHEMALESS;
DEFINE FIELD title       ON job_posting TYPE string;
DEFINE FIELD description ON job_posting TYPE string;

-- Define the analyzer
DEFINE ANALYZER job_text
    TOKENIZERS blank
    FILTERS lowercase, ascii;

-- Index the fields
DEFINE INDEX job_posting_title_fts ON job_posting
    FIELDS title
    SEARCH ANALYZER job_text BM25;

DEFINE INDEX job_posting_desc_fts ON job_posting
    FIELDS description
    SEARCH ANALYZER job_text BM25;
```

BM25 (Best Match 25) is the standard ranking function. It considers term frequency
and document length to rank results.

---

## Querying with MATCHES

Use the `@@` (MATCHES) operator to trigger a full-text search query:

```surql
-- Find postings mentioning Python in the title
SELECT id, title, search::score(1) AS score
FROM job_posting
WHERE title @@ "Python"
ORDER BY score DESC;

-- Multi-word query (AND: both terms must appear)
SELECT id, title FROM job_posting
WHERE description @@ "machine learning Python";

-- Match on multiple indexed fields
SELECT id, title, description,
    search::score(1) AS title_score,
    search::score(2) AS desc_score
FROM job_posting
WHERE title @1@ "engineer"
    OR description @2@ "machine learning"
ORDER BY (title_score + desc_score) DESC;
```

The `@N@` syntax references a specific index by position when scoring multiple
fields separately.

---

## Highlighting Matched Terms

`search::highlight` wraps matched terms in tags for display:

```surql
SELECT
    id,
    search::highlight("<mark>", "</mark>", 1) AS highlighted_title
FROM job_posting
WHERE title @@ "Python engineer"
ORDER BY search::score(1) DESC;

-- Returns:
-- { highlighted_title: "Senior <mark>Python</mark> <mark>Engineer</mark>" }
```

---

## Example: Job Posting Search

```surql
DEFINE TABLE job_posting SCHEMALESS;
DEFINE FIELD title       ON job_posting TYPE string;
DEFINE FIELD company     ON job_posting TYPE record<company>;
DEFINE FIELD description ON job_posting TYPE string;
DEFINE FIELD embedding   ON job_posting TYPE option<array<float>>;

DEFINE ANALYZER job_text
    TOKENIZERS blank
    FILTERS lowercase, ascii, snowball(english);

-- Full-text index on description
DEFINE INDEX job_posting_desc_fts ON job_posting
    FIELDS description
    SEARCH ANALYZER job_text BM25;

-- HNSW index for vector search on same table
DEFINE INDEX job_posting_vector_idx ON job_posting
    FIELDS embedding
    HNSW DIMENSION 384 DIST COSINE TYPE F32;

-- Keyword search
SELECT title, company.name, search::score(1) AS relevance
FROM job_posting
WHERE description @@ "distributed systems Kubernetes"
ORDER BY relevance DESC
LIMIT 20;

-- Highlight matches
SELECT
    title,
    search::highlight("<b>", "</b>", 1) AS description_snippet
FROM job_posting
WHERE description @@ "Python machine learning"
LIMIT 10;
```

---

## Combining Full-Text and Vector Search

Use both when you want keyword precision AND semantic breadth:

```surql
-- Step 1: keyword filter (find records containing exact terms)
LET $keyword_matches = SELECT id FROM job_posting
    WHERE description @@ "Python backend";

-- Step 2: vector search within keyword matches
SELECT id, title,
    vector::similarity::cosine(embedding, $profile_vector) AS score
FROM job_posting
WHERE id IN $keyword_matches
    AND embedding <|20|> $profile_vector
ORDER BY score DESC
LIMIT 10;
```

This pattern:
- Ensures results contain the required keywords (full-text)
- Ranks by semantic similarity within those results (vector)

Alternatively, run both searches independently and merge results in application code,
scoring each result by a weighted combination of keyword rank and vector similarity.

---

## Trade-offs

| Aspect | Upside | Downside |
|--------|--------|---------|
| BM25 scoring | Proven ranking algorithm | Does not understand meaning (only word frequency) |
| Multiple analyzers | Tunable per field | More upfront configuration |
| Combined with vector | Keyword precision + semantic breadth | Two indices to maintain |
| `search::highlight` | Ready for display layer | Returns full field by default; truncate in app code |
| Stemming (snowball) | "running" matches "run" | Language-specific; wrong language = poor results |

**Full-text vs. vector: when to use which**

| Full-text search | Vector search |
|-----------------|---------------|
| User knows the exact technology ("Python") | User describes a concept ("distributed systems experience") |
| Filtering, not ranking, is the goal | Ranking by similarity is the goal |
| Small dataset, fast iteration | Large dataset with embeddings pre-computed |
| Exact phrase matching matters | Paraphrasing and synonyms should match |

---

## When NOT to Use

- When all your queries are by exact record ID — use key-value
- When the text you are searching is very short (< 5 tokens on average) — full-text
  overhead is not worth it; use `string::contains()` or `CONTAINS` instead
- When you only need "does this record mention Python" and not ranking — use
  `WHERE description CONTAINS "Python"` (simpler, no index required)
- When semantic similarity is more important than exact keyword matching — vector
  search alone is sufficient
- When search volume is low and dataset is small — application-level filtering with
  `string::lowercase` comparisons is simpler to set up and maintain
