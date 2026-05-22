---
title: "K8s 集群成本优化方案：砍掉 60% 云账单"
source: "https://mp.weixin.qq.com/s/JPWgnmppvaaBXHeo2yO3nA"
created: 2026-05-22
tags:
  - kubernetes
  - finops
  - cost-optimization
  - scaling
---

> 你的 K8s 集群每月账单是不是像脱缰野马一样失控？Pod 里 request 设了 8 核实际只用了 0.5 核？半夜跑的批处理还占着 32G 内存？

---

## 一、为什么 K8s 成本优化到了必须做的地步？

根据 Flexera 2026 年最新报告，**73% 的企业在 Kubernetes 上存在超过 30% 的资源浪费**，平均浪费率高达 **45%**。

浪费主要来自四大黑洞：

| 浪费类型 | 占比 | 典型场景 |
| --- | --- | --- |
| **过度配置** | 40% | Request/Limit 设为峰值 3-5 倍 |
| **空闲资源** | 30% | 开发/测试环境 7×24 运行 |
| **僵尸资源** | 15% | 废弃 Deployment/未清理 PV |
| **碎片化浪费** | 15% | 节点碎片导致无法调度 |

更致命的是，这些浪费是**隐性的**——不监控根本看不到。

---

## 二、第一层优化：资源 Right-Sizing（省 20%-40%）

### 2.1 问题诊断：集群到底浪费了多少？

快速扫描集群资源利用率的脚本：

~~~bash
#!/bin/bash
# k8s-cost-audit.sh — 快速诊断集群资源浪费
echo "=== Namespace CPU 利用率 ==="
kubectl top pods -A --no-headers | awk '{
  ns=$1; pod=$2;
  split($3,cpu,"m"); usage=cpu[1]/1000;
  printf "%s/%s: %.2f cores\n", ns, pod, usage
}' | sort -t: -k2 -rn | head -20

echo ""
echo "=== Namespace 内存利用率 (Top 20) ==="
kubectl top pods -A --no-headers | awk '{
  ns=$1; pod=$2;
  split($4,mem,"Mi"); usage=mem[1];
  printf "%s/%s: %.0f Mi\n", ns, pod, usage
}' | sort -t: -k2 -rn | head -20

echo ""
echo "=== Pod Request vs 实际使用对比 ==="
kubectl get pods -A -o json | jq -r '
  .items[] | select(.status.phase=="Running") |
  "\(.metadata.namespace)/\(.metadata.name) | CPU Req: \(.spec.containers[].resources.requests.cpu // "none") | Mem Req: \(.spec.containers[].resources.requests.memory // "none")"
' | head -30
~~~

### 2.2 VPA 自动垂直伸缩

VPA 是 Right-Sizing 的核心武器，根据历史数据自动推荐和调整 Pod 的 CPU/内存 Request。

~~~yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: web-app-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
      - containerName: "*"
        minAllowed:
          cpu: 100m
          memory: 128Mi
        maxAllowed:
          cpu: "4"
          memory: 8Gi
        controlledResources: ["cpu", "memory"]
~~~

VPA 四种模式对比：

| 模式 | 行为 | 适用场景 |
| --- | --- | --- |
| `Off` | 仅生成推荐，不修改 Pod | 评估阶段，安全无风险 |
| `Initial` | 仅在 Pod 创建时应用推荐 | 新部署 + 金丝雀 |
| `Recreate` | 重启 Pod 应用推荐 | 非关键服务 |
| `Auto` | 自动驱逐并重建 Pod | 可容忍短暂中断的服务 |

> **生产避坑**：VPA 与 HPA（基于 CPU/内存）**不要同时使用在同一指标上**，否则会互相打架。正确做法是 HPA 管自定义指标（QPS/延迟），VPA 管 CPU/内存。

### 2.3 VPA + HPA 黄金组合架构

~~~yaml
# 最佳实践：VPA 管 CPU/内存，HPA 管业务指标
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: api-server-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  updatePolicy:
    updateMode: "Auto"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second  # HPA 管业务指标
        target:
          type: AverageValue
          averageValue: "1000"
