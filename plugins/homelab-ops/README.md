# homelab-ops

Create, troubleshoot, and migrate Docker services in a Jinja2-templated homelab infrastructure.

## Features

| Component | Type | Purpose |
|-----------|------|---------|
| `new-service` | Skill | Step-by-step guidance for creating services with proper patterns |
| `troubleshoot-service` | Skill | Diagnose issues with Tailscale, health checks, volumes |
| `migrate-service` | Skill | Move services between hosts with data migration |
| `service-reviewer` | Agent | Proactive review of service templates for best practices |
| `inventory-advisor` | Agent | Recommend optimal host placement based on requirements |

## Homelab Architecture

| Component | Purpose |
|-----------|---------|
| Jinja2 templates | `docker-compose.yaml.j2` for variable substitution |
| Tailscale sidecar | Zero-trust networking for all services |
| Traefik | Reverse proxy with automatic TLS |
| 1Password | Secrets management via Ansible lookup |
| Ansible inventory | Service-to-host assignment |

## Hosts

| Host | Type | Capabilities |
|------|------|--------------|
| tower | NAS (x86_64) | NVIDIA GPU, large storage arrays |
| backstreets/badlands | Pi (arm64) | Lightweight services |
| freehold | Pi (arm64) | IoT, Home Assistant |
| harlem | Jetson (arm64) | Edge ML workloads |

## Quick Start

### Creating a New Service

Invoke the skill with: "Create a new homelab service for [app-name]"

The skill guides you through:
1. Creating the service directory structure
2. Writing `docker-compose.yaml.j2` with proper patterns
3. Setting up `.env.j2` with 1Password lookups
4. Configuring Traefik routing metadata
5. Adding the service to Ansible inventory

### Troubleshooting

Invoke with: "Troubleshoot [service-name] - it's not starting"

The skill provides diagnostic checklists for:
- Tailscale connectivity issues
- Health check failures
- 1Password lookup errors
- Volume permission problems

### Migrating Services

Invoke with: "Move [service-name] from [source-host] to [target-host]"

The skill covers:
- Pre-migration checklist
- Inventory updates
- Data volume migration
- Post-migration validation

## Service Patterns

### Standard Service Template

```yaml
---
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

{% include 'shared/tailscale-sidecar.yaml.j2' %}
```

### Key Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `{{ data_base_path }}` | `/srv/data` | Persistent data volumes |
| `{{ docker_compose_base_path }}` | `/srv/compose` | Compose file location |
| `{{ configs_base_path }}` | `/srv/data/configs` | Shared config files |
| `{{ tailscale_authkey }}` | (from vars) | Tailscale auth key |
| `{{ service_name }}` | (set in template) | Service identifier |

### 1Password Secrets

```bash
{{ lookup('onepassword', 'ItemName', vault='Secrets', field='field_name') }}
```
