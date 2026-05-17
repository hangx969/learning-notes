---
title: "K8s 日志管理：基础机制、六种采集方案与审计日志实战"
source:
  - "https://mp.weixin.qq.com/s/eOzdLWDVt_JU0ywK-PsWXQ"
  - "https://mp.weixin.qq.com/s/kvIaTMck_V1LpP848x4v7g"
created: 2026-05-17
tags:
  - kubernetes
  - logging
  - observability
  - audit
aliases:
  - K8s容器日志管理
---

# K8s 日志管理：基础机制、采集方案与审计日志

> 你的 Pod 崩溃了，日志却消失了——这是 K8s 生产环境最令人抓狂的噩梦之一。

在传统 VM 环境中，日志采集很简单：一台服务器，几个固定路径，Filebeat 一扫就搞定。但迁移到 Kubernetes 之后，事情变得复杂了：

- **Pod 是短暂的**：容器崩溃重启后，`/var/log/containers/` 中的日志文件会被截断甚至删除
- **动态调度**：同一个应用的 Pod 随时会漂移到不同 Node，传统 IP 绑定方案失效
- **日志路径不统一**：有的应用写标准输出，有的写文件，有的用 syslog
- **多租户混合**：一个节点上可能运行数十个不同团队的 Pod，日志需要隔离
- **高基数问题**：容器标签、命名空间、Pod 名称的组合爆炸，导致日志索引极度膨胀

---

## 一、K8s 日志基础机制

Kubernetes 容器日志的保存时长并非固定值，而是由**节点本地默认策略**、**日志输出方式**和**持久化方案**共同决定。

### 1.1 节点本地默认日志保存机制——kubelet 管控

K8s 集群中，容器标准输出（stdout/stderr）的日志默认由 kubelet 负责管理，遵循**大小 + 文件数**双重限制策略，而非基于固定时间周期。

#### 核心限制参数（默认值）

打开 kubelet 配置：`/var/lib/kubelet/config.yaml`

- `containerLogMaxFiles: 5`，每个容器最多保留 **5 个**日志文件（含当前活跃文件）
- `containerLogMaxSize: 10Mi`，单个日志文件最大 **10MiB**（达到即触发轮转）

计算：每个容器默认最多占用约 **50MiB** 存储（10MiB x 5 个文件）

#### 自定义 kubelet 配置

通过修改 kubelet 配置可调整默认限制，适用于需要保留更多本地日志的场景。修改 kubelet 配置文件，如：

~~~yaml
containerLogMaxSize: "20Mi"  # 单个文件最大20MiB
containerLogMaxFiles: 10     # 最多保留10个文件
~~~

重启 kubelet 服务使配置生效：`systemctl restart kubelet`

注意：此配置仅影响**新创建**的容器，不作用于存量容器。

### 1.2 日志存储路径

- **Docker 运行时**：`/var/lib/docker/containers/$CONTAINER_ID/$CONTAINER_ID-json.log`，并在 `/var/log/pods` 和 `/var/log/containers` 建立软链接
- **Containerd 运行时**：日志由 kubelet 直接落盘，保存至 `/var/log/pods/<pod_uid>/<container_name>/0.log` 等路径

### 1.3 容器日志生命周期

- 容器删除时，关联日志文件**同步删除**，kubelet 不会保留已删除容器的日志
- 日志轮转仅基于文件大小，**无默认时间限制**，高频日志可能数小时内就完成轮转覆盖，低频日志可能保存数天甚至更久

### 1.4 容器运行时差异

- **Docker**：日志驱动（默认 json-file）独立配置，可能覆盖 kubelet 限制（生产环境不推荐）
- **Containerd**：日志管理完全由 kubelet 控制，配置更统一稳定

### 1.5 日志输出方式对保存时长的影响

| 输出方式 | 保存机制 | 保存时长特点 |
|---|---|---|
| 标准输出 (stdout) | kubelet 统一管控 | 遵循默认 50MiB 限制，容器删除即删除 |
| 容器内文件 | 应用 / sidecar（如 filebeat）自行管理 | 无 kubelet 限制，易导致磁盘溢出。需结合程序自行切割日志文件大小以及保留文件的份数。|
| HostPath 挂载 | 宿主机文件系统 | 脱离容器生命周期，需手动清理 / 配置 logrotate |

