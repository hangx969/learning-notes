---
title: "蓝绿部署还是金丝雀发布？搞懂这两招，K8s生产发布再也不翻车"
source: "https://mp.weixin.qq.com/s/RdOXw-6gcFWoXam7KU2EcA"
author:
  - "[[WAKEUP技术]]"
published:
created: 2026-06-05
description: "2025年某电商平台双十一前夕，研发团队将核心订单服务从 v1.2 升级到 v1.3。没有灰度，没有流量切分，kubectl apply 一键推送，全量上线。"
tags:
  - "clippings"
---
WAKEUP技术 *2026年5月28日 18:19*

> 一次上线把 30% 用户打崩了，你以为是代码质量问题，其实是发布策略没选对。

## 背景：一次代价惨重的"全量发布"

2025年某电商平台双十一前夕，研发团队将核心订单服务从 v1.2 升级到 v1.3。没有灰度，没有流量切分，kubectl apply 一键推送，全量上线。

上线10分钟后，Prometheus 告警炸了——新版本中一个未被测试覆盖的边界条件在真实流量下大量触发，错误率飙升到 45%，订单服务基本瘫痪。

紧急回滚花了 8 分钟，但这 8 分钟损失的交易额超过百万。

这个故事揭示了一个严酷现实： **在 Kubernetes 上能发布，不代表你会"安全发布"。** 蓝绿部署和金丝雀发布，才是生产环境的两把保命锁。

---

## 一、发布策略全景：为什么需要渐进式发布？

Kubernetes 原生提供了几种发布策略：

| 策略 | 速度 | 风险 | 适用场景 |
| --- | --- | --- | --- |
| Recreate | 最快 | 极高（停机） | 开发/测试环境 |
| RollingUpdate | 快 | 中（影响扩散慢） | 默认选择 |
| **Blue-Green** | 秒级切换 | 低（独立环境） | 无损切换、快速回滚 |
| **Canary** | 慢（渐进） | 最低（影响范围可控） | 高风险变更、A/B测试 |

RollingUpdate 是 K8s 默认策略，但它的问题在于：新旧版本 Pod 同时存在，流量无法精确控制，一旦出问题，影响范围取决于滚动进度。

蓝绿和金丝雀则是真正的 **生产级发布武器** 。

---

## 二、蓝绿部署：秒级切换的无损发布

### 核心思想

蓝绿部署维护两套完全相同的生产环境：

- • **Blue（蓝色）** ：当前线上版本，承载 100% 流量
- • **Green（绿色）** ：新版本，部署完成后接受预热测试

切换时，只需将 Service 的 selector 从蓝色改指绿色，流量立刻 100% 切换。回滚也只需反向操作，整个过程几秒内完成。

```
用户流量
    │
    ▼
  Service  ◄── selector: version=blue (切换前)
    │
    ▼
[Blue Pods: v1.2] x5    [Green Pods: v1.3] x5 (已就绪，无流量)
```

### 实战配置

**Blue Deployment（当前线上版本）**

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service-blue
  namespace: production
  labels:
    app: order-service
    version: blue
spec:
  replicas: 5
  selector:
    matchLabels:
      app: order-service
      version: blue
  template:
    metadata:
      labels:
        app: order-service
        version: blue
    spec:
      containers:
      - name: order-service
        image: registry.example.com/order-service:v1.2
        ports:
        - containerPort: 8080
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            cpu: "200m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
```

**Green Deployment（新版本，待上线）**

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service-green
  namespace: production
  labels:
    app: order-service
    version: green
spec:
  replicas: 5
  selector:
    matchLabels:
      app: order-service
      version: green
  template:
    metadata:
      labels:
        app: order-service
        version: green
    spec:
      containers:
      - name: order-service
        image: registry.example.com/order-service:v1.3
        ports:
        - containerPort: 8080
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            cpu: "200m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
```

**Service（流量入口，通过 selector 控制流量去向）**

```
apiVersion: v1
kind: Service
metadata:
  name: order-service
  namespace: production
spec:
  selector:
    app: order-service
    version: blue    # 只需修改此处即可切换流量
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
```

### 蓝绿切换操作步骤

