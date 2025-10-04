# k8s高可用和节点规划

## 节点数量规划

1. 部署多个节点达到总部署服务的要求（每个节点配置可以小些），缺点：管理机器多

2. 部署少量工作节点达到部署服务要求（每个节点配置可以大些），缺点：在更少的节点上运行相同的工作负载自然意味着在每个节点上运行更多的pods，每个pod在运行在节点上的Kubernetes代理上引入了一些开销——比如容器运行时(例如Docker)、kubelet和cAdvisor。
   - 例如，kubelet对节点上的每个容器执行定期的活性和准备性探测——容器越多，意味着kubelet在每次迭代中要做的工作就越多。
   - cAdvisor收集节点上所有容器的资源使用统计信息，kubelet定期查询这些信息并在其API上公开——同样，这意味着在每次迭代中cAdvisor和kubelet都要做更多的工作。如果Pod的数量变大，这些事情可能会开始降低系统的速度，甚至使系统变得不可靠。

3. 如果没有前期的压测数据，一般先采用3 master、2 worker的配置，后期不够了再加节点。

   - 如果没有任何应用的数据，默认给这个最低配置：
   
     - master：8G/8vCPU
     - worker：12G/12vCPU
   - 有应用规划的话，就算一下所有应用的内存、vCPU的占用总和，算上pod副本数来规划配置。
   
   - 一般来说etcd是装在控制节点上的。单独找机器装etcd也行，但是不省钱。
   
   - 3 master是为了etcd的计数选举机制的高可用。 
   
     > etcd一般做3个或者5个备份 - 因为有奇数选举机制：
     >
     > - leader选举算法采用了paxos协议。
     >
     > - paxos核心思想：当半数以上server写成功，则任务数据写成功。如果有3个server则2个写成功即可，当有4个或5个server，则3个写成功即可。服务器数量一般为单数个：如果有3个server，最多允许有一个server挂掉，如果有4个server，则同样最多允许一个server挂掉。因此，3台服务器和4台服务器的容灾能力是一样的，为了节省服务器资源，我们通常采用奇数数量。

- 3 master管理**900个worker**都是够用的

## 日志和监控

- 监控系统：prometheus+alertManager+grafana
- 日志平台：EFK = Elasticsearch + kibana + filebeat/fluentd （节点日志+容器日志）

## 服务高可用规划

从服务分布考虑，同一个服务的多个副本：

- 最好是要打散在不同的节点上，提高服务可用性。
- 如果节点在不同机房，也要分布在不同机房上，提高容灾能力。

（pod之间的反亲和力）

## 服务性能规划

多工作节点的集群，某一些节点可能用的是高性能SSD，节点性能很强。对于计算密集型的服务，需要尽量部署在上面（特殊应用部署到专用节点，提升应用性能）。（节点亲和力）

某些集群有一些GPU节点，让不需要GPU的服务尽量不去调度到GPU节点上。（污点容忍）

相互依赖的服务，尽量调度到同一个域内。

# 如何使用k8s管理应用

## 1 dockerfile制作镜像

- 镜像分为：
  - 基础镜像：centos、rocklinux、ubuntu、debian等
  - 服务镜像：openjdk、nginx、mysql、tomcat等
  - 项目镜像
- java或者go代码需要编译
  - java：mvn编译，生成一个jar包或者war包，放到镜像里
  - go: go build编译，生成一个二进制文件
- php和python可以不用编译
  - py文件直接放到镜像里运行即可

## 2 创建pod

- deployment
- statefulset
- daemonset
- job、cronjob

## 3 数据持久化

- 容器部署过程中一般有三种数据：
  - 容器启动需要的数据，可以是配置文件
  - 启动过程产生的临时数据，需要多个容器共享
  - 运行过程中产生的业务数据
- 采用hostPath、emptyDir、NFS等方式存储或共享

## 4 创建四层代理

- 使用svc的ClusterIP暴露集群内访问，四层代理pod
- svc的名称和IP是由coredns来解析的

## 5 创建七层代理

- 一般是网站类的服务，通过ingress对外暴露应用，通过svc关联pod。
- 通过ingressController实现pod负载均衡
- 支持基于请求头、权重、域名等切分流量，支持TCP/UDP四层和HTTP七层的代理

## 6 日志与监控

- prometheus监控资源状态
- 使用EFK+logstash+kafka收集应用日志

