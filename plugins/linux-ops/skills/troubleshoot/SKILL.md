---
name: troubleshoot
description: Diagnose Linux system issues on Debian/Ubuntu. Trigger when system is slow, CPU/memory/disk is high, services fail to start, network is broken, boot issues occur, or any other performance/connectivity problem. Provides systematic diagnostics starting with general triage commands, then workflows for specific issue types (CPU load, memory pressure, disk space, networking, services, boot, processes).
---

# Troubleshoot

## Overview

Systematically diagnose and investigate Linux system issues on Debian/Ubuntu systems. This skill provides diagnostic workflows starting with quick triage to identify the problem area, then deep-dive diagnostics for specific failure modes. Covers system load, memory, disk, networking, services, boot, and process issues.

**WHEN to use:** System is slow, unresponsive, services won't start, can't connect, out of disk space, high CPU/memory, boot issues, or diagnosis of any Linux system behavior.

## Quick Triage (Always Start Here)

Run these commands first to establish baseline system health:

```bash
# Load and uptime
uptime

# Memory: focus on "available" column, not "free"
free -h

# Disk space by mount point
df -h

# Inodes (can run out even with disk space available)
df -i

# Recent errors (last hour)
journalctl -p err --since "1 hour ago"

# Failed services
systemctl list-units --failed
```

