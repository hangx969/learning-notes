# Calico基础

- Calico是一个开源的网络和安全解决方案，它为容器、虚拟机、主机、k8s提供了高效、可扩展和安全的网络连接和策略管理。

- Calico在K8s中的功能：

  1）支持网络隔离和多租户场景；

  2）为pod提供独立的IP地址；

  3）支持跨主机的容器通信，pod可以通过IP地址直接互相访问；

  4）提供网络安全策略，支持网络流量控制和访问授权，实现网络安全隔离。

## 架构图

![image-20231023152017200](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310241222817.png)

## Calico主要工作组件

1. Felix：运行在每一台 Host 的 agent 进程，主要负责网络接口管理和监听、路由、ARP 管理、ACL 管理和同步、状态上报等。保证跨主机容器网络互通。
2. etcd：分布式键值存储，相当于k8s集群中的数据库，存储着Calico网络模型中IP地址等相关信息。主要负责网络元数据一致性，确保 Calico 网络状态的准确性；

3. BGP Client（BIRD）：Calico 为每一台 Host 部署一个 BGP Client，即每台host上部署一个BIRD。 主要负责把 Felix 写入 Kernel 的路由信息分发到当前 Calico 网络，确保 Workload 间的通信的有效性；

4. BGP Route Reflector：在大型网络规模中，如果仅仅使用 BGP client 形成 mesh 全网互联的方案就会导致规模限制，因为所有节点之间俩俩互联，需要 N^2 个连接，为了解决这个规模问题，可以采用 BGP 的 Router Reflector 的方法，通过一个或者多个 BGP Route Reflector 来完成集中式的路由分发。 

## calico配置文件

### Daemonset配置

```yaml
...
containers:
        # Runs calico-node container on each Kubernetes node. This container programs network policy and routes on each host.
        - name: calico-node
          image: docker.io/calico/node:v3.18.0
……
          env:
          # Use Kubernetes API as the backing datastore.
           - name: DATASTORE_TYPE
             value: "kubernetes"
          # Cluster type to identify the deployment type
           - name: CLUSTER_TYPE
             value: "k8s,bgp"
          # Auto-detect the BGP IP address.
           - name: IP
             value: "autodetect"
          #pod网段
           - name: CALICO_IPV4POOL_CIDR 
             value: "10.244.0.0/16"
          # Enable IPIP
           - name: CALICO_IPV4POOL_IPIP
             value: "Always"
```

### calico-node服务的主要参数:

- CALICO_IPV4POOL_IPIP：

  - IP Pool可以使用两种模式：BGP或IPIP。使用IPIP模式时，设置CALICO_IPV4POOL_IPIP="Always"，不使用IPIP模式时，设置CALICO_IPV4POOL_IPIP="Off"，此时将使用BGP模式。
  - 启用IPIP模式时，Calico将在Node上创建一个名为tunl0的虚拟隧道。

- IP_AUTODETECTION_METHOD：

  - 获取Node IP地址的方式，默认使用第1个网络接口的IP地址，对于安装了多块网卡的Node，可以使用正则表达式选择正确的网卡，例如"interface=eth.*"表示选择名称以eth开头的网卡的IP地址。

    ```yaml
    -  name: IP_AUTODETECTION_METHOD #位置:在calico.yaml-DaemonSet:Containers:env里面配置
       value: "interface=ens33"
    ```

  - 在安装 Calico 网络插件时，指定 IP_AUTODETECTION_METHOD 环境变量是为了确保该插件能够在正确的网络接口上自动检测 Pod IP 地址。这个环境变量的值 "interface=ens33" 指定了 Calico 插件使用 ens33 接口来分配 IP 地址给 Kubernetes Pod，而不是使用默认的自动检测方式。

  - 通常情况下，Kubernetes Pod 中容器的 IP 地址是由容器运行时（如 Docker 或 CRI-O）自动分配的。但是，对于某些网络插件（如 Calico）来说，为了能够正确地配置网络，需要手动指定使用哪个网络接口来自动检测 Pod IP 地址。

  - 因此，在安装 Calico 网络插件时，需要通过 IP_AUTODETECTION_METHOD 环境变量来指定使用 ens33 接口来分配 IP 地址给 Kubernetes Pod。这样可以确保 Calico 插件能够正确地配置 Pod 网络。

