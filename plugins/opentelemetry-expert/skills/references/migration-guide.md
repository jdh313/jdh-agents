# Migrating to OpenTelemetry from Proprietary Agents

This guide covers migrating from vendor-specific instrumentation (Datadog, New Relic, Dynatrace, AppDynamics) to OpenTelemetry.

## Why Migrate to OpenTelemetry?

### Benefits
- **Vendor neutrality:** Switch backends without re-instrumenting code
- **Cost control:** Easier to compare pricing and switch vendors
- **Future-proof:** Industry standard backed by CNCF
- **Richer ecosystem:** More integrations and community support
- **Unified instrumentation:** One SDK for all signals (traces, metrics, logs)

### Trade-offs
- **Initial migration effort:** Requires code changes and testing
- **Feature parity:** Some vendor-specific features may not translate directly
- **Learning curve:** New concepts and tooling

## Migration Strategies

### Strategy 1: Parallel Running (Recommended)

Run OTel alongside existing agent for validation before cutover.

**Pros:**
- Low risk (existing monitoring continues)
- Gradual validation
- Easy rollback

**Cons:**
- Dual overhead during migration (~5-10% extra latency)
- More complex configuration

**Steps:**
1. Install OTel SDK alongside vendor SDK
2. Configure OTel to export to collector + vendor backend
3. Validate parity (compare dashboards, traces)
4. Remove vendor SDK after validation period (2-4 weeks)

### Strategy 2: Service-by-Service Migration

Migrate one service at a time, starting with non-critical services.

**Pros:**
- Isolated risk
- Learn and iterate

**Cons:**
- Longer migration timeline
- Context propagation challenges (mixing vendors)

**Steps:**
1. Pick a low-risk service (internal tool, staging env)
2. Migrate to OTel
3. Validate thoroughly
4. Iterate on next service

### Strategy 3: Big Bang (Not Recommended)

Migrate all services simultaneously.

**Pros:**
- Faster migration

**Cons:**
- High risk
- Difficult to debug issues
- Hard rollback

**When to Use:**
- Small deployments (< 5 services)
- Greenfield projects

## Datadog to OpenTelemetry

### Datadog APM vs OpenTelemetry

| Feature | Datadog APM | OpenTelemetry Equivalent |
|---------|-------------|--------------------------|
| Auto-instrumentation | `ddtrace-run` | `opentelemetry-instrument` |
| Manual spans | `tracer.trace()` | `tracer.start_as_current_span()` |
| Service name | `DD_SERVICE` | `OTEL_SERVICE_NAME` |
| Environment | `DD_ENV` | `deployment.environment` resource attribute |
| Version | `DD_VERSION` | `SERVICE_VERSION` resource attribute |
| Tags | `span.set_tag()` | `span.set_attribute()` |
| Metrics | `statsd` | OpenTelemetry Metrics API |
| Logs | Datadog agent | OTel logs SDK or log shipper |

### Migration Example (Python)

#### Before (Datadog)

```python
from ddtrace import tracer

@tracer.wrap(service="payment-api", resource="process_order")
def process_order(order_id):
    span = tracer.current_span()
    span.set_tag("order.id", order_id)
    span.set_tag("customer.tier", "premium")

    # Business logic
    validate_order(order_id)
    charge_payment(order_id)
```

```bash
# Run with Datadog
DD_SERVICE=payment-api DD_ENV=production ddtrace-run python app.py
```

#### After (OpenTelemetry)

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def process_order(order_id):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        span.set_attribute("customer.tier", "premium")

        # Business logic
        validate_order(order_id)
        charge_payment(order_id)
```

```bash
# Run with OpenTelemetry
export OTEL_SERVICE_NAME=payment-api
export OTEL_RESOURCE_ATTRIBUTES="deployment.environment=production"
opentelemetry-instrument python app.py
```

### Exporting to Datadog from OTel

#### Option 1: Datadog Exporter (Direct)

```python
from opentelemetry.exporter.datadog import DatadogExporter

