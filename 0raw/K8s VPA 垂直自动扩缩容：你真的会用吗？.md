---
title: "K8s VPA 垂直自动扩缩容：你真的会用吗？"
source: "https://mp.weixin.qq.com/s/FfNIwJJrF9XpBSZMNcffag"
author:
  - "[[WAKEUP技术]]"
published:
created: 2026-05-15
description: "个人主页：https://lweiqiang.xyz"
tags:
  - "clippings"
---
WAKEUP技术 *2026年5月15日 09:46*

作者：WAKE UP技术  
公众号：WAKE UP技术  
个人主页：https://lweiqiang.xyz  
技术博客：https://blog.lweiqiang.xyz

---

> 大家都知道 HPA 横向扩容，但资源 requests 设多少合适？全靠拍脑袋？VPA（Vertical Pod Autoscaler）就是解决这个问题的。本文用 Q&A 形式，深入讲解 VPA 的工作原理、四种模式的适用场景，以及与 HPA 共存的正确姿势。

---

**Q1：VPA 是什么？解决了什么问题？**

**A：** VPA（Vertical Pod Autoscaler）是 Kubernetes 的垂直 Pod 自动扩缩容器，它可以根据历史使用量， **自动推荐或调整** Pod 的 CPU/Memory requests 和 limits。

它解决的核心问题是：

| 问题 | 说明 |
| --- | --- |
| requests 设太低 | Pod 频繁被 OOMKilled 或 CPU Throttled |
| requests 设太高 | 资源浪费，节点利用率低 |
| 手动调整滞后 | 业务增长后 requests 没跟上 |

VPA 的三个核心组件：

```
┌───────────────────────────────────────────────────────┐
│                  VPA 组件架构                          │
├──────────────────┬────────────────────────────────────┤
│ Recommender      │ 分析历史指标，生成资源推荐值        │
│ Admission Plugin │ Pod 创建时注入推荐的 requests/limits│
│ Updater          │ 驱逐超出推荐范围的 Pod 触发重建     │
└──────────────────┴────────────────────────────────────┘
```

---

**Q2：VPA 有哪几种 updateMode？分别适合什么场景？**

**A：** VPA 支持四种模式，按侵入性从低到高排列：

| Mode | 行为 | 适用场景 |
| --- | --- | --- |
| `Off` | 只生成推荐，不做任何修改 | 先观察，收集数据 |
| `Initial` | 只在 Pod 首次创建时注入推荐值 | 稳定服务，减少驱逐 |
| `Auto` | 自动注入 + 驱逐过期 Pod | 接受一定重启的服务 |
| `Recreate` | 强制驱逐并用新推荐值重建 | 需要立即生效（少用） |

**生产建议** ：先用 `Off` 模式跑 1-2 周收集推荐值，然后切换到 `Initial` 稳定运行，核心服务不要用 `Auto` 或 `Recreate` ，因为会触发 Pod 重启影响可用性。

---

**Q3：怎么安装 VPA 并创建一个 VPA 对象？**

**A：** 安装 VPA（以 metrics-server 已就绪为前提）：

```
# 克隆官方仓库
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler

# 安装 VPA CRD 和组件
./hack/vpa-up.sh

# 验证安装
kubectl get pods -n kube-system | grep vpa
# vpa-admission-controller-xxx   1/1 Running
# vpa-recommender-xxx             1/1 Running
# vpa-updater-xxx                 1/1 Running
```

创建一个 VPA 对象（Off 模式，先看推荐值）：

```
# vpa-demo.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
  namespace: default
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Off"   # 先用 Off 模式观察
  resourcePolicy:
    containerPolicies:
    - containerName: my-app
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 4
        memory: 4Gi
      controlledResources: ["cpu", "memory"]
```
```
kubectl apply -f vpa-demo.yaml

# 查看推荐值（需等待 VPA 收集足够数据）
kubectl describe vpa my-app-vpa
```

输出示例：

```
Status:
  Recommendation:
    Container Recommendations:
    - Container Name: my-app
      Lower Bound:
        Cpu: 200m
        Memory: 256Mi
      Target:             # 推荐值（最重要）
        Cpu: 500m
        Memory: 512Mi
      Upper Bound:
        Cpu: 1
        Memory: 1Gi
      Uncapped Target:    # 不受 minAllowed/maxAllowed 约束的原始推荐
        Cpu: 500m
        Memory: 512Mi
```

