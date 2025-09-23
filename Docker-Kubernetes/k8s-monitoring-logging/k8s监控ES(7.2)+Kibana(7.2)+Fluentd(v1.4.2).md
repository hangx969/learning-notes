# 日志简介

## 日志的常见级别

- 日志打印通常有四种级别，从高到底分别是：ERROR、WARNING、INFO、DEBUG。应该选用哪种级别是个很重要的问题：

1、DEBUG：

DEBU可以打印出最详细的日志信息，主要用于开发过程中打印一些运行信息。

2、INFO：

INFO可以打印一些你感兴趣的或者重要的信息，这个可以用于生产环境中输出程序运行的一些重要信息，但是不能滥用，避免打印过多的日志。

3、WARNING： 

WARNING 表明发生了一些暂时不影响运行的错误，会出现潜在错误的情形，有些信息不是错误信息，但是也要给程序员的一些提示 

4、ERROR：

ERROR 可以打印错误和异常信息，如果不想输出太多的日志，可以使用这个级别，这一级就是比较重要的错误了，软件的某些功能已经不能继续执行了。

- 日志级别中的优先级：
  - 在系统中如果开启了某一级别的日志后，就不会打印比它级别低的日志。例如，程序如果开启了INFO级别日志，DEBUG日志就不会打印，只会打印ERROR、WARNING、INFO。通常在生产环境中开启INFO日志。

# 常见日志分析方案

## EFK

- 在Kubernetes集群上运行多个服务和应用程序时，日志收集系统可以帮助你快速分类和分析由Pod生成的大量日志数据。Kubernetes中比较流行的日志收集解决方案是Elasticsearch、Fluentd和Kibana（EFK）技术栈，也是官方推荐的一种方案。

- Elasticsearch是一个实时的，分布式的，可扩展的搜索引擎，它允许进行全文本和结构化搜索以及对日志进行分析。它通常用于索引和搜索大量日志数据，也可以用于搜索许多不同种类的文档。

- Elasticsearch通常与Kibana一起部署，kibana可以把Elasticsearch采集到的数据通过dashboard（仪表板）可视化展示出来。Kibana允许你通过Web界面浏览Elasticsearch日志数据，也可自定义查询条件快速检索出elasticccsearch中的日志数据。

- Fluentd是一个流行的开源数据收集器，我们在 Kubernetes 集群节点上安装 Fluentd，通过获取容器日志文件、过滤和转换日志数据，然后将数据传递到 Elasticsearch 集群，在该集群中对其进行索引和存储。
- (有时候F也可以是Filebeat)

## ELK

- E - Elasticsearch（简称：ES）

- L - Logstash

  - Logstash：是一个完全开源的工具，他可以对你的日志进行收集、过滤，并将其存储供以后使用（支持动态的从各种数据源搜集数据，并对数据进行过滤、分析、丰富、统一格式等操作。）。

- K - Kibana

  ![image-20240105164157769](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401051641038.png)

> - EFK和ELK，区别就在于中间的日志收集组件F（fluentd或filebeat）vs L（logstash）
> - F是轻量级的；L是重量级的，logstash本身占用内存就很大，如果拿它来采集日志会占用很多资源。优点是日志格式转换功能很强大。
> - ELK也称ELK Stack

## ELK+filebeat

![image-20240105164228366](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401051642422.png)

- Filebeat（采集）—> Logstash（聚合、处理，转格式用，部署一个就够）—> ElasticSearch（存储）—>Kibana（展示）

## 其他方案

ELK日志流程可以有多种方案（不同组件可自由组合，根据自身业务配置），常见有以下：

- Logstash（采集、处理）—> ElasticSearch （存储）—>Kibana （展示）

- Filebeat（采集、处理）—> ElasticSearch （存储）—>Kibana （展示）

- Filebeat（采集）—> Logstash（聚合、处理）—> ElasticSearch （存储）—>Kibana （展示）

