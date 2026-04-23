---
name: storage
description: Manage filesystems, partitions, mounts, disk health, and storage devices on Debian/Ubuntu. Covers fstab configuration, mount options, LVM, NFS, disk space analysis, RAID awareness, and swap management.
---

# Storage Management

## Overview

Manage filesystems, partitions, mounts, and storage devices on Debian/Ubuntu systems. This skill covers mounting filesystems, configuring fstab, creating and resizing partitions, checking disk health with SMART, managing logical volumes with LVM, mounting NFS shares, analyzing disk space, working with RAID, and optimizing swap.

**Trigger this skill when:** Mount or unmount filesystems, edit fstab, create/resize partitions, add NFS mounts, check disk health, use LVM, analyze storage usage, configure RAID, or adjust swap settings.

## Mount Fundamentals

### Common Mount Operations

```bash
mount                                    # Show all mounted filesystems
mount <device> <mount-point>             # Manually mount device
umount <mount-point>                     # Unmount filesystem
mount -a                                 # Mount all filesystems in fstab (test fstab before reboot)
findmnt                                  # Show mount tree with hierarchy
findmnt --verify                         # Verify fstab syntax (safer than mounting)
lsblk                                    # List block devices and mount points
df -h                                    # Show disk usage per mount point
```

### Manual Mount Example

```bash
mount -t ext4 /dev/sda1 /mnt/data
# or with options:
mount -t ext4 -o noatime,noexec /dev/sda1 /mnt/data
```

## fstab Configuration

The filesystem table (`/etc/fstab`) defines filesystems to mount at boot. Format:

```
<device>  <mount-point>  <type>  <options>  <dump>  <pass>
```

### Field Definitions

| Field | Purpose | Example |
|-------|---------|---------|
| device | Device path, UUID, or LABEL | `/dev/sda1`, `UUID=abc123`, `LABEL=backup` |
| mount-point | Where to mount | `/`, `/home`, `/mnt/data` |
| type | Filesystem type | `ext4`, `xfs`, `nfs`, `swap`, `tmpfs` |
| options | Mount options (comma-separated) | `defaults,noatime,errors=remount-ro` |
| dump | Backup priority (0=skip, 1=include) | `0` or `1` |
| pass | fsck order (0=skip, 1=root, 2+=others) | `0` for non-root, `1` for root |

### Device Identification

**UUID (Recommended — survives device renames):**

```bash
blkid /dev/sda1                  # Get UUID for a device
blkid                            # List all UUIDs
```

Example fstab entry:
```
UUID=12345678-1234-1234-1234-123456789abc  /mnt/data  ext4  defaults  0  2
```

**LABEL (User-friendly, must be unique):**

```bash
e2label /dev/sda1 MyData         # Set label on ext4
xfs_admin -L MyData /dev/sda1    # Set label on XFS
```

Example fstab entry:
```
LABEL=MyData  /mnt/data  ext4  defaults  0  2
```

**Device Path (/dev/sdX — not recommended, can change):**

```
/dev/sda1  /mnt/data  ext4  defaults  0  2
```

### fstab Best Practices

1. **Always use UUID or LABEL** — Survives device renames (e.g., /dev/sda becomes /dev/sdb).
2. **Test before rebooting** — Use `findmnt --verify` or `mount -a` to validate syntax.
3. **Use `noatime` for performance** — Reduces writes by skipping access-time updates.
4. **Set pass=0 for non-root** — Only root (/) should have pass=1; others are fsck'd in parallel.
5. **Add `nofail` for removable devices** — System won't fail to boot if device is absent.
6. **Use `errors=remount-ro` for data safety** — Remount read-only on filesystem errors instead of continuing.

### fstab Example

```
UUID=abc123...  /          ext4  defaults,errors=remount-ro  0  1
UUID=def456...  /boot      ext4  defaults,noatime             0  2
UUID=ghi789...  /home      ext4  defaults,noatime             0  2
UUID=jkl012...  /var       ext4  defaults,noatime             0  2
LABEL=backup    /mnt/backup ext4  defaults,noatime,nofail      0  2
10.13.20.10:/export/nfs   /mnt/nfs  nfs  hard,intr,vers=4.1  0  0
```

## Mount Options

### Common Options

