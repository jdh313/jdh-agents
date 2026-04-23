---
name: permissions
description: Fix file/directory permissions, ownership, umask, ACLs, and troubleshoot permission denied errors on Debian/Ubuntu systems. Trigger on chmod/chown tasks, ACL setup, special bits, permission chains.
---

# Linux File Permissions & Access Control

Comprehensive guide for managing file permissions, ownership, and access control on Debian/Ubuntu systems.

## Standard Permissions

### Octal Notation
Three digits represent permissions for owner, group, others. Each digit is sum of: read (4) + write (2) + execute (1).

```bash
chmod 755 file     # rwx for owner, r-x for group/others
chmod 644 file     # rw- for owner, r-- for group/others
chmod 700 file     # rwx for owner, --- for group/others
chmod 600 file     # rw- for owner, --- for group/others
chmod 777 file     # rwx for all (avoid this in production)
```

### Symbolic Notation
Use `u` (owner), `g` (group), `o` (others), `a` (all). Operations: `+` (add), `-` (remove), `=` (set exactly).

```bash
chmod u+x file           # add execute for owner
chmod g-w file           # remove write for group
chmod o-rwx file         # remove all for others
chmod u=rwx,g=rx file    # set specific permissions
chmod a-rwx file         # remove all, then use +
```

### Common Permission Sets

| Octal | Symbolic | Use Case |
|-------|----------|----------|
| 644 | rw-r--r-- | Regular files (readable by all, writable by owner) |
| 755 | rwxr-xr-x | Executable files, scripts, directories (executable for all) |
| 600 | rw------- | Sensitive files (SSH keys, database creds) |
| 700 | rwx------ | Sensitive directories (private configs) |
| 640 | rw-r----- | Files readable by owner's group only |
| 750 | rwxr-x--- | Directories readable/executable by owner's group only |

## Ownership

### Changing Owner and Group
```bash
chown owner file              # change owner only
chown owner:group file        # change owner and group
chown :group file             # change group only
chown -R owner:group dir/     # recursive (careful with existing permissions)
chown --from=old:oldgrp new:newgrp file  # conditional change
```

### When to Use Each
- **`chown owner:group`** — Assign file to user and group
- **`chown :group`** — Change group, keep owner
- **`chown -R`** — Bulk change (verify first with `find`)
- **`--from=`** — Safety check before overwriting ownership

### Recursive Changes
Always verify scope before recursive operations:
```bash
find dir/ -type f -exec chown owner:group {} \;  # files only
find dir/ -type d -exec chmod 755 {} \;          # directories only
find dir/ -exec chown owner:group {} \;          # everything
```

## Special Permission Bits

Three additional bits: setuid (4), setgid (2), sticky (1). Prepend to octal chmod (e.g., `4755`).

### Setuid (Set User ID)
Executable runs as file owner, not executor.

```bash
chmod u+s file   # symbolic
chmod 4755 file  # octal (rwxr-sr-x)
```

**Use cases:** `passwd`, `sudo`, `ping` (needs root capability temporarily)  
**Security note:** Setuid binaries are privilege escalation risks. Audit carefully.

### Setgid (Set Group ID)
- On file: runs as group owner
- On directory: new files inherit directory's group (useful for shared team directories)

```bash
chmod g+s dir/   # symbolic
chmod 2755 dir/  # octal (rwxr-sr-x)
```

**Use cases:** Shared project directories, version control repos  
**Example:** `2770` (rwxrwx---) for read/write by owner and group, no others.

### Sticky Bit
Only owner (or root) can delete/rename files in directory, even if others have write access.

```bash
chmod o+t dir/   # symbolic
chmod 1777 dir/  # octal (rwxrwxrwt)
```

**Use cases:** `/tmp`, `/var/tmp` (world-writable but protected from deletion)  
**Without sticky bit on `/tmp`:** User A could delete User B's temporary files.

## umask

Default permissions for new files/directories. Subtracted from base permissions (666 for files, 777 for directories).

### System umask
Set in `/etc/profile`, `/etc/bash.bashrc`, or `/etc/login.defs`:

```bash
umask 0022        # creates files as 644, dirs as 755 (typical)
umask 0077        # creates files as 600, dirs as 700 (restrictive)
umask 0002        # creates files as 664, dirs as 775 (group-writable)
```

### User umask
Override in `~/.bashrc`, `~/.zshrc`, or `~/.profile`:

```bash
umask 0077        # private files
```

### Systemd Services
Set in service file `[Service]` section:

```ini
[Service]
UMask=0077
```

### Calculate Effective Permissions
```
Base 666 (files) - umask 0022 = 644 (rw-r--r--)
Base 777 (dirs)  - umask 0022 = 755 (rwxr-xr-x)
Base 666 (files) - umask 0077 = 600 (rw-------)
Base 777 (dirs)  - umask 0077 = 700 (rwx------)
```

## Access Control Lists (ACLs)

Grant fine-grained permissions beyond standard owner/group/others.

### Check Filesystem Support
```bash
mount | grep acl   # ext4, btrfs, xfs support ACLs
getfacl file       # test if ACLs are available
```

### Enable ACLs
For ext4:
```bash
mount -o remount,acl /mount/point
# or in /etc/fstab:
# /dev/sda1 /mount/point ext4 defaults,acl 0 0
```

### View ACLs
```bash
getfacl file       # show detailed ACL
getfacl -R dir/    # recursive
```

### Grant Permissions
```bash
setfacl -m u:username:rw file          # user read+write
setfacl -m g:groupname:rx file         # group read+execute
setfacl -m o::- file                   # remove other permissions
setfacl -x u:username file             # remove user ACL entry
setfacl -b file                        # remove all ACLs
```

