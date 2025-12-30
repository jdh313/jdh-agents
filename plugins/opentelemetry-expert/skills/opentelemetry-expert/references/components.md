# OpenTelemetry Components - When to Use Each

## Component Overview

OpenTelemetry consists of several components that work together. Understanding when to use each is critical for building a robust observability stack.

## 1. OpenTelemetry API

### What It Is
Language-specific APIs that define how to create and manipulate telemetry data (traces, metrics, logs). The API is the stable interface that application code uses.

### When to Use
**Always.** The API is the foundation—all instrumentation uses it, whether auto or manual.

### Key Operations
- `get_tracer()`: Get a tracer instance
- `start_span()` / `start_as_current_span()`: Create spans
- `get_meter()`: Get a meter for metrics
- `create_counter()`, `create_histogram()`: Define metrics
- `set_attribute()`, `add_event()`: Enrich telemetry

### Anti-Pattern
❌ Don't call vendor-specific APIs directly (e.g., Datadog, New Relic SDKs)—use OTel API for portability.

## 2. OpenTelemetry SDK

### What It Is
Language-specific implementation of the API that actually generates and exports telemetry. The SDK is configured with exporters, samplers, processors, and resource attributes.

### When to Use
**Required for all applications.** The SDK is embedded in your application process.

### Configuration Points
- **Resource:** Service name, version, environment
- **Sampler:** Which traces to record
- **Span Processor:** How to process spans (batch vs simple)
- **Exporter:** Where to send data (OTLP, console, Jaeger, etc.)
- **Propagator:** How to propagate context (W3C, B3, etc.)

### Python Example
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

