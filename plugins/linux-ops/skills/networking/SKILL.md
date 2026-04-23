---
name: networking
description: Configure static IPs, DNS resolution, netplan, systemd-networkd, routes, bridges, VLANs, hostname setup, and diagnose connectivity issues on Debian/Ubuntu systems.
---

# Networking

## Overview

This skill covers network configuration and troubleshooting for Debian/Ubuntu systems. Ubuntu uses **Netplan** (YAML abstraction over systemd-networkd) as the default. Debian 12+ also defaults to netplan. Configuring static IPs, DNS, routes, bridges, and bonds typically goes through Netplan. Diagnostic commands and systemd-resolved configuration are also covered.

Refer to `debian-conventions.md` for networking configuration systems by release, DNS resolution chain, and standard network file locations.

## When to Trigger

- Configure static IP addresses or DHCP
- Set up DNS resolution or change DNS servers
- Configure routes, gateways, or multi-path routing
- Create bridges (for VMs) or bonds (for redundancy)
- Set up VLANs
- Configure hostname and FQDN
- Debug connectivity, DNS, or routing issues
- Work with systemd-resolved or netplan

## Quick Start: Netplan Static IP

Most changes go through `/etc/netplan/`:

```yaml
---
# /etc/netplan/99-custom.yaml
network:
  version: 2
  renderer: networkd  # Use systemd-networkd backend
  ethernets:
    eth0:
      addresses: [192.168.1.100/24]
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

Apply and test with **safe rollback**:

```bash
sudo netplan try       # Applies for 120 seconds, auto-rollback on disconnect
sudo netplan apply     # Permanent apply (after you've tested)
```

Always use `netplan try` first. Only use `netplan apply` after confirming connectivity works.

## Task: Static IP Configuration

### Scenario

Change interface `eth0` from DHCP to static IP `192.168.1.50/24`, gateway `192.168.1.1`, DNS `1.1.1.1`.

### Steps

1. **Identify Netplan renderer**

   ```bash
   systemctl status systemd-networkd
   # or check existing config
   grep -r "renderer:" /etc/netplan/ | head -1
   ```

   Debian/Ubuntu default is `networkd` (systemd-networkd backend).

2. **Create or edit Netplan YAML**

   ```yaml
   # /etc/netplan/99-static-eth0.yaml
   network:
     version: 2
     renderer: networkd
     ethernets:
       eth0:
         dhcp4: false
         addresses: [192.168.1.50/24]
         gateway4: 192.168.1.1
         nameservers:
           addresses: [1.1.1.1]
   ```

   **File naming:** Use `99-` prefix to ensure it loads last (lower numbers first).

3. **Test with rollback**

   ```bash
   sudo netplan try
   ```

   If connectivity works, press Enter to accept. If it hangs or fails, system auto-reverts after 120s.

4. **Verify (while in try mode)**

   ```bash
   ip addr show eth0
   ip route show
   resolvectl status  # Check DNS
   ```

5. **Persist if good**

   Press Enter at the `netplan try` prompt. Or:

   ```bash
   sudo netplan apply
   ```

### Debugging

- **Interface doesn't get IP:** Check YAML indentation (spaces, not tabs). Run `netplan validate` to catch syntax errors.
- **DNS not working:** See [DNS Resolution](#task-dns-resolution-and-systemd-resolved).
- **Route not applied:** Ensure `gateway4` or `routes` sections are at the right indent level (same level as `addresses`).

## Task: DNS Resolution and systemd-resolved

### DNS Resolution Chain

On Debian/Ubuntu, DNS resolution follows this order (per `debian-conventions.md`):

1. `/etc/nsswitch.conf` — controls resolution order (usually `files dns`)
2. `systemd-resolved` — stub resolver listening on `127.0.0.53:53`
3. `/etc/resolv.conf` — often symlink to systemd-resolved stub
4. `/etc/hosts` — static mappings (checked first if nsswitch says `files` first)

### Configure DNS via Netplan

```yaml
network:
  ethernets:
    eth0:
      nameservers:
        addresses: [1.1.1.1, 1.0.0.1]
        search: [example.com]  # Search domain for short names
