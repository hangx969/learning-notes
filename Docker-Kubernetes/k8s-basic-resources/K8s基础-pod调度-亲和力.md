# 拓扑域和拓扑键

拓扑域Topology Domain：

- 通常用于标识一组相似属性、相似网络特性的节点。这些节点一般位于同一个物理位置或者网络子网中。拓扑域一般用于亲和力配置。
- 在一个超大的规模集群中，可以使用拓扑域来标记几点所在的机房、子网等信息。
- 拓扑域的划分很简单，给节点打上标签即可；标签的k、v都相同，就表示属于同一个拓扑域。

拓扑键Topology Key：

- 用于指定拓扑域，其实就是标签的key。

## 划分拓扑域

### 基于主机

k8s每个节点都有一个标签标识节点名称：`kubernetes.io/hostname=k9s-master01`。所以每一个节点都是一个拓扑域。

### 基于多区域

比如集群在不同物理区域有节点分布。给节点打上`region=beijing`，`region=nanjing`这样的标签。

### 基于数据中心

按照数据中心的位置，打上`zone=chaoyang`，`zone=haidian`的标签

### 基于子网

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

    - 版本标签："version":"release", "version":"stable"......

    - 环境标签："environment":"dev"，"environment":"test"，"environment":"pro"

    - 架构标签："tier":"frontend"，"tier":"backend" 

- 标签的选择

  - label selector 有两种类型：

    - 基于等式的：例如 environment = dev；version ！= stable

    - 基于集合的： environment in（dev，test）

- 打标签

  ```bash
  kubectl label pod pod-test -n dev version=1.0 # 打标签
  kubectl label pod nginx -n dev version=2.0 --overwrite=true #更新标签
  kubectl label pod nginx -n dev version- # 删掉key为version的标签
  kubectl get pod -n dev --show-labels # 看标签
  kubectl get pod -l "version=2.0" -n dev --show-labels
  kubectl get pods -l version # 列出默认名称空间下标签key是version的pod，不显示标签
  kubectl get pod -L version # 看key为version的pod，并打印标签值
  ```

### NodeName

- 直接指定pod调度到哪个node上 -- spec.nodeName


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

- pod创建之前，由scheduler使用MatchNodeSelector调度策略进行label匹配。找到目标node再调度。是强制约束的: 没有满足条件的node，这个pod就起不来。-- pod.spec.nodeSelector

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

### 节点亲和性调度nodeAffinity

```bash
kubectl explain pods.spec.affinity.nodeAffinity
# preferredDuringSchedulingIgnoredDuringExecution <[]Object>
# requiredDuringSchedulingIgnoredDuringExecution <Object>
```

- prefered表示有节点尽量满足这个位置定义的亲和性，没有满足的也能调度：软亲和性
- required表示必须有节点满足这个位置定义的亲和性，没有满足的就pending：硬亲和性

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
          - key: zone # 硬亲和性 - 必须调度到label是zone=foo或zone=bar的node
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
      preferredDuringSchedulingIgnoredDuringExecution: 
      - preference:
          matchExpressions:
          - key: zone1
            operator: In
            values: 
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
        weight: 20 # 两个条件都有节点满足的话，权重高的条件会优先调度。
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

注意节点亲和性没有反亲和性配置，实现反亲和性无非就是pod不想调度到某些pod，就写operator: NotIn某些values就行了。

### pod亲和性调度

#### podAffinity 

```bash
kubectl explain pods.spec.affinity.podAffinity
# 同样分为硬亲和性和软亲和性：
# preferredDuringSchedulingIgnoredDuringExecution <[]Object>
# requiredDuringSchedulingIgnoredDuringExecution <Object>
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
        requiredDuringSchedulingIgnoredDuringExecution: # 硬亲和性，匹配出来的pod必须在同一位置
        - labelSelector: # 这个pod要跟app=bb的pod做亲和性
            matchExpressions:
            - {key: app, operator: In, values: ["bb"]}
          topologyKey: kubernetes.io/hostname # 怎么定义同一个位置？对于key=kubernetes.io/hostname的node，value相同就算同一位置 ==> 也就是跟匹配的pod在相同的node上算相同的位置。
    containers:
    - name: busybox
      image: busybox:latest
      imagePullPolicy: IfNotPresent
      command:
      - "/bin/sh"
      - "-c"
      - "while true; do echo hello; sleep 10; done"
  ```