- **Filebeat（采集）—> Kafka/Redis(消峰) —> Logstash（聚合、处理）—> ElasticSearch （存储）—> Kibana （展示）**

> 前三种方案可能会在日志量大的时候产生延迟，所以第四种方案加了消息队列做缓冲，适合大量日志情形（每天上TB的日志）

## 组件介绍

### ElasticSearch

- Elasticsearch 是一个分布式的免费开源搜索和分析引擎，适用于包括文本、数字、地理空间、结构化和非结构化数据等在内的所有类型的数据。Elasticsearch 在 Apache Lucene 的基础上开发而成，由 Elasticsearch N.V.（即现在的 Elastic）于 2010 年首次发布。Elasticsearch 以其简单的 REST 风格 API、分布式特性、速度和可扩展性而闻名，是 Elastic Stack 的核心组件；
- Elastic Stack 是一套适用于数据采集、扩充、存储、分析和可视化的免费开源工具。人们通常将 Elastic Stack 称为 ELK Stack（代指 Elasticsearch、Logstash 和 Kibana），目前 Elastic Stack 包括一系列丰富的轻量型数据采集代理，这些代理统称为 Beats，可用来向 Elasticsearch 发送数据。

### beats

- Beats是一个轻量级日志采集器，Beats家族有6个成员，早期的ELK架构中使用Logstash收集、解析日志，但是Logstash对内存、cpu、io等资源消耗比较高。相比Logstash，Beats所占系统的CPU和内存几乎可以忽略不计。
- 目前Beats包含六种工具：

1、Packetbeat：网络数据（收集网络流量数据）

2、Metricbeat：指标（收集系统、进程和文件系统级别的CPU和内存使用情况等数据）

3、Filebeat：日志文件（收集文件数据）

4、Winlogbeat：windows事件日志（收集Windows事件日志数据）

5、Auditbeat：审计数据（收集审计日志）

6、Heartbeat：运行时间监控（收集系统运行时的数据）

### filebeat

- Filebeat是用于转发和收集日志数据的轻量级传送工具。Filebeat监视你指定的日志文件或位置，收集日志事件，并将它们转发到Elasticsearch或 Logstash中。

- Filebeat的工作方式如下：

  - 启动Filebeat时，它将启动一个或多个输入，这些输入将在日志数据指定的位置中查找。
  - 对于Filebeat所找到的每个日志，Filebeat都会启动收集器。每个收集器都读取单个日志以获取新内容，并将新日志数据发送到libbeat。
  - libbeat将聚集事件，并将聚集的数据发送到Filebeat配置的输出。

  ![image-20240105165630579](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401051656658.png)

- Filebeat 有两个主要组件：

  - harvester：一个harvester负责读取一个单个文件的内容。harvester逐行读取每个文件，并把这些内容发送到输出。每个文件启动一个harvester。

  - Input：一个input负责管理harvesters，并找到所有要读取的源。如果input类型是log，则input查找驱动器上与已定义的log日志路径匹配的所有文件，并为每个文件启动一个harvester。

- 传输方案

  1、output.elasticsearch

  - 如果你希望使用 filebeat 直接向 elasticsearch 输出数据，需要配置 output.elasticsearch

  ```yaml
  output.elasticsearch:
    hosts: ["192.168.40.180:9200"]
  ```

  2、output.logstash

  - 如果使用filebeat向 logstash输出数据，然后由 logstash 再向elasticsearch 输出数据，需要配置 output.logstash。
  - logstash 和 filebeat 一起工作时，如果 logstash 忙于处理数据，会通知FileBeat放慢读取速度。一旦拥塞得到解决，FileBeat 将恢复到原来的速度并继续传播。这样，可以减少管道超负荷的情况。

  ```yaml
  output.logstash:
    hosts: ["192.168.40.180:5044"] 
  ```

  3、output.kafka

  - 如果使用filebeat向kafka输出数据，然后由 logstash 作为消费者拉取kafka中的日志，并再向elasticsearch 输出数据，需要配置 output.logstash

  ```yaml
  output.kafka:
    enabled: true
    hosts: ["192.168.40.180:9092"]
    topic: elfk8stest
  ```

