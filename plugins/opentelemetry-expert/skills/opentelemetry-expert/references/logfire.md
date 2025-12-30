# Pydantic Logfire with OpenTelemetry

Pydantic Logfire is an observability platform built on OpenTelemetry, offering a simplified Python-first experience with automatic Pydantic integration, structured logging, and beautiful visualizations.

## What is Logfire?

**Logfire** is Pydantic's observability solution that:
- Uses OpenTelemetry under the hood (fully compatible)
- Provides automatic Pydantic model tracking
- Offers structured logging with trace correlation
- Includes a beautiful web UI for exploring traces and logs
- Supports standard OTel exporters (can send to any OTel backend)

**Key Advantage:** Logfire abstracts OTel complexity while remaining 100% compatible with OTel standards.

## Installation

```bash
pip install logfire
```

## Basic Setup

### Minimal Configuration

```python
import logfire

# Configure Logfire (uses OTel SDK under the hood)
logfire.configure()

# Use Logfire's simplified API
with logfire.span("process_order", order_id=123):
    logfire.info("Processing order", order_id=123)
    validate_order(123)
```

### Production Configuration

```python
import logfire
from logfire import LogfireConfig

logfire.configure(
    token="your-logfire-token",  # Get from https://logfire.pydantic.dev
    service_name="payment-api",
    service_version="1.2.3",
    environment="production",
    send_to_logfire=True,  # Send to Logfire cloud
    console=False  # Disable console output in prod
)
```

### Environment Variables

```bash
export LOGFIRE_TOKEN=your-token
export LOGFIRE_SERVICE_NAME=payment-api
export LOGFIRE_ENVIRONMENT=production
```

## Logfire vs Raw OpenTelemetry

### Raw OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

