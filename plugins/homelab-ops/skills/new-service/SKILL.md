---
name: Homelab New Service
description: This skill should be used when creating new Docker services in the homelab, writing docker-compose.yaml.j2 templates, setting up Tailscale networking, configuring Traefik routing, or integrating 1Password secrets. Trigger phrases include "add a new service", "create docker compose", "set up [service-name]", "homelab service", "add to homelab", or when discussing Jinja2 templates for Docker services.
version: 1.0.0
---

# Homelab New Service

Guide for creating Docker services in the Jinja2-templated homelab infrastructure with Tailscale networking, Traefik routing, and 1Password secrets.

## Service Directory Structure

Every service lives in `services/{service-name}/`:

```
services/{service-name}/
├── docker-compose.yaml.j2    # Required: Jinja2 template
├── .env.j2                   # Required: Environment with secrets
├── README.md                 # Optional: Service documentation
└── config/                   # Optional: Config files
```

## Template Skeleton

Start every `docker-compose.yaml.j2` with this structure:

```yaml
---
# Brief description of the service
{% set service_name = "myservice" %}

x-traefik:
  - service_name: "myservice"
    port: 8080
    tailscale_hostname: "myservice.taileff4c.ts.net"

services:
  myservice:
    image: registry/image:version
    restart: unless-stopped
    volumes:
      - {{ data_base_path }}/myservice:/data
    network_mode: service:tailscale
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

{% include 'shared/tailscale-sidecar.yaml.j2' %}
```

## Key Patterns

### 1. Service Name Variable

Always declare at the top of the template:

```yaml
{% set service_name = "myservice" %}
```

This variable is used by:
- Tailscale sidecar (`TS_HOSTNAME`)
- Traefik routing
- Volume paths

### 2. Traefik Routing Metadata

**Internal-only access:**
```yaml
x-traefik:
  - service_name: "myservice"
    port: 8080
    tailscale_hostname: "myservice.taileff4c.ts.net"
```

**Dual access (internal + public):**
```yaml
x-traefik-private:
  - service_name: "jellyfin"
    port: 8096
    tailscale_hostname: "jellyfin.taileff4c.ts.net"

x-traefik-public:
  - service_name: "jellyfin"
    port: 8096
    tailscale_hostname: "jellyfin.taileff4c.ts.net"
```

### 3. Network Mode

**Standard (most services):**
```yaml
network_mode: service:tailscale
```

All containers in the stack share the Tailscale network. Services communicate via `localhost`.

**Host mode (IoT/discovery services):**
```yaml
network_mode: host
```

Use only when service needs local network access (e.g., Home Assistant, MQTT).

### 4. Volume Paths

Always use Ansible variables for portability:

```yaml
volumes:
  # Persistent data
  - {{ data_base_path }}/myservice:/data

  # Config files (read-only)
  - {{ configs_base_path }}/myservice:/config:ro

  # Local config in service directory
  - ./config:/etc/myservice/config:ro

  # Timezone sync
  - /etc/localtime:/etc/localtime:ro
```

**Path variables:**
| Variable | Default | Tower Override |
|----------|---------|----------------|
| `{{ data_base_path }}` | `/srv/data` | `/mnt/user/docker-volumes` |
| `{{ docker_compose_base_path }}` | `/srv/compose` | `/mnt/user/compose` |
| `{{ configs_base_path }}` | `/srv/data/configs` | `/mnt/user/docker-volumes/configs` |

### 5. Health Checks

Standard health check pattern:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

**Common health check commands:**

| Service Type | Health Check |
|--------------|--------------|
| HTTP service | `curl -f http://localhost:PORT/` |
| PostgreSQL | `pg_isready -d $DB -U $USER` |
| Redis/Valkey | `valkey-cli ping \| grep -q PONG` |
| Custom | `test -f /tmp/healthy` |

### 6. Tailscale Sidecar

Always include at the end of the services section:

```yaml
{% include 'shared/tailscale-sidecar.yaml.j2' %}
```

This adds a standardized Tailscale container with:
- Auth key injection
- Hostname from `service_name` variable
- Health checks
- Automatic restart

### 7. Service Dependencies

When services depend on databases or caches:

```yaml
services:
  myservice:
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
```

## Environment File (.env.j2)

Create `.env.j2` for secrets and configuration:

```bash
# Tailscale hostname (matches service_name)
TS_HOSTNAME=myservice

# Application config
APP_PORT=8080
APP_DEBUG=false

# 1Password secrets
DB_PASSWORD={{ lookup('onepassword', 'MyService', vault='Secrets', field='db_password') }}
API_KEY={{ lookup('onepassword', 'MyService', vault='Secrets', field='api_key') }}

# Database connection (via tailscale, so localhost)
DB_HOST=localhost
DB_PORT=5432
```

**1Password lookup syntax:**
```
{{ lookup('onepassword', 'ItemName', vault='VaultName', field='field_name') }}
```

Common vault: `Secrets`

## Inventory Registration

After creating service files, add to `ansible/inventory.yaml`:

```yaml
hosts:
  hostname:
    services:
      - existing-service
      - myservice  # Add here
```

Choose host based on requirements:
- **tower**: GPU, large storage, x86_64
- **backstreets/badlands**: Lightweight, arm64
- **freehold**: IoT services
- **harlem**: Edge ML (Jetson)

## Deployment Workflow

1. Create `services/{name}/docker-compose.yaml.j2`
2. Create `services/{name}/.env.j2`
3. Add service to host's `services:` list in `inventory.yaml`
4. Run: `ansible-playbook ansible/playbooks/deploy.yaml -l hostname`

## Reference Materials

For detailed patterns and examples:
- `references/patterns.md` - Core compose patterns
- `references/database.md` - PostgreSQL/Redis patterns
- `references/examples.md` - Complete service examples