| Option | Purpose |
|--------|---------|
| `defaults` | Use default mount options for the filesystem |
| `noatime` | Don't update access-time metadata (performance, wear reduction) |
| `relatime` | Update access-time only if it's older than modify-time (compromise) |
| `noexec` | Prevent binary execution (security for /tmp, /var/tmp) |
| `nosuid` | Ignore setuid/setgid bits (security for /tmp, /var/tmp) |
| `nodev` | Prevent device file interpretation (security for /tmp, /var/tmp) |
| `ro` | Read-only |
| `rw` | Read-write |
| `errors=remount-ro` | Remount read-only on filesystem errors (data safety) |
| `nofail` | Don't fail boot if device absent (removable media) |
| `auto` | Automatically mount at boot |
| `noauto` | Manually mount only (no auto-mount) |
| `async` | I/O operations are asynchronous (faster, less safe) |
| `sync` | I/O operations are synchronous (slower, safer) |

### Security-Focused Options for /tmp and /var/tmp

```
/dev/shm    /dev/shm        tmpfs  defaults,noexec,nosuid,nodev,mode=1777  0  0
UUID=abc... /tmp            ext4   defaults,noatime,noexec,nosuid,nodev     0  2
UUID=def... /var/tmp        ext4   defaults,noatime,noexec,nosuid,nodev     0  2
```

This prevents execution of files in /tmp, prevents setuid escalation, and disables device interpretation.

### NFS Mount Options

```bash
mount -t nfs -o hard,intr,vers=4.1 <server>:<path> <mount-point>
```

Common NFS options:

| Option | Purpose |
|--------|---------|
| `soft` | Timeout and return error (risky — incomplete I/O) |
| `hard` | Retry indefinitely (safe, default recommended) |
| `intr` | Allow interruption of hung mounts (Ctrl+C) |
| `timeo=30` | Timeout in tenths of seconds before retry (default 600 = 60s) |
| `retrans=3` | Number of retries before timeout |
| `vers=4.1` | NFS version (prefer 4.1 over older 3) |
| `noatime` | Skip access-time updates |
| `nofail` | Don't fail boot if NFS server unavailable |

Example fstab entry for NFS:

```
10.13.20.10:/export/nfs  /mnt/nfs  nfs  hard,intr,timeo=30,retrans=3,vers=4.1,noatime,nofail  0  0
```

## Filesystem Operations

### Creating Filesystems

**ext4 (general-purpose, supports journaling, good for boot):**

```bash
mkfs.ext4 -L MyData /dev/sda1      # Create with label
mkfs.ext4 -m 5 /dev/sda1           # Reserve 5% for root (default 5%)
mkfs.ext4 -F /dev/sda1             # Force creation (overwrite without prompting)
```

**xfs (high-performance, scales well, good for large storage):**

```bash
mkfs.xfs -L MyData /dev/sda1       # Create with label
mkfs.xfs -f /dev/sda1              # Force creation
```

**When to use each:**
- **ext4**: Boot drives, general-purpose storage, maximum compatibility.
- **xfs**: High-performance, large files, storage arrays, data warehouses.

### Resizing Filesystems

**ext4 (online resize, filesystem stays mounted):**

```bash
resize2fs /dev/sda1                # Resize to full partition
resize2fs /dev/sda1 50G            # Resize to specific size
```

**xfs (only grows, use `xfs_growfs`):**

```bash
xfs_growfs /mnt/data               # Grow to partition size (only if partition enlarged)
xfs_growfs -D 100G /mnt/data       # Grow to specific size (rarely needed)
```

**To shrink ext4 partition: must unmount and use `resize2fs` then `fdisk`/`parted` (complex; usually not worth it).**

### Checking Filesystems

**ext4:**

```bash
fsck.ext4 -n /dev/sda1             # Non-destructive check (no repairs)
fsck.ext4 -y /dev/sda1             # Check and repair automatically (unmount first!)
e2fsck -f /dev/sda1                # Force full check (more thorough)
```

**xfs:**

```bash
xfs_repair -n /dev/sda1            # Non-destructive check
xfs_repair /dev/sda1               # Repair (unmount first!)
```

**Important:** Always unmount before running fsck/repair (except read-only checks with `-n` flag).

## Disk Health & SMART Monitoring

Use smartmontools to monitor disk health with SMART (Self-Monitoring, Analysis and Reporting Technology).

### Installation and Setup

```bash
apt install smartmontools
systemctl enable smartd
systemctl start smartd
```

### SMART Commands

