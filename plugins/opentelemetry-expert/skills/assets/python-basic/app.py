"""
Minimal OpenTelemetry instrumentation example.
Demonstrates auto-instrumentation with Flask and console export for local testing.
"""

from flask import Flask
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# Configure OpenTelemetry SDK
resource = Resource(attributes={SERVICE_NAME: "flask-app"})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Create Flask app
app = Flask(__name__)

# Auto-instrument Flask
FlaskInstrumentor().instrument_app(app)

# Get tracer for manual instrumentation
tracer = trace.get_tracer(__name__)


@app.route("/")
def hello():
    with tracer.start_as_current_span("hello_handler"):
        return {"message": "Hello, World!"}


@app.route("/user/<user_id>")
def get_user(user_id):
    with tracer.start_as_current_span("get_user") as span:
        span.set_attribute("user.id", user_id)
        # Simulate database query
        user = {"id": user_id, "name": "John Doe"}
        return user


if __name__ == "__main__":
    app.run(debug=True, port=5000)
