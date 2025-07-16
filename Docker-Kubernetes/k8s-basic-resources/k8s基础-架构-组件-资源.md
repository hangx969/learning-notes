# K8s基本概念

Kubernetes（简称K8s，希腊语，意为舵手）是一个开源的容器编排系统，用于容器的自动化部署、扩展，以及提供高可用和负载均衡的运行环境。

Kubernetes 提供了一个便携、高效的PaaS 平台，降低了在物理机或虚拟机上调度和运行服务的难度，同时Kubernetes 还整合了网络、存储、安全、监控等能力，是一个非常完善的“云原生操作系统”。

## 里程碑

Kubernetes 的前身是谷歌内部的Borg系统，是基于谷歌15年生产环境经验的基础上开源的一个项目。

1. 由谷歌设计并在2014年开源。
2. 2015年7月第一个稳定版V1.0正式发布。
3. 之后捐献给了CNCF，成为CNCF第一个开源的顶级项目。
4. 2018年从CNCF毕业。目前已成为云原生领域的标准。

## K8s的优势

**有了docker为什么还要用K8s？因为只使用docker：**

1. 缺乏完整的声明周期管理（前置、后置处理）
2. 缺乏服务发现、负载均衡、配置管理、存储管理
3. 程序的扩容、部署、回滚、更新不够灵活
4. 宿主机宕机，容器无法自动恢复、漂移。
5. 程序级健康检查不到位
6. 端口管理比较复杂
7. 流量管理比较复杂

**K8s的优势：**

- 开源开放
- 弹性伸缩（副本数伸缩，节点伸缩）
- 服务发现（svc通过endpoint连接后端pod服务）
- 负载均衡（svc可以提供负载均衡）
- 自愈能力（节点挂了，pod自动漂移）
- 健康检查（三种probe，四种检测方式）
- 滚动更新（新服务完全启动后，旧服务才会被删掉）
- 一键回滚
- 高可用
- 声明式（yaml文件描述期望的状态，k8s帮忙实现）
- 多环境（支持多种容器平台）
- 隔离性（namespace隔离，资源控制）

## K8s带来的效益和挑战

对于开发人员，有了K8s之后：

1. 多环境日志查询困难 --> 无需登录机器就可以查看日志
2. 多环境代码发布困难 --> 不可变基础设置+CICD一键发布
3. 多环境搭建过程复杂 --> namespace隔离、一键备份还原
4. 无关代码占用大量精力（负载均衡、服务发现、高可用） --> 只需要关心业务代码
5. 环境迁移繁琐 --> 通过包管理工具一键迁移

对于运维人员：

1. 基础环境管理难度大 --> 一次构建多次部署
2. 宕机人工处理耗费精力 --> 全自动容灾无需干预
3. 应用扩容繁琐且复杂 --> 一键扩容无需更改配置
4. 中间件搭建维护困难 --> 包管理工具一键安装管理
5. 程序端口维护很麻烦 --> 无需关心端口冲突

仅仅掌握K8s还不够，还需要借助其他的周边生态去扩展K8s的能力：日志收集、监控告警、链路追踪等。Operator、Helm、Devops、Service Mesh等。

# K8s架构

## 集群组件

### 控制节点

#### API server

原生组件

- 其他组件之间相互通信，都不是直接通信的，是通过API server中转的。
- 集群操作的入口。为资源提供增删改查、watch的接口。
- 将集群资源信息存到etcd中。只有api server会和etcd交互

#### scheduler

原生组件

- 监听API server获取pod状态，发现pod.spec.nodeName为空就开始调度pod。
- 通过调度算法，将pod分配到最佳的节点。节点上的kubelet负责启动pod。

#### controller manager

原生组件

- 状态管理器，保证pod等资源达到期望状态。
- 如果资源未达到目标状态，会尝试自动修复并达到期望状态。

> - scheduler和controller manager是有状态组件，只有一个主节点在工作。
> - 主节点信息保存在了leases资源中，可以通过`kubectl get leases -n kube-system`获取，也可以进行横向扩容，选主过程无需人工干预

