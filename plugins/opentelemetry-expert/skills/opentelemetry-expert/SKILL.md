---
name: opentelemetry-expert
description: Use Skill(opentelemetry-expert:opentelemetry-expert) when instrumenting applications with OpenTelemetry, troubleshooting telemetry issues, designing observability architecture, or migrating from proprietary APM agents (Datadog, New Relic) to OpenTelemetry. Covers traces, metrics, logs, sampling strategies, collectors, semantic conventions, and modern best practices (2025). Includes Python-specific guidance and Pydantic Logfire integration. Triggers include "OpenTelemetry", "OTel", "observability", "tracing", "distributed tracing", "instrumentation", "telemetry", "OTLP", "Jaeger", "Logfire", or when user asks about monitoring, APM migration, or adding traces/metrics to applications.
allowed-tools:
  - Read
  - Grep
  - Glob
  - WebSearch
  - WebFetch
---

# OpenTelemetry Expert

## Overview

This skill provides comprehensive guidance for implementing OpenTelemetry, the vendor-neutral observability framework. Use this skill to instrument applications with traces, metrics, and logs, troubleshoot missing or incorrect telemetry, design collector architectures, apply best practices, and migrate from proprietary APM agents to OpenTelemetry.

**When to use this skill:**
- Instrumenting new or existing Python applications (auto or manual instrumentation)
- Troubleshooting missing spans, broken context propagation, or performance issues
- Designing collector architectures (agent vs gateway mode, sampling strategies)
- Migrating from Datadog, New Relic, Dynatrace, or AppDynamics to OpenTelemetry
- Reviewing instrumentation for semantic convention compliance
- Integrating Pydantic Logfire for simplified Python observability

## Core Capabilities

### 1. Understanding OpenTelemetry Fundamentals

Before instrumenting code, establish a solid understanding of OpenTelemetry concepts:

**Read:** `references/basics.md` for core concepts including:
- Three pillars: Traces (distributed tracing), Metrics (time-series data), Logs (structured events)
- Resources, Semantic Conventions, Context Propagation, Sampling
- Auto-instrumentation vs Manual Instrumentation
- Exporters and data flow

**When to read:**
- Starting a new observability implementation
- Onboarding team members to OpenTelemetry
- Clarifying which signal (trace, metric, log) to use for a requirement

### 2. Component Selection and Architecture Design

Determine which OpenTelemetry components to use and how to deploy them:

**Read:** `references/components.md` for guidance on:
- When to use OpenTelemetry API, SDK, Collector
- Auto-instrumentation libraries vs manual spans
- Sampler types (AlwaysOn, TraceIdRatioBased, Tail Sampling)
- Span processors (BatchSpanProcessor vs SimpleSpanProcessor)
- Collector deployment modes (Agent, Gateway, Hybrid)
- Propagators (W3C Trace Context, B3, Jaeger)

**Decision tree for collector deployment:**
- **Local dev:** Skip collector, use console exporter
- **Small scale (< 1k req/min):** Gateway collector only
- **Medium scale (1k-10k req/min):** Agent collectors (DaemonSet/sidecar)
- **Large scale (> 10k req/min):** Hybrid (Agent + Gateway)

**Validate collector configs:** Use `scripts/validate_otel_config.py <config.yaml>` to check for common configuration errors.

**Templates:**
- `assets/collector-basic.yaml` - Local dev / simple deployments
- `assets/collector-production.yaml` - Production with tail sampling, filtering, multi-backend export

### 3. Python Instrumentation

Instrument Python applications with auto-instrumentation, manual spans, metrics, and logging integration:

**Read:** `references/python-instrumentation.md` for:
- Installation (auto-instrumentation vs manual SDK setup)
- Framework-specific auto-instrumentation (Flask, FastAPI, Django, requests, SQLAlchemy, Redis, Celery)
- Manual span creation with attributes, events, status
- Context propagation in HTTP requests and message queues
- Metrics API (counters, histograms, gauges)
- Log correlation with traces (inject `trace_id` and `span_id`)
- Environment variable configuration

**Quick start templates:**
- `assets/python-basic/` - Minimal Flask app with console export (local testing)
- `assets/python-advanced/` - Production-ready example with OTLP export, metrics, error tracking, context propagation

**Verify instrumentation:** Run `scripts/check_instrumentation.py` to validate SDK initialization, exporters, and environment variables.

