# master组件

## API server 

- 集群对外的统一入口，以RESTful API方式做操作。用户对集群控制的唯一入口


## scheduler

- 通过一定的算法算出工作负载到哪个节点

## controller manager

- 节点调度，做部署
- 处理集群的常规后台任务，一个资源对应一个控制器 

## etcd

- 存储系统


# worker node组件

## kubelet

- master派到node节点的代表，用来管理节点的容器，控制容器运行时来跑容器
- 新机器加入集群时，集群通过kubelet来发现这个机器

- kubelet会向集群报告heartbeat


- kubelet另一个重要功能是调用网络插件和存储插件为容器配置网络和持久化存储（CNI、CSI）


## kube-proxy

- 维护node的网络代理，实现服务发现、负载均衡等操作。


- apiserver是集群管理的入口，kubeproxy是具体容器对外提供服务的生产网络入口。


![image-20240725223852759](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202407252238859.png)

# 核心概念

## POD

- 最小部署单元，里面有若干容器。（一般只有一个）其余功能都是为POD所服务的。
- 内部容器的网络互通，是共享的
- 生命周期短暂，重启之后又变成新的POD
- k8s通过controller来管理POD 

## Controller

- pod有两种：
  - 1、自主式pod是直接创建出来的，删了就没了
  - 2、由控制器创建出来的，删了还能自动重建。
- 作用：在集群上管理运行容器。k8s不是直接管理pod，是通过controller来管理pod。
- controller有很多种类型：
  - ReplicaSet：保证副本数量一直维持在期望值，并支持pod数量扩缩容，镜像版本升级
  - Deployment：通过控制ReplicaSet来控制Pod，并支持滚动升级、回退版本
  - Horizontal Pod Autoscaler （HPA）：可以根据集群负载自动水平调整Pod的数量，实现削峰填谷
  - DaemonSet：在集群中的指定Node上运行且仅运行一个副本，一般用于守护进程类的任务
  - Job：它创建出来的pod只要完成任务就立即退出，不需要重启或重建，用于执行一次性任务
  - Cronjob：它创建的Pod负责周期性任务控制，不需要持续后台运行
  - StatefulSet：管理有状态应用
- controller和pod的关系
  - pod通过controller实现应用的运维，比如伸缩，回滚升级等
  - pod和controller通过label来建立关系
  - 由控制器创建出来的pod，删除之后还能自动重建

![image-20240725225330810](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202407252253954.png)

## service

- Service和ingress是流量负载的组件


- 虽然每个Pod都会分配一个单独的Pod IP，然而却存在如下两问题：

  - Pod IP 会随着Pod的重建产生变化
  - Pod IP 仅仅是集群内可见的虚拟IP，外部无法访问

这样对于访问这个服务带来了难度。因此，kubernetes设计了Service来解决这个问题。

- Service可以看作是一组同类Pod对外的访问接口。借助Service，应用可以方便地实现**服务发现**和**负载均衡**。


- Service的主要作用，就是作为 Pod 的代理入口，代替 Pod 对外暴露一个固定的网络地址。


- 四层代理：基于IP和端口

## label

- 标签，是一个键值对。可以对相同类型的pod打标签。


- service可按照标签来统一连接到指定的pod，对外提供服务


## namespace

- 命名空间，隔离pod的运行环境。可以把若干个pod划到一个namespace里面，这里面的可以互相访问。而不能访问其他namespace。
- 用来实现 **多套环境** 或者 **多租户** 的资源隔离：

  - 默认情况下，pod都是可以互相访问的，但是实际使用中可能不想让pod相互访问。将pod划分到不同的namaspace中，形成逻辑上的组。
  - 也可以利用授权机制，将不同的namespace交给不同的租户管理，实现多租户隔离，限定不同租户的使用资源的配额。

# 组件调用关系

- 以部署一个nginx服务来说明kubernetes系统各个组件调用关系：

![image-20240725223919761](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202407252239873.png)

- 首先要明确，一旦kubernetes环境启动之后，master和node都会将自身的信息存储到etcd数据库中

- 一个nginx服务的安装请求会首先被发送到master节点的apiServer组件 

- apiServer组件会调用scheduler组件来决定到底应该把这个服务安装到哪个node节点上

-   scheduler从etcd中读取各个node节点的信息，然后按照一定的算法进行选择，并将结果告知apiServer

- apiServer调用controller-manager去调度Node节点安装nginx服务

- kubelet接收到指令后，会通知docker，然后由docker来启动一个nginx的pod

至此，一个nginx服务就运行了，如果需要访问nginx，就需要通过kube-proxy来对pod产生访问的代理，这样外界用户就可以访问集群中的nginx服务了

# kubectl命令

- k8s中所有的内容都抽象为资源，可以通过kubectl api-resources 来查看


- kubectl的运行是需要配置文件的，而这个配置文件是master节点上的 $HOME/.kube 目录下；如果要在node节点上运行此命令，需要将master节点上的.kube文件复制到node节点上，即在master节点上执行下面操作:


```sh
scp -r HOME/.kube node1:HOME/.kube
```

# Api-resource类型

| **资源分类**  | **资源名称**             | **缩写** | **资源作用**    |
| ------------- | ------------------------ | -------- | --------------- |
| 集群级别资源  | nodes                    | no       | 集群组成部分    |
|               | namespaces               | ns       | 隔离Pod         |
| pod资源       | pods                     | po       | 装载容器        |
| pod资源控制器 | replicationcontrollers   | rc       | 控制pod资源     |
|               | replicasets              | rs       | 控制pod资源     |
|               | deployments              | deploy   | 控制pod资源     |
|               | daemonsets               | ds       | 控制pod资源     |
|               | jobs                     |          | 控制pod资源     |
|               | cronjobs                 | cj       | 控制pod资源     |
|               | horizontalpodautoscalers | hpa      | 控制pod资源     |
|               | statefulsets             | sts      | 控制pod资源     |
| 服务发现资源  | services                 | svc      | 统一pod对外接口 |
|               | ingress                  | ing      | 统一pod对外接口 |
| 存储资源      | volumeattachments        |          | 存储            |
|               | persistentvolumes        | pv       | 存储            |
|               | persistentvolumeclaims   | pvc      | 存储            |
| 配置资源      | configmaps               | cm       | 配置            |
|               | secrets                  |          | 配置            |