#### Etcd

- 不算核心组件，是coreOS开发的键值数据库，通常被部署在控制节点上
- 生产环境中建议部署为大于3的奇数个的Etcd节点，以保证数据的安全性和可恢复性，并且Etcd的数据盘需要使用SSD硬盘。

（kube-proxy、kubelet、runtime也都会在master上部署一份）

> 以上四个系统组件，对于kubeadm安装的集群来说，他们是静态pod形式启动的，查看他们的yaml的时候，会看到一个字段：`staticPodPath: /etc/kubernetes/manifests`，在这个目录下存放着这些pod的yaml，kubelet启动的时候会把他们直接拉起来。这个目录里面的文件都会自动被kubelet启动。

### 工作节点

#### Kube-proxy 

原生组件，可选

- 维护节点上面的网络规则，让集群内外的网络与pod进行通信。（通过ipvs等）
- 负责维护svc和pod之间的请求路由和流量转发。
- 容器对外提供服务的网络入口

> 如果使用Cilium作为CNI组件，可以不安装Proxy。

#### Kubelet

原生组件

- 管理pod，对容器进行健康检查
- 给Api server上报节点和pod状态
- 调用CNI和CSI给容器配置网络和存储

#### Runtime

- 符合CRI标准的都可以，管理容器的生命周期

#### Addons（CoreDNS，Calico）

- CoreDNS：用于集群内部的svc的域名解析，和上游域名的解析转发。让pod把svc的域名解析成svc的IP；对于外部域名可以转发到外部DNS进行域名解析。
- Calico：符合CNI标准的网络插件，负责给每个pod分配一个不会重复的IP。并且把每个节点当做路由器，一个节点的pod可以通过pod的IP访问到其他节点的pod。（跨节点通信，linux内核转发机制）

### 客户端工具

`kubectl + /etc/kubernetes/admin.conf (~/.kube/config)`

## 交互链路

1. 用户发起请求，API server接受请求完成认证鉴权。
2. API server把请求存到etcd
3. scheduler、controller manager、kubelet通过watch的机制监听api server的变化
4. controller manager watch到变化，将请求翻译成模板，比如需要多少资源，多少副本等。返回给API server，存到etcd。
5. scheduler watch到变化，通过api server获取节点信息，通过调度算法打分，选择最优节点去调度pod，更新pod.spec.nodeName字段。返回给api server，存到etcd中
6. 对应节点上的kubelet watch到这个调度请求，通过CRI接口调用容器运行时去创建pod。
7. kube-proxy监听到新pod，维护endpoint，通知api server，写到etcd中。


![image-20240725223852759](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202407252238859.png)

# 核心资源

## 最小单元pod

- 最小部署单元，里面有若干容器。（一般只有一个）其余功能都是为POD所服务的。
- 内部容器的网络互通，是共享的
- 生命周期短暂，重启之后又变成新的POD
- k8s通过controller来管理POD

## 调度资源

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
  - StatefulSet：管理有状态应用。给每一个pod分配固定标识，直接访问。
- controller和pod的关系
  - pod通过controller实现应用的运维，比如伸缩，回滚升级等
  - pod和controller通过label来建立关系
  - 由控制器创建出来的pod，删除之后还能自动重建

![image-20240725225330810](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202407252253954.png)

## 任务管理

crobjob、job

## 服务发布

Endpoint、service（东西流量：服务间访问）、ingress（南北流量：集群 外部访问pod）

## 配置管理

configMap，secret

## 存储管理

PV、PVC

## namespace

提供软隔离，大部分资源是被namespace隔离的，比如A ns里面的pod无法读取到B ns里面的configMap。

# kubectl命令


- kubectl的运行是需要配置文件的，配置文件一开始存在master节点上的`/etc/kubernetes/admin.conf`下，拷贝到`$HOME/.kube/config` 。如果要在其他地方运行此命令，需要将master节点上的config文件复制过去。

# Api-resource类型

k8s中所有的内容都抽象为资源，可以通过kubectl api-resources 来查看

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