**Common patterns:**
```python
# Auto-instrumentation (for frameworks)
from opentelemetry.instrumentation.flask import FlaskInstrumentor
FlaskInstrumentor().instrument_app(app)

# Manual span (for business logic)
with tracer.start_as_current_span("process_order", order_id=123) as span:
    span.set_attribute("order.amount", 99.99)
    process_order(order_id)

# Metrics
counter = meter.create_counter("orders.processed", unit="{order}")
counter.add(1, {"status": "success"})
```

### 4. Best Practices and Production Readiness

Apply modern OpenTelemetry best practices to ensure performance, security, and portability:

**Read:** `references/best-practices.md` for:
- Resource configuration (service name, version, environment)
- Sampling strategies by traffic volume
- Span granularity (what to instrument, what to skip)
- Semantic conventions (always use standard attribute names like `http.method`, `db.system`)
- Attribute cardinality (avoid high-cardinality dimensions in metrics)
- Context propagation testing
- Performance tuning (BatchSpanProcessor, batching intervals)
- Security (scrubbing PII, TLS for exporters)
- Collector deployment patterns (agent + gateway)
- Log/trace correlation
- Testing and validation

**Key rules:**
- Always set `service.name`, `service.version`, `deployment.environment`
- Use `BatchSpanProcessor` in production (not `SimpleSpanProcessor`)
- Sample aggressively (1-10% baseline, 100% errors/slow requests)
- Follow semantic conventions (https://opentelemetry.io/docs/specs/semconv/)
- Avoid high-cardinality attributes in metric dimensions (e.g., `user.id`)
- Export to OTel Collector (OTLP), not directly to vendors

**Checklist before production:**
- Resource attributes configured
- Sampling < 100% (use tail sampling for smart decisions)
- Using BatchSpanProcessor
- Exporter points to collector
- Context propagation tested across services
- Semantic conventions followed
- PII scrubbed or hashed
- Logs include `trace_id`
- Instrumentation overhead measured (< 5% latency increase)

### 5. Troubleshooting Telemetry Issues

Diagnose and fix common OpenTelemetry problems:

**Read:** `references/troubleshooting.md` for solutions to:
- No traces appearing in backend
- Traces missing spans from some services
- High latency / performance issues from instrumentation
- Collector not receiving data or dropping spans
- Context not propagating across services
- Incorrect trace structure (all root spans, no parent-child relationships)
- Semantic convention violations
- Logs not correlated with traces
- Cardinality explosion in metrics
- Missing exceptions in traces

**Debugging workflow:**
1. Test with console exporter (proves SDK is active)
2. Check environment variables (`OTEL_SERVICE_NAME`, `OTEL_EXPORTER_OTLP_ENDPOINT`)
3. Verify collector is reachable (`curl http://localhost:4317`)
4. Check sampling (not `AlwaysOff`)
5. Enable debug logging (`OTEL_LOG_LEVEL=debug`)

**Tools:**
- `scripts/check_instrumentation.py` - Verify Python app instrumentation
- Console exporter - Test locally before deploying
- Collector debug exporter - Print spans to console
- InMemorySpanExporter - Inspect spans in tests

### 6. Migrating from Proprietary APM Agents

Transition from vendor-specific instrumentation to OpenTelemetry:

**Read:** `references/migration-guide.md` for:
- Migration strategies (parallel running, service-by-service, big bang)
- Datadog to OpenTelemetry mapping (auto-instrumentation, manual spans, tags, metrics)
- New Relic to OpenTelemetry migration
- Dynatrace, AppDynamics to OpenTelemetry
- Common challenges (missing features, dashboard breakage, context propagation, cost changes)
- Rollback plans

**Recommended approach:**
1. **Parallel running:** Install OTel alongside existing agent, validate parity, then remove vendor SDK
2. **Start small:** Migrate one low-risk service first (staging, internal tool)
3. **Export to both:** Use collector to send data to both Jaeger (open-source) and vendor backend during transition
4. **Validate dashboards:** Rebuild using OTel semantic conventions
5. **Remove vendor SDK:** After 2-4 week validation period

**Example (Datadog → OTel):**
```python
# Before (Datadog)
from ddtrace import tracer
@tracer.wrap(service="api", resource="process_order")
def process_order(order_id):
    span = tracer.current_span()
    span.set_tag("order.id", order_id)

# After (OpenTelemetry)
from opentelemetry import trace
tracer = trace.get_tracer(__name__)
def process_order(order_id):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
```

### 7. Pydantic Logfire Integration

Use Logfire for simplified Python observability with automatic Pydantic integration:

**Read:** `references/logfire.md` for:
- Logfire vs raw OpenTelemetry (simplified setup, Pydantic integration)
- Basic and production configuration
- Automatic Pydantic model validation tracking
- Structured logging with trace correlation
- Auto-instrumentation (FastAPI, SQLAlchemy, requests, HTTPX, Redis, Celery)
- Metrics
- Exporting to other backends (Jaeger, custom OTel endpoints)
- Testing and development
- When to use Logfire vs raw OTel

**Quick comparison:**
```python
# Raw OpenTelemetry (verbose)
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

# Logfire (simplified)
import logfire
logfire.configure()
with logfire.span("process_order", order_id=123):
    validate_order(123)
```

**Use Logfire when:**
- Building Python applications (especially with Pydantic)
- Want simplified setup and beautiful UI
- Need automatic Pydantic model validation tracking
- Prefer structured logging out-of-the-box

**Use raw OTel when:**
- Non-Python applications
- Need maximum control over SDK configuration
- Custom sampling logic beyond Logfire's API

## Workflow Examples

### Instrumenting a New Python App

1. **Plan approach:**
   - Read `references/basics.md` to understand signals (traces, metrics, logs)
   - Read `references/components.md` to choose auto vs manual instrumentation

2. **Implement:**
   - For quick start: Use `assets/python-basic/app.py` as template
   - For production: Use `assets/python-advanced/app.py` as template
   - Read `references/python-instrumentation.md` for framework-specific guidance

3. **Validate:**
   - Run `scripts/check_instrumentation.py` to verify setup
   - Test with console exporter locally
   - Check `references/best-practices.md` for production checklist

4. **Deploy:**
   - Configure collector using `assets/collector-production.yaml`
   - Validate config with `scripts/validate_otel_config.py`
   - Monitor instrumentation overhead (< 5% latency increase)

### Troubleshooting Missing Traces

1. **Check basics:**
   - Run `scripts/check_instrumentation.py`
   - Enable console exporter to verify spans are created
   - Check environment variables (`OTEL_SERVICE_NAME`, `OTEL_EXPORTER_OTLP_ENDPOINT`)

2. **Follow troubleshooting guide:**
   - Read `references/troubleshooting.md` section "No Traces Appearing in Backend"
   - Test collector connectivity (`curl http://localhost:4317`)
   - Check sampler (not `AlwaysOff`)
   - Enable debug logging (`OTEL_LOG_LEVEL=debug`)

3. **Validate collector:**
   - Run `scripts/validate_otel_config.py collector-config.yaml`
   - Check collector logs (`docker logs otel-collector`)
   - Verify pipelines route to correct backends

### Migrating from Datadog

1. **Plan migration:**
   - Read `references/migration-guide.md` section "Datadog to OpenTelemetry"
   - Choose strategy (recommend parallel running for safety)

2. **Implement:**
   - Install OTel SDK alongside `ddtrace`
   - Map Datadog code to OTel equivalents (see migration guide)
   - Configure collector to export to both Jaeger and Datadog

3. **Validate:**
   - Compare traces in Datadog UI vs Jaeger
   - Check `references/troubleshooting.md` if context propagation breaks
   - Measure performance impact

4. **Cut over:**
   - Remove `ddtrace` after 2-4 week validation
   - Rebuild dashboards using OTel semantic conventions
   - Update documentation and runbooks

## Additional Resources

### External Documentation
- OpenTelemetry Official Docs: https://opentelemetry.io/docs/
- Semantic Conventions: https://opentelemetry.io/docs/specs/semconv/
- Python SDK: https://opentelemetry-python.readthedocs.io/
- Collector Documentation: https://opentelemetry.io/docs/collector/
- Logfire Documentation: https://logfire.pydantic.dev/

### Reference Files
All reference files are detailed and can be read as needed:
- `references/basics.md` - Core concepts and terminology
- `references/components.md` - Component selection guide
- `references/python-instrumentation.md` - Python SDK patterns
- `references/best-practices.md` - Production best practices (2025)
- `references/migration-guide.md` - Vendor migration guides
- `references/troubleshooting.md` - Common issues and solutions
- `references/logfire.md` - Pydantic Logfire integration

### Scripts
- `scripts/validate_otel_config.py` - Validate collector YAML configs
- `scripts/check_instrumentation.py` - Verify Python app instrumentation

### Templates
- `assets/collector-basic.yaml` - Basic collector config
- `assets/collector-production.yaml` - Production collector with tail sampling
- `assets/python-basic/` - Minimal Flask example
- `assets/python-advanced/` - Production-ready Flask example