```bash
smartctl -i /dev/sda               # Get disk info
smartctl -H /dev/sda               # Quick health status
smartctl -a /dev/sda               # Full SMART report (most useful)
smartctl -t short /dev/sda         # Run short self-test (takes ~2 min)
smartctl -t long /dev/sda          # Run long self-test (takes hours, check with -a)
smartctl -A /dev/sda               # Show SMART attributes table
```

### Interpreting SMART Attributes

Key attributes to watch (from smartctl output):

| Attribute | Name | Concern |
|-----------|------|---------|
| 5 | Reallocated Sectors | Any non-zero = failing sectors, disk near end-of-life |
| 187 | Reported Uncorrectable Errors | Non-zero = unrecoverable read errors, data loss risk |
| 188 | Command Timeout | Non-zero = command timeouts, imminent failure |
| 197 | Current Pending Sector | Non-zero = sectors waiting to be remapped, precursor to 5 |
| 198 | Offline Uncorrectable | Non-zero = uncorrectable sectors found during offline tests |

Health status summary: **PASSED** (good), **WARNING** (watch carefully), **FAILED** (replace disk).

### Scheduling SMART Tests

Edit `/etc/smartmontools/smartd.conf`:

```
/dev/sda -a -o on -S on -m root@localhost -M exec /usr/libexec/smartmontools/smartdnotify -s (S/../.././22|L/../../1/02)
```

This runs short tests daily at 22:00 and long tests monthly on the 1st at 02:00, emailing root on errors.

### Monitoring Disks

```bash
tail -f /var/log/syslog | grep smartd   # Watch smartd logs
# or
journalctl -u smartd -f                  # Follow smartd systemd logs
```

## Partition Management

### List Block Devices

```bash
lsblk                               # List all drives and partitions (tree view)
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT  # Custom columns
fdisk -l /dev/sda                  # Show partition table for /dev/sda
parted -l                          # Show all partitions (parted style)
```

### GPT vs MBR

| Aspect | MBR | GPT |
|--------|-----|-----|
| Max disk size | 2 TB | 18 EB |
| Max partitions | 4 primary | 128+ |
| Boot | Legacy BIOS | UEFI (preferred) |
| When to use | Old systems, embedded | Modern systems (use GPT) |

### Creating Partitions

**Using `fdisk` (MBR — older, simpler):**

```bash
fdisk /dev/sda                     # Interactive menu
# Commands: n=new partition, d=delete, p=print, w=write, q=quit
```

**Using `parted` (GPT — modern, recommended):**

```bash
parted /dev/sda                    # Interactive mode
parted -a optimal /dev/sda mkpart primary ext4 1MiB 100%  # Create partition
parted /dev/sda resizepart 1 200GB                        # Resize partition 1 to 200GB
parted -l /dev/sda                 # Show partition table
```

**Using `gdisk` (GPT — interactive):**

```bash
gdisk /dev/sda                     # Similar to fdisk but for GPT
# Commands: n=new, d=delete, p=print, w=write, q=quit
```

### Partition Alignment

When creating partitions, align to 4KB boundaries for modern SSDs/HDDs:

```bash
parted -a optimal /dev/sda mkpart primary ext4 0% 100%  # Auto-aligns
# or manually:
parted /dev/sda mkpart primary ext4 1MiB 100GiB         # 1MiB start = aligned
```

Misaligned partitions cause 4x slower performance on SSDs.

## Logical Volume Management (LVM)

LVM (Logical Volume Manager) adds a layer of abstraction between physical disks and filesystems, enabling:
- **Resizing volumes without unmounting**
- **Snapshots for backup/testing**
- **Thin provisioning (oversubscription)**
- **Spanning volumes across multiple disks**

### LVM Concepts

**Physical Volume (PV):** Raw partition or disk — `/dev/sda1`, `/dev/sdb`

**Volume Group (VG):** Pool of PVs — `vg-data` (combines multiple PVs)

**Logical Volume (LV):** Virtual partition within a VG — `lv-home`, `lv-var`

Hierarchy: `PV` ← `VG` ← `LV` → mounted as `/mnt/data`

### When LVM is Worth the Complexity

- Need to resize volumes without downtime
- Have multiple disks and want to pool them
- Need snapshots for backups or testing
- Want thin provisioning

For simple single-disk setups with static partitioning, skip LVM.

### Creating LVM Volume

