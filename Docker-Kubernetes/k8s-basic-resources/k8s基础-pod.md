# POD介绍

## POD特点

- K8s最小部署单元，里面封装了一个或多个容器。
- pod内部的容器共享存储、网络、PID、IPC等。容器之间可以通过localhost:port互相访问。可以通过volume实现数据共享。
- 生命周期短暂，重启之后又变成新的POD。

## POD存在的意义

1. 对于多容器协作：pod的多容器管理更加高效，更加方便（比如pod内sidecar模式集成日志收集、服务网格等）
2. 对于强依赖服务：pod把多容器放在一起，他们之间可以通过网络共享来通信，更加高效。
3. 简化应用的生命周期管理：k8s对pod的readiness管理比容器完善。
4. 兼容多种运行时：适应容器技术的变化。容器化技术不一定要用docker，换成别的也要支持。

## Pause容器

- 每一个pod里面自动有一个根容器 pause（也叫infra容器），除此之外有许多业务容器（用户容器）。


- kubectl get pods 看到的 READY 1/1 说明该pod里面有1个容器（其实还有个根容器但是默认不显示）。


- pause容器作用：

  - 以它为依据，评估其他容器的健康状态。
  - 启动Pod时，会先启动⼀个pause容器，然后将后续的所有容器都link到这个pause容器，以实现⽹络共享。给他设置一个IP地址（POD IP），其他容器通过此IP来进行内部通信。
  - 存储共享、网络共享都是通过pause实现的。
  
  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310252236935.png" alt="image-20231025223642872" style="zoom:50%;" />

## POD中的容器

Pod中可以同时运行多个容器。同一个Pod中的容器共享资源、网络环境，它们总是被同时调度，只有当你的容器需要紧密配合协作的时候才考虑用这种模式。例如，你有一个容器作为web服务器运行，需要用到共享的volume，有另一个“sidecar”容器来从远端获取资源更新这些文件。一些Pod有init容器和应用容器。在应用程序容器启动之前，运行初始化容器。

1）所有容器使用同一个network namespace，共享一个IP地址和端口空间。意味着容器之间可以通过localhost高效访问，不能有端口冲突。

2）允许容器之间共享存储卷，通过文件系统交互信息。当K8s挂载Volume到Pod上，本质上是将volume挂载到Pod中的每一个容器里。

### 进入容器

```bash
kubectl exec -it -c <container name> -- /bin/bash
```

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

# Pod字段配置

## 端口号

容器的端口号`spec.containers.ports.containerPort`这个字段，仅仅是声明了容器暴露了哪个端口，方便查看。与实际容器里面程序暴露了什么端口没有关系。K8s并不知道程序暴露了哪个端口，并不是你pod设置了80端口，容器就暴露80，设置了81就暴露81。

所以一个pod内多个容器暴露的端口在设计程序的时候就要注意不能冲突，不是pod字段里面声不一样的端口就能避免的，避免不了。

## 启动命令

spec.containers.command和spec.containers.args两个字段，可以覆盖容器内的entrypoint和cmd。

## resources

- requests的资源是直接划分给pod的，即使pod没有使用，所以有时候即使宿主机有资源，但是不能分配了，是因为pod的request已经把资源划分完了，只不过还没实际使用。（`free -m`查看宿主机占用很小，但是实际上已经分配给了pod，所以新pod就pending了）
- 注意：如果只配置了limits不配置requests，会自动帮你把request写成和limits一样的值。所以有时候看到没有配置requests，但是还是无法调度，可能就是这个原因。

## 环境变量

~~~yaml
env:
- name: path
  value: test
- name: POD_NAME
  valuesFrom: 
    fieldRef:
      fieldPath: metadata.name
- name: POD_IP
  valueFrom:
    fieldRef:
      fieldPath: status.podIP
- name: LABEL_APP
  valueFrom:
    fieldRef:
      fieldPath: metadata.labels['run']
~~~

> fieldRef可选的字段：
>
> metadata.name
> metadata.namespace
> metadata.uid
> metadata.labels[xxx]
> metadata.annotations[xxx]
> spec.nodeName
> spec.serviceAccountName
> status.hostIP
> status.hostIPs
> status.podIP
> status.podIPs

## POD重启策略

`Pod.spec.restartPolicy`字段

-   Always：kubelet会定期查询容器的状态，一旦某个容器处于**退出**状态（正常退出后是Completed状态），就对其执行重启操作，这是**默认值。**【保持Always就行】
-   OnFailure：容器异常退出（也就是退出码不为0）时重启。正常退出不会重启。
-   Never： 不论任何状态，都不重启该容器。

测试yaml文件：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: bb-rp
  labels:
    app: busybox
spec:
   containers:
     - name: busybox
       image: busybox:latest
       command: ["/bin/sh"]
       args: ["-c", "sleep 10, exit 1"]
   restartPolicy: Always
