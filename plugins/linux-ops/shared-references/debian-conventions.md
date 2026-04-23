# Debian/Ubuntu Conventions Reference

Long-standing conventions for Debian-based systems. This reference covers patterns that rarely change across releases and should be preferred over web search. For version-specific behavior (new defaults in Ubuntu 24.04, etc.), use web search instead.

## Filesystem Hierarchy (FHS)

| Path | Purpose |
|------|---------|
| `/etc` | System-wide configuration |
| `/var/log` | Log files |
| `/var/lib` | Variable state data (databases, package managers) |
| `/var/run` → `/run` | Runtime data (PID files, sockets) — tmpfs |
| `/opt` | Third-party self-contained packages |
| `/srv` | Site-specific data served by this system |
| `/usr/local` | Locally installed software (not managed by apt) |
| `/home` | User home directories |
| `/root` | Root user's home |
| `/tmp` | Temporary files (cleared on reboot on most setups) |
| `/mnt` | Temporary mount points |
| `/media` | Removable media mount points |

## Default System Groups

| Group | GID | Purpose |
|-------|-----|---------|
| `root` | 0 | Superuser group |
| `sudo` | 27 | Members can use `sudo` (Debian/Ubuntu convention) |
| `adm` | 4 | Read access to log files in `/var/log` |
| `www-data` | 33 | Web server processes (Apache, Nginx) |
| `nogroup` | 65534 | Used when no group is required |
| `systemd-journal` | — | Read access to systemd journal |
| `docker` | — | Docker daemon socket access (created by Docker install) |
| `plugdev` | — | Removable device access |
| `netdev` | — | Network device management |
| `ssl-cert` | — | Read access to SSL private keys in `/etc/ssl/private` |

## UID/GID Ranges

| Range | Purpose |
|-------|---------|
| 0 | root |
| 1–99 | Statically allocated system accounts |
| 100–999 | Dynamically allocated system accounts (`adduser --system`) |
| 1000–59999 | Regular users (`adduser`) |
| 60000–64999 | Reserved (Debian) |
| 65534 | nobody/nogroup |

## apt Configuration

### File Locations

| Path | Purpose |
|------|---------|
| `/etc/apt/sources.list` | Main package sources (legacy, single file) |
| `/etc/apt/sources.list.d/` | Additional sources (`.list` or `.sources` DEB822 format) |
| `/etc/apt/preferences.d/` | Package pinning preferences |
| `/etc/apt/apt.conf.d/` | apt configuration fragments |
| `/etc/apt/trusted.gpg.d/` | Keyring files for repository signing keys |
| `/etc/apt/keyrings/` | Modern keyring location (signed-by in sources) |
| `/var/cache/apt/archives/` | Downloaded .deb package cache |
| `/var/lib/apt/lists/` | Package index cache |

### DEB822 Format (Modern)

Ubuntu 24.04+ and Debian 12+ prefer `.sources` files in DEB822 format:

```
Types: deb
URIs: https://deb.debian.org/debian
Suites: bookworm bookworm-updates
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
```

### Priority Pinning

| Priority | Effect |
|----------|--------|
| < 0 | Never install |
| 0–99 | Install only if no other version available |
| 100 | Default for installed packages |
| 500 | Default for packages in target release |
| 990 | Prefer over current version unless installed is newer |
| 1001+ | Force install (even downgrade) |

## Service Management Conventions

### Systemd Unit Locations (Load Order)

| Path | Purpose | Precedence |
|------|---------|------------|
| `/etc/systemd/system/` | Local admin overrides | Highest |
| `/run/systemd/system/` | Runtime units | Middle |
| `/lib/systemd/system/` | Package-installed units | Lowest |

### Override Pattern

Never edit units in `/lib/systemd/system/`. Instead:

```bash
systemctl edit <unit>           # Creates /etc/systemd/system/<unit>.d/override.conf
systemctl edit --full <unit>    # Full copy to /etc/systemd/system/<unit>
```

### Common Unit Types

| Suffix | Purpose |
|--------|---------|
| `.service` | Daemon or one-shot process |
| `.timer` | Scheduled activation (cron replacement) |
| `.socket` | Socket-activated service |
| `.mount` | Filesystem mount (mirrors fstab) |
| `.target` | Grouping unit (like runlevels) |
| `.path` | Path-based activation |
| `.slice` | Resource control group |

## SSH Conventions