```bash
# 1. Create Physical Volumes
pvcreate /dev/sda1 /dev/sdb1

# 2. Create Volume Group
vgcreate vg-data /dev/sda1 /dev/sdb1

# 3. Create Logical Volumes
lvcreate -L 100G -n lv-home vg-data
lvcreate -L 50G -n lv-backup vg-data

# 4. Create filesystems
mkfs.ext4 /dev/vg-data/lv-home
mkfs.ext4 /dev/vg-data/lv-backup

# 5. Mount
mount /dev/vg-data/lv-home /home
mount /dev/vg-data/lv-backup /mnt/backup
```

Add to fstab:
```
/dev/vg-data/lv-home   /home           ext4  defaults  0  2
/dev/vg-data/lv-backup /mnt/backup     ext4  defaults  0  2
```

### Extending LVM Volumes

**Extend logical volume (no unmount needed):**

```bash
lvextend -L +50G /dev/vg-data/lv-home  # Add 50GB
# Then resize filesystem:
resize2fs /dev/vg-data/lv-home         # ext4
xfs_growfs /mnt/home                    # xfs (use mount point)
```

**Add disk to volume group:**

```bash
pvcreate /dev/sdc1
vgextend vg-data /dev/sdc1
```

### LVM Snapshots

Create point-in-time copy for backup or testing (doesn't copy data, just metadata):

```bash
lvcreate -L 20G -s -n lv-home-snap /dev/vg-data/lv-home
mount /dev/vg-data/lv-home-snap /mnt/snap-home
# Snapshot is now readable, takes space only for changes
rm -rf /mnt/snap-home/*  # Clean up
umount /mnt/snap-home
lvremove /dev/vg-data/lv-home-snap
```

### Viewing LVM Status

```bash
pvs                                      # List physical volumes
vgs                                      # List volume groups
lvs                                      # List logical volumes
lvdisplay                                # Detailed LV info
vgdisplay                                # Detailed VG info
```

## NFS Mounting

Mount remote NFS shares for network storage.

### Checking NFS Server Availability

```bash
showmount -e <nfs-server>               # List exported shares
# Example: showmount -e 10.13.20.10
rpcinfo -p <nfs-server>                 # Check RPC services (NFS, mountd, etc.)
```

### Mounting NFS

**Temporary mount:**

```bash
mount -t nfs 10.13.20.10:/export/nfs /mnt/nfs
# or with specific options:
mount -t nfs -o hard,intr,vers=4.1,timeo=30 10.13.20.10:/export/nfs /mnt/nfs
```

**Permanent mount (in fstab):**

```
10.13.20.10:/export/nfs  /mnt/nfs  nfs  hard,intr,vers=4.1,timeo=30,nofail  0  0
```

### On-Demand Mounting with autofs

automount mounts filesystems on-demand (useful for unstable networks or many shares):

```bash
apt install autofs
```

Edit `/etc/auto.master`:
```
/mnt/nfs  /etc/auto.nfs  --timeout=600
```

Create `/etc/auto.nfs`:
```
*  -fstype=nfs,hard,intr,vers=4.1  10.13.20.10:/export/&
```

This automatically mounts `/mnt/nfs/subdir` when accessed, unmounting after 10 minutes of inactivity.

### Troubleshooting NFS

```bash
mount | grep nfs                        # Check mounted NFS shares
ps aux | grep nfs                       # Check NFS daemons
rpcinfo -p                              # Check local RPC services
nfsstat                                 # NFS statistics
# If mount hangs:
umount -l /mnt/nfs                      # Lazy unmount (unmount when no longer busy)
```

## Disk Space Management

### Checking Disk Usage

```bash
df -h                                   # Disk usage per mount point
df -i                                   # Inode usage per filesystem
du -sh /path                            # Total size of directory
du -h /path | sort -h                   # Directory sizes, sorted
du -h /path --max-depth=1               # Top-level directory sizes only
```

### Interactive Disk Analyzer

```bash
apt install ncdu
ncdu /                                  # Browse filesystem, find large files
# Press '?' for help, 'q' to quit
```

### Finding Large Files

```bash
find / -type f -size +1G -exec ls -lh {} \; | head  # Files > 1GB
find / -type f -mtime -7 -size +100M                 # Files modified in last 7 days, >100MB
```

### Cleaning Up Space

**Package cache:**
```bash
apt clean                               # Remove all cached .deb files
apt autoclean                           # Remove only obsolete cached .deb files
apt autoremove                          # Remove unused dependencies
```

**Journal logs:**
```bash
journalctl --disk-usage                 # Current journal size
journalctl --vacuum-size=1G             # Keep max 1GB of journal
journalctl --vacuum-time=30d            # Keep max 30 days of journal
```

**Log files:**
```bash
find /var/log -type f -mtime +30 -delete  # Delete logs older than 30 days
# Be cautious with this!
```

## RAID Awareness

Software RAID (mdadm) is for on-the-cheap redundancy. Hardware RAID in the storage controller is more reliable.

### RAID Levels (Brief Overview)

| Level | Min Disks | Capacity | Fault Tolerance | Use Case |
|-------|-----------|----------|-----------------|----------|
| 0 | 2 | 100% | None (striping only) | Performance, non-critical |
| 1 | 2 | 50% | 1 disk | Boot drives, critical data |
| 5 | 3 | 66% | 1 disk | General storage, parity |
| 6 | 4 | 75% | 2 disks | Large arrays (safest) |
| 10 | 4 | 50% | 1 per pair | High performance + redundancy |

### Checking RAID Status

```bash
cat /proc/mdstat                        # RAID device status
mdadm --detail /dev/md0                 # Detailed status of /dev/md0
mdadm --detail --scan                   # All RAID arrays
```

### Common RAID Issues

**Degraded array (one disk failed, rebuild in progress):**

```bash
# Wait for rebuild (hours to days for large arrays)
watch -n 1 'cat /proc/mdstat'           # Monitor rebuild progress
# Once rebuild complete, replace failed disk
mdadm /dev/md0 --fail /dev/sdc1         # Mark failed
mdadm /dev/md0 --remove /dev/sdc1       # Remove from array
# (Replace physical disk, then add back)
mdadm /dev/md0 --add /dev/sdc1          # Re-add rebuilt disk
```

For production RAID: use hardware RAID + monitoring rather than mdadm.

## Swap Management

Swap is emergency virtual memory when RAM is exhausted. Avoid relying on swap; it's much slower than RAM.

### Creating a Swap File (Preferred)

**Create and enable:**

```bash
dd if=/dev/zero of=/swapfile bs=1G count=4  # Create 4GB swap file
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

**Add to fstab for persistence:**

```
/swapfile  none  swap  sw  0  0
```

**Or using `fallocate` (faster):**

```bash
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

### Swap Partition (Less Common)

```bash
mkswap /dev/sda2                        # Create swap partition
swapon /dev/sda2

# Add to fstab:
UUID=xyz...  none  swap  sw  0  0
```

### Swap Tuning

**swappiness (0-100, default 60):** How aggressively kernel uses swap.

```bash
sysctl vm.swappiness                    # Current value
sysctl -w vm.swappiness=10              # Set to 10 (prefer RAM)
# Persist by editing /etc/sysctl.conf:
# vm.swappiness = 10
```

Lower swappiness = prefer RAM (better for workstations), higher swappiness = use swap more (better for servers).

### Checking Swap

```bash
free -h                                 # RAM and swap usage
swapon --show                           # Active swap devices
swapoff /swapfile                       # Disable swap before removing
rm /swapfile                            # Remove
```

## Best Practices

1. **Always test fstab before reboot** — Use `findmnt --verify` or `mount -a`.
2. **Use UUID/LABEL, not /dev/sdX** — Device paths can change; UUIDs don't.
3. **Use `noatime` for performance** — Reduces unnecessary writes and improves speed.
4. **Keep `/tmp` and `/var/tmp` with noexec/nosuid/nodev** — Security hardening.
5. **Monitor disk health with smartctl** — Catch failing disks early.
6. **Regular backups before fsck** — Filesystem checks can rarely cause data loss.
7. **NFS: prefer hard,intr over soft** — soft=incomplete I/O on timeout; hard=reliable.
8. **LVM for flexibility, not complexity** — Use if you need resizing or snapshots; skip otherwise.
9. **Avoid relying on swap** — Add RAM instead if swap is constantly used.
10. **Check partition alignment** — Misaligned partitions cause 4x slower SSD performance.

## References

- `/etc/fstab` — Filesystem table
- `/etc/mtab` — Currently mounted filesystems
- `findmnt(8)` — Mount tree and verification
- `lsblk(8)` — Block device listing
- `smartctl(8)` — SMART monitoring
- `mount(8)` — Mount/unmount filesystems
- `fsck(8)` — Filesystem check and repair
- `lvm(8)` — Logical Volume Manager commands
- `nfs(5)` — NFS mount options
- `/var/log/syslog` — System logs (mount errors, smartd alerts)
