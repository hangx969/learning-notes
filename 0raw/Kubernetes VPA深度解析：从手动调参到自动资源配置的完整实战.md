---
title: "Kubernetes VPA深度解析：从手动调参到自动资源配置的完整实战"
source: "https://mp.weixin.qq.com/s/fxp4cBRXUG9XRluke62f-w"
author:
  - "[[WAKEUP技术]]"
published:
created: 2026-06-05
description: "个人主页：https://lweiqiang.xyz"
tags:
  - "clippings"
---
WAKEUP技术 *2026年5月23日 15:13*

作者：WAKE UP技术  
公众号：WAKE UP技术  
个人主页：https://lweiqiang.xyz  
技术博客：https://blog.lweiqiang.xyz

---

某公司 K8s 集群中 120 个微服务的资源配置现状：

```
# 开发随意设的"安全值"
resources:
  requests:
    memory: "512Mi"   # 实际只用 80Mi
    cpu: "500m"       # 实际只用 50m
  limits:
    memory: "2Gi"     # 峰值 300Mi
    cpu: "2000m"      # 峰值 200m
```

粗略计算，该集群 **70% 的资源被浪费** 。集群总可调度内存 512Gi，实际用不到 200Gi，却因 requests 虚高导致 Pod 无法调度，被迫扩容节点。

这就是 VPA（Vertical Pod Autoscaler）要解决的问题。

---

## VPA 是什么

VPA 是一组控制器，自动分析 Pod 历史资源使用量，给出推荐值并自动调整 Pod 的 `requests` 和 `limits` 。

**VPA 与 HPA 的区别** ：

| 维度 | HPA | VPA |
| --- | --- | --- |
| 扩缩方向 | 水平（增删副本数） | 垂直（调整每个 Pod 资源量） |
| 适用场景 | 无状态服务、流量波动 | 无法水平扩展的有状态服务 |
| 触发条件 | 指标超过阈值 | 历史数据分析 |
| 副作用 | 无 Pod 重启 | 修改配置会触发 Pod 重建 |
| 配合使用 | 与 VPA 配合 | 与 HPA 配合（VPA 在 recommend 模式） |

**VPA 的三个核心组件** ：

```
┌────────────────────────────────────────────────┐
│  VPA Recommender  ← 分析 Metrics，生成建议值    │
│        ↓                                       │
│  VPA Updater     ← 对比当前配置与建议值          │
│        ↓                                       │
│  VPA Admission Controller ← 修改 Pod 资源配置   │
└────────────────────────────────────────────────┘
```

---

## 安装与配置 VPA

### 1\. 安装

```
# 克隆 VPA 仓库
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler

# 部署 VPA 组件
./hack/vpa-up.sh

# 验证
kubectl get pods -n kube-system | grep vpa
# vpa-admission-controller-xxx   1/1  Running
# vpa-recommender-xxx            1/1  Running
# vpa-updater-xxx                1/1  Running
```

### 2\. 创建 VPA 对象

```
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: order-service-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: order-service
  
  updatePolicy:
    updateMode: "Auto"           # 关键：自动更新模式
  
  resourcePolicy:
    containerPolicies:
      - containerName: "order-service"
        minAllowed:               # 下限保护
          cpu: "100m"
          memory: "128Mi"
        maxAllowed:               # 上限保护
          cpu: "2000m"
          memory: "4Gi"
        controlledResources: ["cpu", "memory"]
```

---

## VPA 的四种运行模式

### 1\. Off（关闭）

```
updatePolicy:
  updateMode: "Off"
```

VPA 只计算推荐值，不执行任何变更。适合评估阶段。

### 2\. Initial（初始）

```
updatePolicy:
  updateMode: "Initial"
```

仅在 Pod 创建时注入推荐值，后续不再修改。相当于"帮你填一份初始资源配置，之后你自己管"。

### 3\. Recreate（重建）

```
updatePolicy:
  updateMode: "Recreate"
```

当推荐值与当前值差距超过阈值时， **重建 Pod** 来应用新资源。不可用在生产环境的有状态服务（会中断）。

### 4\. Auto（自动）—推荐

```
updatePolicy:
  updateMode: "Auto"
```

结合 Initial + Recreate 的逻辑：新 Pod 创建时注入推荐值，推荐值变化较大时重建 Pod。 **但需要注意 Pod 中断** 。

---

## 实际案例：优化一个有状态服务

### 场景

MySQL StatefulSet 在 K8s 中运行，初期配置：

```
resources:
  requests:
    memory: "2Gi"
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "4000m"
```

### 步骤 1：观察期 —— Off 模式

创建 VPA：

```
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: mysql-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: StatefulSet
    name: mysql
  updatePolicy:
    updateMode: "Off"
```

等待 24 小时后，查看推荐值：

```
kubectl describe vpa mysql-vpa -n production
```

输出关键部分：

```
Recommendation:
  Container Recommendations:
    Container Name: mysql
    Lower Bound:
      Cpu:     200m
      Memory:  900Mi
    Target:
      Cpu:     450m
      Memory:  1.2Gi
    Upper Bound:
      Cpu:     1500m
      Memory:  4Gi
```

