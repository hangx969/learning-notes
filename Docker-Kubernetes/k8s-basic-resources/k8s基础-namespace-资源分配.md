# namespace介绍

Namespace提供了一种将集群资源逻辑上隔离的方式，允许在同一个集群中划分多个虚拟的、逻辑上独立的集群环境，相当于集群的“虚拟化”。

命名空间namespace是k8s集群级别的资源，可以给不同的用户、租户、环境或项目创建对应的命名空间，例如，可以为test、devlopment、production环境分别创建各自的命名空间。

命名空间适用于存在很多跨多个团队或项目的用户的场景。对于只有几到几十个用户的集群，根本不需要创建或考虑命名空间。

创建ns：

```bash
kubectl create ns test
```

## 合理的资源划分

资源限制的重要性：如果没有，可能会产生节点资源被异常耗尽的问题。

pod数量限制的重要性：应对异常pod激增的问题。举个例子，对某个deployment下的pod，进行了内核修改配置（securityContext里面添加sysctl命令），但是如果集群没有允许更改内核参数，可能会报错sysctl forbidden，但是pod资源已经有了，这样的后果是RS会不断的创建pod，可能会直接创建上万个垃圾pod，严重的时候会直接把集群拖垮。

**生产环境一定针对每个ns，对pod数量和RS数量做限制，因为这两个资源是不受管控的资源，防止异常激增。比如限制ns级别的pod数量为512，RS数量为1024。**

### 以租户为单位

是针对ns去限制的。

1. 基于节点去划分：比如一个团队申请了5台8C16G机器加入集群，那么就限制这个团队的ns资源limit为40C80G。
2. 基于现有资源：利用现有资源，直接划分给这个团队固定的cpu和memory

### 以环境为单位

比如有dev、uat、prod等环境，需要预估每个环境的所有微服务情况，留一些冗余。

# ResourceQuota资源

ResourceQuota是k8s中用于资源管理的对象，限制ns中的资源使用量。可以：

- 限制资源使用量
- 限制对象数量

```yaml
apiVersion: v1
kind: ResourceQuota 
metadata: name: customer1-quota 
namespace: customer1 
spec: 
  hard: 
    # 下面的限制建议都打开
    count/pods: "100" 
    requests.cpu: "2" 
    requests.memory: 4Gi 
    limits.cpu: "8" 
    limits.memory: 16Gi
    count/replicasets.apps: 1k
    count/persistentvolumeclaims: "10" 
    requests.storage: 400Gi 
    count/services: "40"
```

