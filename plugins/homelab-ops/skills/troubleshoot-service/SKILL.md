---
name: Homelab Troubleshoot Service
description: Use Skill(homelab-ops:troubleshoot-service) when diagnosing issues with homelab Docker services, debugging Tailscale connectivity, fixing health check failures, resolving 1Password lookup errors, troubleshooting Traefik routing, or investigating container startup failures. Trigger phrases include "service not working", "container failing", "can't connect to", "health check failing", "tailscale not connecting", "traefik not routing", or when a service shows as unhealthy.
version: 1.0.0
---

# Homelab Troubleshoot Service

Diagnostic guide for troubleshooting Docker services in the homelab infrastructure.

## Quick Diagnostic Commands

Run these first to understand the current state:

```bash
# Check container status
docker compose ps

# View recent logs
docker compose logs --tail=50

# Check specific service logs
docker compose logs myservice --tail=100

# Inspect health status
docker inspect --format='{{.State.Health.Status}}' container_name
```

## Diagnostic Decision Tree

```
Service not working?
├─ Container not starting → Check startup issues
├─ Container unhealthy → Check health check failures
├─ Can't reach service → Check Tailscale connectivity
├─ 502/503 errors → Check Traefik routing
├─ Permission denied → Check volume permissions
└─ Secrets not loading → Check 1Password lookups
```

## Common Issues

### 1. Container Startup Failures

**Symptoms:**
- Container exits immediately
- Status shows "Restarting"
- No logs or cryptic error

**Diagnostic:**
```bash
docker compose logs myservice
docker compose config  # Validate compose file
```

**Common causes:**
| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| "No such file" | Volume path doesn't exist | Create directory on host |
| "Permission denied" | Wrong user/group | Add PUID/PGID or fix ownership |
| "Address in use" | Port conflict | Check for duplicate services |
| "Invalid config" | Bad env variable | Check .env rendering |

### 2. Health Check Failures

**Symptoms:**
- Container shows "unhealthy"
- Dependent services won't start
- Intermittent availability

**Diagnostic:**
```bash
# Check health status
docker inspect container_name | jq '.[0].State.Health'

# Run health check manually
docker exec container_name curl -f http://localhost:8080/health
```

**Common causes:**

| Issue | Cause | Fix |
|-------|-------|-----|
| Wrong port | Health check port doesn't match service | Update health check port |
| Service not ready | Start period too short | Increase `start_period` |
| Missing curl | Container lacks curl | Use wget or nc instead |
| Wrong endpoint | Health endpoint changed | Update health check path |

See `references/health-checks.md` for detailed patterns.

### 3. Tailscale Connectivity

**Symptoms:**
- Service unreachable from other devices
- "connection refused" errors
- Tailscale container unhealthy

**Diagnostic:**
```bash
# Check Tailscale container
docker compose logs tailscale

# Verify Tailscale status
docker compose exec tailscale tailscale status

# Check if hostname exists on tailnet
tailscale status | grep service-name
```

**Common causes:**

| Issue | Cause | Fix |
|-------|-------|-----|
| "invalid auth key" | Auth key expired/revoked | Generate new key in Tailscale admin |
| "hostname collision" | Duplicate TS_HOSTNAME | Ensure unique `service_name` |
| Container restarts | Missing depends_on | Add Tailscale to service dependencies |
| Can't reach localhost | Wrong network_mode | Use `network_mode: service:tailscale` |

See `references/tailscale.md` for detailed troubleshooting.

### 4. Traefik Routing

**Symptoms:**
- 502 Bad Gateway
- 503 Service Unavailable
- Service works locally but not via Traefik

**Diagnostic:**
```bash
# Check Traefik logs
docker logs traefik

# Verify x-traefik metadata in compose
grep -A5 'x-traefik' docker-compose.yaml.j2
```

**Common causes:**

| Issue | Cause | Fix |
|-------|-------|-----|
| 502 | Wrong port in x-traefik | Match port to service |
| 503 | Service unhealthy | Fix health check |
| No routing | Missing x-traefik block | Add routing metadata |
| SSL errors | Certificate issue | Check Traefik cert config |

### 5. Volume/Permission Issues

**Symptoms:**
- "Permission denied" in logs
- Empty data after restart
- Config files not loading

**Diagnostic:**
```bash
# Check volume mounts
docker inspect container_name | jq '.[0].Mounts'

# Check host directory permissions
ls -la /srv/data/myservice/

# Check container user
docker exec container_name id
```

**Common causes:**

| Issue | Cause | Fix |
|-------|-------|-----|
| Permission denied | UID mismatch | Add PUID/PGID env vars |
| Empty volumes | Wrong path | Verify data_base_path for host |
| Read-only errors | Missing :rw | Check volume mount flags |
| SELinux blocks | Missing :z label | Add :z or :Z suffix |

### 6. 1Password Lookup Failures

**Symptoms:**
- Rendered .env has literal `{{ lookup(...) }}`
- Service can't authenticate
- "invalid credentials" errors

**Diagnostic:**
```bash
# Check rendered .env (on ansible controller)
cat ansible/.generated/hostname/services/myservice/.env

# Verify 1Password CLI
op signin
op item get "ItemName" --vault Secrets
```

**Common causes:**

| Issue | Cause | Fix |
|-------|-------|-----|
| Literal template | Ansible didn't render | Run playbook again |
| "item not found" | Wrong item name | Check exact name in 1Password |
| "field not found" | Wrong field name | Check field names in item |
| Auth error | 1Password CLI not signed in | Run `op signin` on controller |

## Reference Materials

For detailed troubleshooting patterns:
- `references/tailscale.md` - Tailscale connectivity issues
- `references/health-checks.md` - Health check debugging
- `references/common-issues.md` - Comprehensive troubleshooting checklist
