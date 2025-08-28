# 背景

## 传统服务发布

服务发布种类总结：

1. 外部用户访问
2. 服务间访问
3. 基础组件访问（数据库等组件）

在无注册中心的情况下：外部用户和服务间访问，往往通过一层代理层（Nginx/SLB）代理到后端服务；基础组件访问是直接配置数据库的IP+端口号来访问。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202507172057914.png" alt="image-20250717205717693" style="zoom:50%;" />

在有注册中心的情况下：服务间访问，通过注册中心拿到其他服务的IP+端口号直接连。外部用户的请求通过代理层（nginx/SLB）转发请求给网关层（Gateway），网关层转发请求到各个服务。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202507172055211.png" alt="image-20250717205553958" style="zoom: 50%;" />

k8s中（有注册中心，比如Eureka，虽然这样不推荐但是有时候没办法）：sts类型的服务把自己的headless svc写到注册中心就行了，不用写pod IP。deploy还是要写pod IP。网关也要写ingress暴露出去。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202507172058901.png" alt="image-20250717205802735" style="zoom:50%;" />

K8s中（无注册中心）：服务间访问、基础组件访问走的是svc，外部用户访问走的是ingress-svc-pod。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202507172058270.png" alt="image-20250717205834038" style="zoom:50%;" />

## pod ip访问

- 虽然每个Pod都会分配一个单独的Pod IP，然而却存在如下两问题：

  -   Pod IP 会随着Pod的重建产生变化

  -   Pod IP 仅仅是**集群内可见的虚拟IP**，外部无法访问 

# service介绍

- 这样对于访问这个服务带来了难度。因此，kubernetes设计了Service来解决这个问题，service在生命周期内，IP地址不会变。service通过标签选择器绑定相应的pod，可以通过访问service的ip来访问pod的服务。
- Service可以看作是一组同类Pod对外的访问接口。借助Service，应用可以方便地实现服务发现和负载均衡。

总结：svc为pod提供了一个抽象层，将一组具有相同功能的Pod抽象为一个逻辑上的服务。无论匹配的pod如何变化，比如重启、迁移、扩缩容等，service都能保持一个稳定的访问接口。我们不需要关心pod的具体IP和节点等细节。

## endpoint

k8s在创建Service时，会根据标签选择器(lableSelector)来查找Pod，据此创建与Service同名的endpoint对象。当Pod 地址发生变化时，endpoint也会随之发生变化。

service只是过滤出来要把流量代理到哪些pod上，实际pod信息是endpoint保存的。

service接收前端client请求的时候，就会通过endpoint，找到转发到哪个Pod进行访问的地址。(至于转发到哪个节点的Pod，由负载均衡kube-proxy决定)。



# 实现原理

- Service在很多情况下只是一个概念，真正起作用的其实是`kube-proxy`服务进程，每个Node节点上都运行着一个kube-proxy服务进程。

- 当创建Service的时候会通过api-server向etcd写入创建的service的信息，而kube-proxy会基于watch的机制发现这种Service的变动，然后它会将最新的Service信息转换成对应的**转发规则**。

- 也就是说，表面上看是创建了一个service，对应若干pod，但是**底层会被kubeproxy转换成对应的访问规则**，这种规则根据kubeproxy工作模式的不同，会有不同的规则，如iptables，ipvs规则等。实际工作的是访问规则。 

  ![image-20231111110951734](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311111109863.png)

## Kubeproxy工作模式

### Userspace

userspace模式下，kube-proxy会为每一个Service创建一个监听端口，发向Cluster IP的请求被Iptables规则重定向到kube-proxy监听的端口上，kube-proxy根据LB算法选择一个提供服务的Pod并和其建立链接，以将请求转发到Pod上。 该模式下，kube-proxy充当了一个四层负责均衡器的角色。由于kube-proxy运行在userspace中，在进行转发处理时会增加内核和用户空间之间的数据拷贝，虽然比较稳定，但是效率比较低。

![image-20231111111348557](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311111113677.png)

 目前已废弃不用了。

### iptables

Iptables 是 Linux 原生提供的一个功能强大的防火墙工具，可以用来设置、维护和检查 IPv4 数据包，并且支持源目地址转换等规则。在 iptables 代理模式下， kube-proxy 通过监听 Kubernetes API Server 中 Service 和 Endpoint 对象的变化，动态地更新节点上的 iptables 规则，以实现请求的转发。