### Default ACLs on Directories
New files inherit directory's default ACLs:

```bash
setfacl -d -m u:alice:rwx dir/         # alice gets rwx on new files in dir/
setfacl -d -m g:team:rx dir/           # team group gets r-x on new files
getfacl dir/ | grep default            # view default ACLs
```

### When to Use ACLs
- **Standard permissions insufficient:** Multiple users need different access levels
- **Shared directories:** Project directories with granular per-user/group control
- **Avoid chmod 777:** Use ACLs instead of world-writable directories
- **Better than groups:** When users belong to many groups or you want per-user rules

## Directory Permissions

### Execute Bit on Directories
Execute means "enter" the directory. Cannot list contents without read.

```
r (read)    — list directory contents
w (write)   — create/delete files in directory
x (execute) — enter directory
```

Examples:
```bash
chmod 755 dir/    # rwxr-xr-x: all can enter, owner can modify
chmod 750 dir/    # rwxr-x---: group can enter, others cannot
chmod 700 dir/    # rwx------: only owner can access
chmod 555 dir/    # r-xr-xr-x: all can enter/list, none can modify (archive)
```

### Shared Directories with setgid
Team directory where all members' files become group-owned:

```bash
mkdir /project
chown :team /project
chmod 2770 /project          # rwxrwx---, group ownership inherited
setfacl -d -m g:team:rwx /project  # default ACL for safety
```

New files created by any team member are group-owned, group-writable.

### Temporary Directories with Sticky Bit
```bash
chmod 1777 /tmp              # rwxrwxrwt: world-writable, deletion protected
ls -ld /tmp                  # shows 't' in last position (sticky bit)
```

## Troubleshooting

### Check Permission Chain
Use `namei` to trace full path permissions:

```bash
namei -l /path/to/file
# Output shows permissions for /, path, to, file separately
# Common issue: missing execute on parent directory
```

Example output:
```
f: /home/alice/projects/file.txt
 drwxr-xr-x root root /
 drwxr-xr-x root root home
 drwx------ alice alice alice
 -rw-r--r-- alice alice projects
 -rw-r--r-- alice alice file.txt
```

If any parent dir is missing `x` for the user, access fails.

### Detailed File Info
```bash
stat file                    # show permissions, owner, group, timestamps
stat -c "%a %U:%G %n" file   # compact format: octal perms, owner:group, name
```

### Common "Permission Denied" Causes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Cannot enter directory | Missing `x` on directory | `chmod u+x dir/` or `chmod o+x dir/` |
| Cannot read file in accessible dir | Missing `r` on file | `chmod +r file` |
| Cannot execute script | Missing `x` on file | `chmod +x script.sh` |
| Cannot write to file owned by group | Missing `w` for group | `chmod g+w file` or use ACL |
| Cannot access because of parent dir | Parent dir missing `x` | Add `x` to parent chain |
| SELinux/AppArmor blocking | Security policy | `getenforce` (SELinux) or `aa-status` (AppArmor) |

### Trace Access Denial
```bash
# SELinux (Fedora/RHEL)
getenforce                   # check mode (Enforcing/Permissive/Disabled)
ls -Z file                   # view SELinux context
audit log /var/log/audit/audit.log  # search for denials

# AppArmor (Ubuntu/Debian)
aa-status                    # check profiles
sudo journalctl -u apparmor  # view denials
dmesg | grep -i apparmor     # kernel log
```

## Common Mistakes

### `chmod -R 777` (Never in Production)
```bash
# Bad: makes everything world-readable and writable
chmod -R 777 dir/

# Better: separate files and directories
find dir/ -type f -exec chmod 644 {} \;
find dir/ -type d -exec chmod 755 {} \;
```

Why it's bad: Allows any user to delete, modify, or execute files meant to be private.

### Recursive chmod on Mixed Trees
Always separate file and directory permissions:

```bash
# Bad: applies same permission to files and dirs
chmod -R 755 dir/

# Good: use find to target type
find dir/ -type f -exec chmod 644 {} \;
find dir/ -type d -exec chmod 755 {} \;

# Or use -R with -type (bash only, not POSIX)
chmod -R u+rwX dir/  # X = execute only if already executable or is dir
```

### Forgetting Parent Directory Permissions
Even if a file has `r` permission, you can't access it if parent dir lacks `x`:

```bash
chmod 755 parent/
chmod 600 parent/file    # Correct: parent is executable
# vs
chmod 700 parent/
chmod 600 parent/file    # Wrong: parent not executable for group/others
```

### Over-using Recursive Ownership Changes
```bash
# Risky: changes ownership of everything, including setuid binaries
chown -R newowner:newgroup /usr/local/

# Better: verify first
find /usr/local -exec ls -ld {} \; | head
chown -R newowner:newgroup /usr/local/  # after confirming scope
```

### Incorrect ACL Syntax
```bash
# Wrong: missing colon separators
setfacl -m uusername:rwx file

# Correct: user:name:perms or group:name:perms
setfacl -m u:username:rwx file
setfacl -m g:groupname:rx file
```

## Quick Reference

```bash
# Standard operations
chmod 644 file              # rw-r--r--
chmod 755 file              # rwxr-xr-x
chown owner:group file      # set owner and group
chown -R owner:group dir/   # recursive

# Special bits
chmod u+s file              # setuid
chmod g+s dir/              # setgid on directory
chmod o+t dir/              # sticky bit

# ACLs
setfacl -m u:alice:rw file  # grant alice read+write
setfacl -d -m g:team:rx dir/  # default ACL for new files
getfacl file                # view ACL

# Troubleshooting
namei -l /path/to/file      # trace permission chain
stat file                   # detailed file info
find dir/ -type f -exec chmod 644 {} \;  # files only
```
