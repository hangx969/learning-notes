# 背景

- 虽然每个Pod都会分配一个单独的Pod IP，然而却存在如下两问题：

  -   Pod IP 会随着Pod的重建产生变化

  -   Pod IP 仅仅是**集群内可见的虚拟IP**，外部无法访问 

- 这样对于访问这个服务带来了难度。因此，kubernetes设计了Service来解决这个问题，service在生命周期内，IP地址不会变。service通过标签选择器绑定相应的pod，可以通过访问service的ip来访问pod的服务。

- Service可以看作是一组同类Pod对外的访问接口。借助Service，应用可以方便地实现服务发现和负载均衡。

# 实现原理

- Service在很多情况下只是一个概念，真正起作用的其实是kube-proxy服务进程，每个Node节点上都运行着一个kube-proxy服务进程。

- 当创建Service的时候会通过api-server向etcd写入创建的service的信息，而kube-proxy会基于监听的机制发现这种Service的变动，然后它会将最新的Service信息转换成对应的**转发规则**。

- 也就是说，表面上看是创建了一个service，对应若干pod，但是底层会被kubeproxy转换成对应的访问规则，这种规则根据kubeproxy工作模式的不同，会有不同的规则，如iptables，ipvs规则等。实际工作的是访问规则。 

  ![image-20231111110951734](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311111109863.png)

## Kubeproxy工作模式

### Userspace

- userspace模式下，kube-proxy会为每一个Service创建一个监听端口，发向Cluster IP的请求被Iptables规则重定向到kube-proxy监听的端口上，kube-proxy根据LB算法选择一个提供服务的Pod并和其建立链接，以将请求转发到Pod上。 该模式下，kube-proxy充当了一个四层负责均衡器的角色。由于kube-proxy运行在userspace中，在进行转发处理时会增加内核和用户空间之间的数据拷贝，虽然比较稳定，但是效率比较低。

  ![image-20231111111348557](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311111113677.png)

   

### iptables

- iptables模式下，kube-proxy为service后端的每个Pod创建对应的iptables规则，直接将发向Cluster IP的请求重定向到一个Pod IP。 该模式下kube-proxy不承担四层负责均衡器的角色，只负责创建iptables规则。该模式的优点是较userspace模式效率更高，但不能提供灵活的LB策略，当后端Pod不可用时也无法进行重试。

  ![image-20231111111411881](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311111114959.png)

### ipvs

- ipvs模式和iptables类似，kube-proxy监控Pod的变化并创建相应的ipvs规则。ipvs相对iptables转发效率更高。除此以外，ipvs支持更多的LB算法。

  ![image-20231111111435638](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311111114753.png)

# 负载分发策略

对Service的访问被分发到了后端的Pod上去，目前kubernetes提供了两种负载分发策略：

-   如果不定义，默认使用**kube-proxy的策略**，比如随机、轮询。
-   基于**客户端地址的会话保持模式**，即来自**同一个客户端**发起的所有请求都会转发到固定的一个Pod上。
  - 此模式可以使在spec中添加**sessionAffinity:** **ClientIP**选项。意思是clientIP进来首次被分发到哪个POD，之后就一直保持与这个pod的会话。