`logrotate` 是 Linux/Unix 系统自带的**标准日志管理工具**，核心作用是自动管理日志文件，解决日志文件无限膨胀、占用磁盘空间、难以维护的问题。

### 1.6 持久化日志保存

节点本地日志仅作临时缓存，生产环境必须部署**集中式日志系统**实现长期保存，常见方案及保存策略如下：

- ELK/EFK 等开源方案
- Datadog 等商业平台
- 云厂商托管等

---

## 二、K8s 日志的三种原生形式

### 2.1 容器标准输出/错误（stdout/stderr）

这是 K8s 最推荐的日志方式。容器运行时（containerd/Docker）会将 stdout/stderr 写入 Node 上的固定路径：

~~~
/var/log/pods/<namespace>_<pod-name>_<uid>/<container>/<n>.log
/var/log/containers/<pod-name>_<namespace>_<container>-<container-id>.log  # 软链接
~~~

`kubectl logs` 命令本质上就是读取这些文件。

**关键问题**：Pod 被删除后，这些文件同样被清理。

### 2.2 容器内日志文件

应用将日志写到容器内的某个路径（如 `/app/logs/app.log`），不经过 stdout。这类日志对 Kubelet 完全不可见，只能通过 Sidecar 或 Volume 挂载方式采集。

### 2.3 节点系统日志

来自 kubelet、containerd、systemd 等组件的日志，通过 `journald` 或 `/var/log/syslog` 暴露，通常作为集群运维日志单独处理。

---

## 三、六种日志采集方案深度对比

### 方案一：节点级 DaemonSet（Node Agent）

**代表工具**：Fluent Bit、Fluentd、Filebeat、Vector

这是最主流的生产方案。在每个 Node 上部署一个日志采集 Agent（以 DaemonSet 形式），挂载 Node 的 `/var/log` 目录，批量采集所有容器的 stdout 日志。

~~~yaml
# fluent-bit DaemonSet 核心配置
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
  namespace: logging
spec:
  selector:
    matchLabels:
      app: fluent-bit
  template:
    spec:
      serviceAccountName: fluent-bit
      tolerations:
        - key: node-role.kubernetes.io/control-plane
          effect: NoSchedule
      containers:
        - name: fluent-bit
          image: fluent/fluent-bit:3.2
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          volumeMounts:
            - name: varlog
              mountPath: /var/log
              readOnly: true
            - name: varlibdockercontainers
              mountPath: /var/lib/docker/containers
              readOnly: true
            - name: config
              mountPath: /fluent-bit/etc/
      volumes:
        - name: varlog
          hostPath:
            path: /var/log
        - name: varlibdockercontainers
          hostPath:
            path: /var/lib/docker/containers
        - name: config
          configMap:
            name: fluent-bit-config
~~~

Fluent Bit ConfigMap 核心配置：