| Path | Purpose |
|------|---------|
| `/etc/ssh/sshd_config` | Server configuration |
| `/etc/ssh/sshd_config.d/` | Drop-in config fragments (Include directive) |
| `/etc/ssh/ssh_config` | Client configuration |
| `~/.ssh/authorized_keys` | Per-user authorized public keys |
| `~/.ssh/config` | Per-user client config |
| `/etc/ssh/ssh_host_*` | Host keys (regenerate after cloning VMs) |

## Networking

### Configuration Systems by Release

| System | Used In | Config Path |
|--------|---------|-------------|
| Netplan | Ubuntu 18.04+ (default) | `/etc/netplan/*.yaml` |
| systemd-networkd | Debian 12+, Ubuntu (backend) | `/etc/systemd/network/` |
| ifupdown | Debian (legacy) | `/etc/network/interfaces` |
| NetworkManager | Desktop Ubuntu/Debian | `/etc/NetworkManager/` |

### DNS Resolution Chain

1. `/etc/nsswitch.conf` — controls resolution order
2. `systemd-resolved` (Ubuntu default) — stub resolver at `127.0.0.53`
3. `/etc/resolv.conf` — often a symlink to systemd-resolved stub
4. `/etc/hosts` — static hostname mappings

### Key Network Files

| Path | Purpose |
|------|---------|
| `/etc/hostname` | System hostname |
| `/etc/hosts` | Static name resolution |
| `/etc/resolv.conf` | DNS resolver config (often managed) |
| `/etc/nsswitch.conf` | Name service switch configuration |

## Log Locations

| Log | Path | Notes |
|-----|------|-------|
| System journal | `journalctl` | Primary on systemd systems |
| Syslog | `/var/log/syslog` | If rsyslog installed |
| Auth | `/var/log/auth.log` | SSH, sudo, PAM events |
| Kernel | `/var/log/kern.log` or `journalctl -k` | Kernel messages |
| apt | `/var/log/apt/history.log` | Package operations |
| dpkg | `/var/log/dpkg.log` | Low-level package operations |
| Boot | `journalctl -b` | Current boot messages |
| Unattended upgrades | `/var/log/unattended-upgrades/` | Auto-update logs |

## Filesystem Defaults

### Common Mount Options

| Option | Effect |
|--------|--------|
| `noatime` | Don't update access times (performance) |
| `noexec` | Prevent binary execution |
| `nosuid` | Ignore setuid/setgid bits |
| `nodev` | Ignore device files |
| `ro` | Read-only |
| `defaults` | `rw,suid,dev,exec,auto,nouser,async` |

### Recommended Security Mount Options

| Mount Point | Recommended Options |
|-------------|-------------------|
| `/tmp` | `noexec,nosuid,nodev` |
| `/var/tmp` | `noexec,nosuid,nodev` |
| `/dev/shm` | `noexec,nosuid,nodev` |
| `/home` | `nosuid,nodev` |
| `/var/log` | `noexec,nosuid,nodev` |

## Security Defaults

### PAM Configuration

| Path | Purpose |
|------|---------|
| `/etc/pam.d/` | PAM module configs per service |
| `/etc/pam.d/common-*` | Shared PAM stacks (Debian) |
| `/etc/security/limits.conf` | Resource limits |
| `/etc/security/access.conf` | Access control |

### Sudo Configuration

| Path | Purpose |
|------|---------|
| `/etc/sudoers` | Main sudoers file (edit with `visudo` only) |
| `/etc/sudoers.d/` | Drop-in files (must pass `visudo -cf` check) |

### Sudoers Best Practices

- Never edit `/etc/sudoers` directly — always `visudo`
- Drop-in files: `/etc/sudoers.d/<username>` or `/etc/sudoers.d/<role>`
- Filenames must not contain `.` or `~` (ignored by default)
- Validate before deploying: `visudo -cf /etc/sudoers.d/<file>`
- Prefer group-based rules over per-user rules

## When to Web Search Instead

These areas change frequently enough that web search is more reliable:

- **New release defaults** — Each Ubuntu/Debian release may change default configs
- **Package-specific configuration** — Application configs vary by version
- **Cloud-init behavior** — Varies by cloud provider and version
- **Snap package management** — Rapidly evolving
- **AppArmor profiles** — Package-specific, version-dependent
- **Kernel parameters** — New sysctl options added per kernel version
- **Firmware/driver issues** — Hardware-specific, kernel-version-specific
