---
title: "K8s 发布策略：蓝绿部署与金丝雀发布实战"
source: "https://mp.weixin.qq.com/s/RdOXw-6gcFWoXam7KU2EcA"
created: 2026-06-06
tags:
  - kubernetes
  - CICD
  - blue-green
  - canary
  - argo-rollouts
---

# K8s 发布策略：蓝绿部署与金丝雀发布实战

## 一、发布策略全景对比

| 策略 | 速度 | 风险 | 适用场景 |
|------|------|------|----------|
| Recreate | 最快 | 极高（停机） | 开发/测试环境 |
| RollingUpdate | 快 | 中（影响扩散慢） | 默认选择 |
| **Blue-Green** | 秒级切换 | 低（独立环境） | 无损切换、快速回滚 |
| **Canary** | 慢（渐进） | 最低（影响范围可控） | 高风险变更、A/B测试 |

RollingUpdate 是 K8s 默认策略，问题在于：新旧版本 Pod 同时存在，流量无法精确控制，一旦出问题影响范围取决于滚动进度。

## 二、蓝绿部署：秒级切换的无损发布

### 核心思想

维护两套完整生产环境（Blue 当前版本 / Green 新版本），切换时只需修改 Service 的 selector，流量立即 100% 切换。回滚同样秒级。

### 实战配置

```yaml
# Blue Deployment（当前线上版本）
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service-blue
  namespace: production
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
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests: { cpu: "200m", memory: "256Mi" }
          limits: { cpu: "500m", memory: "512Mi" }
---
# Green Deployment（新版本，部署后无流量）
# 结构同上，version: green, image: v1.3
---
# Service（流量入口，通过 selector 控制流向）
apiVersion: v1
kind: Service
metadata:
  name: order-service
  namespace: production
spec:
  selector:
    app: order-service
    version: blue    # ← 只需修改此处即可切换流量
  ports:
  - port: 80
    targetPort: 8080
```

### 切换操作步骤

```bash
# 1. 部署 Green 版本（不影响线上）
kubectl apply -f order-service-green.yaml

# 2. 等待 Green 就绪
kubectl rollout status deployment/order-service-green -n production

# 3. 验证 Green（内部直连测试）
kubectl port-forward deployment/order-service-green 8080:8080 -n production

# 4. 执行流量切换（核心操作，秒级完成）
kubectl patch service order-service -n production \
  -p '{"spec":{"selector":{"version":"green"}}}'

# 5. 观察 5-10 分钟，如需回滚：
kubectl patch service order-service -n production \
  -p '{"spec":{"selector":{"version":"blue"}}}'

# 6. 确认无误后下线 Blue（节省资源）
kubectl scale deployment/order-service-blue --replicas=0 -n production
```

### 适用场景与局限

- ✅ 零停机切换、版本差异大需完整验证、SLA 回滚 < 1 分钟
- ⚠️ 资源消耗翻倍、数据库 Schema 变更需兼容性处理、无法对真实流量做渐进式验证

## 三、金丝雀发布：精细流量控制的渐进式上线

### 方案一：K8s 原生（粗粒度）

通过调整 Deployment 副本比例控制流量，依赖随机调度，不够精确：

```yaml
# stable: 9 replicas → ~90% 流量
# canary: 1 replica  → ~10% 流量
# 二者共享同一个 Service selector: app=order-service
```

### 方案二：Nginx Ingress Annotation（推荐）

通过 Annotation 实现基于权重/Header/Cookie 的精细流量控制：

```yaml
# 稳定版 Ingress（正常配置）
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: order-service-stable
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
            port: { number: 80 }
---
# 金丝雀 Ingress（核心配置）
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: order-service-canary
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
            port: { number: 80 }
```

**渐进式流量调整脚本**（配合 Prometheus 自动回滚）：

```bash
#!/bin/bash
# canary-progress.sh：渐进式提升金丝雀流量比例
NAMESPACE="production"
INGRESS="order-service-canary"

for weight in 10 25 50 75 100; do
  echo ">>> 设置金丝雀流量比例: ${weight}%"
  kubectl annotate ingress ${INGRESS} -n ${NAMESPACE} \
    nginx.ingress.kubernetes.io/canary-weight="${weight}" --overwrite

  echo ">>> 等待 5 分钟，观察监控指标..."
  sleep 300

  # 检查错误率（需配合 Prometheus）
  ERROR_RATE=$(curl -s "http://prometheus:9090/api/v1/query" \
    --data-urlencode 'query=rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])' \
    | jq '.data.result[0].value[1]' | tr -d '"')

  if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
    echo "❌ 错误率超标，自动回滚至 0%！"
    kubectl annotate ingress ${INGRESS} -n ${NAMESPACE} \
      nginx.ingress.kubernetes.io/canary-weight="0" --overwrite
    exit 1
  fi
  echo "✅ 指标正常，继续推进..."
done
echo "🎉 金丝雀发布完成，全量切换！"
```