iptables模式下，kube-proxy为service后端的每个Pod创建对应的iptables规则，直接将发向Cluster IP的请求重定向到一个Pod IP。该模式下kube-proxy不承担四层负责均衡器的角色，只负责创建iptables规则。

工作流程：
1.  当 Service 被创建或更新时， kube-proxy 会读取 Service 和 Endpoint 对象的信息，并生成相应的 iptables 规则
2.  这些 iptables 规则被添加到内核的 netfilter 处理链中，以拦截和转发目标为 Service IP 地址的流量
3.  当客户端访问 Service 的 IP 地址时， iptables 规则会将流量随机重定向到后端的一个或多个Pod

优点与缺点：

- 优点：iptables 是 Linux 内核的一部分，性能稳定、可靠，iptables 规则易于理解和维护，功能多。较userspace模式效率更高。

- 缺点：随着 Service 数量的增加，iptables 规则的数量也会急剧增加，进而导致性能下降（svc到达几千个的数量级时）。iptables的更新操作可能会暂时锁定整个 iptables 规则表，影响网络性能。不能提供灵活的LB策略，当后端Pod不可用时也无法进行重试。（采用线性表，从上到下一条一条查，性能很低）

> - 在 Kubernetes v1.29 中，Kubernetes 使用 nftables 作为 kube-proxy 新的后端，此功能现在是 Alpha 版本。 iptables 存在无法修复的性能问题，随着规则集大小的增加，性能损耗不断增加。很大程度上由于其无法修复的问题， 内核中 iptables 的开发速度已经放缓，并且大部分已经停止。新功能不会添加到 iptables 中，新功能和性能改进主要进入 nftables。 nftables 能完成 iptables 能做的所有事情，而且做得更好。 --- https://docs.daocloud.io/blogs/231213-k8s-1.29/

![image-20231111111411881](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311111114959.png)

### ipvs

IPVS（IP  Virtual Server）是一种基于内核的负载均衡器，ipvs模式和iptables类似，kube-proxy监控Pod的变化并创建相应的ipvs规则。

ipvs相对iptables转发效率更高（采用hash表，svc数量达到一定规模时，hash表的优势就体现出来了）（超过4k个svc后，ipvs的性能会显著超过iptables）。除此以外，ipvs支持更多的LB算法。

在 IPVS 代理模式下， kube-proxy 通过配置 IPVS 负载均衡器规则来代替使用 iptables。IPVS 使用更高效的数据结构（如 Hash表）来存储和查找规则，可以在大量 Service 的情况下也能保持高性能。

**工作流程：**

1.  当 Service 被创建或更新时，kube-proxy 会读取 Service 和 Endpoint 对象的信息，并配置IPVS 负载均衡策略
2.  IPVS 负载均衡器会根据配置的调度算法（如轮询、最少连接等）将请求转发到后端的一个或多个 Pod 上
3.  当客户端访问 Service 的 IP 地址时，请求会直接被 IPVS 处理并转发到后端 Pod

**优点与缺点：**

- 优点：IPVS 专为负载均衡设计，性能优于 iptables。并且支持多种调度算法，可以根据实际需求选择合适的算法，同时 IPVS 的更新操作对性能的影响较小
- 缺点：在某些情况下，IPVS 可能需要依赖 iptables 来实现一些额外的功能（如源地址 NAT）

**IPVS 负载均衡算法：**

- 【默认值】【不推荐】轮询：rr，按顺序轮流将请求转发到后端的各个 Pod 上，实现请求的均匀分配。
- **【推荐】最小链接数**：lc，将新的请求转发到当前连接数最少的 Pod 上，以平衡各 Pod 的负载
- 源地址哈希：sh，根据请求的源 IP 地址进行哈希计算，将相同源地址的请求转发到同一个 Pod 上，实现会话保持
- 目的地址哈希：dh，根据请求的目的 IP 地址（即 svc 的 Cluster IP）和端口进行哈希计算，选择后端 Pod
- 无需队列等待：nq，如果后端 Pod 的队列为空，则直接选择该 Pod；如果所有 Pod 的队列都非空，则采用其他策略（如轮询或最少连接）来选择 Pod
- 最短期望延迟：sed，考虑 Pod 的当前连接数和连接请求的平均处理时间，选择预计处理时间最短的 Pod 来接收新请求