resource = Resource(attributes={SERVICE_NAME: "payment-api"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process_order") as span:
    span.set_attribute("order.id", 123)
    validate_order(123)
```

### Logfire (Simplified)

```python
import logfire

logfire.configure()

with logfire.span("process_order", order_id=123):
    validate_order(123)
```

**Logfire handles:**
- SDK initialization
- Exporter configuration
- Resource attributes
- Span processors
- Batch configuration

## Automatic Pydantic Integration

### Pydantic Model Validation Tracking

```python
from pydantic import BaseModel
import logfire

logfire.configure()

# Auto-instrument Pydantic globally
logfire.instrument_pydantic()

class Order(BaseModel):
    order_id: int
    amount: float
    customer_id: str

# Validation is automatically traced
order = Order(order_id=123, amount=99.99, customer_id="cust_123")
# Creates a span showing validation success/failure
```

**What Logfire Captures:**
- Validation success/failure
- Field names and types
- Validation errors (with details)
- Model schema

### Manual Pydantic Logging

```python
import logfire
from pydantic import BaseModel

class Order(BaseModel):
    order_id: int
    amount: float

order = Order(order_id=123, amount=99.99)

# Log Pydantic model (automatically serialized)
logfire.info("Order created", order=order)
# Output: {"order": {"order_id": 123, "amount": 99.99}}
```

## Structured Logging

### Basic Logging

```python
import logfire

# Structured logs with automatic trace correlation
logfire.info("User logged in", user_id=123, ip="192.168.1.1")
logfire.warn("High latency detected", latency_ms=2500, endpoint="/api/orders")
logfire.error("Payment failed", order_id=123, error="card_declined")
```

### Logging Inside Spans

```python
with logfire.span("process_payment", order_id=123):
    logfire.info("Charging card")

    try:
        charge_card()
        logfire.info("Payment successful", amount=99.99)
    except Exception as e:
        logfire.error("Payment failed", error=str(e))
        raise
```

**Automatic Features:**
- Logs include `trace_id` and `span_id` (correlation)
- Structured fields (not string concatenation)
- Searchable in Logfire UI

## Span Creation

### Basic Spans

```python
import logfire

with logfire.span("database_query", table="orders"):
    result = db.execute("SELECT * FROM orders")
```

### Nested Spans

```python
with logfire.span("process_order", order_id=123):
    with logfire.span("validate_order"):
        validate_order()

    with logfire.span("charge_payment", amount=99.99):
        charge_payment()
```

### Span Attributes

```python
with logfire.span(
    "api_request",
    method="POST",
    endpoint="/api/orders",
    status_code=201
):
    process_request()
```

### Async Spans

```python
async def fetch_user(user_id):
    async with logfire.span("fetch_user", user_id=user_id):
        user = await db.fetch_user(user_id)
        return user
```

## Auto-Instrumentation

### FastAPI

```python
from fastapi import FastAPI
import logfire

app = FastAPI()

# Auto-instrument FastAPI (traces all endpoints)
logfire.instrument_fastapi(app)

@app.get("/orders")
def get_orders():
    return {"orders": []}
```

**Captures:**
- HTTP method, route, status code
- Request/response headers (configurable)
- Query parameters
- Request body (opt-in)
- Latency

### SQLAlchemy

```python
from sqlalchemy import create_engine
import logfire

engine = create_engine("postgresql://user:pass@localhost/db")

# Auto-instrument SQLAlchemy
logfire.instrument_sqlalchemy(engine=engine)

# All queries are now traced
result = engine.execute("SELECT * FROM orders")
```

**Captures:**
- SQL statements (parameterized)
- Table names
- Query duration
- Rows affected

### Requests (HTTP Client)

```python
import logfire
import requests

# Auto-instrument requests library
logfire.instrument_requests()

# All HTTP requests are traced
response = requests.get("https://api.example.com/users")
```

**Captures:**
- HTTP method, URL
- Status code
- Request/response headers
- Latency

### HTTPX

```python
import logfire
import httpx

# Auto-instrument HTTPX
logfire.instrument_httpx()

async with httpx.AsyncClient() as client:
    response = await client.get("https://api.example.com/users")
```

### Redis

```python
import logfire
import redis

# Auto-instrument Redis
logfire.instrument_redis()

client = redis.Redis(host='localhost', port=6379)
client.set('key', 'value')  # Traced automatically
```

### Celery

```python
import logfire
from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379')

# Auto-instrument Celery
logfire.instrument_celery(app)

@app.task
def process_order(order_id):
    # Task execution is traced
    pass
```

## Metrics

```python
import logfire

# Create counter
orders_counter = logfire.metric_counter(
    "orders.processed",
    unit="orders",
    description="Total orders processed"
)

# Increment counter
orders_counter.add(1, {"status": "success"})

# Create histogram
latency_histogram = logfire.metric_histogram(
    "request.duration",
    unit="ms",
    description="Request duration"
)

latency_histogram.record(125.5, {"route": "/api/orders"})
```

## Exporting to Other Backends

Logfire uses OTel under the hood, so you can export to any OTel-compatible backend.

### Export to Jaeger

```python
import logfire
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logfire.configure(send_to_logfire=False)

# Add custom exporter
exporter = OTLPSpanExporter(endpoint="http://jaeger:4317")
processor = BatchSpanProcessor(exporter)
logfire._tracer_provider.add_span_processor(processor)
```

### Export to Multiple Backends

```python
import logfire
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logfire.configure(send_to_logfire=True)  # Send to Logfire

# Also send to Jaeger
jaeger_exporter = OTLPSpanExporter(endpoint="http://jaeger:4317")
jaeger_processor = BatchSpanProcessor(jaeger_exporter)
logfire._tracer_provider.add_span_processor(jaeger_processor)
```

## Testing and Development

### Console Output (Local Dev)

```python
import logfire

logfire.configure(
    send_to_logfire=False,  # Don't send to cloud
    console=True  # Print to console
)
```

### Testing with InMemory Exporter

```python
import logfire
from opentelemetry.sdk.trace.export import InMemorySpanExporter

exporter = InMemorySpanExporter()
logfire.configure(send_to_logfire=False)

# Add in-memory exporter for testing
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
processor = SimpleSpanProcessor(exporter)
logfire._tracer_provider.add_span_processor(processor)

# Run code
with logfire.span("test"):
    pass

# Inspect spans
spans = exporter.get_finished_spans()
assert len(spans) == 1
assert spans[0].name == "test"
```

## Sampling

```python
import logfire
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

# Sample 10% of traces
logfire.configure(
    sampling=TraceIdRatioBased(0.1)
)
```

## Advanced: Direct OTel SDK Access

Logfire uses OTel SDK internally. You can access it directly for advanced use cases.

```python
import logfire
from opentelemetry import trace

logfire.configure()

# Access underlying OTel tracer
tracer = trace.get_tracer(__name__)

# Use raw OTel API
with tracer.start_as_current_span("custom_span") as span:
    span.set_attribute("custom.attribute", "value")
```

## Best Practices with Logfire

### 1. Use Structured Logging

```python
# ❌ Bad: String concatenation
logfire.info(f"User {user_id} logged in")

# ✅ Good: Structured fields
logfire.info("User logged in", user_id=user_id)
```

### 2. Leverage Pydantic Integration

```python
# ✅ Auto-instrument Pydantic globally
logfire.instrument_pydantic()

# Models are automatically validated and tracked
class Order(BaseModel):
    order_id: int
    amount: float

order = Order(order_id=123, amount=99.99)  # Traced automatically
```

### 3. Add Business Context

```python
with logfire.span(
    "process_order",
    order_id=order.order_id,
    customer_tier=customer.tier,
    total_amount=order.total
):
    process_order(order)
```

### 4. Use Auto-Instrumentation

```python
# ✅ Instrument all common libraries at startup
logfire.instrument_fastapi(app)
logfire.instrument_sqlalchemy(engine)
logfire.instrument_requests()
logfire.instrument_redis()
```

### 5. Correlate Logs with Traces

```python
# Logs inside spans are automatically correlated
with logfire.span("process_payment"):
    logfire.info("Charging card")  # Includes trace_id, span_id
    charge_card()
    logfire.info("Payment successful")
```

## Logfire UI Features

- **Trace Explorer:** Visualize distributed traces
- **Log Explorer:** Search structured logs with full-text search
- **Live Tail:** Real-time log streaming
- **Pydantic Validation Tracking:** See model validation in UI
- **SQL Query Analysis:** Formatted SQL with execution time
- **Error Tracking:** Grouped exceptions with stack traces

## When to Use Logfire vs Raw OTel

### Use Logfire When:
- Building Python applications (especially with Pydantic)
- Want simplified setup and beautiful UI
- Need automatic Pydantic integration
- Prefer structured logging out-of-the-box
- Don't want to manage OTel SDK complexity

### Use Raw OTel When:
- Non-Python applications
- Need maximum control over SDK configuration
- Custom sampling logic beyond what Logfire exposes
- Existing OTel infrastructure

### Hybrid Approach:
Use Logfire in Python apps, but export to your existing OTel Collector/backends alongside Logfire cloud.

## Migration: Raw OTel to Logfire

### Before (Raw OTel)

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

resource = Resource(attributes={SERVICE_NAME: "payment-api"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process_order") as span:
    span.set_attribute("order.id", 123)
    validate_order(123)
```

### After (Logfire)

```python
import logfire

logfire.configure()

with logfire.span("process_order", order_id=123):
    validate_order(123)
```

**Benefits:**
- 90% less boilerplate
- Automatic trace correlation in logs
- Beautiful UI
- Pydantic integration

## Resources

- Logfire Documentation: https://logfire.pydantic.dev
- Logfire GitHub: https://github.com/pydantic/logfire
- Logfire vs OTel Comparison: https://logfire.pydantic.dev/docs/why-logfire/
