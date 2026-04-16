---
title: Azure VM and VMSS
tags:
  - azure/compute
  - azure/VM
  - azure/VMSS
aliases:
  - Azure VM
  - Azure VMSS
  - Virtual Machine Scale Sets
date: 2026-04-16
---

# Azure VM and VMSS

## Related Notes

- [[Azure/1_Azure-Linux-VM-troubheshooting]]
- [[Azure/6_Azure-Networking]]
- [[Azure/5_Azure-Storage]]

---

## VM - IaaS Service

- ==IaaS==: Cloud provides servers, virtualization, storage, and networking; users configure dev environments, manage apps and data
- ==PaaS==: Cloud provides complete dev environment; users develop apps and manage data
- ==SaaS==: Cloud provides ready-to-use applications; users consume directly

![image-20250607215225183](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072152288.png)

---

## VM Physical Node Architecture

VM is deployed in Windows Server physical machines, which reside on racks. Racks have management hardware called ==Fabric==, controlled by ==Fabric Controller==.

Fabric receives definitions for hardware, networking, and other resources. It controls datacenter resource allocation, manages service lifecycles, monitors heartbeats, and handles failures. Datacenter servers form clusters of approximately 1000, also called blades. Clusters belong to different fault domains; each cluster is managed and deployed by FC.

Fabric capabilities:

- Run process service model files
- Allocate compute and network resources (provisioning)
- Prepare nodes
- Configure networking
- Provide service-health management

---

## VM Deployment Architecture

### Fabric

![image-20250607215705735](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072157003.png)

### Host Agent

Fabric creates nodes (physical nodes where VMs reside). Physical nodes have a ==Host Agent==:

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072159883.png" alt="image-20250607215905744" style="zoom:50%;" />

### Guest Agent

Physical nodes contain multiple VMs. VMs have a ==Guest Agent==:

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072159961.png" alt="image-20250607215953894" style="zoom:50%;" />

Guest Agent functions:

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072202407.png" alt="image-20250607220229193" style="zoom:50%;" />

> [!example] Manually Reinstall Guest Agent (waagent)

```sh
# centos7 lab test：
# uninstall waagent
systemctl stop waagent
waagent -deprovision -force
rm -rf /var/lib/waagent

# install waagent
service network restart
yum install -y git
# if python2.7 is not installed, install it
pkg install python27
pkg install Py27-setuptools27 
ln -s /usr/local/bin/python2.7 /usr/bin/python
```

```sh
git clone https://github.com/Azure/WALinuxAgent.git
cd WALinuxAgent
python setup.py install --register-service
waagent --version
systemctl status waagent
```

### Wire Server

Guest Agent communicates with Host Agent through ==Wire Server==. Wire Server docs:

[What is IP address 168.63.129.16? | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/what-is-ip-address-168-63-129-16)

[Azure Instance Metadata Service for virtual machines - Azure Virtual Machines | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service?tabs=windows)

![image-20250607220207319](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072202559.png)

Wire Server troubleshooting:

