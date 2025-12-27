"""
Production-ready OpenTelemetry instrumentation example.
Demonstrates:
- Resource attributes (service name, version, environment)
- OTLP export to collector
- Custom spans with business context
- Metrics (counter, histogram)
- Context propagation
- Error tracking
"""

import os
from flask import Flask, request
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import (
    Resource,
    SERVICE_NAME,
    SERVICE_VERSION,
    DEPLOYMENT_ENVIRONMENT,
)
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.trace import Status, StatusCode
from opentelemetry.propagate import inject

# ----- Configuration -----

# Resource attributes (who is sending telemetry)
resource = Resource(
    attributes={
        SERVICE_NAME: os.getenv("OTEL_SERVICE_NAME", "advanced-app"),
        SERVICE_VERSION: os.getenv("SERVICE_VERSION", "1.0.0"),
        DEPLOYMENT_ENVIRONMENT: os.getenv("ENVIRONMENT", "development"),
        "service.namespace": "demo",
    }
)

# Sampler (10% in production, 100% in dev)
sample_rate = 1.0 if os.getenv("ENVIRONMENT") == "development" else 0.1
sampler = ParentBased(root=TraceIdRatioBased(sample_rate))

# ----- Traces Setup -----

provider = TracerProvider(resource=resource, sampler=sampler)

# OTLP exporter
otlp_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
    insecure=True,
)

processor = BatchSpanProcessor(
    otlp_exporter,
    max_queue_size=2048,
    schedule_delay_millis=5000,
    max_export_batch_size=512,
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# ----- Metrics Setup -----

metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        insecure=True,
    ),
    export_interval_millis=5000,
)

meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

meter = metrics.get_meter(__name__)

# Create metrics
request_counter = meter.create_counter(
    name="http.server.requests",
    description="Total HTTP requests",
    unit="{request}",
)

request_duration = meter.create_histogram(
    name="http.server.request.duration",
    description="HTTP request duration",
    unit="ms",
)

# ----- Flask App -----

app = Flask(__name__)

# Auto-instrument Flask
FlaskInstrumentor().instrument_app(app)


@app.route("/")
def index():
    """Simple endpoint with basic instrumentation."""
    with tracer.start_as_current_span("index_handler"):
        return {"message": "Hello from advanced app!"}


@app.route("/user/<user_id>")
def get_user(user_id):
    """Endpoint demonstrating custom spans and attributes."""
    import time

    start = time.time()

    with tracer.start_as_current_span("get_user_handler") as span:
        # Add business context
        span.set_attribute("user.id", user_id)
        span.set_attribute("user.tier", "premium")

        # Nested span for database query
        with tracer.start_as_current_span("database_query") as db_span:
            db_span.set_attribute("db.system", "postgresql")
            db_span.set_attribute("db.operation", "SELECT")
            db_span.set_attribute("db.statement", "SELECT * FROM users WHERE id = ?")

            # Simulate query
            time.sleep(0.05)
            user = {"id": user_id, "name": "Jane Doe", "tier": "premium"}

            db_span.add_event("Query completed", {"rows_returned": 1})

        # Record metrics
        request_counter.add(
            1, {"http.method": "GET", "http.route": "/user/<user_id>", "http.status_code": 200}
        )
        duration_ms = (time.time() - start) * 1000
        request_duration.record(duration_ms, {"http.route": "/user/<user_id>"})

        return user


@app.route("/order", methods=["POST"])
def create_order():
    """Endpoint demonstrating error tracking and events."""
    import time

    start = time.time()

    with tracer.start_as_current_span("create_order_handler") as span:
        data = request.get_json()
        order_id = data.get("order_id")
        amount = data.get("amount")

        span.set_attribute("order.id", order_id)
        span.set_attribute("order.amount", amount)

        try:
            # Validate order
            with tracer.start_as_current_span("validate_order") as validate_span:
                if amount <= 0:
                    raise ValueError("Invalid order amount")
                validate_span.add_event("Validation passed")

            # Process payment
            with tracer.start_as_current_span("process_payment") as payment_span:
                payment_span.set_attribute("payment.method", "credit_card")
                time.sleep(0.1)  # Simulate payment processing
                payment_span.add_event("Payment successful")

            span.set_status(Status(StatusCode.OK))

            # Record metrics
            request_counter.add(
                1, {"http.method": "POST", "http.route": "/order", "http.status_code": 201}
            )
            duration_ms = (time.time() - start) * 1000
            request_duration.record(duration_ms, {"http.route": "/order"})

            return {"order_id": order_id, "status": "created"}, 201

        except ValueError as e:
            # Record exception in span
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)

            # Record error metric
            request_counter.add(
                1, {"http.method": "POST", "http.route": "/order", "http.status_code": 400}
            )

            return {"error": str(e)}, 400


@app.route("/call-external")
def call_external():
    """Demonstrate context propagation to external services."""
    import requests

    with tracer.start_as_current_span("call_external_handler") as span:
        # Propagate context via headers
        headers = {}
        inject(headers)  # Injects traceparent header

        try:
            # Make external call (context propagates automatically if requests is instrumented)
            response = requests.get(
                "https://jsonplaceholder.typicode.com/posts/1",
                headers=headers,
                timeout=5,
            )

            span.set_attribute("http.status_code", response.status_code)
            return response.json()

        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            return {"error": "External call failed"}, 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
