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
helm pull skywalking/skywalking --version 4.7.0
~~~

## 配置

更改ES配置：

~~~yaml
elasticsearch: 
  antiAffinity: soft 
  clusterName: es-cluster 
  enabled: true 
  esMajorVersion: "7" 
  persistence: 
    annotations: {} 
    enabled: true 
  replicas: 3 
  resources: 
    limits: 
      cpu: 2000m 
      memory: 3Gi 
    requests: 
      cpu: 100m 
      memory: 2Gi 
  volumeClaimTemplate: 
    storageClassName: cfs-sc # 用cubeFS
    accessModes: 
    - ReadWriteOnce
    resources: 
      requests: 
        storage: 5Gi 
~~~

更改OAP资源配置：

~~~yaml
oap: 
  image: 
    pullPolicy: IfNotPresent 
    repository: registry.cn-beijing.aliyuncs.com/dotbalo/skywalking-oap-server 
    tag: 10.2.0 # ？根据最新的更改
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
~~~

更改UI设置：

~~~yaml
ui: 
  image: 
    pullPolicy: IfNotPresent 
    repository: registry.cn-beijing.aliyuncs.com/dotbalo/skywalking-ui 
    tag: 10.2.0 # ？根据最新的更改
  replicas: 1 
  service: 
    annotations: {} 
    externalPort: 80 
    internalPort: 8080 
    type: NodePort 
~~~

## 安装

~~~sh
helm upgrade -i skywalking -n skywalking . --create-namespace -f values.yaml
~~~

通过NodePort访问skywalking UI