```
# 1. 部署 Green 版本（不影响线上）
kubectl apply -f order-service-green.yaml

# 2. 等待 Green 版本所有 Pod 就绪
kubectl rollout status deployment/order-service-green -n production

# 3. 验证 Green 版本（可通过内部直接访问 green service 测试）
kubectl port-forward deployment/order-service-green 8080:8080 -n production
curl http://localhost:8080/health

# 4. 执行流量切换（核心操作，仅需修改 selector）
kubectl patch service order-service -n production \
  -p '{"spec":{"selector":{"version":"green"}}}'

# 5. 观察监控，确认无异常（建议观察 5-10 分钟）
# 如需回滚：
kubectl patch service order-service -n production \
  -p '{"spec":{"selector":{"version":"blue"}}}'

# 6. 确认无误后，下线 Blue 版本（节省资源）
kubectl scale deployment/order-service-blue --replicas=0 -n production
```

### 蓝绿部署的适用场景与局限

**✅ 适用场景：**

- • 需要零停机时间切换
- • 版本差异较大，需要完整环境验证
- • 有严格回滚时间要求（SLA < 1分钟）

**⚠️ 局限性：**

- • 资源消耗翻倍（需同时维护两套完整环境）
- • 数据库 Schema 变更需要额外的兼容性处理
- • 无法对真实用户流量做渐进式验证

---

## 三、金丝雀发布：精细流量控制的渐进式上线

### 核心思想

金丝雀发布源自矿工携带金丝雀进入矿井探测毒气的古老实践。在软件发布中，它意味着：先让少数用户使用新版本，观察指标正常后，再逐步扩大范围。

```
用户流量（100%）
        │
        ▼
   Ingress/服务网格
    ├── 90% ──► [Stable Pods: v1.2] x9
    └── 10% ──► [Canary Pods: v1.3] x1
```

### 方案一：基于 Kubernetes 原生的简易金丝雀

通过调整 Deployment 副本比例，可以实现粗粒度的流量控制（依赖随机调度，不够精确）：

```
# stable deployment: 9 replicas → ~90% 流量
# canary deployment: 1 replica  → ~10% 流量
# 二者共享同一个 Service selector: app=order-service
```
```
# stable-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service-stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: order-service
      track: stable
  template:
    metadata:
      labels:
        app: order-service
        track: stable
    spec:
      containers:
      - name: order-service
        image: registry.example.com/order-service:v1.2
---
# canary-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: order-service
      track: canary
  template:
    metadata:
      labels:
        app: order-service
        track: canary
    spec:
      containers:
      - name: order-service
        image: registry.example.com/order-service:v1.3
```
```
# 共享 Service，不区分 track
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  selector:
    app: order-service    # 同时匹配 stable 和 canary
  ports:
  - port: 80
    targetPort: 8080
```

### 方案二：基于 Nginx Ingress 的精确流量切分（推荐）

Nginx Ingress 通过 Annotation 支持基于权重、Header、Cookie 的精细流量控制：

```
# 稳定版 Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: order-service-stable
  namespace: production
spec:
  ingressClassName: nginx
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: order-service-stable
            port:
              number: 80
---
# 金丝雀 Ingress（核心配置）
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: order-service-canary
  namespace: production
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    # 方式一：基于权重（10% 流量进入金丝雀）
    nginx.ingress.kubernetes.io/canary-weight: "10"
    # 方式二：基于 Header（特定用户强制走金丝雀）
    # nginx.ingress.kubernetes.io/canary-by-header: "X-Canary"
    # nginx.ingress.kubernetes.io/canary-by-header-value: "always"
    # 方式三：基于 Cookie（灰度用户标记）
    # nginx.ingress.kubernetes.io/canary-by-cookie: "canary_user"
spec:
  ingressClassName: nginx
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: order-service-canary
            port:
              number: 80
```

**分阶段调整流量权重脚本：**