## Calico支持的网络模式对比分析

- IPIP

  - 使用 IPIP 封装技术进行数据传输，每个节点需要分配两个 IP 地址，一个是节点 IP 地址，另一个是虚拟节点 IP 地址。相较于 BGP 模式，IPIP 模式的配置更加简单，但是性能和路由协议的稳定性会受到一定影响。
  - 把一个IP数据包又套在一个IP包里，即把IP层封装到IP层的一个 tunnel，它的作用其实基本上就相当于一个基于IP层的网桥，一般来说，普通的网桥是基于mac层的，根本不需要IP，而这个ipip则是通过两端的路由做一个tunnel，把两个本来不通的网络通过点对点连接起来；
  - calico以ipip模式部署完毕后，node上会有一个tunl0的网卡设备，这是ipip做隧道封装用的,也是一种overlay模式的网络。当我们把节点下线，calico容器都停止后，这个设备依然还在，执行 rmmodipip命令可以将它删除。

- BGP

  - 使用 BGP 协议作为路由协议，每个节点会分配一个全局唯一的 IP 地址，可以支持跨 VPC 或者跨云的网络互通。
  - BGP模式直接使用物理机作为虚拟路由路（vRouter），不再创建额外的tunnel

  > - 边界网关协议（BorderGateway Protocol, BGP）是互联网上一个核心的去中心化的自治路由协议。它通过维护IP路由表或‘前缀’表来实现自治系统（AS）之间的可达性，属于矢量路由协议。BGP不使用传统的内部网关协议（IGP）的指标，而是基于路径、网络策略或规则集来决定路由。因此，它更适合被称为矢量性协议，而不是路由协议，通俗的说就是将接入到机房的多条线路（如电信、联通、移动等）融合为一体，实现多线单IP；
  > - BGP 机房的优点：服务器只需要设置一个IP地址，最佳访问路由是由网络上的骨干路由器根据路由跳数与其它技术指标来确定的，不会占用服务器的任何系统；

- 官方提供的calico.yaml模板里，默认打开了ip-ip功能，该功能会在node上创建一个设备tunl0，容器的网络数据会经过该设备被封装一个ip头再转发。

  - 这里，calico.yaml中通过修改calico-node的环境变量：CALICO_IPV4POOL_IPIP来实现ipip功能的开关：默认是Always，表示开启；Off表示关闭ipip。

```yaml
- name:  CLUSTER_TYPE
  value: "k8s,bgp"
  # Auto-detect the BGP IP address.
- name: IP
  value: "autodetect"
  # Enable IPIP
- name: CALICO_IPV4POOL_IPIP
  value: "Always"
```

- VXLAN模式
  - 使用 VXLAN 封装技术进行数据传输，与 IPIP 模式类似，需要为每个节点分配两个 IP 地址，但是 VXLAN 模式相较于 IPIP 模式的性能更好。
- hostgateway模式
  - 将每个节点的主机网络接口作为网关来进行数据传输，不需要额外的 IP 地址分配，但是节点之间的网络互通会受到主机网络接口的限制。
- 总结：
  - calico BGP通信是基于TCP协议的，所以只要节点间三层互通即可完成，即三层互通的环境bird就能生成与邻居有关的路由。但是这些路由和flannel host-gateway模式一样，需要二层互通才能访问的通，因此如果在实际环境中配置了BGP模式生成了路由但是不同节点间pod访问不通，可能需要再确认下节点间是否二层互通。
  - 为了解决节点间二层不通场景下的跨节点通信问题，calico也有自己的解决方案——IPIP模式.

## 配置IPIP模式

