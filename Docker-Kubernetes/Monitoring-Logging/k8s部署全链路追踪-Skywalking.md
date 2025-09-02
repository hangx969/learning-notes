# 链路追踪介绍

为什么要用全链路追踪工具：

1. 当一个微服务项目接入skywalking之后，就能看到每个微服务之间的调用关系、以及每个请求的处理流程。

可以实现：

1. 快速定位故障点
2. 快速定位性能瓶颈
3. 理解服务间依赖关系
4. 全局流量可视化

## 核心概念

Trace：一个请求的完整的请求流程被称为一个Trace，代表从客户端发起请求到后端完全处理的整个过程。一个trace由多个span组成。

Span：一个span表示trace的一部分工作，可以理解为一次函数调用或者是一个HTTP请求。每个span都包含了操作名称、开始时间、结束时间以及操作的元数据等信息。span具有上下级（父子）关系，同时多个span的结合就表达了一次trace。

trace id和span id：每个trace和span都有唯一的id。每个span id包含了指向父级span的引用。

## 工作原理

1. 客户端发起请求
2. 服务A开始处理请求并创建初始Trace和Span
3. 服务A将请求转发给服务B，同时传递TraceID和SpanID
4. 服务B根据传递的信息继续创建新的Span并标记父Span
5. 所有服务处理完成后，各自产生的Span数据都会发送给追踪平台进行汇总
6. 用户可以通过UI查看整个Trace的详细信息

## 链路追踪工具

| 特性/工具  | SkyWalking                          | Pinpoint           | CAT                | Zipkin             | Jaeger                   |
| ---------- | ----------------------------------- | ------------------ | ------------------ | ------------------ | ------------------------ |
| 追踪能力   | 支持跨服务、跨方法追踪、Trace、Span | 方法级别细粒度追踪 | 跨服务追踪         | 跨服务追踪         | 跨服务追踪、分布式追踪   |
| 监控能力   | 指标监控、告警                      | 实时性能监控       | 实时性能监控、告警 | 仅追踪，不支持监控 | 主要追踪，有基础指标监控 |
| 拓扑图支持 | 自动生成服务拓扑图                  | 自动生成服务拓扑图 | 自动生成服务拓扑图 | 不支持             | 支持服务依赖图           |
| 实时性     | 秒级延迟                            | 实时               | 秒级延迟           | 分钟级延迟         | 近实时                   |
| 语言支持   | 多语言                              | 主要支持Java       | 主要支持Java       | 多语言             | 多语言                   |
| 资源消耗   | 中等                                | 较高               | 较低               | 较低               | 中等                     |
| 社区活跃度 | 高（Apache顶级项目、国人开发）      | 中                 | 中                 | 高                 | 高                       |
| 易用性     | UI直观、功能全面                    | UI简单、功能专注   | UI传统             | UI简陋             | UI现代、查询功能强       |
| 使用场景   | 中大型分布式系统                    | 方法级别细粒度追踪 | 实时监控要求高     | 轻量级追踪需求     | 云原生、微服务追踪       |

# Skywalking介绍

Skywalking是一个针对分布式系统的应用性能监控（Application Performance Monitor，APM）和可观测性分析平台（Observability Analysis Platform）。提供了包括分布式追踪、指标监控、故障诊断信息、服务网格遥测分析、异常告警以及可视化界面等功能，可帮助开发人员和运维团队更好的理解和管理应用和服务。

核心特性：

1. 分布式追踪：为请求生成跟踪数据，能够帮助用户了解整个调用链路的情况，定位性能瓶颈和问题根源
2. 度量分析：支持对服务的健康状况进行度量分析，如响应时间、吞吐量、成功率等关键性能指标。程序内信息比如垃圾回收、JVM信息都能看到。
3. 告警机制：支持自定义规则告警，当检测到异常情况时自动发送告警通知
4. 丰富的UI界面：直观易用，支持很多中间件如redis、kafka的链路图生成
5. 低侵入性：通过字节码注入的方式实现代码级别的监控，无需修改业务逻辑即可完成接入
6. 多语言支持：除了Java之外，还支持.NET Core, Node.js, Python, Go等多语言
7. 多平台集成：可以与服务网格、K8s集成