**Quick interpretation:**
- **Load average:** Compare to CPU count (`nproc`). Load=4 on 2-core is bad; load=4 on 8-core is fine.
- **Available memory:** This is what matters (includes page cache). "Free" can be misleading.
- **df -i inode saturation:** If >90%, see [Disk Space](#disk-space) section.
- **Errors in journal:** Focus on timeframe matching the issue.
- **Failed systemd units:** Immediate action items.

## High CPU / Load

**Symptoms:** System slow, high load average, CPU near 100%.

### Step 1: Identify the hot process

```bash
# Real-time view, sorted by CPU
top
# or for better interactivity
htop

# One-time snapshot, top consumers first
ps aux --sort=-%cpu | head -20

# Check for runaway/forking processes
ps aux | grep -E "defunct|<zombie>"
```

### Step 2: Understand context

```bash
# Check iowait vs actual CPU (iostat column %util vs %iowait)
iostat -x 1 5

# If load is high but CPU usage low, you're I/O bound, not CPU bound
vmstat 1 5
# Look at "wa" (wait I/O) column
```

### Step 3: Actions

**If legitimate process is consuming CPU:**
- Lower its priority: `renice -n +10 -p <pid>` (lower priority, 0-20 scale)
- Kill if runaway: `kill -9 <pid>` (only after confirmation)
- Check if it should be running: `systemctl status <service-name>`

**If iowait is the culprit:**
- CPU is waiting for disk I/O — see [Disk Space](#disk-space) or [Storage](#storage--io-performance)
- CPU usage is masked by blocking on I/O

**If load is from fork bombs:**
```bash
# See max processes per user (check limits)
ulimit -u

# Temporarily kill the offender or reboot
```

## Memory Pressure

**Symptoms:** System slow, swap thrashing, "out of memory" errors, OOM killer triggered.

### Step 1: Check memory usage

```bash
# Detailed breakdown
free -h
cat /proc/meminfo

# Memory hogs by process
ps aux --sort=-%mem | head -20

# Check swap usage and pressure
free -h | grep Swap
swapon --show

# OOM killer activity
dmesg | grep -i oom | tail -10
journalctl -p err | grep -i oom
```

### Step 2: Identify pressure points

```bash
# Pages being reclaimed (swap activity)
vmstat 1 5
# Look for "si" (swap in) and "so" (swap out) — non-zero = memory pressure

# Buffer/cache: can be evicted if needed
# Applications using RSS (resident set = actual physical memory)
ps aux --sort=-%mem | head -5 && echo "^^^ Look at RSS column"
```

### Step 3: Actions

**If swap is thrashing:**
- Add RAM (best solution)
- Identify and kill memory hogs: `kill <pid>`
- Increase swap space (temporary, slow): See storage section
- Disable less critical services: `systemctl disable <service>`

**If OOM killer triggered:**
```bash
# See which process was killed
dmesg | grep "Killed process"

# Adjust OOM killer priority for critical processes
# echo -n 100 > /proc/<pid>/oom_score_adj  # (lower score = protect)
```

**If tmpfs is full:**
```bash
# /dev/shm (shared memory)
df -h /dev/shm
du -sh /dev/shm/* | sort -h

# /tmp
df -h /tmp
du -sh /tmp/* | sort -h
```

## Disk Space

**Symptoms:** "No space left on device," `df -h` shows 100% usage.

### Step 1: Quick diagnosis

```bash
# Find the full filesystem
df -h | grep 100%

# Check if it's inodes or blocks
df -i | grep full-filesystem
# If inodes are the issue, see below
```

### Step 2: Find what's consuming space

```bash
# Largest directories
du -sh /* | sort -h | tail -10

# Dig deeper (specific filesystem)
du -sh /var/* | sort -h

# Find large files
find /var -type f -size +100M -exec ls -lh {} \; 2>/dev/null | sort -k5 -h
```

### Step 3: Common culprits and fixes

**Journal taking up space:**
```bash
# Check journal size
journalctl --disk-usage

# Vacuum to specific size (keep last 500MB)
journalctl --vacuum-size=500M

# Or by time (keep 7 days)
journalctl --vacuum-time=7d
```

**Old APT packages:**
```bash
# Clean apt cache
apt clean          # removes all cached .deb files
apt autoclean      # removes old cached packages only
```

**Deleted but open files (still consuming space):**
```bash
# Find them
lsof +D /var | grep deleted

# Cause: process has file open but file was deleted
# Solution: restart the process or kill it
systemctl restart <service>
```

**Log files:**
```bash
# Find and truncate old logs
find /var/log -type f -name "*.log" -mtime +30 -delete
# or truncate instead of delete to preserve permissions:
find /var/log -type f -name "*.log" -mtime +30 -exec truncate -s 0 {} \;
```

### Step 4: Inode exhaustion

If `df -i` shows 100% but `df -h` shows space available:

```bash
# Find files/dirs taking up inodes (usually many small files)
find /var -type f | wc -l        # total files
find /var -type d | wc -l        # total dirs

# Find the culprit directory
find /var -mindepth 2 -maxdepth 2 -type d | while read d; do echo "$(find "$d" -type f 2>/dev/null | wc -l) $d"; done | sort -rn | head -10

# Clean up: if it's temp/cache, delete; if app data, restart app and check
```

## Network Connectivity

**Symptoms:** Can't reach host, DNS not working, service port unreachable.

### Step 1: Link and routing

```bash
# Is interface up?
ip link show

# Do we have an IP?
ip addr show

# Can we reach the gateway?
ip route show              # what's the default route?
ping <gateway-ip>

# Is DNS working?
dig example.com
nslookup example.com
# or test with IP directly to bypass DNS
curl http://8.8.8.8       # should fail, but tests connectivity
```

### Step 2: Service and firewall

```bash
# Is the service listening on the port?
ss -tlnp | grep <port>
# or: netstat -tlnp | grep <port>

# Test the port locally
curl http://localhost:<port>

# Can we reach it from another host?
curl http://<target-ip>:<port>

# Check firewall
ufw status
sudo ufw show added        # to see active rules
# Test: ufw allow <port> then retry

# Check if port is in /etc/services (helps with service lookup)
grep <port>/tcp /etc/services
```

### Step 3: DNS specifically

```bash
# Check resolvers
cat /etc/resolv.conf

# Test direct query
dig @8.8.8.8 example.com

# Trace the query
dig +trace example.com

# Check system DNS (systemd-resolved)
systemctl status systemd-resolved
resolvectl status
```

### Step 4: Connection issues

```bash
# Connection timeout or refused?
curl -vv http://<target>:<port>
# Look at "Connected to" vs "Connection refused"

# Check netstat for LISTEN vs ESTABLISHED
ss -tna | grep -E "LISTEN|ESTABLISHED|TIME_WAIT"

# For SSH specifically
ssh -vvv user@host          # verbose output shows negotiation

# Network path analysis
traceroute <target>
mtr <target>                # real-time traceroute
```

## Service Won't Start

**Symptoms:** `systemctl start <service>` fails, service is inactive.

### Step 1: Service status and logs

```bash
# What's the error?
systemctl status <service>

# More detail from journal
journalctl -u <service> -n 50 --no-pager

# Full log for that service since boot
journalctl -u <service> -b
```

### Step 2: Check dependencies and conflicts

```bash
# What does this service depend on?
systemctl list-dependencies <service>

# What services depend on it?
systemctl list-dependencies --reverse <service>

# Is a conflicting service running?
systemctl list-units --type=service --active
```

### Step 3: Configuration and permissions

```bash
# Validate config (service-specific, examples below)
sshd -t                    # SSH config check
nginx -t                   # Nginx config check
apache2ctl configtest      # Apache config check

# Check service file syntax
systemd-analyze verify <service-name>

# File/directory permissions
ls -la /etc/<service>/
ls -la /var/log/<service>/
# User running service should have read access to config, write to log/data dirs
```

### Step 4: Port conflicts

```bash
# Is the port already in use?
ss -tlnp | grep <port>

# Kill the conflicting process or change the port
# then restart the service
systemctl restart <service>
```

### Step 5: Enable and start

```bash
# Enable on boot, then start
systemctl enable <service>
systemctl start <service>

# Verify it's running and will start on boot
systemctl is-enabled <service>
systemctl is-active <service>
```

## Boot Issues

**Symptoms:** System won't boot, hangs during boot, boots to emergency mode.

### Step 1: Check previous boot

```bash
# Logs from previous boot (before the hang/crash)
journalctl -b -1           # -1 = previous boot
journalctl -b -1 --no-pager -p err

# Boot performance analysis
systemd-analyze blame      # slowest startup units
systemd-analyze critical-chain
```

### Step 2: Emergency/rescue mode entry

```bash
# If stuck in emergency mode, start the shell
systemctl default          # return to multi-user from emergency

# Check for filesystem errors
systemctl status          # look for fsck pending
# or reboot with: systemctl reboot --force
```

### Step 3: fstab issues

```bash
# Check for bad entries
cat /etc/fstab

# Validate mount points exist
ls -la /mount/point

# Test mount manually
mount /mount/point
# or mount by UUID
mount UUID=<uuid> /mount/point
```

### Step 4: Bootloader and kernel

```bash
# Check bootloader (GRUB)
grub-mkconfig -o /boot/grub/grub.cfg

# List available kernels
ls -la /boot/vmlinuz*

# Current kernel
uname -a
```

## Process Debugging

**Symptoms:** Process consuming resources, hung process, need to understand what a process is doing.

### Step 1: Process state

```bash
# Is it running, sleeping, or stopped?
ps aux | grep <process-name>
# Look at STAT column: S (sleeping), R (running), Z (zombie), T (stopped)

# Detailed info
ps -eo pid,ppid,cmd,stat,etime | grep <pid>
```

### Step 2: Open files and sockets

```bash
# What files is it reading/writing?
lsof -p <pid>

# Just network connections
lsof -i -p <pid>

# Open file descriptors
ls -la /proc/<pid>/fd/

# Any memory-mapped files?
cat /proc/<pid>/maps
```

### Step 3: Trace system calls

```bash
# See what the process is doing at the kernel level
strace -p <pid>                    # attach to running process

# Limit to specific syscalls
strace -p <pid> -e trace=open,read,write

# With timestamps
strace -p <pid> -t

# To file (large output)
strace -p <pid> -o /tmp/trace.log
```

### Step 4: Environment and limits

```bash
# Process environment variables
cat /proc/<pid>/environ | tr '\0' '\n'

# Resource limits
cat /proc/<pid>/limits

# Memory layout
cat /proc/<pid>/status | grep Vm
```

## Performance Baseline

**Establish what "normal" looks like before investigating.**

### Step 1: System-wide metrics

```bash
# Snapshot of current state
vmstat 1 5                 # 5 iterations, 1 second apart
# Fields: r (runnable), b (blocked), swpd (swap), wa (wait I/O)

# I/O performance
iostat -x 1 5              # extended stats per device
# Fields: %util (device utilization), %iowait (CPU wait for I/O)

# CPU utilization
sar -u 1 5                 # if sysstat installed

# Memory over time
sar -r 1 5
```

### Step 2: Sustained measurement

```bash
# Collect baseline for comparison later
nohup vmstat 10 >> /tmp/vmstat-baseline.log &
nohup iostat -x 10 >> /tmp/iostat-baseline.log &

# Let it run during normal operations (1 hour minimum)
# Then compare against issue period
```

### Step 3: Recording for playback

```bash
# If sysstat is installed, enable data collection
systemctl enable sysstat
systemctl start sysstat

# Historical data in /var/log/sysstat/
# Replay with: sar -f /var/log/sysstat/sa01
```

## Common Issue Patterns

| Symptom | Likely Cause | Check First | See Section |
|---------|-----------|-----------|------------|
| System slow, load high | CPU-intensive process | `top`, `ps aux --sort=-%cpu` | High CPU / Load |
| Swap thrashing | Out of memory | `free -h`, `vmstat` | Memory Pressure |
| "No space left" | Disk full | `df -h`, `du -sh /*` | Disk Space |
| Can't connect to service | Firewall, wrong port, service down | `ss -tlnp`, `curl localhost` | Network or Service Won't Start |
| SSH won't accept auth | Key permissions, agent | `ls -la ~/.ssh/`, SSH keys section (see linux-ops:ssh) | Network |
| Service fails on boot | Dependency, permission, config | `systemctl status`, `journalctl -u <svc>` | Service Won't Start |
| Zombie processes | Parent not reaping | `ps aux grep <defunct>`, `ps ppid` | Process Debugging |
| Box unresponsive | OOM killer active | `dmesg grep OOM`, `free` | Memory Pressure |

## Related Skills

- **linux-ops:systemd** — Service management details, timer units, socket activation
- **linux-ops:security** — Firewall (ufw), SELinux, AppArmor, permission troubleshooting
- **linux-ops:networking** — Deep network configuration, routing, interfaces
- **linux-ops:permissions** — File/directory permission debugging, user/group operations
- **linux-ops:storage** — Filesystem types, LVM, RAID, mount options
- **linux-ops:ssh** — SSH troubleshooting, key authentication, agent forwarding
- **linux-ops:packages** — APT/dpkg, package dependencies, repository issues

## References

Key files for offline reference:

- `/etc/systemd/system/` — local service definitions
- `/usr/lib/systemd/system/` — system service definitions
- `/proc/meminfo` — detailed memory state
- `/proc/cpuinfo` — CPU information
- `/etc/fstab` — mount configuration
- `/var/log/syslog` (or `/var/log/messages`) — system log

## Quick Commands Cheat Sheet

```bash
# System health snapshot
uptime && free -h && df -h && systemctl list-units --failed

# Top resource consumers
echo "=== CPU ===" && ps aux --sort=-%cpu | head -5
echo "=== Memory ===" && ps aux --sort=-%mem | head -5

# Journal triage (last 100 lines, errors and above)
journalctl -p err -n 100

# Service quick check
systemctl list-units --type=service --all

# Port availability
ss -tlnp

# Disk usage deep dive
du -sh /* | sort -h && du -sh /var/* | sort -h

# Network check
ip addr && ip route && ping 8.8.8.8
```
