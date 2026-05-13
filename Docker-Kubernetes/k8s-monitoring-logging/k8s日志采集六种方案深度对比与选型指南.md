---
title: "Kubernetes 日志采集最佳实践：六种方案深度对比与生产选型指南"
source: "https://mp.weixin.qq.com/s/eOzdLWDVt_JU0ywK-PsWXQ"
created: 2026-05-13
tags:
  - kubernetes
  - logging
  - observability
---

> 你的 Pod 崩溃了，日志却消失了——这是 K8s 生产环境最令人抓狂的噩梦之一。

## 一、为什么日志采集在 K8s 中如此棘手？

在传统 VM 环境中，日志采集很简单：一台服务器，几个固定路径，Filebeat 一扫就搞定。但迁移到 Kubernetes 之后，事情变得复杂了：

- **Pod 是短暂的**：容器崩溃重启后，`/var/log/containers/` 中的日志文件会被截断甚至删除
- **动态调度**：同一个应用的 Pod 随时会漂移到不同 Node，传统 IP 绑定方案失效
- **日志路径不统一**：有的应用写标准输出，有的写文件，有的用 syslog
- **多租户混合**：一个节点上可能运行数十个不同团队的 Pod，日志需要隔离
- **高基数问题**：容器标签、命名空间、Pod 名称的组合爆炸，导致日志索引极度膨胀

---

## 二、K8s 日志的三种原生形式

### 2.1 容器标准输出/错误（stdout/stderr）

这是 K8s 最推荐的日志方式。容器运行时（containerd/Docker）会将 stdout/stderr 写入 Node 上的固定路径：

```
/var/log/pods/<namespace>_<pod-name>_<uid>/<container>/<n>.log
/var/log/containers/<pod-name>_<namespace>_<container>-<container-id>.log  # 软链接
```

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

```yaml
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
```

Fluent Bit ConfigMap 核心配置：

```ini
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
```

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

```yaml
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
```

**优点**：精确采集容器内文件日志，每个 Pod 独立配置灵活性强。

**缺点**：资源开销大（每 Pod 额外 50-200m CPU，64-256MB 内存），大规模集群管理复杂度呈线性增长。

**适用场景**：遗留应用日志写文件、无法改造 stdout 的场景。

---

### 方案三：应用直推（Direct Shipping）

应用通过 SDK 或 HTTP 直接将日志发送到日志后端，跳过中间采集层。

```python
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
```

**优点**：端到端延迟最低（毫秒级），可精确控制日志格式和结构化字段。

**缺点**：与业务代码强耦合，SDK 版本管理混乱，不适合多语言混合场景。

**适用场景**：单一技术栈、对日志延迟极敏感的场景（如金融交易审计日志）。

---

### 方案四：Istio/Service Mesh 访问日志

如果集群已部署 Service Mesh（Istio/Linkerd），Envoy Sidecar 可自动采集 HTTP 访问日志。

```yaml
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
```

**优点**：零代码改造，自动覆盖所有 HTTP/gRPC 流量，与链路追踪天然集成（TraceID 自动注入）。

**缺点**：仅覆盖网络访问日志，应用业务日志无法采集；依赖 Service Mesh。

---

### 方案五：OpenTelemetry 统一采集

OpenTelemetry Collector 同时处理 Metrics、Traces、Logs 三类信号，是 2025 年最热门的方案之一。

```yaml
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
```

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
| DaemonSet (Fluent Bit) | 低 | 低 | stdout | 全规模 | ⭐⭐⭐⭐⭐ |
| Sidecar 采集 | 高 | 中 | 文件+stdout | 小规模 | ⭐⭐⭐ |
| 应用直推 | 低 | 中 | 全量 | 小规模 | ⭐⭐ |
| Service Mesh 访问日志 | 中 | 高 | HTTP流量 | 中大规模 | ⭐⭐⭐ |
| OpenTelemetry Collector | 中 | 中 | 全量 | 全规模 | ⭐⭐⭐⭐⭐ |
| 云原生托管 | 低(运维)高(费用) | 极低 | 全量 | 全规模 | ⭐⭐⭐⭐ |

---

## 五、生产环境五大踩坑实录

### 坑一：Fluent Bit 内存溢出导致节点日志全量丢失

**现象**：Fluent Bit Pod 不断 OOMKilled。

**根因**：某个应用产生了大量异常日志（Error Storm），每秒输出 100MB+ 的 stack trace。

**解决方案**：

```ini
[INPUT]
    Name          tail
    Mem_Buf_Limit 100MB
    Skip_Long_Lines On

[SERVICE]
    storage.type         filesystem
    storage.path         /var/log/flb-storage/
    storage.backlog.mem_limit 100M
```

### 坑二：Pod 重启后丢失前一个容器的日志

**根因**：默认每容器只保留 5 个日志文件，每个最大 10MB。

**解决方案**：

```yaml
# /var/lib/kubelet/config.yaml
containerLogMaxFiles: 20
containerLogMaxSize: 50Mi
```

### 坑三：JSON 日志被双重序列化

**根因**：应用输出结构化 JSON，但 Fluent Bit 将整行作为字符串存储。

**解决方案**：

```ini
[FILTER]
    Name                kubernetes
    Merge_Log           On
    Merge_Log_Key       app_log
    Keep_Log            Off
```

### 坑四：高基数标签导致 Loki 查询超时

**根因**：Loki 不适合高基数标签，Pod IP、Request ID 等字段设为 Label 导致 Stream 爆炸。

**解决方案**：低基数字段做 Label（namespace/app/env），高基数字段做 `structured_metadata`，`labeldrop` 删除高基数 Label。

### 坑五：Sidecar 与 DaemonSet 双重采集

**根因**：Sidecar 转发到 stdout 后被 DaemonSet 再次采集。

**解决方案**：

```yaml
metadata:
  annotations:
    fluentbit.io/exclude: "true"
```

---

## 六、日志采集架构选型决策树

```
应用日志是否全部走 stdout？
├─ 是 → Fluent Bit DaemonSet
│   └─ 是否需要 Traces/Metrics 统一？
│       ├─ 是 → OpenTelemetry Collector
│       └─ 否 → Fluent Bit + Elasticsearch/Loki
└─ 否（部分写文件）→
    ├─ Pod 数量 < 50 → Sidecar 方案
    ├─ Pod 数量 > 50 → 应用改造为 stdout
    └─ 无法改造 → Sidecar + 注解排除 DaemonSet 重复采集
```

## 七、生产环境推荐架构

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

## 八、总结

| 场景 | 推荐方案 |
| --- | --- |
| 新建集群，追求现代化 | OpenTelemetry Collector |
| 快速落地，运维资源有限 | Fluent Bit + Loki |
| 公有云环境 | 云原生托管日志服务 |
| 遗留应用写文件日志 | Sidecar（小规模）/ 应用改造（大规模） |
| 已有 Istio | Service Mesh 访问日志 + DaemonSet 补充 |

三条生产实践黄金法则：

1. **应用日志尽量走 stdout**，减少采集复杂度
2. **结构化 JSON 日志**，让日志可机器解析、可搜索、可告警
3. **日志分级存储**：Error 永久保留 → Warn 保留 30 天 → Info 保留 7 天，控制成本
