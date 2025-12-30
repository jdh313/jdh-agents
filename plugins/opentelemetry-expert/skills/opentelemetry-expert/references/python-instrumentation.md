# Python OpenTelemetry Instrumentation Guide

## Installation

### Option 1: Auto-Instrumentation (Recommended for Quick Start)

```bash
# Install core packages
pip install opentelemetry-distro opentelemetry-exporter-otlp

# Auto-detect and install instrumentation for installed packages
opentelemetry-bootstrap -a install

# Run your application with auto-instrumentation
opentelemetry-instrument \
    --traces_exporter otlp \
    --metrics_exporter otlp \
    --service_name my-service \
    --exporter_otlp_endpoint http://localhost:4317 \
    python app.py
```

### Option 2: Manual SDK Setup (Recommended for Production)

```bash
# Install SDK and exporter
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp

# Install specific instrumentations
pip install opentelemetry-instrumentation-flask
pip install opentelemetry-instrumentation-requests
pip install opentelemetry-instrumentation-sqlalchemy
pip install opentelemetry-instrumentation-redis
```

## Basic Setup (Manual Instrumentation)

### Minimal Trace Setup

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

# Configure resource (service identity)
resource = Resource(attributes={
    SERVICE_NAME: "my-service"
})

# Set up tracer provider
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317"))
provider.add_span_processor(processor)

# Register as global tracer provider
trace.set_tracer_provider(provider)

# Get a tracer instance
tracer = trace.get_tracer(__name__)
```

### Production-Ready Setup

```python
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION, DEPLOYMENT_ENVIRONMENT
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased

# Resource attributes (who is sending the telemetry)
resource = Resource(attributes={
    SERVICE_NAME: os.getenv("SERVICE_NAME", "my-service"),
    SERVICE_VERSION: os.getenv("SERVICE_VERSION", "0.1.0"),
    DEPLOYMENT_ENVIRONMENT: os.getenv("ENVIRONMENT", "development"),
    "service.namespace": os.getenv("SERVICE_NAMESPACE", "default"),
})

# Sampler (control which traces to record)
# Sample 10% in production, 100% in dev
sample_rate = 1.0 if os.getenv("ENVIRONMENT") == "development" else 0.1
sampler = ParentBased(root=TraceIdRatioBased(sample_rate))

# Tracer provider
provider = TracerProvider(resource=resource, sampler=sampler)

# Exporter (where to send traces)
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
    insecure=True  # Use TLS in production
)

# Span processor (batch for efficiency)
processor = BatchSpanProcessor(
    otlp_exporter,
    max_queue_size=2048,
    schedule_delay_millis=5000,  # Export every 5 seconds
    max_export_batch_size=512
)
provider.add_span_processor(processor)

# Console exporter for local debugging
if os.getenv("ENVIRONMENT") == "development":
    console_processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(console_processor)

# Register globally
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)
```

## Framework-Specific Auto-Instrumentation

### Flask

```python
from flask import Flask
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = Flask(__name__)

# Auto-instrument Flask
FlaskInstrumentor().instrument_app(app)

@app.route("/")
def hello():
    return "Hello World"
```

### FastAPI

```python
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()

# Auto-instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

### Django

```python
# In settings.py or apps.py
from opentelemetry.instrumentation.django import DjangoInstrumentor

DjangoInstrumentor().instrument()
```

### Requests Library (HTTP Client)

```python
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Auto-instrument all requests calls
RequestsInstrumentor().instrument()

# Now all requests.get/post calls create spans automatically
import requests
response = requests.get("https://api.example.com/users")
```

### SQLAlchemy (Database)

```python
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Auto-instrument SQLAlchemy engine
from sqlalchemy import create_engine
engine = create_engine("postgresql://user:pass@localhost/db")
SQLAlchemyInstrumentor().instrument(engine=engine)
```

### Redis

```python
from opentelemetry.instrumentation.redis import RedisInstrumentor

# Auto-instrument all Redis clients
RedisInstrumentor().instrument()

import redis
client = redis.Redis(host='localhost', port=6379)
client.set('key', 'value')  # Creates a span automatically
```

### Celery

```python
from opentelemetry.instrumentation.celery import CeleryInstrumentor

# Auto-instrument Celery
CeleryInstrumentor().instrument()

# Celery tasks now create spans
from celery import Celery
app = Celery('tasks', broker='redis://localhost:6379')

@app.task
def add(x, y):
    return x + y
```

## Manual Span Creation

### Basic Span

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def process_order(order_id):
    with tracer.start_as_current_span("process_order") as span:
        # Span is active within this context
        span.set_attribute("order.id", order_id)

        # Do work
        result = validate_order(order_id)

        span.add_event("Order validated", {"result": result})
        return result