# apiserver优化

kube-apiserver是整个集群的所有请求的入口，apiserver不可用会导致集群失效。可以从以下几个方面优化：https://kubernetes.io/docs/reference/command-line-tools-reference/kube-apiserver/，参数优化需要在`/etc/kubernetes/manifests/kube-apiserver.yaml`文件中编辑参数

1. apiserver部署多个实例，前端用SLB做负载均衡，提供可用性。
2. 参数优化：`--max-requests-inflight`=1500
3. 参数优化：`--request-timeout`=300s
4. 参数优化：`--max-mutating-requests-inflight`
   - 给定时间内最大的并发请求数。这个参数的值被设置为 n 时，控制器会同时处理 n 个 mutating 请求，其他的请求则会被放到队列中等待
   - 如果三个apiserver做高可用，物理机配置是4g内存，4vcpu，那么max-mutating-requests-infligh如何配
     置？根据官方建议，每个kube-apiserver处理的最大mutating请求数应该限制在500-1000之间。在一个三节点
     的高可用集群中，可以将这个值设置为3000左右。具体以压测为准。
   - 在进行压测时，可以观察以下指标来评估max-mutating-requests-inflight的值是否适当：
     1）平均响应时间（Response time）：如果max-mutating-requests-inflight过小，可能会导致一些请求
     被阻塞，延长了平均响应时间。
     2）请求成功率（Success rate）：如果max-mutating-requests-inflight设置过大，会导致过多的请求同
     时进入apiserver，导致系统过载，请求成功率下降
5. 参数优化：`--watch-cache-sizes`
   - 每个API请求都会触发API Server的相应操作，如查询、创建、修改和删除等，而watch API请求则会触发API Server对相关对象的监听，并实时返回相应的变更信息。当watch对象数量较大或者频繁变更时，会产生大量的watch事件，如果API Server不能及时处理，就可能导致响应延迟或者watch事件丢失。为了解决这个问题，Kubernetes引入了watch缓存机制，用于在API Server中缓存watch API请求返回的对象列表。通过调整watch-cache-size参数可以控制watch缓存的大小，从而保证API Server的正常运行。某些资源（Pod、Node 等）的监视缓存大小设置，以逗号分隔。每个资源对应的设置格式：resources#size，例如：例如：`--watch-cache-size=nodes#1000,pods#5000`
   - 可以通过监控watch事件的响应时间和缓存命中率等指标，来评估和调整watch-cache-size的值。建议为每个node节点配置watch-cache-size为node的pod数量的两倍左右，这样可以确保所有对象都能被缓存，并且不会出现过度缓存导致的性能问题
6. etcd多实例支持：对于不同的object进行分库存储，数据和状态分离，即将event放在单独的etcd实例中。
   - Kubernetes 1.22及之前版本的etcd是由Kubernetes自己管理的，不允许将状态和网络插件存储在不同的etcd
     集群中。但是从Kubernetes 1.23版本开始，用户可以将Kubernetes状态存储和网络插件存储放在不同的etcd
     集群中，例如：--etcd-servers-overrides=main-etcd:2379=http://main-etcd:2379,network-
     etcd:2379=http://network-etcd:2379
   - 也可以将pods, nodes等object也分离在单独的etcd实例中

# controller-manager优化

> https://kubernetes.io/docs/reference/command-line-tools-reference/kube-controller-manager/
>
> 负责处理各种资源的自动化控制，如Deployment、DaemonSet等。优化Controller Manager的参数可以提高Kubernetes的性能和稳定性

1. `--controllers`参数：
   - 可以通过该参数限制Controller Manager启动的控制器数量。默认情况下，Controller Manager会启动所有控制器，但在实际情况中，可能只需要启动一部分控制器。
   - 根据实际情况，可以选择需要的控制器，避免启动不需要的控制器导致性能损失。例如：--controllers=replicaset,deployment
2. `--concurrent-deployment-syncs`参数：
   - 这个参数指的是控制器每次可以并发处理的最大同步数。每个Deployment都有可能涉及到多个Pod的创建、删除、更新等操作，这些操作会被控制器处理并同步到Kubernetes集群中。而该参数限制了控制器一次可以处理的最大同步数，即控制器在同步过程中，最多可以并发处理的Deployment数量。
   - 默认情况下，每个Deployment控制器最多可以同时同步10个Deployment。如果实际环境中部署了大量的Deployment，可以适当增加该参数的值。例如：--concurrent-deployment-syncs=20。
   - --concurrent-statefulset-syncs同理
