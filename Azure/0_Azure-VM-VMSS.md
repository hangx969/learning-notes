# Azure VM底层

## VM - IaaS服务

- Iaas中，由云服务提供服务器，虚拟化，存储和网络；用户自行配置开发环境，管理应用和数据

- PaaS中，由云服务提供完整的开发环境，由用户进行应用开发和数据管理。

- SaaS中，由云服务提供开发好的应用程序，用户可以直接使用

![image-20250607215225183](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072152288.png)

## VM物理节点架构

VM部署在windows server物理机中，物理机位于机架上，机架上有管理硬件叫Fabric，由Fabric Controller控制。

Fabric接收硬件、网络等资源的的定义，控制数据中心资源的分配和提供，管理服务的生命周期，监控heartbeat，处理故障数据中心的服务器是以1000台左右形成一个cluster，也叫blade，cluster之间属于不同的fault domain；每一个cluster由FC来管理、部署。

Fabric的功能：

- Run process service model files
- Allocate compute and network resources(provisioning)
- Prepare nodes
- Configure networking
- Provide service-health management

## VM部署的底层架构

### Fabric

![image-20250607215705735](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072157003.png)

### Host agent

Fabric创建了node，即VM所在的物理节点，物理节点上有Host Agent，其作用是：

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072159883.png" alt="image-20250607215905744" style="zoom:50%;" />

### Guest Agent

物理节点中可以创建若干VM，VM上有guest agent，其架构是：

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072159961.png" alt="image-20250607215953894" style="zoom:50%;" />

guest agent的作用是：

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072202407.png" alt="image-20250607220229193" style="zoom:50%;" />

手动卸载重装guest agent（waagent）：

~~~sh
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
~~~

~~~sh
git clone https://github.com/Azure/WALinuxAgent.git
cd WALinuxAgent
python setup.py install --register-service
waagent --version
systemctl status waagent
~~~

### Wire server

guest agent通过wire server与host agent通信。有关wire server文档：

[What is IP address 168.63.129.16? | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/what-is-ip-address-168-63-129-16)

[Azure Instance Metadata Service for virtual machines - Azure Virtual Machines | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service?tabs=windows)

![image-20250607220207319](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072202559.png)

wire server troubleshooting:

- [What is IP address 168.63.129.16? | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/what-is-ip-address-168-63-129-16)

