---
name: security
description: Configure firewall (UFW), fail2ban, sysctl kernel parameters, audit framework, AppArmor, file integrity monitoring, kernel hardening, login security, least privilege, and security scanning for Debian/Ubuntu systems. Trigger when hardening servers, configuring firewalls, setting up fail2ban, applying sysctl security, auditing systems, enforcing UFW rules, or scanning for compliance gaps.
---

# Linux Security Hardening

Configure system-level security controls for Debian/Ubuntu. SSH hardening is covered by `linux-ops:ssh`; user/sudo management by `linux-ops:users`.

## UFW (Uncomplicated Firewall)

Enable and configure the firewall with sensible defaults.

```bash
# Enable UFW
sudo ufw enable

# Set default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow specific services or ports
sudo ufw allow ssh                    # Service profile
sudo ufw allow 22/tcp                 # Port with protocol
sudo ufw allow from 10.0.0.0/8        # Subnet
sudo ufw allow from 10.0.0.5 to any port 3306  # Source-specific

# Rate limiting (fail after 6 attempts in 30 seconds)
sudo ufw limit ssh/tcp

# Delete rules
sudo ufw delete allow ssh
sudo ufw delete allow 80/tcp

# Check status and logging
sudo ufw status verbose
sudo ufw logging on
sudo ufw logging high                 # low, medium, high

# View logs
sudo tail -f /var/log/ufw.log

# Application profiles (per-service UFW rules)
sudo ufw app list
sudo ufw allow 'OpenSSH'              # Uses app profile if available
```

**Key concepts:**
- Default policies: deny-in / allow-out (principle of least privilege)
- Use `limit` for rate limiting on attack-prone services (SSH, FTP)
- Application profiles in `/etc/ufw/applications.d/`
- Rules persist across reboots when enabled

## fail2ban

Detect and block brute-force attacks by monitoring logs for failed authentication attempts.

```bash
# Install
sudo apt install fail2ban

# Core config (do not edit directly)
cat /etc/fail2ban/jail.conf

# Create local overrides
sudo nano /etc/fail2ban/jail.local

# Essential jail.local settings
[DEFAULT]
bantime = 3600                 # Ban duration (seconds), -1 = permanent
findtime = 600                 # Window to count failures (seconds)
maxretry = 5                   # Failures before banning

# Enable standard jails
[sshd]
enabled = true

[sshd-ddos]
enabled = true

[recidive]
enabled = true                 # Ban repeat offenders longer
bantime = 86400

# Check jails
sudo fail2ban-client status
sudo fail2ban-client status sshd      # Jail-specific status

# Manually ban/unban IPs
sudo fail2ban-client set sshd banip 192.168.1.100
sudo fail2ban-client set sshd unbanip 192.168.1.100

# Whitelist IPs (never ban)
# In jail.local, add to [DEFAULT] or jail-specific:
ignoreip = 127.0.0.1/8 ::1 10.0.0.0/8 YOUR_IP

# View ban history
sudo grep "Ban " /var/log/fail2ban.log | tail -20

# Restart after changes
sudo systemctl restart fail2ban
```

**Custom filters:** Create `/etc/fail2ban/filter.d/custom.conf`:
```ini
[Definition]
failregex = ^<HOST> \[.+\] "POST /login" .* 401
ignoreregex =
```

Reference in `jail.local`:
```ini
[custom-app]
enabled = true
port = http,https
logpath = /var/log/app.log
filter = custom
```

## sysctl Kernel Parameter Hardening

Harden kernel behavior via `/etc/sysctl.d/` drop-in files.

```bash
# Create drop-in file (prefer this over editing /etc/sysctl.conf)
sudo nano /etc/sysctl.d/99-hardening.conf

# Add hardening parameters:

# IP Forwarding — disable unless router/VPN
net.ipv4.ip_forward = 0
net.ipv6.conf.all.forwarding = 0

# SYN flood protection
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 2

# ICMP redirects — disable (redirect attack vector)
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv6.conf.all.accept_redirects = 0

# Source routing — disable (IP spoofing vector)
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# Reverse path filtering (drop packets from unexpected interfaces)
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Ignore ICMP ping — optional
net.ipv4.icmp_echo_ignore_all = 0    # 1 to ignore

# Core dumps — disable unless debugging
kernel.core_uses_pid = 1
fs.suid_dumpable = 0

# Restrict dmesg access (kernel messages)
kernel.dmesg_restrict = 1

# Restrict kernel pointer exposure (ASLR support)
kernel.kptr_restrict = 2              # 1 = restricted, 2 = restricted for non-root

# Unprivileged BPF — restrict
kernel.unprivileged_bpf_disabled = 1
kernel.unprivileged_userns_clone = 0  # Restrict namespaces

# Restrict ptrace (process tracing)
kernel.yama.ptrace_scope = 2          # 1 = same UID, 2 = CAP_SYS_PTRACE only

# Apply changes immediately
sudo sysctl -p /etc/sysctl.d/99-hardening.conf

# Verify applied
sudo sysctl net.ipv4.tcp_syncookies
sudo sysctl kernel.dmesg_restrict
```

