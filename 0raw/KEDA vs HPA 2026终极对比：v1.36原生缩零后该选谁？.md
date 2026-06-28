---
title: "KEDA vs HPA 2026终极对比：v1.36原生缩零后该选谁？"
source: "https://mp.weixin.qq.com/s/rMLNgv3N9vqkOQ28-833RQ"
author:
  - "[[WAKEUP技术]]"
published:
created: 2026-06-28
description: "2026 年 4 月 22 日，Kubernetes v1.36 正式发布。在 70 项增强中，有一项看似不起眼、实则改变游戏规则的功能悄然进入 Beta 阶段：HPA Scale-to-Zero。"
tags:
  - "clippings"
---
WAKEUP技术 WAKE UP技术 *2026年6月9日 12:01*

2026 年 4 月 22 日，Kubernetes v1.36 正式发布。在 70 项增强中，有一项看似不起眼、实则改变游戏规则的功能悄然进入 Beta 阶段： **HPA Scale-to-Zero** 。

这个从 v1.16（2019年）就开始孵化、历经 7 年打磨的特性，终于在 v1.36 中默认启用。一时间，云原生社区炸开了锅——"HPA 能缩零了，KEDA 是不是要凉？"

真相远比「谁替代谁」的二元叙事复杂得多。本文将深入对比 KEDA 与 HPA 的架构差异、性能特性、适用场景，并给出 2026 年的生产选型决策框架。

---

## 一、HPA 的前世今生：从 CPU 到事件驱动

Kubernetes Horizontal Pod Autoscaler（HPA）是 K8s 内置的自动扩缩容组件。它的核心逻辑非常简单：

```
期望副本数 = ceil(当前指标值 / 目标阈值 × 当前副本数)
```

以 CPU 为例：如果当前 Pod 平均 CPU 使用率为 80%，目标阈值为 50%，HPA 就会将副本数翻倍。

### HPA 的三种指标类型

HPA v2 API（ `autoscaling/v2` ）支持三种指标源：

**1\. Resource Metrics（资源指标）**  
最常用的模式，基于 Pod 的 CPU/内存使用率。通过 Metrics Server 采集，15 秒轮询一次。

```
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**2\. Pod Metrics（Pod 级别自定义指标）**  
例如每个 Pod 的 QPS、活跃连接数。需要部署 Prometheus Adapter 等自定义指标适配器。

**3\. External Metrics（外部指标）**  
从集群外部获取指标，如云消息队列深度、第三方监控系统的数据。同样需要自定义指标适配器。

```
metrics:
- type: External
  external:
    metric:
      name: queue_messages_visible
      selector:
        matchLabels:
          queue: order-processing
    target:
      type: AverageValue
      averageValue: "100"
```

### HPA 的核心局限

在 v1.36 之前，HPA 有三大硬伤：

1. 1\. **不能缩零** ： `minReplicas` 最小为 1，空闲时至少保留一个 Pod，持续产生成本
2. 2\. **无原生外部事件源** ：对接 Kafka、RabbitMQ 等需要自建指标链路，配置复杂
3. 3\. **单一指标服务** ：整个集群只能有一个自定义指标 API 服务，多个适配器会冲突

---

## 二、KEDA：事件驱动的扩缩容专家

KEDA（Kubernetes Event-Driven Autoscaling）是 CNCF 毕业项目，定位为 HPA 的增强扩展，而非替代品。它提供两大核心能力：

### 架构解析

KEDA 由两个核心组件构成：

- • **keda-operator** ：控制器，负责管理 ScaledObject/TriggerAuthentication 等 CRD，协调扩缩容生命周期
- • **keda-metrics-apiserver** ：指标适配器，实现 Kubernetes External Metrics API，将外部事件源指标暴露给 HPA

工作流程如下：

```
外部事件源 → KEDA Scaler 轮询 → 转换为 HPA 指标 → HPA 调整副本数
               ↓（无事件时）
          缩容到 0，等待事件恢复