- [What is IP address 168.63.129.16? | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/what-is-ip-address-168-63-129-16#troubleshoot-connectivity)

VM Agent和Azure platform通信报告状态。

VM拿IP、DHCP也是跟这个IP通信。

The VM Agent requires outbound communication over ports 80/tcp and 32526/ tcp with WireServer (168.63.129.16).

These should be open in the local firewall on the VM. The communication on these ports with 168.63.129.16 is not subject to the configured network security groups; 

168.63.129.16 can provide DNS services to the VM. If this is not desired, outbound traffic to 168.63.129.16 ports 53/ udp and 53/ tcp can be blocked in the local firewall on the VM.

检查连接：

Windows OS

~~~sh
Test-NetConnection 168.63.129.16 -Port 80
Test-NetConnection 168.63.129.16 -Port 32526
~~~

Linux OS

~~~sh
telnet 168.63.129.16 80
telnet 168.63.129.16 32526
~~~

## Azure resource manager

![image-20250608093651506](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506080936637.png)

用户通过Azure Tools 对azure 资源进行操作，都由ARM来接受请求，统一进行相应的操作：

![image-20250608093727794](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506080937848.png)

ARM template：ARM模板：定义资源的础结构和配置的JSON文件，可以自动化建立部署相同的环境。

以部署VM为例：

![image-20250608093812500](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506080938563.png)

## VM ARM部署的过程

SRP、CRP、NRP等分别创建对应的资源

![image-20250607220511709](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072205194.png)

## VM Reginal Code

- China North：bjb

- China North2：bjb2

- China East：sha

- China East2：sha2

## VM平台维护

[维护和更新 - Azure Virtual Machines | Microsoft Docs](https://docs.microsoft.com/zh-cn/azure/virtual-machines/maintenance-and-updates?toc=%2Fazure%2Fvirtual-machines%2Flinux%2Ftoc.json&bc=%2Fazure%2Fvirtual-machines%2Flinux%2Fbreadcrumb%2Ftoc.json)

[Maintenance and updates - Azure Virtual Machines | Microsoft Docs](https://docs.microsoft.com/en-us/azure/virtual-machines/maintenance-and-updates)

### 种类

VM的更新和部署大致分为2种，具体可以参考：

[https://docs.azure.cn/zh-cn/virtual-machines/maintenance-notifications](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Fvirtual-machines%2Fmaintenance-notifications&data=05|01|hangx@microsoft.com|d8d273568cb34e78e5cb08dac6ce9893|72f988bf86f141af91ab2d7cd011db47|1|0|638040887956408818|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=7YV%2FWs7zPRJbo3nEGPjMAYkHVn8CSpLZeXpqVHSH5Pc%3D&reserved=0)

1. 如果维护不需要重启，Azure 会在主机更新时暂停 VM 几秒钟。这些类型的维护操作将逐个容错域进行应用。如果接收到任何警告健康状况信号，则进程将停止。其中，需要重启会发送通知。
2. 如果维护需重新启动，系统会告知计划维护的时间。系统会提供一个大约 35 天的时间窗口，方便我们在适当的时间自行启动维护。

本次部署类型是不需要重启的，可以理解为内存保留类更新，默认会在10几秒内完成，对于这种部署，平台不会发送通知。但可以通过VM metadata service获取平台维护或部署等信息，参考 [Azure 中适用于Windows VM 的计划事件- Azure Virtual Machines | Azure Docs](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Fvirtual-machines%2Fwindows%2Fscheduled-events&data=05|01|hangx@microsoft.com|d8d273568cb34e78e5cb08dac6ce9893|72f988bf86f141af91ab2d7cd011db47|1|0|638040887956408818|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=rxIVU2CHbg6yH1cA6ghYnr1%2B2m2Zc85M%2BJnwwqnr%2F3g%3D&reserved=0)。

### 预警

虚拟机运行状态报警：

一般为了及时得到相关预警和通知，以下监控方案可供采用：

1. 计划事件（Scheduled Event）- 用于监控以下事件，请参考[Azure 中适用于Windows VM 的计划事件| Azure Docs](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Fvirtual-machines%2Fwindows%2Fscheduled-events&data=05|01|hangx@microsoft.com|15154977c2034e01672708db1eb15d71|72f988bf86f141af91ab2d7cd011db47|1|0|638137519467717938|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=Tyeu7iP49%2Bcojmjih2VEmgsB9oaTWeGVYr1bScif6w8%3D&reserved=0)

- [平台启动的维护](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Fvirtual-machines%2Fmaintenance-and-updates%3Fbc%3D%2Fvirtual-machines%2Fwindows%2Fbreadcrumb%2Ftoc.json%26toc%3D%2Fvirtual-machines%2Fwindows%2Ftoc.json&data=05|01|hangx@microsoft.com|15154977c2034e01672708db1eb15d71|72f988bf86f141af91ab2d7cd011db47|1|0|638137519467874150|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=zmQnJFbiJkRPZG%2FUq4pjtdmFrjt5MzpI6EiuQIn7GpI%3D&reserved=0)（例如，VM 重新启动、实时迁移或主机的内存保留更新）
- 虚拟机正在根据预测很快会出现故障的[降级主机硬件](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fazure.microsoft.com%2Fblog%2Ffind-out-when-your-virtual-machine-hardware-is-degraded-with-scheduled-events&data=05|01|hangx@microsoft.com|15154977c2034e01672708db1eb15d71|72f988bf86f141af91ab2d7cd011db47|1|0|638137519467874150|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=ma7jwMEEGEtR7PX6eDU3qbnrcHBTWpJkzacsDz7yvk4%3D&reserved=0)上运行
- 用户启动的维护（例如，用户重启或重新部署VM）

1. Resource Health - 用于监控虚拟机状态，如启动，关机等。参考[Azure 资源运行状况概述| Azure Docs](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Fservice-health%2Fresource-health-overview&data=05|01|hangx@microsoft.com|15154977c2034e01672708db1eb15d71|72f988bf86f141af91ab2d7cd011db47|1|0|638137519467874150|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=cdR49xIoFDSMEGeA1UdZUcMItzh8H1f8oht59fljxbI%3D&reserved=0) & [通过Azure 资源运行状况支持的资源类型|Azure Docs](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Fservice-health%2Fresource-health-checks-resource-types&data=05|01|hangx@microsoft.com|15154977c2034e01672708db1eb15d71|72f988bf86f141af91ab2d7cd011db47|1|0|638137519467874150|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=3CfTXO4fqex8WMC%2FNG74Yuv%2BO38FVAooKW4JlN%2FH2yc%3D&reserved=0)
2. Azure Log Analytics Agent - 更强大的监控和报警服务，如通过日志查询监控心跳，CPU等。参考[Azure 中的警报和通知监视概述| Azure Docs](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Fazure-monitor%2Fplatform%2Falerts-overview&data=05|01|hangx@microsoft.com|15154977c2034e01672708db1eb15d71|72f988bf86f141af91ab2d7cd011db47|1|0|638137519467874150|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=BluOqJ4SpIgpkbMUiE3ZWrefdKDug7br81YTRkrgRFs%3D&reserved=0)

# Azure VM基础知识

## VM Availability Options

- Fault domain
  - 是物理上的分组
  - 在一个数据中心中，服务器被分成若干组，每组使用同一个电源和网络设备
  - 某一组的电源或网络崩溃后，仅有一组服务器受影响，其余组正常运作

- Update domain
  - 逻辑上的分组
  - 一个数据中心中，当服务器需要补丁或软件升级从而重启时，不能所有服务器全部重启
  - 通过分成update domain，每一次只重启一组

- Availability sets
  - 在一个数据中心中，一个availability set由多个fault domain 和 多个 update domain 组成，各自的数量可以配置
  - 可用性集是一个逻辑上的概念，一个可用性集中的多台VM会被分布式的部署在不同的fault和update domain中，来保证高可用性。

- Availability zones
  - 物理上独立的区域，有不同的电源、网络等，
  - 使用区域中的复制VM，一个数据中心倒下，复制的VM将会在另一个中生效
  -  每个zone至少3个数据中心，每个有独立的电源冷却和网络
  - 可以理解为更大尺度上，一个Availability zone是一个fault domain 和update domain；崩溃或者升级时，每次只影响一个zone
  - 作用是避免整个数据中心的崩溃损失
  - Azure中国暂时不支持（北三支持）
- Regional Pair 两两结对 保证升级只升一个，故障优先恢复一个

- VM Scale sets
  - 建立负载均衡的集群

Create VM in Availability Set：

[使用 Azure PowerShell 在可用性集中部署 VM - Azure 虚拟机|微软文档 (microsoft.com)](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/tutorial-availability-sets)

![image-20250608095059478](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506080950649.png)

## VM SKU命名规则

![image-20250607220348948](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072203223.png)

## VM Extension

Azure VM extension是提供部署、配置、自动化的小程序。

如何安装？

- 使用Azure Cli、Powershell、ARM、Portal都可以

安装先决条件

- 想要管理VM 扩展，需要安装**Azure Linux Agent**
- 某些扩展对操作系统有限制

相关文档：

https://docs.microsoft.com/en-us/azure/virtual-machines/extensions/agent-windows

[Azure Linux VM Agent Overview - Azure Virtual Machines |微软文档 (microsoft.com)](https://docs.microsoft.com/en-us/azure/virtual-machines/extensions/agent-linux)

[azure-linux-extensions/CustomScript at master ·Azure/azure-linux-extensions ·GitHub](https://github.com/Azure/azure-linux-extensions/tree/master/CustomScript)

https://docs.microsoft.com/en-us/azure/virtual-machines/windows/extensions-customscript?toc=%2Fazure%2Fvirtual-machines%2Fwindows%2Ftoc.json

**Troubleshooting：**

Extension是由VM Agent来进行管理，日志位置：/var/log/azure/\<extension name\>/extension.log

[Troubleshoot the Azure Linux Agent - Virtual Machines | Microsoft Docs](https://docs.microsoft.com/en-us/troubleshoot/azure/virtual-machines/linux-azure-guest-agent)

[Troubleshooting Azure Windows VM Agent - Virtual Machines | Microsoft Learn](https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/windows-azure-guest-agent)

[Troubleshoot Agent and extension issues - Azure Backup | Microsoft Learn](https://learn.microsoft.com/en-us/azure/backup/backup-azure-troubleshoot-vm-backup-fails-snapshot-timeout#the-agent-installed-in-the-vm-but-unresponsive-for-windows-vms)

### 常用Extension

#### VMAccess

What?

- VM发生磁盘错误，或者忘记了root密码，或者删掉了SSH私钥，需要恢复，那就得去数据中心打开控制台再重新设置
- VMAccess Extension可以访问控制台以重置对Linux的访问
- 在Linux中，要有waagent.service进程

How？

- 在VM可以正常访问Azure Linux Agent时可用以下方法：
  - 可以用Azure Cli命令加上参数，直接设置
  - 可以自建JSON文件设置好准备重设的参数，用Azure Cli命令读取，进行设置

方法步骤：

[重置对 Azure Linux VM 的访问 - Azure 虚拟机|微软文档 (microsoft.com)](https://docs.microsoft.com/en-us/azure/virtual-machines/extensions/vmaccess)

command用法：

[azure-linux-extensions/VMAccess at master ·Azure/azure-linux-extensions ·GitHub](https://github.com/Azure/azure-linux-extensions/tree/master/VMAccess)

#### Run command

可以自定义在VM中运行命令

[Run scripts in a Windows VM in Azure using action Run Commands - Azure Virtual Machines | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-machines/windows/run-command#restrictions)

查看在虚拟机运行run command的脚本内容，可以在linux虚拟机的/var/lib/waagent/run-command/download看到相关的脚本和执行结果。script.sh是脚本，sdtout是执行结果。

## VM Image and snapshot

What is image

- Image是完整VM或者仅OS disk的副本，以一台配置好的VM作为模板，创建多个同样的VM。
- 在创建VM之前，要去掉VM的个人账户信息，再generalize

Image和snapshot的区别？

- image包含了VM上所有的disk，可以用来创建新的VM
- snapshot是对单个disk的复制
- 还有image创建之前deprovision清除了个人信息；snapshot不需要

How

- 对于managed disk的VM，portal上直接就有capture选项

文档：

[使用 Azure CLI 捕获 Linux VM 的托管映像 - Azure 虚拟机|微软文档 (microsoft.com)](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/capture-image)

[在 Azure 中创建托管映像 - Azure 虚拟机|微软文档 (microsoft.com)](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/capture-image-resource)

## Azure VM Boot Diagnotics

[Azure 中 VM 的启动诊断 - 虚拟机|微软文档 (microsoft.com)](https://docs.microsoft.com/en-us/troubleshoot/azure/virtual-machines/boot-diagnostics)

在Portal中，可以通过屏显 / 串口日志来查看虚拟机遇到的启动问题。通过屏显查看虚拟机失去响应时的运行状态。

- Linux：
  - sos report: [如何收集Linux 虚拟机的诊断日志 | Azure Docs](https://docs.azure.cn/zh-cn/articles/azure-operations-guide/virtual-machines/linux/aog-virtual-machines-linux-howto-gather-diagnostic-log)
  - 大部分系统日志会存放在/var/log 目录下：比如/var/log/boot.log记录系统启动信息；/var/log/secure记录SSH，sudo，添加用户，修改密码等安全信息；/var/log/massage记录重要系统信息
  - rsystemd服务管理日志。可以在/etc/rsystemd.conf中配置日志的记录和保存

- Windows System Event Log

  - C:\Windows\System32\winevt\Logs

  - C:\Windows\Memory.dmp if available

  - C:\Windows\Minidump\ if available

# Azure VM troubleshooting

## Recovery VM

1. 当VM出现一些无法启动或者无法ssh的问题时，可以尝试将问题VM的OS Disk创建snapshot，通过snapshot创建新的Recovery Disk。

2. 创建一台Dv3或者Ev3级以上配置的VM，与Recovery Disk的Region保持相同。安装Windows Server 2016+版本（支持nested virtualization），进入系统后开启Hyper-V功能和management tools: `Install-WindowsFeature -Name Hyper-V -IncludeManagementTools -Restart`

3. 将Recovery Disk挂载到此VM上，进入系统offline掉这个disk，然后用这个disk创建hyper-v虚拟机：

   - Computer management - disk management - offline
   - Hyper-V manager - New VM - attach a virtual hard disk later 

   - VM settings - IDE controller0 - hard drive - physical hard disk - apply

   - Get into console

4. 进入VM console之后就可以进行排错或者修复了

这种方式适合Guest Agent无法访问，或者需要重置本地密码等情况，相关文档：

[如何通过 Hyper-V Console 方式修复虚拟机无法访问的问题 | Azure Docs](https://docs.azure.cn/zh-cn/articles/azure-operations-guide/virtual-machines/aog-virtual-machines-howto-fix-ssh-or-rdp-issues-via-hyper-v-console)

[Nested Virtualization | Microsoft Docs](https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/user-guide/nested-virtualization)

[在 Windows Server |上安装 Hyper-V 角色微软文档 (microsoft.com)](https://docs.microsoft.com/en-us/windows-server/virtualization/hyper-v/get-started/install-the-hyper-v-role-on-windows-server)

[How to reset local Linux password on Azure VMs - Virtual Machines | Microsoft Learn](https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/linux/reset-password)

console如何进入单用户模式：[How to Boot into Single User Mode in CentOS/RHEL 7 (tecmint.com)](https://www.tecmint.com/boot-into-single-user-mode-in-centos-7/#:~:text=How to Boot into Single User Mode 1.,e key to edit the first boot option.)

## Mount os disk

当发现文件系统由于fstab的错误设置而被挂载为ro模式，无法修改内部文件的时候，在Hyper-V中进入启动引导模式不太好操作。此时可以采用workaround：将issueDisk以数据盘的形式挂载到一台VM上，mount到某个目录下，再打开里面的fstab进行修改。改完后再挂到nested VM里面进行其余操作

## mount disk+chroot

相关文档：[How to troubleshoot the chroot environment in a Linux Rescue VM - Virtual Machines | Microsoft Learn](https://learn.microsoft.com/en-us/troubleshoot/azure/virtual-machines/chroot-environment-linux#rhelcentosoracle-6x--oracle-8x--rhelcentos-7x-with-raw-partitions)

# Azure VMSS

VMSS是一组独立的VM的组合，是负载均衡的，可以根据用户的需求，自动增减VM instance，便于集中管理、配置、更新大量VM与手动创建相比，突出优势是自动化配置，自动负载均衡。适用于大规模计算任务。而且适合需求随时间变化大的任务，节省成本和时间。

[Azure virtual machine scale sets overview - Azure Virtual Machine Scale Sets | Microsoft Docs](https://docs.microsoft.com/en-us/azure/virtual-machine-scale-sets/overview)

[Azure 虚拟机规模集概述 - Azure Virtual Machine Scale Sets | Azure Docs](https://docs.azure.cn/zh-cn/virtual-machine-scale-sets/overview?toc=%2Farticles%2Fazure-operations-guide%2Ftoc.json)

![image-20250608100534712](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506081005945.png)

![image-20250608100552233](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506081005473.png)

## VMSS-Load Balancer

Load balancer工作在传输层，访问VMSS的方法：

- 为每个VM提供自己的公共IP，比较贵。

- 可以使用Load Balancer与NAT结合使用：

  - 系统将公共IP地址分配给LB，由LB将流量路由，通过每个VM的端口，分配到各个VM instance。 

  - 默认情况下，会将网络地址转换(NAT) 规则添加到LB，由后者将远程连接流量转发给给定端口上的每个VM。

## VMSS Auto-scale

[教程 - 使用 Azure CLI 自动缩放规模集 - Azure Virtual Machine Scale Sets | Azure Docs](https://docs.azure.cn/zh-cn/virtual-machine-scale-sets/tutorial-autoscale-cli)

[在 Azure 门户中自动缩放虚拟机规模集 - Azure 虚拟机规模集|微软文档 (microsoft.com)](https://docs.microsoft.com/en-us/azure/virtual-machine-scale-sets/virtual-machine-scale-sets-autoscale-portal)