### logstash

- Logstash是一个开源数据收集引擎，具有实时管道功能。Logstash可以动态地将来自不同数据源的数据统一起来，并将数据标准化到你所选择的目的地。Logstash 是一个应用程序日志、事件的传输、处理、管理和搜索的平台。你可以用它来统一对应用程序日志进行收集管理，提供 Web 接口用于查询和统计。

- 工作原理

  ![image-20240105170525124](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401051705178.png)

  - Logstash 有两个必要元素：input 和 output ，一个可选元素：filter。 这三个元素分别代表 Logstash 事件处理的三个阶段：输入 > 过滤器 > 输出

    - Input负责从数据源采集数据。

    - filter 将数据修改为你指定的格式或内容。

    - output 将数据传输到目的地。

  - 在实际应用场景中，通常输入、输出、过滤器不止一个。Logstash 的这三个元素都使用插件式管理方式，可以根据应用需要，灵活的选用各阶段需要的插件，并组合使用。

- 常用input模块

  Logstash 支持各种输入选择 ，可以在同一时间从众多常用来源捕捉事件。能够以连续的流式传输方式，可从日志、指标、Web 应用、数据存储以及各种 AWS 服务采集数据。

  - file：从文件系统上的文件读取

  - syslog：在众所周知的端口514上侦听系统日志消息，并根据RFC3164格式进行解析

  - redis：从redis服务器读取，使用redis通道和redis列表。 Redis经常用作集中式Logstash安装中的“代理”，它将接收来自远程Logstash“托运人”的Logstash事件排队。

  - beats：处理由Filebeat发送的事件。

- 常用的filter模块

  - grok：解析和结构任意文本。Grok目前是Logstash中将非结构化日志数据解析为结构化和可查询的最佳方法。

  - mutate：对事件字段执行一般转换。可以重命名，删除，替换和修改事件中的字段。
  - drop：完全放弃一个事件，例如调试事件。
  - clone：制作一个事件的副本，可能会添加或删除字段。
  - geoip：添加有关IP地址的地理位置的信息

- 常用output

  - elasticsearch：将事件数据发送给 Elasticsearch（推荐模式）。

  - file：将事件数据写入文件或磁盘。

  - graphite：将事件数据发送给 graphite（一个流行的开源工具，存储和绘制指标，http://graphite.readthedocs.io/en/latest/）。

  - statsd：将事件数据发送到 statsd（这是一种侦听统计数据的服务，如计数器和定时器，通过UDP发送并将聚合发送到一个或多个可插入的后端服务）。

- 常用code插件

  -  json：以JSON格式对数据进行编码或解码。

  -  multiline：将多行文本事件（如java异常和堆栈跟踪消息）合并为单个事件。

- logstash在不考虑性能的前提下，适用于解决复杂的日志解析情况；性能有限情况下，不推荐给每台服务器部署logstash。

### fluentd

- fluentd是一个针对日志的收集、处理、转发系统。通过丰富的插件系统，可以收集来自于各种系统或应用的日志，转化为用户指定的格式后，转发到用户所指定的日志存储系统之中。
- fluentbit是比fluentd更轻量的工具，适用于更小型的或者嵌入式的设备。

### rsyslog

- 绝大多数 Linux 发布版本默认的 syslog 守护进程，rsyslog 可以做的不仅仅是将日志从 syslog socket 读取并写入 /var/log/messages 。它可以提取文件、解析、缓冲(磁盘和内存)以及将它们传输到多个目的地，包括 Elasticsearch 

# 部署es+fluentd+kibana方案

