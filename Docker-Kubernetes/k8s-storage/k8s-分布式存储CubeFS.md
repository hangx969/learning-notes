# 存储架构对比

## 单节点存储

一种常见但又失败的存储设计：一台存储服务器，挂载了很多磁盘，搭建一个nfs或者其他nas服务提供存储。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202508281559728.png" alt="image-20250828155935532" style="zoom:50%;" />

这种架构存在很多问题：

1. 单点故障，非高可用
   - 如果想再搭一台作为高可用，很难实时同步两台节点的数据；而且故障转移也很困难，大概率转移不过去。
2. 性能瓶颈，数据阻塞
   - 存储服务器的网卡成为网络数据流量的瓶颈，一般只有一个或者两个磁盘承载读写，也会成为瓶颈。
3. 存储有限，扩容复杂
4. 安全性低，容易宕机
5. 功能有限，只支持文件
   - 如果想实现块存储或者对象存储是不支持的
6. 隔离性差，无权限管理

## 分布式存储

生产环境中建议使用分布式存储。分布式存储有以下优势：

1. 支持近乎无限的扩容
   - 可以通过添加节点到集群的方式扩容
   - 扩容后集群会自动balance
2. 支持容错能力和数据冗余
   - 可以配置存储多份文件副本
   - 可以配置文件拆分成多份存储到不同节点上
3. 支持多机房多区域部署
4. 支持负载均衡和并行处理
   - 数据可以在多个节点并行处理，性能更好
5. 支持权限管理和多用户
6. 支持多种文件存储类型
   - 块存储（可以当做一块硬盘直接挂载到某台机器上或者容器内）、对象存储（s3、hadoop等协议）
7. 支持普通硬件设计
   - nfs存储性能就依赖于高性能磁盘，分布式存储可以通过缓存、中间件等，即使在普通硬件上也可以提高性能

## 分布式存储平台

主要对比主流的Ceph和CubeFS：

| 特性       | Ceph                                                         | CubeFS                                                       |
| ---------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 设计目标   | 统一存储解决方案，支持块、对象、文件存储                     | 专注于文件、对象存储                                         |
| 存储类型   | 对象、块、文件系统                                           | 对象、文件系统（目前不支持块存储）                           |
| 扩展性     | 支持超大规模集群，PB-EB级                                    | 支持大规模集群，但是针对中小规模场景优化更好                 |
| 性能       | 大文件性能优秀，小文件性能一般                               | 小文件和大文件性能均优秀                                     |
| 元数据管理 | 基于RADOS分布式存储，元数据分布在OSD中                       | 独立的Metadata节点管理元数据，避免瓶颈                       |
| 部署复杂度 | 需要配置多组件（Monitor、Manager、OSD等）维护比k8s还困难<br />直接部署到k8s较困难，而且对接K8s也需要其它工具支持 | 轻量级，部署简单，适合云原生环境                             |
| 硬件要求   | 对磁盘IO和网络带宽要求较高                                   | 硬件要求相对较低（企业级也要用高性能磁盘和万兆带宽）         |
| 社区活跃度 | 社区庞大、文档丰富、生态成熟                                 | 中文文档齐全（由OPPO开源的）                                 |
| 成熟度     | 技术成熟，已在生产环境中广泛使用                             | 较新的项目，生产环境验证时间较短                             |
| 使用场景   | 通用存储需求，企业级数据中心                                 | 云原生环境、大数据分析、AI训练、容器化等场景，有专门优化。   |
| 兼容性     | 支持多种协议（S3、iSCSI、NFS、HDFS等）                       | 支持多种协议，主要针对对象、文件存储                         |
| 扩展方式   | 水平扩展、支持动态扩展                                       | 水平扩展、支持动态扩展                                       |
| 容错机制   | 多副本嚯纠删码机制                                           | 多副本或纠删码机制（文件经常访问-多副本好一些；不经常访问-纠删码好一些） |

## k8s上落地分布式存储平台

裸机部署分布式存储平台，管理很复杂，而且对故障的承受能力也比较差。

在k8s上部署分布式存储平台，有如下优势：

1. 简化部署和管理
   - 不需要在每台机器上维护配置文件。用helm等工具在k8s上实现IaC，方便管理
2. 自动化运维
3. 一键式动态扩展
   - daemonset实现每个节点的配置相同