```

# POD生命周期

K8S文档：[Pod 的生命周期 | Kubernetes](https://kubernetes.io/zh-cn/docs/concepts/workloads/pods/pod-lifecycle/)

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310252254552.png" alt="image-20231025225409474" style="zoom:50%;" />

- kubelet创建pause根容器
- 运行Initcontainer
  - 先于主容器运行一些自定义工具程序或自定义代码。串行进行，前一个失败不会运行后一个。
  - 作用在整个pod范围的。
- 运行主容器
- 主容器启动之后--post start hook
- 存活性探测、就绪性探测
- 停止前钩子 (每个container都可以定义各自的钩子)
- pod终止过程

## pod创建过程

- 用户通过kubectl或其他api客户端提交需要创建的pod信息给apiServer

- apiServer开始生成pod对象的metadata，并将信息存入etcd，然后返回确认信息至客户端

- 其它组件使用watch机制来跟踪检查apiServer上的变动。**scheduler发现有新的pod对象要创建，开始为Pod分配主机并将结果信息更新至apiServer**

- node节点上的kubelet发现有pod调度过来，调用容器运行时启动容器，并将结果回送至apiServer

- apiServer将接收到的pod状态信息存入etcd中

  ![image-20231026203326085](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310262033218.png)

## Pod启动过程

kubectl create pod -- pending -- ContainerCreating -- InitContainer -- Container Running -- `Startup Probe -- Liveness/Readiness Probes` -- Endpoint添加pod IP

> Startup Probe是在另外两个之前运行的。

## pod删除过程

- 用户向apiServer发送删除pod的命令。
- apiServcer中的pod信息会在宽限期内（默认30s）被视为dead。以下三个步骤同步执行：
  - kubelet将pod转为Terminating状态
  - **endpoint控制器**监控到pod关闭，将与pod IP剔除。
  - 如果当前pod对象定义了`preStop钩子处理器`，terminating时同步执行。如果宽限期结束PreStop仍未结束，再获得两秒宽限期
- 宽限期结束后，若pod中还存在仍在运行的进程，那么pod会收到立即终止`SIGKILL`的信号。
- kubelet请求apiServer将此pod资源的宽限期设置为0从而完成删除操作，此时pod对于用户已不可见。

```bash
# 强制删除pod
kuebctl delete po xxx --force --grace-period=0
```

## 钩子函数

### 介绍

在`pod.spec.containers.lifecycle`下面定义

- PostStart
  - 启动后执行，如果执行失败，容器会按照重启策略重新启动。不需要传递任何参数。
  - 用于资源部署、环境准备等。

  > 注意：postStart并不是在容器启动命令之前运行的，并不能保证。可以理解为是同时运行的。所以这个功能并不适合做初始化操作。初始化操作最好加一个initContianer。一些不影响程序启动的命令可以加到preStart里面
  
- PreStop：
  - 删除前执行，没执行完就会阻塞在这里
  - 用于优雅关闭应用程序、通知其他系统等。

### 优雅关闭

当用户删除含有pod的资源对象时（如RC、deployment等），K8S为了让应用程序优雅关闭（即让**程序完成正在处理的请求后再关闭**），K8S提供两种信息通知：

1. 默认：K8S通知node执行docker stop命令，docker会先向容器中PID为1的进程发送系统信号SIGTERM，然后等待容器中的应用程序终止执行，如果等待时间达到设定的超时时间，或者默认超时时间（30s），会继续发送SIGKILL的系统信号强行kill掉进程。

2. 使用pod生命周期（利用PreStop回调函数），它执行在发送终止信号之前。

默认情况下，所有的删除操作的优雅退出时间都在30秒以内。kubectl delete命令支持--grace-period=的选项，以运行用户来修改默认值。0表示删除立即执行，并且立即从API中删除pod。在节点上，被设置了立即结束的的pod，仍然会给一个很短的优雅退出时间段，才会开始被强制杀死。

### 示例

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: life-demo
spec:
  containers:
  - name: lifecycle-demo-container
    image: nginx:latest
    imagePullPolicy: IfNotPresent
    lifecycle:
      postStart:
        exec:
          command: ["/bin/sh", "-c","echo 'lifecycle hookshandler' > /usr/share/nginx/html/test.html"]
      preStop:
        exec:
          command: ["/bin/sh", "-c", "sleep", "10"] # sleep是一个非常常用的preStop命令，就让容器等一段时间再退出。
        # k8s 1.30以上可以直接用sleep作为preStop
        # sleep:
          # seconds: 60
```

# Pod状态

| 状态                          | 说明                                                         |
| ----------------------------- | ------------------------------------------------------------ |
| Pending（挂起）               | Pod已被Kubernetes系统接收，但仍有一个或多个容器未被创建，可以通过kubectl describe查看处于Pending状态的原因 |
| Running（运行中）             | Pod已经被绑定到一个节点上，并且所有的容器都已经被创建，而且至少有一个是运行状态，或者是正在启动或者重启，可以通过kubectl logs查看Pod的日志 |
| Succeeded（成功）             | 所有容器执行成功并终止，并且不会再次重启，可以通过kubectl logs查看Pod日志 |
| Failed/Error（失败）          | 所有容器都已终止，并且至少有一个容器以失败的方式终止，也就是说这个容器要么以非零状态退出，要么被系统终止，可以通过logs和describe查看Pod日志和状态 |
| Unknown（未知）               | 通常是由于通信问题造成的无法获得Pod的状态                    |
| ImagePullBackOff/ErrImagePull | 镜像拉取失败，一般是由于镜像不存在、网络不通或者需要登录认证引起的，可以使用describe命令查看具体原因 |
| CrashLoopBackOff              | 表示 Pod 中发生的重启循环：Pod 中的容器已启动，但崩溃然后又重新启动，一遍又一遍。<本身并不是一个错误，而是表明发生了一个错误，导致 Pod 无法正常启动。重启的原因是pod的重启策略设置为Always或者OnFailure，可以通过logs命令查看具体原因，一般为启动命令不正确，健康检查不通过等。<br />BackOff含义是：重启之间的指数延迟（10 秒、20 秒、40 秒……），上限为 5 分钟。当 Pod 状态显示 CrashLoopBackOff 时，表示它当前正在等待指示的时间，然后再重新启动 Pod。除非它被修复，否则它可能会再次失败。 |
| OOMKilled                     | 容器内存溢出，一般是容器的内存Limit设置的过小，或者程序本身有内存溢出，可以通过logs查看程序启动日志 |
| Terminating                   | Pod正在被删除，可以通过describe查看状态                      |
| SysctlForbidden               | Pod自定义了内核配置，但kubelet没有添加内核配置或配置的内核参数不支持，可以通过describe查看具体原因 |
| Completed                     | 容器内部主进程退出，一般计划任务执行结束会显示该状态，此时可以通过logs查看容器日志 |
| ContainerCreating             | Pod正在创建，一般为正在下载镜像，或者有配置不当的地方，可以通过describe查看具体原因 |
| Evited                        | 多见于系统内存或硬盘资源不足                                 |

