# Complete Service Examples

Real examples from the homelab at different complexity levels.

## Simple Service: n8n

Single container with basic volumes. Good starting template.

### docker-compose.yaml.j2

```yaml
---
# Define Traefik configuration templates for external Ansible processing
{% set service_name = "n8n" %}
x-traefik:
  - service_name: "n8n"
    port: 5678
    tailscale_hostname: "n8n.taileff4c.ts.net"

services:
  n8n:
    image: n8nio/n8n:2.0.2
    container_name: n8n
    volumes:
      - {{ data_base_path }}/n8n:/home/node/.n8n
    network_mode: service:tailscale
    env_file:
      - .env

{% include 'shared/tailscale-sidecar.yaml.j2' %}
```

### .env.j2

```bash
TS_HOSTNAME=n8n
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD={{ lookup('onepassword', 'n8n', vault='Secrets', field='password') }}
```

---

## Medium Service: Immich

Photo management with database, Redis, and ML container.

### docker-compose.yaml.j2

```yaml
---
# Immich: Self-hosted photo and video management
{% set service_name = "immich" %}

x-traefik-private:
  - service_name: "immich"
    port: 2283
    tailscale_hostname: "immich.taileff4c.ts.net"

services:
  immich-server:
    image: ghcr.io/immich-app/immich-server:v1.124.2
    container_name: immich-server
    restart: unless-stopped
    env_file: .env
    volumes:
      - {{ data_base_path }}/immich/library:/usr/src/app/upload
      - /etc/localtime:/etc/localtime:ro
    network_mode: service:tailscale
    depends_on:
      redis:
        condition: service_healthy
      database:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:2283/api/server/ping || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  immich-machine-learning:
    image: ghcr.io/immich-app/immich-machine-learning:v1.124.2-cuda
    container_name: immich-ml
    restart: unless-stopped
    env_file: .env
    volumes:
      - {{ data_base_path }}/immich/ml-cache:/cache
    network_mode: service:tailscale
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    healthcheck:
      disable: true

  redis:
    image: docker.io/valkey/valkey:8-bookworm
    container_name: immich-redis
    restart: unless-stopped
    network_mode: service:tailscale
    healthcheck:
      test: ["CMD-SHELL", "valkey-cli ping | grep -q PONG"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  database:
    image: docker.io/tensorchord/pgvecto-rs:pg14-v0.2.0
    container_name: immich-postgres
    restart: unless-stopped
    env_file: .env
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_USER: ${DB_USERNAME}
      POSTGRES_DB: ${DB_DATABASE_NAME}
      POSTGRES_INITDB_ARGS: '--data-checksums'
    volumes:
      - {{ data_base_path }}/immich/postgres:/var/lib/postgresql/data
    network_mode: service:tailscale
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -d ${DB_DATABASE_NAME} -U ${DB_USERNAME}"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    command:
      [
        "postgres",
        "-c", "shared_preload_libraries=vectors.so",
        "-c", "search_path=\"$$user\", public, vectors",
        "-c", "max_wal_size=2GB",
        "-c", "shared_buffers=512MB",
      ]

{% include 'shared/tailscale-sidecar.yaml.j2' %}
```

### .env.j2

```bash
TS_HOSTNAME=immich

# Immich
UPLOAD_LOCATION=/usr/src/app/upload
IMMICH_VERSION=release

# Database
DB_PASSWORD={{ lookup('onepassword', 'Immich', vault='Secrets', field='db_password') }}
DB_USERNAME=postgres
DB_DATABASE_NAME=immich
DB_HOSTNAME=localhost
```

---

## Complex Service: NetBox

DCIM/IPAM with main app, workers, housekeeping, PostgreSQL, and Redis.

### docker-compose.yaml.j2

