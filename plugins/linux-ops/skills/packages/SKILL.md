---
name: packages
description: Install, update, and manage Debian/Ubuntu packages with apt. Covers repository management, package pinning, unattended upgrades, security updates, and troubleshooting.
---

# Package Management

## Overview

Manage Debian/Ubuntu packages and repositories using apt. This skill covers installing and updating packages, configuring repositories, pinning versions, setting up automatic updates, and diagnosing package issues.

**Trigger this skill when:** Installing/removing packages, updating systems, adding third-party repositories, pinning specific versions, configuring unattended upgrades, or fixing package conflicts.

## apt Fundamentals

### Common Operations

```bash
apt update                    # Refresh package index (always do before install)
apt install <package>         # Install one or more packages
apt remove <package>          # Remove package (keeps config files)
apt purge <package>           # Remove package and config files
apt upgrade                   # Update installed packages (safe, respects pinning)
apt full-upgrade              # Dist-upgrade (may remove packages if needed)
apt autoremove                # Remove unused dependencies
apt clean                     # Clear cached .deb files
apt autoclean                 # Clear cached obsolete .deb files
apt search <term>             # Search package database
apt show <package>            # Show package details (version, depends, size)
```

### Key Distinctions

- **apt upgrade** vs **apt full-upgrade**: Use `upgrade` for regular updates (respects pinning, doesn't remove). Use `full-upgrade` for release upgrades (dist-upgrade equivalent, may break things).
- **apt remove** vs **apt purge**: Use `remove` to keep config; use `purge` for clean removal (useful before reinstalling).
- **apt** vs **apt-get**: Use `apt` for interactive commands (human-readable output). Use `apt-get` in scripts (stable interface).

### Best Practice

Always run `apt update` before `apt install` to avoid stale package cache causing "not found" errors.

## Repository Management

### Adding Repositories

**Modern approach (DEB822 format, Ubuntu 24.04+ / Debian 12+):**

Create `.sources` file in `/etc/apt/sources.list.d/`:

```bash
cat > /etc/apt/sources.list.d/docker.sources << 'EOF'
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: bookworm
Components: stable
Architectures: amd64
Signed-By: /etc/apt/keyrings/docker.gpg
EOF
```

Then download and verify the signing key:

```bash
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
apt update
```

**Legacy approach (.list files):**

```bash
echo "deb https://download.docker.com/linux/debian bookworm stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Add signing key
curl -fsSL https://download.docker.com/linux/debian/gpg | \
  sudo apt-key add -
```

### Repository Configuration

Key locations (from debian-conventions.md):

| Path | Purpose |
|------|---------|
| `/etc/apt/sources.list` | Main sources (legacy, single file) |
| `/etc/apt/sources.list.d/` | Additional sources (`.list` or `.sources` DEB822 format) |
| `/etc/apt/trusted.gpg.d/` | Keyring files for repo signing keys |
| `/etc/apt/keyrings/` | Modern keyring location (referenced via `Signed-By`) |

### DEB822 Format Reference

```
Types: deb
URIs: https://deb.debian.org/debian
Suites: bookworm bookworm-updates
Components: main contrib non-free non-free-firmware
Architectures: amd64 arm64
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
```

### Repository Best Practices

- Always use signed repositories (verify GPG key fingerprints before trusting).
- Prefer `.sources` (DEB822) format on modern systems — cleaner and more maintainable.
- Store keyrings in `/etc/apt/keyrings/` and reference via `Signed-By` in `.sources` files.
- Keep `/etc/apt/sources.list.d/` organized by service/provider.
- Test new repos with `apt update` before installing packages.

## Package Pinning

Control which version of a package is installed or preferred. Pinning is managed in `/etc/apt/preferences.d/` files.

### Preference File Structure

```
Package: <package-name>
Pin: <pin-specification>
Pin-Priority: <priority>
```

### Priority Values

From debian-conventions.md:

| Priority | Effect |
|----------|--------|
| < 0 | Never install this version |
| 0–99 | Install only if explicitly requested |
| 100 | Default for installed packages |
| 500 | Default for packages in target release |
| 990 | Prefer but don't force |
| 1001+ | Force (even downgrade) |

### Common Use Cases

**Hold a package at current version (prevent upgrades):**

```
Package: postgresql
Pin: version *
Pin-Priority: 1001
```

Or use apt directly:

```bash
apt-mark hold postgresql        # Prevent upgrades
apt-mark unhold postgresql      # Allow upgrades again
apt-mark showhold               # Show all held packages
```

**Prefer backports but allow updates from main:**

Create `/etc/apt/preferences.d/backports`:

```
Package: *
Pin: release a=bookworm-backports
Pin-Priority: 490

Package: *
Pin: release a=bookworm
Pin-Priority: 500
```

(Backports default to 100; this bumps them to 490 while keeping main at 500.)

**Pin specific version:**

```
Package: docker.io
Pin: version 24.0.*
Pin-Priority: 900
```

### Testing Pin Effects

Before deploying:

```bash
apt-get install --dry-run <package>    # See what would happen
apt policy <package>                     # Show all available versions and current pin
```

## Unattended Upgrades

Automatically apply security updates on a schedule.

### Installation and Setup

```bash
apt install unattended-upgrades apt-listchanges
```

Main config: `/etc/apt/apt-conf.d/50unattended-upgrades`

### Configuration

Enable automatic security updates:

```bash
cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF
```

Customize origins (security-only updates):

Edit `/etc/apt/apt-conf.d/50unattended-upgrades` and modify the `Unattended-Upgrade::Allowed-Origins` section:

```
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};
```

### Advanced Options

**Blacklist packages (skip automatic updates):**

```
Unattended-Upgrade::Package-Blacklist {
    "postgresql";
    "mysql-server";
};
```

**Enable automatic reboot after updates:**

```
Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-Time "02:00";
```

**Email notifications:**

```
Unattended-Upgrade::Mail "admin@example.com";
Unattended-Upgrade::Mail-Report "on-change";  # or "always"
```

### Logs and Debugging

```bash
tail -f /var/log/unattended-upgrades/unattended-upgrades.log
systemctl status unattended-upgrades
journalctl -u unattended-upgrades -n 50
```

## Version Management

### Check Versions

```bash
apt list --installed                # List all installed packages with versions
apt list --upgradable               # Show packages with available updates
apt-cache policy <package>          # Show available + installed versions
dpkg -l | grep <pattern>            # Low-level package listing
```

### View Available Versions

```bash
apt list -a <package>               # All available versions from repos
apt-cache versions <package>         # Show version history
```

### Change Installed Version

```bash
apt install <package>=<version>     # Install specific version (exact pin)
apt install <package>/bookworm      # Install from specific release
```

## Troubleshooting

### Broken Dependencies

```bash
apt --fix-broken install            # Resolve broken dependency chains
apt install -f                      # Short form of --fix-broken
```

### Hash Sum Mismatch

Indicates corrupted cache:

```bash
rm /var/lib/apt/lists/* -vf         # Clear package lists
apt clean                            # Clear cached .deb files
apt update                           # Rebuild cache
apt install -f                       # Fix any broken packages
```

### Lock File Issues

Another process is using apt:

```bash
lsof /var/lib/apt/lists/lock        # Find blocking process
# Wait for process to finish, or:
sudo kill -9 <pid>                  # Last resort; may corrupt state
rm /var/lib/apt/lists/lock          # Clean up after force-kill
apt update                           # Rebuild
```

### Configure Pending Packages

dpkg in inconsistent state:

```bash
dpkg --configure -a                 # Complete interrupted configurations
apt install -f                      # Fix dependency issues
```

### Unmet Dependencies

```bash
apt install -f                      # Attempt auto-fix
apt-get install --no-install-recommends <package>  # Skip recommends
```

### Check Syntax Errors in Sources

```bash
apt-key list                         # View trusted keys (deprecated, for legacy)
apt-cache search .                   # Test if repos are reachable
```

## Security Updates

### Identify Security Updates

```bash
apt list --upgradable               # Shows all available updates
apt update && apt install -s         # Simulate full upgrade (see what would happen)
```

### Ubuntu Pro / ESM (Extended Security Maintenance)

For long-term support releases (LTS), Ubuntu Pro provides security updates beyond the standard 5-year window:

```bash
sudo pro enable esm-apps esm-infra   # Enable Extended Security Maintenance
pro status                            # Check Pro status and coverage
```

Debian users should check debian-security.org for security announcements.

### Security Repository

Both Debian and Ubuntu maintain dedicated security repositories:

**Debian:**
```
Types: deb
URIs: http://security.debian.org/debian-security
Suites: bookworm-security
Components: main contrib non-free non-free-firmware
```

**Ubuntu (included by default):**
```
Types: deb
URIs: http://security.ubuntu.com/ubuntu
Suites: focal-security
Components: main restricted universe multiverse
```

## Best Practices

1. **Always `apt update` before install** — Prevents stale cache errors.
2. **Use `apt`, not `apt-get`, for interactive use** — Better output formatting.
3. **Don't mix repositories carelessly** — Different repos may have conflicting library versions.
4. **Test pinning with `apt policy` first** — Verify desired version will be selected.
5. **Keep `/etc/apt/sources.list.d/` organized** — One file per service/provider.
6. **Use DEB822 format (.sources) on modern systems** — More maintainable than legacy .list files.
7. **Verify GPG keys before trusting repos** — Check fingerprints from official sources.
8. **Review unattended-upgrade logs regularly** — Catch failed updates or unexpected removals.
9. **Test major upgrades (full-upgrade) on non-prod first** — These can break system packages.
10. **Use `apt-mark hold` instead of manual pinning for version freezes** — Simpler and more readable.

## References

- `/etc/apt/sources.list` — Main source listing
- `/etc/apt/sources.list.d/` — Additional sources directory
- `/etc/apt/preferences.d/` — Pinning preferences
- `/etc/apt/apt.conf.d/` — apt configuration
- `/etc/apt/trusted.gpg.d/` — Legacy keyring location
- `/etc/apt/keyrings/` — Modern keyring location
- `/var/log/apt/history.log` — apt operation history
- `/var/log/unattended-upgrades/` — Automatic update logs
- debian-conventions.md — Debian filesystem and configuration standards