> 注意：
>
> - 不推荐默认的轮询算法是因为如果某个节点由于性能问题（比如cpu、内存高），导致上面pod处理请求比较慢，但是轮询是感知不到的。会导致请求不断还是会继续发送到这个节点的pod上，导致这个pod一直cpu飚高，但是其他pod空闲。

![image-20231111111435638](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311111114753.png)

## 负载分发策略

对Service的访问被分发到了后端的Pod上去，目前kubernetes提供了两种负载分发策略：

-   如果不定义，默认使用**kube-proxy的策略**，比如随机、轮询。
-   基于**客户端地址的会话保持模式**，即来自**同一个客户端**发起的所有请求都会转发到固定的一个Pod上。
  - 此模式可以使在spec中添加**sessionAffinity:** **ClientIP**选项。意思是clientIP进来首次被分发到哪个POD，之后就一直保持与这个pod的会话。

## 更改svc代理模式

~~~sh
# 查看当前的代理模式：
curl 127.0.0.1:10249/proxyMode
iptables
# 更改 proxy 的代理模式为 ipvs：
kubectl edit cm kube-proxy -n kube-system
# mode更改成"ipvs"
# 二进制安装方式配置文件在每个机器上 
#重启 kube-proxy 生效（二进制安装方式使用 systemctl restart kube-proxy）：
kubectl patch daemonset kube-proxy -p 
"{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"date\":\"`date +'%s'`\"}}}}}" -n kube-system
# 再次查看代理模式：
curl 127.0.0.1:10249/proxyMode
ipvs
~~~

## 更改ipvs负载均衡算法

~~~sh
# 在机器上查看 ipvs 规则：
yum install ipvsadm -y
ipvsadm -ln
IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port Scheduler Flags
-> RemoteAddress:Port Forward Weight ActiveConn InActConn
TCP 172.16.32.128:32000 rr
-> 172.16.85.217:8443 Masq 1 0 0 
TCP 172.16.32.128:32001 rr
-> 192.168.181.141:80 Masq 1 0 0

# 更改代理算法为最小连接数：
kubectl edit cm kube-proxy -n kube-system
# 把ipvs.scheduler字段改成"lc"
# 重启 Proxy：
kubectl patch daemonset kube-proxy -p "{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"date\":\"`date +'%s'`\"}}}}}" -n kube-system
# 查看 ipvs 算法：
ipvsadm -ln
IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port Scheduler Flags
-> RemoteAddress:Port Forward Weight ActiveConn InActConn
TCP 172.16.32.128:32000 lc
-> 172.16.85.217:8443 Masq 1 0 0 
TCP 172.16.32.128:32001 lc
-> 192.168.181.141:80 Masq 1 0 0
~~~

# svc域名

- service只要创建完成，我们就可以直接解析它的域名，每一个服务创建完成后都会在集群dns中动态添加一个资源记录，添加完成后我们就可以解析了，资源记录格式是：

  ```bash
  #服务名.命名空间.[域名后缀]
  SVC_NAME.NS_NAME.[DOMAIN.LTD.]
  #集群默认的域名后缀是svc.cluster.local.
  svc_name.ns_name.svc.cluster.local
  ```
  
  ```bash
  #在pod里面curl svc的域名
  kubectl exec -it dep-nginx-57886b49fb-f2bk2 -- /bin/bash
  curl svc-nginx.default.svc.cluster.local
  ```
  

# yaml字段

```yaml
# spec
kubectl explain service.spec

KIND:     Service
VERSION:  v1
RESOURCE: spec <Object>
DESCRIPTION:
     Spec defines the behavior of a service.
     https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#spec-and-status
     ServiceSpec describes the attributes that a user creates on a service.
FIELDS:
   allocateLoadBalancerNodePorts	<boolean>
   clusterIP	<string> #动态分配的地址，也可以自己在创建的时候指定，创建之后就改不了了
   clusterIPs	<[]string>
   externalIPs	<[]string>
   externalName	<string>
   externalTrafficPolicy	<string>
   healthCheckNodePort	<integer>
   ipFamilies	<[]string>
   ipFamilyPolicy	<string>
   loadBalancerIP	<string>
   loadBalancerSourceRanges	<[]string>
   ports	<[]Object>  #定义service端口，用来和后端pod建立联系
   publishNotReadyAddresses	<boolean>
   selector	<map[string]string> #通过标签选择器选择关联的pod有哪些
   sessionAffinity	<string>
   sessionAffinityConfig	<Object> #service在实现负载均衡的时候还支持sessionAffinity，会话联系，默认是none，随机调度的（基于iptables规则调度的）；如果我们定义sessionAffinity的client ip，那就表示把来自同一客户端的IP请求调度到同一个pod上
   topologyKeys	<[]string>
   type	<string>  #定义service的类型
   
#spec.ports
kubectl explain service.spec.ports

KIND:     Service
VERSION:  v1
RESOURCE: ports <[]Object>
DESCRIPTION:
     The list of ports that are exposed by this service. More info:
     https://kubernetes.io/docs/concepts/services-networking/service/#virtual-ips-and-service-proxies
     ServicePort contains information on service's port.
FIELDS:
   appProtocol	<string>
   name	<string>  #定义端口的名字
   nodePort	<integer>   #service在物理机映射的端口，默认在 30000-32767 之间
   port	<integer> -required-  #service的端口，这个是k8s集群内部服务可访问的端口
   protocol	<string>
   targetPort	<string> # targetPort是pod上的端口，从port和nodePort上来的流量，经过kube-proxy流入到后端pod的targetPort上，最后进入容器。
```

