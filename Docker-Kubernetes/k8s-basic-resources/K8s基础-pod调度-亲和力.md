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
# node-02生产环境专用，打一个污点来区分
kubectl taint node node-02 node-type=production:NoExcute

# 给节点去除污点，后面带一个减号
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
    operator: "Equal" # Equal要求k、v、effect必须全部匹配上，才能容忍。如果是Exists，那么NoExcute可以向下兼容匹配到 NoSchedule、PreferNoSchedule的effect。(NoExcute > NoSchedule > PreferNoSchedule)
    value: "production" # value可以是空的，表示容忍特定key的污点
    effect: "NoExecute" # effect也可以是空的。
    tolerationSeconds: 3600 # NoExcute专用字段，通常情况下，如果给一个节点添加了一个 effect 值为 NoExecute 的污点，则任何不能容忍这个污点的 Pod 都会马上被驱逐，任何可以容忍这个污点的 Pod 都不会被驱逐。但是，如果 Pod 存在一个 effect 值为 NoExecute 的容忍度指定了可选属性 tolerationSeconds 的值，则表示在给节点添加了上述污点之后， Pod 还能继续在节点上运行的时间。3600这表示如果这个 Pod 正在运行，同时一个匹配的污点被添加到其所在的节点， 那么 Pod 还将继续在节点上运行 3600 秒，然后被驱逐。 如果在此之前上述污点被删除了，则 Pod 不会被驱逐。
```

# 实战示例

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
        image: registry.cn-beijing.aliyuncs.com/dotbalo/nginx:1.15.12 
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
        image: registry.cn-beijing.aliyuncs.com/dotbalo/nginx:1.15.12 
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