- 部署一个有3个节点的Elasticsearch集群。我们使用3个Elasticsearch Pods可以避免高可用中的多节点群集中发生的“脑裂”的问题。 Elasticsearch脑裂可参考如下：https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-node.html#split-brain

  > - 在 Elasticsearch 中，"脑裂"（Split Brain）是一个术语，用于描述当网络异常发生时，集群的节点被分成两个或更多的独立的组，每个组都不能与其他组通信。这可能导致数据不一致，因为每个分区可能会独立地做出决策，例如选举主节点或接受写操作。
  >
  > - 为了防止脑裂，Elasticsearch 使用了一种叫做 "最小主节点" 的设置。这个设置定义了一个节点数，只有当集群中的节点数达到这个数时，才能进行主节点的选举。这样可以确保在网络分区事件发生时，只有节点最多的那一部分可以选举主节点，从而避免数据不一致。并且确保了在任何时候，集群中只有一个主节点。
  > - 如果你有 3 个节点，那么 "最小主节点" 的数量应该设置为 2。这意味着只有当至少有 2 个节点可以通信时，才能进行主节点的选举。如果网络分区导致 3 个节点被分成了两组（例如，一组有 2 个节点，另一组有 1 个节点），那么只有节点数为 2 的那一组可以选举主节点，因为它满足了 "最小主节点" 的数量要求。这样就避免了脑裂问题。