#### podAntiAffinity

跟podAffinity相反，yaml上同样要定义出两个信息：

- 后来的pod跟啥pod做亲和？-- labelSelector
- 依据什么条件判断是同一位置还是不同位置？-- topologyKey

~~~yaml
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
    podAntiAffinity:
      perferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100 # 软亲和性才有的权重属性。当具有多个软亲和性规则的时候，优先满足高权重的规则。
        podAffinityTerm:
          labelSelector: # 这个pod要跟app=bb的pod做反亲和性
            matchExpressions:
            - key: app
              operator: In
              values: ["bb"]
        namespaces: # 和哪些ns下的pod进行匹配。通常设置为当前ns，扫描整个集群比较消耗性能。
        - default
        namespaceSelector: {} # 也可以在这里通过标签匹配ns
        topologyKey: kubernetes.io/hostname # 怎么定义同一个位置？对于key=kubernetes.io/hostname的node，value相同就算同一位置 ==> 也就是跟匹配的pod在相同的node上算相同的位置。
  containers:
  - name: busybox
    image: busybox:latest
    imagePullPolicy: IfNotPresent
    command:
    - "/bin/sh"
    - "-c"
    - "while true; do echo hello; sleep 10; done"
~~~

# 调度实战示例

## 同一个应用必须部署在不同的宿主机

~~~yaml
kind: Deployment 
metadata: 
  name: diff-nodes 
spec: 
  selector: 
    matchLabels: 
      app: diff-nodes 
  replicas: 2 
  template: 
    metadata: 
      labels: 
        app: diff-nodes 
    spec: 
      affinity: 
        podAntiAffinity: 
          requiredDuringSchedulingIgnoredDuringExecution: 
            - labelSelector: 
                matchExpressions: 
                  - key: app 
                    operator: In 
                    values: 
                      - diff-nodes # 当前ns中具有app=diff-nodes标签的pod不允许被调度到hostname相同的节点上 
              topologyKey: kubernetes.io/hostname 
              namespaces: [] # 空表示当前namespace
      containers: 
        - name: diff-nodes 
          image: nginx:1.15.12 
~~~

## 同一个应用尽量部署在不同的宿主机

~~~yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: diff-nodes 
spec: 
  selector: 
    matchLabels: 
      app: diff-nodes 
  replicas: 2 
  template: 
    metadata: 
      labels: 
        app: diff-nodes 
    spec: 
      affinity: 
        podAntiAffinity: 
          preferredDuringSchedulingIgnoredDuringExecution: 
            - podAffinityTerm: 
                labelSelector: 
                  matchExpressions: 
                    - key: app 
                      operator: In 
                      values: 
                        - diff-nodes 
                topologyKey: kubernetes.io/hostname 
                namespaces: []
              weight: 100 
      containers: 
      - name: diff-nodes 
        image: nginx:1.15.12 
~~~

## 同一个应用尽量分布在不同的机房

~~~yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: diff-zone 
spec: 
  selector: 
    matchLabels:  
      app: diff-zone 
  replicas: 3 
  template: 
    metadata: 
      labels: 
        app: diff-zone 
    spec: 
      affinity: 
        podAntiAffinity: 
          preferredDuringSchedulingIgnoredDuringExecution: 
            - podAffinityTerm: 
                labelSelector: 
                  matchExpressions: 
                    - key: app 
                      operator: In 
                      values: 
                        - diff-zone 
                topologyKey: zone 
                namespaces: [] 
              weight: 100 
      containers: 
        - name: diff-nodes 
          image: nginx:1.15.12 
~~~

## 应用和缓存尽量部署在同一个可用域