**分析** ：

- • **Target（推荐值）** ：requests 应为 450m CPU / 1.2Gi 内存 —— 比原来的 1000m/2Gi 小很多
- • **Upper Bound（上限）** ：limits 建议 1500m/4Gi
- • **Lower Bound（下限）** ：最低 200m/900Mi

### 步骤 2：切换为 Initial 模式

修改 VPA 为 Initial 模式，让新 Pod 使用推荐值：

```
spec:
  updatePolicy:
    updateMode: "Initial"
```

执行滚动升级：

```
kubectl rollout restart statefulset mysql -n production
```

### 步骤 3：对比资源变化

```
# 查看 VPA 优化前后的资源分配
kubectl top pod mysql-0 -n production
# 优化前: CPU 80m / Memory 500Mi（分配了 1000m/2Gi）
# 优化后: CPU 120m / Memory 800Mi（分配了 450m/1.2Gi）
```

**效果** ：

- • 单个 Pod 节省：550m CPU + 800Mi 内存
- • 3 副本：节省 1650m CPU + 2.4Gi 内存
- • 省下一个 4C8G 节点的成本

---

## VPA 使用避坑指南

### 坑 1：VPA 与 HPA 同时使用

**错误** ：VPA 设 Auto 模式 + HPA 同时生效

VPA 调整资源时会重建 Pod，HPA 又会根据负载调整副本数。两者同时作用于 CPU，可能导致：

- • VPA 缩小 resources → 副本 CPU 不足 → HPA 扩容 → 更多 Pod → 资源总量反而增加

**正确做法** ：

```
# VPA 改为 Off 或 Initial，只管推荐不管执行
spec:
  updatePolicy:
    updateMode: "Off"

# 只在 VPA 中调整 memory（不改 CPU），HPA 管 CPU
spec:
  resourcePolicy:
    containerPolicies:
      - containerName: "*"
        controlledResources: ["memory"]  # 只管控内存
```

HPA 和 VPA 分工：HPA 管副本数和 CPU，VPA 管内存。

### 坑 2：OOMKill 的恶性循环

Pod 被 VPA 缩小内存后偶尔 OOM → Pod 重启 → 重启期间无历史数据 → VPA 给出更小的推荐值 → 更大 OOM 风险。

**解决办法** ：

```
spec:
  resourcePolicy:
    containerPolicies:
      - containerName: "app"
        minAllowed:
          memory: "256Mi"  # 设置合理下限
        maxAllowed:
          memory: "2Gi"
        mode: "Auto"
```

**很重要** ： `minAllowed` 必须大于应用的空闲基准内存，要有一定冗余。

### 坑 3：对 JVM 应用的资源推荐偏差

JVM 应用的 RSS 内存和使用内存差异大。VPA 推荐基于容器内存使用，但 JVM 启动就会分配大量堆内存。

**建议** ：对 JVM 应用设置合理的 `minAllowed` ，至少等于 `-Xms` 的值：

```
resourcePolicy:
  containerPolicies:
    - containerName: "spring-app"
      minAllowed:
        memory: "1Gi"  # 与 -Xms1g 对应
        cpu: "500m"
```

### 坑 4：干扰 Prometheus 查询的容器重启

VPA 频繁重启容器会导致 Prometheus 数据出现空洞：

```
# 限制 VPA 更新频率
spec:
  updatePolicy:
    updateMode: "Auto"
    minReplicas: 1
  # 没有直接限制频率的参数，但可以通过 resourcePolicy 的差距阈值间接控制
```

---

## 进阶：自定义 Recommender

如果默认的直方图算法不够，可以部署自定义 Recommender：

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: custom-vpa-recommender
  namespace: kube-system
spec:
  replicas: 1
  template:
    spec:
      containers:
        - name: recommender
          image: my-registry/custom-recommender:v1
          args:
            - --recommender-name=custom
            - --storage=prometheus
            - --prometheus-address=http://prometheus:9090
            - --history-length=14d
            - --pod-recommendation-min-memory=64Mi
```

在 VPA 对象中指定：

```
spec:
  recommenders:
    - name: custom
```

---

## 总结

VPA 的核心价值在于 **用数据驱动的方式消灭"猜的参数"** ：

| 阶段 | 操作 |
| --- | --- |
| 观察期（1-7天） | Off 模式，收集推荐值 |
| 灰度验证 | Initial 模式，新 Pod 使用推荐值 |
| 生产推广 | Auto 模式 + minAllowed/maxAllowed 保护 |
| 长期维护 | 定期 review VPA 推荐值趋势 |

**三条铁律** ：

1. 1\. **永远设置 minAllowed/maxAllowed** —— 防止推荐值极端化
2. 2\. **有状态服务用 Initial 而非 Auto** —— 避免不必要的中断
3. 3\. **VPA + HPA 共存时，VPA 只管控内存** —— CPU 交给 HPA

---

*WAKE UP技术 | K8s 资源配置没有银弹，但有数据驱动的方法论*

**微信扫一扫赞赏作者**

继续滑动看下一个

WAKE UP技术

向上滑动看下一个