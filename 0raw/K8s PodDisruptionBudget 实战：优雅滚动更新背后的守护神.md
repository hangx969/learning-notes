---
title: "K8s PodDisruptionBudget 实战：优雅滚动更新背后的守护神"
source: "https://mp.weixin.qq.com/s/lXl9ZvAdJ7mTbwsdpwSPig"
author:
  - "[[WAKEUP技术]]"
published:
created: 2026-06-05
description: "个人主页：https://lweiqiang.xyz"
tags:
  - "clippings"
---
WAKEUP技术 *2026年5月24日 13:07*

作者：WAKE UP技术  
公众号：WAKE UP技术  
个人主页：https://lweiqiang.xyz  
技术博客：https://blog.lweiqiang.xyz

---

如果你在生产环境做过 K8s 节点维护，或者目睹过一次滚动更新把服务打瘫，那你很可能遇到了这个问题： **所有副本恰好在同一时间被驱逐或重启** 。

PodDisruptionBudget（PDB）就是用来解决这个问题的。它不是一个复杂的概念，但在生产中被忽略的频率高得惊人——直到出了事故才被人记起来。

---

## 一、什么是 PDB，为什么需要它

K8s 中，Pod 被中断（Disruption）分两种：

- • **非自愿中断（Involuntary）** ：节点宕机、内核 panic、OOMKill，这类无法提前预知
- • **自愿中断（Voluntary）** ： `kubectl drain` 、滚动更新、集群升级，这类是人为触发的

PDB 只对 **自愿中断** 生效，它告诉 K8s："在任何主动操作期间，我的这组 Pod 最多/最少允许多少个同时不可用。"

没有 PDB， `kubectl drain node-1` 会不管不顾地驱逐节点上的所有 Pod；有了 PDB，驱逐操作会被迫等待，直到副本数量满足你设定的可用性下限。

---

## 二、PDB 的两种配置方式

PDB 有两个关键字段，二选一：

### 方式一：minAvailable——最少保持可用

```
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

**场景** ：支付服务有 3 个副本， `minAvailable: 2` 意味着任何时候最多只能有 1 个 Pod 被中断。

### 方式二：maxUnavailable——最多允许不可用

```
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

两者都支持 **百分比** ，这在副本数量动态变化时更实用：

```
spec:
  minAvailable: "80%"    # 始终保持80%的副本可用
  # 或者
  maxUnavailable: "20%"  # 最多允许20%不可用
```

**注意** ：百分比会向下取整。如果你有 3 个副本且设置 `minAvailable: "80%"` ，计算结果是 2.4，向下取整为 2——和直接写 2 效果一样。

---

## 三、PDB 如何与 Drain 和滚动更新配合

### 场景一：kubectl drain 节点维护

```
# 准备维护 node-3
kubectl drain node-3 --ignore-daemonsets --delete-emptydir-data
```

drain 过程中，K8s 的 eviction API 会检查目标 Pod 对应的 PDB：

```
检查 PDB → 驱逐 pod-A(node-3) 是否会违反 minAvailable?
  当前可用: 3/3
  驱逐后剩余: 2/3
  minAvailable: 2 → 满足 → 允许驱逐
  
等待 pod-A 在其他节点就绪后，再尝试驱逐 pod-B...
```

如果你有 2 个节点同时被 drain，而服务只有 2 个副本且 `minAvailable: 2` ，第二个节点的驱逐就会被 **无限阻塞** 。这是保护，也是陷阱（下面会详细讲）。

### 场景二：Deployment 滚动更新

滚动更新（RollingUpdate）本身有 `maxUnavailable` 和 `maxSurge` 控制，但它们是 Deployment 策略层的配置，而 PDB 是额外的保护层：

```
# Deployment 的更新策略
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```

两者同时存在时，PDB 的约束更严格——滚动更新的每一步都必须同时满足 Deployment 策略和 PDB 的约束。

---

## 四、生产中的典型配置模式

### 模式一：高可用服务（3副本+）

```
# 始终保持至少2个副本在线
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

```
# 对于有状态服务，通常只允许1个同时不可用
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: mysql-pdb
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app: mysql
      role: replica  # 只保护 replica，不保护 primary（或单独配置）
```

### 模式三：批处理 Job（允许较多中断）

```
# 批处理 Worker，允许最多30%同时被中断
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: batch-worker-pdb
spec:
  maxUnavailable: "30%"
  selector:
    matchLabels:
      app: batch-worker