### 方案三：Argo Rollouts（企业级推荐）

专为渐进式发布设计的 CRD，支持自动分析、Metric 门控、与 ArgoCD 深度集成：

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: order-service
  namespace: production
spec:
  replicas: 10
  strategy:
    canary:
      steps:
      - setWeight: 10           # Step 1: 切 10% 流量
      - pause: {duration: 5m}   # 暂停5分钟，自动分析
      - setWeight: 25
      - pause: {duration: 10m}
      - setWeight: 50
      - pause: {}               # 无时限暂停，等待人工确认
      - setWeight: 75
      - pause: {duration: 5m}
      - setWeight: 100
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
    successCondition: result[0] >= 0.99  # 成功率低于 99% 则自动回滚
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus.monitoring:9090
        query: |
          sum(rate(http_requests_total{service="{{args.service-name}}",status!~"5.."}[5m]))
          /
          sum(rate(http_requests_total{service="{{args.service-name}}"}[5m]))
```

**Argo Rollouts 常用操作**：

```bash
# 安装
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts \
  -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# 查看 Rollout 状态
kubectl argo rollouts get rollout order-service -n production --watch

# 手动推进到下一步（暂停状态时）
kubectl argo rollouts promote order-service -n production

# 中止发布并回滚
kubectl argo rollouts abort order-service -n production
```

## 四、生产关键注意事项

### 1. 数据库兼容性是最大的坑

新旧版本同时运行期间访问同一数据库，必须保证 Schema 兼容：

```sql
-- ❌ 错误：直接删除列（旧版本 Pod 会报错）
ALTER TABLE orders DROP COLUMN old_field;

-- ✅ 正确：三步 expand/contract 模式
-- Step 1（发布前）：新版本兼容旧列，同时写入新列
-- Step 2（清零旧版本后）：新版本只读新列
-- Step 3（下次发布）：删除旧列
```

推荐工具：Flyway、Liquibase 管理 Schema 变更。

### 2. 健康检查 + 优雅停机

```yaml
readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 5
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 15"]  # 蓝绿切换后让旧 Pod 处理完进行中的请求
terminationGracePeriodSeconds: 60
```

### 3. Prometheus 金丝雀告警规则

```yaml
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
  - alert: CanaryHighLatency
    expr: |
      histogram_quantile(0.99,
        sum(rate(http_request_duration_seconds_bucket{service="order-service-canary"}[5m])) by (le)
      ) > 0.5
    for: 3m
    labels:
      severity: warning
```

### 4. 有状态服务不建议蓝绿部署

StatefulSet（Redis、Kafka 等）的 PVC 不能直接切换，推荐滚动更新或专门的 Operator 管理。

### 5. 金丝雀发布前置检查清单

```bash
# 1. 确认 readinessProbe 配置正确
# 2. 确认资源限制已设置
# 3. 确认 PDB 存在（保障滚动期间可用性）
kubectl get pdb -n production
# 4. 确认监控面板已就绪
# 5. 确认回滚命令已准备（回滚不应超过1分钟）
```

## 五、蓝绿 vs 金丝雀选型决策树

| 维度 | 蓝绿部署 | 金丝雀发布 |
|------|----------|------------|
| 回滚速度 | ⚡ 秒级 | 🐢 分钟级 |
| 资源消耗 | 💸 高（2x） | 💰 低 |
| 流量控制精度 | ❌ 非此即彼 | ✅ 1%-100% 任意 |
| 配置复杂度 | 低（原生 Service） | 中-高（Ingress/Rollouts） |
| 最适合场景 | 无状态、对回滚时间敏感 | 高风险变更、A/B 测试 |

```
是否需要 < 1 分钟回滚？
├── 是 → 蓝绿部署（接受 2x 资源消耗）
└── 否
    ├── 变更风险高 / 需要 A/B 测试？
    │   ├── 是 → 金丝雀发布（Nginx Ingress 或 Argo Rollouts）
    │   └── 否 → RollingUpdate（资源受限场景）
    └── 有自动化需求 / 大型团队？
        └── Argo Rollouts（企业级首选）
```