~~~yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: my-app 
spec: 
  replicas: 2 
  selector: 
    matchLabels: 
      app: my-app 
  template: 
    metadata: 
      labels: 
        app: my-app 
    spec: 
      affinity: 
        podAffinity: 
          preferredDuringSchedulingIgnoredDuringExecution: 
          - weight: 100 
            podAffinityTerm: 
              labelSelector: 
                matchExpressions: # 这个deployment的pod尽量和app=cache的pod分布在zone标签和值相同的节点上
                - key: app 
                  operator: In 
                  values: 
                  - cache 
              topologyKey: zone
      containers: 
      - name: my-app 
        image: nginx:1.15.12 
~~~

缓存服务的deployment尽量也要设置成和这个my-app的pod亲和性

## 计算服务必须部署至高性能机器

假设集群中有一批机器是高性能机器，而有一些需要密集计算的服务，需要部署至这些机器，以提高计算性能，此时可以使用节点亲和力来控制Pod尽量或者必须部署至这些节点上。

比如计算服务只能部署在ssd或nvme的节点上：

~~~yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: compute 
spec: 
  replicas: 2 
  selector: 
    matchLabels: 
      app: compute 
  template: 
    metadata: 
      labels: 
        app: compute 
    spec: 
      affinity: 
        nodeAffinity: 
          requiredDuringSchedulingIgnoredDuringExecution: 
            nodeSelectorTerms: 
            - matchExpressions: 
              - key: disktype 
                operator: In 
                values: 
                - ssd 
                - nvme 
      containers: 
      - name: compute 
        image: nginx:1.15.12 
~~~

## 计算服务尽量部署到高性能机器

如果不强制要求，可以让计算服务尽量部署至高性能机器： 

~~~yaml
   nodeAffinity: 
          preferredDuringSchedulingIgnoredDuringExecution: 
          - weight: 100 
            preference: 
              matchExpressions: 
              - key: disktype 
                operator: In 
                values: 
                - ssd 
                - nvme 
~~~

同时还可以配置优先使用ssd的机器： 

~~~yaml
affinity: 
  nodeAffinity: 
    preferredDuringSchedulingIgnoredDuringExecution: 
    - weight: 100 
      preference: 
        matchExpressions: 
        - key: disktype 
          operator: In 
          values: 
          - ssd 
    - weight: 50 
      preference: 
        matchExpressions: 
        - key: disktype 
          operator: In 
          values: 
          - nvme
~~~

## 应用尽量不部署到低性能机器

假如已知集群中有一些机器可能性能不佳或者其他因素的影响，需要控制某个服务尽量不部署至这些机器，此时只需要把operator改为NotIn即可： 

~~~yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: compute-intensive-app 
spec: 
  replicas: 3 
  selector: 
    matchLabels: 
      app: compute-intensive 
template: 
  metadata: 
    labels: 
      app: compute-intensive  
  spec: 
    affinity: 
      nodeAffinity: 
        preferredDuringSchedulingIgnoredDuringExecution: 
        - weight: 100 
          preference: 
            matchExpressions: 
            - key: performance 
              operator: NotIn 
              values: 
              - low 
    containers: 
    - name: compute-intensive 
      image: nginx:1.15.12 
~~~

## 拓扑域约束-应用均匀分布

Kubernetes 的 `spec.topologySpreadConstraints`（拓扑域约束） 是一种高级的调度策略，用于确保工作负载的副本在集群中的不同拓扑域（如节点、可用区、区域等）之间均匀分布。（和亲和性没关系，独立的字段）

~~~yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: example-deployment 
spec: 
  replicas: 3 
  selector: 
    matchLabels: 
      app: example 
  template: 
    metadata: 
      labels: 
        app: example 
    spec:
      topologySpreadConstraints: 
      - maxSkew: 1 
        whenUnsatisfiable: DoNotSchedule 
        topologyKey: kubernetes.io/hostname 
        labelSelector: 
          matchLabels: 
            app: example 
      containers: 
      - name: example 
        image: nginx:1.15.12 
~~~

- topologySpreadConstraints：拓扑域约束配置，可以是多个副本均匀分布在不同的域中，配置多个时，需要全部满足
- maxSkew：指定允许的最大偏差。例置为 1，那么在任何拓扑域中，副本的数量最多只能相差 1
- whenUnsatisfiable：指定当无法满足拓扑约束时的行为
  - DoNotSchedule：不允许调度新的Pod，直到满足约束
  - ScheduleAnyway：即使不满足约束，也允许调度新的Pod
