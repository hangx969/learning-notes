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

### Wire server

guest agent通过wire server与host agent通信。有关wire server文档：

[What is IP address 168.63.129.16? | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/what-is-ip-address-168-63-129-16)

[Azure Instance Metadata Service for virtual machines - Azure Virtual Machines | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service?tabs=windows)

![image-20250607220207319](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072202559.png)

## VM ARM部署的过程

SRP、CRP、NRP等分别创建对应的资源

![image-20250607220511709](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072205194.png)

## VM Reginal Code

- China North：bjb

- China North2：bjb2

- China East：sha

- China East2：sha2

# Azure VM基础知识

## VM SKU命名规则

![image-20250607220348948](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202506072203223.png)

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