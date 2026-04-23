---
name: users
description: "Trigger when: creating users or service accounts, managing group membership, configuring sudo access, changing shell/home, removing users, or debugging PAM/access issues on Debian/Ubuntu systems."
---

# User and Group Management

Guide for managing Linux users, groups, and access control on Debian/Ubuntu systems. See `../../../shared-references/debian-conventions.md` for UID/GID ranges, default groups, sudoers conventions, and PAM paths.

## Regular User Creation

Use `adduser` (interactive, Debian-recommended) rather than `useradd` (low-level, requires flag knowledge).

**Command:**
```bash
adduser <username>
```

**What it does:**
- Creates home directory at `/home/<username>`
- Sets default shell to `/bin/bash`
- Creates matching group `<username>` (GID in range 1000–59999)
- Prompts for password, full name, phone, room number (accept defaults by pressing Enter)
- Adds user to default groups: typically `users`, optionally `adm` if admin account

**Flags:**
- `--gecos "<full name>"` — Pre-fill full name (skip prompt)
- `--disabled-password` — Create account but disable password login (use for accounts with only SSH keys)
- `--shell /bin/bash` — Explicit shell choice (rarely needed, bash is default)

**Verify:**
```bash
id <username>
# Shows UID, GID, group membership
```

## Service Accounts

Service accounts run daemons and should NOT have interactive login capability.

**Command:**
```bash
adduser --system --no-create-home --shell /usr/sbin/nologin <service-name>
```

