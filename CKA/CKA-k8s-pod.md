# POD介绍

## POD特点

- 最小部署单元，里面有若干容器。（一般只有一个）其余功能都是为POD所服务的。pod由controller控制器部署管理。
- 内部容器的网络互通，是共享的。
- 生命周期短暂，重启之后又变成新的POD。

## POD存在的意义

1. 容器是单进程的，里面跑一个程序；pod是多进程的，可以运行多个应用程序
2. 适应容器技术的变化。容器化技术不一定要用docker，换成别的也要支持。
3. 亲密性应用
   1. 两个应用之间交互、调用
   2. 网络之间调用

## POD组成

- 每一个pod里面自动有一个根容器 pause（也叫infra容器），除此之外会有许多业务容器（用户容器）。


- kubectl get pods 看到的 READY 1/1 说明该pod里面有1个容器（其实还有个根容器但是默认不显示）。


- pause容器作用：

  - 以它为依据，评估其他容器的健康状态。
  - 启动Pod时，会先启动⼀个pause容器，然后将后续的所有容器都link到这个pause容器，以实现⽹络共享。给他设置一个IP地址（POD IP），其他容器通过此IP来进行内部通信。

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310252236935.png" alt="image-20231025223642872" style="zoom:50%;" />

## POD中的容器

Pod中可以同时运行多个容器。同一个Pod中的容器共享资源、网络环境，它们总是被同时调度，只有当你的容器需要紧密配合协作的时候才考虑用这种模式。例如，你有一个容器作为web服务器运行，需要用到共享的volume，有另一个“sidecar”容器来从远端获取资源更新这些文件。一些Pod有init容器和应用容器。在应用程序容器启动之前，运行初始化容器。

1）所有容器使用同一个network namespace，共享一个IP地址和端口空间。意味着容器之间可以通过localhost高效访问，不能有端口冲突。

2）允许容器之间共享存储卷，通过文件系统交互信息。当K8s挂载Volume到Pod上，本质上是将volume挂载到Pod中的每一个容器里。

## POD应用示例

1. 代码自动发版更新

   - 假如生产环境部署了一个go的应用，而且部署了几百个节点，希望这个应用可以定时的同步最新的代码，以便自动升级线上环境。这时，我们不希望改动原来的go应用，可以开发一个Git代码仓库的自动同步服务，然后通过Pod的方式进行编排，并共享代码目录，就可以达到更新java应用代码的效果。

     <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310261900543.png" alt="image-20231026190044415" style="zoom:50%;" />

2. 日志收集服务

   - 某服务模块已经实现了一些核心的业务逻辑，并且稳定运行了一段时间，日志记录在了某个目录下，按照不同级别分别为 error.log、access.log、warning.log、info.log，现在希望收集这些日志并发送到统一的日志处理服务器上。
   - 这时我们可以修改原来的服务模块，在其中添加日志收集、发送的服务，但这样可能会影响原来服务的配置、部署方式，从而带来不必要的问题和成本，也会增加业务逻辑和基础服务的藕合度。

   - 如果使用Pod的方式，通过简单的编排，既可以保持原有服务逻辑、部署方式不变，又可以增加新的日志收集服务。
   - 而且如果我们对所有服务的日志生成有一个统一的标准，或者仅对日志收集服务稍加修改，就可以将日志收集服务和其他服务进行Pod编排，提供统一、标准的日志收集方式。

   <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310261902236.png" alt="image-20231026190227168" style="zoom:50%;" />



# POD生命周期

## POD生命周期

- pod创建过程
- 运行init container
  - 先于主容器运行一些自定义工具程序或自定义代码。串行进行，前一个失败不会运行后一个。

- 运行main container

- pod终止过程
<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310252254552.png" alt="image-20231025225409474" style="zoom:50%;" />

## POD创建过程

- 用户通过kubectl或其他api客户端提交需要创建的pod信息给apiServer

- apiServer开始生成pod对象的metadata，并将信息存入etcd，然后返回确认信息至客户端

- apiServer开始反映etcd中的pod对象的变化，其它组件使用watch机制来跟踪检查apiServer上的变动

- **scheduler发现有新的pod对象要创建，开始为Pod分配主机并将结果信息更新至apiServer**

- node节点上的kubelet发现有pod调度过来，调用容器运行时启动容器，并将结果回送至apiServer

- apiServer将接收到的pod状态信息存入etcd中

  ![image-20231026203326085](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310262033218.png)

## pod删除过程

- 用户向apiServer发送删除pod对象的命令。
- apiServcer中的pod对象信息会随着时间的推移而更新，在宽限期内（默认30s），pod被视为dead。
- 将pod标记为terminating状态。
- kubelet在监控到pod对象转为terminating状态的同时启动pod关闭过程。
- **端点控制器**监控到pod对象的关闭行为时将其从所有匹配到此端点的service资源的端点列表中移除。
- 如果当前pod对象定义了**preStop钩子处理器**，则在其标记为terminating后即会以同步的方式启动执行。
- pod对象中的容器进程收到停止信号。
- 宽限期结束后，若pod中还存在仍在运行的进程，那么pod对象会收到立即终止的信号。
- kubelet请求apiServer将此pod资源的宽限期设置为0从而完成删除操作，此时pod对于用户已不可见。

## 钩子函数

在pod.spec.containers.lifecycle下面定义

- Post-start：启动后执行，如果执行失败容器会按照重启策略重新启动
- Pr-start：删除前执行，没执行完就会阻塞在这里

## POD状态

- Pending：apiserver创建了pod资源对象，但是尚未调度或者镜像还没下载完
- Running：pod已经被调度到某个node，并且所有容器都被kubelet创建完成
- Succeed：pod中所有的容器都成功终止，且不会被重启（容器一次性执行成功的意思）
- Failed：所有容器都已经终止，但是至少有一个终止失败；即容器返回了非0的退出状态
- unknown：apiserver获取不到pod的状态，通常是由于网络失败导致

# POD健康探测

## pod容器探测

[https://gitee.com/hangxu969/golang/blob/main/k8s%E8%AF%A6%E7%BB%86%E6%95%99%E7%A8%8B/Kubernetes%E8%AF%A6%E7%BB%86%E6%95%99%E7%A8%8B.md#534-%E5%AE%B9%E5%99%A8%E6%8E%A2%E6%B5%8B](https://gitee.com/hangxu969/golang/blob/main/k8s详细教程/Kubernetes详细教程.md#534-容器探测)

Pod.spec.containers.livenessProbe / readinessProbe

两种探针：

- Liveness probe：检测是否正常运行，如果不是，k8s将重启容器（pod的restart policy来操作（always，OnFailure，Never））
- Readiness probe：就绪性探针，检测是否可以接受请求，如果不能，k8s不会转发流量。检查失败，k8s就会把pod从service endpoint中剔除。不加入到负载均衡的列表中。

支持的三种探测方式：

- Exec命令：在容器内执行一次命令，如果命令执行的退出码为0，则认为程序正常，否则不正常
- TCPSocket：将会尝试访问**指定端口**，如果能够建立这条连接（发现容器在监听这个端口 ），则认为程序正常，否则不正常
- HTTPGet：调用容器内Web应用的URL，如果返回的状态码在200和399之间，则认为程序正常，否则不正常

# POD重启策略

**Pod.spec.restartPolicy**

-   Always ：容器失效时，自动重启该容器，这也是**默认值。**
-   OnFailure ： 容器终止运行且**退出码不为0**时重启 (exit     code 不为0代表**异常终止**)
-   Never ： 不论状态为何，都不重启该容器