~~~

---

## 三、第二层优化：节点效率最大化（省 20%-30%）

### 3.1 Karpenter 替代 Cluster Autoscaler

2026 年，**Karpenter 已经全面超越 Cluster Autoscaler**，成为节点自动伸缩的首选方案：

| 维度 | Cluster Autoscaler | Karpenter |
| --- | --- | --- |
| **扩容速度** | 30-60 秒 | 5-15 秒（直接调用 EC2 API） |
| **节点类型** | 需预定义 ASG | 支持任意实例类型组合 |
| **Consolidation** | 仅缩容空节点 | 主动替换低效节点 |
| **成本优化** | 被动缩容 | 主动 Spot/按需混合 |
| **Bin-Packing** | ASG 粒度 | Pod 粒度精准匹配 |

~~~yaml
# 生产级 Karpenter 配置
apiVersion: karpenter.sh/v1beta1
kind: Provisioner
metadata:
  name: production-provisioner
spec:
  requirements:
    - key: karpenter.sh/capacity-type
      operator: In
      values: ["spot", "on-demand"]  # Spot 优先
    - key: kubernetes.io/arch
      operator: In
      values: ["amd64"]
    - key: node.kubernetes.io/instance-type
      operator: In
      values:
        - "m6i.large"        # 通用计算
        - "m6i.xlarge"
        - "r6i.large"        # 内存密集
        - "c6i.2xlarge"      # CPU 密集
  ttlSecondsAfterEmpty: 60          # 空节点 60 秒后回收
  ttlSecondsUntilExpired: 604800    # 节点最长存活 7 天（滚动更新）
  limits:
    resources:
      cpu: "1000"
      memory: 2000Gi
  consolidation:
    enabled: true                   # 开启主动合并
  providerRef:
    name: default
~~~

### 3.2 Spot 实例策略（砍 60%-70% 计算成本）

Spot 实例是成本优化的核武器，关键是**正确处理中断**：

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: batch-processor
spec:
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          preference:
            matchExpressions:
              - key: karpenter.sh/capacity-type
                operator: In
                values: ["spot"]
  terminationGracePeriodSeconds: 30
  containers:
    - name: worker
      image: my-batch-processor:v1.2
      lifecycle:
        preStop:
          exec:
            command: ["/bin/sh", "-c", "echo 'Shutting down gracefully...' && sleep 10"]
      resources:
        requests:
          cpu: "2"
          memory: "4Gi"
        limits:
          cpu: "4"
          memory: "8Gi"
~~~

### 3.3 Topology Spread 防止单节点故障

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-frontend
spec:
  replicas: 6
  template:
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: web-frontend
        - maxSkew: 2
          topologyKey: kubernetes.io/hostname
          whenUnsatisfiable: ScheduleAnyway
          labelSelector:
            matchLabels:
              app: web-frontend
~~~

---

## 四、第三层优化：工作负载调度策略（省 10%-20%）

### 4.1 非生产环境定时开关

这是**投入产出比最高**的优化。开发和测试环境不需要 7×24 运行：

~~~yaml
# 工作日 20:00 缩容
apiVersion: batch/v1
kind: CronJob
metadata:
  name: scale-down-dev-after-hours
  namespace: dev
spec:
  schedule: "0 20 * * 1-5"
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: scaler-sa
          containers:
            - name: scaler
              image: bitnami/kubectl:1.31
              command:
                - kubectl
                - scale
                - deployment
                - --all
                - --replicas=0
                - -n
                - dev
          restartPolicy: OnFailure
---
# 工作日 08:00 扩容
apiVersion: batch/v1
kind: CronJob
metadata:
  name: scale-up-dev-morning
  namespace: dev
spec:
  schedule: "0 8 * * 1-5"
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: scaler-sa
          containers:
            - name: scaler
              image: bitnami/kubectl:1.31
              command:
                - kubectl
                - scale
                - deployment
                - --all
                - --replicas=1
                - -n
                - dev
          restartPolicy: OnFailure
