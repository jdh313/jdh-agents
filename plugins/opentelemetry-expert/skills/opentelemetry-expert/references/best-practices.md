# OpenTelemetry Best Practices (2025)

This document covers modern best practices for implementing OpenTelemetry in production systems.

## 1. Resource Configuration

### ✅ Always Set Core Resource Attributes

```python
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT

resource = Resource(attributes={
    SERVICE_NAME: "payment-api",
    SERVICE_VERSION: "2.1.0",  # From git tag or build metadata
    DEPLOYMENT_ENVIRONMENT: "production",  # or "staging", "development"
    "service.namespace": "payments",  # Logical grouping
    "service.instance.id": os.getenv("HOSTNAME"),  # Pod name, EC2 instance ID
})
```

### Why This Matters
- Enables filtering and grouping in observability UIs
- Critical for multi-environment and multi-service debugging
- Required for cost attribution and capacity planning

### Environment Variables (Preferred in 2025)

```bash
export OTEL_SERVICE_NAME=payment-api
export OTEL_SERVICE_VERSION=$(git describe --tags)
export OTEL_RESOURCE_ATTRIBUTES="deployment.environment=production,service.namespace=payments"
```

### Cloud-Specific Attributes

```python
# AWS
"cloud.provider": "aws"
"cloud.platform": "aws_ec2"  # or "aws_ecs", "aws_lambda"
"cloud.region": "us-east-1"
"cloud.account.id": "123456789"

# Kubernetes
"k8s.namespace.name": "production"
"k8s.pod.name": os.getenv("HOSTNAME")
"k8s.deployment.name": "payment-api"
"k8s.cluster.name": "prod-cluster"

# Container
"container.id": os.getenv("CONTAINER_ID")
"container.image.name": "payment-api"
"container.image.tag": "v2.1.0"
```

## 2. Sampling Strategy

### Development: AlwaysOn

```python
from opentelemetry.sdk.trace.sampling import AlwaysOnSampler
sampler = AlwaysOnSampler()
```

### Production: Ratio-Based Head Sampling (Simple)

```python
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased

# Sample 5% of traces, always respect parent's decision
sampler = ParentBased(root=TraceIdRatioBased(0.05))
```

### Production: Tail Sampling (Advanced, Requires Collector)

Use tail sampling for intelligent sampling decisions:

```yaml
# collector-config.yaml
processors:
  tail_sampling:
    policies:
      # Always sample errors
      - name: errors
        type: status_code
        status_code: {status_codes: [ERROR]}

      # Always sample slow requests (> 2s)
      - name: slow_requests
        type: latency
        latency: {threshold_ms: 2000}

      # Always sample specific endpoints
      - name: critical_endpoints
        type: string_attribute
        string_attribute: {key: http.route, values: [/checkout, /payment]}

      # Sample 5% of everything else
      - name: baseline
        type: probabilistic
        probabilistic: {sampling_percentage: 5}
```

### Recommended Sampling Rates by Traffic Volume

| Requests/min | Sampling Strategy | Sample Rate |
|--------------|-------------------|-------------|
| < 100 | Head sampling | 100% |
| 100-1k | Head sampling | 50% |
| 1k-10k | Head sampling | 10% |
| 10k-100k | Tail sampling | 5% baseline + errors + slow |
| > 100k | Tail sampling | 1% baseline + errors + slow |

### Always Sample These

Regardless of traffic, always sample:
- Errors (HTTP 5xx, exceptions)
- Slow requests (p95+ latency)
- Critical business flows (checkout, payment, signup)
- VIP customers (if identifiable early)

## 3. Span Granularity

### ✅ Right Level of Granularity

```python
# ✅ Good: Business-level spans
with tracer.start_as_current_span("process_order"):
    validate_order()
    charge_payment()
    send_confirmation()

# ❌ Bad: Too granular (creates noise)
for item in order.items:
    with tracer.start_as_current_span(f"process_item_{item.id}"):
        calculate_tax(item)
```

### Guidelines
- **Do:** Create spans for business operations, external calls, database queries
- **Don't:** Create spans for loops, getters/setters, utility functions
- **Rule of Thumb:** If it takes < 10ms, probably doesn't need a span

