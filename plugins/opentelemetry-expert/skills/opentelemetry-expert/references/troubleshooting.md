# OpenTelemetry Troubleshooting Guide

Common issues and how to resolve them.

## 1. No Traces Appearing in Backend

### Symptoms
- Application runs without errors
- No traces visible in Jaeger/Datadog/New Relic

### Debugging Steps

#### Step 1: Verify Instrumentation is Active

```python
from opentelemetry import trace

# Check if tracer provider is set
provider = trace.get_tracer_provider()
print(f"Tracer provider: {provider}")  # Should NOT be ProxyTracerProvider

# Create a test span
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("test_span") as span:
    span.set_attribute("test", "value")
    print(f"Span created: {span}")
```

**If using auto-instrumentation:**
```bash
# Verify environment variables
echo $OTEL_SERVICE_NAME
echo $OTEL_EXPORTER_OTLP_ENDPOINT

# Check that opentelemetry-instrument is wrapping your app
opentelemetry-instrument --log-level debug python app.py
```

#### Step 2: Test with Console Exporter

```python
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

# Add console exporter to see spans locally
console_processor = BatchSpanProcessor(ConsoleSpanExporter())
trace.get_tracer_provider().add_span_processor(console_processor)
```

**Expected output:**
```json
{
    "name": "test_span",
    "context": {"trace_id": "0x...", "span_id": "0x..."},
    "attributes": {"test": "value"}
}
```

#### Step 3: Verify Exporter Endpoint

```bash
# Test collector connectivity
curl http://localhost:4317  # gRPC (should refuse connection, but proves port is open)
curl http://localhost:4318  # HTTP

# Check collector logs
docker logs otel-collector
```

**Common issues:**
- Wrong endpoint (`http://localhost:4317` vs `localhost:4317` for gRPC)
- Wrong protocol (gRPC vs HTTP)
- Firewall blocking port
- Collector not running

#### Step 4: Check Sampling

```python
from opentelemetry import trace

# Verify sampler is not AlwaysOff
provider = trace.get_tracer_provider()
print(f"Sampler: {provider._active_span_processor._sampler}")
```

**If sampling rate is too low:**
```bash
# Force 100% sampling temporarily
export OTEL_TRACES_SAMPLER=always_on
```

#### Step 5: Check Exporter Errors

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable OTel SDK debug logging
logging.getLogger("opentelemetry").setLevel(logging.DEBUG)
```

**Common errors:**
```
Failed to export spans: [Errno 111] Connection refused
```
→ Collector is not running or wrong endpoint

```
Failed to export spans: Deadline Exceeded
```
→ Collector is overloaded or network issue

## 2. Traces Missing Spans from Some Services

### Symptoms
- Some services appear in traces
- Other services are missing

### Causes

#### Cause 1: Context Propagation Broken

**Check headers:**
```python
from opentelemetry.propagate import inject

headers = {}
inject(headers)
print(headers)  # Should include: {'traceparent': '00-...'}
```

**Verify propagation in HTTP client:**
```python
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Ensure instrumentation is enabled
RequestsInstrumentor().instrument()

# Make request (should auto-inject headers)
import requests
response = requests.get("http://api.example.com")
```

**Check propagator configuration:**
```python
from opentelemetry.propagate import get_global_textmap

propagator = get_global_textmap()
print(f"Propagator: {propagator}")  # Should be TraceContextTextMapPropagator
```

#### Cause 2: Service Not Instrumented

**Verify auto-instrumentation is active:**
```bash
# List installed instrumentation packages
pip list | grep opentelemetry-instrumentation
```

**Enable specific instrumentation:**
```python
from opentelemetry.instrumentation.flask import FlaskInstrumentor

FlaskInstrumentor().instrument_app(app)
```

#### Cause 3: Async / Background Tasks

**For Celery, manually propagate context:**
```python
from celery import Celery
from opentelemetry.instrumentation.celery import CeleryInstrumentor

# Instrument Celery
CeleryInstrumentor().instrument()

# For manual propagation (if auto-instrumentation doesn't work):
from opentelemetry.propagate import inject, extract

