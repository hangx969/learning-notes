---
title: "K8s PodDisruptionBudget 实战：优雅中断保护"
source: "https://mp.weixin.qq.com/s/lXl9ZvAdJ7mTbwsdpwSPig"
created: 2026-06-06
tags:
  - kubernetes
  - pdb
  - high-availability
  - deployment
---

# K8s PodDisruptionBudget 实战

## 一、什么是 PDB

Pod 中断分两种：
- **非自愿中断（Involuntary）**：节点宕机、内核 panic、OOMKill，无法提前预知
- **自愿中断（Voluntary）**：`kubectl drain`、滚动更新、集群升级，人为触发

PDB 只对**自愿中断**生效，告诉 K8s："在任何主动操作期间，我的这组 Pod 最多/最少允许多少个同时不可用。"

没有 PDB，`kubectl drain` 会不管不顾地驱逐所有 Pod；有了 PDB，驱逐操作会被迫等待，直到副本数量满足可用性下限。

## 二、两种配置方式（二选一）

### minAvailable——最少保持可用

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payment-service-pdb
  namespace: production
spec:
  minAvailable: 2        # 始终保持至少2个Pod可用
  selector:
    matchLabels:
      app: payment-service
```

### maxUnavailable——最多允许不可用

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: order-service-pdb
  namespace: production
spec:
  maxUnavailable: 1      # 最多允许1个Pod同时不可用
  selector:
    matchLabels:
      app: order-service
```

两者都支持**百分比**（副本数动态变化时更实用）：

```yaml
spec:
  minAvailable: "80%"    # 始终保持80%的副本可用
  # 或
  maxUnavailable: "20%"  # 最多允许20%不可用
```

> **注意**：百分比会向下取整。3 副本 + `minAvailable: "80%"` = 2.4 → 取整为 2。

## 三、PDB 与 Drain / 滚动更新的配合

### 场景一：kubectl drain 节点维护

drain 过程中，K8s 的 eviction API 会检查目标 Pod 对应的 PDB：

```
检查 PDB → 驱逐 pod-A 是否会违反 minAvailable?
  当前可用: 3/3
  驱逐后剩余: 2/3
  minAvailable: 2 → 满足 → 允许驱逐
  
等待 pod-A 在其他节点就绪后，再尝试驱逐 pod-B...
```

如果 2 个节点同时被 drain，而服务只有 2 副本且 `minAvailable: 2`，第二个节点的驱逐会被**无限阻塞**。

### 场景二：Deployment 滚动更新

滚动更新本身有 `maxUnavailable` 和 `maxSurge` 控制，PDB 是额外的保护层。两者同时存在时，**PDB 的约束更严格**——每一步都必须同时满足 Deployment 策略和 PDB 约束。

## 四、生产配置模式

### 模式一：高可用服务（3副本+）

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-gateway-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: api-gateway
      tier: frontend
```

### 模式二：数据库 StatefulSet（严格保护）

```yaml
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app: mysql
      role: replica  # 只保护 replica，primary 单独配置
```

### 模式三：批处理 Job（允许较多中断）

```yaml
spec:
  maxUnavailable: "30%"
  selector:
    matchLabels:
      app: batch-worker
```

## 五、四大配置陷阱

### 陷阱一：单副本服务配 minAvailable: 1

```yaml
# ❌ 会导致节点永远无法被 drain！
spec:
  replicas: 1
---
spec:
  minAvailable: 1  # 只有1个副本，drain时永远无法满足
```

drain 会永远卡住，直到手动 `--force` 或修改 PDB。单副本服务要么接受中断，要么升级到 2 副本。

### 陷阱二：minAvailable 等于副本总数

```yaml
# ❌ 等同于"不允许任何中断"
spec:
  replicas: 3
---
spec:
  minAvailable: 3  # 节点维护永远无法进行
```

正确做法：`minAvailable: replicas - 1` 或用百分比留出余量。

### 陷阱三：忘记配 selector

```yaml
# ❌ selector 为空会匹配所有 Pod
spec:
  minAvailable: 2
  selector: {}  # 误保护命名空间内所有 Pod
```

### 陷阱四：PDB 和 HPA 配合时的计算失误

HPA 动态调整副本数，PDB 百分比需考虑最小副本场景：

```yaml
# HPA: minReplicas: 2, maxReplicas: 10
# PDB: maxUnavailable: "50%"
# 当副本是2时，50%=1，可能对高可用服务太激进

# 更安全的做法：用绝对数
spec:
  minAvailable: 1  # 无论 HPA 如何扩缩，至少保证1个可用
```

## 六、验证 PDB 是否生效

```bash
# 查看 PDB 状态
kubectl get pdb -n production
# NAME                   MIN AVAILABLE   MAX UNAVAILABLE   ALLOWED DISRUPTIONS   AGE
# payment-service-pdb    2               N/A               1                     3d

# 检查 drain 被阻塞的原因
kubectl get events -n production --field-selector reason=DisruptionTarget

# 调用 eviction API 测试（被 PDB 阻止会返回 429 Too Many Requests）
```

`ALLOWED DISRUPTIONS` 是当前允许中断的 Pod 数量，取决于当前可用副本数和 PDB 配置。

## 七、完整生产示例（支付服务）

```yaml
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
  namespace: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0      # 先扩再缩，零停机
      maxSurge: 1
  template:
    spec:
      terminationGracePeriodSeconds: 60
      containers:
      - name: payment
        image: payment-service:v2.3.1
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
---
# PDB
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payment-service-pdb
  namespace: production
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: payment-service
```

`maxUnavailable: 0` + `minAvailable: 2` 组合效果：
- 滚动更新时先启动新 Pod（surge），确认就绪后再删除旧 Pod
- 节点维护时最多只允许驱逐 1 个 Pod