- topologyKey：指定拓扑域的键
- labelSelector：指定要应用拓扑约束的Pod的标签选择器，通常配置为当前Pod的标签

# 污点与容忍

官网链接：https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/

前面的亲和性调度是站在pod的角度上，通过对pod的属性添加，来决定调度到什么node上。也可以站在node的角度上，在node上添加污点属性，决定是否允许pod调度进来。

考虑以下问题：

1. 节点故障如何快速恢复服务

   - 默认情况下如果一个节点故障，五分钟之后才会触发pod漂移，还是有影响的。需要一种方法实现快速故障转移。

2. 特殊资源节点如何不浪费

   - 比如有一些GPU节点、高性能机器等，如何不让普通pod调度上去。

3. 节点维护如何确保可用性

   - 节点维护、升级、打补丁的时候，如何保证不影响上面的pod。

   - 新增节点在完全验证测试之前，暂时不接受pod调度。

4. 多租户如何进行隔离

   - 某些节点属于租户A，另一些节点属于租户B。怎么保证租户隔离，比如租户A的pod不能调度到租户B的节点上。

引出污点容忍的作用：

1. 污点和容忍是k8s提供的强大的调度控制机制，可以实现精细化管理和调度优化。
2. 污点用于标记节点，容忍用于控制pod的调度行为。

## 污点

相当于给节点上了锁，有钥匙（容忍）的pod才能调度上去。没有要钥匙的调度不上去。

### Effect类型

污点定义是键值对数据，**key=value:effect**, key和value是**污点的标签**；effect描述污点的作用，支持如下三个选项：

1. `PreferNoSchedule`：kubernetes将尽量避免把Pod调度到具有该污点的Node上，除非没有其他节点可调度
   - 尽量别来，除非没办法
   - 适用于软性资源隔离的场景

2. `NoSchedule`：kubernetes将不会把Pod调度到具有该污点的Node上，但不会影响当前Node上已存在的Pod
   - 新的别来，在这的就别动了
   - 用于资源隔离（比如给GPU节点打上污点）和节点维护的场景

3. `NoExecute`：kubernetes将不会把Pod调度到具有该污点的Node上，同时也会将Node上已存在的Pod驱离
   - 新的别来，旧的赶紧走
   - 用于节点故障转移、紧急维护的场景


### 污点操作

打污点：

~~~sh
kubectl taint node node-01 ssd=true:PreferNoschedule
# 不包含value
kubectl taint node node-01 ssd:PreferNoschedule
# 所有节点打污点
kubectl taint node ssd=true:PreferNoschedule --all
~~~

查看一个节点的污点：

```bash
kubectl get node master-01 -o=jsonpath='{.spec.taints}'
kubectl describe node master-01 | grep Taint -A 10
# 看所有节点的污点
kuebctl describe node | grep Taint -A 10
```

删除污点：

~~~sh
kubectl taint node node-01 ssd=true:PreferNoSchedule-
~~~

修改污点（必须是key和effect相同，只改value的情况）

~~~sh
kubectl taint node node-01 ssf=false:PerferNoSchedule --overwtire
~~~

### 常见内置污点

- node.kubernetes.io/not-ready：相当于节点状态Ready为false。节点出问题时会自动添加这个污点。会自动驱逐pod。
- node.kubernetes.io/unreachable：Node Controller访问不到节点时会自动添加，相当于节点状态Ready的值为Unknown。会自动驱逐pod。
- node.kubernetes.io/out-of-disk：节点磁盘耗尽
- node.kubernetes.io/memory-pressure：节点内存压力
- node.kubernetes.io/disk-pressure：节点磁盘压力
- node.kubernetes.io/pid-pressure：节点pid压力
- node.kubernetes.io/network-unavailable：节点网络不可达
- node.kubernetes.io/unschedulable：节点不可调度

除了前两个，后面的都是不会驱逐pod的。