- 可以在dockerhub里面搜到最新版的：[elasticsearch - Official Image (docker.com)](https://hub.docker.com/_/elasticsearch)，[kibana - Official Image (docker.com)](https://hub.docker.com/_/kibana)、[fluentd - Official Image (docker.com)](https://hub.docker.com/_/fluentd)

## 部署nfs-provisioner

### 安装nfs服务

```sh
#安装nfs服务，nfs server端是master1节点
#所有node上yum安装nfs
yum install nfs-utils -y

#所有node上启动nfs服务
systemctl start nfs
systemctl enable nfs

#在master-1上创建nfs共享目录
mkdir /data/v1 -p

#编辑/etc/exports文件
vim /etc/exports
/data/v1 192.168.40.0/24(rw,no_root_squash)

#加载配置，使配置生效
exportfs -arv
systemctl restart nfs
```

### RBAC授权

- nfs-provisioner需要与apiserver交互，所以需要sa rbac赋权

```yaml
#创建sa
apiVersion: v1
kind: ServiceAccount
metadata:
 name: nfs-provisioner
---
#创建nfs用的clusterrole
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: nfs-provisioner-runner
rules:
  - apiGroups: [""]
    resources: ["persistentvolumes"]
    verbs: ["get", "list", "watch", "create", "delete"]
  - apiGroups: [""]
    resources: ["persistentvolumeclaims"]
    verbs: ["get", "list", "watch", "update"]
  - apiGroups: ["storage.k8s.io"]
    resources: ["storageclasses"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["create", "update", "patch"]
  - apiGroups: [""]
    resources: ["services", "endpoints"]
    verbs: ["get"]
  - apiGroups: ["extensions"]
    resources: ["podsecuritypolicies"]
    resourceNames: ["nfs-provisioner"]
    verbs: ["use"]
---
#给sa赋权
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: run-nfs-provisioner
subjects:
  - kind: ServiceAccount
    name: nfs-provisioner
    namespace: default
roleRef:
  kind: ClusterRole
  name: nfs-provisioner-runner
  apiGroup: rbac.authorization.k8s.io
---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: leader-locking-nfs-provisioner
rules:
  - apiGroups: [""]
    resources: ["endpoints"]
    verbs: ["get", "list", "watch", "create", "update", "patch"]
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: leader-locking-nfs-provisioner
subjects:
  - kind: ServiceAccount
    name: nfs-provisioner
    namespace: default
roleRef:
  kind: Role
  name: leader-locking-nfs-provisioner
  apiGroup: rbac.authorization.k8s.io
```

> 注意：k8s1.20+版本通过nfs provisioner动态生成pv会报错: Unexpected error getting claim reference to claim "default/test-claim1": selfLink was empty, can't make reference，报错原因是1.20版本启用了selfLink，解决方法如下；
>
> - vim /etc/kubernetes/manifests/kube-apiserver.yaml
>
> ```yaml
> spec:
>   containers:
>   - command:
>   - kube-apiserver
>   #添加这一行：
>   - --feature-gates=RemoveSelfLink=false
> ```
>
> ```sh
> #更新apiserver
> kubectl apply -f /etc/kubernetes/manifests/kube-apiserver.yaml
> ```
>
> - 重新更新apiserver.yaml会有生成一个新的pod：kube-apiserver，这个pod状态是CrashLoopBackOff，需要删除
>
> ```sh
> kubectl delete pods kube-apiserver -n kube-system
> ```
>
> - /etc/kubernetes/manifests/kube-apiserver.yaml这个文件默认的权限是：600，不能改，改完之后就连不到apiserver了。
> - 注意：1.27版本这个feature-gate不需要改了

### 部署nfs-provisioner deploy

```yaml
kind: Deployment
apiVersion: apps/v1
metadata:
  name: nfs-provisioner
spec:
  selector:
    matchLabels:
      app: nfs-provisioner
  replicas: 1
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: nfs-provisioner
    spec:
      serviceAccount: nfs-provisioner
      containers:
        - name: nfs-provisioner
          #这个image需要先上传
          image: registry.cn-hangzhou.aliyuncs.com/open-ali/xianchao/nfs-client-provisioner:v1
          imagePullPolicy: IfNotPresent
          volumeMounts:
            - name: nfs-client-root
              mountPath: /persistentvolumes
          env:
            - name: PROVISIONER_NAME
              value: example.com/nfs
            - name: NFS_SERVER
              value: 192.168.40.180 #nfs服务端ip
            - name: NFS_PATH
              value: /data/v1 #nfs服务端共享的目录
      volumes:
        - name: nfs-client-root
          nfs:
            server: 192.168.40.180
            path: /data/v1
```

### 创建storage class

~~~yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: do-block-storage
provisioner: example.com/nfs #该值需要和nfs provisioner deploy的env里配置的PROVISIONER_NAME值保持一致
~~~

## 部署elastic search

```bash
#创建namespace
kubectl create ns kube-logging
```

~~~yaml
#创建headless svc代理sts pod
kind: Service
apiVersion: v1
metadata:
  name: elasticsearch
  namespace: kube-logging
  labels:
    app: elasticsearch
spec:
  selector:
    app: elasticsearch
  clusterIP: None
  ports:
    - port: 9200
      name: rest
    - port: 9300
      name: inter-node
---
#创建sts
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: es-cluster #pod名称为es-cluster，可以通过es-cluster-[0,1,2].elasticsearch.kube-logging.svc.cluster.local，由headless svc解析到pod ip地址
  namespace: kube-logging
spec:
  serviceName: elasticsearch
  replicas: 3
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      containers:
      - name: elasticsearch
        image: docker.elastic.co/elasticsearch/elasticsearch:7.2.0
        imagePullPolicy: IfNotPresent
        resources:
            limits:
              cpu: 1000m
            requests:
              cpu: 100m
        ports:
        - containerPort: 9200
          name: rest
          protocol: TCP
        - containerPort: 9300
          name: inter-node
          protocol: TCP
        volumeMounts:
        - name: data
          mountPath: /usr/share/elasticsearch/data
        env:
          - name: cluster.name
            value: k8s-logs
          - name: node.name
            valueFrom:
              fieldRef:
                fieldPath: metadata.name
          - name: discovery.seed_hosts
            value: "es-cluster-0.elasticsearch.kube-logging.svc.cluster.local,es-cluster-1.elasticsearch.kube-logging.svc.cluster.local,es-cluster-2.elasticsearch.kube-logging.svc.cluster.local"
          #此字段用于设置在es集群中节点相互连接的发现方法，它为集群指定了一个静态主机列表。sts Pod具有唯一的 DNS 地址es-cluster-[0,1,2].elasticsearch.kube-logging.svc.cluster.local，因此我们相应地设置此地址变量即可。es发现的更多信息：https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-discovery.html
          - name: cluster.initial_master_nodes
            value: "es-cluster-0,es-cluster-1,es-cluster-2"
          - name: ES_JAVA_OPTS
            value: "-Xms512m -Xmx512m"
            #这里我们设置为-Xms512m -Xmx512m，告诉JVM使用512 MB的最小和最大堆。
      initContainers:
      - name: fix-permissions
        image: busybox
        imagePullPolicy: IfNotPresent
        command: ["sh", "-c", "chown -R 1000:1000 /usr/share/elasticsearch/data"]
        #将 Elasticsearch 数据目录的用户和组更改为1000:1000（es服务的 UID），pod里面运行的服务通常是uid 1000
        #默认k8s用root挂载数据目录，这会使得es无法访问数据目录，参考es中的默认注意事项：https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#_notes_for_production_use_and_defaults。
        securityContext:
          privileged: true
        volumeMounts:
        - name: data
          mountPath: /usr/share/elasticsearch/data
      - name: increase-vm-max-map 
        image: busybox
        imagePullPolicy: IfNotPresent
        command: ["sysctl", "-w", "vm.max_map_count=262144"] #增加操作系统对mmap计数的限制，默认情况下该值可能太低，导致内存不足的错误：https://www.elastic.co/guide/en/elasticsearch/reference/current/vm-max-map-count.html
        securityContext:
          privileged: true
      - name: increase-fd-ulimit 
        image: busybox
        imagePullPolicy: IfNotPresent
        command: ["sh", "-c", "ulimit -n 65536"] #增加打开文件描述符的最大数量
        securityContext:
          privileged: true
  volumeClaimTemplates:
  - metadata:
      name: data
      labels:
        app: elasticsearch
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: do-block-storage
      resources:
        requests:
          storage: 5Gi
~~~

- pod部署完成之后，可以通过REST API检查elasticsearch集群是否部署成功，使用下面的命令将本地端口9200转发到 Elasticsearch 节点（如es-cluster-0）对应的端口：

  ```sh
  kubectl port-forward es-cluster-0 9200:9200 --namespace=kube-logging
  
  #本地主机的 9200 端口转发到es-cluster-0 的 9200 端口。可以通过访问本地主机的 9200 端口来访问 es-cluster-0 Pod 的 9200 端口提供的服务了。
  #命令是临时的，ctrl+c一停止，端口转发就停止了。
  ```

- 然后，在另外的终端窗口中，执行如下请求：

  ```sh
  curl http://localhost:9200/_cluster/state?pretty
  #返回json文件，说明了es集群的状态
  ```

## 部署fluentd

- 使用daemonset部署fluentd，保证每个节点都运行同样的pod副本，抓每个节点的日志。
- 容器应用程序的输入输出日志会重定向到node节点里的json文件中，fluentd可以tail和过滤以及把日志转换成指定的格式发送到elasticsearch集群中。
- 除了容器日志，fluentd也可以采集kubelet、kube-proxy、docker的日志。

~~~yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: fluentd
  namespace: kube-logging
  labels:
    app: fluentd
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: fluentd
  labels:
    app: fluentd
rules:
- apiGroups:
  - ""
  resources:
  - pods
  - namespaces
  verbs:
  - get
  - list
  - watch
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: fluentd
roleRef:
  kind: ClusterRole
  name: fluentd
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: ServiceAccount
  name: fluentd
  namespace: kube-logging
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: kube-logging
  labels:
    app: fluentd
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      serviceAccount: fluentd
      serviceAccountName: fluentd
      tolerations:
      - key: node-role.kubernetes.io/master
        effect: NoSchedule
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemonset:v1.4.2-debian-elasticsearch-1.1
        #适用于containerd容器运行时的镜像：docker.io/fluent/fluentd-kubernetes-daemonset:v1.16-debian-elasticsearch7-1
        imagePullPolicy: IfNotPresent
        env:
          - name:  FLUENT_ELASTICSEARCH_HOST
            value: "elasticsearch.kube-logging.svc.cluster.local"
          - name:  FLUENT_ELASTICSEARCH_PORT
            value: "9200"
          - name: FLUENT_ELASTICSEARCH_SCHEME
            value: "http"
          - name: FLUENTD_SYSTEMD_CONF
            value: disable
          #禁用systemd日志收集，通常用于优化Fluentd的性能，因为收集和处理 systemd 的日志可能会消耗大量的 CPU 和内存资源。如果你的应用程序不依赖systemd 的日志，或者你有其他方式来收集这些日志，那么可以安全地禁用这个功能。
          #systemd 的日志是由 systemd 产生的，记录了系统服务的启动、运行和停止等信息。这些日志通常存储在 /var/log/journal/ 目录下
          #如果用containerd作为容器运行时，需要加上下面两行。
          #- name: FLUENT_CONTAINER_TAIL_PARSER_TYPE
          #  value: "cri"
          #- name: FLUENT_CONTAINER_TAIL_PARSER_TIME_FORMAT
          #  value: "%Y-%m-%dT%H:%M:%S.%L%z"
        resources:
          limits:
            memory: 512Mi
          requests:
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      terminationGracePeriodSeconds: 30
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
~~~

## 部署kibana可视化UI界面

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: kibana
  namespace: kube-logging
  labels:
    app: kibana
spec:
  ports:
  - port: 5601
  selector:
    app: kibana
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kibana
  namespace: kube-logging
  labels:
    app: kibana
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kibana
  template:
    metadata:
      labels:
        app: kibana
    spec:
      containers:
      - name: kibana
        image: docker.elastic.co/kibana/kibana:7.2.0
        imagePullPolicy: IfNotPresent
        resources:
          limits:
            cpu: 1000m
          requests:
            cpu: 100m
        env:
          - name: ELASTICSEARCH_URL
            value: http://elasticsearch.kube-logging.svc.cluster.loccal:9200 #环境变量设置es暴露的rest接口的端口
        ports:
        - containerPort: 5601
~~~

- kibana的svc开了node的31966端口，浏览器访问即可看到。

- 配置UI界面

  ![image-20240106160418876](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401061604157.png)

![image-20240106160503170](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401061605221.png)

- 输入`logstash*`即可匹配到 Elasticsearch 集群中的所有日志数据。-> Next，选择@timestamp -> Create Index Pattern

- 点击左侧discovery可以查看日志，点击左侧添加不同字段。

- 可以添加filter或者用query来查：

  ![image-20240106163251702](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401061632776.png)

## 测试EFK收集业务pod日志

~~~yaml
#部署示例业务pod
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dep-busybox
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: busybox
  template:
    metadata:
      labels:
        app: busybox
    spec:
      containers:
      - name: busybox
        image: busybox:latest
        imagePullPolicy: IfNotPresent
        args: ["/bin/sh", "-c", 'i=0; while true; do echo "$i: $(date)"; i=$((i+1)); sleep 1; done']
        volumeMounts:
        - name: localtime
          mountPath: /etc/localtime
      volumes:
      - name: localtime
        hostPath:
          path: /usr/share/zoneinfo/Asia/Shanghai
~~~

> ~~~yaml
>         volumeMounts:
>         - name: localtime
>           mountPath: /etc/localtime
>       volumes:
>       - name: localtime
>         hostPath:
>           path: /usr/share/zoneinfo/Asia/Shanghai
> ~~~
>
> - 通过这一部分的挂载，把本地的北京时间挂到了pod里面，让pod中产生的log时间更易读。

- kibana中，通过query pod name来看：

  ~~~mysql
  kubernetes.pod_name : dep-busybox-577ccf67c4-nqbcn
  ~~~

# 