4. 故障自愈和高可用性
   - 健康检查、自动故障恢复漂移
5. 云原生生态集成
   - 云原生应用可以直接用CSI对接到存储

# CubeFS介绍

官网：[CubeFS | A Cloud Native Distributed Storage System](https://www.cubefs.io/zh/docs/master/overview/introduction.html)

CubeFS是新一代云原生存储产品，目前已经是CNCF毕业的开源项目。兼容S3、POSIX、HDFS等多种访问协议，支持多副本与纠删码两种存储引擎，提供多租户、多AZ部署以及跨区域复制等多种特性。广泛应用于大数据、AI、容器平台、数据库、中间件存算分离、数据共享以及数据保护等场景。

比如大模型服务，部署一个deepseek，671B的参数量，模型文件就得接近上TB。模型文件越多，对存储性能要求越高，放到CubeFS上，吞吐量很优秀，可以支持大模型服务。放到单节点存储上会拖慢大模型速度。

## 特性

1. 多协议：S3、POSIX、HDFS
2. 双引擎：支持多副本和纠删码
3. 多租户：支持多租户隔离和权限分配
4. 可扩展：支持各模块水平扩展、轻松扩展到PB或EB级
5. 高性能：支持多级缓存、支持多种高性能的复制协议。
6. 云原生：自带CSI插件，一键集成到k8s
7. 多场景：大数据分析、机器学习、深度训练、共享存储、对象存储、数据库中间件等。

## 架构

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202508281651643.png" alt="image-20250828165135446" style="zoom:50%;" />

1. Master Node：

   集群管理中枢和请求入口，管理其他节点，分发请求到其他节点

2. Meta Node：

   元数据节点，存储文件metadata：文件名称、存储状态、副本状态等。这些数据都是缓存到内存中的

3. Data Node:

   数据节点，真正存储数据的地方。如果采用副本模式就是Data Node；如果采用纠删码模式就是Blob Node。

4. Object Node：

   CubeFS也是支持S3协议的，object node对外提供s3协议，应用通过object node作为入口访问到对象存储。

# 企业级分布式存储架构设计

## 部署方式

### 混合部署

混合部署指的是已经有一个现成的k8s集群，已经部署了一些业务应用，再把分布式存储平台也部署上去。

不过是部署在特殊节点上，通过打污点的形式，不让其他应用pod部署上去。

对于CubeFS的挂载，应用可以通过Master节点的service来挂载，或者通过object node来挂载对象存储。

### 独立部署-基础设施集群

是企业中比较常见、典型、可靠的部署方式：

1. 把一些通用服务单独部署到基础设施集群中（比如CubeFS、prometheus、grafana、ECK等）
2. 应用业务单独部署在业务集群中

基础设施集群中的通用服务怎么对外提供服务？需要看服务是通过什么协议代理的：

1. 通过TCP四层协议代理的，比如mysql、redis：
   - 可以在两个集群中间加一个F5（负载均衡器）
   - 可以把服务通过NodePort暴露
2. 通过HTTP七层协议代理的
   - 可以通过ingress，暴露一个内部域名，只能内网去解析。如果没有内网域名，可以在业务集群的coreDNS上配置自定义解析，解析到基础设施集群的入口。
   - 也可以通过istio ingressGateway暴露域名。

## 资源分配建议

### 总内存

以CubeFS为例，元数据节点总内存计算规则：每个文件元数据占用空间2KB-4KB。

- 根据文件数量预估：
  - 假设已知的文件数量预估为10亿，则需要的内存KB为：20亿KB
  - 换算为GB：20亿/1024/1024 = 2000GB = 2TB内存

- 根据数据量预估：
  - 假设集群数据总量为10PB = 10240TB = 10737418240MB
  - 通过CubeFS默认分片大小8MB预估，可能需要10737418240/8=1342177280个文件
  - 通过计算规则，需要的内存为：1342177280*2 = 2684354560KB = 2500GB = 2.5TB

### 服务器硬件

假设需要落地1PB CubeFS存储（需要256G内存）。

常见的配置：一台16硬盘位的存储服务器：

- 每个硬盘位插一个16T的SAS硬盘（目前SAS盘性价比最高），这样一台存储服务器就有256T硬盘空间，四台就能满足1PB了。
- 四个内存槽，每个插上64G内存条，总共256G内存，四台服务器就有约1TB内存了，远超需求量。（内存一般来说是容易满足的，而且服务器内存条也比较便宜，不会成为瓶颈）

如果担心16盘位受到服务器故障影响较大，可以换成8盘位的服务器：

- 每个硬盘位插一个16T的SAS硬盘，8台可以满足1PB。
- 内存槽4个，每个槽插一个32G内存条，8台也是1TB内存，足够用。

所以就把服务器盘位、硬盘容量规划好就行，内存一般不会成为瓶颈。

# CubeFS部署

## 部署架构

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202508281805748.png" alt="image-20250828180510573" style="zoom:50%;" />

- `Master`：资源管理节点，负责维护整个集群的元信息，部署为 StatefulSet 资源。
- `DataNode`：数据存储节点，需要挂载大量磁盘负责文件数据的实际存储，部署为 DaemonSet 资源。
- `MetaNode`：元数据节点，负责存储所有的文件元信息，部署为 DaemonSet 资源。
- `ObjectNode`：负责提供转换 S3 协议提供对象存储的能力，无状态服务，部署为 Deployment 资源。

## 配置标签

CubeFS 安装时会根据这些标签通过`nodeSelector`进行匹配，然后在机器创建起对应的`Pod`。

实验环境下就三个节点，所有节点都用做所有三个角色：

~~~sh
# Master 节点，至少三个，建议为奇数个 
kubectl label node component.cubefs.io/master=enabled --all
# MetaNode 元数据节点，至少 3 个，奇偶无所谓 
kubectl label node component.cubefs.io/metanode=enabled --all
# Dataode 数据节点，至少 3 个，奇偶无所谓 
kubectl label node component.cubefs.io/datanode=enabled --all
# ObjectNode 对象存储节点，可以按需进行标记，不需要对象存储功能的话也可以不部署这个组件 
kubectl label node component.cubefs.io/objectnode=enabled --all
~~~

## 配置数据盘

搭建分布式存储，是需要专门挂载磁盘的。

在配置了`kubectl label node <nodename> component.cubefs.io/datanode=enabled`的数据节点上，对数据盘进行初始化操作。

首先添加一个新盘，然后通过fdisk -l查看：

~~~sh
fdisk -l | grep dev/sd
# Disk /dev/sdb: 6 GiB, 6442450944 bytes, 12582912 sectors
~~~

格式化磁盘并挂载：

~~~sh
# 格式化硬盘 
mkfs.xfs -f /dev/sdb 
# 创建挂载目录，如果机器上存在多个需要挂载的数据磁盘，则每个磁盘按以上步骤进行格式化和挂载磁盘，挂载目录按照data0/data1/../data999的顺序命名 
mkdir /data0 
# 挂载磁盘 
mount /dev/sdb /data0 

# 开机自动挂载
blkid /dev/sdb # 获取磁盘UUID
vim /etc/fstab 
UUID=1c6fa33b-2901-4a9b-8c8c-ea70f265e26d   /data0   xfs    defaults  0 0
mount -a 
~~~

> 注意：如果有多个数据节点，需要保证每个数据节点的磁盘数量、大小等配置是完全一致的。因为后面配置数据节点的时候，是所有数据节点统一配置的。这样出错的概率小。

## helm安装

官网指南：[CubeFS | A Cloud Native Distributed Storage System](https://www.cubefs.io/zh/docs/master/deploy/k8s.html)

github地址：[cubefs/cubefs-helm: The cubefs-helm project helps deploy a CubeFS cluster orchestrated by Kubernetes.](https://github.com/cubefs/cubefs-helm)

### 下载helm包

~~~sh
git clone https://github.com/cubefs/cubefs-helm.git
~~~

### 配置values

#### 组件和镜像

~~~yaml
# 临时关闭一些组件 
cd cubefs-helm/cubefs 
vim values.yaml 
  client: false 
  csi: false 
  monitor: false 
  ingress: false 
# 调整组件的镜像地址（如果报错说明镜像源还不支持这些新版镜像，还是用默认的，手动传到节点解压）
image: 
  server: m.daocloud.io/docker.io/cubefs/cfs-server:v3.4.0 
  client: m.daocloud.io/docker.io/cubefs/cfs-client:v3.4.0 
  blobstore: m.daocloud.io/docker.io/cubefs/blobstore:v3.4.0 
  csi_driver: m.daocloud.io/docker.io/cubefs/cfs-csi-driver:v3.4.0 
  csi_provisioner: m.daocloud.io/registry.k8s.io/sig-storage/csi-provisioner:v2.2.2 
  csi_attacher: m.daocloud.io/registry.k8s.io/sig-storage/csi-attacher:v3.4.0 
  csi_resizer: m.daocloud.io/registry.k8s.io/sig-storage/csi-resizer:v1.3.0 
  driver_registrar: m.daocloud.io/registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.5.0 
  grafana: m.daocloud.io/docker.io/grafana/grafana:6.4.4 
  prometheus: m.daocloud.io/docker.io/prom/prometheus:v2.13.1 
  consul: m.daocloud.io/docker.io/library/consul:1.6.1 
~~~

#### 主节点配置

~~~yaml
# 主节点副本数，建议奇数 
master: 
  replicas: 3
  tolerations:
    - key: "node-role.kubernetes.io/control-plane"
      operator: "Equal"
      effect: "NoSchedule"
# 资源请求： 
  resources:
    enabled: true
    requests: 
      memory: "256Mi" 
      cpu: "200m" 
    limits: 
      memory: "2Gi" 
      cpu: "2000m" 
# 生产环境建议： 
    requests: 
      memory: "8Gi" 
      cpu: "2000m" 
    limits: 
      memory: "32Gi" 
      cpu: "8000m"
~~~

#### 元数据节点配置

~~~yaml
metanode: 
  # metanode可用的内存，建议主机内存的80% 
  total_mem: "7516192768" # 这里配置7G
# 资源配置 
  resources:
    enabled: true
    requests: 
      memory: "256Mi" 
      cpu: "200m" 
    limits: 
      memory: "2Gi" 
      cpu: "2000m" 
# 生产环境建议 
  resources:
    enabled: true
    requests: 
      memory: "32Gi" 
      cpu: "2000m" 
    limits: 
      memory: "256Gi" # 要比上面的total_mem的值稍微大一些。比如上面配置了128G，这里配置132G。给一些buffer
      cpu: "8000m" 
~~~

#### 数据节点配置

~~~yaml
# 数据盘配置 
# datanode.disks字段用于配置数据的挂载点，同时可以为每个磁盘保留一定的空间 
  disks: 
    # 默认是给磁盘预留20G空间防止爆盘 - /data0:2147483648
    - /data0:536870912 # 这里给了0.5G
# 资源配置：
  resources:
    enabled: true
    requests: 
      memory: "256Mi" 
      cpu: "200m" 
    limits: 
      memory: "2Gi" 
      cpu: "2000m" 
# 生产环境建议 
    requests: 
      memory: "8Gi" 
      cpu: "2000m" 
    limits: 
      memory: "32Gi" 
      cpu: "8000m" 
~~~

#### 对象存储节点配置

~~~yaml
objectnode: 
  # 对象存储的域名 
  region: "spark" 
# 对象存储的域名。公司内部有域名就用，没有就用这个默认的。
domains: "objectcfs.cubefs.io,objectnode.cubefs.io" 
~~~

### 安装CubeFS

~~~sh
cd ./cubefs-helm/cubefs
helm upgrade --i cubefs -n cubefs --create-namespace . 
~~~

> 2025-08-28 安装的3.3.2.150.0 Release版本，有个bug：
>
> 在`cubefs-helm/cubefs/templates/statefulset-master.yaml`文件的第80行，需要把：
>
> `value: {{ .Value.master.legacy_data_media_type | quote }}` 他的Value加上s：
>
> `value: {{ .Values.master.legacy_data_media_type | quote }}`
>
> 否则会报错：Error: template: cubefs/templates/statefulset-master.yaml:80:30: executing "cubefs/templates/statefulset-master.yaml" at <.Value.master.legacy_data_media_type>: nil pointer evaluating interface {}.master

如果遇到启动失败的，可以在对应的节点上，查看/var/log/cubefs下的日志。

## CubeFS客户端部署

~~~sh
https://github.com/cubefs/cubefs/releases/ 
tar xf cubefs-3.5.0-linux-amd64.tar.gz 
cd build/bin 
~~~