### Span Depth Limit
- Keep trace depth < 10 levels
- Each span adds overhead (~1-5ms)
- Deep traces are hard to visualize

## 4. Semantic Conventions (Critical for 2025)

### Always Use Standard Attribute Names

OpenTelemetry defines semantic conventions for common operations. **Always follow them.**

#### HTTP Operations

```python
# ✅ Correct
span.set_attribute("http.method", "POST")
span.set_attribute("http.status_code", 200)
span.set_attribute("http.route", "/api/orders")
span.set_attribute("http.target", "/api/orders?page=2")
span.set_attribute("http.user_agent", request.headers["User-Agent"])

# ❌ Wrong (vendor lock-in, breaks queries)
span.set_attribute("method", "POST")
span.set_attribute("status", 200)
```

#### Database Operations

```python
# ✅ Correct
span.set_attribute("db.system", "postgresql")
span.set_attribute("db.name", "orders_db")
span.set_attribute("db.statement", "SELECT * FROM orders WHERE user_id = ?")
span.set_attribute("db.operation", "SELECT")
span.set_attribute("db.sql.table", "orders")

# ❌ Wrong
span.set_attribute("database", "postgresql")
span.set_attribute("query", "SELECT ...")
```

#### Messaging (Queues, Kafka, etc.)

```python
# ✅ Correct
span.set_attribute("messaging.system", "kafka")
span.set_attribute("messaging.destination", "orders.created")
span.set_attribute("messaging.operation", "publish")  # or "receive"
span.set_attribute("messaging.message.id", message_id)

# ❌ Wrong
span.set_attribute("queue", "orders.created")
```

#### RPC/gRPC

```python
# ✅ Correct
span.set_attribute("rpc.system", "grpc")
span.set_attribute("rpc.service", "OrderService")
span.set_attribute("rpc.method", "CreateOrder")
span.set_attribute("rpc.grpc.status_code", 0)
```

### Reference
https://opentelemetry.io/docs/specs/semconv/

## 5. Attribute Cardinality

### High Cardinality = Expensive

**Cardinality:** Number of unique values for an attribute.

- **Low cardinality (good):** `http.method` (5-10 values), `http.status_code` (~60 values)
- **High cardinality (dangerous):** `user.id` (millions), `request.id` (billions)

### ✅ Safe Attributes (Use Freely)

```python
# These have limited unique values
span.set_attribute("http.method", "POST")  # ~10 values
span.set_attribute("http.status_code", 200)  # ~60 values
span.set_attribute("db.operation", "SELECT")  # ~10 values
span.set_attribute("environment", "production")  # ~5 values
span.set_attribute("user.tier", "premium")  # ~5 values
```

### ❌ Dangerous Attributes (Avoid in Metrics, Use Sparingly in Traces)

```python
# ❌ High cardinality - avoid in metric dimensions
request_counter.add(1, {"user.id": user_id})  # Millions of users
request_counter.add(1, {"trace.id": trace_id})  # Billions of traces

# ✅ Safe - use in traces for debugging
span.set_attribute("user.id", user_id)  # OK in traces (sampled)
span.set_attribute("order.id", order_id)  # OK in traces
```

### Guidelines
- **Metrics:** Only use low-cardinality dimensions (< 100 unique values)
- **Traces:** Can use high-cardinality attributes (sampled data)
- **Logs:** Can include anything (point-in-time data)

## 6. Context Propagation

### Always Propagate Context

Context propagation is how trace IDs flow across service boundaries.

#### HTTP (Auto-Handled by Instrumentation)

```python
# Auto-instrumentation handles this for you
from opentelemetry.instrumentation.requests import RequestsInstrumentor
RequestsInstrumentor().instrument()

# This request will automatically include traceparent header
requests.get("https://api.example.com/users")
```

#### Manual HTTP Propagation (When Needed)

```python
from opentelemetry.propagate import inject

headers = {}
inject(headers)  # Adds traceparent, tracestate headers

response = requests.get("https://api.example.com", headers=headers)
```

#### Message Queues (Critical)

