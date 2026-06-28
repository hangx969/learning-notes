---
title: "KEDA vs HPA 2026 终极对比：v1.36 原生缩零后该选谁？"
source: "https://mp.weixin.qq.com/s/rMLNgv3N9vqkOQ28-833RQ"
created: 2026-06-28
tags:
  - kubernetes
  - keda
  - hpa
  - autoscaling
  - scale-to-zero
---

# KEDA vs HPA 2026 终极对比

> 2026 年 4 月 22 日，Kubernetes v1.36 正式发布。HPA Scale-to-Zero 特性进入 Beta 默认启用。社区炸开了锅——"HPA 能缩零了，KEDA 是不是要凉？"
>
> 答案：两者是**共生**关系，不是竞争。

## 一、HPA 的前世今生

HPA（Horizontal Pod Autoscaler）是 K8s 内置的自动扩缩容组件。核心公式：

```
期望副本数 = ceil(当前指标值 / 目标阈值 × 当前副本数)
```

### HPA v2 三种指标类型

| 指标类型 | 说明 | 数据来源 |
|---------|------|---------|
| **Resource Metrics** | CPU/内存使用率（最常用） | Metrics Server，15 秒轮询 |
| **Pod Metrics** | 每个 Pod 的 QPS、活跃连接数等自定义指标 | 需部署 Prometheus Adapter 等适配器 |
| **External Metrics** | 集群外部指标（云消息队列深度等） | 需自定义指标适配器 |

### HPA v1.36 之前的三大硬伤

1. **不能缩零**：`minReplicas` 最小为 1，空闲时至少保留一个 Pod，持续产生成本
2. **无原生外部事件源**：对接 Kafka、RabbitMQ 等需要自建指标链路，配置复杂
3. **单一指标服务**：整个集群只能有一个自定义指标 API 服务，多个适配器会冲突

## 二、KEDA：事件驱动的扩缩容专家

KEDA（Kubernetes Event-Driven Autoscaling）是 CNCF 毕业项目，定位为 HPA 的**增强扩展**而非替代品。

### 架构

```
外部事件源 → KEDA Scaler 轮询 → 转换为 HPA 指标 → HPA 调整副本数
                ↓（无事件时）
           缩容到 0，等待事件恢复
```

**关键设计：KEDA 不替换 HPA，而是为每个 ScaledObject 自动生成对应的 HPA 资源。** 缩放决策最终仍由 HPA 执行。

### 内置 60+ 开箱即用 Scaler

| 类别 | 支持的事件源 |
|------|-----------|
| 消息队列 | Kafka、RabbitMQ、AWS SQS、Azure Service Bus、NATS、Redis Streams、GCP Pub/Sub |
| 数据库 | PostgreSQL、MySQL、MongoDB、Redis Lists |
| 云服务 | AWS CloudWatch、Azure Monitor、GCP Stackdriver |
| 定时任务 | Cron 触发器，支持时区配置 |
| 其他 | Prometheus、Datadog、New Relic |

### ScaledObject 实战（Kafka 消费者）

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: order-consumer
spec:
  scaleTargetRef:
    name: order-consumer
  pollingInterval: 30
  cooldownPeriod: 300
  minReplicaCount: 0        # 缩零
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

### KEDA 2.16 新特性（2026）

- GCP Secret Manager 支持（TriggerAuthentication 直接引用，无需手动管理 K8s Secret）
- ConfigMap TriggerAuthentication（简化配置管理）
- NATS 2.10 集成优化（事件处理延迟降低 55%）
- Redis 7.2 Streams 深度支持（Consumer Group 级别扩缩容）

## 三、v1.36 大新闻：HPA Scale-to-Zero

`HPAScaleToZero` 特性门控在 v1.36 中默认启用，历经 7 年打磨（从 v1.16 开始孵化）。

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: batch-processor
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: batch-processor
  minReplicas: 0              # v1.36 原生支持！
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

HPA Scale-to-Zero 解决的是"能缩零"的问题，但**仍需要外部指标源来通知 HPA 何时从 0 恢复到 1**。KEDA 恰好可以作为这个外部指标源——你甚至可以同时使用 HPA Scale-to-Zero 和 KEDA。

### v1.36 同期新特性：External Metrics Fallback

当外部指标源不可用时（Prometheus 宕机、云 API 超时），HPA 使用配置的回退值继续决策，而不是完全冻结扩缩容。

## 四、全方位对比矩阵

