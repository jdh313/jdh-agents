# SurrealDB: Time-Series Model

## When to Use

Use time-series conventions when:
- Records represent events, state changes, or measurements at a point in time
- The primary query pattern is "what happened between time A and time B"
- Records are append-only — created once, never updated
- You need time-bucketed aggregations (count per day, average per hour)
- Examples: application status history, audit logs, job search activity events,
  webhook delivery logs, background job results

SurrealDB does not have a dedicated time-series engine, but its `datetime` type,
time functions, and index support make it effective for temporal data patterns.

---

## Core Building Blocks

### The `datetime` Type

```surql
DEFINE TABLE application_event SCHEMAFULL;
DEFINE FIELD event_type  ON application_event TYPE string
    ASSERT $value IN ["applied", "screened", "interviewed", "offered", "rejected", "withdrawn"];
DEFINE FIELD job_posting ON application_event TYPE record<job_posting>;
DEFINE FIELD occurred_at ON application_event TYPE datetime
    VALUE $value OR time::now();
DEFINE FIELD notes       ON application_event TYPE option<string>;

-- Insert event
CREATE application_event SET
    event_type = "applied",
    job_posting = job_posting:acme_ml;

-- Insert with explicit timestamp
CREATE application_event SET
    event_type = "interviewed",
    job_posting = job_posting:acme_ml,
    occurred_at = d"2024-03-15T10:30:00Z";
```

### Time-Based Record IDs

For high-throughput append-only data, use timestamp-based IDs to guarantee ordering:

```surql
-- Manually set a time-based ID
CREATE application_event:["2024-03-15T10:30:00Z", "acme_ml"] SET
    event_type = "interviewed",
    job_posting = job_posting:acme_ml;
```

Or let the table auto-generate UUIDs and rely on the `occurred_at` field for ordering.

---

## Time Range Queries

```surql
-- All events in the last 30 days
SELECT * FROM application_event
WHERE occurred_at >= time::now() - 30d
ORDER BY occurred_at DESC;

-- Events for a specific job posting in a date window
SELECT event_type, occurred_at FROM application_event
WHERE job_posting = job_posting:acme_ml
    AND occurred_at BETWEEN d"2024-01-01T00:00:00Z" AND d"2024-06-30T23:59:59Z"
ORDER BY occurred_at ASC;

-- Most recent event per job posting
SELECT job_posting, array::last(
    SELECT event_type, occurred_at FROM application_event
    WHERE job_posting = $parent.job_posting
    ORDER BY occurred_at ASC
) AS latest_event
FROM application_event
GROUP BY job_posting;
```

---

## Time Functions

| Function | Returns | Example |
|----------|---------|---------|
| `time::now()` | Current UTC datetime | `VALUE time::now()` |
| `time::floor(dt, duration)` | Truncate to bucket | `time::floor(occurred_at, 1d)` |
| `time::ceil(dt, duration)` | Round up to bucket | `time::ceil(occurred_at, 1h)` |
| `time::day(dt)` | Day of month (1–31) | `time::day(occurred_at)` |
| `time::month(dt)` | Month (1–12) | `time::month(occurred_at)` |
| `time::year(dt)` | Year | `time::year(occurred_at)` |
| `time::format(dt, fmt)` | String formatting | `time::format(occurred_at, "%Y-%m")` |

---

## Time-Bucketed Aggregations

Count events per day using `time::floor`:

```surql
SELECT
    time::floor(occurred_at, 1d) AS day,
    event_type,
    count() AS n
FROM application_event
WHERE occurred_at >= time::now() - 90d
GROUP BY day, event_type
ORDER BY day ASC;
```

Weekly activity summary:

```surql
SELECT
    time::floor(occurred_at, 7d) AS week,
    count() AS total_events,
    count(WHERE event_type = "applied") AS applications,
    count(WHERE event_type = "interviewed") AS interviews
FROM application_event
GROUP BY week
ORDER BY week DESC;
```

---

## Example: Job Application Status History

```surql
DEFINE TABLE application_event SCHEMAFULL;
DEFINE FIELD event_type  ON application_event TYPE string
    ASSERT $value IN ["applied", "screened", "phone_screen", "technical",
                      "onsite", "offered", "rejected", "withdrawn", "accepted"];
DEFINE FIELD job_posting ON application_event TYPE record<job_posting>
    ASSERT $value != NONE;
DEFINE FIELD occurred_at ON application_event TYPE datetime
    VALUE $value OR time::now();
DEFINE FIELD source      ON application_event TYPE option<string>;  -- "email", "portal", "recruiter"
DEFINE FIELD notes       ON application_event TYPE option<string>;

DEFINE INDEX application_event_time_idx ON application_event
    FIELDS occurred_at;
DEFINE INDEX application_event_posting_idx ON application_event
    FIELDS job_posting, occurred_at;

-- Full application timeline
SELECT event_type, occurred_at, notes
FROM application_event
WHERE job_posting = job_posting:acme_ml
ORDER BY occurred_at ASC;

-- Current funnel status (most recent event per posting)
SELECT DISTINCT job_posting,
    (SELECT VALUE event_type FROM application_event
     WHERE job_posting = $parent.job_posting
     ORDER BY occurred_at DESC LIMIT 1)[0] AS current_status
FROM application_event;
```

---

## Trade-offs

| Aspect | Upside | Downside |
|--------|--------|---------|
| Append-only semantics | Clean audit trail, simple inserts | No updates — state is derived from event sequence |
| Time indices | Fast range scans | Must define index explicitly; no automatic partitioning |
| Flexible structure | Mix time-series and document models | No native retention/expiry policies |
| Built into SurrealDB | No separate TSDB to operate | Less optimized than dedicated TSDBs (InfluxDB, TimescaleDB) |

---

## When NOT to Use

- When records need frequent updates (mutating records breaks append-only semantics) —
  store the current state separately from the event log
- When you need sub-millisecond ingestion at millions of events per second — use a
  dedicated time-series database (InfluxDB, TimescaleDB) and sync summaries to SurrealDB
- When time is just one field among many and not the primary access pattern — use
  relational with a `created_at` field instead of designing around time-series conventions
- When you need automatic data retention/expiry — SurrealDB does not have TTL on records;
  implement retention via a background job