## 容忍

键值对数据，要定义出来容忍什么k、v、effect的污点。

注意pod定义了容忍，只是可以被调度到污点节点上，而不是一定会调度到带污点的节点上。

```bash
# node-02生产环境专用，打一个污点来区分
kubectl taint node node-02 node-type=production:NoExcute

# 给节点去除污点，后面带一个减号
kubectl taint node node-02 key: node-type-
```

### 容忍类型

~~~yaml
# 完全匹配。容忍的k，v，effect和污点的完全一样
tolerations:
- key: "taintKey"
  operator: "Equal"
  value: "taintValue"
  effect: "NoSchedule"
  
# 不完全匹配，没有value，只要容忍的key、effect和污点一样就能匹配上
tolerations:
- key: "taintKey"
  operator: "Equal"
  effect: "NoSchedule"

# Key匹配，容忍的key和污点的key一样就能匹配上
tolerations:
- key: "taintKey"
  operator: "Exists"

# 容忍所有污点（不推荐），除非是daemonset要在所有节点部署。
tolerations:
- operator: "Exists"

# 容忍一段时间。只容忍3600s，之后这个pod就要走了。适用于节点故障快速漂移。容忍not-ready和unreachable的污点，时间10s。节点故障之后10s，pod就可以漂移了。（默认是300s才开始漂移）
tolerations:
- key: "taintKey"
  operator: "Equal"
  value: "taintValue"
  effect: "NoSchedule"
  tolerationSeconds: 3600
~~~

### 字段配置

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
    operator: "Equal" # Equal要求k、v、effect必须全部匹配上，才能容忍。如果是Exists，那么NoExcute可以向下兼容匹配到 NoSchedule、PreferNoSchedule的effect。(NoExcute > NoSchedule > PreferNoSchedule)
    value: "production" # value可以是空的，表示容忍特定key的污点
    effect: "NoExecute" # effect也可以是空的。
    tolerationSeconds: 10 # NoExcute专用字段。容忍10s后就立刻被驱逐。
