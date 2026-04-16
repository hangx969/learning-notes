---
title: Azure Linux VM Troubleshooting
tags:
  - azure/compute
  - azure/VM
  - azure/troubleshooting
  - azure/linux
aliases:
  - Linux VM Troubleshooting
  - Azure VM Linux Issues
date: 2026-04-16
---

# Azure Linux VM Troubleshooting

## Related Notes

- [[Azure/0_Azure-VM-VMSS]]

---

## Expand OS Disk

### Issue

Expanded OS disk size in Azure portal but the Linux filesystem is not expanded.

### Solve

Help cx to expand the root filesystem:

[如何在 Linux 虚拟机上扩展根文件系统 | Azure Docs](https://docs.azure.cn/en-us/articles/azure-operations-guide/virtual-machines/linux/aog-virtual-machines-qa-linux-root-file-system-extension)

- Backup the OS disk first
- `df -h` check the root file system usage

- In CentOS 6:
  - Expand the /sda1 partition: ==fdisk==
  - Reboot
  - Expand the root filesystem: ==resize2fs==
  - Then the root fs will be expanded.

> [!info] Useful Disk Commands
> `df -h` provides information on the overall disk space usage, showing statistics for each mounted file system.
>
> `du -h` provides information about the sizes of directories and files in a specified directory or a list of directories.
>
> `lsblk -f` command is used to list information about block devices, including file system information.
>
> `fdisk -l` command is used to list information about the **disk partitions** on a system.

---

## Filesystem Corrupted

### Issue

VM started failure with filesystem corrupted.

### Solve

[文件系统损坏导致虚拟机无法正常启动的问题及解决方法 | Azure Docs](https://docs.azure.cn/en-us/articles/azure-operations-guide/virtual-machines/linux/aog-virtual-machines-troubleshoot-restart)

- **Root fs corrupted:**
  - Create another rescue VM and mount the issue disk as a data disk
  - Backup the fs info
  - `fsck -yM /dev/sdc1`
- **Normal partition corrupted:**
  - Create another rescue VM and mount the issue disk as a data disk
  - Comment out the corrupted fs in fstab of the issue disk
  - Mount back the issue disk to the VM
  - `fsck -yM` to repair the fs
  - Un-comment the partition in fstab, reboot VM

---

## VM Cannot Start with fstab Issue

### Issue

- cx deleted a data disk but in fstab, the disk info is still there ==> VM cannot start (we can get error message ==dependency failed== in serial log)

### Solve

- Mount the issue VM disk to a rescue VM as a data disk
- Edit the fstab, either comment out the corresponding line in fstab or add ==nofail== to this line
- Mount back to the original VM and start

---

## Ubuntu Netplan Issue

### Issue

- VM start failure with error message:

  **Error** in network definition `/etc/netplan/50-cloud-init.yaml` line 8 column 12: unknown key dhcp4-overrides

### Solve

- Netplan is a command-line network configuration utility for Linux-based operating systems, including Ubuntu. It is used to configure and manage network interfaces and network settings, such as IP addresses, DNS settings, and routing tables.
- Netplan is the default network configuration tool on ==Ubuntu 17.10== and later.
- Lower version netplan will have compatible issue with Ubuntu 18.04
- Mount the OS disk to a rescue VM and use ==chroot== to get root environment
- `apt install netplan.io` to get latest version

---

## Ubuntu Unattended-Upgrades

### Issue

- Azure Kubernetes service uses upstream Ubuntu as Operating system for worker nodes.
- Customers running Ubuntu 18.04 who had ==Unattended-Upgrades== enabled, would receive a **systemd version** upgrade that resulted in Domain Name System (DNS) resolution errors.
- There is a bug in this new version of systemd, it cleared the content in `/etc/resolv.conf`, causing DNS error.

### Solve

> [!tip] Quick Fix
> Reboot VM to get DNS conf back, or manually write the content back to `/etc/resolv.conf`.

- Some customers disabled the Unattended-Upgrades in Ubuntu and changed to manually upgrade.

---

## How to Upgrade CentOS to Specific Minor Version

[如何升级 CentOS 到指定小版本 | Azure Docs](https://docs.azure.cn/en-us/articles/azure-operations-guide/virtual-machines/linux/aog-virtual-machines-linux-centos-howto-upgrade-to-specified-minor-version)

- By default, CentOS `yum update` will upgrade to the latest minor version
- But we can configure the yum repo configuration to upgrade to specific minor version
- It is located in `/etc/yum.repos.d`, and repo file name ends with `.repo`
- If we want to install different versions of kernel, we can configure yum to connect to the repo url of different version
- So, we can configure the ==CentOSBase.repo== and ==OpenLogic.repo==, edit the baseurl, write the specific minor version
- `yum clean all` ==> `yum update`

---

## How to Upgrade Ubuntu Kernel Version

- [如何升级 Ubuntu 内核 | Azure Docs](https://docs.azure.cn/en-us/articles/azure-operations-guide/virtual-machines/linux/aog-virtual-machines-linux-ubuntu-howto-upgrade-kernel)
- Find the Ubuntu official website to get specific kernel version link
- `wget` the specific link
- `dpkg -i` to install

---

## SSH Failed

### Internal OS Issue

- sshd not started
- CPU/memory pressure causing sshd service not operational
- Wrong configuration in `/etc/ssh/sshd_config`

### Network Connectivity Issue

- Wrong configure in network
  1. For example, in `/etc/sysconfig/network-scripts/ifcfg-eth0`, you set static IP address, but actually the IP of NIC is from DHCP
- Host server: ==firewalld== or ==iptables== has blocked the client IP, or blocked the 22 port inbound, or changed ssh port to another port
- Client server: firewall blocked server IP or 22 port outbound

---

## Pacemaker Node Reboot

### Issue

Cx reported a VM restarted unexpectedly.

### Solve

- Collect OS logs in `/var/log/`, and check messages
- Find that the VM is a node of a ==pacemaker cluster==

> [!important] Root Cause
> The networking connectivity between pacemaker nodes were lost for 30 sec, then one node was rebooted by its peer. Further investigation showed the connectivity loss was sometimes caused by underlying host node patch.