---

**Q4：VPA 和 HPA 能同时使用吗？**

**A：** **不能同时对同一资源（CPU/Memory）使用 VPA Auto/Recreate 模式 + HPA based on CPU/Memory** ，这会造成控制器互相打架：VPA 刚把 requests 调大，HPA 发现利用率下降开始缩容；HPA 缩容后资源利用率上升，VPA 又推大 requests……死循环。

**正确的共存方案** ：

```
方案1：VPA Off 模式 + HPA（VPA 只做参考，人工调整 requests）
方案2：VPA 管 Memory（HPA 不基于 Memory 扩容）+ HPA 管 CPU 水平扩容
方案3：KEDA 基于自定义指标 HPA + VPA Off 模式推荐
```

配置示例（VPA 只管内存，HPA 只管 CPU 水平扩容）：

```
# VPA：只控制 Memory
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: my-app
      controlledResources: ["memory"]   # 只控制内存
      minAllowed:
        memory: 128Mi
      maxAllowed:
        memory: 4Gi
---
# HPA：只基于 CPU 水平扩
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

**Q5：VPA 推荐值算法是什么？怎么影响它的推荐结果？**

**A：** VPA Recommender 使用 **指数衰减直方图** 算法对历史 CPU/Memory 使用量建模：

- • **CPU 推荐** ：基于使用量分布的第 95 百分位（P95），不是平均值
- • **Memory 推荐** ：基于最近一段时间的内存使用高水位
- • **历史窗口** ：默认采集过去 8 天的数据（可通过 `--history-length` 调整）
- • **衰减因子** ：越近的数据权重越高（近期流量特征更重要）

这意味着：

- • 如果你的服务有周期性业务高峰（每周一峰值），VPA 会把这个峰值纳入推荐
- • 如果刚上线没多少历史数据，推荐值可能偏低，需要等 1-2 周

通过 `resourcePolicy` 可以约束推荐范围：

```
resourcePolicy:
  containerPolicies:
  - containerName: my-app
    minAllowed:
      cpu: 200m       # 不能低于 200m
      memory: 256Mi
    maxAllowed:
      cpu: 2          # 不能超过 2 核（防止推荐值过大占满节点）
      memory: 2Gi
```

---

**Q6：VPA 会不会驱逐正在处理请求的 Pod？**

**A：** 会，这是 VPA `Auto` / `Recreate` 模式的最大风险。Updater 组件发现 Pod 当前资源与推荐值差异超过阈值时，会主动 evict Pod。

**缓解措施** ：

1. 1\. **配合 PDB（PodDisruptionBudget）限制最大驱逐数**
```
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-app-pdb
spec:
  maxUnavailable: 1      # 同时只允许 1 个 Pod 不可用
  selector:
    matchLabels:
      app: my-app
```
1. 2\. **设置合理的 minAllowed/maxAllowed 缩小触发范围**
2. 3\. **生产核心服务建议使用 `Initial` 模式** ，只在 Pod 重建（滚动升级/节点迁移）时才注入新推荐值，不主动驱逐。

---

**Q7：如何监控 VPA 的运行效果？**

**A：** 使用 Prometheus + Grafana 监控 VPA：

```
# VPA 关键指标（vpa-recommender 暴露）
vpa_recommender_memory_usage            # Recommender 自身内存使用
vpa_recommender_cpu_usage               # Recommender CPU 使用
vpa_recommender_recommendations_total   # 总推荐次数

# 通过 kubectl 定期导出推荐值差异（可写脚本告警）
kubectl get vpa -A -o json | jq '.items[] | {
  name: .metadata.name,
  namespace: .metadata.namespace,
  target: .status.recommendation.containerRecommendations[0].target
}'
```

也可以直接在 Grafana 导入 VPA 相关 Dashboard（Grafana ID: **14588** ）。

---

> **总结** ：VPA 是解决 K8s 资源 requests 配置不当的利器。关键要点：1）先用 `Off` 模式收集推荐数据；2）核心服务用 `Initial` 减少驱逐影响；3）与 HPA 共存时要分离控制维度（VPA 管内存，HPA 管 CPU）；4）始终配合 PDB 保障可用性。

**微信扫一扫赞赏作者**

继续滑动看下一个

WAKE UP技术

向上滑动看下一个