```

## 污点容忍实战示例

### 主节点禁止调度

在生产环境中，Kubernetes 的主节点除了部署系统组件外，不推荐再部署任何服务，此时可 以通过添加污点来禁止调度：

~~~sh
kubectl taint node k8s-master01 node-role.kubernetes.io/control-plane:NoSchedule
# 也可以添加NoExecute类型的污点，此时不容忍该污点的Pod会被驱逐重建： 
kubectl taint node k8s-master01 node-role.kubernetes.io/control-plane:NoExecute 
~~~

一般建议把NoSchedule和NoExecute都加上。

### 新节点禁止调度

当Kubernetes 集群添加新节点时，通常情况下不会立即调度Pod到该节点，需要经过完整 的可用性测试之后才可以调度Pod，此时也可以使用污点先临时禁止该节点的调度：

~~~sh
kubectl taint node k8s-master01 new-node=true:NoSchedule
# 同样的道理，比如在禁止调度之前已经有Pod部署在该节点，可以进行驱逐： 
kubectl taint node k8s-master01 new-node=true:NoExecute 
~~~

### 节点维护和下线

当Kubernetes的节点需要进行下线维护时，此时需要先把该节点的服务进行驱逐和重新调度。

此时需要根据实际情况判断是直接驱逐还是选择重新调度，比如某个Pod只有一个副本，或者某个服务比较重要，就不能直接进行驱逐，而是需要先把节点关闭调度，然后在进行服务的重新部署。

#### 基于污点实现

关闭维护节点的调度，用NoSchedule：

~~~sh
kubectl taint node k8s-node02 maintain:NoSchedule 
~~~

重新触发某个服务的滚动改部署，这样新pod会调度到其他节点：

~~~sh
kubectl rollout restart deploy redis -n basic-component-dev
~~~

接下来节点上已经没有重要服务了，可以对节点的其他不重要pod进行驱逐，用NoExecute：

~~~sh
kubectl taint node k8s-node02 maintain:NoExecute 
~~~

驱逐后，即可按照预期进行对节点进行维护，维护完成以后，可以删除污点，恢复调度： 

~~~sh
kubectl taint node k8s-node02 maintain- 
~~~

#### 基于cordon实现

除了自定义污点，也可以使用cordon将节点设置为维护状态： 

~~~sh
kubectl cordon k8s-node01 
~~~

此时节点会被标记一个SchedulingDisabled状态（其实也是通过内置NoSchedule污点实现），但是已经运行在该节点的Pod不受影响。

然后驱逐节点上面的服务：

~~~sh
kubectl drain k8s-node01 --ignore-daemonsets --delete-emptydir-data
~~~

恢复节点：

~~~sh
kubectl uncordon k8s-node01
~~~

### 特殊节点资源保留

当Kubernetes中存储特殊节点时，应该尽量保持不要特殊资源的Pod不要调度到这些节点上，此时可以通过污点进行控制。

比如包含了GPU的节点，不能被任意调度：

~~~sh
kubectl taint node k8s-node02 gpu=true:NoSchedule 
~~~

具有其它特殊资源，比如是ssd节点，尽量不要调度：

~~~sh
kubectl taint node k8s-node02 ssd=true:PreferNoSchedule
~~~

如果某个pod需要GPU资源，添加容忍才能调度上去：

~~~yaml
tolerations: 
- key: "gpu" 
  operator: "Exists" 
  effect: "NoSchedule" 
~~~

完整配置，同时添加了节点选择器和容忍（或者不用节点选择器，用resource申请GPU资源也行）

~~~yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: gpu-example 
spec: 
  replicas: 1 
  selector: 
    matchLabels: 
      app: gpu-example 
  template: 
    metadata: 
      labels: 
        app: gpu-example 
    spec: 
      nodeSelector: # 必须定义节点选择器才能保证调度到gpu节点
        gpu: "true" 
      tolerations: # 容忍不能保证一定部署到GPU节点上，要用节点选择器配合容忍才行
      - key: "gpu" 
        operator: "Exists" 
        effect: "NoSchedule" 
      containers: 
      - name: gpu-example 
        image: nginx:1.15.12
~~~

### 专用节点隔离

一个Kubernetes集群，很常见会有一些专用的节点，比如ingress controller、gateway、storage或者多租户环境等。

这些节点通常不建议和其他服务交叉使用，所以需要利用污点和容忍将这些节点隔离起来。

比如选择一批节点作为ingress入口的节点：

~~~sh
kubectl label node k8s-node02 ingress=true 
# 添加一个污点，不让其他服务部署 
kubectl taint node k8s-node02 ingress=true:NoSchedule 
~~~

更改Ingress Controller的部署资源，添加容忍和节点选择器：

~~~yaml
kubectl edit ds -n ingress-nginx 
nodeSelector: 
  ingress: "true" 
  kubernetes.io/os: linux 
tolerations: 
- key: ingress 
  operator: Exists
  effect: NoSchedule
~~~

### 节点宕机快速恢复

当Kubernetes集群中有节点故障时，Kubernetes会自动恢复故障节点上的服务：

1. 自动给故障节点打上node.kubernetes.io/unreachable和node.kubernetes.io/not-ready污点，effect是NoExecute。

2. 污点打完，上面的pod并不是立刻被驱逐。默认情况下，节点故障时五分钟后，会重新调度上面的pod。

此时可以利用污点的 tolerationSeconds 加快pod被驱逐的速度。

~~~yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: tolerations-second 
spec: 
  replicas: 1 
  selector: 
    matchLabels: 
      app: tolerations-second 
  template: 
    metadata: 
      labels: 
        app: tolerations-second 
    spec: 
      tolerations: 
      - key: node.kubernetes.io/unreachable 
		operator: Exists 
		effect: NoExecute
		tolerationSeconds: 10 # 容忍not-ready和unreachable的污点，时间10s。节点故障之后10s，pod就可以漂移了。（默认是300s才开始漂移）
 	  - key: node.kubernetes.io/not-ready 
		operator: Exists 
		effect: NoExecute
		tolerationSeconds: 10 
      containers: 
      - name: nginx
        image: nginx:1.15.12 
~~~

