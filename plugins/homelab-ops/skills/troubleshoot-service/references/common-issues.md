# Common Issues Checklist

Comprehensive troubleshooting checklist for homelab Docker services.

## Pre-Flight Checklist

Before diving deep, verify these basics:

- [ ] Service files exist in `services/{name}/`
- [ ] Service is in host's `services:` list in inventory.yaml
- [ ] Ansible playbook was run after changes
- [ ] Container is actually running (`docker compose ps`)

## Issue Categories

### Container Won't Start

**Check in order:**

1. **Compose file syntax**
   ```bash
   docker compose config
   ```
   Fix any YAML errors shown.

2. **Image availability**
   ```bash
   docker compose pull
   ```
   If pull fails, check image name/tag.

3. **Volume paths exist**
   ```bash
   ls -la {{ data_base_path }}/myservice/
   ```
   Create missing directories.

4. **Rendered template**
   ```bash
   cat ansible/.generated/hostname/services/myservice/docker-compose.yaml
   ```
   Look for unrendered Jinja2 (`{{ }}`).

5. **Environment file**
   ```bash
   cat ansible/.generated/hostname/services/myservice/.env
   ```
   Check for empty values or template syntax.

### Container Restarts Loop

**Check in order:**

1. **Recent logs**
   ```bash
   docker compose logs myservice --tail=100
   ```

2. **Exit code**
   ```bash
   docker inspect myservice --format='{{.State.ExitCode}}'
   ```
   - `0` = Clean exit (check restart policy)
   - `1` = Application error (check logs)
   - `137` = OOM killed (add memory limits)
   - `139` = Segfault (image/arch issue)

3. **Resource constraints**
   ```bash
   docker stats myservice --no-stream
   ```

### Service Unreachable

**Check in order:**

1. **Container running?**
   ```bash
   docker compose ps
   ```

2. **Tailscale connected?**
   ```bash
   docker compose exec tailscale tailscale status
   ```

3. **Service listening?**
   ```bash
   docker compose exec myservice netstat -tlnp
   ```

4. **Port correct?**
   Compare x-traefik port with service port.

5. **DNS resolving?**
   ```bash
   tailscale ping myservice.taileff4c.ts.net
   ```

### Data Not Persisting

**Check in order:**

1. **Volume mounted?**
   ```bash
   docker inspect myservice | jq '.[0].Mounts'
   ```

2. **Correct path?**
   Compare with data_base_path for the host:
   - Standard: `/srv/data`
   - Tower: `/mnt/user/docker-volumes`

3. **Permissions?**
   ```bash
   ls -la /path/to/volume/
   docker exec myservice id
   ```

4. **Named volume vs bind mount?**
   Named volumes survive `docker compose down`.
   Bind mounts require host path to exist.

### Secrets Not Loading

**Check in order:**

1. **1Password CLI authenticated?**
   ```bash
   op whoami
   ```

2. **Item exists?**
   ```bash
   op item get "ItemName" --vault Secrets
   ```

3. **Field exists?**
   ```bash
   op item get "ItemName" --vault Secrets --fields field_name
   ```

4. **Rendered .env?**
   ```bash
   cat ansible/.generated/hostname/services/myservice/.env
   ```
   Should NOT contain `{{ lookup(...) }}`.

5. **Re-run playbook**
   ```bash
   ansible-playbook ansible/playbooks/deploy.yaml -l hostname
   ```

## Host-Specific Issues

### Tower (NAS)

- Uses different paths (`/mnt/user/...`)
- User is `root`, not `server`
- May have Unraid-specific volume issues

### Raspberry Pi

- Limited resources (check memory)
- arm64 architecture (verify image supports it)
- SD card I/O can be slow

### Jetson

- GPU driver issues
- Custom Python interpreter path
- NVIDIA container runtime required for GPU

## Network Issues

### Can't Reach Other Services

All services use localhost when on same Tailscale network:
```bash
# From within container
curl http://localhost:5432  # Not postgres:5432
```

### Port Conflicts

Check if port is already in use:
```bash
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

### DNS Issues

Tailscale Magic DNS should resolve hostnames:
```bash
nslookup myservice.taileff4c.ts.net
```

## Performance Issues

### High CPU

```bash
docker stats --no-stream
```

Consider adding resource limits:
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
```

### High Memory

```bash
docker stats --no-stream
```

Add memory limits:
```yaml
deploy:
  resources:
    limits:
      memory: 1G
```

### Slow Disk I/O

On Raspberry Pi with SD card:
- Move data to external SSD
- Use tmpfs for temp files

## Quick Fixes

| Symptom | Quick Fix |
|---------|-----------|
| Container won't start | `docker compose down && docker compose up -d` |
| Stale config | Re-run Ansible playbook |
| Tailscale disconnected | Restart Tailscale container |
| Unhealthy status | Increase start_period |
| Permission denied | Fix ownership: `chown -R UID:GID /path` |
| Out of disk | `docker system prune -a` |

## When All Else Fails

1. **Check upstream docs** - Image might have requirements
2. **Compare with working service** - Find differences
3. **Fresh start** - Remove and recreate:
   ```bash
   docker compose down -v
   rm -rf /srv/data/myservice/*
   docker compose up -d
   ```
4. **Check GitHub issues** - Others may have same problem