```

### Direct systemd-resolved Configuration

If you need to override Netplan or configure globally:

```ini
# /etc/systemd/resolved.conf
[Resolve]
DNS=1.1.1.1 1.0.0.1
FallbackDNS=8.8.8.8
Domains=example.com  # Search domain
DNSSEC=yes
```

Then reload:

```bash
sudo systemctl restart systemd-resolved
resolvectl status  # Verify
```

### Verify DNS Works

```bash
resolvectl status                    # Current DNS config + status
dig google.com                       # Full DNS query with details
nslookup google.com                  # Simple DNS lookup
host example.com                     # Another lookup tool
curl -v https://example.com 2>&1 | grep -i "connected to"
```

### Common Issue: Resolved Not Working

- **Check stub resolver:** `cat /etc/resolv.conf` should symlink to `127.0.0.53`.
- **If it doesn't:** `sudo ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf`
- **If resolved is disabled:** Check `/etc/systemd/resolved.conf` for `DNSStubListener=no` (or other distro issue).

## Task: Hostname Management

### Set Hostname

```bash
sudo hostnamectl set-hostname my-server
sudo hostnamectl set-hostname my-server --static   # Set in /etc/hostname too
sudo hostnamectl set-hostname "My Server" --pretty # Pretty hostname for UI
```

This updates:
- `/etc/hostname` (persistent)
- systemd hostname database
- `/etc/hosts` (partially — add entry manually for completeness)

### Add Local Domain Entries

Edit `/etc/hosts`:

```
192.168.1.50  my-server.local  my-server
```

Then verify:

```bash
hostname -f         # FQDN (if set properly)
getent hosts my-server.local
```

## Task: Routes and Advanced Routing

### Static Routes via Netplan

```yaml
network:
  ethernets:
    eth0:
      addresses: [192.168.1.100/24]
      gateway4: 192.168.1.1
      routes:
        - to: 10.0.0.0/8
          via: 192.168.1.254
          metric: 100
        - to: 172.16.0.0/12
          via: 192.168.1.253
          metric: 200
```

### View Current Routes

```bash
ip route show               # All routes
ip route show table local   # Local routes
ip -4 route show            # IPv4 only
```

### Add Temporary Route (reverts on reboot)

```bash
sudo ip route add 10.0.0.0/8 via 192.168.1.254
```

## Task: Bridges (for VM Host)

Bridge mode allows a VM to appear on the same network as the host (useful for homelab VMs).

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: false
  bridges:
    br0:
      dhcp4: true  # Or static IP
      interfaces: [eth0]  # Bridge onto eth0
```

After apply, DHCP (or static) runs on `br0` instead of `eth0`. VMs attach to `br0` via `network: bridge=br0` in their config.

### Verify Bridge

```bash
ip link show type bridge
brctl show          # If bridge-utils installed
```

## Task: Bonds and Link Aggregation

Combine multiple NICs for redundancy or bandwidth:

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0: {}
    eth1: {}
  bonds:
    bond0:
      interfaces: [eth0, eth1]
      parameters:
        mode: active-backup  # Failover mode (simple)
        # mode: balance-alb  # Load-balance mode
        mii-monitor-interval: 100
      dhcp4: true
```

Modes:
- `active-backup` — one active, others standby (simplest)
- `balance-rr` — round-robin across all
- `balance-alb` — adaptive load-balancing

## Task: VLAN Configuration

VLANs segment a single physical NIC into multiple logical networks. Useful in homelab for device segmentation.

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0: {}  # Physical NIC, no config
  vlans:
    vlan10:
      id: 10
      link: eth0
      addresses: [192.168.10.100/24]
      gateway4: 192.168.10.1
    vlan20:
      id: 20
      link: eth0
      addresses: [192.168.20.100/24]
      gateway4: 192.168.20.1
```

After apply, packets with VLAN tag 10 go to `vlan10` interface, tag 20 to `vlan20`, etc. Requires VLAN-capable switch on the other end.

## Task: Network Troubleshooting

### Diagnostic Workflow

