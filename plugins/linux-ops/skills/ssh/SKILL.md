---
name: ssh
description: Configure SSH key generation, server hardening, authentication, and troubleshooting for Debian/Ubuntu systems. Triggers on harden SSH, SSH keys, disable password auth, SSH config, SSH troubleshooting, or key rotation.
---

# SSH Hardening and Key Management

Configure SSH key generation, server hardening, authentication, and client configuration for Debian/Ubuntu systems. Covers practical workflows from initial key setup through production hardening and troubleshooting.

## Key Management

### Generate SSH Keys

**ED25519 (preferred)**
```bash
ssh-keygen -t ed25519 -C "user@host" -f ~/.ssh/id_ed25519 -N ""
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

**RSA 4096 (fallback for older systems)**
```bash
ssh-keygen -t rsa -b 4096 -C "user@host" -f ~/.ssh/id_rsa -N ""
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

Options:
- `-C` — comment (user@host for identification)
- `-f` — file path
- `-N ""` — empty passphrase (use `""` for interactive prompt instead)

### Deploy Public Keys

**ssh-copy-id (recommended)**
```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host
```

**Manual append to authorized_keys**
```bash
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### authorized_keys Format and Options

Each line is a key with optional prefix options:

```
ssh-ed25519 AAAAC3Nza... user@laptop
command="/usr/bin/rsync --server" ssh-ed25519 AAAAC3Nza... backup@server
from="192.168.1.10,10.0.0.5" ssh-ed25519 AAAAC3Nza... admin@office
no-port-forwarding,no-X11-forwarding,no-pty ssh-ed25519 AAAAC3Nza... ci@builder
```

Common prefix options:
- `command="..."` — Force execution of this command, ignore client command
- `from="ip/subnet"` — Restrict to source IP or CIDR block
- `no-port-forwarding` — Disable SSH port forwarding
- `no-X11-forwarding` — Disable X11 forwarding
- `no-pty` — No pseudo-terminal allocation (useful for automated tasks)
- `restrict` — Shorthand for disabling agent, port-forward, PTY, user-rc, X11

## Server Hardening

### Recommended sshd_config Settings

```bash
# Basic auth
PermitRootLogin no
PasswordAuthentication no
PermitEmptyPasswords no
PubkeyAuthentication yes

# Access control
AllowUsers user1 user2
AllowGroups ssh-users
MaxAuthTries 3
LoginGraceTime 30s
ClientAliveInterval 300
ClientAliveCountMax 2

# Network
Port 22
ListenAddress 0.0.0.0
ListenAddress ::

# Keys and algorithms (see "Key Algorithms" section)
HostKeyAlgorithms ssh-ed25519,rsa-sha2-512,rsa-sha2-256
KexAlgorithms curve25519-sha256,diffie-hellman-group16-sha512
Ciphers chacha20-poly1305@openssh.com,aes-256-gcm@openssh.com,aes-128-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com