# InitContainer

- spec字段下的initContainers。可以有一个或多个，如果多个按照定义的顺序依次执行，先执行初始化容器1，再执行初始化容器2等，等初始化容器执行完具体操作之后初始化容器就退出了，只有所有的初始化容器执行完后，主容器才启动。

- 由于一个Pod里容器存储卷是共享的，所以Init Container里产生的数据可以被主容器使用到，Init Container可以在多种K8S资源里被使用到，如Deployment、DaemonSet, StatefulSet、Job等，但都是在Pod启动时，在主容器启动前执行，做初始化工作。

- 初始化容器与主容器区别是:

  - 初始化容器不支持 Readinessprobe,因为它们必须在Pod就绪之前运行完成。	

  - 每个Init容器必须运行成功,下一个才能够运行。

示例:

```yaml
#主容器运行nginx服务，初始化容器用来给主容器生成index.html文件
apiVersion: v1
kind: Pod
metadata:
  name: init-nginx
spec:
  volumes:
  - name: pod-workdir
    emptyDir: {} #把物理机的目录挂进pod
  initContainers:
  - name: install
    image: docker.io/library/busybox:1.28
    imagePullPolicy: IfNotPresent
    command:
    - wget
    - "-O"
    - "/work-dir/index.html"
    - "https://www.baidu.com" #把百度主页下下来存到这个目录
    volumeMounts:
    - name: pod-workdir
      mountPath: /work-dir
  containers:
  - name: nginx
    image: nginx:latest
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 80
    volumeMounts:
    - name: pod-workdir
      mountPath: /usr/share/nginx/html #俩容器挂了同一个物理机存储，是文件共享的，html文件会同步进来。
```

```bash
pod-init   0/1     Init:0/2   0          7s
#Init: 0/2，表示两个初始化容器未完成
```

# POD健康探测