1. **Check interface status**

   ```bash
   ip link show
   ip addr show
   ```

   Look for `UP` (interface active) vs `DOWN`.

2. **Verify IP and gateway**

   ```bash
   ip route show
   ip route get 8.8.8.8  # Trace route to a public IP
   ```

3. **Test local connectivity**

   ```bash
   ping 192.168.1.1          # Gateway
   ping 192.168.1.100        # Another host on LAN
   ```

4. **Test DNS**

   ```bash
   resolvectl status
   dig google.com
   nslookup 8.8.8.8  # Reverse lookup for gateway
   ```

5. **Test internet (if expected)**

   ```bash
   curl -v https://google.com 2>&1 | head -20
   ```

6. **Check for packet loss or latency**

   ```bash
   mtr -c 10 8.8.8.8         # Modern traceroute with loss stats
   ping -c 5 8.8.8.8         # Simple 5-packet ping
   ```

### Common Issues

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Interface DOWN | Physical disconnect or Netplan error | Check cable, run `netplan validate`, check logs: `journalctl -u systemd-networkd -n 50` |
| No IP address | DHCP server unreachable or static config wrong | Check DHCP server, verify YAML indentation, test with `netplan try` |
| DNS not resolving | systemd-resolved not running or misconfigured | `systemctl status systemd-resolved`, check `/etc/systemd/resolved.conf`, restart with `systemctl restart systemd-resolved` |
| Slow connectivity | High latency or packet loss | Use `mtr` to identify where loss occurs, check gateway/route metrics |
| Connection drops | MTU mismatch or firmware issue | Check MTU: `ip link show eth0 \| grep mtu`, test with `ping -M do -s 1472 <ip>` to find MTU ceiling |
| Route not working | Wrong metric or interface not bound | Check `ip route show`, ensure interface is UP, verify route via `ip route get <dest>` |

### Systemd-networkd Logs

Netplan uses systemd-networkd as backend. Check service logs:

```bash
sudo journalctl -u systemd-networkd -n 100  # Last 100 lines
sudo journalctl -u systemd-networkd -f      # Follow live
```

### Netplan Validation

```bash
sudo netplan validate
netplan --debug generate  # See what YAML compiles to
```

## Task: Cloud-init and Network Config Persistence

### Issue: Cloud-init Overwrites Network Config

On cloud-deployed systems (AWS, Azure, etc.), cloud-init may override `/etc/netplan/`. To prevent:

```yaml
# /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
network: {config: disabled}
```

After this, cloud-init won't touch `/etc/netplan/`. Verify:

```bash
cloud-init status
sudo cloud-init clean --logs --seed  # Reset cloud-init (if needed)
```

## Task: Interface Naming

Linux uses **predictable interface names** (e.g., `eth0`, `wlan0` mapped to physical location). For consistency across reboots:

- Names based on: firmware, device path, MAC address (in predictable order)
- To see mapping: `ip link show`
- To rename (via Netplan): Not directly, but reference by MAC in Netplan if needed

If you see unusual names like `enp2s0f0` (pci path) or `enx...` (MAC-based), these are predictable—don't change them without good reason.

## Task: MTU Configuration

MTU (Maximum Transmission Unit) is usually 1500 bytes. Some networks require smaller (e.g., 1400 for some ISPs, 1450+ for tunnels).

### Set MTU via Netplan

```yaml
network:
  ethernets:
    eth0:
      mtu: 1450
      dhcp4: true
```

### Test MTU

```bash
ping -M do -s 1472 8.8.8.8      # Try 1500-byte packet (1472 payload + 28 header)
# If fails, lower payload until it works
```

## Notes on Firewall Integration

Network configuration and firewall rules are independent:
- **Networking skill** (this) — IP config, routing, DNS, netplan
- **Security skill** — UFW, iptables/nftables rules, port blocking

When debugging connectivity, verify both:
1. Network config is correct (routing, DNS working)
2. Firewall isn't blocking the traffic (`sudo ufw status`, check inbound/outbound rules)

---

**Key Takeaway:** Use `netplan try` before `netplan apply`. Always test before persisting. Check systemd-networkd logs if things don't work.