```
#!/bin/bash
# canary-progress.sh：渐进式提升金丝雀流量比例

NAMESPACE="production"
INGRESS="order-service-canary"

for weight in 10 25 50 75 100; do
  echo ">>> 设置金丝雀流量比例: ${weight}%"
  kubectl annotate ingress ${INGRESS} -n ${NAMESPACE} \
    nginx.ingress.kubernetes.io/canary-weight="${weight}" \
    --overwrite

  echo ">>> 等待 5 分钟，观察监控指标..."
  sleep 300

  # 检查错误率（需要配合 Prometheus）
  ERROR_RATE=$(curl -s "http://prometheus:9090/api/v1/query" \
    --data-urlencode 'query=rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])' \
    | jq '.data.result[0].value[1]' | tr -d '"')

  echo ">>> 当前错误率: ${ERROR_RATE}"

  # 如果错误率超过 1%，自动回滚
  if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
    echo "❌ 错误率超标，自动回滚至 0%！"
    kubectl annotate ingress ${INGRESS} -n ${NAMESPACE} \
      nginx.ingress.kubernetes.io/canary-weight="0" \
      --overwrite
    exit 1
  fi

  echo "✅ 指标正常，继续推进..."
done

echo "🎉 金丝雀发布完成，全量切换！"
```

### 方案三：使用 Argo Rollouts（企业级推荐）

Argo Rollouts <sup>[1]</sup> 是专门为渐进式发布设计的 CRD，支持自动分析、Metric 门控、与 ArgoCD 深度集成：

```
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: order-service
  namespace: production
spec:
  replicas: 10
  strategy:
    canary:
      # 金丝雀发布步骤
      steps:
      - setWeight: 10           # Step 1: 切 10% 流量
      - pause: {duration: 5m}   # 暂停5分钟，人工/自动分析
      - setWeight: 25
      - pause: {duration: 10m}
      - setWeight: 50
      - pause: {}               # 无时限暂停，等待人工确认
      - setWeight: 75
      - pause: {duration: 5m}
      - setWeight: 100          # 全量
      # 自动分析配置
      analysis:
        templates:
        - templateName: success-rate
        startingStep: 2
        args:
        - name: service-name
          value: order-service-canary
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      containers:
      - name: order-service
        image: registry.example.com/order-service:v1.3
---
# 分析模板：基于 Prometheus 指标自动判断是否继续
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
  - name: service-name
  metrics:
  - name: success-rate
    interval: 2m
    # 成功率低于 99% 则自动回滚
    successCondition: result[0] >= 0.99
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus.monitoring:9090
        query: |
          sum(rate(http_requests_total{service="{{args.service-name}}",status!~"5.."}[5m]))
          /
          sum(rate(http_requests_total{service="{{args.service-name}}"}[5m]))
```

**Argo Rollouts 操作命令：**

```
# 安装 Argo Rollouts
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts \
  -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# 安装 kubectl 插件
brew install argoproj/tap/kubectl-argo-rollouts  # macOS
# 或下载二进制 kubectl-argo-rollouts-linux-amd64

# 查看 Rollout 状态
kubectl argo rollouts get rollout order-service -n production --watch

# 手动推进到下一步（暂停状态时）
kubectl argo rollouts promote order-service -n production

# 中止发布并回滚
kubectl argo rollouts abort order-service -n production

# 查看发布历史
kubectl argo rollouts history rollout order-service -n production
```

---

## 四、生产环境关键注意事项

### 1\. 数据库兼容性是最大的坑

蓝绿/金丝雀发布过程中，新旧版本会同时运行并访问同一数据库。必须确保：

```
-- ❌ 错误做法：直接删除列（旧版本 Pod 会报错）
ALTER TABLE orders DROP COLUMN old_field;

-- ✅ 正确做法（三步走）：
-- Step 1（发布前）：新版本兼容旧列，同时写入新列
-- Step 2（发布后，清零旧版本）：新版本只读新列
-- Step 3（下次发布）：删除旧列
ALTER TABLE orders ADD COLUMN new_field VARCHAR(255);
```

**推荐工具：** Flyway、Liquibase 管理 Schema 变更，配合 expand/contract 模式。

### 2\. 健康检查必须完善

蓝绿切换和金丝雀晋级必须依赖可靠的健康检查：

```
livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 5
  failureThreshold: 3

# 优雅停机（蓝绿切换后，旧 Pod 处理完进行中的请求）
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 15"]
terminationGracePeriodSeconds: 60
```

### 3\. 监控告警是发布决策的依据

金丝雀发布的核心价值在于"可观测"。必须在发布前建立告警基线：

