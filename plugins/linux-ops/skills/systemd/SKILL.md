---
name: systemd
description: Manage systemd services, timers, and units on Debian/Ubuntu. Write custom service files, manage resource control, override package units, explore journal logs, and replace cron with timers.
---

# Systemd Service Management

## Overview

Manage systemd services, timers, and units on Debian/Ubuntu systems. This skill covers creating and modifying service units, understanding unit file structure, managing service state, setting up timers to replace cron, exploring journal logs, resource control, and troubleshooting systemd issues.

**Trigger this skill when:** Creating custom services, writing unit files, modifying service behavior, setting up scheduled tasks with timers, checking service status, reviewing logs, or configuring resource limits.

## Service Management Fundamentals

### Core Commands

```bash
systemctl start <unit>              # Start a service (immediate, not persistent)
systemctl stop <unit>               # Stop a service
systemctl restart <unit>            # Stop and start
systemctl reload <unit>             # Reload config without restarting
systemctl status <unit>             # Show service status and recent log
systemctl enable <unit>             # Enable (start on boot)
systemctl disable <unit>            # Disable (don't start on boot)
systemctl is-active <unit>          # Check if running (exit code 0 = active)
systemctl is-enabled <unit>         # Check if enabled (exit code 0 = enabled)
systemctl list-units --state=failed # Show all failed units
systemctl list-units --type=service # List all .service units
```

### Key Distinctions

- **start vs enable**: `start` activates now; `enable` activates on boot. A service can be enabled but not running, or running but disabled.
- **restart vs reload**: `restart` stops and starts (brief downtime); `reload` reloads config without stopping (zero downtime, not all services support it).
- **status output**: Shows active state, PID, memory, recent log lines. Use `journalctl -u <unit>` for full log history.

### Best Practice

After modifying a unit file, always run `systemctl daemon-reload` before restarting. Systemd caches unit definitions; reload updates the cache.

## Unit File Structure

Systemd unit files are INI-style configuration files with `[Section]` headers. Most common units are `.service` files.

### Basic Service Structure

```ini
[Unit]
Description=My Custom Service
After=network.target                # Start after network is ready
Wants=network-online.target         # Optional: recommended dependencies
Requires=database.service           # Hard dependency: fail if this fails

[Service]
Type=simple                         # Service type (see Type Values below)
ExecStart=/usr/bin/myapp --config /etc/myapp.conf
ExecReload=/bin/kill -HUP $MAINPID # Optional: reload command
ExecStop=/bin/kill -TERM $MAINPID  # Optional: custom stop sequence
Restart=on-failure                  # Restart policy (see Restart Policies below)
RestartSec=5                        # Wait 5s before restarting
User=myapp                          # Run as this user
Group=myapp                         # Run as this group
WorkingDirectory=/var/lib/myapp     # Change directory before starting
Environment="VAR=value"             # Set environment variable
EnvironmentFile=/etc/default/myapp  # Load environment from file
StandardOutput=journal              # Log stdout to journal
StandardError=journal               # Log stderr to journal

[Install]
WantedBy=multi-user.target          # Enabled symlinks in this target's .wants/
```

### Type Values

| Type | When to Use | Behavior |
|------|-------------|----------|
| `simple` | Most services | ExecStart process is the main service. Default. |
| `forking` | Daemons that fork (e.g., old-style daemons) | Parent process exits; child continues. Systemd waits for parent exit. |
| `oneshot` | One-time tasks, scripts | Runs once; service is "inactive" after. Useful for initialization. |
| `notify` | Services that signal readiness | Service signals systemd when ready via `sd_notify()` (Type=notify, ExecStart must be a dbus-aware binary). Systemd waits for signal before starting dependents. |
| `dbus` | Services that acquire a D-Bus name | Similar to notify; systemd waits for D-Bus name acquisition. |

### Restart Policies

| Policy | Restarts When |
|--------|---------------|
| `no` | Never restart (default) |
| `always` | Always restart, even if exited cleanly |
| `on-failure` | Only if exited with non-zero status |
| `on-abnormal` | Only if terminated by signal or timeout |
| `on-success` | Only if exited cleanly |
| `on-watchdog` | Only if watchdog timeout triggers |

### Key Directives

