# Health Check Troubleshooting

Guide for diagnosing and fixing Docker health check issues.

## Diagnostic Commands

```bash
# Check current health status
docker inspect --format='{{json .State.Health}}' container_name | jq

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' container_name

# Run health check manually
docker exec container_name curl -f http://localhost:8080/health
```

## Understanding Health Check States

| State | Meaning |
|-------|---------|
| `starting` | Within start_period, checks not counted |
| `healthy` | Recent checks passed |
| `unhealthy` | Failed `retries` consecutive times |

## Common Issues

### Wrong Port

**Symptoms:**
- Health check always fails
- Service works when accessed manually

**Fix:**
Verify port matches the service:
```yaml
services:
  myservice:
    # Service listens on 3000
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]  # Not 8080!
```

### Missing Health Endpoint

**Symptoms:**
- Health check returns 404
- Service works but shows unhealthy

**Fix options:**

1. Use root path if service has no health endpoint:
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8080/"]
   ```

2. Use TCP check instead of HTTP:
   ```yaml
   healthcheck:
     test: ["CMD", "nc", "-z", "localhost", "8080"]
   ```

3. Check process is running:
   ```yaml
   healthcheck:
     test: ["CMD", "pgrep", "-x", "myprocess"]
   ```

### Start Period Too Short

**Symptoms:**
- Container marked unhealthy during startup
- Works after manual restart
- Slow-starting services always fail

**Fix:**
Increase `start_period` for slow services:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 120s  # 2 minutes for slow services
```

Recommended start periods:
| Service Type | start_period |
|--------------|--------------|
| Simple web app | 30s |
| Database | 60s |
| App with migrations | 120s |
| NetBox/complex apps | 300s |

### Container Lacks curl

**Symptoms:**
- Health check fails with "curl: not found"
- Alpine or minimal images

**Fix options:**

1. Use wget (common in Alpine):
   ```yaml
   healthcheck:
     test: ["CMD", "wget", "-q", "--spider", "http://localhost:8080/health"]
   ```

2. Use shell built-ins:
   ```yaml
   healthcheck:
     test: ["CMD-SHELL", "true"]  # Just check container runs
   ```

3. Use nc (netcat):
   ```yaml
   healthcheck:
     test: ["CMD", "nc", "-z", "localhost", "8080"]
   ```

### Database Health Checks

**PostgreSQL:**
```yaml
healthcheck:
  test: pg_isready -q -t 2 -d $$POSTGRES_DB -U $$POSTGRES_USER
  start_period: 20s
  timeout: 30s
  interval: 10s
  retries: 5
```

**Redis/Valkey (no auth):**
```yaml
healthcheck:
  test: ["CMD-SHELL", "valkey-cli ping | grep -q PONG"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```

**Redis/Valkey (with auth):**
```yaml
healthcheck:
  test: '[ $$(valkey-cli --pass "$${REDIS_PASSWORD}" ping) = ''PONG'' ]'
  start_period: 5s
  timeout: 3s
  interval: 1s
  retries: 5
```

### Worker/Background Process Health Checks

For processes without HTTP endpoints:

```yaml
healthcheck:
  test: ps -aux | grep -v grep | grep -q myworker || exit 1
  start_period: 20s
  timeout: 3s
  interval: 15s
```

Or check for a PID file:
```yaml
healthcheck:
  test: ["CMD", "test", "-f", "/tmp/worker.pid"]
```

## Standard Health Check Template

Use this for most HTTP services:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:PORT/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

Adjust:
- `PORT` - Match service port
- `start_period` - Increase for slow services
- `/health` - Use actual health endpoint or `/`

## Dependencies and Health Checks

Make services wait for healthy dependencies:

```yaml
services:
  app:
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
```

This prevents the app from starting until databases are ready.

## Debugging Health Checks

### Step 1: Check container status
```bash
docker compose ps
```

### Step 2: View health check history
```bash
docker inspect container_name | jq '.[0].State.Health'
```

### Step 3: Run health check manually
```bash
# Get the health check command
docker inspect --format='{{.Config.Healthcheck.Test}}' container_name

# Run it manually
docker exec container_name curl -f http://localhost:8080/health
```

### Step 4: Check service logs
```bash
docker compose logs myservice --tail=100
```
