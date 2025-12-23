---
name: Homelab Migrate Service
description: This skill should be used when moving services between homelab hosts, changing service assignments in inventory, handling path differences between hosts (NAS vs Pi vs Jetson), or migrating data volumes. Trigger phrases include "move service to", "migrate from tower to", "relocate service", "change host for", or when discussing service placement optimization.
version: 1.0.0
---

# Homelab Migrate Service

Guide for moving Docker services between hosts in the homelab infrastructure.

## Pre-Migration Checklist

Before migrating, verify:

- [ ] **Architecture compatibility** - arm64 vs x86_64
- [ ] **GPU requirements** - Only tower and harlem have GPUs
- [ ] **Storage requirements** - Large data? Use tower
- [ ] **Resource requirements** - Heavy compute? Avoid Pi
- [ ] **Data volume size** - Estimate transfer time
- [ ] **Downtime window** - Plan for service interruption

## Host Capabilities

| Host | Arch | GPU | Storage | Best For |
|------|------|-----|---------|----------|
| tower | x86_64 | NVIDIA | NAS arrays | Media, ML, heavy compute, large data |
| backstreets | arm64 | None | SSD | Lightweight services |
| badlands | arm64 | None | SSD | Lightweight services |
| freehold | arm64 | None | Local | IoT, Home Assistant |
| harlem | arm64 | Jetson | SSD | Edge ML workloads |

## Path Differences

**Critical:** Hosts use different base paths!

| Host | data_base_path | docker_compose_base_path |
|------|----------------|--------------------------|
| Standard (Pi, Jetson) | `/srv/data` | `/srv/compose` |
| tower (NAS) | `/mnt/user/docker-volumes` | `/mnt/user/compose` |

The Ansible templates handle this automatically via variables, but data migration must account for these differences.

## Migration Workflow

### Step 1: Stop Service on Source

```bash
# SSH to source host
ssh server@source-host

# Stop the service
cd /srv/compose/myservice  # or /mnt/user/compose/myservice on tower
docker compose down
```

### Step 2: Update Inventory

Edit `ansible/inventory.yaml`:

```yaml
# Remove from source host
source-host:
  services:
    - other-service
    # - myservice  # Remove this line

# Add to target host
target-host:
  services:
    - existing-service
    - myservice  # Add this line
```

### Step 3: Migrate Data

**Option A: rsync (recommended for large data)**
```bash
# From source to target
rsync -avz --progress \
  /srv/data/myservice/ \
  server@target-host:/srv/data/myservice/
```

**Option B: tar + ssh (for smaller data)**
```bash
# Create archive and transfer
tar -czf - /srv/data/myservice | \
  ssh server@target-host "tar -xzf - -C /"
```

**Tower-specific paths:**
```bash
# From tower
rsync -avz --progress \
  /mnt/user/docker-volumes/myservice/ \
  server@target-host:/srv/data/myservice/

# To tower
rsync -avz --progress \
  /srv/data/myservice/ \
  root@tower:/mnt/user/docker-volumes/myservice/
```

### Step 4: Deploy to Target

```bash
# Run Ansible to render and deploy
ansible-playbook ansible/playbooks/deploy.yaml -l target-host
```

### Step 5: Verify

```bash
# SSH to target host
ssh server@target-host

# Check service status
cd /srv/compose/myservice
docker compose ps
docker compose logs --tail=50

# Verify Tailscale connectivity
tailscale ping myservice.taileff4c.ts.net
```

### Step 6: Clean Up Source

After confirming migration success:

```bash
# SSH to source host
ssh server@source-host

# Remove containers and volumes
cd /srv/compose/myservice
docker compose down -v

# Optionally remove data (after backup verification!)
rm -rf /srv/data/myservice
```

## Special Considerations

### Database Migrations

For services with databases:

1. **Stop writes first** - Put service in maintenance mode
2. **Dump database** - More reliable than file copy
   ```bash
   docker compose exec postgres pg_dump -U user dbname > backup.sql
   ```
3. **Transfer dump** - Smaller than data directory
4. **Restore on target** - After service starts
   ```bash
   docker compose exec -T postgres psql -U user dbname < backup.sql
   ```

### GPU Service Migration

Only migrate to/from GPU-capable hosts:
- tower (NVIDIA)
- harlem (Jetson)

Verify GPU access after migration:
```bash
docker compose exec myservice nvidia-smi
```

### Large Media Libraries

For services like Jellyfin, Immich:

1. **Use rsync with --partial** - Resume interrupted transfers
2. **Consider NFS mount** - Keep data on tower, access from anywhere
3. **Migrate during low-usage** - Large transfers impact network

### Tailscale Hostname

The Tailscale hostname stays the same after migration because:
- It's derived from `service_name` in the template
- Tailscale handles the routing automatically

No DNS or client changes needed.

## Rollback Procedure

If migration fails:

1. **Stop service on target**
   ```bash
   docker compose down
   ```

2. **Re-add to source inventory**
   ```yaml
   source-host:
     services:
       - myservice  # Add back
   ```

3. **Re-deploy to source**
   ```bash
   ansible-playbook ansible/playbooks/deploy.yaml -l source-host
   ```

4. **Verify source works**
   ```bash
   docker compose ps
   ```

## Reference Materials

For detailed information:
- `references/inventory.md` - Inventory management
- `references/host-differences.md` - Per-host configurations