> 注意Selector字段：svc通过selector选择对应标签的pod去代理流量。

# svc分类

## ClusterIP

- svc暴露的IP，只能在集群内访问。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dep-nginx
spec:
  selector:
    matchLabels:
      run: nginx # 标签要写pod的标签，也就是deployment的选择器匹配的标签，而不是deployment自己的标签。
  replicas: 3
  template:
    metadata:
      labels:
        run: nginx
    spec:
      containers:
      - name: nginx
        image: docker.io/library/nginx:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80  #pod中的容器需要暴露的端口
#---
apiVersion: v1
kind: Service
metadata:
  name: svc-nginx
  labels:
    run: nginx
spec:
  selector:
    run: nginx
  type: ClusterIP
  ports:
  - name: port-svc-nginx
    port: 80 # service 暴露的端口
    protocol: TCP
    targetPort: 80 # pod暴露的端口
```

```bash
#查看node上的ipvs设置的svc的IP和endpoint的对应关系：
ipvsadm -Ln

TCP  10.99.178.109:80 rr
  -> 10.244.184.54:80             Masq    1      0          0         
  -> 10.244.184.55:80             Masq    1      0          0         
  -> 10.244.190.30:80             Masq    1      0          0    
```

- **HeadLiness** Service：不想使用service提供的负载均衡，希望自己定策略。这种不分配cluster IP，只能通过service的域名来访问。yaml文件中将cluster IP设置为None即可。

> 注意：clusterIP虽然在宿主机上能直接请求，但是svc的FQDN在宿主机上可能无法解析。因为宿主机的DNS不是CoreDNS。

## NodePort

- 将pod通过node上的端口暴露给外部，可以在集群外访问服务，原理是将pod的端口（targetPort）映射到Node的一个端口（nodePort）上（3000-32767，api-server的--service-node-port-range参数来控制的），通过NodeIP：NodePort来访问。NodePort 类型的服务将在**每个节点上公开一个端口**，并将流量路由到后端 Pod。

- 注意是**每个节点**！当在Kubernetes中创建一个NodePort类型的Service时，Kubernetes会在每个Node上打开相同的端口。这样，无论你的请求发送到哪个Node，都可以通过这个端口访问到Service。这是通过Kubernetes的iptables规则或者IPVS来实现的。

- 访问链路：

  client -> nodeIP:nodePort -> node的docker0网卡 -> pod

> 注意1.18之后的集群，这个NodePort不能用netstat或者ss探测到了，因为它仅仅是用iptables/ipvs建了一个映射，不是起了一个socket链接了。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: svc-nginx-nodeport
  labels:
    run: nginx
spec:
  selector:
    run: nginx
  type: NodePort
  ports:
  - port: 80 #svc端口
    protocol: TCP
    targetPort: 80 # pod端口
    nodePort: 30380 #pod端口映射到物理机的端口
```

## ExternalName

是service的特例，没有selector、端口映射、endpoint。它是通过返回外部服务的别名来提供服务。类似于域名解析中的CNAME。

比如可以定义一个 Service，后端设置为一个外部域名，这样通过 Service 的名称即可访问到该域名。使用 nslookup 解析以下文件定义的 Service ，集群的 DNS 服务将返回一个值为 www.taobao.com 的 CNAME 记录：

~~~yaml
kind: Service
apiVersion: v1
metadata:
  name: my-externalname