```

### Nested Spans (Parent-Child Relationship)

```python
def process_order(order_id):
    with tracer.start_as_current_span("process_order") as parent_span:
        parent_span.set_attribute("order.id", order_id)

        # Child span 1
        with tracer.start_as_current_span("validate_order") as child_span:
            child_span.set_attribute("validation.type", "fraud_check")
            validate_order(order_id)

        # Child span 2
        with tracer.start_as_current_span("charge_payment") as child_span:
            child_span.set_attribute("payment.method", "credit_card")
            charge_payment(order_id)
```

### Span with Attributes

```python
with tracer.start_as_current_span("database_query") as span:
    # Semantic conventions for database operations
    span.set_attribute("db.system", "postgresql")
    span.set_attribute("db.name", "mydb")
    span.set_attribute("db.statement", "SELECT * FROM users WHERE id = ?")
    span.set_attribute("db.operation", "SELECT")

    # Business attributes
    span.set_attribute("user.id", user_id)
    span.set_attribute("user.tier", "premium")
```

### Span with Events

```python
with tracer.start_as_current_span("order_processing") as span:
    span.add_event("Order received")

    validate_order()
    span.add_event("Validation complete", {"validation_status": "passed"})

    charge_payment()
    span.add_event("Payment charged", {"amount": 99.99, "currency": "USD"})
```

### Span with Status

```python
from opentelemetry.trace import Status, StatusCode

with tracer.start_as_current_span("risky_operation") as span:
    try:
        result = risky_operation()
        span.set_status(Status(StatusCode.OK))
    except Exception as e:
        span.set_status(Status(StatusCode.ERROR, str(e)))
        span.record_exception(e)  # Records exception details
        raise
```

### Span Kind

```python
from opentelemetry.trace import SpanKind

# CLIENT: Making an outbound request
with tracer.start_as_current_span("http_request", kind=SpanKind.CLIENT) as span:
    requests.get("https://api.example.com")

# SERVER: Handling an inbound request (auto-instrumentation usually handles this)
with tracer.start_as_current_span("handle_request", kind=SpanKind.SERVER) as span:
    process_request()

# INTERNAL: Internal operation (default)
with tracer.start_as_current_span("business_logic", kind=SpanKind.INTERNAL) as span:
    do_work()

# PRODUCER: Sending a message to a queue
with tracer.start_as_current_span("publish_message", kind=SpanKind.PRODUCER) as span:
    queue.publish(message)

# CONSUMER: Receiving a message from a queue
with tracer.start_as_current_span("consume_message", kind=SpanKind.CONSUMER) as span:
    message = queue.consume()
```

## Context Propagation

### HTTP Context Propagation (Manual)

```python
from opentelemetry.propagate import inject, extract
import requests

# Outgoing HTTP request - inject trace context into headers
def make_request(url):
    headers = {}
    inject(headers)  # Injects traceparent, tracestate headers

    response = requests.get(url, headers=headers)
    return response

# Incoming HTTP request - extract trace context from headers
def handle_request(request):
    # Extract context from incoming headers
    context = extract(request.headers)

    # Use extracted context as parent
    with tracer.start_as_current_span("handle_request", context=context) as span:
        process_request()
```

### Message Queue Context Propagation

```python
from opentelemetry.propagate import inject, extract

# Producer - inject context into message metadata
def publish_message(queue, message_body):
    metadata = {}
    inject(metadata)  # Add trace context to metadata

    message = {
        "body": message_body,
        "metadata": metadata
    }
    queue.publish(message)

# Consumer - extract context from message metadata
def consume_message(queue):
    message = queue.consume()
    context = extract(message["metadata"])

    with tracer.start_as_current_span("process_message", context=context) as span:
        process(message["body"])
```

## Metrics (OpenTelemetry Metrics API)

### Setup Metrics

```python
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Set up meter provider
exporter = OTLPMetricExporter(endpoint="http://localhost:4317")
reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
provider = MeterProvider(metric_readers=[reader], resource=resource)
metrics.set_meter_provider(provider)

# Get a meter
meter = metrics.get_meter(__name__)
```

### Counter

```python
# Create counter
request_counter = meter.create_counter(
    name="http.server.requests",
    description="Total HTTP requests",
    unit="{request}"
)

# Increment counter
def handle_request(method, route, status_code):
    request_counter.add(1, {
        "http.method": method,
        "http.route": route,
        "http.status_code": status_code
    })
```

### Histogram

```python
# Create histogram for request duration
request_duration = meter.create_histogram(
    name="http.server.request.duration",
    description="HTTP request duration",
    unit="ms"
)

# Record value
import time

def handle_request(route):
    start = time.time()
    process_request()
    duration_ms = (time.time() - start) * 1000

    request_duration.record(duration_ms, {"http.route": route})