| Directive | Purpose | Example |
|-----------|---------|---------|
| `Description` | Human-readable unit name | `Description=My Web Server` |
| `After`/`Before` | Ordering (not hard dependency) | `After=network.target` |
| `Wants` | Soft dependency (don't fail if missing) | `Wants=optional-service.service` |
| `Requires` | Hard dependency (fail if missing) | `Requires=database.service` |
| `ExecStart` | Main process command | `ExecStart=/usr/bin/myapp` |
| `ExecReload` | Reload signal handler | `ExecReload=/bin/kill -HUP $MAINPID` |
| `ExecStop` | Custom stop sequence | `ExecStop=/bin/kill -TERM $MAINPID` |
| `User`/`Group` | Run as this user/group | `User=www-data` |
| `WorkingDirectory` | Change cwd before starting | `WorkingDirectory=/var/www` |
| `Environment` | Set environment variables | `Environment="DEBUG=1"` |
| `EnvironmentFile` | Load environment from file | `EnvironmentFile=/etc/default/app` |
| `StandardOutput`/`StandardError` | Redirect output | `StandardOutput=journal` |
| `Restart`/`RestartSec` | Restart policy and delay | `Restart=on-failure` / `RestartSec=5` |
| `TimeoutStartSec` | Max startup time before failure | `TimeoutStartSec=30s` |
| `TimeoutStopSec` | Max stop time before kill | `TimeoutStopSec=10s` |
| `WantedBy` | Target that wants this unit | `WantedBy=multi-user.target` |

## Writing Custom Services

### Placement

From debian-conventions.md, systemd loads units in this order (first found wins):

| Path | Purpose | Precedence |
|------|---------|-----------|
| `/etc/systemd/system/` | Local admin overrides | Highest |
| `/run/systemd/system/` | Runtime units | Middle |
| `/lib/systemd/system/` | Package-installed units | Lowest |

**Never edit files in `/lib/systemd/system/`** — packages will overwrite them. Always place custom units in `/etc/systemd/system/`.

### Simple Service Example

```ini
[Unit]
Description=Python Web App
After=network.target

[Service]
Type=simple
User=appuser
Group=appuser
WorkingDirectory=/opt/myapp
Environment="PYTHONUNBUFFERED=1"
ExecStart=/usr/bin/python3 /opt/myapp/app.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable myapp.service
sudo systemctl start myapp.service
sudo systemctl status myapp.service
```

### Oneshot Service (Task)

For one-time initialization scripts:

```ini
[Unit]
Description=Initialize Application Data
Before=myapp.service

[Service]
Type=oneshot
ExecStart=/opt/myapp/init.sh
User=appuser
RemainAfterExit=yes                # Service stays "active" even after exit

[Install]
WantedBy=multi-user.target
```

### Service with Dependencies

```ini
[Unit]
Description=My App Service
Requires=postgresql.service         # Fail if PostgreSQL isn't running
After=postgresql.service            # Order: start PostgreSQL first

[Service]
Type=simple
ExecStart=/usr/bin/myapp
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## Overriding Package-Installed Units

When a package provides a unit (e.g., nginx.service), override it without creating a full copy.

### Using systemctl edit (Recommended)

Create a drop-in override (doesn't overwrite package unit):

```bash
sudo systemctl edit nginx.service
```

This opens an editor for `/etc/systemd/system/nginx.service.d/override.conf`. Add only the sections to override:

```ini
[Unit]
Description=Nginx Web Server (Custom Override)

[Service]
ExecStart=
ExecStart=/usr/sbin/nginx -g "daemon off;" -c /etc/nginx/custom.conf
Environment="WORKER_PROCESSES=8"
```

Note: `ExecStart=` (empty) clears the original before setting the new one. This prevents appending.

### Full Copy (systemctl edit --full)

For extensive changes:

```bash
sudo systemctl edit --full nginx.service
```

This copies the entire unit to `/etc/systemd/system/nginx.service` for full customization.

### Never Direct Edit

Avoid editing `/lib/systemd/system/` or `/etc/systemd/system/nginx.service` directly if the package provided the unit. Use `systemctl edit`.

## Timers (Cron Replacement)

Timers are systemd units that trigger other units on a schedule. They replace cron for modern systems.

### Timer Unit Structure

```ini
[Unit]
Description=Run Backup Daily
Requires=backup.service            # Require this service to exist

[Timer]
OnCalendar=daily                   # Schedule: daily, weekly, monthly, or cron-like
OnBootSec=5min                     # Also run 5min after boot
Persistent=true                    # If missed, run once after boot
Unit=backup.service                # Service to activate

[Install]
WantedBy=timers.target             # Start this timer on boot
```

### OnCalendar Expressions

| Expression | Meaning |
|-----------|---------|
| `daily` or `*-*-* 00:00:00` | Midnight every day |
| `weekly` or `Mon *-*-* 00:00:00` | Monday midnight |
| `monthly` | First day of month at 00:00 |
| `yearly` | Jan 1 at 00:00 |
| `*-*-* 09:30:00` | 9:30 AM every day (custom time) |
| `Mon,Wed,Fri *-*-* 14:00:00` | Monday, Wednesday, Friday at 2 PM |
| `*-*-1,15 *-*-* 03:00:00` | 1st and 15th of month at 3 AM |
| `Mon *-*-* 09:00, 14:00, 18:00` | Mon at 9 AM, 2 PM, 6 PM (multiple times) |

See `man systemd.time` for full syntax.

### Other Timer Options

| Option | Purpose |
|--------|---------|
| `OnBootSec=10min` | Run 10 minutes after boot |
| `OnUnitActiveSec=1h` | Run 1 hour after service last activated |
| `OnCalendar=*-*-* 12:00:00` | Run at noon every day |
| `Persistent=true` | If timer missed (system was down), run once on boot |
| `Unit=<service>` | Service to activate (default: unit name with .service) |
| `AccuracySec=1s` | How precise the timer should be (1s, 1min, etc.) |

### Timer Example: Daily Backup

1. Create the service (`/etc/systemd/system/backup.service`):

```ini
[Unit]
Description=Daily System Backup
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh
User=root
StandardOutput=journal
StandardError=journal
```

2. Create the timer (`/etc/systemd/system/backup.timer`):

```ini
[Unit]
Description=Daily Backup Schedule
Requires=backup.service

[Timer]
OnCalendar=daily
OnBootSec=10min
Persistent=true
Unit=backup.service

[Install]
WantedBy=timers.target
```

3. Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable backup.timer
sudo systemctl start backup.timer
sudo systemctl list-timers               # See all timers
sudo systemctl list-timers backup.timer  # See next run time
```

## Journal Logging

Systemd's journal is the primary logging system on modern Linux. All service output goes here by default.

### Basic Queries

```bash
journalctl -u nginx.service                # Logs for nginx service only
journalctl -u nginx.service -f             # Follow (tail -f mode)
journalctl -u nginx.service -n 50          # Last 50 lines
journalctl -u nginx.service --since "5 min ago"  # Last 5 minutes
journalctl -u nginx.service --until "10 min ago" # Until 10 minutes ago
journalctl -b                              # Current boot only
journalctl -b -1                           # Previous boot
journalctl -p err                          # Error priority and above
journalctl -p notice..err                  # Range: notice to error
```

### Priority Levels

From high to low: `emerg`, `alert`, `crit`, `err`, `warning`, `notice`, `info`, `debug`

### Filtering and Analysis

```bash
journalctl -u nginx.service | grep "GET"  # Search logs
journalctl --no-pager                     # Don't paginate (good for scripts)
journalctl -o json                        # JSON output (machine-readable)
journalctl -o verbose                     # Very detailed output
journalctl -S "2024-01-15" -U "2024-01-16"  # Date range
```

### Persistent Journal

By default, the journal is stored in `/run/systemd/journal/` (lost on reboot). To persist:

```bash
sudo mkdir -p /var/log/journal
sudo systemctl restart systemd-journald
```

Then configure in `/etc/systemd/journald.conf`:

```ini
[Journal]
Storage=persistent                  # persistent, volatile, auto
MaxRetentionSec=30day              # Keep logs for 30 days
SystemMaxUse=1G                    # Max disk usage
```

## Resource Control

Limit CPU, memory, I/O, and other resources for a service.

### Adding Resource Limits

Edit the service and add limits to `[Service]`:

```bash
sudo systemctl edit myapp.service
```

```ini
[Service]
CPUQuota=50%                       # Limit to 50% of 1 CPU core
MemoryMax=512M                     # Hard memory limit
MemoryHigh=256M                    # Memory warning (before OOM)
IOWeight=100                       # Relative I/O weight (default 100)
TasksMax=100                       # Max processes this service can spawn
```

### Common Limits

| Directive | Example | Purpose |
|-----------|---------|---------|
| `CPUQuota` | `50%` or `200%` | Limit CPU usage (100% = 1 core) |
| `CPUAccounting` | `yes` | Enable CPU time tracking |
| `MemoryMax` | `512M` | Hard memory limit (kill if exceeded) |
| `MemoryHigh` | `256M` | Soft limit (warns but doesn't kill) |
| `MemoryAccounting` | `yes` | Enable memory tracking |
| `IOWeight` | `100` | Relative I/O priority (10-1000) |
| `IOReadBandwidthMax` | `/dev/sda 100M` | Limit read throughput |
| `IOWriteBandwidthMax` | `/dev/sda 50M` | Limit write throughput |
| `TasksMax` | `1000` | Max processes the service can create |

### Applying and Checking

```bash
sudo systemctl daemon-reload
sudo systemctl restart myapp.service
systemctl show myapp.service -p CPUQuota -p MemoryMax  # Verify
```

## Hardening Units

Apply security restrictions to services via `[Service]` section:

```ini
[Service]
ProtectSystem=strict               # Read-only filesystem (except /dev, /proc, /run)
ProtectHome=yes                    # Hide /home, /root, /run/user
NoNewPrivileges=yes                # Prevent privilege escalation
PrivateTmp=yes                     # Private /tmp (per-service)
ReadOnlyPaths=/etc                 # Make /etc read-only for this service
ReadWritePaths=/var/log/myapp      # Except /var/log/myapp (writable)
```

## Targets (Runlevels)

Targets are groupings of units, similar to old runlevels.

### Common Targets

| Target | Purpose |
|--------|---------|
| `multi-user.target` | Multi-user mode (no GUI) — usual default |
| `graphical.target` | Multi-user + GUI (depends on multi-user) |
| `rescue.target` | Single-user shell for repair |
| `reboot.target` | Reboot |
| `poweroff.target` | Shutdown |
| `halt.target` | Halt |

### Checking and Setting Default

```bash
systemctl get-default                      # Show default target on boot
sudo systemctl set-default multi-user.target  # Set default
systemctl isolate rescue.target             # Switch to rescue (emergency)
systemctl isolate graphical.target          # Switch to GUI (if installed)
```

## Troubleshooting

### Unit File Syntax Errors

After editing a unit file, systemd reports errors in `status` output:

```bash
sudo systemctl daemon-reload  # Check and reload all units
systemctl status myapp.service  # See any errors
```

Look for messages like `Invalid directive "BadKey"` or `Failed to parse value`. Edit with `systemctl edit` to fix.

### Dependency Issues

Check what a unit depends on:

```bash
systemctl show myapp.service -p Requires -p After -p Wants
```

Check what depends on a unit:

```bash
systemctl show postgresql.service -p WantedBy -p RequiredBy
```

Circular dependencies cause boot failure. Use `systemd-analyze verify <unit>` (newer systemd) to check.

### Startup Performance Analysis

```bash
systemd-analyze                      # Overall boot time
systemd-analyze blame                # Slowest services (critical path)
systemd-analyze critical-chain       # Dependency chain affecting boot time
systemd-analyze verify <unit>        # Check unit for errors
```

### Service Won't Start

Check status and journal:

```bash
sudo systemctl status myapp.service         # See error
sudo journalctl -u myapp.service -n 20     # Recent logs
sudo journalctl -u myapp.service -f        # Follow logs while starting
```

Common issues:
- **Permission denied**: Check `User=` and file ownership
- **No such file or directory**: Verify `ExecStart=` path and `WorkingDirectory=`
- **Timeout**: Increase `TimeoutStartSec=`
- **Dependencies failing**: Check `Requires=` and `After=` ordering

### Reload Doesn't Work

Not all services support reload. If `systemctl reload` fails:

```bash
sudo systemctl restart myapp.service  # Use restart instead
```

Only services with `ExecReload=` support reload. Verify before documenting it.

## Socket Activation

Services can start on-demand when a socket receives data (advanced).

Brief overview: Create a `.socket` unit that listens on a port/path, then have the `.service` listen on the inherited socket. Systemd starts the service only when needed. Use for infrequently-used services to save resources.

```ini
# myapp.socket
[Unit]
Description=My App Socket
Before=myapp.service

[Socket]
ListenStream=8080

[Install]
WantedBy=sockets.target

# myapp.service
[Unit]
Requires=myapp.socket

[Service]
ExecStart=/usr/bin/myapp
```

For most use cases, this is overkill — just use `Type=simple`.

## Best Practices

1. **Always `systemctl daemon-reload` after editing unit files** — Systemd caches definitions.
2. **Use `systemctl edit` for overrides** — Never directly edit package units in `/lib/systemd/system/`.
3. **Set `Type=simple` by default** — It's the most predictable for most services.
4. **Use `Type=oneshot` with `RemainAfterExit=yes` for initialization scripts** — Prevents repeated runs.
5. **Use timers instead of cron** — More flexible scheduling, better integration with systemd.
6. **Redirect stdout/stderr to journal** — `StandardOutput=journal StandardError=journal` for unified logging.
7. **Set `Restart=on-failure`** — Services should survive temporary failures gracefully.
8. **Use soft dependencies (Wants=) for optional features** — Use `Requires=` only for critical deps.
9. **Specify users and groups** — Don't run services as root unless necessary. Use `User=` and `Group=`.
10. **Document custom units with `Description=`** — Makes troubleshooting easier later.
11. **Use `OnBootSec=` for timers in addition to `OnCalendar=`** — Ensures tasks run after boot even if machine was off.
12. **Test before deploying** — Use `systemctl daemon-reload`, enable, and verify with `systemctl status`.

## References

- debian-conventions.md — Systemd paths, units, and load order
- `/etc/systemd/system/` — Local unit file directory
- `/lib/systemd/system/` — Package-provided units (read-only)
- `man systemd.service` — Service unit directive reference
- `man systemd.timer` — Timer unit syntax and examples
- `man systemd.unit` — [Unit] section directives
- `man journalctl` — Journal querying
- `systemd-analyze` — Boot performance and dependency analysis
