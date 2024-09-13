# 测试网络连通性命令

## psping

tcp连接，测试端口开没开：[PsPing - Sysinternals | Microsoft Learn](https://learn.microsoft.com/en-us/sysinternals/downloads/psping)

psping <source machine_ip>: 443 和 9443 

## telnet

```bash
虚拟机连不上，可以用telnet来看一下端口可达性
telnet 168.63.129.16 80
```

## nc

测试tcp连接 

```bash
nc -vz mcr.azk8s.cn 443
-z：Zero-I/O mode, report connection status only
-v, --verbose Set verbosity level (can be used several times)
```

## dig

dig（域信息搜索器）命令是一个用于询问 DNS 域名服务器的灵活的工具。它执行 DNS 搜索，显示从受请求的域名服务器返回的答复。

```bash
dig mcr.azk8s.cn 443
dig mcr.azk8s.cn 
```

Dig工具使用：

- @来指定域名服务器、
- -t 指定要解析的类型

- A 为解析类型 ，A记录：解析域名到IP

```bash
dig -t A svc-sts-nginx.default.svc.cluster.local @10.0.0.10
```

## curl

- 测试连接外网连通性。不带有任何参数时，curl 就是发出 GET 请求。
  - curl myip.ipip.net（只能说明对外网访问没问题）

![image-20231030202611975](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310302026034.png)

- curl ipconfig.me：也能查看本机IP

## siege 

- 可以产生持续的访问请求，用于压测。

```bash
siege -c 15 -t 20m https://fibonnodeis.chinacloudsites.cn
```

## tcpdump

1. 网络包收集，Linux平台我们通常使用tcpdump进行收集，方法如下

```bash
tcpdump -i any host <Pod-IP> -C 10 -W 10 -w 31983.pcap
#<Pod-IP> 需修改为Pod的IP地址，作为过滤条件。
#-C是每个文件大小的上限，以M为单位。
#-W是最多写入多少个抓包文件，编号从0开始，到9写满后，从0号文件开始循环写。
#也就是说上述指令在抓包时最多会占用大约10 *10 = 100M的磁盘空间，您可以根据实际情况进行配置
#考虑到网络包通常都很大，所以我们应该需要设置一个监控脚本来监控应用日志，如果发现应用日志有相关报错，我们可以kill掉tcpdump的收集进程
```

## windows抓网络包

1. 使用管理员权限打开cmd，然后运行如下命令，其中C:\temp\netshtrace.etl是文件保存路径

   ```bash
   netsh.exe trace start capture=yes maxsize=500M overwrite=yes tracefile=C:\temp\netshtrace.etl
   ```

   ![image-20231030203953076](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310302039136.png)

2. 复现问题

3. 运行如下命令停止抓包

   ```bash
   netsh.exe trace stop
   ```

![image-20231030204052140](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310302040199.png)

# Azure Networking

## VNET

- VNet 允许许多类型的 Azure 资源（例如 Azure 虚拟机 (VM)）以安全方式彼此通信、与 Internet 通信，以及与本地网络通信。

  From <https://docs.azure.cn/zh-cn/virtual-network/virtual-networks-overview>

- 虚拟网络是通过互联网在设备、服务器、虚拟机之间进行的通信。同样，Azure 虚拟网络 （VNet） 是一个专用网络，具有互连的 Azure 资源，如 Azure 虚拟机、基础结构和网络。它支持通过 Internet 在各种 Azure 资源之间进行通信。在虚拟网络中，连续的 IP 地址块用于创建多个子网网络。From <https://k21academy.com/microsoft-azure/az-303/azure-networking/>

- 当VNET里面的资源没有Public IP的时候，能访问Internet吗？
  - 答案：YES。通过Private IP，通过VNET向外发送数据的时候，会用NAT将Private IP转换为Public IP，照样访问。入站流量也会将NAT转换为Private IP

## Public IP 和 Private IP

- **专用** – 专用 IP 地址允许在 Azure资源组中通信资源。换句话说，资源无法访问网络外部的专用 IP。可以使用专用地址连接的资源包括 VM 网络接口、ILB（内部负载均衡器）和应用程序网关。
- **公共** – 公共 IP 地址允许 Azure资源通过 Internet 与面向公众的 Azure 服务进行通信。换句话说，资源可以访问网络外部的公共 IP。可以使用公共地址连接的一些资源包括VM 网络接口、面向公众的 ILB、应用程序网关、VPN 网关和 Azure 防火墙。

From <https://k21academy.com/microsoft-azure/az-303/azure-networking/>

## Subnet

- 众所周知，子网是覆盖一系列 IP 地址的网络的一部分。在 Azure 中，VNet 可以划分为组织的较小子网。在 Azure 中创建 VNet 时，需要指定子网范围和拓扑。在“子网”中，“IP 地址”范围将是虚拟网络 （VNet） 中使用的一大块 IP 地址的子部分。将为网络中的虚拟机和资源分配这些子网中的 IP 地址。

- Azure会在每个子网中保留前四个IP和最后一个IP以供自己使用

From <https://k21academy.com/microsoft-azure/az-303/azure-networking/> 

## NSG

- 网络安全组在网络级别充当防火墙。它会筛选通过虚拟网络中的 Azure 资源传递的流量。NSG 是一组安全规则，用于定义优先级、源或目标、协议、方向、端口范围和操作。使用这些规则，NSG 允许或拒绝入站和出站流量。

From <https://k21academy.com/microsoft-azure/az-303/azure-networking/>

## 网关

- 网关实质上是一个网络通向其他网络的IP地址。

- 比如有网络A和网络B，网络A的IP地址范围为 “192.168.1.1~192. 168.1.254”，子网掩码为255.255.255.0;网络B的IP地址范围为“192.168.2.1~192.168.2.254”，子网掩 码为255.255.255.0。在没有路由器的情况下，两个网络之间是不能进行TCP/IP通信的，即使是两个网络连接在同一台交换机(或集线器) 上，TCP/IP协议也会根据子网掩码(255.255.255.0)判定两个网络中的主机处在不同的网络里。

- 而要实现这两个网络之间的通信，则必须通过网关。如果网络A中的主机发现数据包的目的主机不在本地网络中，就把数据包转发给它自己的网关，再由网关转发给网络B的网关，网络B的网关再转发给网络B的某个主机。网络B向网络A转发数据包的过程也是如此。
- 所以说，只有设置好网关的IP地址，TCP/IP协议才能实现不同网络之间的相互通信。
- 那么这个IP地址是哪台机器的IP地址呢? 网关的IP地址是具有路由功能的设备的IP地址，具有路由功能的设备有路由器、启用了路由协议的服务器(实质上相当于一台路由器)、代理服务器(也相当于一台路由器)!

## Azure Relay

[什么是 Azure 中继？ - Azure Relay | Azure Docs](https://docs.azure.cn/zh-cn/azure-relay/relay-what-is-it)

## Private and service endpoint

Azure 中的专用终结点（Private Endpoint）和服务终结点（Service Endpoint）都可以用于加强安全性和控制网络访问。它们的区别在于：

1. 定义和范围：专用终结点是针对单个 Azure 资源（例如虚拟机、存储帐户等）的，而服务终结点是针对服务标识符（例如 Azure 存储、Azure SQL 数据库等）的。
2. 网络路径：专用终结点通过在 VNet 中创建一个专用 IP 地址，将 Azure 资源直接连接到 VNet 中的子网。这样，资源就可以通过 VNet 的私有 IP 地址进行访问，而无需通过公共 Internet。服务终结点则是通过 Azure 资源的虚拟网络服务终结点连接到服务标识符。
3. 安全性：专用终结点通过将网络流量限制为 Azure 资源的专用 IP 地址来提高安全性。服务终结点通过将网络流量限制为特定服务的 IP 地址范围来提高安全性。在访问受服务终结点保护的服务时，如果网络流量来自未经授权的 IP 地址，则服务将被拒绝。

综上所述，专用终结点和服务终结点都是提高安全性和控制网络访问的重要工具。选择使用哪种终结点取决于需要保护的资源类型和服务类型。

- 存储账户配置了private endpoint的时候，如果从subnet内访问，那么azure dns也先去解析公共终结点（例如artifactorysa.file.core.chinacloudapi.cn），通过cname记录解析到private endpoint（例如artifactorysa.privatelink.file.core.chinacloudapi.cn），再由private endpoint解析成内网IP。
- 自己本地DNS需要设置把公共终结点forward到azure dns上来做解析。或者直接在/etc/hosts上把公共终结点配置为终结点的私有IP

## Loadbalancer

- Load balancer 工作在传输层 

- 访问VMSS的方法：

  - 为每个VM提供自己的公共IP，比较贵

  - 可以使用Load Balancer 与 NAT结合使用：
    - 系统将公共 IP 地址分配给LB，由LB将流量路由，通过每个VM的端口，分配到各个VM instance。 
    - 默认情况下，会将网络地址转换(NAT) 规则添加到LB，由后者将远程连接流量转发给给定端口上的每个 VM。

## VM内网访问方案

多台虚拟机都分配公网Ip的风险是容易被端口扫描，暴力破解

- 方案1：
  - VNET里面部署很多台VM，但只有一台跳板机开了公网IP，通过这一台的网卡来连到其他虚拟机的网卡，来访问其他虚拟机。

- 方案2：
  - 公司内网和VNET，两边搭gateway，通过VPN来连到虚拟机

- 方案3：
  - 直接买专线，内网到数据中心专线访问。