# OpenTelemetry Basics

## What is OpenTelemetry?

OpenTelemetry (OTel) is a vendor-neutral, open-source observability framework for cloud-native software. It provides a unified set of APIs, SDKs, and tools to instrument, generate, collect, and export telemetry data (traces, metrics, and logs) for analysis.

**Key Benefits:**
- Vendor-neutral: No lock-in to specific observability platforms
- Standardized: Consistent instrumentation across languages and frameworks
- Auto-instrumentation: Automatic telemetry for popular libraries and frameworks
- Future-proof: Backed by CNCF and major cloud providers

## Three Pillars of Observability

### 1. Traces (Distributed Tracing)

**What:** Record of a request's journey through a distributed system.

**Structure:**
- **Trace:** The complete end-to-end journey of a request
- **Span:** A single unit of work within a trace (e.g., a function call, database query, HTTP request)
- **Span Context:** Propagated metadata (trace ID, span ID) that connects spans

**Key Attributes:**
- `trace_id`: Unique identifier for the entire trace
- `span_id`: Unique identifier for this span
- `parent_span_id`: Links to parent span
- `name`: Human-readable operation name
- `kind`: Type of span (CLIENT, SERVER, INTERNAL, PRODUCER, CONSUMER)
- `start_time` / `end_time`: Timestamps
- `status`: Status code (OK, ERROR, UNSET)
- `attributes`: Key-value metadata (e.g., `http.method`, `db.statement`)
- `events`: Time-stamped log messages within the span
- `links`: Connections to other traces (for async workflows)

**When to Use:**
- Understanding request flow through microservices
- Identifying performance bottlenecks
- Debugging distributed systems
- Analyzing latency across service boundaries

### 2. Metrics (Time-Series Data)

**What:** Numerical measurements recorded over time.

**Types:**
- **Counter:** Monotonically increasing value (e.g., total requests, errors)
- **Gauge:** Value that can go up or down (e.g., CPU usage, queue depth)
- **Histogram:** Distribution of values (e.g., request duration percentiles)
- **UpDownCounter:** Counter that can decrease (e.g., active connections)

**Key Attributes:**
- `name`: Metric identifier (e.g., `http.server.request.duration`)
- `description`: Human-readable explanation
- `unit`: Measurement unit (e.g., `ms`, `By`, `{request}`)
- `attributes`: Dimensions for filtering (e.g., `http.route`, `status_code`)

**When to Use:**
- Monitoring system health and performance
- Alerting on thresholds
- Capacity planning
- SLI/SLO tracking

### 3. Logs (Structured Events)

**What:** Timestamped records of discrete events.

**Structure:**
- `timestamp`: When the event occurred
- `severity`: Log level (DEBUG, INFO, WARN, ERROR, FATAL)
- `body`: The log message (can be structured JSON)
- `resource`: Where it came from (service name, host, etc.)
- `trace_context`: Associated trace and span IDs (for correlation)
- `attributes`: Additional metadata

**When to Use:**
- Debugging specific issues
- Auditing and compliance
- Correlating with traces to understand context
- Capturing detailed error information

## Core Concepts

### Resources

**What:** Immutable metadata about the entity producing telemetry.

**Examples:**
- `service.name`: Name of the service (e.g., "payment-api")
- `service.version`: Version of the service
- `deployment.environment`: Environment (e.g., "production", "staging")
- `host.name`: Hostname or container ID
- `cloud.provider`, `cloud.region`: Cloud metadata

**Best Practice:** Set resources once at application startup via environment variables or SDK configuration.

### Semantic Conventions

**What:** Standardized naming and attribute schemas for common operations.

**Why Important:** Enables cross-service queries and vendor portability.

**Examples:**
- HTTP: `http.method`, `http.status_code`, `http.route`, `http.target`
- Database: `db.system`, `db.name`, `db.statement`, `db.operation`
- Messaging: `messaging.system`, `messaging.destination`, `messaging.operation`
- RPC: `rpc.system`, `rpc.service`, `rpc.method`

**Reference:** https://opentelemetry.io/docs/specs/semconv/

### Context Propagation

**What:** Mechanism to pass trace context across process boundaries.

**How:**
- Headers in HTTP requests (e.g., `traceparent`, `tracestate`)
- Message metadata in queues
- Thread-local storage within a process

**Standards:**
- W3C Trace Context (default)
- B3 (Zipkin)
- Jaeger

### Sampling

**What:** Controlling which traces are recorded to reduce overhead and costs.

**Types:**
- **Head Sampling:** Decision made at trace start (fast, simple, but can miss rare errors)
  - `AlwaysOn`: Record everything (dev/test)
  - `AlwaysOff`: Record nothing
  - `TraceIdRatioBased`: Sample X% of traces
  - `ParentBased`: Follow parent span's decision
- **Tail Sampling:** Decision made after trace completes (slower, but smarter)
  - Sample errors, slow requests, specific endpoints
  - Requires OTel Collector

**Best Practice:**
- Start with head sampling for simplicity
- Move to tail sampling in collector for production workloads
- Always sample errors and slow requests

## Instrumentation Types

### Auto-Instrumentation

**What:** Automatically capture telemetry without code changes using agents or framework hooks.

**Python Example:**
```bash
pip install opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install
opentelemetry-instrument --traces_exporter otlp python app.py
```

**Pros:**
- Quick to set up
- No code changes
- Covers common libraries (requests, Flask, Django, SQLAlchemy, etc.)

**Cons:**
- Less control over span details
- May capture too much or too little
- Performance overhead if not tuned

### Manual Instrumentation

**What:** Explicitly create spans and add attributes in your code.

**Python Example:**
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def process_order(order_id):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        # Business logic here
        span.add_event("Order validated")
```

**Pros:**
- Full control over spans, attributes, events
- Capture business-specific context
- Optimize performance by controlling granularity

**Cons:**
- Requires code changes
- More maintenance

**Best Practice:** Start with auto-instrumentation, add manual instrumentation for critical business flows.

## Exporters

**What:** Components that send telemetry data to backends.

**Common Exporters:**
- **OTLP (OpenTelemetry Protocol):** Recommended default, works with OTel Collector
- **Console:** Print to stdout (debugging)
- **Jaeger:** Direct export to Jaeger
- **Zipkin:** Direct export to Zipkin
- **Prometheus:** Metrics only (pull-based)
- **Vendor-specific:** Datadog, New Relic, Honeycomb, etc.

**Best Practice:** Export to OTel Collector (OTLP), not directly to vendors. Collector provides buffering, retries, and vendor flexibility.

## Data Flow

```
Application Code
    ↓
Auto/Manual Instrumentation
    ↓
OpenTelemetry SDK (in-process)
    ↓
Exporter (OTLP)
    ↓
OpenTelemetry Collector (optional but recommended)
    ↓
Backend (Jaeger, Prometheus, Datadog, etc.)
```

## Getting Started Checklist

1. **Define Resources:** Set `service.name`, `service.version`, `deployment.environment`
2. **Choose Instrumentation:** Start with auto-instrumentation for quick wins
3. **Configure Exporter:** Use OTLP to Collector for flexibility
4. **Set Sampling:** Start with ratio-based sampling (1-10% in production)
5. **Follow Semantic Conventions:** Use standard attribute names
6. **Test Locally:** Verify traces in Jaeger or console exporter
7. **Add Manual Spans:** Instrument critical business logic
8. **Monitor Performance:** Check instrumentation overhead (<5% latency increase)
9. **Correlate Signals:** Link traces to logs and metrics
10. **Iterate:** Refine sampling, add attributes, improve cardinality