- [What is IP address 168.63.129.16? | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/what-is-ip-address-168-63-129-16)
- [What is IP address 168.63.129.16? | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/what-is-ip-address-168-63-129-16#troubleshoot-connectivity)

> [!important] Wire Server Communication
> VM Agent communicates with Azure platform to report status. VM gets IP and DHCP through ==168.63.129.16==.
>
> The VM Agent requires outbound communication over ports ==80/tcp== and ==32526/tcp== with WireServer (168.63.129.16).
>
> These should be open in the local firewall on the VM. Communication on these ports with 168.63.129.16 is not subject to configured NSGs.
>
> 168.63.129.16 can provide DNS services to the VM. If not desired, outbound traffic to 168.63.129.16 ports 53/udp and 53/tcp can be blocked in the local firewall.

Check connectivity:

Windows OS:

```sh
Test-NetConnection 168.63.129.16 -Port 80
Test-NetConnection 168.63.129.16 -Port 32526
```

Linux OS:

```sh
telnet 168.63.129.16 80
telnet 168.63.129.16 32526
```

---

## Azure Resource Manager

![image-20250608093651506](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506080936637.png)

Users operate Azure resources through Azure Tools, all requests are received by ==ARM== which performs the corresponding operations:

![image-20250608093727794](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506080937848.png)

==ARM Template==: JSON files defining resource infrastructure and configuration, enabling automated deployment of identical environments.

Example of VM deployment:

![image-20250608093812500](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506080938563.png)

---

## VM ARM Deployment Process

SRP, CRP, NRP etc. create corresponding resources respectively:

![image-20250607220511709](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072205194.png)

---

## VM Regional Code

| Region       | Code |
| ------------ | ---- |
| China North  | bjb  |
| China North2 | bjb2 |
| China East   | sha  |
| China East2  | sha2 |

---

## VM Platform Maintenance

[维护和更新 - Azure Virtual Machines | Microsoft Docs](https://docs.microsoft.com/zh-cn/azure/virtual-machines/maintenance-and-updates?toc=%2Fazure%2Fvirtual-machines%2Flinux%2Ftoc.json&bc=%2Fazure%2Fvirtual-machines%2Flinux%2Fbreadcrumb%2Ftoc.json)

[Maintenance and updates - Azure Virtual Machines | Microsoft Docs](https://docs.microsoft.com/en-us/azure/virtual-machines/maintenance-and-updates)

### Types

VM updates and deployments are roughly divided into 2 types:

[https://docs.azure.cn/zh-cn/virtual-machines/maintenance-notifications](https://docs.azure.cn/zh-cn/virtual-machines/maintenance-notifications)

1. If maintenance does not require a reboot, Azure pauses the VM for a few seconds during host update. These maintenance operations are applied fault domain by fault domain. The process stops if any warning health signals are received. Maintenance requiring reboot sends a notification.
2. If maintenance requires a reboot, the system notifies the planned maintenance time. A window of approximately ==35 days== is provided for self-service maintenance.

> [!info] Memory-Preserving Updates
> Memory-preserving updates typically complete within ~10 seconds. For this type of deployment, the platform does not send notifications. However, you can obtain platform maintenance/deployment info through VM Metadata Service. See [Azure 中适用于Windows VM 的计划事件](https://docs.azure.cn/zh-cn/virtual-machines/windows/scheduled-events).

### Alerts

VM health status alerting. Common monitoring options:

1. **Scheduled Events** - Monitor the following events, see [Azure 中适用于Windows VM 的计划事件 | Azure Docs](https://docs.azure.cn/zh-cn/virtual-machines/windows/scheduled-events):
   - [Platform-initiated maintenance](https://docs.azure.cn/zh-cn/virtual-machines/maintenance-and-updates) (e.g., VM reboot, live migration, memory-preserving updates)
   - VM running on [degraded host hardware](https://azure.microsoft.com/blog/find-out-when-your-virtual-machine-hardware-is-degraded-with-scheduled-events) predicted to fail soon
   - User-initiated maintenance (e.g., user restart or redeploy VM)

2. **Resource Health** - Monitor VM state (start, shutdown, etc.). See [Azure 资源运行状况概述 | Azure Docs](https://docs.azure.cn/zh-cn/service-health/resource-health-overview) & [通过Azure 资源运行状况支持的资源类型 | Azure Docs](https://docs.azure.cn/zh-cn/service-health/resource-health-checks-resource-types)

3. **Azure Log Analytics Agent** - More powerful monitoring and alerting service, such as monitoring heartbeats and CPU through log queries. See [Azure 中的警报和通知监视概述 | Azure Docs](https://docs.azure.cn/zh-cn/azure-monitor/platform/alerts-overview)

---

# Azure VM Basics

## VM Availability Options

- **Fault Domain**
  - Physical grouping
  - In a datacenter, servers are divided into groups, each using the same power supply and network equipment
  - If one group's power or network fails, only that group is affected

- **Update Domain**
  - Logical grouping
  - When servers need patches or upgrades requiring restarts, not all servers restart at once
  - Divided into update domains, only one group restarts at a time

- **Availability Sets**
  - Within a datacenter, an availability set consists of multiple fault domains and update domains (configurable)
  - A logical concept: VMs in an availability set are distributed across different fault and update domains for high availability

- **Availability Zones**
  - Physically independent zones with separate power, networking, etc.
  - Use zone-replicated VMs; if one datacenter goes down, replicated VMs activate in another
  - Each zone has at least ==3 datacenters==, each with independent power, cooling, and networking
  - Can be understood as a larger-scale fault domain and update domain
  - Protects against entire datacenter failures
  - Azure China limited support (North3 supports)

- **Regional Pair** - Paired regions ensure upgrades affect only one, with priority recovery for one

- **VM Scale Sets** - Build load-balanced clusters

### Create VM in Availability Set

[使用 Azure PowerShell 在可用性集中部署 VM - Azure 虚拟机 | 微软文档](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/tutorial-availability-sets)

![image-20250608095059478](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506080950649.png)

---

## VM SKU Naming Convention

![image-20250607220348948](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072203223.png)

---

## VM Extension

Azure VM Extensions are small programs providing deployment, configuration, and automation.

**How to install:**

- Using Azure CLI, PowerShell, ARM, Portal

**Prerequisites:**

- Need ==Azure Linux Agent== installed to manage VM extensions
- Some extensions have OS limitations

Related docs:

- https://docs.microsoft.com/en-us/azure/virtual-machines/extensions/agent-windows
- [Azure Linux VM Agent Overview | 微软文档](https://docs.microsoft.com/en-us/azure/virtual-machines/extensions/agent-linux)
- [azure-linux-extensions/CustomScript | GitHub](https://github.com/Azure/azure-linux-extensions/tree/master/CustomScript)
- https://docs.microsoft.com/en-us/azure/virtual-machines/windows/extensions-customscript?toc=%2Fazure%2Fvirtual-machines%2Fwindows%2Ftoc.json

> [!tip] Troubleshooting Extensions
> Extensions are managed by VM Agent. Log location: `/var/log/azure/<extension name>/extension.log`

- [Troubleshoot the Azure Linux Agent - Virtual Machines | Microsoft Docs](https://docs.microsoft.com/en-us/troubleshoot/azure/virtual-machines/linux-azure-guest-agent)
- [Troubleshooting Azure Windows VM Agent - Virtual Machines | Microsoft Learn](https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/windows-azure-guest-agent)
- [Troubleshoot Agent and extension issues - Azure Backup | Microsoft Learn](https://learn.microsoft.com/en-us/azure/backup/backup-azure-troubleshoot-vm-backup-fails-snapshot-timeout#the-agent-installed-in-the-vm-but-unresponsive-for-windows-vms)

### Common Extensions

#### VMAccess

**What?**

- VM disk error, forgotten root password, or deleted SSH private key - need recovery, which normally requires datacenter console access
- ==VMAccess Extension== can access the console to reset Linux access
- Requires `waagent.service` process running on Linux

**How?**

- When VM can access Azure Linux Agent:
  - Use Azure CLI command with parameters to set directly
  - Create JSON file with reset parameters, use Azure CLI to read and apply

Steps:

- [重置对 Azure Linux VM 的访问 | 微软文档](https://docs.microsoft.com/en-us/azure/virtual-machines/extensions/vmaccess)
- [azure-linux-extensions/VMAccess | GitHub](https://github.com/Azure/azure-linux-extensions/tree/master/VMAccess)

#### Run Command

Can run custom commands in a VM.

[Run scripts in a Windows VM in Azure using action Run Commands - Azure Virtual Machines | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-machines/windows/run-command#restrictions)

> [!note] Run Command Script Location
> View run command scripts on Linux VM at `/var/lib/waagent/run-command/download`. `script.sh` is the script, `stdout` is the execution result.

---

## VM Image and Snapshot

**What is Image:**

- Image is a copy of a complete VM or OS disk only. Use a configured VM as template to create multiple identical VMs.
- Before creating VM from image, remove personal account info, then ==generalize==.

**Difference between Image and Snapshot:**

- Image contains all disks of the VM, can be used to create new VMs
- Snapshot is a copy of a single disk
- Image creation requires ==deprovision== to clear personal info; snapshot does not

**How:**

- For managed disk VMs, Portal has a direct capture option

Docs:

- [使用 Azure CLI 捕获 Linux VM 的托管映像 | 微软文档](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/capture-image)
- [在 Azure 中创建托管映像 | 微软文档](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/capture-image-resource)

---

## Azure VM Boot Diagnostics

[Azure 中 VM 的启动诊断 | 微软文档](https://docs.microsoft.com/en-us/troubleshoot/azure/virtual-machines/boot-diagnostics)

In Portal, use ==screen display== / ==serial log== to view VM boot issues. Use screen display to check VM state when it becomes unresponsive.

- **Linux:**
  - sos report: [如何收集Linux 虚拟机的诊断日志 | Azure Docs](https://docs.azure.cn/zh-cn/articles/azure-operations-guide/virtual-machines/linux/aog-virtual-machines-linux-howto-gather-diagnostic-log)
  - Most system logs are in `/var/log/`: e.g., `/var/log/boot.log` for boot info; `/var/log/secure` for SSH, sudo, user add, password changes; `/var/log/messages` for important system info
  - rsyslogd manages logs. Configure in `/etc/rsyslog.conf`

- **Windows System Event Log:**
  - `C:\Windows\System32\winevt\Logs`
  - `C:\Windows\Memory.dmp` if available
  - `C:\Windows\Minidump\` if available

---

# Azure VM Troubleshooting

## Recovery VM

> [!summary] Recovery VM Process
> When a VM has boot or SSH issues, create a snapshot of the OS Disk, then create a Recovery Disk from the snapshot and attach it to a recovery VM for troubleshooting.

1. Create snapshot of issue VM's OS Disk, create new Recovery Disk from snapshot.

2. Create a ==Dv3 or Ev3+== VM in the same Region as the Recovery Disk. Install Windows Server 2016+ (supports nested virtualization), enable Hyper-V:
   ```
   Install-WindowsFeature -Name Hyper-V -IncludeManagementTools -Restart
   ```

3. Attach Recovery Disk to the VM, offline the disk, create Hyper-V VM with it:
   - Computer Management - Disk Management - Offline
   - Hyper-V Manager - New VM - Attach a virtual hard disk later
   - VM Settings - IDE Controller0 - Hard Drive - Physical Hard Disk - Apply
   - Get into console

4. Access VM console for troubleshooting or repair.

This method is suitable when Guest Agent is inaccessible, or for resetting local passwords. Related docs:

- [如何通过 Hyper-V Console 方式修复虚拟机无法访问的问题 | Azure Docs](https://docs.azure.cn/zh-cn/articles/azure-operations-guide/virtual-machines/aog-virtual-machines-howto-fix-ssh-or-rdp-issues-via-hyper-v-console)
- [Nested Virtualization | Microsoft Docs](https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/user-guide/nested-virtualization)
- [在 Windows Server 上安装 Hyper-V 角色 | 微软文档](https://docs.microsoft.com/en-us/windows-server/virtualization/hyper-v/get-started/install-the-hyper-v-role-on-windows-server)
- [How to reset local Linux password on Azure VMs - Virtual Machines | Microsoft Learn](https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/linux/reset-password)
- [How to Boot into Single User Mode in CentOS/RHEL 7 (tecmint.com)](https://www.tecmint.com/boot-into-single-user-mode-in-centos-7/)

---

## Mount OS Disk

When the filesystem is mounted as ==read-only== due to incorrect fstab settings and internal files cannot be modified, the Hyper-V boot mode approach is difficult. Workaround: attach the issue disk as a data disk to another VM, mount it to a directory, edit fstab. After changes, re-attach to the nested VM for further operations.

---

## Mount Disk + chroot

Related doc: [How to troubleshoot the chroot environment in a Linux Rescue VM - Virtual Machines | Microsoft Learn](https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/chroot-environment-linux#rhelcentosoracle-6x--oracle-8x--rhelcentos-7x-with-raw-partitions)

---

# Azure VMSS

==VMSS== (Virtual Machine Scale Sets) is a combination of independent VMs that is load-balanced, can automatically scale VM instances based on demand. Features centralized management, configuration, and updating of large numbers of VMs. Key advantage over manual creation is automated configuration, automatic load balancing. Suitable for large-scale compute tasks and workloads with varying demand over time, saving cost and time.

- [Azure virtual machine scale sets overview | Microsoft Docs](https://docs.microsoft.com/en-us/azure/virtual-machine-scale-sets/overview)
- [Azure 虚拟机规模集概述 | Azure Docs](https://docs.azure.cn/zh-cn/virtual-machine-scale-sets/overview)

![image-20250608100534712](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506081005945.png)

![image-20250608100552233](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506081005473.png)

---

## VMSS - Load Balancer

Load Balancer works at the transport layer. Methods to access VMSS:

- Assign each VM its own public IP (expensive)

- Use ==Load Balancer with NAT==:
  - Assign public IP to LB, LB routes traffic through each VM's port to individual VM instances
  - By default, NAT rules are added to LB, forwarding remote connection traffic to each VM on given ports

---

## VMSS Auto-scale

- [教程 - 使用 Azure CLI 自动缩放规模集 | Azure Docs](https://docs.azure.cn/zh-cn/virtual-machine-scale-sets/tutorial-autoscale-cli)
- [在 Azure 门户中自动缩放虚拟机规模集 | 微软文档](https://docs.microsoft.com/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-autoscale-portal)

---

# VM Security

> [!important] Azure VM Security Best Practices

- **Overall VM protection**: See [Azure 中IaaS 工作负载的安全性最佳做法 | Azure Docs](https://docs.azure.cn/zh-cn/security/fundamentals/iaas)
- **OS-level protection**: Deploy [Microsoft Antimalware for Azure | Azure Docs](https://docs.azure.cn/zh-cn/security/fundamentals/antimalware) to identify and remove viruses and malware (note: mining software is not in scope)
- **OS updates**: See [为Azure VM 启用Azure 自动化更新管理 | Azure Docs](https://docs.azure.cn/zh-cn/automation/update-management/enable-from-vm) for enabling update management and scheduled batch updates
- **Performance monitoring**: See [使用Azure Monitor 代理从虚拟机收集事件和性能计数器 | Azure Docs](https://docs.azure.cn/zh-cn/azure-monitor/agents/data-collection-rule-azure-monitor-agent) for configuring performance monitoring and alerts
- **Security posture**: See [Microsoft Defender for Servers 概述 | Azure Docs](https://docs.azure.cn/zh-cn/defender-for-cloud/defender-for-servers-introduction) for configuring Microsoft Defender for Cloud, with integration to Microsoft Sentinel [Detect threats with built-in analytics rules in Microsoft Sentinel | Azure Docs](https://docs.azure.cn/zh-cn/sentinel/detect-threats-built-in) for monitoring OS-level anomalies
- **Network configuration**: See [限制直连Internet连接](https://docs.azure.cn/zh-cn/security/fundamentals/iaas#restrict-direct-internet-connectivity) for configuring ==NSG== and enabling ==JIT (Just-In-Time)== access control. Enable NSG flow logs via [NSG 流日志 - Azure Network Watcher | Microsoft Learn](https://learn.microsoft.com/zh-cn/azure/network-watcher/network-watcher-nsg-flow-logging-overview)
