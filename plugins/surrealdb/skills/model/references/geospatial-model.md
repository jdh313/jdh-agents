# SurrealDB: Geospatial Model

## When to Use

Use the geospatial model when:
- Records store physical locations (latitude/longitude, addresses, regions)
- Queries need proximity — "find all X within N kilometers of Y"
- Queries need containment — "is this point inside this polygon"
- Examples: company office locations, job posting locations, candidate home cities,
  territory boundaries, delivery zones

The geospatial model is rarely a primary model — it is most often combined with
relational or document tables that happen to have a location field.

---

## Geometry Types

SurrealDB supports GeoJSON geometry types as native field values:

| Type | Description | Example |
|------|-------------|---------|
| `point` | Single coordinate (lon, lat) | Office location |
| `line` | Ordered sequence of points | Commute route |
| `polygon` | Closed ring of points | Territory boundary |
| `multipoint` | Set of points | Multiple office locations |
| `multiline` | Set of lines | Road network segment |
| `multipolygon` | Set of polygons | Multi-region territory |
| `collection` | Mix of geometry types | Combined geographic features |

Note: GeoJSON uses `[longitude, latitude]` order — not the more intuitive lat/lon.

---

## Defining a Geometry Field

```surql
DEFINE TABLE office SCHEMAFULL;
DEFINE FIELD name      ON office TYPE string ASSERT $value != NONE;
DEFINE FIELD company   ON office TYPE record<company>;
DEFINE FIELD address   ON office TYPE option<string>;
DEFINE FIELD location  ON office TYPE geometry(point);
DEFINE FIELD timezone  ON office TYPE option<string>;

-- Insert with GeoJSON point
CREATE office:acme_sf SET
    name = "Acme San Francisco",
    company = company:acme,
    address = "555 Market St, San Francisco, CA 94105",
    location = (-122.3985, 37.7914),    -- (longitude, latitude)
    timezone = "America/Los_Angeles";
```

---

## Geospatial Queries

### Distance Queries

```surql
-- Find all offices within 50 km of a point
LET $origin = (-122.4194, 37.7749);  -- San Francisco city center

SELECT name, address,
    geo::distance($origin, location) AS distance_meters
FROM office
WHERE geo::distance($origin, location) < 50000  -- 50 km in meters
ORDER BY distance_meters ASC;
```

### Containment Queries

```surql
-- Define a territory polygon
LET $bay_area = {
    type: "Polygon",
    coordinates: [[
        [-122.6, 37.2], [-121.7, 37.2],
        [-121.7, 38.0], [-122.6, 38.0],
        [-122.6, 37.2]
    ]]
};

-- Find all offices inside the polygon
SELECT name, location FROM office
WHERE geo::contains($bay_area, location);
```

### Point Inclusion

```surql
-- Check if a candidate's city is within a job's territory
SELECT id, name FROM job_posting
WHERE geo::contains(coverage_area, $candidate_location);
```

---

## Geospatial Index (MTREE)

Add an MTREE index for faster spatial queries on large tables:

```surql
DEFINE INDEX office_location_idx ON office
    FIELDS location
    MTREE DIMENSION 2;  -- 2D spatial index
```

Without a spatial index, proximity queries perform a full table scan.
At table sizes above ~10,000 records, the index becomes necessary.

---

## Geospatial Functions

| Function | Description | Return |
|----------|-------------|--------|
| `geo::distance(point, point)` | Distance between two points (meters) | float |
| `geo::area(geometry)` | Area of a polygon (square meters) | float |
| `geo::bearing(point, point)` | Compass bearing between points (degrees) | float |
| `geo::centroid(geometry)` | Center point of a geometry | point |
| `geo::contains(geom, point)` | Is point inside geometry? | bool |
| `geo::intersects(geom, geom)` | Do two geometries overlap? | bool |

---

## Example: Job Postings with Location

Combining relational + geospatial for a job posting with office location:

```surql
DEFINE TABLE job_posting SCHEMALESS;
DEFINE FIELD title       ON job_posting TYPE string;
DEFINE FIELD company     ON job_posting TYPE record<company>;
DEFINE FIELD office_location ON job_posting TYPE option<geometry(point)>;
DEFINE FIELD remote      ON job_posting TYPE string
    ASSERT $value IN ["onsite", "hybrid", "remote"];

DEFINE INDEX job_posting_location_idx ON job_posting
    FIELDS office_location MTREE DIMENSION 2;

-- Insert posting with location
CREATE job_posting:acme_ml SET
    title = "ML Engineer",
    company = company:acme,
    office_location = (-122.3985, 37.7914),
    remote = "hybrid";

-- Find all hybrid/onsite postings within 30 miles (~48 km) of candidate
LET $home = (-122.2712, 37.8044);  -- Oakland, CA

SELECT title, company.name, remote,
    geo::distance($home, office_location) / 1000 AS distance_km
FROM job_posting
WHERE remote != "remote"
    AND geo::distance($home, office_location) < 48000
ORDER BY distance_km ASC;
```

---

## Trade-offs

| Aspect | Upside | Downside |
|--------|--------|---------|
| Native geometry types | No external GIS extension needed | GeoJSON syntax requires attention to lon/lat order |
| MTREE index | Fast proximity queries | Additional index overhead; must specify dimension |
| Combine with other models | Location on existing records | No built-in geocoding (convert address → coords externally) |
| `geo::distance` | Haversine formula (accurate for Earth surface) | Returns meters — convert for display |

---

## When NOT to Use

- When location is just a human-readable string (city, country) and you never query
  by proximity or containment — store it as a plain string field
- When geospatial queries are rare (< 1% of queries) and the dataset is small —
  compute distances in application code instead
- When you need advanced GIS features (topology operations, projections, WKT format) —
  use PostGIS (PostgreSQL extension) for complex GIS workloads
- When your app only needs "same city" matching — a string comparison on a city field
  is simpler and more maintainable than geospatial coordinates
