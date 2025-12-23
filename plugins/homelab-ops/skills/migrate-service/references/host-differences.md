# Host Differences Guide

Detailed comparison of homelab hosts and their configurations.

## Host Overview

| Host | Group | IP | Arch | User | Special |
|------|-------|-----|------|------|---------|
| backstreets | raspberry_pi | 10.13.20.116 | arm64 | server | Primary Pi |
| badlands | raspberry_pi | 10.13.20.115 | arm64 | server | Secondary Pi |
| freehold | raspberry_pi | 10.13.30.10 | arm64 | server | IoT VLAN |
| harlem | jetson | 10.13.20.188 | arm64 | server | Jetson GPU |
| tower | nas | 10.13.20.10 | x86_64 | root | Unraid NAS |

## Path Configuration

### Standard Hosts (Pi, Jetson)

```yaml
docker_compose_base_path: /srv/compose
data_base_path: /srv/data
configs_base_path: /srv/data/configs
```

Compose files deployed to:
```
/srv/compose/{service-name}/docker-compose.yaml
/srv/compose/{service-name}/.env
```

Data volumes at:
```
/srv/data/{service-name}/
```

### Tower (NAS)

```yaml
docker_compose_base_path: /mnt/user/compose
data_base_path: /mnt/user/docker-volumes
configs_base_path: /mnt/user/docker-volumes/configs
```

Compose files deployed to:
```
/mnt/user/compose/{service-name}/docker-compose.yaml
/mnt/user/compose/{service-name}/.env
```

Data volumes at:
```
/mnt/user/docker-volumes/{service-name}/
```

## Architecture Compatibility

### arm64 Only Images

Some images don't support arm64. Check before migrating to Pi/Jetson:
- Some proprietary software
- Older image versions
- Windows-based containers (obviously)

### x86_64 Only Images

Some services only run on x86_64 (tower):
- Some ML models
- Wine/Windows compatibility layers

### Multi-arch Images

Most modern images support both architectures:
- Official images (postgres, redis, nginx)
- LinuxServer.io images
- Major project images (Jellyfin, Immich)

Verify at Docker Hub or check `docker manifest inspect image:tag`.

## GPU Capabilities

### Tower (NVIDIA)

Full NVIDIA GPU support:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

Use for:
- ML inference (Ollama, Immich ML)
- Video transcoding (Jellyfin, Tdarr)
- CUDA workloads

### Harlem (Jetson)

NVIDIA Jetson GPU:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

Use for:
- Edge ML inference
- Lightweight GPU tasks
- Low-power GPU workloads

Note: Jetson uses different CUDA libraries than desktop NVIDIA.

### Pi Hosts

No GPU acceleration. Use CPU-only images:
- `immich-machine-learning` (CPU version)
- Software transcoding only

## Resource Limits

### Raspberry Pi Limits

Recommended limits for Pi:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 1536M
    reservations:
      memory: 256M
```

Avoid running on Pi:
- Services > 2GB RAM
- CPU-intensive ML
- Multiple databases

### Jetson Limits

More capable than Pi but limited:

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 4G
```

### Tower

No practical limits needed. NAS has abundant resources.

## Storage Considerations

### Tower Storage

- **Array storage**: Large, slow (HDDs)
- **Cache**: Fast (SSD/NVMe)
- **Best for**: Media libraries, backups, cold data

Use cache for databases:
```yaml
volumes:
  - /mnt/cache/myservice/db:/var/lib/postgresql/data
```

### Pi Storage

- **SD card**: Slow, wear-prone
- **External SSD**: Recommended for data
- **Best for**: Light workloads, config-only services

### Jetson Storage

- **NVMe**: Fast internal storage
- **Best for**: ML models, active data

## Network Configuration

### Standard Network

Most hosts on main VLAN (10.13.20.0/24):
- backstreets: 10.13.20.116
- badlands: 10.13.20.115
- harlem: 10.13.20.188
- tower: 10.13.20.10

### IoT VLAN

Freehold on IoT VLAN (10.13.30.0/24):
- freehold: 10.13.30.10

IoT services (Home Assistant, MQTT) should run here for direct device access.

## SSH Access

### Standard Hosts

```bash
ssh server@hostname
```

### Tower

```bash
ssh root@tower
```

Tower runs as root due to Unraid's architecture.

## Service Placement Guidelines

| Service Type | Best Host | Reason |
|--------------|-----------|--------|
| Media (Jellyfin, Tdarr) | tower | GPU + storage |
| ML inference | tower, harlem | GPU |
| Lightweight web apps | backstreets, badlands | Sufficient resources |
| IoT (Home Assistant) | freehold | IoT VLAN access |
| Monitoring (Grafana) | tower | Storage for metrics |
| Automation (n8n) | backstreets | Light resource use |
| Document management | tower, backstreets | Storage needs vary |

## Migration Checklist by Host Type

### To Tower

- [ ] Service supports x86_64
- [ ] Large storage needs justified
- [ ] GPU needed? Verify NVIDIA support
- [ ] Update paths in rsync commands

### To Pi

- [ ] Service supports arm64
- [ ] Memory < 1.5GB
- [ ] Not CPU intensive
- [ ] Consider external SSD for data

### To Jetson

- [ ] Service supports arm64
- [ ] Edge ML workload
- [ ] Jetson CUDA compatible (if GPU)

### To Freehold

- [ ] IoT-related service
- [ ] Needs direct device access
- [ ] Lightweight resource needs