```python
from opentelemetry.propagate import inject, extract

# Producer: Inject context
def publish_to_queue(message_body):
    carrier = {}
    inject(carrier)  # Get current trace context

    message = {
        "body": message_body,
        "trace_context": carrier  # Include in message metadata
    }
    queue.publish(message)

# Consumer: Extract context
def consume_from_queue():
    message = queue.consume()
    context = extract(message.get("trace_context", {}))

    # Use extracted context as parent
    with tracer.start_as_current_span("process_message", context=context):
        process(message["body"])
```

### Test Context Propagation

Verify trace IDs flow end-to-end:
1. Make a request to Service A
2. Check trace in UI includes spans from Service A and Service B
3. If not, context propagation is broken

## 7. Performance Optimization

### Use BatchSpanProcessor (Required)

```python
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# ✅ Batches spans, reduces network calls
processor = BatchSpanProcessor(
    exporter,
    max_queue_size=2048,
    schedule_delay_millis=5000,  # Export every 5s
    max_export_batch_size=512
)

# ❌ Don't use SimpleSpanProcessor in production (exports each span immediately)
```

### Tune Batch Processor

```python
# High-throughput service
processor = BatchSpanProcessor(
    exporter,
    max_queue_size=4096,  # Larger buffer
    schedule_delay_millis=10000,  # Export less frequently
    max_export_batch_size=1024  # Larger batches
)

# Low-latency service (need spans quickly)
processor = BatchSpanProcessor(
    exporter,
    max_queue_size=512,
    schedule_delay_millis=1000,  # Export more frequently
    max_export_batch_size=256
)
```

### Measure Instrumentation Overhead

**Target:** < 5% latency increase from instrumentation

```bash
# Benchmark without instrumentation
wrk -t4 -c100 -d30s http://localhost:8000/api

# Benchmark with instrumentation
OTEL_TRACES_SAMPLER=always_on wrk -t4 -c100 -d30s http://localhost:8000/api

# Compare p50, p95, p99 latencies
```

### Reduce Overhead
- Lower sampling rate (fewer spans processed)
- Increase batch export interval (fewer network calls)
- Disable auto-instrumentation for low-value libraries
- Use asynchronous exporters

## 8. Security Best Practices

### Scrub Sensitive Data

```python
# ❌ Bad: PII in attributes
span.set_attribute("user.email", "user@example.com")
span.set_attribute("credit_card.number", "4111-1111-1111-1111")

# ✅ Good: Hash or omit PII
import hashlib
email_hash = hashlib.sha256(email.encode()).hexdigest()
span.set_attribute("user.email.hash", email_hash)

# ✅ Good: Use user ID instead
span.set_attribute("user.id", user_id)
```

### Filter Sensitive SQL

```python
# ❌ Bad: SQL with PII
span.set_attribute("db.statement", "SELECT * FROM users WHERE email = 'user@example.com'")

# ✅ Good: Parameterized query (auto-instrumentation handles this)
span.set_attribute("db.statement", "SELECT * FROM users WHERE email = ?")
```

### Use Collector to Scrub Data

```yaml
# collector-config.yaml
processors:
  attributes:
    actions:
      # Remove sensitive attributes
      - key: user.email
        action: delete
      - key: http.request.header.authorization
        action: delete
      # Redact credit card numbers in attributes
      - key: payment.card.number
        action: update
        value: "[REDACTED]"
```

### TLS for Exporter

```python
# ✅ Use TLS in production
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

exporter = OTLPSpanExporter(
    endpoint="https://collector.example.com:4317",
    insecure=False,  # Enforce TLS
    credentials=ChannelCredentials(...)
)
```

## 9. Collector Deployment (2025 Recommendations)

### Agent + Gateway Pattern (Recommended for Production)

```
App → OTLP → Agent Collector (DaemonSet/Sidecar)
    → OTLP → Gateway Collector (Deployment)
    → Backends
```

**Why:**
- Agent handles batching, retries, local enrichment
- Gateway handles tail sampling, filtering, fan-out
- Isolates apps from backend changes

### Collector Configuration Layers

```yaml
# Agent Collector (local, minimal processing)
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:
    timeout: 5s
    send_batch_size: 512
  memory_limiter:
    check_interval: 1s
    limit_mib: 512
  resource:
    attributes:
      - key: k8s.pod.ip
        from_attribute: net.host.ip
        action: insert

exporters:
  otlp:
    endpoint: gateway-collector:4317

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch, resource]
      exporters: [otlp]
```

