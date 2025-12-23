# Ansible Inventory Guide

Guide for managing service assignments in the homelab Ansible inventory.

## Inventory Structure

Location: `ansible/inventory.yaml`

```yaml
all:
  vars:
    ansible_user: server
    ansible_python_interpreter: /usr/bin/python3

  children:
    docker_hosts:
      children:
        raspberry_pi:
          vars:
            arch: arm64
          hosts:
            backstreets:
              ansible_host: 10.13.20.116
              services:
                - alloy-agent
                - n8n
                - paperless-ngx

        jetson:
          vars:
            arch: arm64
          hosts:
            harlem:
              ansible_host: 10.13.20.188
              services:
                - alloy-agent
                - traefik

        nas:
          vars:
            arch: x86_64
          hosts:
            tower:
              ansible_host: 10.13.20.10
              ansible_user: root
              docker_compose_base_path: "/mnt/user/compose"
              data_base_path: "/mnt/user/docker-volumes"
              services:
                - jellyfin
                - grafana-stack
```

## Key Components

### Host Groups

| Group | Description | Hosts |
|-------|-------------|-------|
| `raspberry_pi` | Raspberry Pi nodes | backstreets, badlands, freehold |
| `jetson` | NVIDIA Jetson devices | harlem |
| `nas` | NAS storage servers | tower |
| `cloud` | Cloud VPS (unused) | - |

### Host Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `ansible_host` | IP address | Required |
| `ansible_user` | SSH user | `server` |
| `arch` | CPU architecture | From group |
| `services` | List of services to deploy | Required |
| `data_base_path` | Data volume path | `/srv/data` |
| `docker_compose_base_path` | Compose file path | `/srv/compose` |

### Services List

Each host has a `services:` list defining which services to deploy:

```yaml
hosts:
  myhost:
    services:
      - service-a
      - service-b
      - service-c
```

Services must:
- Have a directory in `services/{name}/`
- Contain `docker-compose.yaml.j2`
- Be listed in exactly ONE host's services list

## Managing Services

### Add Service to Host

```yaml
# Before
backstreets:
  services:
    - alloy-agent
    - n8n

# After
backstreets:
  services:
    - alloy-agent
    - n8n
    - new-service  # Added
```

### Remove Service from Host

```yaml
# Before
backstreets:
  services:
    - alloy-agent
    - n8n
    - old-service

# After
backstreets:
  services:
    - alloy-agent
    - n8n
    # old-service removed
```

### Move Service Between Hosts

```yaml
# Before
backstreets:
  services:
    - myservice

tower:
  services:
    - jellyfin

# After
backstreets:
  services:
    # myservice removed

tower:
  services:
    - jellyfin
    - myservice  # Added here
```

### Disable Service Temporarily

Comment out the service:

```yaml
services:
  - alloy-agent
  - n8n
  # - paperless-ngx  # Temporarily disabled
```

## Host-Specific Overrides

### Path Overrides

Tower uses different paths:

```yaml
tower:
  docker_compose_base_path: "/mnt/user/compose"
  data_base_path: "/mnt/user/docker-volumes"
```

Standard hosts use defaults from `group_vars/all/paths.yaml`:
- `docker_compose_base_path: /srv/compose`
- `data_base_path: /srv/data`

### User Override

Tower runs as root:

```yaml
tower:
  ansible_user: root
```

### Python Interpreter

Jetson has custom Python path:

```yaml
harlem:
  ansible_python_interpreter: /home/server/.ansible-venv/bin/python
```

## Deployment Commands

### Deploy All Services to a Host

```bash
ansible-playbook ansible/playbooks/deploy.yaml -l hostname
```

### Deploy Specific Service

```bash
ansible-playbook ansible/playbooks/deploy.yaml -l hostname -e "services=['myservice']"
```

### Deploy to All Hosts

```bash
ansible-playbook ansible/playbooks/deploy.yaml
```

### Dry Run

```bash
ansible-playbook ansible/playbooks/deploy.yaml -l hostname --check
```

## Validation

### Check Inventory Syntax

```bash
ansible-inventory --list -i ansible/inventory.yaml
```

### List Services per Host

```bash
ansible-inventory --list -i ansible/inventory.yaml | jq '.["_meta"]["hostvars"]' | grep -A20 services
```

### Verify Host Connectivity

```bash
ansible docker_hosts -m ping
```