3. `--node-monitor-grace-period`参数：
   - 控制的是节点失联的容忍时间，即 Kubernetes master 节点会等待多久来检测节点是否掉线。默认值是 40 秒，当节点在这个时间内无法与 API server 连接时，它将被视为不可用。
   - 作用是保护短时间的网络故障，防止假阳性的掉线。当一个节点真的宕机时，节点的kubelet 会通知 API server 并将节点标记为不可用，如果实际环境中节点数量较大，可以适当调整该参数的值，以避免控制器因等待时间过长而导致性能下降。例如：--node-monitor-grace-period=10s。
4. `--terminated-pod-gc-threshold`参数：
   - 定义了 kubelet 清理终止的 pod 的最短时间。当一个 pod 终止时，kubelet 将在 terminated-pod-gc-threshold 之前等待清理 pod，如果超过这个时间，kubelet 将清理该 pod 的所有数据，包括日志、容器工作区等。
   - 这个参数的设置应该考虑集群规模和资源限制。如果集群中 Pod 数量较多，可以适当调高这个值，以减轻 API Server 的压力。但是如果设置得太高，可能会影响垃圾回收的效率，导致系统资源浪费。
   - 如果你的集群中有大量的短期任务，可以将这个值设置得更低一些，例如 30 分钟。如果你的集群中只有少量的长期任务，可以将这个值设置得更高一些，例如 6小时。

# kubelet优化

https://kubernetes.io/zh-cn/docs/concepts/architecture/nodes/

1. 使用 Node Status Update Frequency减少心跳上报频率
   - Kubelet 心跳上报频率可以通过调整 --node-status-update-frequency 参数来进行优化。
   - 默认情况下，该参数的值为 10s，即每 10s 向 Kubernetes API Server 报告一次 Node 状态信息。如果调整该值，可以减少
     Kubelet 发送心跳请求的频率，从而减轻 API Server 的压力，提高系统性能。
   - 如果你的集群中有大量的节点（例如1000个以上），则建议将该参数设置为30s或更高的值。如果你的集群中只有几十个节点，则可以将该参数设置为默认值10s或稍微调高一些。

2. 为了进一步减轻 API Server 的压力，可以使用 Node Release 功能。该功能可以在 Node 不再存在时，立即从 Kubernetes API Server 中删除 Node 相关的资源。这样可以避免过期的 Node 对系统性能造成的负面影响。
   - 要启用 Node Release 功能，需要在 Kubelet 配置文件中添加以下参数：--feature-gates="NodeRelease=true"

3. `--eviction-hard`参数优化：
   - 该参数用于设置pod内存和CPU使用量的硬阈值。
   - memory.available：系统中可用内存的阈值，单位为字节。如果系统中可用内存低于这个阈值，kubelet将开
     始驱逐一些pod。
   - nodefs.available：系统可用磁盘空间的阈值，单位为字节。如果系统中可用磁盘空间低于这个阈值，
     kubelet将开始驱逐一些pod。

4. `--eviction-soft`参数优化：
   - 设置Pod驱逐的软性限制。当达到软性限制时，kubelet会给Pod一个grace period（默认是30秒）的时间，等待Pod自行退出，如果超过该时间仍未退出，则kubelet会尝试强制驱逐Pod。
   - --eviction-soft=memory.available=1.5Gi,nodefs.available=10%,nodefs.inodesFree=5%，这个参数设置了内存可用空间至少为 1.5GB，磁盘可用空间至少为总磁盘空间的 10%，inode 可用数量至少为总 inode 数量的 5%。如果节点上的资源使用超出这些限制，kubelet 会尝试释放缓存等资源，以避免驱逐 pod。如果这种方式无法释放足够的资源，才会考虑驱逐 pod。

# kube-scheduler优化

https://kubernetes.io/zh-cn/docs/concepts/scheduling-eviction/scheduler-perf-tuning/

