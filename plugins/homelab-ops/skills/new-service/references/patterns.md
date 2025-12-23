# Core Compose Patterns

Patterns extracted from the homelab infrastructure for Docker Compose Jinja2 templates.

## Tailscale Sidecar

The shared sidecar template (`services/shared/tailscale-sidecar.yaml.j2`):

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

**Usage:** Always include via `{% include 'shared/tailscale-sidecar.yaml.j2' %}` at the end of your services section.

## Multi-Container Network Sharing

When multiple containers need to communicate:

```yaml
services:
  main-app:
    network_mode: service:tailscale
    environment:
      - DB_HOST=localhost      # Not postgres:5432
      - REDIS_HOST=localhost   # Not redis:6379

  postgres:
    network_mode: service:tailscale
    # Accessible at localhost:5432

  redis:
    network_mode: service:tailscale
    # Accessible at localhost:6379
```

All containers share Tailscale's network stack, so they communicate via `localhost`.

## YAML Anchors for Service Variants

Reuse configuration for workers/background tasks:

```yaml
services:
  main: &main
    image: myapp:latest
    env_file: .env
    volumes:
      - {{ data_base_path }}/myapp:/data
    network_mode: service:tailscale

  worker:
    <<: *main
    command: /app/worker.sh
    depends_on:
      main:
        condition: service_healthy
```

## GPU Passthrough

For services requiring GPU (tower/harlem only):

```yaml
services:
  ml-service:
    image: myml:cuda
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    network_mode: service:tailscale
```

## Resource Limits

For resource-constrained hosts (Raspberry Pi):

```yaml
services:
  myservice:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1536M
        reservations:
          memory: 512M
```

## CIFS/NFS Volume Mounts

For NAS storage access:

```yaml
volumes:
  media:
    driver_opts:
      type: "cifs"
      o: "username=${CIFS_USERNAME},password=${CIFS_PASSWORD},uid=99,gid=100,file_mode=0644,dir_mode=0755,noperm"
      device: "//10.13.20.10/documents/myapp"
```

Requires CIFS credentials in `.env.j2`:
```bash
CIFS_USERNAME={{ lookup('onepassword', 'NAS', vault='Secrets', field='username') }}
CIFS_PASSWORD={{ lookup('onepassword', 'NAS', vault='Secrets', field='password') }}
```

## User/Group Mapping

For services that need specific UID/GID (common with NAS):

```yaml
services:
  myservice:
    environment:
      - PUID=99
      - PGID=100
    user: "99:100"
```

## Timezone Sync

Mount localtime for consistent timestamps:

```yaml
volumes:
  - /etc/localtime:/etc/localtime:ro
```

## SELinux Volume Labels

For hosts with SELinux enabled:

```yaml
volumes:
  - {{ data_base_path }}/myservice:/data:z      # Shared label
  - ./config:/config:Z                          # Private label
```

## Conditional Port Exposure

Some services need host ports (for syslog, OTLP, etc.):

```yaml
services:
  collector:
    ports:
      - "514:514/udp"      # Syslog
      - "4317:4317"        # OTLP gRPC
    network_mode: service:tailscale
```

Note: This still uses Tailscale network but binds specific ports to the host.