~~~

### 4.2 Pod 优先级与资源抢占

让关键工作负载优先获取资源，非关键任务为关键任务让路：

~~~yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: critical-production
value: 1000000
globalDefault: false
description: "生产关键服务，永远不被抢占"
preemptionPolicy: Never
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: batch-jobs
value: 100
globalDefault: false
description: "批处理任务，可被抢占"
preemptionPolicy: PreemptLowerPriority
---
# 批处理 Pod 使用低优先级
apiVersion: v1
kind: Pod
metadata:
  name: nightly-report-generator
spec:
  priorityClassName: batch-jobs
  tolerations:
    - key: "spot-instance"
      operator: "Exists"
      effect: "NoSchedule"
  containers:
    - name: report-gen
      image: report-generator:v2
      resources:
        requests:
          cpu: "4"
          memory: "16Gi"
~~~

---

## 五、第四层优化：监控与 FinOps 可观测性

### 5.1 Prometheus 成本监控

关键告警规则：

~~~yaml
groups:
  - name: k8s_cost_efficiency
    rules:
      # 节点 CPU 利用率低于 20% 告警
      - alert: NodeCPUUnderutilized
        expr: |
          avg(node_namespace_pod_container:container_cpu_usage_seconds_total:sum_rate) by (node)
          / sum(kube_node_status_allocatable{resource="cpu"}) by (node) < 0.2
        for: 2h
        labels:
          severity: warning
          category: cost
        annotations:
          summary: "节点 {{ $labels.node }} CPU 利用率低于 20%"
          description: "持续 2 小时 CPU 利用率不足 20%，建议缩容或合并工作负载"

      # Request 与实际使用偏差超过 3 倍
      - alert: OverRequestedResources
        expr: |
          sum(kube_pod_container_resource_requests{resource="cpu"}) by (namespace)
          / sum(rate(container_cpu_usage_seconds_total{container!=""}[1h])) by (namespace) > 3
        for: 6h
        labels:
          severity: warning
          category: cost
        annotations:
          summary: "命名空间 {{ $labels.namespace }} CPU Request 是实际使用的 3 倍以上"

      # 僵尸 Pod
      - alert: ZombiePods
        expr: |
          count by (namespace) (kube_pod_status_phase{phase=~"Failed|Pending|Unknown"} == 1) > 0
        for: 1h
        labels:
          severity: info
          category: cost
        annotations:
          summary: "命名空间 {{ $labels.namespace }} 存在僵尸 Pod"

      # PVC 未绑定超过 24 小时
      - alert: UnboundPVC
        expr: |
          kube_persistentvolumeclaim_status_phase{phase="Pending"} == 1
        for: 24h
        labels:
          severity: warning
          category: cost
        annotations:
          summary: "PVC {{ $labels.persistentvolumeclaim }} 超过 24 小时未绑定"
~~~

### 5.2 OpenCost 集群成本分摊

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: opencost
  namespace: opencost
spec:
  replicas: 1
  selector:
    matchLabels:
      app: opencost
  template:
    metadata:
      labels:
        app: opencost
    spec:
      containers:
        - name: opencost
          image: opencost/opencost:1.113
          ports:
            - containerPort: 9003
          env:
            - name: PROMETHEUS_ENDPOINT
              value: "http://prometheus-server.monitoring.svc:9090"
            - name: CLOUD_PROVIDER_API_KEY
              valueFrom:
                secretKeyRef:
                  name: cloud-api-key
                  key: api-key
          resources:
            requests:
              cpu: "100m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
~~~

OpenCost 能回答的关键问题：每个 Namespace 每天花多少钱？哪个 Deployment 是成本大头？Spot vs On-Demand 各占多少比例？数据传输费用多少？

---

## 六、第五层优化：存储与网络成本

### 6.1 存储成本优化