## Audit Framework (auditd)

Monitor system calls and file access for security auditing and compliance.

```bash
# Install
sudo apt install auditd

# Core config
sudo nano /etc/audit/rules.d/audit.rules

# Example audit rules:

# Monitor sudo usage
-a always,exit -F path=/etc/sudoers -F perm=wa -F auid>=1000 -F auid!=-1 -k sudoers_changes

# Monitor privileged command execution
-a always,exit -F path=/usr/bin/passwd -F auid>=1000 -F auid!=-1 -k passwd_changes

# Monitor user/group changes
-a always,exit -F path=/etc/group -F perm=wa -F auid>=1000 -F auid!=-1 -k group_changes
-a always,exit -F path=/etc/passwd -F perm=wa -F auid>=1000 -F auid!=-1 -k passwd_changes
-a always,exit -F path=/etc/shadow -F perm=wa -F auid>=1000 -F auid!=-1 -k shadow_changes

# Monitor system calls (login, execve)
-a always,exit -F arch=b64 -S adjtimex -S settimeofday -k time_change
-a always,exit -F arch=b32 -S adjtimex -S settimeofday -S stime -k time_change

# Monitor file deletions
-a always,exit -F arch=b64 -S unlink,unlinkat,rename,renameat -F auid>=1000 -F auid!=-1 -k delete

# Reload rules
sudo systemctl restart auditd

# Search audit logs for specific events
sudo ausearch -k sudoers_changes
sudo ausearch -ts recent -m EXECVE | head -30

# Generate audit report
sudo aureport --summary
sudo aureport -x                     # Executable summary
```

## AppArmor

Use mandatory access control to restrict application capabilities.

```bash
# Check AppArmor status
sudo aa-status
sudo aa-status | grep -E "profiles in|processes have profiles"

# Profile modes:
#   enforce — denials are blocked and logged
#   complain — denials are logged but allowed

# Put profile in complain mode (for debugging)
sudo aa-complain /etc/apparmor.d/usr.bin.man

# Put profile in enforce mode
sudo aa-enforce /etc/apparmor.d/usr.bin.man

# Reload all profiles
sudo systemctl reload apparmor

# View denials in syslog
sudo grep -i apparmor /var/log/syslog | grep DENIED

# Check profile syntax
sudo apparmor_parser -T -d /etc/apparmor.d/usr.bin.man

# Common profiles
sudo aa-status | grep enabled
```

**Note:** AppArmor profile authoring is complex. For application-specific hardening, search the web for "apparmor [application-name] profile" or consult application documentation.

## File Integrity Monitoring

Detect unauthorized changes to critical files.

```bash
# Install AIDE (Advanced Intrusion Detection Environment)
sudo apt install aide aide-common

# Initialize database (may take a few minutes)
sudo aideinit

# Check for changes
sudo aide --check
sudo aide --check | grep "changed" | head -20

# Update database after authorized changes
sudo aide --update
sudo mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz

# Schedule daily check via cron
echo "0 3 * * * /usr/bin/aide --check" | sudo tee /etc/cron.d/aide

# Verify package file integrity (package-level, not file-level)
sudo apt install debsums
sudo debsums -c                      # Check installed packages

# Tripwire (alternative, more complex)
sudo apt install tripwire
```

## Kernel Hardening

Enable kernel-level memory protection and restrict privileged operations.

```bash
# ASLR (Address Space Layout Randomization) — should be enabled by default
cat /proc/sys/kernel/randomize_va_space
# 0 = disabled, 1 = basic, 2 = full

# Verify via sysctl (set in sysctl.d earlier):
sudo sysctl kernel.randomize_va_space
kernel.randomize_va_space = 2

# Stack protector (compile-time hardening, check with hardening-check)
sudo apt install hardening-includes
hardening-check /bin/ls

# Restrict kernel logging (dmesg_restrict) — set in sysctl.d
sudo sysctl kernel.dmesg_restrict

# Restrict kernel pointer leaks (kptr_restrict) — set in sysctl.d
sudo sysctl kernel.kptr_restrict

# Disable unprivileged BPF and namespaces — set in sysctl.d
sudo sysctl kernel.unprivileged_bpf_disabled
sudo sysctl kernel.unprivileged_userns_clone

# Check current hardening state
sudo cat /proc/cmdline               # Boot parameters
```