[https://gitee.com/hangxu969/golang/blob/main/k8s%E8%AF%A6%E7%BB%86%E6%95%99%E7%A8%8B/Kubernetes%E8%AF%A6%E7%BB%86%E6%95%99%E7%A8%8B.md#534-%E5%AE%B9%E5%99%A8%E6%8E%A2%E6%B5%8B](https://gitee.com/hangxu969/golang/blob/main/k8s详细教程/Kubernetes详细教程.md#534-容器探测)

> - 这三种probe需要在yaml文件里面自己配。
> - StartupProbe探测成功后才会进行LivenessProbe和ReadinessProbe。后两者是并行的，没有先后关系。

## 四种探测方法

- Exec命令：在容器内执行指定命令，如果命令执行的`退出码为0`，则认为程序正常；退出码非0，则不正常。
- TCPSocket：将会尝试访问容器的`IP:端口`，如果能够建立这条连接（发现容器在监听这个端口），则认为程序正常，否则不正常。
- HTTPGet：通过`容器IP+端口号+路径`，调用HTTP GET，如果返回的状态码在`200-399`之间，则认为程序正常，否则不正常。

- gRPC：GRPC协议的健康检查，如果响应的状态是"SERVING"，则认为容器健康。

## 三种探针

### StartupProbe

- 是为了解决程序启动时间很长，启动慢问题的。如果不配这个，程序启动慢，端口起不来，livenessProbe检测不过，会一直重复被liveness探针重启，重启完程序又没启动完，又被重启了。进入CrashLookBackoff状态。（把initialDelaySeconds调高点也行，但是调高点又会造成服务漂移之后启动太慢。而且有时候服务启动的时间不固定，这样还是startupProbe更好用）
- 当配置了startupProbe启动探针，会先禁用其他探针，直到startupProbe探针成功，成功后将退出不再进行探测；如果startupProbe探针探测失败，pod将会根据重启策略重启。
- 如果容器没有提供启动探测，则默认状态为成功Success。

**示例**

- Exec模式

  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: startupprobe
  spec:
    containers:
    - name: startup
      image: tomcat-8.5-jre8:v1
      imagePullPolicy: IfNotPresent
      ports:
      - containerPort: 8080
      startupProbe:
        exec:
          command:
          - "/bin/sh"
          - "-c"
          - "ps aux | grep tomcat"
        initialDelaySeconds: 20 #容器启动后多久开始探测
        periodSeconds: 20 #执行探测的时间间隔
        timeoutSeconds: 10 #探针执行检测请求后，等待响应的超时时间
        successThreshold: 1 #成功多少次才算成功
        failureThreshold: 3 #失败多少次才算失败
  ```

- tcp socket模式

  对于startupProbe，更推荐用tcpSocket方式，因为端口起来了说明程序没问题了。

  ```yaml
      startupProbe:
        tcpSocket:
          port: 8080
        initialDelaySeconds: 10 #容器启动后多久开始探测
        periodSeconds: 5 #执行探测的时间间隔
        timeoutSeconds: 2 #探针执行检测请求后，等待响应的超时时间
        successThreshold: 1 #成功多少次才算成功
        failureThreshold: 30 #失败多少次才算失败
  ```

- http get模式

  ```yaml
      startupProbe:
        httpGet:
          path: /health # 检查路径
          port: 8080
          scheme: HTTP
          # httpHeaders: # 可选，请求头。可以传入一个token做一个简单认证。
          # - name: end-user
            # value: Jason
          # 默认探测localhost:8080
        initialDelaySeconds: 20 # 容器启动后多久开始探测。
        periodSeconds: 20 #执行探测的时间间隔
        timeoutSeconds: 10 #探针执行检测请求后，等待响应的超时时间
        successThreshold: 1 # 探测成功多少次才算成功
        failureThreshold: 3 # 探测失败多少次才算失败
  ```

### LivenessProbe

- 用指定的方式（exec、tcp、http）检测pod中的**容器是否正常运行**。
- 如果检测失败，则认为容器不健康，Kubelet杀死容器，根据restartPolicy判断是否重启。
- 如果容器配置中没有配置 livenessProbe，Kubelet 将认为存活探针探测一直为success（成功）状态。

> 存活探针是一种从应用故障中恢复的强劲方式，但应谨慎使用。你必须仔细配置存活探针，确保它能真正标示出不可恢复的应用故障，例如死锁。

**示例**

- exec模式

  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: liveness-exec
    labels:
      app: liveness
  spec:
    containers:
    - name: liveness
      image: busybox:1.28
      imagePullPolicy: IfNotPresent
      args:                       #创建测试探针探测的文件
      - /bin/sh
      - -c
      - touch /tmp/healthy; sleep 30; rm -rf /tmp/healthy; sleep 600
      livenessProbe:
        initialDelaySeconds: 10   #延迟检测时间
        periodSeconds: 5          #检测时间间隔
        exec:
          command:
          - cat
          - /tmp/healthy
          
  # 容器在初始化后，首先创建一个 /tmp/healthy 文件，然后执行睡眠命令，睡眠 30 秒，到时间后执行删除 /tmp/healthy 文件命令。而设置的存活探针检检测方式为执行 shell 命令，用 cat 命令输出 healthy 文件的内容，如果能成功执行这条命令，存活探针就认为探测成功，否则探测失败。在前 30 秒内，由于文件存在，所以存活探针探测时执行 cat /tmp/healthy 命令成功执行。30 秒后 healthy 文件被删除，所以执行命令失败，Kubernetes 会根据 Pod 设置的重启策略来判断，是否重启 Pod。
  ```

- http模式

  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: liveness-http
    labels:
      test: liveness
  spec:
    containers:
    - name: liveness
  image: docker.io/mydlqclub/springboot-helloworld:0.0.1 #ctr -n=k8s.io images import springboot.tar.gz解压
  imagePullPolicy: IfNotPresent
      livenessProbe:
        initialDelaySeconds: 20   #延迟加载时间
        periodSeconds: 5          #重试时间间隔
        timeoutSeconds: 10        #超时时间设置
        httpGet:
          scheme: HTTP
          port: 8081
          path: /actuator/health
  #上面 Pod 中启动的容器是一个 SpringBoot 应用，其中引用了 Actuator 组件，提供了 /actuator/health 健康检查地址，存活探针可以使用 HTTPGet 方式向服务发起请求，请求 8081 端口的 /actuator/health 路径来进行存活判断：任何大于或等于200且小于400的代码表示探测成功。任何其他代码表示失败。如果探测失败，则会根据重启策略做后续操作。
  ```

- tcp模式

  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: liveness-tcp
    labels:
      app: liveness-tcp
  spec:
    containers:
    - name: liveness
      image: nginx:latest
      imagePullPolicy: IfNotPresent
      livenessProbe:
        initialDelaySeconds: 15
        periodSeconds: 20
        tcpSocket:
          port: 80
  #探测80端口起来没起来
  #停掉nginx
  #k exec -it liveness-tcp -- /bin/bash
  #nginx -s stop ==> 会被存活探测自动重启。
  ```

### ReadinessProbe

- 用于检测容器中的应用是否可以接受请求，当探测成功后才使Pod对外提供网络访问，将容器标记为就绪状态，可以加到pod前端负载。

- 如果探测失败，则将容器标记为未就绪状态，会把pod从endpoint中移除。

- ReadinessProbe 和 livenessProbe 可以使用相同探测方式，只是对 Pod 的处置方式不同：

  - readinessProbe 当检测失败后，将 Pod 的 IP:Port 从对应的 EndPoint 列表中删除。

  - livenessProbe 当检测失败后，将杀死容器并根据 Pod 的重启策略来决定是否重启。

注意：Readiness不重启容器，之后Liveness才会重启。

**示例**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: springboot
  labels:
    app: springboot
spec:
  containers:
  - name: springboot
    image: docker.io/mydlqclub/springboot-helloworld:0.0.1
    imagePullPolicy: IfNotPresent
    ports:
    - name: server
      containerPort: 8080
    - name: management
      containerPort: 8081
    readinessProbe:
      initialDelaySeconds: 20   
      periodSeconds: 5          
      timeoutSeconds: 10   
      httpGet:
        scheme: HTTP
        port: 8081
        path: /actuator/health 
---
apiVersion: v1
kind: Service
metadata:
  name: springboot
  labels:
    app: springboot
spec:
  selector:
    app: springboot
  type: NodePort
  ports:
  - name: server
    port: 8080
    targetPort: 8080
    nodePort: 31180
  - name: management
    port: 8081
    targetPort: 8081
    nodePort: 31181

#Springboot 项目，设置 ReadinessProbe 探测 SpringBoot 项目的 8081 端口下的 /actuator/health 接口，如果探测成功则代表内部程序以及启动，就开放对外提供接口访问，否则内部应用没有成功启动，暂不对外提供访问，直到就绪探针探测成功。
```

## 三种probe混合使用

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: springboot-live
  labels:
    app: springboot
spec:
  containers:
  - name: springboot
    image: docker.io/mydlqclub/springboot-helloworld:0.0.1
    imagePullPolicy: IfNotPresent
    ports:
    - name: server
      containerPort: 8080
    - name: management
      containerPort: 8081
    readinessProbe:
      initialDelaySeconds: 20   
      periodSeconds: 5          
      timeoutSeconds: 10   
      httpGet:
        scheme: HTTP
        port: 8081
        path: /actuator/health
    livenessProbe:
      initialDelaySeconds: 20
      periodSeconds: 5
      timeoutSeconds: 10
      httpGet:
        scheme: HTTP
        port: 8081
        path: /actuator/health
    startupProbe:
      initialDelaySeconds: 20
      periodSeconds: 5
      timeoutSeconds: 2
      httpGet:
        scheme: HTTP
        port: 8081
        path: /actuator/health
---
apiVersion: v1
kind: Service
metadata:
  name: springboot-live
  labels:
    app: springboot
spec:
  selector:
    app: springboot
  type: NodePort
  ports:
  - name: server
    port: 8080
    targetPort: 8080
    nodePort: 31180
  - name: management
    port: 8081
    targetPort: 8081
    nodePort: 31181
```

### grpc模式（k8s 1.24+）

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: etcd-with-grpc
spec:
  containers:
  - name: etcd
    image: registry.cn-hangzhou.aliyuncs.com/google_containers/etcd:3.5.1-0
    command: [ "/usr/local/bin/etcd", "--data-dir", "/var/lib/etcd", "--listen-client-urls", "http://0.0.0.0:2379", "--advertise-client-urls", "http://127.0.0.1:2379", "--log-level", "debug"]
    ports:
    - containerPort: 2379
    livenessProbe:
      grpc:
        port: 2379 # 对于gRPC的服务，配一个gRPC的端口就行。
      initialDelaySeconds: 10
~~~

# 生产环境建议

## 探针参数配置

> 在生产环境中，健康检查接口是一定要配置的，否则在deployment的滚动更新中，新起来的pod就会直接顶替原来的pod，造成宕机。

pod可以通过存活探测和就绪探测对容器进行健康检查：

- 探测间隔时间太短，可能会增加集群的负载，并且可能会导致不必要的故障转移或服务中断
- 探测间隔时间太长，可能出现Pod里的容器已经出问题了，但是还没开始探测，pod就不会从svc移除，请求svc还会把流量转到没就绪的pod。

那如何设置探测时间、探测超时时间、探测失败次数，做到最大限度的做到业务无感知，需要根据具体的应用程序和环境来确定。以下是一些考虑因素和常见的最佳实践：

1. startupProbe
   - 初始延迟（initialDelaySeconds）：默认是0s，但是建议设置为应用程序完成启动所需的时间，确保程序可以顺利完成初始化。一般设置为几秒就行。
   - 探测间隔（periodSeconds）：默认10s，设短一些，5s
   - 探测超时时间（timeoutSeconds）：默认1s，设置为应用正常响应的范围内即可，通常是1-5s。
   - 连续失败阈值（failureThreshold）：设高一点，30次失败才认为程序没起来。这样相当于给了30*5=150s的时间启动，**只要启动起来了，就直接过了。**
2. livenessProbe
   - 初始延迟（initialDelaySeconds）：默认是0s，但是建议设置为应用程序完成启动所需的时间，确保程序可以顺利完成初始化。一般设置为几秒到几分钟
   - 探测间隔（periodSeconds）：默认是10s，但是建议根据应用特点进行调整。轻量级应用，可以设置较短间隔（5-10s）；重型应用建议增加间隔（30-60s）
   - 探测超时时间（timeoutSeconds）：默认1s，设置为应用正常响应的范围内即可，通常是1-5s。
   - 连续失败阈值（failureThreshold）：一般连续2次失败即认为探测失败，减少因为短暂网络问题或偶发故障引起误报。
3. readinessProbe
   - 其余参数和livenessProbe类似
   - 连续成功阈值（successThreshold）：一般设置1次成功即认为就绪，可以尽早把流量转发到已就绪的pod

> k8s中探测间隔最小单位就是1s，如果需要更短的探测间隔，可以自己写脚本来实现：
>
> - 在业务pod里面定义sidecar容器，执行一个shell脚本，每隔1ms请求一次探测接口（一般是代码里面预先留出的）
>
> ~~~sh
> #!/bin/bash
> while true; do
>   response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)
>   if [ "$response" != "200" ]; then
>     echo "Tomcat is not healthy. Exiting..."
>     exit 1
>   fi
>   
>   sleep 0.001  # 控制每次检测间隔为1ms
> Done
> ~~~