resource = Resource(attributes={
    "service.name": "payment-api",
    "service.version": "1.2.3",
    "deployment.environment": "production"
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://collector:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
```

### When NOT to Use
Don't run the SDK in serverless functions with very short lifetimes—use environment variable configuration for auto-instrumentation instead.

## 3. OpenTelemetry Collector

### What It Is
Standalone process that receives, processes, and exports telemetry data. Acts as a vendor-neutral intermediary between applications and backends.

### When to Use

#### ✅ Always Use in Production
- **Decoupling:** Change backends without redeploying apps
- **Buffering:** Handle backend outages gracefully
- **Batching:** Reduce network calls and backend load
- **Filtering:** Drop high-cardinality or sensitive data
- **Enrichment:** Add metadata (k8s pod name, cloud region)
- **Tail Sampling:** Smart sampling after trace completes
- **Fan-out:** Send to multiple backends (Jaeger + Datadog)

#### ❌ Skip in Local Dev
- Adds complexity
- Console exporter is simpler for debugging

### Deployment Modes

#### Agent Mode (Sidecar/DaemonSet)
**When:** Deploy alongside each application instance (in same pod/host)

**Pros:**
- Low latency
- Isolated failure domain (one app's collector doesn't affect others)
- Can enrich with local host metadata

**Cons:**
- More collector instances to manage
- Higher resource usage

**Use Case:** High-throughput apps, Kubernetes DaemonSet, EC2 host agent

#### Gateway Mode (Centralized)
**When:** Deploy as a central cluster service

**Pros:**
- Fewer instances to manage
- Centralized filtering and tail sampling
- Lower per-instance resource cost

**Cons:**
- Single point of failure (mitigate with HA setup)
- Slightly higher network latency

**Use Case:** Small-scale deployments, serverless, cost optimization

#### Hybrid Mode
**When:** Agent for collection, Gateway for advanced processing

**Example:**
```
App → OTLP → Agent Collector (batching, basic filtering)
    → OTLP → Gateway Collector (tail sampling, enrichment)
    → Backends
```

**Use Case:** Large-scale production (recommended)

### Key Collector Features

#### Receivers
Accept telemetry data in various formats.

**Examples:**
- `otlp`: Receive OTLP (gRPC or HTTP)
- `jaeger`: Receive Jaeger-format traces
- `prometheus`: Scrape Prometheus metrics
- `hostmetrics`: Collect host metrics (CPU, memory)
- `k8s_cluster`: Collect Kubernetes cluster metrics

#### Processors
Transform, filter, or enrich data.

**Essential Processors:**
- `batch`: Batch spans/metrics before export (reduces network calls)
- `memory_limiter`: Prevent OOM by limiting memory usage
- `resource`: Add/modify resource attributes
- `attributes`: Add/modify span/metric attributes
- `filter`: Drop spans/metrics by criteria
- `tail_sampling`: Sample traces after completion
- `probabilistic_sampler`: Head sampling by percentage
- `span`: Rename, modify spans

#### Exporters
Send telemetry to backends.

**Examples:**
- `otlp`: Export to another collector or OTLP backend
- `jaeger`: Export to Jaeger
- `prometheus`: Expose metrics for Prometheus scraping
- `logging`: Debug by logging to console
- `datadog`, `newrelic`, `honeycomb`: Vendor exporters

### Collector Configuration Example
See `assets/collector-basic.yaml` and `assets/collector-production.yaml` in this skill.

## 4. Auto-Instrumentation Libraries

### What They Are
Framework-specific plugins that automatically create spans for common operations without code changes.

### When to Use
**Always start here** for quick time-to-value.

### Python Auto-Instrumentation Packages
- `opentelemetry-instrumentation-flask`: Flask apps
- `opentelemetry-instrumentation-fastapi`: FastAPI apps
- `opentelemetry-instrumentation-django`: Django apps
- `opentelemetry-instrumentation-requests`: HTTP client
- `opentelemetry-instrumentation-sqlalchemy`: Database queries
- `opentelemetry-instrumentation-redis`: Redis operations
- `opentelemetry-instrumentation-celery`: Celery tasks
- `opentelemetry-instrumentation-aws-lambda`: Lambda functions

**Install All at Once:**
```bash
opentelemetry-bootstrap -a install
```

### When to Supplement with Manual Instrumentation
- Auto-instrumentation captures too much noise
- Need business-specific attributes (e.g., `user.id`, `order.amount`)
- Critical code paths not covered by auto-instrumentation
- Want to control span names for readability

## 5. Manual Instrumentation

### When to Use
**After auto-instrumentation**, to add business context or fill gaps.

### Use Cases
- Add spans for critical business logic (e.g., "process_payment", "validate_order")
- Add attributes for business dimensions (e.g., `customer.tier`, `product.category`)
- Add events for key milestones (e.g., "fraud_check_passed")
- Create custom metrics (e.g., `orders.processed`, `payment.amount`)
- Propagate context in async workflows (Celery, queues)

### Python Example
```python
from opentelemetry import trace, metrics

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Custom counter
orders_counter = meter.create_counter(
    "orders.processed",
    description="Number of orders processed",
    unit="{order}"
)

def process_order(order_id, customer_id):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("customer.id", customer_id)

        # Business logic
        validate_order(order_id)
        span.add_event("Order validated")

        charge_payment(order_id)
        span.add_event("Payment charged")

        orders_counter.add(1, {"status": "success"})
```

## 6. Propagators

### What They Are
Mechanisms to serialize trace context and propagate it across process boundaries (HTTP headers, message metadata).

### When to Choose

#### W3C Trace Context (Default)
**When:** Modern apps, vendor-neutral setup

**Format:**
```
traceparent: 00-{trace_id}-{span_id}-{flags}
tracestate: vendor1=value,vendor2=value
```

**Use:** This is the default—stick with it unless you have legacy constraints.

#### B3 (Zipkin)
**When:** Legacy Zipkin instrumentation or Istio service mesh

**Format:**
```
X-B3-TraceId: {trace_id}
X-B3-SpanId: {span_id}
X-B3-Sampled: {0|1}
```

#### Jaeger
**When:** Legacy Jaeger instrumentation

**Format:**
```
uber-trace-id: {trace_id}:{span_id}:{parent_id}:{flags}
```

### Configuration
```python
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat

# Use B3 instead of W3C
set_global_textmap(B3MultiFormat())
```

## 7. Samplers

### When to Use Each

#### AlwaysOn Sampler
**When:** Local dev, debugging, low-traffic services
**Trade-off:** Records everything—high cost, 100% accuracy

```python
from opentelemetry.sdk.trace.sampling import AlwaysOnSampler
```

#### AlwaysOff Sampler
**When:** Temporarily disable tracing
**Trade-off:** No telemetry

#### TraceIdRatioBased Sampler
**When:** Production apps with moderate traffic (< 10k req/min)
**Trade-off:** Simple, predictable cost, but may miss rare errors

**Example:** Sample 10% of traces
```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
sampler = TraceIdRatioBased(0.1)  # 10%
```

#### ParentBased Sampler
**When:** Microservices—follow parent span's decision
**Trade-off:** Maintains sampling consistency across services

**Example:**
```python
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
sampler = ParentBased(root=TraceIdRatioBased(0.1))
```

#### Tail Sampling (Collector-Based)
**When:** High-traffic production (> 10k req/min), need smart sampling
**Trade-off:** Complex, requires collector, slight delay

**Use Cases:**
- Always sample errors (status=ERROR)
- Always sample slow requests (> 2s)
- Sample specific endpoints (e.g., /checkout)
- Sample specific customers (e.g., VIP tier)

**See:** `assets/collector-production.yaml` for tail sampling config

## 8. Span Processors

### BatchSpanProcessor (Recommended)
**When:** Production—batches spans before export to reduce network overhead

**Config:**
- `max_queue_size`: Buffer size (default: 2048)
- `schedule_delay_millis`: How often to export (default: 5000ms)
- `max_export_batch_size`: Max spans per batch (default: 512)

```python
from opentelemetry.sdk.trace.export import BatchSpanProcessor
processor = BatchSpanProcessor(exporter)
```

### SimpleSpanProcessor
**When:** Local dev, debugging—exports each span immediately

```python
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
processor = SimpleSpanProcessor(exporter)
```

## Decision Tree: Which Components to Use?

### Local Development
- ✅ SDK with console exporter
- ✅ Auto-instrumentation
- ❌ Skip collector

### Production - Small Scale (< 1k req/min)
- ✅ SDK with OTLP exporter → Collector (gateway mode)
- ✅ Auto-instrumentation + manual for critical flows
- ✅ Head sampling (TraceIdRatioBased 10-50%)
- ✅ BatchSpanProcessor

### Production - Medium Scale (1k-10k req/min)
- ✅ SDK with OTLP exporter → Collector (agent mode)
- ✅ Auto-instrumentation + manual spans
- ✅ Head sampling (5-10%) or tail sampling
- ✅ Collector processors: batch, memory_limiter, attributes

### Production - Large Scale (> 10k req/min)
- ✅ SDK with OTLP exporter → Agent Collector → Gateway Collector
- ✅ Auto-instrumentation + manual spans
- ✅ Tail sampling in gateway collector
- ✅ Collector processors: batch, memory_limiter, tail_sampling, filter
- ✅ Fan-out to multiple backends

## Common Mistakes to Avoid

1. **Sending directly to vendor backends:** Use collector for flexibility
2. **Over-instrumenting:** Too many spans increases cost and noise
3. **Under-sampling in production:** 100% sampling is expensive
4. **Ignoring semantic conventions:** Custom attribute names hurt portability
5. **Not using batch processor:** SimpleSpanProcessor kills performance
6. **Skipping the collector:** Redeploying apps to change backends is painful
7. **Not correlating logs with traces:** Missing `trace_id` in logs
8. **High cardinality attributes:** Don't use `user.id` in metric labels (use traces)