~~~yaml
# 不同场景使用不同存储类型
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: low-cost-retain
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3          # GP3 比 GP2 便宜 20%，IOPS 更高
  fsType: ext4
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer  # 延迟绑定，减少跨 AZ 费用
---
# 临时数据用便宜存储
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: cheap-temp
provisioner: kubernetes.io/aws-ebs
parameters:
  type: st1           # 吞吐优化 HDD，比 SSD 便宜 75%
  fsType: ext4
reclaimPolicy: Delete
~~~

### 6.2 网络成本控制

跨可用区和跨区域的流量是隐形杀手。关键优化策略：

1. 使用 `WaitForFirstConsumer` 延迟绑定，确保 PVC 和 Pod 在同一 AZ
2. 同一 AZ 内的 Pod 优先调度（Topology Spread）
3. 压缩 Service Mesh 的 mTLS 流量（减少 15%-20% 网络开销）

---

## 七、生产环境 5 大避坑指南

### 坑位 1：VPA 和 HPA 同时基于 CPU 伸缩

**现象**：Pod 被反复驱逐，服务不稳定。

**根因**：VPA 增大 CPU Request → HPA 检测到利用率下降 → HPA 缩容 → VPA 又增大 → 死循环。

**解决**：VPA 管基础资源，HPA 只管业务指标（QPS/延迟）。

### 坑位 2：Karpenter Consolidation 误杀关键 Pod

**现象**：Consolidation 主动替换节点时，关键服务被短暂中断。

**解决**：

~~~yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-server-pdb
spec:
  minAvailable: "50%"
  selector:
    matchLabels:
      app: api-server
~~~

### 坑位 3：Spot 实例大规模回收导致雪崩

**现象**：某个可用区的 Spot 价格飙升，数百个 Pod 同时被驱逐。

**解决**：强制多 AZ 分散 + 合理设置 PDB。

### 坑位 4：ResourceQuota 阻止 VPA 缩减

**现象**：VPA 推荐降低 Request，但 Pod 无法更新。

**解决**：定期审查 ResourceQuota，移除不必要的 `min` 约束。

### 坑位 5：监控盲区——只看节点不看 Pod

**现象**：节点利用率看起来正常，但大量 Pod 在浪费资源。

**解决**：部署 OpenCost + kube-state-metrics，建立 Pod 级别的成本视图。

---

## 八、优化效果总结与落地路线图

| 优化层级 | 措施 | 预期节省 | 实施难度 | 建议顺序 |
| --- | --- | --- | --- | --- |
| **L1** | Right-Sizing (VPA) | 20%-40% | 低 | 第 1 周 |
| **L2** | Karpenter + Spot | 20%-30% | 中 | 第 2 周 |
| **L3** | 非生产环境定时开关 | 10%-20% | 低 | 第 1 周 |
| **L3** | 优先级调度 | 5%-10% | 中 | 第 3 周 |
| **L4** | FinOps 监控 | 持续优化 | 中 | 第 1-2 周 |
| **L5** | 存储网络优化 | 5%-15% | 高 | 第 4 周 |

**综合预期：通过 4 周实施，可降低 40%-60% 的 Kubernetes 云账单。**

落地顺序：

~~~
Week 1: 部署 VPA(Off 模式) + OpenCost + 非生产环境 CronJob
        ↓ 收集 1 周推荐数据
Week 2: 启用 VPA(Auto) + 部署 Karpenter + Spot 混合策略
        ↓ 观察 1 周稳定性
Week 3: 配置 PriorityClass + PDB + 拓扑分散
        ↓
Week 4: 存储优化 + 网络优化 + Prometheus 成本告警
~~~

---

## 九、总结

Kubernetes 成本优化不是一次性的任务，而是一个**持续运转的 FinOps 实践**。核心原则三句话：

1. **测量一切**：没有监控就没有优化。部署 OpenCost + Prometheus，让每一分钱都可追溯
2. **自动化决策**：用 VPA 替代人工估算，用 Karpenter 替代手动运维，让机器替你省钱
3. **渐进式落地**：从 VPA Off 模式开始评估，逐步切换到 Auto；先 Spot 补充再 Spot 为主