~~~ini
[INPUT]
    Name              tail
    Tag               kube.*
    Path              /var/log/containers/*.log
    Parser            cri
    DB                /var/log/flb_kube.db
    Mem_Buf_Limit     50MB
    Skip_Long_Lines   On
    Refresh_Interval  10

[FILTER]
    Name                kubernetes
    Match               kube.*
    Kube_URL            https://kubernetes.default.svc:443
    Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token
    Kube_Tag_Prefix     kube.var.log.containers.
    Merge_Log           On
    Keep_Log            Off
    K8S-Logging.Parser  On
    K8S-Logging.Exclude On
    Labels              On
    Annotations         Off

[OUTPUT]
    Name            es
    Match           kube.*
    Host            elasticsearch-master
    Port            9200
    Index           k8s-logs
    Logstash_Format On
    Logstash_Prefix k8s
    Replace_Dots    On
    Retry_Limit     False
    tls             On
    tls.verify      Off
~~~

**优点**：
- 资源开销低，每节点一个 Agent，对业务 Pod 零侵入
- Fluent Bit 单核可处理 **200MB/s** 以上的日志流
- 自动附加 K8s 元数据（Pod、Namespace、Label）

**缺点**：
- 只能采集 stdout/stderr，容器内文件日志无法采集
- 节点故障时，Agent 随之宕机，存在采集丢失风险

**适用场景**：95% 的生产场景首选，应用日志统一走 stdout。

---

### 方案二：Sidecar 容器方案

当应用无法改造为 stdout 输出时，在同一个 Pod 中注入一个日志采集 Sidecar，共享 Volume 读取文件日志。

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-with-sidecar
spec:
  template:
    spec:
      containers:
        - name: app
          image: my-app:v1.0
          volumeMounts:
            - name: app-logs
              mountPath: /app/logs
        - name: log-collector
          image: fluent/fluent-bit:3.2
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 200m
              memory: 128Mi
          volumeMounts:
            - name: app-logs
              mountPath: /app/logs
              readOnly: true
            - name: fluent-bit-config
              mountPath: /fluent-bit/etc/
          env:
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
      volumes:
        - name: app-logs
          emptyDir: {}
        - name: fluent-bit-config
          configMap:
            name: sidecar-fluent-bit-config
~~~

**优点**：精确采集容器内文件日志，每个 Pod 独立配置灵活性强。

**缺点**：资源开销大（每 Pod 额外 50-200m CPU，64-256MB 内存），大规模集群管理复杂度呈线性增长。

**适用场景**：遗留应用日志写文件、无法改造 stdout 的场景。

---

### 方案三：应用直推（Direct Shipping）

应用通过 SDK 或 HTTP 直接将日志发送到日志后端，跳过中间采集层。

~~~python
# Python 示例：直接推送到 Loki
import logging
from logging_loki import LokiHandler

handler = LokiHandler(
    url="http://loki:3100/loki/api/v1/push",
    tags={"app": "my-service", "env": "prod"},
    auth=("admin", "password"),
    version="1",
)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.info("User login", extra={"user_id": "12345"})
~~~

**优点**：端到端延迟最低（毫秒级），可精确控制日志格式和结构化字段。

**缺点**：与业务代码强耦合，SDK 版本管理混乱，不适合多语言混合场景。

**适用场景**：单一技术栈、对日志延迟极敏感的场景（如金融交易审计日志）。

---

### 方案四：Istio/Service Mesh 访问日志

如果集群已部署 Service Mesh（Istio/Linkerd），Envoy Sidecar 可自动采集 HTTP 访问日志。

~~~yaml
# Istio 启用访问日志
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: mesh-logging
  namespace: istio-system
spec:
  accessLogging:
    - providers:
        - name: envoy
      disabled: false
~~~

**优点**：零代码改造，自动覆盖所有 HTTP/gRPC 流量，与链路追踪天然集成（TraceID 自动注入）。

**缺点**：仅覆盖网络访问日志，应用业务日志无法采集；依赖 Service Mesh。

---

### 方案五：OpenTelemetry 统一采集

OpenTelemetry Collector 同时处理 Metrics、Traces、Logs 三类信号，是 2025 年最热门的方案之一。

~~~yaml
# OpenTelemetry Collector 配置核心片段
receivers:
  filelog:
    include:
      - /var/log/pods/*/*/*.log
    operators:
      - type: regex_parser
        id: parser-containerd
        regex: '^(?P<time>[^ ^Z]+Z) (?P<stream>stdout|stderr) (?P<logtag>[^ ]*) ?(?P<log>.*)$'
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:
    send_batch_size: 10000
    timeout: 5s
  k8sattributes:
    auth_type: serviceAccount
    extract:
      metadata:
        - k8s.pod.name
        - k8s.deployment.name
        - k8s.namespace.name
        - k8s.node.name

exporters:
  loki:
    endpoint: http://loki:3100/loki/api/v1/push
  elasticsearch:
    endpoint: https://elasticsearch:9200

service:
  pipelines:
    logs:
      receivers: [filelog, otlp]
      processors: [batch, k8sattributes]
      exporters: [loki]
~~~

**优点**：Logs/Metrics/Traces 三合一；厂商中立，支持 50+ 输出端；CNCF 社区活跃，是未来技术标准。

**缺点**：配置较复杂，学习曲线陡；部分 Receiver 尚在迭代中。

**适用场景**：新建集群或全面可观测性改造首选。

---

### 方案六：云原生日志服务（托管方案）

| 云厂商 | 产品 | 特点 |
| --- | --- | --- |
| AWS | CloudWatch Container Insights / FireLens | 与 EKS 深度集成 |
| 阿里云 | 日志服务 SLS + logtail | 支持 ACK 一键接入 |
| 腾讯云 | CLS + 日志采集 Agent | 与 TKE 深度集成 |
| GCP | Cloud Logging + GKE | 原生集成，零配置 |

优势是零运维，但长期成本可能高于自建，且存在厂商锁定风险。

---

## 四、六种方案对比总览

| 方案 | 资源开销 | 运维复杂度 | 功能覆盖 | 适用规模 | 推荐指数 |
| --- | --- | --- | --- | --- | --- |
| DaemonSet (Fluent Bit) | 低 | 低 | stdout | 全规模 | ★★★★★ |
| Sidecar 采集 | 高 | 中 | 文件+stdout | 小规模 | ★★★ |
| 应用直推 | 低 | 中 | 全量 | 小规模 | ★★ |
| Service Mesh 访问日志 | 中 | 高 | HTTP流量 | 中大规模 | ★★★ |
| OpenTelemetry Collector | 中 | 中 | 全量 | 全规模 | ★★★★★ |
| 云原生托管 | 低(运维)高(费用) | 极低 | 全量 | 全规模 | ★★★★ |

---

## 五、生产环境五大踩坑实录

### 坑一：Fluent Bit 内存溢出导致节点日志全量丢失

**现象**：Fluent Bit Pod 不断 OOMKilled。

**根因**：某个应用产生了大量异常日志（Error Storm），每秒输出 100MB+ 的 stack trace。

**解决方案**：

~~~ini
[INPUT]
    Name          tail
    Mem_Buf_Limit 100MB
    Skip_Long_Lines On

[SERVICE]
    storage.type         filesystem
    storage.path         /var/log/flb-storage/
    storage.backlog.mem_limit 100M
~~~

### 坑二：Pod 重启后丢失前一个容器的日志

**根因**：默认每容器只保留 5 个日志文件，每个最大 10MB。

**解决方案**：

~~~yaml
# /var/lib/kubelet/config.yaml
containerLogMaxFiles: 20
containerLogMaxSize: 50Mi
~~~

### 坑三：JSON 日志被双重序列化

**根因**：应用输出结构化 JSON，但 Fluent Bit 将整行作为字符串存储。

**解决方案**：

~~~ini
[FILTER]
    Name                kubernetes
    Merge_Log           On
    Merge_Log_Key       app_log
    Keep_Log            Off
~~~

### 坑四：高基数标签导致 Loki 查询超时

**根因**：Loki 不适合高基数标签，Pod IP、Request ID 等字段设为 Label 导致 Stream 爆炸。

**解决方案**：低基数字段做 Label（namespace/app/env），高基数字段做 `structured_metadata`，`labeldrop` 删除高基数 Label。

### 坑五：Sidecar 与 DaemonSet 双重采集

**根因**：Sidecar 转发到 stdout 后被 DaemonSet 再次采集。

**解决方案**：

~~~yaml
metadata:
  annotations:
    fluentbit.io/exclude: "true"
~~~

---

## 六、日志采集选型决策树与推荐架构

### 6.1 选型决策树

~~~
应用日志是否全部走 stdout？
├─ 是 → Fluent Bit DaemonSet
│   └─ 是否需要 Traces/Metrics 统一？
│       ├─ 是 → OpenTelemetry Collector
│       └─ 否 → Fluent Bit + Elasticsearch/Loki
└─ 否（部分写文件）→
    ├─ Pod 数量 < 50 → Sidecar 方案
    ├─ Pod 数量 > 50 → 应用改造为 stdout
    └─ 无法改造 → Sidecar + 注解排除 DaemonSet 重复采集
~~~

### 6.2 生产环境推荐架构

**中小规模集群（< 100 节点）：PLG Stack**
- 采集层：Fluent Bit DaemonSet（< 50MB/节点）
- 存储层：Grafana Loki（成本比 ES 低 80%）
- 展示层：Grafana

**大规模集群（> 100 节点）：EFK + Kafka 缓冲**
- 采集层：Fluent Bit DaemonSet
- 缓冲层：Kafka（削峰）
- 存储层：Elasticsearch
- 展示层：Kibana

**面向未来：OpenTelemetry + 多后端**
- 采集层：OTel Collector DaemonSet
- 路由层：OTel Collector Gateway
- 存储层：Loki（日志）+ Prometheus（指标）+ Tempo（链路）
- 展示层：Grafana

---

## 七、K8s 审计日志

### 7.1 审计日志是什么？

K8s 审计日志是 API Server 的**访客登记簿**。每一个对 API Server 的请求（kubectl、Controller、Scheduler、外部调用），都会被记录下来。

一条审计日志记录了一个 API 请求的完整生命周期：

~~~json
{
  "kind": "Event",
  "apiVersion": "audit.k8s.io/v1",
  "level": "RequestResponse",
  "auditID": "aBcDeFgHi",
  "stage": "ResponseComplete",
  "requestURI": "/api/v1/namespaces/prod/pods/order-service-6d8f9",
  "verb": "delete",
  "user": {
    "username": "zhangsan",
    "groups": ["system:authenticated"]
  },
  "sourceIPs": ["10.0.1.15"],
  "objectRef": {
    "resource": "pods",
    "namespace": "prod",
    "name": "order-service-6d8f9"
  },
  "responseStatus": {
    "code": 200
  },
  "requestObject": {},
  "responseObject": {},
  "timestamp": "2026-05-12T03:15:22Z"
}
~~~

**这条记录回答的问题**：

- 谁？（username: zhangsan）
- 从哪来？（sourceIPs: 10.0.1.15）
- 做了什么？（verb: delete）
- 对什么资源？（objectRef: pods/prod/order-service-6d8f9）
- 结果如何？（responseStatus: 200）
- 什么时候？（timestamp）

### 7.2 审计策略配置实战

K8s 审计需要通过**审计策略文件（Audit Policy）**来配置——定义哪些事件需要记录、记录到什么详细程度。

~~~yaml
# /etc/kubernetes/audit-policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
# 默认规则：不记录
omitStages:
  - "RequestReceived"

rules:
  # 1. 在命名空间 default 中，不记录对 Pod 的请求
  - level: None
    namespaces: ["default"]
    resources:
      - group: ""
        resources: ["pods"]

  # 2. 记录对 Secret 和 ConfigMap 的所有请求（安全敏感）
  - level: RequestResponse
    resources:
      - group: ""
        resources: ["secrets", "configmaps"]

  # 3. 记录对 RBAC 相关资源的修改操作
  - level: RequestResponse
    verbs: ["create", "update", "patch", "delete"]
    resources:
      - group: "rbac.authorization.k8s.io"
        resources: ["*"]

  # 4. 记录生产命名空间的所有写操作
  - level: RequestResponse
    verbs: ["create", "update", "patch", "delete"]
    namespaces: ["prod", "prod-chn", "prodfeu-chn"]

  # 5. 健康检查等只读请求，只记录元数据
  - level: Metadata
    verbs: ["get", "list", "watch"]

  # 6. 节点（Node）相关操作，记录请求体
  - level: Request
    resources:
      - group: ""
        resources: ["nodes"]

  # 7. 默认规则：只读操记录元数据，写操作记录完整信息
  - level: Metadata
    verbs: ["get", "list", "watch"]
  - level: RequestResponse
~~~

**审计级别（Level）说明**：

| Level | 记录内容 | 适用场景 |
| --- | --- | --- |
| `None` | 不记录 | 高频只读操作（如健康检查） |
| `Metadata` | 只记录请求元数据（谁、什么资源、什么操作） | 只读查询 |
| `Request` | 记录元数据 + 请求体 | 敏感资源查询 |
| `RequestResponse` | 记录元数据 + 请求体 + 响应体 | 写操作、安全审计 |

### 7.3 在 API Server 中启用审计

修改 kube-apiserver 的启动参数（静态 Pod 方式）：

~~~yaml
# /etc/kubernetes/manifests/kube-apiserver.yaml
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: kube-apiserver
      command:
        - kube-apiserver
        # 审计策略文件
        - --audit-policy-file=/etc/kubernetes/audit-policy.yaml
        # 审计日志输出文件
        - --audit-log-path=/var/log/kubernetes/audit/audit.log
        # 日志文件最大大小（MB）
        - --audit-log-maxsize=100
        # 保留的旧日志文件数量
        - --audit-log-maxbackup=10
        # 保留的天数
        - --audit-log-maxage=30
        # （可选）输出到webhook
        - --audit-webhook-config-file=/etc/kubernetes/audit-webhook.yaml
~~~

**重要提醒**：audit.log 文件会快速增长，必须配置日志轮转！

~~~ini
# /etc/logrotate.d/k8s-audit
/var/log/kubernetes/audit/audit.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 root root
    postrotate
        systemctl reload kubelet
    endscript
}
~~~

### 7.4 审计日志采集与存储架构

生产环境不会直接读取 audit.log 文件——需要集中式采集和分析。

~~~
K8s API Server
    │
    ├── 输出到文件（audit.log）
    │       └── Fluent Bit / Filebeat 采集
    │               └── Elasticsearch / Loki
    │                       └── Kibana / Grafana（可视化查询）
    │
    └── 输出到 Webhook（实时）
            └── 审计专用后端（如 Falco、自研系统）
~~~

**使用 Fluent Bit 采集审计日志**：

~~~ini
# /etc/fluent-bit/conf.d/k8s-audit.conf
[INPUT]
    Name tail
    Path /var/log/kubernetes/audit/audit.log
    Parser k8s-audit
    Tag k8s.audit
    Refresh_Interval 5
    Mem_Buf_Limit 50MB

[OUTPUT]
    Name es
    Match k8s.audit
    Host elasticsearch.logging.svc
    Port 9200
    Index k8s-audit-logs
~~~

**审计日志的 JSON 解析器**：

~~~ini
# /etc/fluent-bit/parsers.conf
[PARSER]
    Name k8s-audit
    Format json
    Time_Key timestamp
    Time_Format %Y-%m-%dT%H:%M:%SZ
~~~

### 7.5 典型排查场景

**场景 1：追踪"谁删了我的资源"**

~~~bash
# 在audit.log中搜索删除操作
grep '"verb":"delete"' /var/log/kubernetes/audit/audit.log | \
  jq 'select(.objectRef.name=="order-service-6d8f9") | 
       {time: .timestamp, user: .user.username, ip: .sourceIPs[0], verb: .verb, resource: .objectRef}'
~~~

**场景 2：发现异常高频 API 调用（可能是攻击或 Bug）**

~~~bash
# 统计每个用户的API调用次数
cat /var/log/kubernetes/audit/audit.log | \
  jq -r '.user.username + " " + .verb + " " + .requestURI' | \
  sort | uniq -c | sort -rn | head -20
~~~

**场景 3：检测匿名访问**

~~~bash
# 查找system:anonymous用户的操作
grep '"username":"system:anonymous"' /var/log/kubernetes/audit/audit.log
~~~

**场景 4：Grafana 可视化——监控异常操作**

~~~promql
# Prometheus + Grafana告警规则
groups:
  - name: k8s_audit_alerts
    rules:
      - alert: AnonymousAccessDetected
        expr: |
          sum(rate(k8s_audit_events_total{user="system:anonymous"}[5m])) > 0
        labels:
          severity: critical
        annotations:
          summary: "检测到匿名用户访问K8s API"
~~~

---

## 八、审计日志合规与安全

### 8.1 合规视角：等保 2.0 与 SOC2 的要求

**等保 2.0（中国网络安全等级保护）** 对云计算平台的要求：

- 必须记录用户操作日志，保留至少 6 个月
- 日志必须不可篡改
- 必须能追踪到具体操作人

**SOC2 Type II** 对审计的要求：

- 所有对生产环境的变更必须有审计记录
- 审计日志必须定期审查
- 异常操作必须能触发告警

**K8s 审计日志直接满足上述要求**，但需要配合：

1. **不可篡改存储**：将审计日志发送至 WORM（一次写入多次读取）存储，如 S3 Object Lock
2. **定期审计**：每月导出敏感操作（RBAC 变更、Secret 访问、生产资源删除）并人工审查
3. **实时告警**：对接 SIEM 系统（如 Splunk、ELK Watcher）

~~~json
// Elasticsearch Watcher示例：告警敏感操作
{
  "trigger": {
    "schedule": { "interval": "1m" }
  },
  "input": {
    "search": {
      "request": {
        "indices": ["k8s-audit-logs"],
        "body": {
          "query": {
            "bool": {
              "must": [
                { "terms": { "verb": ["create", "update", "patch", "delete"] } },
                { "terms": { "objectRef.resource": ["secrets", "configmaps", "roles", "rolebindings"] } },
                { "range": { "@timestamp": { "gte": "now-1m" } } }
              ]
            }
          }
        }
      }
    }
  },
  "condition": { "compare": { "ctx.payload.hits.total": { "gt": 0 } } },
  "actions": { "send_email": { "email": { "to": ["sre@company.com"] } } }
}
~~~

### 8.2 性能优化：审计日志不是免费午餐

全量记录 `RequestResponse` 级别会产生显著的性能开销（序列化、磁盘 IO、网络传输）。

**优化策略 1：分级记录**

~~~yaml
# 对核心命名空间使用RequestResponse，其余使用Metadata
rules:
  - level: RequestResponse
    namespaces: ["prod", "prod-chn"]
  - level: Metadata
    namespaces: ["staging", "dev"]
  - level: None
    namespaces: ["kube-system"]  # kube-system内部通信量大，酌情过滤
~~~

**优化策略 2：采样**

~~~yaml
# 对只读操作采样10%
rules:
  - level: Metadata
    verbs: ["get", "list", "watch"]
    omitStages:
      - "ResponseComplete"
    # 注意：原生K8s审计策略不支持采样
    # 如需采样，可通过webhook后端实现
~~~

**优化策略 3：使用 Webhook 异步处理**

~~~yaml
# kube-apiserver配置：输出到webhook（非阻塞）
- --audit-webhook-config-file=/etc/kubernetes/audit-webhook.yaml
- --audit-webhook-mode=batch  # 批量发送，减少API Server阻塞
~~~

### 8.3 与 Open Policy Agent（OPA）联动

审计日志是"事后追溯"，OPA 是"事前拦截"。两者结合，形成完整的 K8s 安全闭环。

~~~yaml
# OPA Gatekeeper策略示例：禁止在prod命名空间创建LoadBalancer类型Service
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sNoLoadBalancerInProd
metadata:
  name: no-lb-in-prod
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Service"]
    namespaces: ["prod", "prod-chn"]
  parameters:
    prohibitedType: "LoadBalancer"
~~~

当 OPA 拦截请求时，K8s 仍会记录审计日志（verb: create，status: 403），形成完整的"拦截+记录"链条。

### 8.4 快速启用 K8s 审计日志

~~~bash
# 1. 创建审计策略文件
cat > /etc/kubernetes/audit-policy.yaml <<EOF
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  - level: Metadata
EOF

# 2. 修改kube-apiserver配置
# 添加 --audit-policy-file 和 --audit-log-path 参数

# 3. 重启kubelet使配置生效
systemctl restart kubelet

# 4. 验证审计日志
tail -f /var/log/kubernetes/audit/audit.log | jq .
~~~

---

## 九、总结

### 日志采集选型速查

| 场景 | 推荐方案 |
| --- | --- |
| 新建集群，追求现代化 | OpenTelemetry Collector |
| 快速落地，运维资源有限 | Fluent Bit + Loki |
| 公有云环境 | 云原生托管日志服务 |
| 遗留应用写文件日志 | Sidecar（小规模）/ 应用改造（大规模） |
| 已有 Istio | Service Mesh 访问日志 + DaemonSet 补充 |
| 安全审计与合规 | API Server 审计日志 + SIEM 集成 |

### 生产实践黄金法则

1. **应用日志尽量走 stdout**，减少采集复杂度
2. **结构化 JSON 日志**，让日志可机器解析、可搜索、可告警
3. **日志分级存储**：Error 永久保留 -> Warn 保留 30 天 -> Info 保留 7 天，控制成本
4. **启用审计日志**：配置只需 30 分钟，但它给你的是面对生产事故时"有据可查"的从容
5. **审计 + OPA 联动**：事前拦截 + 事后追溯，形成完整安全闭环