```

### Gauge (ObservableGauge)

```python
import psutil

# Create observable gauge for CPU usage
def get_cpu_usage():
    return psutil.cpu_percent()

cpu_gauge = meter.create_observable_gauge(
    name="system.cpu.usage",
    description="CPU usage percentage",
    unit="%",
    callbacks=[lambda: [(get_cpu_usage(), {})]]
)
```

### UpDownCounter

```python
# Track active connections
active_connections = meter.create_up_down_counter(
    name="http.server.active_connections",
    description="Active HTTP connections",
    unit="{connection}"
)

def on_connection_open():
    active_connections.add(1)

def on_connection_close():
    active_connections.add(-1)
```

## Logging Integration

### Correlate Logs with Traces

```python
import logging
from opentelemetry import trace
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Auto-inject trace context into logs
LoggingInstrumentor().instrument(set_logging_format=True)

# Configure logging to include trace context
logging.basicConfig(
    format='%(asctime)s %(levelname)s [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s] %(message)s'
)

logger = logging.getLogger(__name__)

def process_order(order_id):
    with tracer.start_as_current_span("process_order") as span:
        # Logs will automatically include trace_id and span_id
        logger.info(f"Processing order {order_id}")

        try:
            validate_order(order_id)
        except Exception as e:
            logger.error(f"Order validation failed: {e}")
            raise
```

### Structured Logging with Trace Context

```python
import structlog
from opentelemetry import trace

def add_trace_context(logger, log_method, event_dict):
    """Add trace context to structured logs"""
    span = trace.get_current_span()
    if span:
        span_context = span.get_span_context()
        event_dict["trace_id"] = format(span_context.trace_id, "032x")
        event_dict["span_id"] = format(span_context.span_id, "016x")
    return event_dict

structlog.configure(
    processors=[
        add_trace_context,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

def process_order(order_id):
    with tracer.start_as_current_span("process_order"):
        logger.info("processing_order", order_id=order_id)
```

## Environment Variables (Alternative to Code Config)

Instead of configuring in code, use environment variables:

```bash
# Resource attributes
export OTEL_SERVICE_NAME=my-service
export OTEL_SERVICE_VERSION=1.0.0
export OTEL_RESOURCE_ATTRIBUTES="deployment.environment=production,service.namespace=payments"

# Exporter configuration
export OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc  # or http/protobuf
export OTEL_EXPORTER_OTLP_HEADERS="api-key=secret"

# Trace configuration
export OTEL_TRACES_SAMPLER=traceidratio
export OTEL_TRACES_SAMPLER_ARG=0.1  # Sample 10%

# Propagator
export OTEL_PROPAGATORS=tracecontext,baggage  # W3C (default)
# export OTEL_PROPAGATORS=b3multi  # Zipkin B3
# export OTEL_PROPAGATORS=jaeger  # Jaeger

# Run with auto-instrumentation
opentelemetry-instrument python app.py
```

## Best Practices

### 1. Use Semantic Conventions
Follow standard naming for common operations:
- HTTP: `http.method`, `http.status_code`, `http.route`
- Database: `db.system`, `db.name`, `db.statement`
- Messaging: `messaging.system`, `messaging.destination`

Reference: https://opentelemetry.io/docs/specs/semconv/

### 2. Avoid High Cardinality in Metric Dimensions
❌ **Bad:** `request_counter.add(1, {"user.id": user_id})`  # Millions of unique users
✅ **Good:** `request_counter.add(1, {"user.tier": "premium"})`  # Few unique tiers

### 3. Use Batch Processor
Always use `BatchSpanProcessor` in production, not `SimpleSpanProcessor`.

### 4. Set Resource Attributes
Always set `service.name`, `service.version`, and `deployment.environment`.

### 5. Sample Aggressively in High-Traffic Apps
Start with 1-10% sampling in production to control costs.

### 6. Correlate Logs with Traces
Inject `trace_id` and `span_id` into logs for easy correlation.

### 7. Add Business Context
Don't just instrument framework code—add spans for business operations with business attributes.

### 8. Test Locally
Use console exporter to verify spans before deploying.

### 9. Use Collector
Send to OTel Collector (OTLP), not directly to vendors.

### 10. Monitor Instrumentation Overhead
Check that latency increase is < 5% (use benchmarks).

## Common Pitfalls

1. **Not propagating context in async workflows** (Celery, queues)
2. **Creating too many spans** (span per iteration in a loop)
3. **Using high cardinality attributes in metrics** (`user.id`, `request.id`)
4. **Not setting span status on errors** (use `span.set_status(StatusCode.ERROR)`)
5. **Forgetting to record exceptions** (use `span.record_exception(e)`)
6. **Not testing instrumentation locally** (always verify with console exporter)