spec:
  type: ExternalName
  externalName: www.taobao.com
~~~

使用场景案例：

假设某个项目具备 DEV/UAT 两个环境，每个环境需要链接指定的数据库等基础组件。基础组件同样也是在 K8s 中按照不同的环境进行划分和部署，比如 DEV 环境所用的基础组件均在basic-component-dev 命名空间下，以此类推。

为了降低配置文件的维护复杂度，准备使用 ExternalName 类型的 Service 对基础组件的连接地址进行映射，这样就可以用同名的 Service 区分不同的环境，从而降低配置文件维护的复杂度。

比如配置了在同一个项目的不同环境里面都配置一个同名的 Redis Service，类型为ExternalName，并且按照不同环境指向不同的基础组件地址，这样每个项目的不同环境，都可以用 Redis 这一个地址就可以访问到不同基础组件。

环境准备：

~~~sh
#  创建 Namespace
kubectl create ns basic-component-dev
kubectl create ns basic-component-uat
#  创建服务
kubectl create deploy redis -n basic-component-dev --image=registry.cn-beijing.aliyuncs.com/dotbalo/redis:7.2.5
kubectl create deploy redis -n basic-component-uat --image=registry.cn-beijing.aliyuncs.com/dotbalo/redis:7.2.5
#  创建 Service
kubectl expose deploy redis --port 6379 -n basic-component-dev
kubectl expose deploy redis --port 6379 -n basic-component-uat
~~~

访问测试：

~~~sh
#  创建一个专门用于测试的 Redis 客户端
kubectl create deploy redis-cli --image=registry.cnbeijing.aliyuncs.com/dotbalo/redis:7.2.5
#  测试每个环境的 Redis 基础组件
kubectl exec -ti redis-cli-57cc5fd584-hvxzq -- bash
redis-cli -h redis.basiccomponent-dev
set a dev
get a
redis-cli -h redis.basiccomponent-uat
set a uat
get a
~~~

创建项目的两个环境

~~~sh
kubectl create ns projecta-dev
kubectl create ns projecta-uat
~~~

在每个项目的环境下，创建一个 externalName 类型的 Service，用于连接到不同环境的基础组件。每个externalName的svc都叫redis，但是连接的是自己环境的对应redis svc。所以不同环境里面写代码的时候，直接写redis就能解析了。

~~~yaml
kind: Service
apiVersion: v1
metadata:
  name: redis
  namespace: projecta-dev
spec:
  type: ExternalName
  externalName: redis.basic-component-dev.svc.cluster.local
---
kind: Service
apiVersion: v1
metadata:
  name: redis
  namespace: projecta-uat
spec:
  type: ExternalName
  externalName: redis.basic-component-uat.svc.cluster.local
~~~

接下来在每个项目的环境下，创建两个 Redis 客户端，用于模拟需要链接 Redis 的应用程序：

~~~sh
kubectl create deploy usercenter --image=registry.cnbeijing.aliyuncs.com/dotbalo/redis:7.2.5 -n projecta-dev
kubectl create deploy usercenter --image=registry.cnbeijing.aliyuncs.com/dotbalo/redis:7.2.5 -n projecta-uat
~~~

测试每个环境下的 externalName：

~~~sh
# DEV环境
kubectl get po -n projecta-dev
kubectl exec -ti usercenter-6685654cc4-pc6m9 -n projecta-dev -- bash 
redis-cli -h redis
get a
"dev"
# UAT 环境
kubectl get po -n projecta-uat
kubectl exec -ti usercenter-6685654cc4-m9wrb -n projecta-uat -- bash
redis-cli -h redis
get a
"uat"
~~~

## LoadBalancer