```yaml
---
# Define Traefik configuration templates for external Ansible processing
{% set service_name = "netbox" %}

x-traefik:
  - service_name: "netbox"
    port: 8080
    tailscale_hostname: "netbox.taileff4c.ts.net"

services:
  netbox: &netbox
    image: ghcr.io/jdh313/netbox-custom-image:v4.3.1-3.3.0
    depends_on:
      - postgres
      - redis
      - redis-cache
    user: "root:root"
    restart: unless-stopped
    healthcheck:
      test: curl -f http://localhost:8080/login/ || exit 1
      start_period: 300s
      timeout: 3s
      interval: 15s
    volumes:
      - ./config:/etc/netbox/config:z,ro
      - {{ data_base_path }}/netbox/media:/opt/netbox/netbox/media:rw
      - {{ data_base_path }}/netbox/reports:/opt/netbox/netbox/reports:rw
      - {{ data_base_path }}/netbox/scripts:/opt/netbox/netbox/scripts:rw
    network_mode: service:tailscale
    env_file: .env

  netbox-worker:
    <<: *netbox
    depends_on:
      netbox:
        condition: service_healthy
    command:
      - /opt/netbox/venv/bin/python
      - /opt/netbox/netbox/manage.py
      - rqworker
    healthcheck:
      test: ps -aux | grep -v grep | grep -q rqworker || exit 1
      start_period: 20s
      timeout: 3s
      interval: 15s

  netbox-housekeeping:
    <<: *netbox
    depends_on:
      netbox:
        condition: service_healthy
    command:
      - /opt/netbox/housekeeping.sh
    healthcheck:
      test: ps -aux | grep -v grep | grep -q housekeeping || exit 1
      start_period: 20s
      timeout: 3s
      interval: 15s

  postgres:
    image: postgres:18
    healthcheck:
      test: pg_isready -q -t 2 -d $$POSTGRES_DB -U $$POSTGRES_USER
      start_period: 20s
      timeout: 30s
      interval: 10s
      retries: 5
    env_file: .env
    volumes:
      - {{ data_base_path }}/netbox/db/data:/var/lib/postgresql/data
    restart: unless-stopped
    network_mode: service:tailscale

  redis:
    image: docker.io/valkey/valkey:9.0-alpine
    command:
      - sh
      - -c
      - valkey-server --appendonly yes --requirepass $$REDIS_PASSWORD --port 6380
    healthcheck:
      test: '[ $$(valkey-cli --pass "$${REDIS_PASSWORD}" ping) = ''PONG'' ]'
      start_period: 5s
      timeout: 3s
      interval: 1s
      retries: 5
    env_file: .env
    volumes:
      - {{ data_base_path }}/netbox/redis:/data
    network_mode: service:tailscale

  redis-cache:
    image: docker.io/valkey/valkey:9.0-alpine
    command:
      - sh
      - -c
      - valkey-server --requirepass $$REDIS_CACHE_PASSWORD --port 6381
    env_file: .env
    volumes:
      - {{ data_base_path }}/netbox/redis-cache:/data
    network_mode: service:tailscale

{% include 'shared/tailscale-sidecar.yaml.j2' %}
```

### .env.j2

```bash
TS_HOSTNAME=netbox

# NetBox
CORS_ORIGIN_ALLOW_ALL=True
SUPERUSER_EMAIL=jacob@jdh.onl
SUPERUSER_PASSWORD={{ lookup('onepassword', 'Netbox', vault='Secrets', field='su_pw') }}
ALLOWED_HOSTS=*
GRAPHQL_ENABLED=True
HOUSEKEEPING_INTERVAL=86400
MEDIA_ROOT=/opt/netbox/netbox/media
SECRET_KEY={{ lookup('onepassword', 'Netbox', vault='Secrets', field='secret_key') }}

# Database
DB_HOST=localhost
DB_NAME=netbox
DB_USER=netbox
DB_PASSWORD={{ lookup('onepassword', 'Netbox', vault='Secrets', field='db_pw') }}

# PostgreSQL container
POSTGRES_PASSWORD={{ lookup('onepassword', 'Netbox', vault='Secrets', field='db_pw') }}
POSTGRES_DB=netbox
POSTGRES_USER=netbox

# Redis (main - port 6380)
REDIS_HOST=localhost
REDIS_PORT=6380
REDIS_DATABASE=0
REDIS_PASSWORD={{ lookup('onepassword', 'Netbox', vault='Secrets', field='redis_pw') }}

# Redis cache (port 6381)
REDIS_CACHE_HOST=localhost
REDIS_CACHE_PORT=6381
REDIS_CACHE_DATABASE=1
REDIS_CACHE_PASSWORD={{ lookup('onepassword', 'Netbox', vault='Secrets', field='redis_cache_pw') }}
```

---

## Key Takeaways

| Complexity | Characteristics |
|------------|-----------------|
| **Simple** | Single container, basic env, no database |
| **Medium** | Main app + database + cache, GPU optional |
| **Complex** | Multiple workers, YAML anchors, multi-Redis, long start periods |

### Patterns Used

1. **YAML anchors** (`&netbox`, `<<: *netbox`) - Reduce duplication for worker containers
2. **Dependency chains** - Workers depend on main app being healthy
3. **Port offsets** - Multiple Redis on different ports (6380, 6381)
4. **SELinux labels** - `:z` suffix for shared volumes on Fedora/RHEL hosts