```yaml
# Gateway Collector (centralized, advanced processing)
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:
    timeout: 10s
    send_batch_size: 1024
  memory_limiter:
    check_interval: 1s
    limit_mib: 2048
  tail_sampling:
    policies:
      - name: errors
        type: status_code
        status_code: {status_codes: [ERROR]}
      - name: slow
        type: latency
        latency: {threshold_ms: 2000}
      - name: baseline
        type: probabilistic
        probabilistic: {sampling_percentage: 5}
  attributes:
    actions:
      - key: user.email
        action: delete  # Scrub PII

exporters:
  otlp/jaeger:
    endpoint: jaeger:4317
  otlp/datadog:
    endpoint: datadog-agent:4317

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, tail_sampling, attributes, batch]
      exporters: [otlp/jaeger, otlp/datadog]
```

## 10. Logs and Traces Correlation

### Inject Trace Context into Logs

```python
import logging
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Auto-inject trace context
LoggingInstrumentor().instrument(set_logging_format=True)

logging.basicConfig(
    format='%(asctime)s [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s] %(message)s'
)

# Logs automatically include trace_id and span_id
logger.info("Processing order")
```

### Query Logs by Trace ID

In your log aggregation tool (e.g., Elasticsearch, Datadog):

```
trace_id:"d4cda95b652f4a1592b449d5929fda1b"
```

## 11. Testing and Validation

### Local Testing with Console Exporter

```python
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

# Add console exporter for debugging
console_processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(console_processor)
```

### Validate Spans

Check for:
- [ ] Trace ID present
- [ ] Span ID present
- [ ] Parent span ID correct (for child spans)
- [ ] Resource attributes set (`service.name`, `deployment.environment`)
- [ ] Semantic conventions followed (`http.method`, `db.system`, etc.)
- [ ] Status set correctly (OK for success, ERROR for failures)
- [ ] Exceptions recorded (`span.record_exception(e)`)

### Integration Tests

```python
from opentelemetry.sdk.trace.export import InMemorySpanExporter

# Use in-memory exporter for testing
exporter = InMemorySpanExporter()
processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)

# Run code
process_order(order_id="123")

# Validate spans
spans = exporter.get_finished_spans()
assert len(spans) == 3  # process_order, validate_order, charge_payment
assert spans[0].name == "process_order"
assert spans[0].attributes["order.id"] == "123"
```

## 12. Monitoring OpenTelemetry Itself

### Collector Metrics

Enable Prometheus exporter in collector to monitor itself:

```yaml
exporters:
  prometheus:
    endpoint: 0.0.0.0:8888

service:
  telemetry:
    metrics:
      address: 0.0.0.0:8888
```

**Key Metrics:**
- `otelcol_receiver_accepted_spans`: Spans received
- `otelcol_receiver_refused_spans`: Spans rejected (back pressure)
- `otelcol_exporter_sent_spans`: Spans exported
- `otelcol_exporter_send_failed_spans`: Export failures
- `otelcol_processor_dropped_spans`: Spans dropped by sampling

### SDK Metrics (Python)

```python
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader

reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)

# SDK emits internal metrics
```

## Summary Checklist

### Before Production Deployment

- [ ] Resource attributes configured (`service.name`, `service.version`, `deployment.environment`)
- [ ] Sampling configured (not 100% in production)
- [ ] Using `BatchSpanProcessor` (not `SimpleSpanProcessor`)
- [ ] OTLP exporter points to collector (not directly to vendor)
- [ ] Context propagation tested (trace IDs flow across services)
- [ ] Semantic conventions followed (standard attribute names)
- [ ] High-cardinality attributes avoided in metrics
- [ ] PII scrubbed or hashed
- [ ] TLS enabled for exporter
- [ ] Logs correlated with traces (`trace_id` in logs)
- [ ] Instrumentation overhead measured (< 5% latency increase)
- [ ] Collector deployed (agent + gateway pattern)
- [ ] Collector metrics monitored
- [ ] Integration tests written