## 宽限期设置

宽限期默认就是30s，即使preStop设90s，也不行，等了30+2s宽限期过了之后，就强制kill pod了。

但是对于一些特殊业务， 特别是有一次长连接的，就是需要等待超过30s处理完流量连接才能平滑退出。怎么办？

改pod的宽限期：`pod.spec.terminationGracePeriodSeconds: 90`

## 零宕机发版的注意事项

1. 对于启动慢的程序，用startupProbe；对于所有程序，最好都加上livenessProbe和readinessProbe。
2. 对于优雅退出，要用preStop等待程序真正执行完再退出。
3. 对于springCloud框架，不推荐在k8s上使用，因为K8s可以平替掉springCloud。如果真的要在K8s上跑springCloud，注意：
   - pod都是注册了Pod IP到Eureka/Nacos注册中心，其他pod从注册中心拿最新的IP注册表，实现pod间访问，而不走k8s的svc。
   - 这样pod轮替更新之后，注册中心可能还没更新pod IP，或者其他服务还没拿到更新的pod IP，就会导致旧的IP仍在被访问。
   - 解决1：pod下线之前，请求Eureka的接口，下线这个pod IP，而且再让eureka通知其他客户端刷新pod IP。问题：开发不愿意实现。
   - 解决2：pod下线之前，给程序发下线信号，再加一个`preStop: sleep`的时间优雅退出。
   - 解决3：当然还是迁移到k8s最好了。k8s svc endpoint的剔除、注册是非常快的。