```

**关键设计：KEDA 不替换 HPA，而是为每个 ScaledObject 自动生成对应的 HPA 资源。** 缩放决策最终仍由 HPA 执行。

### ScaledObject 实战配置

以 Kafka 消费者为例：

```
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: order-consumer
spec:
  scaleTargetRef:
    name: order-consumer
  pollingInterval: 30
  cooldownPeriod: 300
  minReplicaCount: 0
  maxReplicaCount: 50
  triggers:
  - type: kafka
    metadata:
      bootstrapServers: kafka-broker:9092
      consumerGroup: order-processor
      topic: orders
      lagThreshold: "100"
      offsetResetPolicy: latest
```

KEDA 内置 **60+ 开箱即用的 Scaler** ，覆盖主流消息队列、数据库、云服务和定时任务：

| 类别 | 支持的事件源 |
| --- | --- |
| 消息队列 | Kafka、RabbitMQ、AWS SQS、Azure Service Bus、NATS、Redis Streams、GCP Pub/Sub |
| 数据库 | PostgreSQL、MySQL、MongoDB、Redis Lists |
| 云服务 | AWS CloudWatch、Azure Monitor、GCP Stackdriver |
| 定时任务 | Cron 触发器，支持时区配置 |
| 其他 | Prometheus、Datadog、New Relic |

### KEDA 2.16 新特性

2026 年 KEDA 发展至 2.16 版本，几个重要增强：

- • **GCP Secret Manager** 支持：TriggerAuthentication 可直接引用 GCP Secret Manager 中的凭证，无需手动管理 Kubernetes Secret
- • **ConfigMap TriggerAuthentication** ：触发器认证信息可从 ConfigMap 读取，简化配置管理
- • **NATS 2.10 集成优化** ：事件处理延迟降低 55%
- • **Redis 7.2 Streams 深度支持** ：支持 Consumer Group 级别扩缩容

---

## 三、v1.36 大新闻：HPA Scale-to-Zero

这是 2026 年 autoscaling 领域最大的变化。 `HPAScaleToZero` 特性门控在 v1.36 中默认启用，HPA 原生支持将 Deployment 缩容到 0 副本。

### 配置方式

```
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: batch-processor
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: batch-processor
  minReplicas: 0    # v1.36 原生支持
  maxReplicas: 20
  metrics:
  - type: External
    external:
      metric:
        name: queue.depth
      target:
        type: AverageValue
        averageValue: "10"
```

### 重要限制

HPA Scale-to-Zero 解决的是「能缩零」的问题，但 **仍需要外部指标源来通知 HPA 何时从 0 恢复到 1** 。KEDA 恰好可以作为这个外部指标源——你甚至可以同时使用 HPA Scale-to-Zero 和 KEDA。

### 另外一个好消息：External Metrics Fallback

v1.36 同时将 `HPAContainerMetrics` 之前的另一项增强拉入 Beta： **外部指标降级回退** 。当外部指标源不可用时（如 Prometheus 宕机、云 API 超时），HPA 会使用配置的回退值继续决策，而不是完全冻结扩缩容。

```
metrics:
- type: External
  external:
    metric:
      name: queue.depth
    target:
      type: AverageValue
      averageValue: "10"
  # v1.36 新增：指标不可用时的回退值
  describedObject:
    kind: Service
    name: queue-service