**Flags explained:**
- `--system` — Allocates UID in system range (100–999), not user range
- `--no-create-home` — Skip home directory creation (services don't need `/home` entry)
- `--shell /usr/sbin/nologin` — Prevents login attempts (login returns "This account is currently not available")
- `--group` — Automatically creates dedicated group (recommended but optional; happens automatically in most Debian versions)

**Why nologin matters:**
- Prevents `ssh <service-name>@host` from working
- Fails gracefully instead of spawning a restricted shell
- More explicit audit trail if someone attempts login

**Example:**
```bash
adduser --system --no-create-home --shell /usr/sbin/nologin redis-server
# Creates user redis-server:100, group redis-server:100
```

## Group Management

**Create standalone group (not tied to user):**
```bash
addgroup --gid <GID> <groupname>
# Use GID in system range (100–999) for service groups
```

**Add user to existing group:**
```bash
usermod -aG <groupname> <username>
# -a = append (keep other groups), -G = supplementary groups
```

**CRITICAL: Always use `-aG`, never just `-G`**
- `-G` alone REPLACES all groups (destructive — user loses sudoers, docker, etc.)
- `-aG` APPENDS the new group while keeping existing membership

**Remove user from group:**
```bash
delgroup <username> <groupname>
# Or: gpasswd -d <username> <groupname>
```

**List group members:**
```bash
getent group <groupname>
# Output: groupname:x:GID:member1,member2,...
```

**View user's groups:**
```bash
groups <username>
id <username>  # More detailed
```

**Naming conventions:**
- Service-specific groups: lowercase, hyphenated (e.g., `nginx-cache`, `postgres-backup`)
- Access control groups: descriptive (e.g., `docker`, `adm`, `sudo`)
- Avoid reserved system groups (0–99 GID range)

## Sudo Configuration

Never edit `/etc/sudoers` directly — syntax errors lock out all sudo access.

**Drop-in file pattern (recommended):**
```bash
visudo -f /etc/sudoers.d/<role>
# Validates before save, prevents locked-out state
```

**Example rule — per-user unrestricted sudo:**
```
alice ALL=(ALL:ALL) ALL
# alice can run any command as any user:group on any host
```

**Example rule — group-based sudo (preferred):**
```
%sudo ALL=(ALL:ALL) ALL
# Members of 'sudo' group can sudo
# This is the default on Debian/Ubuntu
```

**Example rule — specific commands without password:**
```
%docker-admins ALL=(ALL) NOPASSWD: /usr/bin/dockerd
# Members of docker-admins can run /usr/bin/dockerd with no password prompt
```

**NOPASSWD gotchas:**
- Use sparingly — trades authentication for convenience
- Applies per-command, not per-user (be explicit about which commands)
- Audit who is in the group granting NOPASSWD access

**Validation before deploying:**
```bash
visudo -cf /etc/sudoers.d/<file>
# Checks syntax without modifying
```

**Filename rules:**
- Must NOT contain `.` or `~` (these are ignored by sudoers parser)
- Use lowercase, underscores OK (e.g., `docker_admins`, `backup_user`)
- No extension

**Example file structure:**
```
# /etc/sudoers.d/docker_group
%docker ALL=(ALL:ALL) NOPASSWD: /usr/bin/docker

# /etc/sudoers.d/postgres_backup
postgres-backup ALL=(postgres) NOPASSWD: /usr/bin/pg_dump, /usr/bin/psql
```

## User Removal

**Soft delete (preserve home directory and files):**
```bash
deluser <username>
# Removes user from /etc/passwd, keeps /home/<username>
```

**Hard delete (remove home directory and mail):**
```bash
deluser --remove-home <username>
# Removes user and /home/<username>/
```

**Remove associated group:**
```bash
delgroup <username>
# Typically safe if group has same name as user (created by adduser)
```

**Clean up sudo references:**
```bash
grep <username> /etc/sudoers.d/*
# Check for lingering sudoers rules
# Remove stale files manually if found
```

**Verify removal:**
```bash
id <username>  # Should error: "no such user"
ls -la /home/ | grep <username>  # Should be gone or orphaned
```

## PAM Basics

PAM (Pluggable Authentication Modules) handles password policy, access control, and account validation.

**When PAM matters:**
- Password complexity requirements (`pam_pwquality.so`)
- Login attempt rate limiting
- Account lockout after failed attempts
- Two-factor authentication integration
- Access time restrictions (e.g., "user can only login 9–5 Mon–Fri")

**Key config locations:**
- `/etc/pam.d/common-password` — Password strength, expiration
- `/etc/pam.d/common-auth` — Login authentication
- `/etc/pam.d/common-account` — Account validity (expiration, lockout)
- `/etc/pam.d/common-session` — Session setup (e.g., temp directory cleanup)
- `/etc/security/limits.conf` — Resource limits (max processes, memory)

**Default Debian setup:**
- Passwords validated by `pam_unix.so` (standard UNIX hashing)
- Password quality checked by `pam_pwquality.so` (if installed)
- Account lockout NOT configured by default (no login attempt limit)

**Check PAM configuration for a service:**
```bash
cat /etc/pam.d/sshd
# Shows which PAM modules are loaded for SSH
```

**Modify password strength:**
Edit `/etc/security/pwquality.conf`:
```
minlen=12        # Minimum length
dcredit=-1       # Require at least 1 digit
ucredit=-1       # Require at least 1 uppercase
lcredit=-1       # Require at least 1 lowercase
ocredit=-1       # Require at least 1 special char
```

## Common Mistakes to Avoid

**Mistake 1: Using `useradd` without `-m`**
```bash
# WRONG — no home directory created
useradd alice
# Correct:
useradd -m alice
# Better: use adduser instead (handles defaults)
adduser alice
```

**Mistake 2: Forgetting `-aG` when adding groups**
```bash
# WRONG — drops all existing groups, user loses sudo access
usermod -G docker alice
# Correct:
usermod -aG docker alice
```

**Mistake 3: Editing `/etc/sudoers` directly**
```bash
# WRONG — syntax error = locked out
nano /etc/sudoers
# Correct:
visudo  # or: visudo -f /etc/sudoers.d/role
```

**Mistake 4: Allowing login on service accounts**
```bash
# WRONG — service account has /bin/bash shell, can be exploited
adduser --system myservice  # Defaults to /bin/sh
# Correct:
adduser --system --shell /usr/sbin/nologin myservice
```

**Mistake 5: Running services as root**
```bash
# WRONG — service compromise = full system compromise
sudo /usr/bin/redis-server
# Correct: Create dedicated service user, configure service to run as that user
adduser --system --no-create-home --shell /usr/sbin/nologin redis
# Then in service config: User=redis
```

**Mistake 6: Using NOPASSWD for all commands**
```bash
# WRONG — anyone in group can do anything with no auth
%admins ALL=(ALL) NOPASSWD: ALL
# Correct: Restrict to specific commands
%admins ALL=(ALL) NOPASSWD: /usr/bin/systemctl
```

**Mistake 7: Forgetting to validate sudoers syntax**
```bash
# WRONG — deploy broken rule, breaks sudo
echo "%newgroup ALL=(ALL) ALL" > /etc/sudoers.d/newgroup
# Correct:
echo "%newgroup ALL=(ALL) ALL" | sudo tee /etc/sudoers.d/newgroup
sudo visudo -cf /etc/sudoers.d/newgroup  # Validate before relying on it
```

## UID/GID Ranges Reference

See `../../../shared-references/debian-conventions.md` for complete table:

| Range | Purpose |
|-------|---------|
| 0 | root |
| 1–99 | Static system accounts (pre-allocated) |
| 100–999 | Dynamic system accounts (`adduser --system`) |
| 1000–59999 | Regular users (`adduser`) |
| 65534 | nobody/nogroup |

## Default Groups Reference

From `../../../shared-references/debian-conventions.md`:

| Group | GID | Purpose |
|-------|-----|---------|
| `sudo` | 27 | Sudo access |
| `adm` | 4 | Read `/var/log` files |
| `www-data` | 33 | Web server processes |
| `docker` | — | Docker daemon socket access |
| `systemd-journal` | — | systemd journal access |
| `ssl-cert` | — | Read `/etc/ssl/private` |

## Workflows

**Scenario: Create regular user with sudo access**
```bash
adduser alice
usermod -aG sudo alice
# alice can now use sudo (sudo group is already configured in sudoers)
```

**Scenario: Create service account for custom app**
```bash
adduser --system --no-create-home --shell /usr/sbin/nologin myapp
adduser --system --no-create-home --shell /usr/sbin/nologin myapp-worker
usermod -aG myapp myapp-worker  # worker is member of myapp group
# Create shared directory:
sudo mkdir -p /opt/myapp/data
sudo chown myapp:myapp /opt/myapp/data
sudo chmod 755 /opt/myapp/data
```

**Scenario: Grant specific user backup command without password**
```bash
visudo -f /etc/sudoers.d/backup_user
# Add: backup-user ALL=(root) NOPASSWD: /usr/bin/mysqldump
visudo -cf /etc/sudoers.d/backup_user  # Validate
```

**Scenario: Offboard user**
```bash
# Preserve files, remove login:
deluser alice
# Or hard delete:
deluser --remove-home alice
# Check for leftover sudoers rules:
grep -r alice /etc/sudoers.d/ && rm /etc/sudoers.d/*alice*
# Check cron:
crontab -u alice -l 2>/dev/null && crontab -u alice -r
```

---

## Links

- Debian admin handbook: https://debian-handbook.info/
- `adduser` man page: `man adduser`
- `visudo` man page: `man visudo`
- PAM documentation: `/usr/share/doc/libpam-doc/` (if installed)