```
# Prometheus 告警规则示例
groups:
- name: canary-release
  rules:
  - alert: CanaryHighErrorRate
    expr: |
      sum(rate(http_requests_total{service="order-service-canary", status=~"5.."}[5m]))
      /
      sum(rate(http_requests_total{service="order-service-canary"}[5m])) > 0.01
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "金丝雀版本错误率超标，建议回滚"
      description: "金丝雀服务 5xx 错误率已达 {{ $value | humanizePercentage }}"

  - alert: CanaryHighLatency
    expr: |
      histogram_quantile(0.99, 
        sum(rate(http_request_duration_seconds_bucket{service="order-service-canary"}[5m])) by (le)
      ) > 0.5
    for: 3m
    labels:
      severity: warning
    annotations:
      summary: "金丝雀版本 P99 延迟过高"
```

### 4\. 有状态服务的特殊处理

对于 StatefulSet（如 Redis、Kafka 等），蓝绿部署需要额外考虑：

- • 持久化数据的兼容性（PVC 不能直接切换）
- • 有状态服务推荐使用滚动更新或专门的 Operator 管理
- • 不建议对有状态服务直接使用蓝绿部署

### 5\. 金丝雀发布的"安全快门"清单

发布前务必确认：

```
# 发布前检查清单
echo "=== 金丝雀发布前置检查 ==="

# 1. 确认 readinessProbe 配置正确
kubectl get deploy order-service-canary -o jsonpath='{.spec.template.spec.containers[0].readinessProbe}' | jq .

# 2. 确认资源限制已设置
kubectl get deploy order-service-canary -o jsonpath='{.spec.template.spec.containers[0].resources}' | jq .

# 3. 确认 PodDisruptionBudget 存在（保障滚动更新期间可用性）
kubectl get pdb -n production

# 4. 确认监控面板已就绪
echo "请打开 Grafana 并保持金丝雀对比面板可见"

# 5. 确认回滚命令已准备就绪（回滚操作不应超过1分钟）
echo "回滚命令备用：kubectl annotate ingress order-service-canary nginx.ingress.kubernetes.io/canary-weight=0 --overwrite"
```

---

## 五、蓝绿 vs 金丝雀：该怎么选？

| 维度 | 蓝绿部署 | 金丝雀发布 |
| --- | --- | --- |
| 回滚速度 | ⚡ 秒级（Service selector 切换） | 🐢 分钟级（逐步降权重） |
| 资源消耗 | 💸 高（2倍资源） | 💰 低（可少量 Canary Pod） |
| 流量控制精度 | ❌ 非此即彼（100% 切换） | ✅ 精细（1%-100% 任意） |
| 数据库兼容性风险 | 中（瞬间切换，时间窗口短） | 低（长时间双版本，需仔细设计） |
| 配置复杂度 | 低（原生 Service 支持） | 中-高（需要 Ingress 或 Rollouts） |
| 最适合场景 | 无状态服务、对回滚时间敏感 | 高风险变更、新功能 A/B 测试 |

**选型决策树：**

```
是否需要 < 1 分钟回滚？
├── 是 → 蓝绿部署（但要接受 2x 资源消耗）
└── 否
    ├── 变更风险高 / 需要 A/B 测试？
    │   ├── 是 → 金丝雀发布（Nginx Ingress 或 Argo Rollouts）
    │   └── 否 → RollingUpdate（资源受限场景）
    └── 有自动化需求 / 大型团队？
        └── Argo Rollouts（企业级首选）
```

---

## 总结

蓝绿部署和金丝雀发布代表了两种不同的风险管理哲学：

- • **蓝绿** ：用空间换时间，以 2x 资源成本换取秒级切换能力，适合强调"即时回滚"的关键服务。
- • **金丝雀** ：用时间换安全，以渐进式流量控制最小化影响范围，适合高风险变更和 A/B 测试场景。

两者都需要可靠的健康检查、完善的监控告警和数据库兼容性设计作为支撑。

真正的生产发布成熟度不在于选哪一个，而在于 **将发布决策与可观测性数据深度绑定** ——让数据说话，让系统自动判断是推进还是回滚。

从一次手动 kubectl patch 开始，到 Argo Rollouts 自动分析驱动的全自动渐进式发布，这条路值得每个 K8s 团队走一遍。

---

> 作者：WAKE UP技术 | 专注云原生与 K8s 生产实践  
> 个人主页：https://lweiqiang.xyz

#### 引用链接

`[1]` Argo Rollouts: *https://argoproj.github.io/argo-rollouts/*

**微信扫一扫赞赏作者**

继续滑动看下一个

WAKE UP技术

向上滑动看下一个