```

---

## 四、全方位对比矩阵

| 维度 | HPA（v1.36） | KEDA（2.16） |
| --- | --- | --- |
| **定位** | K8s 原生内置组件 | CNCF 项目，增强 HPA |
| **安装成本** | 零，内置即可用 | 需部署 Operator + CRD |
| **缩零支持** | ✅ Beta，默认启用 | ✅ 稳定，核心功能 |
| **事件源** | 需自定义指标适配器 | 内置 60+ Scaler，开箱即用 |
| **指标链路** | Metrics Server → Adapter → HPA | Scaler → Metrics API Server → HPA |
| **轮询间隔** | 默认 15 秒 | 默认 30 秒（可配） |
| **多事件源** | 不支持单 HPA 多外部指标类型 | 支持单 ScaledObject 多触发器 |
| **认证管理** | 依赖适配器自行处理 | TriggerAuthentication + 云 IAM |
| **冷启动延迟** | 取决于外部指标响应 + Pod 启动 | 取决于 pollingInterval + 事件源响应 + Pod 启动 |
| **调试难度** | 低， `kubectl describe hpa` | 中高，需排查 Operator 日志 + ScaledObject 状态 + HPA 状态 |
| **升级维护** | 随 K8s 版本升级 | 需手动升级 CRD + Operator |

---

## 五、生产环境选型决策树

### 场景一：标准 HTTP 服务

**选 HPA。**

你的服务是典型的 REST API，流量与 CPU/内存正相关。HPA 原生支持，零额外依赖，配置简单。

```
# 仅需这一个 YAML
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-server
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  minReplicas: 2
  maxReplicas: 20
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
```

### 场景二：消息队列消费者

**选 KEDA。**

KEDA 的杀手场景。无需搭建 Prometheus → Adapter → HPA 的复杂链路，直接对接消息队列即可。

```
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: kafka-consumer
spec:
  scaleTargetRef:
    name: kafka-consumer
  pollingInterval: 15        # 对齐 HPA 默认间隔
  cooldownPeriod: 300       # 缩容冷却 5 分钟
  minReplicaCount: 0         # 缩零
  maxReplicaCount: 100
  triggers:
  - type: kafka
    metadata:
      bootstrapServers: kafka-cluster:9092
      consumerGroup: order-group
      topic: orders
      lagThreshold: "50"
      activationLagThreshold: "5"  # 从 0 恢复的阈值
```

### 场景三：混合场景（HTTP + 事件驱动）

**HPA + KEDA 协同。**

同一个集群中，HTTP 服务用 HPA，队列消费者用 KEDA，两者互不冲突。KEDA 底层仍创建 HPA 资源，最终由 HPA 执行扩缩容。

特别提醒： **不要为同一个 Deployment 同时创建 HPA 和 KEDA ScaledObject** ，会导致副本数控制冲突。

### 场景四：多事件源混合触发

**选 KEDA。**

需要同时基于 Kafka 积压、Redis 队列长度、定时任务触发扩缩容？KEDA 的多触发器机制是唯一选择：

```
triggers:
- type: kafka
  metadata:
    bootstrapServers: kafka:9092
    consumerGroup: processor
    topic: events
    lagThreshold: "100"
- type: redis
  metadata:
    address: redis:6379
    listName: task-queue
    listLength: "50"
- type: cron
  metadata:
    timezone: Asia/Shanghai
    start: "30 8 * * 1-5"   # 工作日 8:30 预扩容
    end: "30 18 * * 1-5"    # 工作日 18:30 缩容
    desiredReplicas: "5"
```

### 场景五：测试/预发布环境

**选 v1.36 HPA Scale-to-Zero。**

如果集群已升级至 v1.36，测试环境可以直接使用原生 HPA 缩零，无需额外部署 KEDA。减少组件依赖，降低维护成本。

---

## 六、五大生产避坑指南

### 坑一：缩零后的冷启动延迟

**现象** ：消费者从 0 恢复到处理第一条消息，可能耗时 30-90 秒。

**原因** ：KEDA pollingInterval（30秒） + HPA 响应（15秒） + Pod 调度 + 镜像拉取 + 应用初始化。

**解决** ：

- • 对延迟敏感的服务，将 `minReplicaCount` 设为 1
- • 预构建镜像，使用镜像预热或本地缓存
- • 将 `pollingInterval` 调至 10-15 秒

### 坑二：认证配置复杂

**现象** ：KEDA 连接云服务事件源时报认证错误。

**解决** ：

- • AWS 环境：优先使用 IRSA（IAM Roles for Service Accounts）代替静态密钥
- • GCP 环境：使用 KEDA 2.16 新增的 GCP Secret Manager 集成
- • 本地密钥：通过 Kubernetes Secret + TriggerAuthentication 管理，定期轮转
```
apiVersion: keda.sh/v1alpha1
kind: TriggerAuthentication
metadata:
  name: keda-trigger-auth-aws