## 官网

- github：[apache/skywalking: APM, Application Performance Monitoring System](https://github.com/apache/skywalking)
- 官网：[Apache SkyWalking](https://skywalking.apache.org/)
- 中文文档：[SkyWalking 文档中文版（社区提供）](https://skyapm.github.io/document-cn-translation-of-skywalking/)

官网里面主要是去看server部分：[SkyWalking Servers](https://skywalking.apache.org/docs/#SkyWalkingServers)

根据自己的应用程序语言不同，有不同语言的agent接入skywalking的文档：[SkyWalking Agents](https://skywalking.apache.org/docs/#Agents)

安装：[SkyWalking Operation](https://skywalking.apache.org/docs/#Operation) （推荐安装在K8s中，因为方便做成一个高可用集群）

### Helm Chart

官网中提供了helm和operator安装两种方式。operator安装支持自动inject sidecar，但是对多语言支持还是不太灵活，所以还是推荐helm安装。

helm chart github：[apache/skywalking-helm at v4.7.0](https://github.com/apache/skywalking-helm/tree/v4.7.0)

## 核心术语

1. Service：一组提供相同功能或业务逻辑的应用。可以是一个微服务、一个Web应用、一个数据库等。一般是按照项目去分组。
2. Instance：服务的一个具体运行实例或者副本。在一个分布式环境中，同一个服务可能部署在多个不同的服务器或容器上，每个容器或服务器上的这个服务就是一个Instance
3. Endpoint：服务中可以被外部访问的具体路径或者接口，端点是服务对外暴露功能的入口点。

## 架构图

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202508302013712.png" alt="image-20250830201311544" style="zoom:67%;" />

1. Tracing、Metrics

   数据来源，可以用skywalking agent或者其他客户端，支持不同格式的追踪数据。只要能写到它的接口上都能接收。

2. OAP平台

   skywalking server端，集群模式多副本部署。

   - receiver：暴露gRPC和HTTP接口接受数据
   - Tracing和metrics分别接收对应的数据
   - Analysis：分析数据生成报表
   - Query：暴露查询接口

3. 数据存储

   支持ES、mysql等。推荐用ES部署，扩容方便

4. UI界面

# Helm部署skywalking集群

注意：最低需要3台4C8G的机器用于练习。

## helm chart下载

~~~sh
# 添加Skywalking Helm源：
helm repo add skywalking https://apache.jfrog.io/artifactory/skywalking-helm
helm repo update skywalking
helm pull skywalking/skywalking --version 4.3.0
# 新版skywalking迁移到了OCI仓库（新版oap起不来，这里先不用了，先用上面的4.3.0测试）
helm pull oci://registry-1.docker.io/apache/skywalking-helm --version 4.7.0
~~~

## 配置

注意：本次实验选择的是ES当做后端存储。官网提到的Opensearch和ES基本是一样的，因为ES改过开源协议，出来个平替Opensearch。

更改ES配置：

~~~yaml
elasticsearch:
  antiAffinity: soft
  clusterName: es-cluster
  config:
    host: elasticsearch
    password: admin
    port:
      http: 9200
    user: admin
  enabled: true
  esMajorVersion: "7"
  image: docker.elastic.co/elasticsearch/elasticsearch
  imagePullPolicy: IfNotPresent
  imageTag: 7.5.1
  persistence:
    enabled: true
  replicas: 3
  resources:
    limits:
      cpu: 2000m
      memory: 3Gi
    requests:
      cpu: 100m
      memory: 2Gi
  tolerations:
    - key: "node-role.kubernetes.io/control-plane"
      operator: "Equal"
      effect: "NoSchedule"
  volumeClaimTemplate:
    storageClassName: sc-nfs
    accessModes:
    - ReadWriteOnce
    resources:
      requests:
        storage: 1Gi
~~~

更改OAP资源配置：

~~~yaml
oap: 
  image: 
    repository: registry.cn-beijing.aliyuncs.com/dotbalo/skywalking-oap-server 
    tag: 10.2.0 
  javaOpts: -Xmx2g -Xms2g 
  replicas: 1 
  resources: 
    limits: 
      cpu: 2000m 
      memory: 3Gi 
    requests: 
      cpu: 100m 
      memory: 2Gi 
  storageType: elasticsearch 
  tolerations:
    - key: "node-role.kubernetes.io/control-plane"
      operator: "Equal"
      effect: "NoSchedule"
~~~

更改UI设置：

~~~yaml
ui: 
  image: 
    pullPolicy: IfNotPresent 
    repository: registry.cn-beijing.aliyuncs.com/dotbalo/skywalking-ui 
    tag: 10.2.0
  replicas: 1 
  service: 
    annotations: {} 
    externalPort: 80 
    internalPort: 8080 
    type: NodePort 
~~~

## 安装

~~~sh
# 删掉ES里面这两个文件：
rm -f skywalking/charts/elasticsearch/templates/poddisruptionbudget.yaml
rm -f skywalking/charts/elasticsearch/templates/podsecuritypolicy.yaml
# 安装
helm upgrade -i skywalking -n skywalking . --create-namespace -f values.yaml
~~~

通过NodePort访问skywalking UI

> 注：如果oap server pod始终起不来，报错是liveness probe失败，log里面没看到任何ERROR信息，可能是因为默认的liveness probe太严格了，oap启动比较慢，还没完全起来就被linevess探测给重启了。
>
> 去看template发现liveness probe是写死的，给他时间改长一点：
>
> ~~~yaml
> vim skywalking/templates/oap-deployment.yaml
>   livenessProbe:
>     tcpSocket:
>       port: 12800
>     initialDelaySeconds: 60    # 从15秒增加到60秒，给更多启动时间
>     periodSeconds: 30          # 从20秒增加到30秒，减少检查频率
>     timeoutSeconds: 10         # 超时时间
>     failureThreshold: 5        # 失败阈值，允许更多次失败
>     successThreshold: 1        # 成功阈值
> ~~~

# skywalking数据接入方案

其它Agent参考文档：https://skywalking.apache.org/docs/ 

## Java接入方案

Java Agent 参考文档：https://skywalking.apache.org/docs/skywalking-java/v9.4.0/en/setup/service-agent/java-agent/containerization/#kubernetes

接入Java程序，是需要一个java agent镜像注入到程序里面的。

### 怎么注入

有两种方法：

1. 直接把java agent injector的jar包放到应用程序的image里面。但是这样需要重新编译镜像，非常麻烦。
2. 加入一个initContainer，指定包含了java agent的jar包的image：
   1. 通过emptyDir作为sidecar数据共享
   2. 把jar包从initContainer拷贝到应用程序pod指定路径里面
   3. 应用程序pod直接指定一行JAVA_TOOL_OPTIONS参数指定java agent jar包路径即可完成注入。

~~~yaml
apiVersion: v1 
kind: Pod 
metadata: 
  name: agent-as-sidecar 
spec: 
  restartPolicy: Never 
  volumes: 
  - name: skywalking-agent 
    emptyDir: { } 
  initContainers: 
    - name: agent-container 
      image: apache/skywalking-java-agent:8.7.0-alpine 
      volumeMounts: 
        - name: skywalking-agent 
          mountPath: /agent 
      command: [ "/bin/sh" ] 
      args: [ "-c", "cp -R /skywalking/agent /agent/" ]
  containers: 
    - name: app-container 
      image: springio/gs-spring-boot-docker 
      volumeMounts: 
        - name: skywalking-agent 
          mountPath: /skywalking 
      env: 
        - name: JAVA_TOOL_OPTIONS 
          value: "-javaagent:/skywalking/agent/skywalking-agent.jar"
~~~

### 获取java agent镜像

去dockerhub直接搜`skywalking-java-agent`，找到最新版tag、以及对应的java版本，拉下来。

### 启动常用环境变量

- JAVA_TOOL_OPTIONS：指定JAVA的启动参数，加载agent可以通过该变量实现，比如-javaagent:/skywalking/agent/skywalking-agent.jar
- SW_AGENT_NAME：服务名称，建议格式<组名>::<逻辑名>，推荐配置为`命令空间::服务名称`
- SW_AGENT_INSTANCE_NAME：实例名称，通常用于表示同一个服务不同的示例，默认为UUID@hostname，推荐使用Pod名称作为实例名称
- SW_AGENT_COLLECTOR_BACKEND_SERVICES：Skywalking OAP svc地址

其他变量可以参考：https://skywalking.apache.org/docs/skywalking-java/v9.4.0/en/setup/service-agent/java-agent/configurations/

### 实战示例

接下来找一个测试服务，配置Agent并测试。首先对于服务的部署文件，需要添加如下内容：

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-handler-sw
  namespace: demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-handler
  template:
    metadata:
      labels:
        app: demo-handler
        version: v1
    spec: 
      volumes: 
      - name: skywalking-agent 
        emptyDir: {}
      # 注入agent的initContainer
      initContainers: 
      - name: agent-container 
        image: registry.cn-beijing.aliyuncs.com/dotbalo/skywalking-java-agent:9.4.0-java8 
        volumeMounts: 
        - name: skywalking-agent 
          mountPath: /agent 
        command: [ "/bin/sh" ] 
        args: [ "-c", "cp -R /skywalking/agent /agent/ ; mkdir -p /agent/agent/logs/ ; chown -R 1001.1001 /agent" ]
      # 主容器
      containers:
      - name: demo-handler
        image: registry.cn-beijing.aliyuncs.com/dotbalo/demo-handler:v0.0.1-upgrade 
        imagePullPolicy: IfNotPresent 
        env:
        - name: SPRING_PROFILES_ACTIVE
          value: k8supgrade
        - name: SERVER_PORT
          value: "8080"
        - name: JAVA_TOOL_OPTIONS 
          value: "-javaagent:/skywalking/agent/skywalking-agent.jar" 
        - name: NAMESPACE 
          valueFrom: 
            fieldRef: 
              fieldPath: metadata.namespace 
        - name: APP 
          valueFrom: 
            fieldRef: 
              fieldPath: metadata.labels['app'] 
        - name: SW_AGENT_NAME 
          value: $(NAMESPACE)::$(APP) 
        - name: SW_AGENT_INSTANCE_NAME 
          valueFrom: 
            fieldRef: 
              fieldPath: metadata.name 
        - name: SW_AGENT_COLLECTOR_BACKEND_SERVICES 
          value: skywalking-oap.skywalking.svc.cluster.local:11800 
        volumeMounts: 
        - name: skywalking-agent 
          mountPath: /skywalking
        livenessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 5
          successThreshold: 1
          tcpSocket:
            port: 8080
          timeoutSeconds: 2
        readinessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 5
          successThreshold: 1
          tcpSocket:
            port: 8080
          timeoutSeconds: 2
---
apiVersion: v1
kind: Service
metadata:
  name: handler
  namespace: demo
spec:
  selector:
    app: demo-handler
  ports:
  - name: http-web
    port: 80
    protocol: TCP
    targetPort: 8080
~~~

不论是什么样的java服务，都可以按照这个方式去注入java agent。

模拟请求：

~~~sh
curl 10.244.43.47:8080/api/generate
~~~

## Go接入方案

### 怎么注入

Go程序接入skywalking，也是两种方法：

1. 源码当中直接在main package里面导入一个包：`import _ "github.com/apache/skywalking-go"`（文档：[Setup in build | Apache SkyWalking](https://skywalking.apache.org/docs/skywalking-go/latest/en/setup/gobuild/#22-code-dependency)）

2. 不动源码，在镜像构建的时候用go agent的inject方法自动注入skywalking源码（文档：[Setup in docker | Apache SkyWalking](https://skywalking.apache.org/docs/skywalking-go/latest/en/setup/docker/)）

   ~~~sh
   # import the skywalking go base image 
   FROM apache/skywalking-go:<version>-go<go version> 
    
   # Copy application code 
   COPY /path/to/project /path/to/project 
   
   # Inject the agent into the project or get dependencies by application self 
   # skywalking-go-agent -inject会分析项目中的Go 源码文件，找到需要监控的目标函数或方法，并插入相应的探针代码，这些探针代码会在程序运行时捕获调用链信息、性能数据等，并将其发送到 SkyWalking 后端 
   RUN skywalking-go-agent -inject /path/to/project 
   
   # 通过 -toolexec，Go的编译器会在编译过程中应用SkyWalking的监控逻辑，生成包含监控功能的最终二进制文件 
   RUN go build -toolexec="skywalking-go-agent" -a /path/to/project 
   ~~~

### 获取go agent镜像

去dockerhub直接搜`skywalking-go`，找到最新版tag、以及对应的go版本，拉下来。

### 启动常用环境变量

- SW_AGENT_REPORTER_GRPC_BACKEND_SERVICE：Skywalking OAP 地址
- SW_AGENT_NAME：服务名称，建议格式<组名>::<逻辑名>，推荐配置为命令空间::服务名称
- SW_AGENT_INSTANCE_NAME：实例名称，通常用于表示同一个服务不同的示例，默认为UUID@hostname，推荐使用Pod名称作为实例名称

其它变量可以参考：

- https://skywalking.apache.org/docs/skywalking-go/v0.5.0/en/advanced-features/settings-override/

### 实战示例

下载测试程序：

~~~sh
git clone https://gitee.com/dukuan/demo-order.git 
~~~

在下载的git目录中创建Dockerfile：

~~~sh
FROM apache/skywalking-go:0.5.0-go1.22 AS builder 
COPY ./ /go/src/ 
WORKDIR /go/src/ 
#ENV GO111MODULE=on 
#ENV GOPROXY=https://goproxy.cn,direct 
RUN export GO111MODULE=on && \ 
    export GOPROXY=https://goproxy.cn,direct && \ 
    export CGO_ENABLED=0 && \
    export GOOS=linux && \
    skywalking-go-agent -inject /go/src && \ 
    go build -o ./order -toolexec="skywalking-go-agent" -a /go/src # 编译完在当前目录就会生成一个odrder的二进制文件

FROM alpine:3.20
COPY --from=builder /go/src/order . 
CMD [ "./order" ] 
~~~

编译程序：

~~~sh
docker build -t demo-order-sw:v1 . 
~~~

创建基础组件服务：

~~~sh
kubectl create -f mysql.yaml -f mysql-svc.yaml -n demo
~~~

配置数据库：

~~~sh
mysql> create database orders; 
mysql> CREATE USER 'order'@'%' IDENTIFIED BY 'password'; 
mysql> GRANT ALL ON orders.* TO 'order'@'%'; 
~~~

创建go程序（由于Go的代码在编译时已经插入探针，所以在启动时，不用特别指定配置，只需要保留相关的环境变量即可）

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-order-sw
  namespace: demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-order
  template:
    metadata:
      labels:
        app: demo-order
    spec:
      containers:
      - name: demo-order
        image: registry.cn-beijing.aliyuncs.com/dotbalo/demo-order:v2
        imagePullPolicy: IfNotPresent
        env:
        - name: MYSQL_HOST
          value: mysql
        - name: MYSQL_PORT
          value: "3306"
        - name: MYSQL_USER
          value: order
        - name: MYSQL_PASSWORD
          value: password
        - name: MYSQL_DB
          value: orders
        - name: NAMESPACE 
          valueFrom: 
            fieldRef: 
              fieldPath: metadata.namespace 
        - name: APP 
          valueFrom: 
            fieldRef: 
              fieldPath: metadata.labels['app'] 
        - name: SW_AGENT_NAME 
          value: $(NAMESPACE)::$(APP) 
        - name: SW_AGENT_INSTANCE_NAME 
          valueFrom: 
            fieldRef: 
              fieldPath: metadata.name 
        - name: SW_AGENT_REPORTER_GRPC_BACKEND_SERVICE 
          value: skywalking-oap.skywalking:11800 
        livenessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 5
          successThreshold: 1
          tcpSocket:
            port: 8080
          timeoutSeconds: 2
        readinessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 5
          successThreshold: 1
          tcpSocket:
            port: 8080
          timeoutSeconds: 2
~~~

模拟请求：

~~~sh
curl 172.16.85.206:8080/orders
~~~

skywalking UI中会看到自动加进去了“虚拟数据库”的界面，可以看到请求mysql的指标。这是skywalking可以动态发现数据库的功能。

# skywalking UI介绍

最常用的界面：常规服务 - 服务

- Service Apdex：应用的性能指数，0-1,。0.8表示80%的用户\请求是满意（成功）的。较低说明服务可能有问题
- Endpoint指标：每个接口级别的指标
- 下面的Service可以看每个服务组里面包含哪些微服务；Topology可以看到拓扑图；Trace可以看到每个接口请求过程中的span，如果某个span时间很长，代表可能有问题；log中如果有报错的时候会看到
- 在Service中点击某个微服务，可以看到这个微服务有多少个实例；点击某个示例进去可以看到更具体的指标，甚至可以看到JVM、Golang程序的堆栈、线程池等内部程序指标

# skywalking接入完整项目实战

skywalking接入项目，只和微服务采用什么语言开发有关系，和项目架构、项目设计没关系。哪个微服务需要接入skywalking，就直接在deployment中添加环境变量，或者go项目构建带agent的镜像等。

位于另一个ns内的微服务项目，都是通过skywalking的OAP server的svc来给skywalking推送数据的。

# skywalking告警通知

Skywalking支持针对采集的Metrics数据进行监控告警，可以在异常出现时发送告警。

Skywalking告警核心由一组规则实现，主要包含如下三个部分：

1. 指标Metrics：收集的关于Service、Instance、Endpoint的各种性能指标数据
2. 规则Rules：告警的触发规则，默认定义在config/alarm-settings.yml文件中，支持比较运算符和逻辑运算符等
3. 钩子Hooks：当告警被触发后，通过钩子来执行特定的操作，如发送通知等。

## 配置文件管理

默认是在oap pod中的`/skywalking/config/*`目录，但是在helm chart目录下的`files/config.d/oap/alarm-settings.yml`可以覆盖掉前者。所以直接把alarm-settings.yml文件放进`files/config.d/oap/alarm-settings.yml`，用helm管理即可。

~~~sh
# 首先创建oap目录
mkdir -p ./skywalking/files/conf.d/oap/
# 从容器中拿出默认的配置文件
kuebctl cp <oap pod name>:/skywalking/config/alarm-settings.yml ./skywalking/files/conf.d/oap/
# 在这个默认规则文件中继续添加内容即可
# helm管理
cd ./skywalking/
helm upgrade -i skywalking -n skywalking . -f values.yaml

# 更新完可以去pod里面看配置是否生效
cat /skywalking/config/alarm-settings.yml
~~~

## 告警规则

### 字段

告警规则由如下元素组成：（[Alerting Rules](https://skywalking.apache.org/docs/main/latest/en/setup/backend/backend-alarm/#rules)）

1. 规则名称，全局唯一，没有一个专门字段，在告警规则yaml中直接写上就行，下面都是子字段。必须以_rule结尾
2. expression：使用MOE（Metrics Query Expression）定义，表达式的结果必须是SINGLE_VALUE，且根操作必须是一个比较操作或者布尔操作，同时结果必须为1(true)或者0(false)，当结果为1(true)时，告警会触发
3. including-names：包含的instance名称，可以是Service、Instance、Endpoint等。列表类型。
4. exclude-names：排除的instance名称
5. period：周期，检查告警条件的时间窗口大小，分钟为单位
6. silence-period：静默期，某个告警被触发后，接下来的一段时间内，该告警不会被再次触发，不指定则默认和period一样
7. hooks：告警触发时绑定的钩子名称。名称格式为{hookType}.{hookName}（比如slack.custom1），并且必须在alarm-settings.yml文件的hooks部分定义。如果未指定钩子名称，则会使用全局钩子。
8. message：告警提示信息。

告警表达式计算规则：[Metrics Query Expression(MQE) Syntax | Apache SkyWalking](https://skywalking.apache.org/docs/main/latest/en/api/metrics-query-expression/)

### 默认规则

skywalking内置了如下的告警规则（在oap pod中的`/skywalking/config/alarm-settings.yml`里面）：

1. 服务在过去3分钟内平均响应时间超过1秒
2. 服务在过去两分钟内的成功率低于80%
3. 服务响应时间的百分位数在过去的3分钟内超过1秒
4. 服务实例在过去2分钟内的平均响应时间超过1秒
5. 端点在过去2分钟内的平均响应时间超过1秒
6. 数据库在过去2分钟内的平均响应时间超过1秒
7. 端点关系在过去2分钟内的平均响应时间超过1秒

### 规则表达式注意事项

注意：以这一条为例：服务在过去3分钟内平均响应时间超过1秒，他的告警规则写法是：

~~~sh
sum(service_resp_time > 1000) >= 3
~~~

这样写会和prometheus的写法不太一样，是因为prometheus是时序数据库，直接用avg(service_resp_time[3m]) >= 1000。但是skywalking不是这样。它使用一种滑动窗口的写法，具体解释看这里（[Alerting | Apache SkyWalking](https://skywalking.apache.org/docs/main/latest/en/setup/backend/backend-alarm/#rules)）。简单说就是想要看几分钟内的数据，>=后面就写几就行了。

## hooks

更多hook：[Hooks | Apache SkyWalking](https://skywalking.apache.org/docs/main/latest/en/setup/backend/backend-alarm/#hooks)

以钉钉为例：首先需要添加一个机器人，拿到加签的值、webhook的值

~~~yaml
# 添加钉钉告警 
hooks: 
  dingtalk: 
    default: 
      is-default: true 
      text-template: |- 
        { 
           "msgtype": "text", 
           "text": { 
             "content": "Apache SkyWalking Alarm: \n %s." 
           } 
         }
      webhooks: 
      - url: https://oapi.dingtalk.com/robot/send?access_token=xxx # webhook url
        secret: xxx # 加签的值
~~~

## 自定义告警规则

除了默认告警，还可以添加一些自定义告警。指标的名称可以去UI dashboard中找到想要的表，点击编辑就能看到对应的metrics名称，然后就能用来写监控规则。

比如想要监控Java服务JVM线程池是否阻塞，可以通过`instance_jvm_thread_blocked_state_thread_count`指标进行监控。

监控过去2分钟内JVM阻塞的线程数大于5：

~~~yaml
thread_block_rule: 
  expression: sum(instance_jvm_thread_blocked_state_thread_count > 5) >= 2 
  period: 5 # 检查过去5分钟的数据
  message: "服务 {name} 的线程池，在过去两分钟内被阻塞的数量超过5" 
  hooks: # 不写的话就走默认的hooks
  - dingtalk.default
~~~

如果规则写的语法有问题，oap pod会起不来。
