# 架构和组件

## AKS使用的container runtime

[Cluster configuration in Azure Kubernetes Services (AKS) - Azure Kubernetes Service | Microsoft Docs](https://docs.microsoft.com/en-us/azure/aks/cluster-configuration)

![image-20231031091153864](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310310911624.png)

## AKS集群的组成

![image-20231031091235694](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310310912766.png)

![image-20231031091357813](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310310913878.png)

### 控制平面

由Azure管理，组件：

| apiserver  | 集群对外的统一入口，以RESTful  API方式做操作。提供认证、授权、API注册和发现等机制 |
| ---------- | ------------------------------------------------------------ |
| scheduler  | 负责集群资源调度，按照预定的调度策略将Pod调度到相应的node节点上 |
| etcd       | 负责存储集群中各种资源对象的信息                             |
| controller | 负责维护集群的状态，比如程序部署安排、故障检测、自动扩展、滚动更新等 |

### 节点

由用户管理，组件：

| kubelet           | master派到node节点的代表，负责维护容器的生命周期，即通过控制docker，来创建、更新、销毁容器 |
| ----------------- | ------------------------------------------------------------ |
| kubeproxy         | 维护node的网络代理，管理服务和IP，实现负载均衡等操作         |
| container runtime | 运行容器的软件，负责镜像管理和POD的运行。  如果 AKS 群集使用适用于 Linux 节点池的 Kubernetes 1.19 版及更高版，则这些群集使用 **containerd** 作为它们的容器运行时。 从 1.20 版开始，可在预览版中使用 **containerd** 作为容器运行时，**Docker** 仍是默认的容器运行时。 |

- 在 AKS 中，群集的节点的 VM  映像基于 Ubuntu Linux 或 Windows Server 2019 

## 资源预留

- AKS需要占用节点VM中的资源来实现集群管理，应注意节点资源可能会少于VM的总资源，可以查看可分配的资源：

  kubectl describe node [NODE_NAME]

- 规则

  - 节点越大，意味着管理难度越大，所以预留的资源也就相应的增加。

  - 定义资源时，定义requests 和 limits两种属性，分别是调度和最大。部署的时候是docker来实现对容器的限制（cgroup）

  - 预留以下两种资源：

    - CPU

      - CPU的资源单位是millicores，是CPU时间，1000m代表将CPU时间分为1000份，分给某个容器。

      - 主机内核增加，预留的资源就增加。

    - 内存

      - 单位 Mi = 1024 * 1024 （1024进制）

      - kubelet守护程序

        node至少要有750Mi内存，少于这个数，就会杀掉POD了。

        为kubelet 守护程序正常运行而预留 (kube-reserved) 的内存的递减速率。

        实行阶梯预留：

        - 前 4 GB 内存的 25%

        - 下一个 4 GB 内存的 20%（最多     8 GB）

        - 下一个 8 GB 内存的 10%（最多     16 GB）

        - 下一个 112 GB 内存的     6%（最多 128 GB）

        - 128 GB 以上任何内存的 2%

举例：

如果一个节点提供 7 GB 内存，它会报告 34% 的内存不可分配，包括 750Mi 硬逐出阈值：0.75 + (0.25*4) + (0.20*3) = 0.75GB + 1GB + 0.6GB = 2.35GB / 7GB = 33.57% reserved

- 对比CPU和内存

  - CPU是可压缩资源，当可压缩资源不足时，服务会性能下降，并不会因此异常退出
  - 内存是不可压缩资源，当内存资源不足时，服务会OOM被kill掉

  - CPU和内存的单位官网详解：[Pod 和容器的资源管理|Kubernetes](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#meaning-of-cpu)

Q:limit可以超过100%？

## 节点池

- 一个集群至少包含一个节点池。节点池分为用户节点池和系统节点池，（至少有一个系统节点池）。

- 创建节点池后，VM的size无法再改变。想要加入不同size的VM，可以新建节点池。

### VMSS/VMAS

VMAS based: [az aks | Microsoft Learn](https://learn.microsoft.com/en-us/cli/azure/aks?view=azure-cli-latest#az-aks-create-examples)

```bash
az aks create -g hangvmasaks-RG -n hangvmasaks --kubernetes-version 1.24.9 --vm-set-type AvailabilitySet -l chinaeast2
```

(如果是使用可用性集的集群只能使用一个node pool，并且无法直接将可用性集集群转换为VMSS，需要重建AKS cluster选择使用VMSS再迁移应用。另外，我们不建议您手动更改可用性集中VM的配置或大小，这会使AKS集群内的配置与实际VMAS上的配置不符，从而导致AKS运行异常)

### AKS-Engine

使用 [AKS 引擎](https://github.com/Azure/aks-engine)在 Azure 上托管的自托管 Kubernetes 群集。

### latest model

- AKS所使用的VMSS资源由AKS服务自动管理，您只需要确保AKS版本处于支持范围内，不需要担心VMSS instance是否是latest model。AKS服务会在需要的时候更新现有VMSS实例的模型，如在集群版本升级或更新AKS节点镜像时。VMSS实例的是否处于latest model只是指当前实例配置和VMSS的期望配置之间是否有差别，不会影响AKS中工作负荷的正常运行。VMSS不要求所有实例都随时运行在最新模型上。AKS服务可以根据您的需求，比如在升级集群版本或更新节点镜像时，使实例应用最新模型。

- 手动更新到latest model

  如果某一个VM的latest model显示为no，如何变为yes？

  如果升级模式为手动模式，则VMSS属性发生更改后，需要对每一个VMSS instance手动更新一下信息。

  方法请参考：[修改 Azure 虚拟机规模集 - Azure Virtual Machine Scale Sets | Microsoft Docs](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.microsoft.com%2Fzh-cn%2Fazure%2Fvirtual-machine-scale-sets%2Fvirtual-machine-scale-sets-upgrade-scale-set%23how-to-bring-vms-up-to-date-with-the-latest-scale-set-model&data=05|01|hangx%40microsoft.com|ec5e6c14baa84a6a04a808da64bc4b42|72f988bf86f141af91ab2d7cd011db47|1|0|637933057333114597|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=IFFax1x2l7tXV9gSqJufJG3mJxWqiQ%2Fy%2BEeMG259QJY%3D&reserved=0)

## 资源组

### AKS创建两个资源组

[有关 Azure Kubernetes 服务 (AKS) 的常见问题解答 - Azure Kubernetes Service | Azure Docs](https://docs.azure.cn/zh-cn/aks/faq#why-are-two-resource-groups-created-with-aks)

为什么使用 AKS 创建两个资源组？

- AKS 在多个 Azure 基础结构资源之上构建，包括VMSS、虚拟网络和托管磁盘。 这使你能够在 AKS 提供的托管 Kubernetes 环境中利用 Azure 平台的许多核心功能。

为了启用此体系结构，每个 AKS 部署跨越两个资源组：

第一个资源组（自己命的名）

- 此组仅包含 Kubernetes     服务资源。 在部署过程中，AKS 资源提供程序会自动创建第二个资源组。 例如，第二个资源组为     MC_myResourceGroup_myAKSCluster_chinaeast2。 有关如何指定这第二个资源组的名称，请参阅下一部分。

第二个资源组（称为节点资源组，自动命名） 

- 包含与该群集相关联的所有基础结构资源。     这些资源包括 **Kubernetes 节点 VM、虚拟网络和存储**。 
- 默认情况下，节点资源组使用类似于     MC_ResourceGroup_AKSCluster_chinaeast2 的名称。 
- 每当删除群集时，AKS     会自动删除节点资源组，因此，仅应对生命周期与群集相同的资源使用 AKS。

# 存储

## 卷 Volume

卷的类型

- emptydir
  - 是主机上的空目录，支持多容器共享
  - 用作临时空间，POD生命周期结束后，数据也永久删除

- ConfigMap
  - 存储配置信息，明文存储
  - 由同一个namespace中的pod来使用

- Secret
  - 主要用于存储敏感信息，例如密码、秘钥、证书等等。
  - 存储在tmpfs中。加密存储。
  - 最后一个使用secret的POD删除后，该secret也会删除


## 存储层的设置：StorageClass

- 在k8s中，存储类是PV的属性，可以让pvc根据storage class来匹配PV。

![image-20231031092048895](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310310920002.png)

## PV、PVC

- PV（Persistent Volume）持久化卷，是对底层的共享存储的一种抽象。一般情况下PV由kubernetes管理员进行创建和配置，它与底层具体的共享存储技术有关，并通过**插件**完成与共享存储的对接。

- PVC（Persistent Volume Claim）是持久卷声明的意思，是用户对于存储需求的一种声明。换句话说，PVC其实就是用户向kubernetes系统发出的一种资源需求申请。

![image-20231031092138489](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310310921546.png)

- PV可以动态创建or静态创建

  - 静态创建：

    自己创建disk - 自己用这个disk创建PV - 声明PVC绑定到PV上 - 声明POD使用这个PVC

  - 动态创建：

    [动态创建 Azure 磁盘卷 - Azure Kubernetes Service | Azure Docs](https://docs.azure.cn/zh-cn/aks/azure-disks-dynamic-pv#built-in-storage-classes)

    自己声明PVC - PVC自动创建相应的PV和Disk - 声明POD的时候挂载就好

  1. 如果使用默认存储类之一，则默认创建存储类后将无法更新卷大小。若要能够在创建存储类后更新卷大小，请将行：**allowVolumeExpansion: true** 添加到其中一个默认存储类，或者也可以创建自己的自定义存储类。 可以使用 **kubectl edit sc** 命令编辑现有存储类。
  2. 不支持减小PVC的大小（以防数据丢失）。
  3. 如果要使用大小为 4 TiB 的磁盘，需要创建一个定义 cachingmode: None 的存储类，因为磁盘缓存不支持 4 TiB 及更大的磁盘

## Disk、Fileshare

概述：

PV可以使用Azure Managed Disk 或者 Azure File Share。

- 托管磁盘仅支持单个POD访问
- File Share 支持多个POD同时访问
- 二者均可选择HDD和SSD

![image-20231031155907782](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311559854.png)

### Azure Disk

-  Azure 磁盘以 **ReadWriteOnce** 的形式装载，因此仅可用于**单个** **Pod**。 对于可同时由多个 Pod 访问的存储卷，请使用 Azure 文件存储。

  ![image-20231031160101114](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311601163.png)

## Intree和CSI

- Intree：K8s原生支持一些存储类型的PV，但是是存在k8s仓库里，与k8s强耦合，意味着更新会绑定，开发者必须遵循k8s社区的规则编写存储代码等问题。CSI的出现解决了上述问题，使得三方存储代码可以与k8s代码解耦，第三方存储开发者只需要实现CSI接口就行了，无需关注平台是k8s还是Swarm。

- CSI：是一套标准，存储资源使用这套标准，对外提供接口，底层可以用azure、emc等等存储

  [概念 - Azure Kubernetes 服务 (AKS) 中的存储 - Azure Kubernetes Service | Azure Docs](https://docs.azure.cn/zh-cn/aks/concepts-storage)

  [在 Azure Kubernetes 服务 (AKS) 中使用 Azure 磁盘的容器存储接口 (CSI) 驱动程序 - Azure Kubernetes Service | Azure Docs](https://docs.azure.cn/zh-cn/aks/azure-disk-csi)
  
  ![image-20231031161135450](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311611525.png)

## KB:创建azurefile-csi-premium

1. 需要安装和配置 Azure CLI 2.42 或更高版本。运行 az --version 即可查找版本。 如果需要进行安装或升级，请参阅[安装Azure CLI](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Flearn.microsoft.com%2Fcli%2Fazure%2Finstall-azure-cli&data=05|01|hangx%40microsoft.com|27b99b0c0a1f47c38bdd08db5bffcd9a|72f988bf86f141af91ab2d7cd011db47|1|0|638204926499746499|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=bRVollhf98PuLVWF6WL72Bu7GOx7jYJoFn3xh8bDigE%3D&reserved=0)。

2. 请在现有的AKS集群上开启file driver功能，参考命令：

```bash
az aks update -n myAKSCluster -g myResourceGroup --enable-file-driver
```

3. 参考 [https://docs.azure.cn/zh-cn/aks/azure-csi-files-storage-provision#create-an-azure-file-share](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Faks%2Fazure-csi-files-storage-provision%23create-an-azure-file-share&data=05|01|hangx%40microsoft.com|27b99b0c0a1f47c38bdd08db5bffcd9a|72f988bf86f141af91ab2d7cd011db47|1|0|638204926499746499|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=27P37I9N%2BrcQvii7pG3ULmvRHYYoWKFw3aLFaIChNKs%3D&reserved=0)     创建文件共享，存储账户SKU需要设置为Premium_LRS。

4. 参考 [https://docs.azure.cn/zh-cn/aks/azure-csi-files-storage-provision#create-a-kubernetes-secret](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Faks%2Fazure-csi-files-storage-provision%23create-a-kubernetes-secret&data=05|01|hangx%40microsoft.com|27b99b0c0a1f47c38bdd08db5bffcd9a|72f988bf86f141af91ab2d7cd011db47|1|0|638204926499746499|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=YobuJEWWaU629jdnIUSrHbZNaLuTjxQJ8kYL0y42Zls%3D&reserved=0) 创建K8S机密，供后续挂载使用。

5. 参考 [https://docs.azure.cn/zh-cn/aks/azure-csi-files-storage-provision#create-a-kubernetes-secret](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Faks%2Fazure-csi-files-storage-provision%23create-a-kubernetes-secret&data=05|01|hangx%40microsoft.com|27b99b0c0a1f47c38bdd08db5bffcd9a|72f988bf86f141af91ab2d7cd011db47|1|0|638204926499746499|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=YobuJEWWaU629jdnIUSrHbZNaLuTjxQJ8kYL0y42Zls%3D&reserved=0)  将文件共享装载为永久性卷，请注意在storageClassName中应填入azurefile-csi-premium，而不是默认的azurefile-csi。Request的文件共享大小应大于等于100GB，因为premium文件共享所支持的最小大小就是100GB。

# AKS缩放 

## 水平POD自动缩放

Kubernetes 使用水平 Pod 自动缩放程序 (horizonal POD Autoscaler) 来监视资源需求并自动缩放副本数量。 默认情况下，水平 Pod 自动缩放程序每隔 60 秒检查一次指标 API。

Pod数目可以根据业务负载大小自动伸缩，这部分内容请参考官方k8s的说明。（AKS未做改动）

[https://kubernetes.io/zh-cn/docs/tasks/run-application/horizontal-pod-autoscale/](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fkubernetes.io%2Fzh-cn%2Fdocs%2Ftasks%2Frun-application%2Fhorizontal-pod-autoscale%2F&data=05|01|hangx%40microsoft.com|d16dee583a894b2bbaf908db4467d2f5|72f988bf86f141af91ab2d7cd011db47|1|0|638178985041775899|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=MNkUmaiDydvjpGGc7u2Qc8X7Y9tjuVQMOrwLpG%2BLRLM%3D&reserved=0)

## 集群自动缩放

[https://learn.microsoft.com/zh-cn/azure/aks/cluster-autoscaler](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Flearn.microsoft.com%2Fzh-cn%2Fazure%2Faks%2Fcluster-autoscaler&data=05|01|hangx%40microsoft.com|d16dee583a894b2bbaf908db4467d2f5|72f988bf86f141af91ab2d7cd011db47|1|0|638178985041775899|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=3G3ZNsVj966KXErjjODri%2Bwir9Qy8iOsrSy8qpmuUjs%3D&reserved=0)

Cluster Autoscaler，每10s监视一次API。

1.  集群节点scale up：当发现有pod是因为资源约束而无法被部署在任何一个node上时，会触发scale up，向集群中添加一个节点。

2. 集群节点scale down：当已有一段时间存在未使用的容量时，群集自动缩放程序会减少节点数。默认情况下cpu memory资源使用率少于50%且所有pod均可被remove时，触发锁容操作。

3. 关于节点自动缩放的时间控制，您可以参考如下config map文件：[https://learn.microsoft.com/zh-cn/azure/aks/cluster-autoscaler#using-the-autoscaler-profile](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Flearn.microsoft.com%2Fzh-cn%2Fazure%2Faks%2Fcluster-autoscaler%23using-the-autoscaler-profile&data=05|01|hangx%40microsoft.com|d16dee583a894b2bbaf908db4467d2f5|72f988bf86f141af91ab2d7cd011db47|1|0|638178985041775899|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=oUFktC7REoIKBMU%2Fk3isV8dp2mh8bdL3zZyk1Kk82RY%3D&reserved=0)

![image-20231031092258665](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310310922718.png)

## 处理burst情况

当应用程序需要快速缩放的时候，可以采用AKS + Azure Container Instance （ACI），快速部署应用实例。ACI可作为虚拟节点，k8s可在其中运行POD。

不能全用ACI，至少得有一个Worker node

![image-20231031092411134](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310310924175.png)

# AKS Service

![image-20231031093829593](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310310938689.png)

# K8S舍弃dockershim

## Dockerd

dockerd本来是一个单体引擎。docker是CS架构，客户端就是docker cli，服务端是dockerd。

后来把底层交给了社区，拆分成三部分：

1. containerd，作为高层运行时，捐赠给了CNCF。负责镜像拉取和解压。（但是不负责镜像的制作和上传）
2. runC，作为底层运行时，捐赠给了OCI。负责实现OCI运行时规范，管理容器生命周期，与底层Linux系统做交互。
3. dockerd还是留在docker公司做维护。

![image-20231031094821517](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310310948615.png)

## CRI

k8s在1.5版本引入了CRI（容器运行时接口），意思是只要容器运行时实现了CRI接口，那么kubelet就可以调用。

需要一个shim接口层来实现CRI的接口规范，kubelet需要与通过shim来访问到dockerd，进而访问到容器运行时。

- k8s在1.6版本内置了dockershim

- 但是dockershim的官方社区维护停止了，所以k8s在1.23版本弃用了dockershim。

- 现在CNCF把shim集成到了containerd当中（叫CRI plugin）这样kubelet当中的CRI接口直接访问containerd，就绕开了dockerd。

  ![image-20231031095623715](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310310956817.png)

**对我们的使用有啥影响？**

- 使用起来没啥影响。镜像的制作和发布还是要用docker来做，镜像拉取的时候依然是用的containerd。

- 唯一的区别就是轻量化了，shim集成到contianerd当中去了。

  ![image-20231031095531638](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310310955757.png)

**但是对底层资源利用效率有影响：**

[Azure Kubernetes 服务 (AKS) 中的群集配置 - Azure Kubernetes Service | Microsoft Docs](https://docs.microsoft.com/zh-cn/azure/aks/cluster-configuration)

![image-20231031095510684](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310310955758.png)

# AKS VKB

## 安装kubectl

```bash
az aks install-cli
#将/usr/local/bin加入环境变量 （Please ensure that /usr/local/bin is in your search PATH, so the `kubectl` command can be found.）
vim /etc/profile
#在末尾加入两行代码：
PATH=$PATH:/usr/local/bin
export PATH
#执行脚本：
source /etc/profile
```

## 删除节点

- 不能用kubectl delete node来删，这是k8s level的操作；k8s level与aks nodepool level没有api call。

- nodepool不能感知k8s层面的变化。node用kubectl删了之后，nodepool显示不出来数量的变化。之后如果去scale，会产生错误。

- 如果真的误删，有两种work around：1. nodepool上重启被删掉的vmss 2. 升级到高版本。

## 临时盘

https://docs.microsoft.com/en-us/azure/virtual-machines/ephemeral-os-disks

https://docs.microsoft.com/en-us/azure/aks/cluster-configuration#ephemeral-os

对于VM Throttling的问题，最好的建议就是启用临时OS盘：

- 临时OS盘，用VM本地存储，优点是提高IO性能和读写速度， 可以快速reimage，快速集群扩展和升级。部署在临时盘或者VM缓存上。缺点是重启就没了。
- 只要机型适合创建临时OS盘，AKS就默认是临时OS盘，否则会是托管盘。cli创建aks集群时，用--node-osdisk-type
- （PG说过，两个node     pool，一个开了临时OS盘，一个没开，负载有可能会更倾向于部署到性能更好的pool上）

## Node状态

![image-20231031103813424](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311038599.png)

报告Node Not Ready，主要可能是因为如下几大组件出问题：

- kubelet

  向集群注册、报告heartbeat、健康状态。

  Heartbeat的机制：

  - 小集群：kubelet直接报告

  - 大集群：通过创建lease     object，每隔一定间隔，向api server报告status。

- kubeproxy

  kubeproxy也是以pod的形式部署在node上

- addons

  常见的以deamonset、deployment来部署。

  AKS troubleshooting的时候，omsagent常见。

### PLEG

![image-20231031104756604](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311047710.png)

## Extensions

- 默认集群会装两个extension（1. custom script：配置相应的环境；2. billing相关的），ssh linux的扩展也可能有，如果客户曾ssh登录上去过，这个不要紧，模板和实例都会更新。
- 不推荐在VMSS实例上装extension，我们其他服务通过pod来部署
- 如果有其他的extension，可能原因就是这个。

## 登录node

### 方法1：kubectl debug

[recommended way](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Faks%2Fssh&data=02|01|Qing.Fang%40microsoft.com|3de2db456b2d451fc19d08d7e82a27d3|72f988bf86f141af91ab2d7cd011db47|1|0|637233140101185002&sdata=vyGFHDhxqaDo%2BdDFc6hGHN%2BatvZrPL8oX9NXbyCQ%2BJQ%3D&reserved=0)

```bash
kubectl get nodes -o wide
kubectl debug node/<node name> -it --image=mcr.azk8s.cn/aks/fundamental/base-ubuntu:v0.0.11
chroot /host
```

> 此命令创建特权容器并SSH连接到该容器（特权容器通过Hostpath的方式将node的根目录 / 挂载到POD内部的 /host；在POD里面执行 chroot /host，将会把 /host改为pod的根目录）：特权容器

### 方法2 node-shell

```bash
curl -LO https://github.com/kvaps/kubectl-node-shell/raw/master/kubectl-node_shell
chmod a+x kubectl-node_shell
mv ./kubectl-node_shell /usr/local/bin/kubectl-node_shell
```

### 方法3：直接ssh

- 在vmss所在的vnet中新建一台跳板机vm

- 安装az cli

[Install the Azure CLI on Linux | Microsoft Docs](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=dnf)

```bash
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc

echo -e "[azure-cli]
name=Azure CLI
baseurl=https://packages.microsoft.com/yumrepos/azure-cli
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc" | sudo tee /etc/yum.repos.d/azure-cli.repo

yum install -y dnf
sudo dnf install azure-cli
```

- 生成ssh秘钥

```bash
ssh-keygen 
```

- 登录azcli

```bash
az cloud set -n AzureChinaCloud
az account set --subscription <name or id>
az login
```

- 将公钥推送至vmss模板

```bash
az vmss extension set --resource-group MC_aksTest_aksTest_chinaeast2 --vmss-name aks-nodepool2-36202706-vmss --name VMAccessForLinux --publisher Microsoft.OSTCExtensions --version 1.4 --protected-settings "{\"username\":\"azureuser\", \"ssh_key\":\"$(cat /root/.ssh/id_rsa.pub)\"}"
```

- 将key更新至每一个节点

```bash
az vmss update-instances --instance-ids '*' --resource-group MC_aadaks_icyaks_chinaeast2 --name aks-nodepool1-27240906-vmss
```

- 客户端直接用node内网IP登录

```bash
ssh -i id_rsa azureuser@<aks node private IP> 
```

###  方法4：使用kubectl-enter登录node

```bash
kubectl-enter
sudo wget https://raw.githubusercontent.com/andyzhangx/demo/master/dev/kubectl-enter
sudo chmod a+x ./kubectl-enter
./kubectl-enter <node-name>
```

## 收集node日志

### kubectl cp命令

- 在管理机上创建特权容器：

```bash
kubectl get nodes -o wide
kubectl debug node/<node name> -it --image=mcr.azk8s.cn/aks/fundamental/base-ubuntu:v0.0.11
```

- 进入到node内部后，特权容器是把node的/挂载到了pod的/host目录下。切换根目录到/host：

```bash
chroot /host
```

- 准备日志文件（收集、打包、切换owner）：

```bash
cd /tmp/
mkdir logsCollection
journalctl -u kubelet > logsCollection/kubelet.log
date > logsCollection/dateOutput.txt
last > logsCollection/lastOutput.txt
cd /var/log/
cp -r azure/ auth.log\* messages\* syslog\* waagent.log\* /tmp/logsCollection/
ls /tmp/logsCollection/
cd /tmp/
tar zcvf logsCollection.tgz logsCollection/\*
sudo chown azureuser:azureuser logsCollection.tgz
```

- 准备好之后，特权容器的会话不要关闭，保持特权容器running状态；重新开一个ssh会话，连接到管理机上，并运行以下命令：

```bash
kubectl get pods
kubectl cp <debugger pod name>:host/tmp/logsCollection.tgz ./<destination file name> 
```

- 完成后，日志就从特权容器中转移到了管理机上，上传即可。

- 注意：用官方这个特权容器方法，journalctl -u kubelet 这个命令只有在chroot /host之后才能运行，在node里面直接运行是不行的。

### sftp命令

登录到node中，准备好文件，利用sftp把文件转移到另一台VM上。

- sftp到另一台VM（需要知道username和password）

- (如果是kubectl debug登录到的节点，需要chroot /host 之后才能用sftp转移文件；如果是node-shell登录到的节点，直接在node里面转移就行)

```bash
sftp hangx@52.130.152.117
put <path/file name>
```

### container insight

- AKS今年新上线一个Feature，可以直接借助Container insight收集node系统日志，具体如下

  [https://learn.microsoft.com/en-us/azure/azure-monitor/containers/container-insights-syslog#prerequisites](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fazure%2Fazure-monitor%2Fcontainers%2Fcontainer-insights-syslog%23prerequisites&data=05|01|hangx%40microsoft.com|4982c51d3d40444106e308dba20d4c8e|72f988bf86f141af91ab2d7cd011db47|1|0|638281950270554904|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=2FPYL8S7t96u6LHR7SzuKe4qzJ0K0STPwEaaBnAKmZ0%3D&reserved=0)

- 请注意，不是通过AKS diagnostic方式开启syslog收集。

- 开启方法 -- 命令行enable：

  ![image-20231031150041889](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311500948.png)

- 查看log：

  1. 通过workbook查看syslog：

  2. 使用log query 直接查看：

     ![image-20231031150144966](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311501101.png)

- 该功能的原理是在节点上起一个ama的pod，负责收集节点日志并上传到Log Analytics Workspace中，有极大概率能保存node not ready时的系统日志。

## 特权容器

```bash
kubectl debug node/aks-nodepool2-36202706-vmss00001a -it --image=mcr.azk8s.cn/aks/fundamental/base-ubuntu:v0.0.11
```

```bash
Name:         node-debugger-aks-nodepool2-36202706-vmss00001a-cfqhw
......
    Mounts:
      /host from host-root (rw)
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-jzvdt (ro)

Volumes:
  host-root:
    Type:          HostPath (bare host directory volume)
    Path:          /
    HostPathType:
......
```

- 这个pod通过hostpath的方式，将宿主机的 / 挂载到了pod的 /host下。
- chroot /host 会将这个pod的根目录更改为 /host ==> 就看到了宿主机的文件系统了。

## reconcile

[az aks | Microsoft Learn](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fcli%2Fazure%2Faks%3Fview%3Dazure-cli-latest%23az-aks-update&data=05|01|hangx%40microsoft.com|8da5567f67e34cd6bb1e08dac1597557|72f988bf86f141af91ab2d7cd011db47|1|0|638034887449347002|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=IaHppznYYlinzbemnv7xdp6ddikQuxvEXqH2ihohI5w%3D&reserved=0) 

- az aks update在不带可选参数的情况下调用时，它将尝试在不更改当前集群配置的情况下将集群恢复到其目标状态。这可以用于摆脱非成功状态。 也就是我们常说的aks reconcile. 
- 对API发起PUT请求，让集群对照config文件，一一对比所有object现状（node pod等）。当前状态与config不一致时，修改object的状态。

- Reconcile有两种方法：az aks update | az aks upgrade（不能完全代替reconcile），推荐用**az aks update**

- The aks-preview Azure CLI extension (version 0.5.66+) now supports running：

  **az aks update -g <resourceGroup> -n <clusterName>** without any optional arguments. 

  This will perform an update operation without performing any changes, which can recover a cluster stuck in a failure state

  Remember to **upgrade your az cli** to latest version and **install aks-preview extension** or you will hit bellow errors

### 是否会引起重启

- 怎么判断reconcile是否会引起节点重启？

  看latest model是no，大概率会引起节点reimage。通常是因为节点vmss现在的实例和模板库不一致。（也有可能是因为改了节点sku、扩展等等）

- 如果VMSS实例和VMSS模板一样（latest model是yes），但是vmss模板和node image（aks最新的库，里面存着各个版本的vhd）不同：

  - 会先校验vmss模板和node image库，发现不同，就按照node image的库 -> 更新vmss模板 -> 再更新vmss实例。
  - 所以在这种情况，会出现latest model显示yes，但是reconcile触发了节点reimage。

- 总之，不建议从VMSS层面更改任何配置，要从VMSS模板层面来改动。而改动方法就是按新的模板新建一个pool，迁移过去，干掉旧的。

# AKS升级

## 不同版本的区别

- 希望了解版本1.23.8和版本1.23.15版本之间的变化。您可以通过github的release note了解其中具体的差别。

  Release note：[Releases · Azure/AKS (github.com)](https://github.com/Azure/AKS/releases)

- AKS版本信息构成为[major].[minor].[patch]

  从此链接，您可以获取到中国区AKS的发布日历[Azure Kubernetes 服务中支持的Kubernetes 版本- Azure Kubernetes Service | Azure Docs](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Faks%2Fsupported-kubernetes-versions%3Ftabs%3Dazure-cli%23aks-kubernetes-release-calendar&data=05|01|hangx%40microsoft.com|53bf571c037a4b8f1c9208db512b597c|72f988bf86f141af91ab2d7cd011db47|1|0|638193018965476016|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=MAreiIP9ltF2iLuWGLB2SkHGLRkMxTaNhZJOMdNIWPs%3D&reserved=0)

- 由于AKS跟随K8s的发布，由于其版本升级的话会有一些组件的变化，以下为一些已知的组件变化，对此也建议您升级前对应用也进行相应的测试评估。

  1.24.x版本

  1.24上有如下已知较大的改动：[kubernetes/CHANGELOG-1.24.md at master · kubernetes/kubernetes · GitHub](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fgithub.com%2Fkubernetes%2Fkubernetes%2Fblob%2Fmaster%2FCHANGELOG%2FCHANGELOG-1.24.md%23urgent-upgrade-notes&data=05|01|hangx%40microsoft.com|53bf571c037a4b8f1c9208db512b597c|72f988bf86f141af91ab2d7cd011db47|1|0|638193018965476016|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=G0%2Fc%2BrOsHkZlsnpscXrD%2Fm11DcJhVy81zPt9LTkyrL4%3D&reserved=0)。

  默认serviceaccount不再包含secret。

  1.25+版本（包含1.26）

  Ubuntu底层从cgroup1切换成cgroup2，Java/JDK旧版本会因为cgroupv2导致内存消耗增加，进而导致OOM。

  Java/JDK support for cgroups v2 is available in [JDK 11 (patch 11.0.16 and later) or JDK 15 and above](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fbugs.java.com%2Fbugdatabase%2Fview_bug.do%3Fbug_id%3D8230305&data=05|01|hangx%40microsoft.com|53bf571c037a4b8f1c9208db512b597c|72f988bf86f141af91ab2d7cd011db47|1|0|638193018965476016|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=0JHQtaNhsXwgHrflZoNYFfeej0A2SQZGLcYeRtCuV34%3D&reserved=0). AKS Kubernetes 1.25+ uses cgroups v2. Please migrate your workloads to the new JDK.

## 支持策略

目前support plan的分为N-2(regular supported version in AKS)和N-3 (platform support)：[Supported Kubernetes versions in Azure Kubernetes Service (AKS). - Azure Kubernetes Service | Azure Docs](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fen-us%2Faks%2Fsupported-kubernetes-versions%3Ftabs%3Dazure-cli&data=05|01|hangx%40microsoft.com|ce4b56a9a7044b63f1c608db623fe714|72f988bf86f141af91ab2d7cd011db47|1|0|638211798876829076|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=pgtGz1kkrMojmsdELYN9DkKJx4aGMckQxQAfvBCQaRc%3D&reserved=0)

N-2和N-3的比对：

[https://docs.azure.cn/en-us/aks/supported-kubernetes-versions?tabs=azure-cli#platform-support-policy](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fen-us%2Faks%2Fsupported-kubernetes-versions%3Ftabs%3Dazure-cli%23platform-support-policy&data=05|01|hangx%40microsoft.com|ce4b56a9a7044b63f1c608db623fe714|72f988bf86f141af91ab2d7cd011db47|1|0|638211798876829076|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=npHk9XQT9RQ0u2oO9KOH7d6l5TKJnIj%2BtTLP1Fxl4Z4%3D&reserved=0)

简单来说，平台的支持N-3是一个缩减的支持，因此，还是建议按照N-2的方式来安排版本升级。

## 升级方法

[升级 Azure Kubernetes 服务 (AKS) 群集 - Azure Kubernetes Service | Azure Docs](https://docs.azure.cn/zh-cn/aks/upgrade-cluster)

注意：升级k8s版本后，缓冲节点将会被删除，升级后的node name还是跟原来一样

## 升级注意事项

- 在升级群集之前，请使用 `az aks get-upgrades` 命令检查哪些 Kubernetes 版本可用于升级：

```bash
az aks get-upgrades --resource-group myResourceGroup --name myAKSCluster -o table
```

- 使用 `az aks upgrade` 命令升级 AKS 群集。

```bash
az aks upgrade  --resource-group myResourceGroup  --name myAKSCluster  --kubernetes-version KUBERNETES_VERSION
```

- 如果使用的是自定义的网络配置CNI，请升级前检查剩余的IP地址段是否足够。

  [https://docs.azure.cn/zh-cn/aks/configure-azure-cni#plan-ip-addressing-for-your-cluster](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Faks%2Fconfigure-azure-cni%23plan-ip-addressing-for-your-cluster&data=05|01|hangx%40microsoft.com|500341f829b8489023a008da704897e6|72f988bf86f141af91ab2d7cd011db47|1|0|637945754427761634|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=iHGX0I8Kk3QMVTemDtxK1fXllvXANum58QbGq%2FCp5Kk%3D&reserved=0)

- 检查下集群里是否部署了PDB，如果部署了，先delete掉，升级完再部署上；

  [https://kubernetes.io/docs/tasks/run-application/configure-pdb/](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fkubernetes.io%2Fdocs%2Ftasks%2Frun-application%2Fconfigure-pdb%2F&data=05|01|hangx%40microsoft.com|500341f829b8489023a008da704897e6|72f988bf86f141af91ab2d7cd011db47|1|0|637945754427761634|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=IAXUZiZfhb9HLdx0tmiYA6spIhpOUkfzqYipEA4LRHg%3D&reserved=0)

```bash
kubectl get poddisruptionbudgets <pdb name> -o yaml  > <pdbname>.yaml
kubectl delete pdb <pdb-name>
```

- 如果是多节点池，注意升级完面板之后，再逐个升级节点池；

- 升级之前先查看下集群整体资源是否充足

```bash
kubectl top node
```

如果不足，请先scale up一个节点；再升级；

```bash
az aks scale --resource-group myResourceGroup --name myAKSCluster --node-count <target number>
```

- 关于各个版本的EOS时间，N+2版本GA之后，第N个版本就要EOS了；

- 不要跨版本升级：AKS不支持跨版本升级。除非当前版本不受支持，那才可以直接跳跃升级到最低的受支持版本。

- 注意：container runtime的更改 [https://docs.azure.cn/zh-cn/aks/cluster-configuration#container-runtime-configuration](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Faks%2Fcluster-configuration%23container-runtime-configuration&data=05|01|hangx%40microsoft.com|500341f829b8489023a008da704897e6|72f988bf86f141af91ab2d7cd011db47|1|0|637945754427761634|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=3J0X8nLZb%2FfJEG2Q6%2FWQlC7CHKFOzBeclNzoJ2j%2B1Iw%3D&reserved=0)

-  查看是否升级成功

```bash
az aks show --resource-group myResourceGroup --name myAKSCluster --output table
```

## 自动升级选项

https://docs.azure.cn/zh-cn/aks/auto-upgrade-cluster?tabs=azure-cli#cluster-auto-upgrade-channels

| 通道                 | 操作                                                         | 示例                                                         |
| :------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| `none`               | 禁用自动升级，使群集保持其当前版本的 Kubernetes。            | 如果保持不变，则为默认设置。                                 |
| `patch`              | 当有最新的受支持补丁版本可用时，将群集自动升级到该版本，同时使次要版本保持不变。 | 例如，如果群集运行版本 1.17.7，而版本 1.17.9、1.18.4、1.18.6 和 1.19.1 可用，则群集将升级到 1.17.9。 |
| `stable`             | 自动将群集升级到次要版本 N-1 的最新受支持补丁发行版，其中 N 是最新的受支持次要版本。 | 例如，如果群集运行版本 1.17.7，而版本 1.17.9、1.18.4、1.18.6 和 1.19.1 可用，则群集将升级到 1.18.6。 |
| `rapid`              | 自动将群集升级到最新受支持次要版本的最新受支持补丁发行版。   | 如果群集的 Kubernetes 版本是一个 N-2 次要版本，其中 N 是最新的受支持次要版本，则群集将首先升级到 N-1 次要版本的最新受支持补丁版本。 例如，如果群集运行版本 1.17.7，而版本 1.17.9、1.18.4、1.18.6 和 1.19.1 可用，则群集将先升级到 1.18.6，然后升级到 1.19.1。 |
| `node-image`（旧版） | 自动将节点映像升级到可用的最新版本。                         | Microsoft 经常（通常每周）为映像节点提供补丁和新映像，但除非升级节点映像，正在运行的节点将不会获得新映像。 当有新版本可用时，打开节点映像通道会自动更新节点映像。 如果使用此通道，默认情况下将禁用 Linux [无人参与升级]。 只要次要 Kubernetes 版本仍然受支持，节点映像升级就会适用于已弃用的补丁版本。 不再建议使用此通道，未来将弃用此通道。 有关可以自动升级节点映像的选项，请参阅[节点映像自动升级](https://docs.azure.cn/zh-cn/aks/auto-upgrade-node-image)中的 `NodeImage` 通道。 |

## PDB

Disruptions [干扰（Disruptions） | Kubernetes](https://kubernetes.io/zh-cn/docs/concepts/workloads/pods/disruptions/)

怎么算的：

- 首先，pdb yaml就三个字段：selector、min available和max unavailable。

- min available和max unavailable是可以根据情况设定的，而allowed disruption是系统自动算出来的。

- 比如下图，coredns pod minAvailable=1，最少要有一个在工作，这个pod目前就俩，所以允许的中断 alllowed disruption就是1个

![image-20231031105327848](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311053910.png)

# Cert

- TLS通信双方需要证书，集群里面的每个组件都需要CA，api，etcd，kubelet等都需要。
- CA：certificate authority     - AKS中的证书颁发机构 - suppose有效期30年 - 自签的 - 产品组控制的
- 给API kubelet ETCD等组件颁发证书

- CA过期：报x509，kubectl命令失效，所有节点与API失联，集群non-success状态

## Cert和sp的区别

- cert是组件之间互相通信

- sp是负责代表k8s去拿一些资源，比如scale up的时候去拿一些计算 网络 存储资源用到的。

## AKS升级会自动轮换Cert

![image-20231031151204236](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311512305.png)

- 前提：需要开TLS Bootstrapping功能 [Certificate Rotation in Azure Kubernetes Service (AKS) - Azure Kubernetes Service | Microsoft Learn](https://learn.microsoft.com/en-us/azure/aks/certificate-rotation#how-to-check-whether-current-agent-node-pool-is-tls-bootstrapping-enabled)

## 手动轮换证书

证书过期后，将无法使用kubectl等命令联系到AKS集群，在此情况下，请参考文档中的手动步骤，对证书进行轮换。

[https://docs.azure.cn/zh-cn/aks/certificate-rotation#rotate-your-cluster-certificates](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Faks%2Fcertificate-rotation%23rotate-your-cluster-certificates&data=05|01|hangx%40microsoft.com|f991155818a2436c7dc408daace6da54|72f988bf86f141af91ab2d7cd011db47|1|0|638012404887442278|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=RQ9tT6%2BESKaserf%2By6yBhxqvFmKsjY1qcfv2gxEl80w%3D&reserved=0)

通常的步骤包含：

- 使用 az aks  get-credentials 登录到 AKS 群集
- 使用 az aks  rotate-certs 轮换群集上的所有证书、CA 和 SA
- 轮换成功后，再次运行“az aks get-credentials -g $RESOURCE_GROUP_NAME -n $CLUSTER_NAME --overwrite-existing”更新本地证书。

需要特别注意的是，

- 使用 az aks rotate-certs 手动轮换证书将重新创建所有节点、VM规模集及其磁盘，并可能导致 AKS 群集downtime长达 30 分钟。
- 跟版本过低一起遇到的话，得先升级。

- 如果不想用rotate cert来轮换，有如下workaround：

  - 用命令直接rotate cert，会导致所有nodes重建，service会重新部署。客户要继续使用service原来的配置，重新部署有很大可能会更改旧的配置。因此使用下面的WA：

  - 使用acli执行如下指令:

  ```bash
  az extension remove --name aks-preview
  az extension add --source https://raw.githubusercontent.com/andyzhangx/demo/master/aks/rotate-tokens/aks_preview-0.5.0-py2.py3-none-any.whl -y RESOURCE_GROUP_NAME=  CLUSTER_NAME=
  az aks reconcile-control-plane-certs -g $RESOURCE_GROUP_NAME -n $CLUSTER_NAME
  ```

  - 命令执行完成后，会更新Master节点的证书

  - Master证书更新完成后，对aks集群节点池进行扩容，新生成的节点会从master获取正确的证书.

  - 新节点生成后，逐步删除节点池中的旧节点，业务会从旧节点逐渐转移到新节点，直到删除所有的旧节点。

## Troubleshooting

- [Certificate Rotation in Azure Kubernetes Service (AKS) - Azure Kubernetes Service | Microsoft Docs](https://docs.microsoft.com/en-us/azure/aks/certificate-rotation#aks-certificates-certificate-authorities-and-service-accounts)

- [Azure Kubernetes 服务 (AKS) 中的证书轮换 - Azure Kubernetes Service | Azure Docs](https://docs.azure.cn/zh-cn/aks/certificate-rotation)

![image-20231031151301068](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311513144.png)

## cert过期对业务的影响

- 不一定，cert影响的是组件之间的通信。如果业务不需要组件之间的通信，那么理论上不会影响业务。

- 即使node not ready，pod也可能正常跑着。因为node状态是kubelet定时向api server报告状态，其中哪一步中断，导致获取不到状态就报告not ready。

# AKS的SP/MI

## SP

[使用 Azure Kubernetes 服务 (AKS) 的服务主体 - Azure Kubernetes Service | Microsoft Docs](https://docs.microsoft.com/zh-cn/azure/aks/kubernetes-service-principal?tabs=azure-cli)

- AKS集群若要访问其他Azure资源如ACR或者scale up的时候需要获取计算 网络 存储等资源等，需要使用AAD service pricinpal。

- 服务主体不会自动创建，需要自己创建。服务主体会过期，必须定时续订才能让集群正常运行。

- 查看

  ```bash
  #查看aks的SP信息
  az aks show -g aksTest -n aksTest --query "servicePrincipalProfile"
  ```


### 过期

SP过期之后，借助SP权限操作的动作都会收到影响，比如但不限于以下：

1. Azure Container Registry - If you use Azure Container Registry (ACR) as your container image store, you need to grant permissions to the service principal for your AKS cluster to read and pull images. 
2. Networking - You may use advanced networking where the virtual network and subnet or public IP addresses are in another resource group.
3. Storage - If you need to access existing disk resources in another resource group

### 更新

- 创建服务主体

  [使用 Azure Kubernetes 服务 (AKS) 的服务主体 - Azure Kubernetes Service | Microsoft Docs](https://docs.microsoft.com/zh-cn/azure/aks/kubernetes-service-principal?tabs=azure-cli#manually-create-a-service-principal)

- 查看SP过期时间

  [为 Azure Kubernetes 服务 (AKS) 群集更新或轮换凭据 - Azure Kubernetes Service | Microsoft Learn](https://learn.microsoft.com/zh-cn/azure/aks/update-credentials#check-the-expiration-date-of-your-service-principal)

- 更新SP的秘钥

  [为 Azure Kubernetes 服务 (AKS) 群集更新或轮换凭据 - Azure Kubernetes Service | Microsoft Learn](https://learn.microsoft.com/zh-cn/azure/aks/update-credentials#reset-the-existing-service-principal-credentials)

  - 因为SP的信息不是一个变量在每个虚拟机里面引用，他是写死在每个vmss instance上面的，所以更新SP后，一定会涉及到reimage，node重启。
  - 更新服务主体凭据会通过升级每个节点的image完成，会造成集群节点重启，但不会是同时做image upgrade，上层业务如果有多副本以及冗余机制可以不受影响。

- 用新秘钥更新集群

  [为 Azure Kubernetes 服务 (AKS) 群集更新或轮换凭据 - Azure Kubernetes Service | Microsoft Learn](https://learn.microsoft.com/zh-cn/azure/aks/update-credentials#update-aks-cluster-with-service-principal-credentials)

## MSI

- MSI在集群中分为cluster identity和kubelet identity：[AKS Review - 2.1: Identity & Access Control - Cluster, Operator & Pod Identity - Microsoft Community Hub](https://techcommunity.microsoft.com/t5/fasttrack-for-azure/aks-review-2-1-identity-amp-access-control-cluster-operator-amp/ba-p/3716906)

```bash
#查看aks的kubelet identity信息
az aks show -g aksTest -n aksTest --query "identityProfile"
#查看aks的cluster identity信息
az aks show -g aksTest -n aksTest --query "identity"
```

- 从SP迁移到MSI：[在 Azure Kubernetes 服务中使用托管标识 - Azure Kubernetes Service | Microsoft Learn](https://learn.microsoft.com/zh-cn/azure/aks/use-managed-identity#update-an-aks-cluster-to-use-a-managed-identity)
  - 升级完之后，控制平面和addon会使用managed identity, 但是nodepool的kubelet还是会用SP不会马上生效，直到image库里面出现一个比当前image新的image，nodepool更新image才会生效。
  - nodepool更新image：[Upgrade Azure Kubernetes Service (AKS) node images - Azure Kubernetes Service | Microsoft Learn](https://learn.microsoft.com/en-us/azure/aks/node-image-upgrade#upgrade-all-nodes-in-all-node-pools)
    ![image-20231031155011070](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311550126.png)

# AKS networking

## 部署AKS的网络规划

- AKS 部署时显示的limit如下（代码中指定的上限）

| **Maximum nodes per cluster with Virtual Machine Scale  Sets and [Standard Load Balancer SKU](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.microsoft.com%2Fen-us%2Fazure%2Fload-balancer%2Fload-balancer-overview&data=05\|01\|hangx%40microsoft.com\|7610021292ff4f9af8af08da7e8fc17f\|72f988bf86f141af91ab2d7cd011db47\|1\|0\|637961453218706948\|Unknown\|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D\|3000\|\|\|&sdata=q6Dbhxw7TUAjxvW2q%2BQRK9z5RzHRzHHBtK%2FfxnHApqM%3D&reserved=0)** | 1000 (across all [node   pools](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.microsoft.com%2Fen-us%2Fazure%2Faks%2Fuse-multiple-node-pools&data=05\|01\|hangx%40microsoft.com\|7610021292ff4f9af8af08da7e8fc17f\|72f988bf86f141af91ab2d7cd011db47\|1\|0\|637961453218706948\|Unknown\|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D\|3000\|\|\|&sdata=xXWeqw27H4iFK7l7LoCazcl8NkP%2FIB1wKuOpD9Imut0%3D&reserved=0)) |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| Maximum node pools per cluster                               | 100                                                          |
| Maximum pods per node: [Basic networking](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.microsoft.com%2Fen-us%2Fazure%2Faks%2Fconcepts-network%23kubenet-basic-networking&data=05\|01\|hangx%40microsoft.com\|7610021292ff4f9af8af08da7e8fc17f\|72f988bf86f141af91ab2d7cd011db47\|1\|0\|637961453218706948\|Unknown\|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D\|3000\|\|\|&sdata=2uuA96L2KVXU8gh7nvVeoX7DzfLOZw9t8dKLrhbak4Y%3D&reserved=0) with Kubenet | Maximum: 250  Azure CLI default: 110  Azure Resource Manager template default: 110  Azure portal deployment default: 30 |
| Maximum pods per node: [Advanced networking](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.microsoft.com%2Fen-us%2Fazure%2Faks%2Fconcepts-network%23azure-cni-advanced-networking&data=05\|01\|hangx%40microsoft.com\|7610021292ff4f9af8af08da7e8fc17f\|72f988bf86f141af91ab2d7cd011db47\|1\|0\|637961453218706948\|Unknown\|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D\|3000\|\|\|&sdata=Z8hR7xFY5GKNl8o9lC6DL32dbvS0B3BbjOVmQWRQwQs%3D&reserved=0) with Azure Container Networking Interface | Maximum: 250  Default: 30                                    |

- 网络限制：

  - Kube-proxy，kube-proxy是基于iptables来实现服务发现和负载均衡，但随着节点，service以及pod数目增加，每个节点上的kube-proxy更新就会成为瓶颈。（kube-proxy一直监听api，会实时刷新监听到的变化）

  - 关于SNAT 端口问题

    Kubenet方式，无论集群内部通信还是pod到external的通信都需要借助NAT，并且source IP会被显示为node primary ip。

    CNI方式，集群内部通信不需要NAT，但是traffic out cluster（出VNET）还要借助NAT 

  - 一个public IP可以提供6400个SNAT port，默认node小于50个时，每个node预留1024个 port。

- 默认情况下使用SLB时候，会有一个public绑定。但用户可以指定多个public到该SLB。

  [https://docs.microsoft.com/en-us/azure/aks/load-balancer-standard#scale-the-number-of-managed-outbound-public-ips](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.microsoft.com%2Fen-us%2Fazure%2Faks%2Fload-balancer-standard%23scale-the-number-of-managed-outbound-public-ips&data=05|01|hangx%40microsoft.com|7610021292ff4f9af8af08da7e8fc17f|72f988bf86f141af91ab2d7cd011db47|1|0|637961453218706948|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=tbEhr8ma0M8XWguog1iGLY1dTArG1M22%2FBV%2BHHntcNw%3D&reserved=0)

- 综上，我们可以考虑借助向LB中添加多个IP以及修改每个节点可使用的SNAT port数目，来定制该大型集群。

  [https://docs.microsoft.com/en-us/azure/aks/load-balancer-standard#provide-your-own-outbound-public-ips-or-prefixes](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.microsoft.com%2Fen-us%2Fazure%2Faks%2Fload-balancer-standard%23provide-your-own-outbound-public-ips-or-prefixes&data=05|01|hangx%40microsoft.com|7610021292ff4f9af8af08da7e8fc17f|72f988bf86f141af91ab2d7cd011db47|1|0|637961453218706948|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=wIcEy4Y1ISj%2FZk90tpYRl91C1UZdA2aCHD2RZStDA2E%3D&reserved=0)

-  确认了SNAT耗尽的问题，可以借助添加IP到SLB来解决。其中一个SLB最多可以天机600个public ip；一个SLB的IP可以提供给64000个端口。绑定方式：[https://docs.microsoft.com/en-us/azure/aks/load-balancer-standard#provide-your-own-outbound-public-ips-or-prefixes](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.microsoft.com%2Fen-us%2Fazure%2Faks%2Fload-balancer-standard%23provide-your-own-outbound-public-ips-or-prefixes&data=05|01|hangx%40microsoft.com|7610021292ff4f9af8af08da7e8fc17f|72f988bf86f141af91ab2d7cd011db47|1|0|637961453218706948|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=wIcEy4Y1ISj%2FZk90tpYRl91C1UZdA2aCHD2RZStDA2E%3D&reserved=0)

- 使用NAT gateway方式，最多有16个IP可以绑定，至多提供64000x16个port，不能保证符合您的需求

  [https://docs.microsoft.com/en-us/azure/aks/nat-gateway](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.microsoft.com%2Fen-us%2Fazure%2Faks%2Fnat-gateway&data=05|01|hangx%40microsoft.com|7610021292ff4f9af8af08da7e8fc17f|72f988bf86f141af91ab2d7cd011db47|1|0|637961453218706948|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=ozoOdsxvIL5X1KcvN3a9eCv%2BQ3x3QF1y8VaCCwmJgMc%3D&reserved=0)

- node里面的pod都是私网IP地址，pod向外暴露，或者service向外暴露，由公网IP访问的话，是通过source 端的NAT转换，也就是把pod 私网IP通过SNAT端口的方式暴露出去。每个节点上的端口数目都是一定的，暴露太多就容易耗尽。每个节点的port数目怎么判断：根据node里面的pod数目而定： 

  ![image-20231031165015209](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311650318.png)

# AzureLinux

- 新的服务Azure Linux Container Host for AKS已经上线，它针对在 Azure Kubernetes 服务 (AKS) 上运行容器工作负载进行了优化。它由 Microsoft 维护，并基于 Microsoft Azure Linux（由 Microsoft 创建的开源 Linux 分发）。详细信息请参考如下文档：

  [https://docs.azure.cn/en-us/aks/cluster-configuration#mariner-os](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fen-us%2Faks%2Fcluster-configuration%23mariner-os&data=05|01|hangx%40microsoft.com|c828ffda638b4906ed2908db6d762366|72f988bf86f141af91ab2d7cd011db47|1|0|638224126451526625|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=5CqF6%2FP%2BqE0E5D3PM4tr1LC%2BxgMzWq8LUooGdewb%2BKc%3D&reserved=0)

  [https://learn.microsoft.com/en-us/azure/azure-linux/intro-azure-linux](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fazure%2Fazure-linux%2Fintro-azure-linux&data=05|01|hangx%40microsoft.com|c828ffda638b4906ed2908db6d762366|72f988bf86f141af91ab2d7cd011db47|1|0|638224126451526625|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=VZk0SxRf%2FGe4c4d5IOHtcjgmA%2FS2Upl3%2BimjCfLvE2E%3D&reserved=0)

根据文档，您可以：

- 新建使用Azure Linux Container Host 的AKS集群。
- 在现有的AKS进群中添加使用Azure Linux Container Host的node pool ([https://learn.microsoft.com/en-us/azure/azure-linux/tutorial-azure-linux-add-nodepool#1---add-an-azure-linux-node-pool](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fazure%2Fazure-linux%2Ftutorial-azure-linux-add-nodepool%231---add-an-azure-linux-node-pool&data=05|01|hangx%40microsoft.com|c828ffda638b4906ed2908db6d762366|72f988bf86f141af91ab2d7cd011db47|1|0|638224126451682847|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=giCoLXfAftZccD%2FwyFwhHiH%2FmxdrljSDD4%2FR9qxvqsY%3D&reserved=0))。
- 将现有的AKS集群迁移到Azure Linux Container Host ([https://learn.microsoft.com/en-us/azure/azure-linux/tutorial-azure-linux-migration](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fazure%2Fazure-linux%2Ftutorial-azure-linux-migration&data=05|01|hangx%40microsoft.com|c828ffda638b4906ed2908db6d762366|72f988bf86f141af91ab2d7cd011db47|1|0|638224126451682847|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=fXlxB89Rc4xe7JZDlXSxQm0DMxLbpKLziZcQ4%2FPmOjA%3D&reserved=0))。

# AKS-AAD

AKS-managed Azure AD 和Use Azure RBAC for Kubernetes authorization和Use Kubernetes RBAC with Azure AD integration之间的区别：

首先，[**AKS – managed Azure AD integration**](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Faks%2Fmanaged-aad&data=05|01|hangx%40microsoft.com|d2117bfa41ad4203878508db503e5dc4|72f988bf86f141af91ab2d7cd011db47|1|0|638192001046754818|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=Wz%2BtdrdWvG5iIsoPooG%2FRHt44mjfsh27TRYZJGs%2Fd%2BQ%3D&reserved=0)区别于后两者，侧重在AKS集群和AAD的集成方式，相比于[legacy AAD integration](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Faks%2Fazure-ad-integration-cli&data=05|01|hangx%40microsoft.com|d2117bfa41ad4203878508db503e5dc4|72f988bf86f141af91ab2d7cd011db47|1|0|638192001046754818|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=l8t4H095y03VbRfVEzSPNpO2pd2QNGubM5EW6vlklkQ%3D&reserved=0)简化了集成步骤，目的都是用户可以通过AAD验证连接登录到AKS集群。

- 用户若被赋予Azure Kubernetes Service Cluster Admin Role角色，在运行“ [az aks get-credentials](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fcli%2Fazure%2Faks%23az_aks_get_credentials&data=05|01|hangx%40microsoft.com|d2117bfa41ad4203878508db503e5dc4|72f988bf86f141af91ab2d7cd011db47|1|0|638192001046754818|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=FC%2BBZug1EUKUtMCWPXBxy4fKPoJDCLP1gux3z1cbXnc%3D&reserved=0) ”后会kubeconfig会获取到k8s集群下定义的clusterAdmin角色权限。
- 用户若被赋予Azure Kubernetes Service Cluster User Role角色，在运行“ [az aks get-credentials](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fcli%2Fazure%2Faks%23az_aks_get_credentials&data=05|01|hangx%40microsoft.com|d2117bfa41ad4203878508db503e5dc4|72f988bf86f141af91ab2d7cd011db47|1|0|638192001046754818|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=FC%2BBZug1EUKUtMCWPXBxy4fKPoJDCLP1gux3z1cbXnc%3D&reserved=0) ”后会kubeconfig仍为空，管理员需要为其在集群内赋予k8s RBAC role。
- 用户登录没有与AAD集成的AKS集群时，cluster User 角色具有的效果与 cluster Admin 角色相同，即所有用户登录时都是clusterAdmin角色。

**Use Kubernetes RBAC with Azure AD integration**，其中Kubernetes RBAC是k8s原生的访问控制方法，其角色定义和绑定只适用于集群内部资源的访问控制。在集成了AAD的AKS集群上，我们可以将k8s role绑定给AAD user/group，其综合效果为：

- 在Azure层面赋予用户Azure Kubernetes Service Cluster User Role角色使其可以连接到集群
- 在集群层面通过RoleBindings 和ClusterRoleBindings控制用户的访问权限

**Use Azure RBAC for Kubernetes authorization**是指在启用了managed AAD 集成以及azure RBAC的AKS集群上，用户在Azure层面被赋予特定角色后，k8s集群内也相应为该用户赋予了角色所对应的集群资源访问权限。即管理员只需要为用户在Azure层面赋予角色即可实现集群内部的权限控制，目前可用的内置角色参考[概念- Azure Kubernetes 服务(AKS) 中的访问和标识- Azure Kubernetes Service | Azure Docs](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Faks%2Fconcepts-identity%23built-in-roles&data=05|01|hangx%40microsoft.com|d2117bfa41ad4203878508db503e5dc4|72f988bf86f141af91ab2d7cd011db47|1|0|638192001046754818|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=RqY4pYm9FIge4BcIiMi461rhHE95VmqENxbSpEHsZJw%3D&reserved=0)。

![image-20231031165724202](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311657279.png)

# AKS计划内维护

[使用计划内维护来计划和控制 Azure Kubernetes 服务 (AKS) 群集的升级 - Azure Kubernetes Service | Microsoft Learn](https://learn.microsoft.com/zh-cn/azure/aks/planned-maintenance)

新添加一个：

```bash
az aks maintenanceconfiguration add -g myResourceGroup --cluster-name myAKSCluster -n aksManagedAutoUpgradeSchedule --schedule-type Weekly --day-of-week Friday --interval-weeks 3 --duration 8 --utc-offset +05:30 --start-time 00:00
```

更新已有的：

```bash
az aks maintenanceconfiguration update -g myResourceGroup --cluster-name myAKSCluster --name default --weekday Monday --start-hour 2
```



# AKS微服务架构示例

![image-20231031100726276](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311007396.png)