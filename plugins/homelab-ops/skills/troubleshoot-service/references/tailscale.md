# Tailscale Troubleshooting

Detailed guide for diagnosing and fixing Tailscale connectivity issues in the homelab.

## Diagnostic Commands

```bash
# Check Tailscale container status
docker compose logs tailscale

# Verify Tailscale is connected
docker compose exec tailscale tailscale status

# Check if service appears on tailnet
tailscale status | grep service-name

# Test connectivity from another device
tailscale ping service-name.taileff4c.ts.net
```

## Common Issues

### Auth Key Problems

**Symptoms:**
- Container logs show "auth key invalid" or "unauthorized"
- Tailscale container keeps restarting
- Service never appears on tailnet

**Causes:**
1. Auth key expired (default 90 days)
2. Auth key revoked
3. Auth key has usage limit reached
4. Wrong auth key in Ansible vars

**Fix:**
1. Generate new auth key in Tailscale admin console
2. Update `ansible/group_vars/all/tailscale.yaml`:
   ```yaml
   tailscale_authkey: "tskey-auth-xxx..."
   ```
3. Re-run Ansible playbook to re-render templates
4. Restart the service: `docker compose down && docker compose up -d`

**Prevention:**
- Use reusable auth keys
- Set calendar reminder for key rotation

### Hostname Collision

**Symptoms:**
- Service appears briefly then disappears
- Another device shows the hostname
- Inconsistent connectivity

**Causes:**
1. Duplicate `service_name` in different services
2. Old service still registered with same hostname
3. TS_HOSTNAME not using service_name variable

**Fix:**
1. Check for duplicates:
   ```bash
   grep -r "service_name =" services/*/docker-compose.yaml.j2
   ```
2. Remove old device from Tailscale admin if needed
3. Ensure template uses variable:
   ```yaml
   {% set service_name = "unique-name" %}
   # And sidecar uses:
   - TS_HOSTNAME={{ service_name }}
   ```

### Network Mode Misconfiguration

**Symptoms:**
- Main service can't reach localhost ports
- Services work individually but not together
- "Connection refused" to localhost

**Causes:**
1. Missing `network_mode: service:tailscale`
2. Mixed network modes in same stack
3. Service started before Tailscale

**Fix:**
1. Verify ALL containers use same network mode:
   ```yaml
   services:
     app:
       network_mode: service:tailscale
     postgres:
       network_mode: service:tailscale
     redis:
       network_mode: service:tailscale
   ```

2. Add explicit dependency:
   ```yaml
   services:
     app:
       depends_on:
         tailscale:
           condition: service_healthy
   ```

### Sidecar Not Starting

**Symptoms:**
- No Tailscale container in `docker compose ps`
- Service starts but has no network access

**Causes:**
1. Missing `{% include 'shared/tailscale-sidecar.yaml.j2' %}`
2. Template rendering failed
3. Indentation error in include

**Fix:**
1. Verify include at end of compose file:
   ```yaml
   services:
     myservice:
       # ...

   {% include 'shared/tailscale-sidecar.yaml.j2' %}
   ```

2. Check rendered output:
   ```bash
   cat ansible/.generated/hostname/services/myservice/docker-compose.yaml
   ```

3. Look for `tailscale:` service in rendered file

### Tailscale Health Check Failing

**Symptoms:**
- Tailscale container shows "unhealthy"
- Other containers won't start (if using condition: service_healthy)

**Causes:**
1. Network connectivity issues
2. Tailscale not fully initialized
3. Start period too short

**Fix:**
The standard sidecar includes proper health check:
```yaml
healthcheck:
  test: ["CMD-SHELL", "tailscale status --peers=false || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

If still failing:
1. Check network connectivity from host
2. Verify auth key is valid
3. Check Tailscale container logs

## Advanced Diagnostics

### Check Tailscale Network Interface

```bash
docker compose exec tailscale ip addr show tailscale0
```

Should show assigned Tailscale IP (100.x.x.x).

### Verify DNS Resolution

```bash
docker compose exec tailscale nslookup other-service.taileff4c.ts.net
```

### Test Internal Connectivity

From within a service container:
```bash
docker compose exec myservice curl -f http://localhost:8080
```

### Check Firewall Rules

On host:
```bash
sudo iptables -L -n | grep -i tailscale
```

## Reference: Tailscale Sidecar Configuration

Standard sidecar from `services/shared/tailscale-sidecar.yaml.j2`:

```yaml
  tailscale:
    image: tailscale/tailscale:v1.86.5
    restart: unless-stopped
    environment:
      - TS_AUTHKEY={{ tailscale_authkey }}
      - TS_HOSTNAME={{ service_name }}
    healthcheck:
      test: ["CMD-SHELL", "tailscale status --peers=false || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
```

Requirements:
- `service_name` variable must be set in compose file
- `tailscale_authkey` comes from Ansible vars
