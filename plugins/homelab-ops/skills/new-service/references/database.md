# Database Service Patterns

Patterns for adding PostgreSQL, Redis/Valkey, and other databases to homelab services.

## PostgreSQL

### Basic PostgreSQL Container

```yaml
  postgres:
    image: postgres:18
    restart: unless-stopped
    healthcheck:
      test: pg_isready -q -t 2 -d $$POSTGRES_DB -U $$POSTGRES_USER
      start_period: 20s
      timeout: 30s
      interval: 10s
      retries: 5
    env_file: .env
    volumes:
      - {{ data_base_path }}/myservice/db/data:/var/lib/postgresql/data
    network_mode: service:tailscale
```

### PostgreSQL with Extensions (pgvector, pgvecto-rs)

For ML/embedding workloads:

```yaml
  database:
    image: docker.io/tensorchord/pgvecto-rs:pg14-v0.2.0
    restart: unless-stopped
    env_file: .env
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_USER: ${DB_USERNAME}
      POSTGRES_DB: ${DB_DATABASE_NAME}
      POSTGRES_INITDB_ARGS: '--data-checksums'
    volumes:
      - {{ data_base_path }}/myservice/postgres:/var/lib/postgresql/data
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
```

### PostgreSQL Environment Variables (.env.j2)

```bash
# PostgreSQL container
POSTGRES_PASSWORD={{ lookup('onepassword', 'MyService', vault='Secrets', field='db_password') }}
POSTGRES_DB=myservice
POSTGRES_USER=myservice

# Application connection
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE_NAME=myservice
DB_USERNAME=myservice
DB_PASSWORD={{ lookup('onepassword', 'MyService', vault='Secrets', field='db_password') }}
```

## Redis/Valkey

### Basic Redis (Valkey) Container

```yaml
  redis:
    image: docker.io/valkey/valkey:9.0-alpine
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "valkey-cli ping | grep -q PONG"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    volumes:
      - {{ data_base_path }}/myservice/redis:/data
    network_mode: service:tailscale
```

### Redis with Password

```yaml
  redis:
    image: docker.io/valkey/valkey:9.0-alpine
    command:
      - sh
      - -c
      - valkey-server --appendonly yes --requirepass $$REDIS_PASSWORD
    healthcheck:
      test: '[ $$(valkey-cli --pass "$${REDIS_PASSWORD}" ping) = ''PONG'' ]'
      start_period: 5s
      timeout: 3s
      interval: 1s
      retries: 5
    env_file: .env
    volumes:
      - {{ data_base_path }}/myservice/redis:/data
    network_mode: service:tailscale
```

### Multiple Redis Instances (Cache + Queue)

```yaml
  redis:
    image: docker.io/valkey/valkey:9.0-alpine
    command:
      - sh
      - -c
      - valkey-server --appendonly yes --requirepass $$REDIS_PASSWORD --port 6380
    env_file: .env
    volumes:
      - {{ data_base_path }}/myservice/redis:/data
    network_mode: service:tailscale

  redis-cache:
    image: docker.io/valkey/valkey:9.0-alpine
    command:
      - sh
      - -c
      - valkey-server --requirepass $$REDIS_CACHE_PASSWORD --port 6381
    env_file: .env
    volumes:
      - {{ data_base_path }}/myservice/redis-cache:/data
    network_mode: service:tailscale
```

### Redis Environment Variables (.env.j2)

```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD={{ lookup('onepassword', 'MyService', vault='Secrets', field='redis_password') }}

# Redis cache (if separate)
REDIS_CACHE_HOST=localhost
REDIS_CACHE_PORT=6381
REDIS_CACHE_PASSWORD={{ lookup('onepassword', 'MyService', vault='Secrets', field='redis_cache_password') }}
```

## Service Dependencies

Always wait for databases to be healthy:

```yaml
services:
  myservice:
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
```

## Volume Paths Convention

Organize database volumes under the service:

```
{{ data_base_path }}/myservice/
├── db/
│   └── data/          # PostgreSQL data
├── redis/             # Redis data
├── redis-cache/       # Cache data (if separate)
└── ...                # Other service data
```

## Database Health Check Reference

| Database | Health Check Command |
|----------|---------------------|
| PostgreSQL | `pg_isready -q -t 2 -d $DB -U $USER` |
| MySQL/MariaDB | `mysqladmin ping -h localhost` |
| Redis/Valkey | `valkey-cli ping \| grep -q PONG` |
| Redis (with auth) | `valkey-cli --pass "$PASSWORD" ping` |
| MongoDB | `mongosh --eval "db.adminCommand('ping')"` |