| 维度 | HPA（v1.36） | KEDA（2.16） |
|------|:-----------:|:----------:|
| **定位** | K8s 原生内置组件 | CNCF 毕业项目，增强 HPA |
| **安装成本** | 零，内置即可用 | 需部署 Operator + CRD |
| **缩零支持** | ✅ Beta，默认启用 | ✅ 稳定，核心功能 |
| **事件源** | 需自定义指标适配器 | 内置 60+ Scaler，开箱即用 |
| **多事件源** | 不支持单 HPA 多外部指标类型 | 支持单 ScaledObject 多触发器 |
| **认证管理** | 依赖适配器自行处理 | TriggerAuthentication + 云 IAM |
| **轮询间隔** | 默认 15 秒 | 默认 30 秒（可配） |
| **调试难度** | 低，`kubectl describe hpa` | 中高，需排查 Operator + ScaledObject + HPA |
| **升级维护** | 随 K8s 版本升级 | 需手动升级 CRD + Operator |

## 五、选型决策树

| 场景 | 推荐 | 理由 |
|------|------|------|
| **标准 HTTP 服务** | **HPA** | 原生支持，零额外依赖，CPU/内存指标足够 |
| **消息队列消费者** | **KEDA** | 杀手场景——60+ Scaler 开箱即用，无需搭 Prometheus → Adapter 链路 |
| **混合场景（HTTP + 事件驱动）** | **HPA + KEDA 协同** | HTTP 服务用 HPA，队列消费者用 KEDA，两者互不冲突 |
| **多事件源混合触发** | **KEDA** | 同时基于 Kafka 积压 + Redis 队列 + Cron 定时扩缩容，KEDA 多触发器是唯一选择 |
| **测试/预发布环境** | **v1.36 HPA** | 集群已升级 v1.36，直接用原生缩零，减少组件依赖 |

> ⚠️ **不要为同一个 Deployment 同时创建 HPA 和 KEDA ScaledObject**，会导致副本数控制冲突。

## 六、五大生产避坑

### 坑 1：缩零后的冷启动延迟

消费者从 0 恢复到处理第一条消息可能耗时 30-90 秒（KEDA pollingInterval 30s + HPA 响应 15s + Pod 调度 + 镜像拉取 + 应用初始化）。

**解决**：延迟敏感服务将 `minReplicaCount` 设为 1；预构建镜像 + 本地缓存；pollingInterval 调至 10-15 秒。

### 坑 2：认证配置复杂

KEDA 连接云服务事件源时报认证错误。

**解决**：AWS 用 IRSA（IAM Roles for Service Accounts）代替静态密钥；GCP 用 KEDA 2.16 新增的 GCP Secret Manager 集成；本地密钥通过 TriggerAuthentication + K8s Secret 管理并定期轮转。

### 坑 3：HPA 指标不可用导致决策冻结

Prometheus 宕机后 HPA 既不扩也不缩，集群规模僵死。

**解决**：v1.36 使用 External Metrics Fallback 配置降级值；或考虑 KEDA 内置的 Prometheus Scaler。

### 坑 4：多 HPA/KEDA 控制器冲突

副本数反复震荡，Deployment 状态异常。

**解决**：每个 Deployment 只用一个扩缩容控制器；KEDA 环境下删除手动创建的 HPA；用 `kubectl get hpa -A` 和 `kubectl get scaledobject -A` 检查冲突。

### 坑 5：KEDA 升级 CRD 不兼容

升级 KEDA 后 ScaledObject 报 schema 校验错误。

**解决**：升级前阅读 Release Notes 的 "Upgrade Notes"；Helm 升级时指定 `--set crds.install=true`；关键集群先在 staging 验证。

## 七、监控告警配置

```yaml
groups:
- name: autoscaling
  rules:
  # HPA 无法获取指标
  - alert: HPAMetricsUnavailable
    expr: kube_hpa_status_condition{condition="AbleToScale",status="false"} == 1
    for: 5m
    labels: { severity: warning }

  # KEDA Scaler 错误
  - alert: KEDAScalerErrors
    expr: sum(rate(keda_scaler_errors[5m])) by (scaledObject, scaler) > 0
    for: 5m
    labels: { severity: warning }

  # HPA 接近上限
  - alert: HPANearMaxReplicas
    expr: (kube_hpa_status_current_replicas / kube_hpa_spec_max_replicas) > 0.8
    for: 10m
    labels: { severity: warning }
```

## 八、总结

v1.36 的 HPA Scale-to-Zero 不是替代信号，而是**互补信号**：

1. **HPA 仍是标准 HTTP 服务的首选** — 原生、简单、可靠。v1.36 让测试环境也有了缩零能力
2. **KEDA 在事件驱动领域不可替代** — 60+ 内置 Scaler、多触发器融合、原生认证管理，HPA 短期内无法覆盖
3. **两者会继续共存并深化协同** — KEDA 底层依赖 HPA 执行缩放，HPA Scale-to-Zero 依赖外部指标源（如 KEDA）告知何时恢复

> **一句话选型：HTTP 服务用 HPA，队列消费用 KEDA，混合场景两者协同，测试环境 v1.36 原生缩零。**