# In producer
def send_task():
    carrier = {}
    inject(carrier)
    app.send_task("process", kwargs={"trace_context": carrier})

# In consumer
@app.task
def process(trace_context):
    context = extract(trace_context)
    with tracer.start_as_current_span("process_task", context=context):
        do_work()
```

## 3. High Latency / Performance Issues

### Symptoms
- Application latency increased after adding OTel
- High CPU usage

### Debugging Steps

#### Step 1: Measure Overhead

```bash
# Benchmark without instrumentation
wrk -t4 -c100 -d30s http://localhost:8000

# Benchmark with instrumentation
OTEL_TRACES_SAMPLER=always_on wrk -t4 -c100 -d30s http://localhost:8000
```

**Target:** < 5% latency increase

#### Step 2: Use BatchSpanProcessor (Not SimpleSpanProcessor)

```python
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# ❌ Don't use SimpleSpanProcessor in production
# from opentelemetry.sdk.trace.export import SimpleSpanProcessor

processor = BatchSpanProcessor(exporter)  # ✅ Batches spans
```

#### Step 3: Reduce Sampling Rate

```bash
# Sample only 10% of traces
export OTEL_TRACES_SAMPLER=traceidratio
export OTEL_TRACES_SAMPLER_ARG=0.1
```

#### Step 4: Tune Batch Processor

```python
processor = BatchSpanProcessor(
    exporter,
    max_queue_size=2048,  # Increase buffer
    schedule_delay_millis=10000,  # Export less frequently
    max_export_batch_size=512
)
```

#### Step 5: Disable Unnecessary Instrumentation

```bash
# Don't auto-install all instrumentations
# opentelemetry-bootstrap -a install  # ❌ Installs everything

# Install only what you need
pip install opentelemetry-instrumentation-flask
pip install opentelemetry-instrumentation-requests
```

## 4. Collector Issues

### Collector Not Receiving Data

**Check collector logs:**
```bash
docker logs otel-collector

# Look for:
# "Everything is ready. Begin running and processing data."
```

**Verify collector config:**
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317  # ✅ Correct
      # endpoint: localhost:4317  # ❌ Wrong (won't accept external connections)
```

**Test with curl:**
```bash
# gRPC (should refuse connection but proves port is open)
curl http://localhost:4317

# HTTP
curl -X POST http://localhost:4318/v1/traces \
  -H "Content-Type: application/json" \
  -d '{"resourceSpans": []}'
```

### Collector Dropping Spans

**Check collector metrics:**
```bash
curl http://localhost:8888/metrics | grep dropped
```

**Common causes:**
- `memory_limiter` processor hitting limit
- Exporter failures (backend unreachable)
- Buffer overflow (too many spans, not enough export capacity)

**Solutions:**
```yaml
processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 2048  # Increase memory limit

  batch:
    timeout: 10s
    send_batch_size: 1024  # Increase batch size for efficiency
```

### Collector OOMKilled (Kubernetes)

**Increase memory limits:**
```yaml
# deployment.yaml
resources:
  limits:
    memory: 2Gi  # Increase from 512Mi
  requests:
    memory: 1Gi
```

**Enable memory_limiter:**
```yaml
processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 1536  # 75% of 2Gi limit
```

## 5. Context Not Propagating

### HTTP Context Propagation

**Verify headers are injected:**
```python
import requests
from opentelemetry.propagate import inject

headers = {}
inject(headers)
print(headers)  # {'traceparent': '00-...', 'tracestate': '...'}

response = requests.get("https://api.example.com", headers=headers)
```

**Check server is extracting context:**
```python
from opentelemetry.propagate import extract
from flask import request

@app.route("/api/endpoint")
def endpoint():
    # Extract context from headers
    context = extract(request.headers)
    print(f"Extracted context: {context}")

    with tracer.start_as_current_span("endpoint", context=context):
        return "OK"
```

### Message Queue Context Propagation

**Producer: Inject into message metadata**
```python
from opentelemetry.propagate import inject

carrier = {}
inject(carrier)

message = {
    "body": "...",
    "metadata": carrier  # Include trace context
}
queue.publish(message)
```

