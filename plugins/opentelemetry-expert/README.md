# OpenTelemetry Expert Plugin

Comprehensive expert guidance for OpenTelemetry instrumentation, distributed tracing, and observability architecture.

## What This Plugin Does

This plugin provides expert-level support for:
- **Instrumenting applications** with OpenTelemetry (auto and manual instrumentation)
- **Troubleshooting telemetry issues** (missing traces, span problems, context propagation)
- **Designing observability architecture** (collector deployment, sampling strategies, multi-backend export)
- **Migrating from proprietary APM agents** (Datadog, New Relic, Dynatrace, AppDynamics)
- **Optimizing performance** with best practices and production-ready configurations
- **Integrating Pydantic Logfire** for simplified Python observability

## When to Use This Plugin

Invoke this plugin when working with:
- **Observability projects** - Adding traces, metrics, and logs to applications
- **OpenTelemetry setup** - Configuring SDK, collectors, and exporters
- **Production deployments** - Applying sampling strategies, resource configuration, and semantic conventions
- **APM migrations** - Moving from vendor-specific instrumentation to OpenTelemetry
- **Distributed systems** - Debugging context propagation across services
- **Python applications** - Leveraging Pydantic Logfire integration
- **Collector configuration** - Designing agent/gateway architectures

## Key Trigger Phrases

The plugin activates when you mention:
- "OpenTelemetry" or "OTel"
- "Distributed tracing" or "tracing"
- "Observability" or "observability architecture"
- "Instrumentation" or "auto-instrumentation"
- "Telemetry" or "OTLP"
- "Jaeger" or "Logfire"
- "Monitoring" or "APM"
- "Adding traces" or "adding metrics"

## Contents

### Skills
- **SKILL.md** - Comprehensive expert guidance with workflows, patterns, and best practices

### Reference Materials
- **basics.md** - Core concepts (traces, metrics, logs, resources, propagation, sampling)
- **components.md** - Component selection and architecture decisions
- **python-instrumentation.md** - Python SDK patterns and framework-specific guidance
- **best-practices.md** - 2025 production best practices and checklists
- **troubleshooting.md** - Diagnosing and fixing common issues
- **migration-guide.md** - Step-by-step guides for migrating from other APM agents
- **logfire.md** - Pydantic Logfire integration and simplified Python observability

### Assets
- **collector-basic.yaml** - Basic collector configuration for development
- **collector-production.yaml** - Production-ready collector with tail sampling
- **python-basic/** - Minimal Flask example with console export
- **python-advanced/** - Production-ready Python instrumentation example

### Scripts
- **validate_otel_config.py** - Validate OpenTelemetry collector configurations
- **check_instrumentation.py** - Verify Python application instrumentation

## Installation

This plugin is installed as part of the Claude Code marketplace. Once available, it will be automatically invoked when relevant keywords appear in your requests.

## Quick Start Example

For a new Python application, this plugin guides you through:

1. **Planning** - Choosing between auto-instrumentation and manual spans
2. **Setup** - Installing OpenTelemetry SDK and dependencies
3. **Implementation** - Creating spans, metrics, and log correlation
4. **Validation** - Testing with console exporter before production
5. **Deployment** - Configuring collector and production environment variables

## Key Recommendations

**Setup:**
- Use `BatchSpanProcessor` in production (not `SimpleSpanProcessor`)
- Always configure `service.name`, `service.version`, and `deployment.environment`
- Export to OpenTelemetry Collector (OTLP), not directly to vendors

**Sampling:**
- Baseline 1-10% sampling based on traffic volume
- Use tail sampling for 100% error/slow request capture
- Avoid `AlwaysOn` in high-traffic scenarios

**Instrumentation:**
- Follow OpenTelemetry semantic conventions
- Use auto-instrumentation for framework code
- Add manual spans for business logic
- Avoid high-cardinality dimensions in metrics

## Additional Resources

- [OpenTelemetry Official Documentation](https://opentelemetry.io/docs/)
- [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [Python SDK](https://opentelemetry-python.readthedocs.io/)
- [Collector Documentation](https://opentelemetry.io/docs/collector/)
- [Logfire Documentation](https://logfire.pydantic.dev/)