> CPU的单位解释：[为 Pod 和容器管理资源 | Kubernetes](https://kubernetes.io/zh-cn/docs/concepts/configuration/manage-resources-containers/)
>
> CPU 资源的限制和请求以 “cpu” 为单位。 在 Kubernetes 中，一个 CPU 等于 **1 个物理 CPU 核** 或者 **1 个虚拟核**， 取决于节点是一台物理主机还是运行在某物理主机上的虚拟机。
>
> - 如果是request.cpu: 0.5 --> 那就是请求0.5个核
> - 如果是request.cpu: 500m --> 那是500毫核 --> 也就是0.5核

> 注意:
>
> - ns指定了ResourceQuota之后，如果创建的deployment没有显式指定requests和limits，那么pod会创建不出来。此时的状态就是deployment正常，但是pod实际数量为0，可以describe rs来看，也可以get events来看。
> - 新创建的resourceQuota，不会影响已经在运行的服务，但是一旦出发更新或者删除，那么就会产生影响，超过的就创建不出来了

# LimitRange资源

只配置了resourceQuota是不够的，想象这样一种例子：有一个pod设置request是1m/1Mi，有一个节点已经资源马上满了，但是还是可以接受这个pod，但是这个pod随着运行吃了更多资源，这个节点就满了。

这样是不行的，需要：

1. 对requests和limits的值也进行合理性的约束，不符合约束的就禁止创建；
2. 对于没有显式声明requests和limits的资源，添加上一个默认值。

在Kubernetes集群中部署任何的服务，都建议添加resources参数，也就是配置内存和CPU资源的请求和限制。如果不想给每个容器都手动添加资源配置，此时可以使用limitRange实现给每个容器自动添加资源配置（不会覆盖已经配置的值）。

~~~yaml
apiVersion: v1
kind: LimitRange 
metadata:
  name: cpu-mem-limit-range
spec:
  limits:
  - type: Container # 可以写container、pod
    default: # default就是limit的默认值
      cpu: 1 
      memory: 512Mi
    defaultRequest: # request的默认值
      cpu: 0.5 
      memory: 256Mi
    min: # requests不能小于这里的值
      memory: 32Mi
      cpu: 100m
    max: # limits不能大于这里的值
      memory: 1Gi
      cpu: 1
  - type: PersistentVolumeClaim # 限制PVC的存储大小范围（创建太多很小的PVC，可能会产生过多的存储碎片）
    max: 
      storage: 3Gi 
    min: 
      storage: 1Gi
~~~

> 注意：
>
> 1. limitRange是针对pod去修改的，deployment的yaml不会被修改。

# QoS

想象这样一个场景：节点上面的pod由于流量高峰，资源使用量上升，超出节点资源量。这时候节点会启动一些OOM Kill的机制，杀掉pod。如果有一些重要的pod不希望被杀掉，或者尽量在最后被杀掉，怎么去保护？

QoS：Quality of Service，表示程序的服务质量，K8s集群每一个pod，都会有对应的QoS级别，可以**决定pod在资源紧张时候的处理顺序**。同时可以确保关键服务的稳定性和可靠性。（QoS不是K8s的特性，Linux里面的程序也有服务质量的概念）

## Guaranteed

Guaranteed级别的Pod具有最高的优先级，Kubernetes会确保这些Pod获得足够的资源，也就是Kubernetes调度器会确保这些Pod调度到能够提供所需资源的节点上。

配置Guaranteed级别的Pod，需要满足如下条件：

1. Pod中的每个容器必须指定limits.memory和requests.memory，并且两者需要相等
2. Pod中的每个容器必须指定limits.cpu和requests.cpu，并且两者需要相等

~~~yaml
limits:
  cpu: 200m
  memory: 512Mi
requests:
  cpu: 200m
  memory: 512Mi
~~~

> 一般mysql、redis等基础组件，需要尽量配成Guaranteed，预估好资源，直接给他requests、limits配成一样的（给冗余多一点）

## Burstable

Burstable级别的Pod具有中等优先级，Kubernetes会尽量满足其资源请求，但在资源紧张时可能会被驱逐，Kubernetes调度器会确保这些Pod调度到能够提供所需资源的节点上，如果节点上有额外的资源，这些Pod可以使用超过其请求的资源。

配置Burstable级别的Pod，需要满足如下条件：

1. Pod不符合Guaranteed的配置要求
2. Pod中至少有一个容器配置了requests.cpu或requests.memory。（即这类服务知道最小用量，但是机器资源充足时会占用更多）

~~~yaml
requests:
  memory: 128Mi 
  cpu: 100m
~~~

## BestEffort

BestEffort级别的Pod是最低优先级，Kubernetes不保证这些Pod获得任何资源，在资源紧张时，这些Pod最先被驱逐。同时Kubernetes调度器会尝试将这些Pod调度到任何节点上，但不保证节点上有足够的资源。

配置BestEffort级别的Pod，不配置resources字段即可。



# ns删除后卡在terminating状态

- 需要手动结束finalizer

~~~sh
# 开启代理
kubectl proxy
# Starting to serve on 127.0.0.1:8001
# 新开终端
kubectl get namespace $NAMESPACE -o json > temp.json
# 编辑状态文件
vim temp.json
# 删掉以下三行：
"finalizers": [
   "controller.cattle.io/namespace-auth"
],
# 发送状态文件
curl -k -H "Content-Type: application/json" -X PUT --data-binary @temp.json 127.0.0.1:8001/api/v1/namespaces/$NAMESPACE/finalize
~~~

不推荐，还是建议先回收其中的资源再删除ns。

# 特殊namespace

## kube-node-lease

- 节点的心跳信息会存放在其中，api server去里面查看心跳信息，获取node状态。