exporter = DatadogExporter(
    agent_url="http://localhost:8126",
    service="payment-api"
)
```

**Pros:** Native Datadog integration
**Cons:** Still locked to Datadog

#### Option 2: OTel Collector → Datadog (Recommended)

```yaml
# collector-config.yaml
exporters:
  datadog:
    api:
      key: ${DD_API_KEY}
      site: datadoghq.com

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [datadog]
```

**Pros:** Decouples app from Datadog, easier to switch later
**Cons:** Adds collector deployment

### Datadog-Specific Features

#### Unified Service Tagging

**Datadog:** `DD_SERVICE`, `DD_ENV`, `DD_VERSION`

**OTel Equivalent:**
```bash
export OTEL_SERVICE_NAME=payment-api
export OTEL_RESOURCE_ATTRIBUTES="deployment.environment=production,service.version=1.2.3"
```

#### Datadog Profiling

**Not directly supported by OTel.** Continue using `ddtrace` profiler if needed:

```bash
# Run both OTel and Datadog profiler
DD_PROFILING_ENABLED=true opentelemetry-instrument ddtrace-run python app.py
```

#### Datadog Metrics (DogStatsD)

**OTel Equivalent:** Use OpenTelemetry Metrics API

**Before:**
```python
from datadog import statsd

statsd.increment('orders.processed', tags=["status:success"])
```

**After:**
```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)
counter = meter.create_counter("orders.processed")
counter.add(1, {"status": "success"})
```

## New Relic to OpenTelemetry

### New Relic Agent vs OpenTelemetry

| Feature | New Relic | OpenTelemetry Equivalent |
|---------|-----------|--------------------------|
| Auto-instrumentation | `newrelic-admin run-program` | `opentelemetry-instrument` |
| Manual spans | `newrelic.agent.function_trace()` | `tracer.start_as_current_span()` |
| App name | `NEW_RELIC_APP_NAME` | `OTEL_SERVICE_NAME` |
| Attributes | `newrelic.agent.add_custom_attribute()` | `span.set_attribute()` |
| Events | `newrelic.agent.record_custom_event()` | `span.add_event()` |

### Migration Example (Python)

#### Before (New Relic)

```python
import newrelic.agent

@newrelic.agent.function_trace(name="process_order")
def process_order(order_id):
    newrelic.agent.add_custom_attribute("order.id", order_id)

    validate_order(order_id)
    newrelic.agent.record_custom_event("OrderProcessed", {"order_id": order_id})
```

```bash
NEW_RELIC_APP_NAME=payment-api newrelic-admin run-program python app.py
```

#### After (OpenTelemetry)

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def process_order(order_id):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)

        validate_order(order_id)
        span.add_event("OrderProcessed", {"order_id": order_id})
```

```bash
export OTEL_SERVICE_NAME=payment-api
opentelemetry-instrument python app.py
```

### Exporting to New Relic from OTel

```yaml
# collector-config.yaml
exporters:
  otlp:
    endpoint: https://otlp.nr-data.net:4317
    headers:
      api-key: ${NEW_RELIC_LICENSE_KEY}

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp]
```

### New Relic-Specific Features

#### Browser Monitoring (RUM)
**Not directly in OTel Python SDK.** Use New Relic Browser agent separately or consider:
- OpenTelemetry JS for browser instrumentation
- Send OTel browser traces to New Relic

#### Synthetics
**Keep using New Relic Synthetics**—not replaced by OTel.

## Dynatrace to OpenTelemetry

### Dynatrace OneAgent vs OpenTelemetry

| Feature | Dynatrace | OpenTelemetry Equivalent |
|---------|-----------|--------------------------|
| Auto-instrumentation | OneAgent | `opentelemetry-instrument` |
| PurePath | Dynatrace-specific | Distributed traces |
| Custom attributes | `dt.custom_attribute` | `span.set_attribute()` |

### Exporting to Dynatrace

```yaml
# collector-config.yaml
exporters:
  otlp:
    endpoint: https://{your-environment-id}.live.dynatrace.com:443/api/v2/otlp
    headers:
      Authorization: Api-Token ${DYNATRACE_API_TOKEN}

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp]
```

## AppDynamics to OpenTelemetry

### AppDynamics Agent vs OpenTelemetry

| Feature | AppDynamics | OpenTelemetry Equivalent |
|---------|-------------|--------------------------|
| Auto-instrumentation | AppDynamics agent | `opentelemetry-instrument` |
| Business transactions | AppDynamics-specific | Manual spans |
| Custom metrics | AppDynamics SDK | OTel Metrics API |

### Exporting to AppDynamics