**Consumer: Extract from metadata**
```python
from opentelemetry.propagate import extract

message = queue.consume()
context = extract(message.get("metadata", {}))

with tracer.start_as_current_span("process_message", context=context):
    process(message["body"])
```

## 6. Incorrect Trace Structure

### Symptoms
- All spans are root spans (no parent-child relationship)
- Trace is fragmented

### Cause: Not Using Context Manager

**❌ Wrong:**
```python
span = tracer.start_span("parent")
child_span = tracer.start_span("child")  # Not a child!
span.end()
child_span.end()
```

**✅ Correct:**
```python
with tracer.start_as_current_span("parent") as parent:
    with tracer.start_as_current_span("child") as child:
        # child is automatically a child of parent
        pass
```

## 7. Semantic Convention Violations

### Symptoms
- Queries like `http.method:POST` don't work
- Dashboards broken after switching vendors

### Fix: Use Standard Attribute Names

**❌ Wrong:**
```python
span.set_attribute("method", "POST")
span.set_attribute("status", 200)
```

**✅ Correct:**
```python
span.set_attribute("http.method", "POST")
span.set_attribute("http.status_code", 200)
```

**Reference:** https://opentelemetry.io/docs/specs/semconv/

## 8. Logs Not Correlated with Traces

### Symptoms
- Logs don't include `trace_id` / `span_id`

### Fix: Instrument Logging

```python
from opentelemetry.instrumentation.logging import LoggingInstrumentor

LoggingInstrumentor().instrument(set_logging_format=True)

import logging
logging.basicConfig(
    format='%(asctime)s [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s] %(message)s'
)
```

## 9. Cardinality Explosion (Metrics)

### Symptoms
- Metrics backend complains about high cardinality
- Queries slow or timing out

### Cause: High-Cardinality Dimensions

**❌ Wrong:**
```python
counter.add(1, {"user.id": user_id})  # Millions of unique users
counter.add(1, {"request.id": request_id})  # Billions of requests
```

**✅ Correct:**
```python
counter.add(1, {"user.tier": "premium"})  # ~5 unique values
counter.add(1, {"http.route": "/api/orders"})  # ~100 unique values
```

**Rule:** Metric dimensions should have < 100 unique values.

## 10. Missing Exceptions in Traces

### Symptoms
- Exception occurs but span status is OK

### Fix: Record Exceptions

```python
with tracer.start_as_current_span("operation") as span:
    try:
        risky_operation()
    except Exception as e:
        span.set_status(Status(StatusCode.ERROR, str(e)))
        span.record_exception(e)  # ✅ Record exception details
        raise
```

## Debugging Tools

### 1. OTEL_LOG_LEVEL

```bash
export OTEL_LOG_LEVEL=debug
opentelemetry-instrument python app.py
```

### 2. OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED

```bash
# Disable log instrumentation if causing issues
export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=false
```

### 3. Collector Debug Exporter

```yaml
exporters:
  logging:
    loglevel: debug

service:
  pipelines:
    traces:
      exporters: [logging]  # Print spans to console
```

### 4. InMemorySpanExporter (Testing)

```python
from opentelemetry.sdk.trace.export import InMemorySpanExporter

exporter = InMemorySpanExporter()
processor = BatchSpanProcessor(exporter)
provider.add_span_processor(processor)

# Run code
process_order()

# Inspect spans
spans = exporter.get_finished_spans()
for span in spans:
    print(f"{span.name}: {span.attributes}")
```

## Quick Checklist

When traces aren't working:

- [ ] Service name configured (`OTEL_SERVICE_NAME`)
- [ ] Exporter endpoint correct (`OTEL_EXPORTER_OTLP_ENDPOINT`)
- [ ] Collector is running and reachable
- [ ] Sampler is not `AlwaysOff`
- [ ] Using `BatchSpanProcessor` (not `SimpleSpanProcessor`)
- [ ] Context propagation configured (headers injected/extracted)
- [ ] Auto-instrumentation enabled for frameworks in use
- [ ] Console exporter works (proves SDK is active)
- [ ] Collector logs show no errors
- [ ] Semantic conventions followed