# Features
PrintMotd no
X11Forwarding no
PermitUserEnvironment no
Compression no
TCPKeepAlive yes
```

### Drop-in Configuration

Use `/etc/ssh/sshd_config.d/` instead of editing `/etc/ssh/sshd_config` directly. The Include directive loads all files in lexicographic order.

**Create a drop-in file**
```bash
sudo tee /etc/ssh/sshd_config.d/99-hardening.conf > /dev/null <<EOF
PasswordAuthentication no
PermitRootLogin no
MaxAuthTries 3
ClientAliveInterval 300
EOF
```

**Test and reload**
```bash
sudo sshd -t  # Test syntax (required before reloading)
sudo systemctl reload ssh
```

Naming: Use numeric prefix (e.g., `50-`, `99-`) to control load order. Debian loads `/etc/ssh/sshd_config` first, then `/etc/ssh/sshd_config.d/*.conf`.

## Port and Listen Address

### Changing the Default Port

Limited security value (obscurity is not security), but useful to reduce bot noise:

```bash
# In sshd_config or drop-in
Port 2222
```

**Considerations:**
- Update firewall rules
- Document port in team wiki
- Still use strong authentication (keys, not passwords)
- Bots will find it eventually; not a substitute for hardening

### Binding to Specific Interfaces

Only listen on private networks if SSH should not be internet-facing:

```bash
# Listen only on 10.0.0.0/24 (private network)
ListenAddress 10.0.0.50

# Listen on multiple addresses
ListenAddress 0.0.0.0
ListenAddress ::
ListenAddress 192.168.1.50
```

## Key Algorithms

**Current best practice (as of 2025):** Check Mozilla SSH Guidelines (web search `mozilla ssh guidelines`) for latest recommendations. Algorithm selection changes as vulnerabilities emerge.

### Disable Weak Algorithms

```bash
# sshd_config — remove old/weak algorithms
HostKeyAlgorithms ssh-ed25519,rsa-sha2-512,rsa-sha2-256
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group16-sha512
Ciphers chacha20-poly1305@openssh.com,aes-256-gcm@openssh.com,aes-128-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com

# Do NOT use
# - DSA host keys (deprecated)
# - ECDSA (weaker than ed25519)
# - diffie-hellman-group1-sha1 (broken)
# - 3des, RC4, MD5
```

### View Supported Algorithms

```bash
ssh -Q kex        # Key exchange
ssh -Q key        # Host key types
ssh -Q cipher     # Ciphers
ssh -Q mac        # MACs
```

## Client Configuration

### ~/.ssh/config Patterns

```bash
# Basic host
Host prod-server
    HostName 192.168.1.100
    User admin
    IdentityFile ~/.ssh/id_ed25519
    Port 2222

# Jump host (bastion)
Host internal-db
    HostName 10.0.0.50
    User dbuser
    ProxyJump prod-server
    IdentityFile ~/.ssh/id_rsa

# Wildcard with fallback
Host *.internal
    User admin
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking accept-new
    UserKnownHostsFile ~/.ssh/known_hosts

Host *
    AddKeysToAgent yes
    IdentitiesOnly yes
    ServerAliveInterval 60
```

### Connection Multiplexing

Reuse SSH connections to reduce latency:

```bash
# In ~/.ssh/config
Host *
    ControlMaster auto
    ControlPath ~/.ssh/control-%h-%p-%r
    ControlPersist 600
```

This creates a socket file that subsequent connections reuse. Useful for nested tunneling and repeated file transfers.

## Host Keys

### Regenerate After VM Clone

Cloned VMs share host keys. Regenerate to avoid key conflicts:

```bash
sudo ssh-keygen -A  # Generate all default key types
sudo systemctl restart ssh
```

**Verify keys changed:**
```bash
ssh-keyscan localhost | head -1  # New fingerprint
```

### Managing known_hosts

```bash
# Remove old entry
ssh-keygen -R hostname

# View current keys
ssh-keyscan hostname

# Trust new fingerprint interactively
ssh -o StrictHostKeyChecking=accept-new user@newhost
```

### Host Key Rotation

Regular rotation is optional but recommended for long-lived servers:

```bash
# Check current keys
sudo ls -la /etc/ssh/ssh_host_*
sudo ssh-keygen -l -f /etc/ssh/ssh_host_ed25519_key

# Regenerate all (service goes down briefly)
sudo ssh-keygen -A
sudo systemctl restart ssh
```

Update team SSH configs to accept the new fingerprint.

## Troubleshooting

### Verbose Debugging

```bash
# Client-side verbose output
ssh -vvv user@host

# Server-side (in another terminal)
sudo sshd -D -d -p 2222  # Run in foreground on alternate port
```

### Check Server Logs

```bash
# Auth attempts and failures
sudo tail -f /var/log/auth.log

# Systemd logs
sudo journalctl -u ssh -n 50 -f
```

### Common Issues

**Permission Denied (publickey)**
- Check `~/.ssh` is `700`
- Check `~/.ssh/authorized_keys` is `600`
- Check `~/.ssh/id_*` is `600`
- Run `ssh -vvv` to see which key is offered
- Verify key in `authorized_keys` matches `id_*.pub`

**Too Many Authentication Failures**
- `MaxAuthTries` exceeded; wait or increase temporarily
- Check if wrong keys are being offered (use `-i` to specify key file)
- Clear SSH agent with `ssh-add -D` if testing multiple keys

**Connection Refused / No Route to Host**
- Check firewall: `sudo ufw status` or `sudo iptables -L -n`
- Check `ListenAddress` in sshd_config matches client target
- Verify SSH is running: `sudo systemctl status ssh`

**Cannot SSH After Editing sshd_config**
- Always test before applying: `sudo sshd -t`
- Keep existing SSH session open while reloading
- If locked out, use Proxmox/IPMI console or physical access to revert

**Timeout on Connect**
- Check `ClientAliveInterval` and `LoginGraceTime` (too short?)
- Check MTU issues: `ping -M do -s 1472 host` (test path MTU)
- Review firewall rules for rate limiting

### AppArmor / SELinux Issues

If present, SSH may be confined:

```bash
# Check status
sudo aa-status | grep sshd  # AppArmor
getenforce  # SELinux

# Logs
sudo tail -f /var/log/audit/audit.log  # SELinux denials
```

Most stock Debian/Ubuntu installs use AppArmor with permissive SSH policy. Only adjust if needed.

## Two-Factor Authentication (2FA)

SSH 2FA via PAM (TOTP, U2F) is possible but complex. Setup changes with OpenSSH and libpam versions.

**Recommendation:** Search "SSH 2FA Debian 24.04" or equivalent for current instructions. Common approaches:
- `libpam-google-authenticator` — TOTP
- `libpam-u2f` — YubiKey / FIDO2
- `sshpass` or `keyboard-interactive` — fallback prompts

Ensure password auth is disabled in sshd_config (or use 2FA *with* pubkey auth, not as replacement).