```

---

## 五、常见的 PDB 配置陷阱

### 陷阱一：单副本服务配 minAvailable: 1

```
# ❌ 这会导致节点永远无法被 drain！
spec:
  replicas: 1
  ...
---
spec:
  minAvailable: 1  # 只有1个副本，drain时永远无法满足
```

单副本服务要么接受可能的中断，要么升级到 2 副本。配 PDB 而不增加副本，只会让运维陷入困境：

```
$ kubectl drain node-1 --ignore-daemonsets
node/node-1 already cordoned
evicting pod production/payment-service-xxx
error when evicting pods/"payment-service-xxx" -n "production" (will retry after 5s): 
  Cannot evict pod as it would violate the pod's disruption budget.
```

drain 会永远卡在这里，直到有人手动 `--force` 强制驱逐或修改 PDB。

### 陷阱二：PDB minAvailable 等于副本总数

```
spec:
  replicas: 3
---
spec:
  minAvailable: 3  # ❌ 等同于"不允许任何中断"
```

这配置的效果是节点维护永远无法进行。正确做法是 `minAvailable: replicas - 1` 或使用百分比留出余量。

### 陷阱三：忘记配 selector

```
# ❌ selector 为空会匹配所有 Pod
spec:
  minAvailable: 2
  selector: {}  # 这会保护命名空间内所有 Pod
```

如果 selector 过宽，PDB 会误保护不相关的 Pod，导致不必要的驱逐阻塞。

### 陷阱四：PDB 和 HPA 配合时的计算失误

HPA 会动态调整副本数，PDB 的百分比配置需要考虑最小副本场景：

```
# HPA 配置
spec:
  minReplicas: 2
  maxReplicas: 10

# PDB 配置
spec:
  maxUnavailable: "50%"  # 当副本是2时，50%=1，意味着可以下降到1个
                         # 这对高可用服务来说可能太激进了
```

更安全的做法是用绝对数：

```
spec:
  minAvailable: 1  # 无论 HPA 如何扩缩，至少保证1个可用
```

---

## 六、如何验证 PDB 是否生效

### 查看 PDB 状态

```
kubectl get pdb -n production
# NAME                   MIN AVAILABLE   MAX UNAVAILABLE   ALLOWED DISRUPTIONS   AGE
# payment-service-pdb    2               N/A               1                     3d
# order-service-pdb      N/A             1                 1                     3d
```

`ALLOWED DISRUPTIONS` 是当前允许中断的 Pod 数量，取决于当前可用副本数和 PDB 配置。

### 模拟驱逐测试

```
# 使用 eviction API 测试（不会真正删除 Pod）
kubectl get pod payment-service-xxx -n production -o json | \
  jq '.metadata.name' | \
  xargs -I{} kubectl debug -it {} --image=busybox -- /bin/sh

# 或者直接调用 eviction API
cat <<EOF | kubectl apply -f -
apiVersion: policy/v1
kind: Eviction
metadata:
  name: payment-service-xxx
  namespace: production
EOF
```

如果 PDB 阻止了驱逐，会返回 `429 Too Many Requests` 。

### 检查 drain 被阻塞的原因

```
kubectl get events -n production --field-selector reason=DisruptionTarget
# 可以看到因为 PDB 被阻止的驱逐记录
```

---

## 七、一个完整的生产示例

下面是一个电商支付服务的完整 PDB + Deployment 配置：

```
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: payment-service
      version: v2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0      # 滚动更新时不允许不可用（先扩再缩）
      maxSurge: 1            # 允许临时多1个Pod
  template:
    metadata:
      labels:
        app: payment-service
        version: v2
    spec:
      terminationGracePeriodSeconds: 60  # 给Pod 60s优雅退出
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
# pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payment-service-pdb
  namespace: production
spec:
  minAvailable: 2           # 3副本中至少2个可用
  selector:
    matchLabels:
      app: payment-service
```

`maxUnavailable: 0` + `minAvailable: 2` 的组合意味着：

- • 滚动更新时先启动新 Pod（surge），确认就绪后再删除旧 Pod
- • 节点维护时最多只允许驱逐 1 个 Pod

这是对支付类核心服务来说最稳健的配置。

---

PDB 不是万能的，它只能保护自愿中断，节点宕机该挂还是会挂。但它能把"人为操作导致的可用性损失"降到最低，是生产集群中不该省略的基础配置。

配了 PDB，不等于一劳永逸；没配 PDB，就等于把可用性交给了运气。

**微信扫一扫赞赏作者**

继续滑动看下一个

WAKE UP技术

向上滑动看下一个