1. `--percentage-of-nodes-to-score`
   - 是kube-scheduler的一个配置参数，用于设置每次调度器评分时要评估的节点百分比。这个参数的作用是优化调度器的性能，减少评估所有节点的时间和资源消耗。
   - 当kube-scheduler需要为一个Pod选择一个节点时，它会评估所有满足要求的节点，并计算它们的得分，然后选
     择得分最高的节点来运行Pod。如果集群中的节点数量很大，评估所有节点的得分会消耗大量时间和资源，这时可
     以通过设置--percentage-of-nodes-to-score来限制每次评分的节点数量。
   - 例如，假设设置--percentage-of-nodes-to-score为50，kube-scheduler在评估节点得分时只会评估50%的节点，即随机选择50%的节点进行评估，然后选择其中得分最高的节点来运行Pod。这样可以减少评估时间和资源消耗，提高调度器的性能。
   - 需要注意的是，设置--percentage-of-nodes-to-score的值过小可能会影响调度器的精度，因为它评估的节点
     数量越少，得分越容易受随机因素的影响

2. `--preemption`用于设置调度器的预抢占策略。这个参数的作用是在调度器无法为一个Pod找到满足要求的节点时，尝试通过预抢占其他Pod来腾出资源。
   - 当kube-scheduler需要为一个Pod选择节点时，如果找不到满足要求的节点，就会尝试使用预抢占策略。如果设
     置了--preemption参数，kube-scheduler会查找集群中已经运行的、优先级较低的Pod，并尝试将它们从当前
     节点上驱逐，以腾出资源给优先级较高的Pod。这样可以提高调度器的效率，减少Pod无法调度的情
     况。
   - 需要注意的是，使用预抢占策略可能会对系统的稳定性产生一定的影响。因为抢占其他Pod可能会导致这些Pod的
     性能下降，甚至出现故障。因此，在使用--preemption参数时，需要谨慎考虑集群的负载情况、Pod的优先级和
     抢占策略等因素，以确保系统的稳定性和可靠性
   - 另外，需要注意的是，--preemption参数的默认值为false，即kube-scheduler默认不启用预抢占策略。如果需
     要使用预抢占策略，必须将--preemption参数设置为true。

# k8s网络优化

1. flannel

   - flannel可以为Pod分配IP地址，不负责实现网络策略隔离。flannel支持三种不同的网络模式，分别是host-gw模式、vxlan模式和UDP模式。

   1、host-gw模式

   - 在host-gw模式下，flannel会在每个节点上创建一个虚拟网卡，然后将该虚拟网卡的IP地址设置为节点的实际IP地址。然后，flannel会将每个节点的虚拟网卡信息发布到etcd集群中，其他节点通过etcd获取该信息，然后可以通过虚拟网卡与其他节点通信。host-gw模式的优点是性能高、简单易用，缺点是不支持跨VPC/VLAN网络，需要节点IP地址在同一网段内。

   - VPC是Virtual Private Cloud的缩写，是指虚拟专用云，是一种基于云技术的网络隔离方案，用于隔离不同的云资
     源（例如云服务器、云数据库等）。

   - VLAN是Virtual Local Area Network的缩写，是指虚拟局域网，是一种将物理局域网划分为多个虚拟局域网的
     技术，可以实现不同网络设备的分段管理和通信隔离。

   - 通过启动参数 --ip-masq=false 禁用 masquerading，然后通过 --public-ip=<public_ip> 指定主机IP地址。如：

     flanneld --etcd-endpoints=$ETCD_ENDPOINTS --etcd-prefix=$FLANNEL_ETCD_PREFIX --iface=$IFACE --ip-masq=false --public-ip=$HOST_IP

   2、vxlan模式

   - 在vxlan模式下，flannel会在每个节点上创建一个vxlan接口，将不同节点的vxlan接口通过UDP隧道连接在一起，以实现跨节点通信。vxlan模式的优点是可以跨VPC/VLAN网络，缺点是需要支持VXLAN技术，会增加一定的网络延迟。

   - 通过启动参数 --vni=<VXLAN_VNI> 指定 VXLAN 网络标识 (VNI)。如：

     flanneld --etcd-endpoints=$ETCD_ENDPOINTS --etcd-prefix=$FLANNEL_ETCD_PREFIX --iface=$IFACE --vni=1

   3、UDP模式，现在用的很少了。

   - 在UDP模式下，flannel会通过UDP协议来实现容器之间的通信，每个节点都会绑定一个UDP端口，然后通过路由表将容器的流量转发到正确的节点。UDP模式的优点是可以跨VPC/VLAN网络，同时不需要支持VXLAN技术，缺点是会增加一定的网络延迟和CPU消耗。