spec:
  podIdentity:
    provider: aws-eks        # 使用 IRSA，无静态密钥
```

### 坑三：HPA 指标不可用导致决策冻结

**现象** ：Prometheus 宕机后，HPA 既不放也不缩，集群规模僵死。

**解决** ：v1.36 使用 External Metrics Fallback 配置降级值：

```
metrics:
- type: External
  external:
    metric:
      name: prometheus_queue_depth
    target:
      type: AverageValue
      averageValue: "50"
  # 使用 fallback 需要额外的适配器支持
  # 或考虑 KEDA 内置的 Prometheus Scaler
```

### 坑四：多 HPA/KEDA 控制器冲突

**现象** ：副本数反复震荡，Deployment 状态异常。

**原因** ：为同一工作负载配置了多个扩缩容控制器（自定义 HPA + KEDA ScaledObject + CronJob 脚本）。

**解决** ：

- • 每个 Deployment 只用一个扩缩容控制器
- • KEDA 环境下删除手动创建的 HPA，由 KEDA 自动管理
- • 使用 `kubectl get hpa -A` 和 `kubectl get scaledobject -A` 检查冲突

### 坑五：KEDA 升级 CRD 不兼容

**现象** ：升级 KEDA 后 ScaledObject 报 schema 校验错误。

**原因** ：KEDA 小版本升级可能引入 CRD schema 变更，需要先更新 CRD 定义再升级 Operator。

**解决** ：

- • 升级前阅读 Release Notes 中的 "Upgrade Notes" 部分
- • 使用 Helm 升级时，指定 `--set crds.install=true`
- • 关键集群建议先在 staging 环境验证

---

## 七、监控告警配置

无论选 HPA 还是 KEDA，完备的监控是弹性伸缩的基石。

### Prometheus 告警规则

```
groups:
- name: autoscaling
  rules:
  # HPA 无法获取指标
  - alert: HPAMetricsUnavailable
    expr: |
      kube_hpa_status_condition{
        condition="AbleToScale",
        status="false"
      } == 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "HPA {{ $labels.hpa }} in {{ $labels.namespace }} cannot fetch metrics"

  # KEDA Scaler 错误
  - alert: KEDAScalerErrors
    expr: |
      sum(rate(keda_scaler_errors[5m])) by (scaledObject, scaler) > 0
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "KEDA Scaler {{ $labels.scaler }} has errors on {{ $labels.scaledObject }}"

  # HPA 接近上限
  - alert: HPANearMaxReplicas
    expr: |
      (kube_hpa_status_current_replicas / kube_hpa_spec_max_replicas) > 0.8
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "HPA {{ $labels.hpa }} at {{ $value | humanizePercentage }} of max replicas"
```

---

## 八、总结：KEDA 与 HPA 的未来

v1.36 的 HPA Scale-to-Zero 不是一个替代信号，而是一个 **互补信号** 。核心结论有三：

**1\. HPA 仍是标准 HTTP 服务的首选**

对于 CPU/内存驱动的 Web 服务，HPA 原生、简单、可靠。v1.36 的 Scale-to-Zero 让测试环境也有了缩零能力，减少额外依赖。

**2\. KEDA 在事件驱动领域不可替代**

60+ 内置 Scaler、多触发器融合、原生认证管理——这些是 HPA 短期内无法覆盖的能力。KEDA 仍是消息队列、定时任务、批处理场景的最佳选择。

**3\. 它们会继续共存并深化协同**

KEDA 底层依赖 HPA 执行缩放，HPA Scale-to-Zero 依赖外部指标源（如 KEDA）告知何时恢复。两者的关系是 **共生** ，而非竞争。

**一句话选型指南** ：

> HTTP 服务用 HPA，队列消费用 KEDA，混合场景两者协同，测试环境 v1.36 原生缩零。

---

*本文由「WAKE UP技术」原创发布，覆盖 KEDA 2.16 与 Kubernetes v1.36 最新特性。欢迎分享给正在纠结弹性伸缩方案的同事。*

**微信扫一扫赞赏作者**