- 需要借助外部云环境
  - Azure文档中的LB：
    - Internal LB：[创建内部负载均衡器 - Azure Kubernetes Service | Azure Docs](https://docs.azure.cn/zh-cn/aks/internal-lb)
    - External LB：[在 Azure Kubernetes 服务 (AKS) 中使用公共负载均衡器 - Azure Kubernetes Service | Azure Docs](https://docs.azure.cn/zh-cn/aks/load-balancer-standard)
- 通过一个外部LB，直接代理到pod上

![image-20231112160812381](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311121608561.png)

# 自定义endpoint资源

service不仅仅可以用在集群内部pod上，也可以用在外部IP和域名上。比如外部有一个域名或者IP，可以创建一个svc来实现集群内服务去访问。这样更方便管理，这个后端服务变化，我们只需要去改service就行了，代码不用动。

这种情况下，endpoint是需要我们手动去创建的。（默认情况下集群内部的服务，不需要手动维护endpoint；这种外部的，需要自己建endpoint）

使用场景：

- 希望在生产环境中使用某个固定的名称而非 IP 地址访问外部的中间件服务；
- 希望 Service 指向另一个 Namespace 中或其他集群中的服务；
- 正在将工作负载转移到 Kubernetes 集群，但是一部分服务仍运行在 Kubernetes 集群
  之外的 backend。

## 示例：集群引用外部mysql数据库

- 模拟在物理机上装一个mysql，用k8s的service来代理

- node2上安装mysql

  ```bash
  yum install mariadb-server.x86_64 -y
  systemctl start mariadb
  ```

- 创建mysql的svc，不定义selector

  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: svc-mysql
  spec:
    type: ClusterIP
    ports:
    - port: 3306
  # 这个service没有定义label selector，所以不会生成endpoint
  ```

- 自定义一个endpoint

  ```yaml
  apiVersion: v1
  kind: Endpoints
  metadata:
    name: svc-mysql # ep的name必须和要手动关联的svc的name相同。
  subsets:
  - addresses: 
    - ip: 192.168.40.5 # 直接写上装了mysql的物理机ip
    ports:
    - port: 3306 #暴露mysql的3306
  # ep创建好之后，describe svc会自动关联上ep
  # 上面配置就是将外部IP地址和服务引入到k8s集群内部，由service作为一个代理来达到能够访问外部服务的目的。
  ```

  > endpoint必须和svc名称一样，二者才会自动关联。
  
  # coredns组件 

CoreDNS 其实就是一个 DNS 服务，而 DNS 作为一种常见的服务发现手段，所以很多开源项目以及工程师都会使用 CoreDNS 为集群提供服务发现的功能，Kubernetes 就在集群中使用 CoreDNS 解决服务发现的问题。 

# 自带svc：kubernetes

在 Kubernetes 集群中，名称为 "kubernetes" 的 Service 是一个特殊的 Service，它提供了对 Kubernetes API server 的访问。其他组件去访问api server的时候就是走的kubernetes这个service。

这个 Service 的主要作用是允许集群内的 Pod 通过 Service 网络（通常是 ClusterIP）来访问 Kubernetes API，而不需要知道 API server 的实际 IP 地址或主机名。这对于运行在 Pod 中的应用程序来说非常有用，因为它们可以使用 Kubernetes API 来查询集群状态、操作资源等，而无需关心 API server 的具体位置。

# kube-proxy由iptables切换到ipvs

- 在用kubeadm安装集群时，在kubeadm.yaml文件中手动定义了kube-proxy的类型

~~~yaml
---
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: ipvs
~~~

- 安装配置ipvs

```sh
#在所有节点上安装以下：
yum install -y ipset ipvsadm
#所有节点加载内核参数
cat << 'EOF' > /etc/sysconfig/modules/ipvs.modules
#!/bin/bash
ipvs_modules=(ip_vs ip_vs_lc ip_vs_wlc ip_vs_rr ip_vs_wrr ip_vs_lblc ip_vs_lblcr ip_vs_dh ip_vs_sh ip_vs_fo ip_vs_nq
ip_vs_sed ip_vs_ftp nf_conntrack_ipv4)
for kernel_module in ${ipvs_modules[*]}; do
/sbin/modinfo -F filename ${kernel_module} > /dev/null 2>&1
if [ $? -eq 0 ]; then
/sbin/modprobe ${kernel_module}
fi
done
EOF

chmod +x /etc/sysconfig/modules/ipvs.modules
/etc/sysconfig/modules/ipvs.modules
```

- 编辑configmap

~~~sh
kubectl -n kube-system edit cm kube-proxy
#修改mode字段为"ipvs"
#手动删除kube-proxy pod，自动生成的新pd会拉取新的配置
kubectl -n kube-system get pod -l k8s-app=kube-proxy | grep -v 'NAME' | awk '{print $1}' | xargs kubectl -n kube-system delete pod
#清理iptables防火墙规则
iptables -t filter -F; iptables -t filter -X; iptables -t nat -F; iptables -t nat -X
#修改ipvs模式之后过5-10分钟测试在k8s创建pod是否可以正常访问网络
kubectl run busybox --image busybox:1.28 --restart=Never --rm -it busybox -- sh
~~~

