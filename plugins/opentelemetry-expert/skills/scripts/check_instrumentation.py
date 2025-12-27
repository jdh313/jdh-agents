#!/usr/bin/env python3
"""
Check if a Python application is properly instrumented with OpenTelemetry.

Usage:
    python check_instrumentation.py
    PYTHONPATH=. python check_instrumentation.py  # If script is in project
"""

import sys
import os


def check_environment_variables():
    """Check if required OTel environment variables are set."""
    print("🔍 Checking environment variables...\n")

    required_vars = {
        "OTEL_SERVICE_NAME": "Identifies your service (required)",
    }

    recommended_vars = {
        "OTEL_EXPORTER_OTLP_ENDPOINT": "Where to send telemetry (default: http://localhost:4317)",
        "OTEL_RESOURCE_ATTRIBUTES": "Additional resource attributes (e.g., deployment.environment)",
        "OTEL_TRACES_SAMPLER": "Sampling strategy (default: parentbased_always_on)",
    }

    issues = []

    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}={value}")
        else:
            print(f"❌ {var} not set - {description}")
            issues.append(f"Missing required: {var}")

    print()

    for var, description in recommended_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}={value}")
        else:
            print(f"⚠️  {var} not set - {description}")

    return issues


def check_sdk_initialization():
    """Check if OTel SDK is initialized."""
    print("\n🔍 Checking OpenTelemetry SDK initialization...\n")

    try:
        from opentelemetry import trace
    except ImportError:
        print("❌ OpenTelemetry SDK not installed")
        print("   Install: pip install opentelemetry-api opentelemetry-sdk")
        return ["SDK not installed"]

    issues = []

    # Check tracer provider
    provider = trace.get_tracer_provider()
    provider_class = provider.__class__.__name__

    if provider_class == "ProxyTracerProvider":
        print(f"❌ TracerProvider not initialized (using {provider_class})")
        print("   Call trace.set_tracer_provider(TracerProvider()) or use opentelemetry-instrument")
        issues.append("TracerProvider not initialized")
    else:
        print(f"✅ TracerProvider initialized: {provider_class}")

    return issues


def check_exporters():
    """Check if exporters are configured."""
    print("\n🔍 Checking exporters...\n")

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
    except ImportError:
        print("⚠️  Cannot check exporters (SDK not installed)")
        return []

    issues = []
    provider = trace.get_tracer_provider()

    if isinstance(provider, TracerProvider):
        # Access span processors
        processors = provider._active_span_processor._span_processors

        if not processors:
            print("❌ No span processors configured")
            print("   Add: provider.add_span_processor(BatchSpanProcessor(exporter))")
            issues.append("No exporters configured")
        else:
            print(f"✅ {len(processors)} span processor(s) configured:")
            for processor in processors:
                processor_class = processor.__class__.__name__
                print(f"   - {processor_class}")

                # Check if using BatchSpanProcessor (recommended)
                if "Simple" in processor_class:
                    print("     ⚠️  Using SimpleSpanProcessor - consider BatchSpanProcessor for production")
    else:
        print("⚠️  Cannot inspect providers (not using SDK TracerProvider)")

    return issues


def check_instrumentation_packages():
    """Check installed auto-instrumentation packages."""
    print("\n🔍 Checking installed instrumentation packages...\n")

    common_packages = [
        ("opentelemetry-instrumentation-flask", "Flask"),
        ("opentelemetry-instrumentation-fastapi", "FastAPI"),
        ("opentelemetry-instrumentation-django", "Django"),
        ("opentelemetry-instrumentation-requests", "HTTP client (requests)"),
        ("opentelemetry-instrumentation-httpx", "HTTP client (httpx)"),
        ("opentelemetry-instrumentation-sqlalchemy", "SQLAlchemy"),
        ("opentelemetry-instrumentation-psycopg2", "PostgreSQL (psycopg2)"),
        ("opentelemetry-instrumentation-redis", "Redis"),
        ("opentelemetry-instrumentation-celery", "Celery"),
        ("opentelemetry-instrumentation-aws-lambda", "AWS Lambda"),
    ]

    installed = []
    missing = []

    for package, description in common_packages:
        try:
            __import__(package.replace("-", "_"))
            installed.append(f"{package} ({description})")
            print(f"✅ {package} - {description}")
        except ImportError:
            missing.append(f"{package} ({description})")

    if not installed:
        print("⚠️  No auto-instrumentation packages found")
        print("   Install: opentelemetry-bootstrap -a install")
    elif missing:
        print(f"\n⚠️  {len(missing)} common instrumentation(s) not installed (install if needed):")
        for pkg in missing:
            print(f"   - {pkg}")

    return []


def test_span_creation():
    """Test creating a span."""
    print("\n🔍 Testing span creation...\n")

    try:
        from opentelemetry import trace
    except ImportError:
        print("⚠️  Cannot test span creation (SDK not installed)")
        return []

    tracer = trace.get_tracer(__name__)

    try:
        with tracer.start_as_current_span("test_span") as span:
            span.set_attribute("test.attribute", "value")
            print("✅ Successfully created test span")
            print(f"   Trace ID: {format(span.get_span_context().trace_id, '032x')}")
            print(f"   Span ID: {format(span.get_span_context().span_id, '016x')}")
    except Exception as e:
        print(f"❌ Failed to create span: {e}")
        return ["Span creation failed"]

    return []


def main():
    print("=" * 60)
    print("OpenTelemetry Instrumentation Check")
    print("=" * 60)

    all_issues = []

    all_issues.extend(check_environment_variables())
    all_issues.extend(check_sdk_initialization())
    all_issues.extend(check_exporters())
    all_issues.extend(check_instrumentation_packages())
    all_issues.extend(test_span_creation())

    print("\n" + "=" * 60)
    if not all_issues:
        print("✅ All checks passed! OpenTelemetry is properly configured.")
        sys.exit(0)
    else:
        print(f"❌ Found {len(all_issues)} issue(s):\n")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {issue}")
        print("\nFix these issues and run again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