## Login Security

Enforce strong password policies and account lockout.

```bash
# Install PAM quality enforcement
sudo apt install libpam-pwquality

# Configure password quality policy
sudo nano /etc/security/pwquality.conf

# Example settings:
minlen = 14              # Minimum length
dcredit = -1             # Require digits
ucredit = -1             # Require uppercase
lcredit = -1             # Require lowercase
ocredit = -1             # Require special characters
maxrepeat = 3            # Max repeated chars
usercheck = 1            # Check against username
enforce_for_root = 1     # Apply to root

# Apply to sudo password prompts
sudo grep pam_pwquality /etc/pam.d/sudo
# Should show: password requisite pam_pwquality.so retry=3

# Account lockout (pam_faillock)
sudo nano /etc/pam.d/common-password

# Add for login/sudo:
auth required pam_faillock.so preauth silent audit deny=5 unlock_time=900

# Check locked accounts
sudo faillock --user username
sudo faillock --user username --reset  # Unlock

# Login banners
sudo nano /etc/issue                # MOTD before login
sudo nano /etc/motd                 # MOTD after login
# Note: Legal/informational only, not effective deterrent
```

## Principle of Least Privilege

Run services with minimal required permissions.

```bash
# Check service users/groups
sudo ps aux | grep -E "^\w+\s" | grep -v root | head -10

# Verify services run as dedicated users
ps aux | grep nginx     # Should be www-data, not root
ps aux | grep postgres  # Should be postgres, not root

# Use capabilities instead of setuid
# Example: Allow `ping` without root
sudo setcap cap_net_raw=ep /bin/ping
sudo getcap /bin/ping   # Verify

# Remove unnecessary setuid bits
sudo find / -perm /4000 2>/dev/null | head -20

# systemd hardening in service units
# Restrict filesystem access:
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/service

# Drop capabilities:
CapabilityBoundingSet=CAP_NET_BIND_SERVICE CAP_SETUID
AmbientCapabilities=CAP_NET_BIND_SERVICE

# Example service hardening:
sudo systemctl cat nginx | grep -E "Protect|Capability"
```

## Security Scanning

Audit system configuration against security benchmarks.

```bash
# Install Lynis (system auditing tool)
sudo apt install lynis

# Run full audit
sudo lynis audit system

# View detailed results
sudo lynis audit system > /tmp/lynis_report.txt
grep -i "warning\|suggestion" /tmp/lynis_report.txt

# Run specific checks
sudo lynis audit system --quick    # Quick scan
sudo lynis show categories         # See all audit categories
sudo lynis audit system --tests KRNL  # Kernel tests only

# CIS Benchmarks (reference standards)
# - CIS Debian Linux 12 Benchmark
# - CIS Ubuntu Linux 22.04 LTS Benchmark
# Download from https://www.cisecurity.org/cis-benchmarks
# Use Lynis + manual review to measure compliance

# Automated CIS scanning tools (web search for current versions):
# - CIS-CAT Lite (free tier)
# - OpenSCAP (SCAP compliance)
# - Aide + custom scripts

# Quick security posture check
sudo systemctl status ufw           # Firewall enabled?
sudo systemctl status fail2ban      # Fail2ban running?
sudo sysctl -a | grep hardening    # Sysctl parameters?
sudo aa-status | head -5            # AppArmor profiles?
```

## Workflow: System Hardening Checklist

1. **Enable firewall** — `ufw enable` + default policies + allow necessary services
2. **Enable fail2ban** — protect SSH and other services from brute force
3. **Harden sysctl** — apply kernel parameter hardening via `/etc/sysctl.d/99-hardening.conf`
4. **Enable auditing** — configure auditd for sensitive operations (sudoers, system calls, user/group changes)
5. **Configure AppArmor** — enable profiles for high-risk services (nginx, postgresql, etc.)
6. **File integrity** — set up AIDE for critical file monitoring
7. **Login security** — enforce password policies and account lockout
8. **Audit compliance** — run Lynis to identify remaining gaps

## References

- UFW: `man ufw`, `/etc/ufw/` configurations
- fail2ban: `man fail2ban-client`, `/etc/fail2ban/jail.conf`
- sysctl: `man 8 sysctl`, `/etc/sysctl.d/`
- auditd: `/etc/audit/rules.d/`, `ausearch`, `aureport`
- AppArmor: `aa-status`, `/etc/apparmor.d/`
- AIDE: `man aide`, `/etc/aide/aide.conf`
- Lynis: https://cisofy.com/lynis/ (check for latest versions)
