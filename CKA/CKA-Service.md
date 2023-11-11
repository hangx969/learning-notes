# 背景

- 虽然每个Pod都会分配一个单独的Pod IP，然而却存在如下两问题：

  -   Pod IP 会随着Pod的重建产生变化

  -   Pod IP 仅仅是**集群内可见的虚拟IP**，外部无法访问 

- 这样对于访问这个服务带来了难度。因此，kubernetes设计了Service来解决这个问题，service在生命周期内，IP地址不会变。service通过标签选择器绑定相应的pod，可以通过访问service的ip来访问pod的服务。

- Service可以看作是一组同类Pod对外的访问接口。借助Service，应用可以方便地实现服务发现和负载均衡。

- k8s在创建Service时，会根据标签选择器selector(lable selector)来查找Pod，据此创建与Service同名的endpoint对象，当Pod 地址发生变化时，endpoint也会随之发生变化，service接收前端client请求的时候，就会通过endpoint，找到转发到哪个Pod进行访问的地址。(至于转发到哪个节点的Pod，由负载均衡kube-proxy决定)

# 实现原理

- Service在很多情况下只是一个概念，真正起作用的其实是kube-proxy服务进程，每个Node节点上都运行着一个kube-proxy服务进程。

- 当创建Service的时候会通过api-server向etcd写入创建的service的信息，而kube-proxy会基于watch的机制发现这种Service的变动，然后它会将最新的Service信息转换成对应的**转发规则**。

- 也就是说，表面上看是创建了一个service，对应若干pod，但是底层会被kubeproxy转换成对应的访问规则，这种规则根据kubeproxy工作模式的不同，会有不同的规则，如iptables，ipvs规则等。实际工作的是访问规则。 

  ![image-20231111110951734](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311111109863.png)

# Kubeproxy工作模式

## Userspace

- userspace模式下，kube-proxy会为每一个Service创建一个监听端口，发向Cluster IP的请求被Iptables规则重定向到kube-proxy监听的端口上，kube-proxy根据LB算法选择一个提供服务的Pod并和其建立链接，以将请求转发到Pod上。 该模式下，kube-proxy充当了一个四层负责均衡器的角色。由于kube-proxy运行在userspace中，在进行转发处理时会增加内核和用户空间之间的数据拷贝，虽然比较稳定，但是效率比较低。

  ![image-20231111111348557](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311111113677.png)

   

## iptables

- iptables模式下，kube-proxy为service后端的每个Pod创建对应的iptables规则，直接将发向Cluster IP的请求重定向到一个Pod IP。 该模式下kube-proxy不承担四层负责均衡器的角色，只负责创建iptables规则。该模式的优点是较userspace模式效率更高，但不能提供灵活的LB策略，当后端Pod不可用时也无法进行重试。

  ![image-20231111111411881](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311111114959.png)

## ipvs

- ipvs模式和iptables类似，kube-proxy监控Pod的变化并创建相应的ipvs规则。ipvs相对iptables转发效率更高。除此以外，ipvs支持更多的LB算法。

  ![image-20231111111435638](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311111114753.png)

# 负载分发策略

对Service的访问被分发到了后端的Pod上去，目前kubernetes提供了两种负载分发策略：

-   如果不定义，默认使用**kube-proxy的策略**，比如随机、轮询。
-   基于**客户端地址的会话保持模式**，即来自**同一个客户端**发起的所有请求都会转发到固定的一个Pod上。
  - 此模式可以使在spec中添加**sessionAffinity:** **ClientIP**选项。意思是clientIP进来首次被分发到哪个POD，之后就一直保持与这个pod的会话。

# SVC域名

- service只要创建完成，我们就可以直接解析它的域名，每一个服务创建完成后都会在集群dns中动态添加一个资源记录，添加完成后我们就可以解析了，资源记录格式是：

  ```bash
  #服务名.命名空间.[域名后缀]
  SVC_NAME.NS_NAME.[DOMAIN.LTD.]
  #集群默认的域名后缀是svc.cluster.local.
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

# clusterIP

- svc暴露的IP只能在集群内访问。

```yaml
#deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dep-nginx
spec:
  selector:
    matchLabels:
      run: nginx
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
        startupProbe:
           periodSeconds: 5
           initialDelaySeconds: 60
           timeoutSeconds: 10
           httpGet:
             scheme: HTTP
             port: 80
             path: /
        livenessProbe:
           periodSeconds: 5
           initialDelaySeconds: 60
           timeoutSeconds: 10
           httpGet:
             scheme: HTTP
             port: 80
             path: /
        readinessProbe:
           periodSeconds: 5
           initialDelaySeconds: 60
           timeoutSeconds: 10
           httpGet:
             scheme: HTTP
             port: 80
             path: /
#...
#service
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

# NodePort

- 将pod通过node上的端口暴露给外部，可以在集群外访问服务，原理是将pod的端口（targetPort）映射到Node的一个端口（nodePort）上，通过NodeIP：NodePort来访问。NodePort 类型的服务将在每个节点上公开一个端口，并将流量路由到后端 Pod。

- 访问链路：

  client -> nodeIP:nodePort -> node的docker0网卡 -> pod

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