4. httpGet是比tcpSocket更可靠的检查方式：
   - 对于Java程序，可能会假死：即使端口通着，内部逻辑不执行了（可能因为内存溢出等原因）。这样tcpSocket可能探测不出来，httpGet才能检测出来。
   - 但是如果开发不想去实现httpGet的接口，退而求其次用tcpSocket。

# POD调度

> Pod 在其生命周期中只会被[调度](https://kubernetes.io/zh-cn/docs/concepts/scheduling-eviction/)一次。 一旦 Pod 被调度（分派）到某个节点，Pod 会一直在该节点运行，直到 Pod 停止或者被终止。

默认情况下，pod在哪个节点上运行，是通过scheduler采用相应的算法来算出来的，这个过程不受人工控制。在实际使用中，需要手动控制pod调度到某些特定节点。

k8s提供了四种调度方式：

1. 自动调度：scheduler自动算
2. 定向调度：NodeName、NodeSelector
3. 亲和性调度：NodeAffinity、PodAffinity、PodAntiAffinity（基于标签实现）
4. 污点调度：Taints、Toleration（基于node）

## 定向调度

可以使用pods.spec.nodeName或者nodeSelector字段指定要调度到的node节点。

### 标签

- 作用

  - label对各种资源（node，pod，svc等）加上标签；键值对的形式

  - 常用的label

    - 版本标签："version":"release",     "version":"stable"......

    - 环境标签："environment":"dev"，"environment":"test"，"environment":"pro"

    - 架构标签："tier":"frontend"，"tier":"backend" 

- 标签的选择

  - label selector 有两种类型：

    - 基于等式的：例如 environment = dev；version ！= stable

    - 基于集合的： environment in（dev，test）

- 打标签

  ```bash
  kubectl label pod pod-test -n dev version=1.0 #打标签
  kubectl label pod nginx -n dev version=2.0 --overwrite=true #更新标签
  kubectl label pod nginx -n dev version- #删掉key为version的标签
  kubectl get pod -n dev --show-labels #看标签
  kubectl get pod -l "version=2.0" -n dev --show-labels
  kubectl get pods -l version #列出默认名称空间下标签key是version的pod，不显示标签
  kubectl get pod -L version #看key为version的pod，并打印标签值
  ```

### NodeName

- 直接指定pod调度到哪个node上 

  -- spec.nodeName

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo-pod
  namespace: default
  labels:
    app: tomcat
    env: dev
spec:
  nodeName: node-01
  containers:
  - name:  tomcat-pod-java
    ports:
    - containerPort: 8080
    image: tomcat:8.5-jre8-alpine
    imagePullPolicy: IfNotPresent
  - name: busybox
    image: busybox:latest
    command:
    - "/bin/sh"
    - "-c"
    - "while true; do echo hello; sleep 10; done"
```

### nodeSelector

- pod创建之前，由scheduler使用MatchNodeSelector调度策略进行label匹配。找到目标node再调度。是强制约束的: 没有满足条件的node，这个pod就起不来。
- pod.spec.nodeSelector

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: demo-pod
  namespace: default
  labels:
    app: tomcat
    env: dev
spec:
  nodeSelector:
    disk: ceph
  containers:
  - name:  tomcat-pod-java
    ports:
    - containerPort: 8080
    image: tomcat:8.5-jre8-alpine
    imagePullPolicy: IfNotPresent
  - name: busybox
    image: busybox:latest
    command:
    - "/bin/sh"
    - "-c"
    - "while true; do echo hello; sleep 10; done"
```

```bash
kubectl get nodes --show-labels #看node标签
kubectl label nodes node-01 disk=ceph #给node打标签
```

> - 如果nodeName和nodeSelector都写上，并且这两个配置的调度node冲突，就会报错：Predictate NodeAffnity Failed.
> - NodeName优先级高，在master节点有污点的情况下，如果定义nodename=master，则会强制调度上去。

## 亲和性调度

```bash
kubectl explain pods.spec.affinity
```

**种类**

- nodeAffinity

- podAffinity 

- nodeAntiAffinity

**应用**

- 亲和性：如果两个应用**频繁交互**，那就有必要利用亲和性让两个应用的尽可能的靠近，这样可以减少因网络通信而带来的性能损耗。
- 反亲和性：当应用的采用**多副本部署**时，有必要采用**反亲和性**让各个应用实例打散分布在各个node上，这样可以提高服务的高可用性。

### nodeAffinity

```bash
kubectl explain pods.spec.affinity.nodeAffinity
#preferredDuringSchedulingIgnoredDuringExecution <[]Object>
#requiredDuringSchedulingIgnoredDuringExecution <Object>
```

- prefered表示有节点尽量满足这个位置定义的亲和性，没有满足的也能调度：软亲和性
- require表示必须有节点满足这个位置定义的亲和性，没有满足的就pending：硬亲和性

#### 硬亲和性

```bash
kubectl explain pods.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-node-affinity-demo
  namespace: default
  labels:
    app: bb
    tier: ft
spec:
  affinity:
    nodeAffinity:
     requiredDuringSchedulingIgnoredDuringExecution:
       nodeSelectorTerms:
       - matchExpressions:
         - key: zone #硬亲和性 - 必须调度到label是zone=foo或zone=bar的node
           operator: In
           values: 
           - foo
           - bar
  containers:
  - name: busybox
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    command:
    - "/bin/sh"
    - "-c"
    - "while true; do echo hello; sleep 10; done"
```

#### 软亲和性

```bash
kubectl explain pods.spec.affinity.nodeAffinity.preferredDuringSchedulingIgnoredDuringExecution

preference   <Object> -required-
A node selector term, associated with the corresponding weight.

weight       <integer> -required-
Weight associated with matching the corresponding nodeSelectorTerm, in the range 1-100.
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-node-affinity-demo
  namespace: default
  labels:
    app: bb
    tier: ft
spec:
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution: #是一个对象列表[]objects，他下面的要用 - 划分字段。
      - preference:
          matchExpressions: #是一个[]object，下面字段用 - 
          - key: zone1
            operator: In
            values: #是一个字符串列表，下面用 - 连接
            - foo1
            - bar1
        weight: 10
      - preference:
          matchExpressions:
          - key: zone2
            operator: In
            values:
            - foo2
            - bar2
        weight: 20 #两个条件都有节点满足的话，权重高的条件会优先调度。
  containers:
  - name: busybox
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    command:
    - "/bin/sh"
    - "-c"
    - "while true; do echo hello; sleep 10; done"
```

> NodeAffinity的注意事项：
>
> 1.  如果同时定义了nodeSelector和nodeAffinity，那么必须两个条件都得到满足，Pod才能运行在指定的Node上
> 2.  如果nodeAffinity指定了多个nodeSelectorTerms，那么只需要其中一个能够匹配成功即可
> 3.  如果一个nodeSelectorTerms中有多个matchExpressions ，则一个节点必须满足所有的才能匹配成功
> 4.  如果一个pod所在的Node在Pod运行期间其标签发生了改变，不再符合该Pod的节点亲和性需求，则系统将忽略此变化

### podAffinity 

```bash
kubectl explain pods.spec.affinity.podAffinity
#同样分为硬亲和性和软亲和性：
#preferredDuringSchedulingIgnoredDuringExecution <[]Object>
#requiredDuringSchedulingIgnoredDuringExecution <Object>
```

- 先部署了一组pod，后部署的pod亲和先部署的pod，跟他部署到同一位置。
- yaml上要定义出两个信息：
  - 后来的pod跟先前的啥pod做亲和？-- labelSelector
  - 依据什么条件判断是同一位置还是不同位置？--topologyKey

- 示例：

  创建第一组pod：

  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: pod-podAffinity-1
    namespace: default
    labels:
      app: bb
      tier: ft
  spec:
    containers:
    - name: busybox
      image: busybox:latest
      imagePullPolicy: IfNotPresent
      command:
      - "/bin/sh"
      - "-c"
      - "while true; do echo hello; sleep 10; done"
  ```

  创建第二个pod，跟第一个做亲和性：

  ```yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: pod-podAffinity-2
    namespace: default
    labels:
      app: bb
      tier: ft
  spec:
    affinity:
      podAffinity:
        requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector: #这个pod要跟app=bb的pod做亲和性
            matchExpressions:
            - {key: app, operator: In, values: ["bb"]}
          topologyKey: kubernetes.io/hostname #怎么定义同一个位置？对于key=kubernetes.io/hostname的node，value相同就算同一位置。==> 也就是跟匹配的pod在相同的node上算相同的位置。
    containers:
    - name: busybox
      image: busybox:latest
      imagePullPolicy: IfNotPresent
      command:
      - "/bin/sh"
      - "-c"
      - "while true; do echo hello; sleep 10; done"
  ```

### podAntiAffinity

跟podAffinity相反，yaml上同样要定义出两个信息：

- 后来的pod跟啥pod做亲和？-- labelSelector
- 依据什么条件判断是同一位置还是不同位置？--topologyKey

## 污点调度

官网链接：https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/

> - 前面的亲和性调度是站在pod的角度上，通过对pod的属性添加，来决定调度到什么node上。
> - 也可以站在node的角度上，在node上添加污点属性，决定是否允许pod调度进来。

### 污点

是键值对数据，**key=value:effect**, key和value是**污点的标签**；effect描述污点的作用，支持如下三个选项：

- PreferNoSchedule：kubernetes将尽量避免把Pod调度到具有该污点的Node上，除非没有其他节点可调度 -- 尽量别来，除非没办法
- NoSchedule：kubernetes将不会把Pod调度到具有该污点的Node上，但不会影响当前Node上已存在的Pod -- 新的别来，在这的就别动了
- NoExecute：kubernetes将不会把Pod调度到具有该污点的Node上，同时也会将Node上已存在的Pod驱离 -- 新的别来，旧的赶紧走

查看一个节点的污点：

```bash
kubectl get node master-01 -o=jsonpath='{.spec.taints}'
```

### 容忍

- tolerance，键值对数据，要定义出来容忍什么k、v、effect的污点。

- 示例

```bash
#node-02生产环境专用，打一个污点来区分
kubectl taint node node-02 node-type=production:NoExcute

#给节点去除污点，后面带一个减号
kubectl taint node node-02 key: node-type-
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-podAffinity-2
  namespace: default
  labels:
    app: bb
    tier: ft
spec:
  containers:
  - name: busybox
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    command:
    - "/bin/sh"
    - "-c"
    - "while true; do echo hello; sleep 10; done"
  tolerations:
  - key: "node-type"
    operator: "Equal" #Equal要求k、v、effect必须全部匹配上，才能容忍。如果是Exists，那么NoExcute可以向下兼容匹配到 NoSchedule、PreferNoSchedule的effect。(NoExcute > NoSchedule > PreferNoSchedule)
    value: "production" #value可以是空的，表示容忍特定key的污点
    effect: "NoExecute" # effect也可以是空的。
    tolerationSeconds: 3600 #NoExcute专用字段，通常情况下，如果给一个节点添加了一个 effect 值为 NoExecute 的污点，则任何不能容忍这个污点的 Pod 都会马上被驱逐，任何可以容忍这个污点的 Pod 都不会被驱逐。但是，如果 Pod 存在一个 effect 值为 NoExecute 的容忍度指定了可选属性 tolerationSeconds 的值，则表示在给节点添加了上述污点之后， Pod 还能继续在节点上运行的时间。3600这表示如果这个 Pod 正在运行，同时一个匹配的污点被添加到其所在的节点， 那么 Pod 还将继续在节点上运行 3600 秒，然后被驱逐。 如果在此之前上述污点被删除了，则 Pod 不会被驱逐。
```

# 容器保持长时运行

- 如果容器的主进程退出，Pod 通常会自动重启该容器。然而，在某些情况下，主进程的退出可能是不可避免的，这时我们需要确保容器通过其他方式持续运行。有以下几种思路：

  1. 保持后台进程持续运行

     ~~~yaml
     apiVersion: v1
     kind: Pod
     metadata:
       name: tail-pod
     spec:
       containers:
       - name: nginx
         image: nginx:latest
         command: ["tail", "-f", "/dev/null"] 
     # tail 命令进入了一个无限循环状态，持续读取一个始终为空的文件（/dev/null），从而保持容器的持续运行。不执行任何实际操作，因此不会占用大量系统资源。
     ~~~

  2. 保持容器无限暂停

     ~~~yaml
     apiVersion: v1
     kind: Pod
     metadata:
       name: sleep-pod
     spec:
       containers:
       - name: alpine
         image: alpine:latest
         command: ["sleep", "infinity"] 
     # 容器会保持在一个无限期的休眠状态。这种方法非常轻量，因为 sleep 命令本身不消耗 CPU 资源，而仅仅占用少量内存
     ~~~

  3. 使用进程管理器保持容器运行

     - 进程管理器是用于管理进程生命周期的工具，特别适用于需要在容器内运行多个进程的场景。Tini 是一种轻量级的进程管理器，设计用于在容器环境中运行，能够处理常见的 `PID 1` 问题，如信号处理、孤儿进程清理等。
     - 在容器化环境中，通常只有一个进程（通常是 `PID 1`）被直接运行，并且由它来管理整个容器的生命周期。然而，某些情况下，`PID 1` 进程无法正常处理信号或清理子进程，从而导致容器中的进程管理混乱。Tini 作为容器的 `init` 系统，能够有效地接管 `PID 1` 的角色，处理信号转发、子进程清理等工作，从而保证容器内的多进程运行稳定。

     - 构建镜像

     ```sh
     FROM ubuntu:latest
     ADD https://github.com/krallin/tini/releases/download/v0.19.0/tini /tini
     RUN chmod +x /tini
     ENTRYPOINT ["/tini", "--"]
     CMD ["your-main-process"]
     
     docker build -t your-image-with-tini .
     ```

     - 创建pod

     ~~~yaml
     apiVersion: v1
     kind: Pod
     metadata:
       name: tini-pod
     spec:
       containers:
       - name: my-container
         image: your-image-with-tini
         command: ["your-main-process"]
     ~~~

# 查看pod日志

```bash
kubectl logs <pod name> 
# 当pod处于crash状态的时候，容器不断重启，此时用 kubelet logs 可能出现一直捕捉不到日志。kubelet会保持前几个失败的容器，用--previous就能看到其日志。
kubectl logs --previous <pod name>

#查看pod内容器的日志
kubectl logs mypod --all-containers
#查看pod内某个容器日志
kubectl logs mypod -c container-name

#查看kube events
kubectl get events
kubectl get events --field-selector involvedObject.name=podName
```

# 