AppDynamics supports OTLP natively in recent versions:

```yaml
exporters:
  otlp:
    endpoint: https://<controller-host>:443/otlp
    headers:
      Authorization: Bearer ${APPDYNAMICS_API_KEY}
```

## Common Migration Challenges

### 1. Missing Vendor-Specific Features

**Problem:** Vendor SDKs have features not in OTel (e.g., Datadog profiling, New Relic Synthetics).

**Solution:**
- Run OTel for traces + vendor agent for specific features
- Find OTel alternatives (e.g., Pyroscope for profiling)
- Accept feature loss if not critical

### 2. Dashboard Breakage

**Problem:** Dashboards built on vendor-specific attributes break after migration.

**Solution:**
- Map vendor attributes to OTel semantic conventions
- Use collector attribute processor to rename attributes
- Rebuild dashboards using OTel conventions

```yaml
# collector-config.yaml
processors:
  attributes:
    actions:
      # Map Datadog tags to OTel attributes
      - key: env
        action: upsert
        from_attribute: deployment.environment
      - key: version
        action: upsert
        from_attribute: service.version
```

### 3. Context Propagation Between Old and New Services

**Problem:** Service A (Datadog) → Service B (OTel) loses trace context.

**Solution:**
- Configure both propagators during migration:

```python
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.propagators import CompositePropagator

# Support both W3C and B3 (Datadog-compatible)
set_global_textmap(CompositePropagator([
    TraceContextTextMapPropagator(),
    B3MultiFormat()
]))
```

### 4. Performance Regression

**Problem:** OTel adds more latency than vendor agent.

**Solution:**
- Tune sampling (reduce sample rate)
- Use `BatchSpanProcessor` (not `SimpleSpanProcessor`)
- Disable unnecessary auto-instrumentation
- Profile and optimize

### 5. Cost Changes

**Problem:** New billing model (some vendors charge for OTel data differently).

**Solution:**
- Estimate costs before migration (spans ingested vs. agent-based pricing)
- Use tail sampling to control volume
- Compare vendor pricing for OTLP ingestion

## Migration Checklist

### Pre-Migration
- [ ] Inventory existing instrumentation (which services, which SDK)
- [ ] Document custom spans, metrics, attributes
- [ ] Identify vendor-specific features in use
- [ ] Estimate OTel costs (spans/sec × pricing)
- [ ] Choose migration strategy (parallel running vs. service-by-service)

### During Migration
- [ ] Install OTel SDK
- [ ] Configure resource attributes (`service.name`, `deployment.environment`)
- [ ] Migrate auto-instrumentation (`ddtrace-run` → `opentelemetry-instrument`)
- [ ] Migrate custom spans (vendor SDK → OTel SDK)
- [ ] Configure exporter (OTLP → collector → vendor)
- [ ] Test context propagation
- [ ] Validate trace data (compare with existing vendor)
- [ ] Update dashboards (use OTel semantic conventions)
- [ ] Monitor performance (latency, error rate)

### Post-Migration
- [ ] Remove vendor SDK after validation period
- [ ] Update runbooks and documentation
- [ ] Train team on OTel concepts
- [ ] Set up alerting on collector metrics
- [ ] Explore multi-vendor backends (Jaeger, Prometheus, etc.)

## Rollback Plan

If migration fails, rollback steps:

1. **Stop OTel instrumentation:**
   ```bash
   # Remove opentelemetry-instrument wrapper
   python app.py  # Instead of: opentelemetry-instrument python app.py
   ```

2. **Re-enable vendor SDK:**
   ```bash
   # Datadog
   DD_SERVICE=payment-api ddtrace-run python app.py

   # New Relic
   newrelic-admin run-program python app.py
   ```

3. **Revert code changes** (if manual instrumentation was added)

4. **Restore dashboards** from backup

## Resources

- OpenTelemetry Semantic Conventions: https://opentelemetry.io/docs/specs/semconv/
- Datadog → OTel Migration Guide: https://docs.datadoghq.com/tracing/trace_collection/otel_instrumentation/
- New Relic OpenTelemetry Support: https://docs.newrelic.com/docs/more-integrations/open-source-telemetry-integrations/opentelemetry/
- Dynatrace OpenTelemetry Guide: https://www.dynatrace.com/support/help/extend-dynatrace/opentelemetry