~~~yaml
在calico.yaml文件中找到以下内容：
# Disable IPIP tunneling. (required on Azure)
# - name: CALICO_IPV4POOL_IPIP
# value: "Never“
将注释去掉，并将value修改为"CrossSubnet"，表示启用IPIP模式。
~~~

## 配置BGP模式

~~~yaml
在calico.yaml文件中找到以下内容：
# Enable BGP. (required to enable bird)
# - name: CALICO_IPV4POOL_CIDR
# value: "192.168.0.0/16"
# - name: CALICO_IPV4POOL_IPIP
# value: "CrossSubnet"
# - name: CALICO_NETWORKING_BACKEND
# value: "bird"
将注释去掉，并将CALICO_IPV4POOL_CIDR修改为当前网络的CIDR地址，CALICO_IPV4POOL_IPIP修改为
"CrossSubnet"，CALICO_NETWORKING_BACKEND修改为"bird"，表示启用BGP模式。
~~~

> 备注：当CALICO_IPV4POOL_IPIP被设置为“CrossSubnet”时，Calico可以为不同子网中的节点创建IPIP隧道，以便它们可以通过隧道相互通信。在 BGP 模式下，IPIP 仍然是 Calico 网络的一部分，用于支持 Kubernetes 网络的内部通信，因此仍需要设置CALICO_IPV4POOL_IPIP 参数。设置为 “CrossSubnet” 表示启用 IPIP 模式，且IPIP 模式的隧道可以跨越多个子网，而不仅仅是在同一子网内（子网值物理机网络）。这有助于支持更大规模的Kubernetes 网络，其中节点分布在多个子网中。

## 配置VXLAN模式

~~~yaml
在calico.yaml文件中找到以下内容：
# Enable VXLAN encapsulation mode. (required to enable host-gw and vxlan)
# - name: CALICO_IPV4POOL_IPIP
# value: "CrossSubnet"
# - name: CALICO_NETWORKING_BACKEND
# value: "vxlan“
将注释去掉，并将CALICO_IPV4POOL_IPIP修改为"CrossSubnet"，CALICO_NETWORKING_BACKEND修改为
"vxlan"，表示启用VXLAN模式。
~~~

## 配置host-gw模式

~~~yaml
在calico.yaml文件中找到以下内容：
# Enable host gateway mode. (required to enable host-gw and vxlan)
# - name: CALICO_IPV4POOL_IPIP
# value: "CrossSubnet"
# - name: CALICO_NETWORKING_BACKEND
# value: "hostgw“
将注释去掉，并将CALICO_IPV4POOL_IPIP修改为"CrossSubnet"，CALICO_NETWORKING_BACKEND修改为
"hostgw"，表示启用host-gw模式。
~~~

## 安装calico-deployment部署

1. 从官网找到最新版calico的yaml链接：https://docs.tigera.io/calico/latest/getting-started/kubernetes/self-managed-onprem/onpremises#install-calico
2. 下载yaml文件部署

# 其他常用网络插件

1、Flannel：是一个轻量级的 CNI 插件，使用 VXLAN 技术来实现网络的通信和隔离，适用于小规模集群。它使用iptables来实现NAT，支持多种后端存储，包括 etcd、consul、zookeeper等。

2、Calico：是一个完全基于BGP协议的CNI插件，可以实现高性能和高扩展性的网络功能。Calico使用了IPIP、BGP和VXLAN技术，可以轻松扩展网络规模。它还支持网络安全策略、网络流量策略和网络监控等功能。

3、Weave Net：是一个简单易用的CNI插件，使用虚拟路由和Overlay网络实现容器之间的通信和隔离。它提供了一种快速、可靠和可扩展的解决方案，并支持多云环境。

4、Cilium：是一个支持L3、L4和L7网络安全的CNI插件，具有网络和安全功能集成，使用eBPF技术，可以实现更好的性能和可观测性。

> 对于小规模的Kubernetes集群，Flannel和Weave Net比较适合，而对于大规模的集群，Calico、Cilium则是一个更好的选择。

