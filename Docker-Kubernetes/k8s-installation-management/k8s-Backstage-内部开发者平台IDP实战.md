---
title: "K8s 平台工程实战：用 Backstage 打造一站式内部开发者平台"
source: "https://mp.weixin.qq.com/s/MY4_lenKLHmNhhgIZFYvKw"
created: 2026-06-28
tags:
  - kubernetes
  - platform-engineering
  - backstage
  - idp
---

# K8s 平台工程实战：Backstage IDP

## 一、为什么需要 IDP

"帮我建个测试环境呗，要一个 namespace，配好 MySQL 和 Redis，再加个 Ingress。"

20 分钟后，手动创建了 Namespace、写了 Deployment、申请了 PV、配了 Service、调了 Ingress…… 然后发现忘记开 NetworkPolicy。

当团队有 10 个开发小组、每个迭代都要申请新环境时，运维完全陷在"YAML 流水线"里——不断复制粘贴模板、手动改参数、祈祷别写错缩进。

**Kubernetes 太强大了，但也太复杂了。** CNCF 2026 年报告显示：80% 的企业正在或已经搭建内部开发者平台（IDP）。

### 从 DevOps 到 Platform Engineering

| 模式 | 开发者体验 |
|------|-----------|
| **原始 DevOps** | 开发者 = K8s 管理员（要懂 Deployment/Service/Ingress/ConfigMap/Secret/PV/PVC...） |
| **平台工程** | 点击"创建服务" → 填入名字 → 自动生成全套资源 → 5 分钟拿到可访问环境 |

### IDP 要解决的核心问题

1. **认知负荷过载**：K8s 有 50+ 种资源类型，没人能全记住
2. **环境申请缓慢**：靠工单（TicketOps）等运维手动建，动辄数小时
3. **配置碎片化**：文档存在 Wiki/飞书/Confluence/本地 markdown 里，版本混乱
4. **合规不可控**：谁建了什么、用了什么镜像、开了什么端口——没人知道
5. **重复造轮子**：每个新服务都要重新配 CI/CD、监控、日志、告警

## 二、Backstage 是什么

Backstage 是 Spotify 开源的一体化开发者门户（Developer Portal），被 Netflix、American Airlines、Zalando、Expedia Group 等数百家企业采用。核心由一个 **Software Catalog（软件目录）** 和一套 **插件生态系统** 组成。

**核心能力：**

- **Software Catalog**：所有服务、API、资源库的统一注册中心
- **Software Templates**：一键创建标准化服务的脚手架模板
- **TechDocs**：Markdown → 文档站点，代码即文档
- **Kubernetes 插件**：在 Backstage 中直接查看 Pod 状态、日志、资源使用
- **150+ 插件生态**：ArgoCD、GitHub Actions、PagerDuty、Prometheus、Grafana、Jira……

一句话总结：**Backstage 是开发者的"Apple Store"——所有工具、服务、文档的入口。**

## 三、架构速览

```
┌──────────────────────────────────────────────┐
│         Backstage Frontend (React)           │
│  ┌───────┐ ┌────────┐ ┌───────┐ ┌─────────┐ │
│  │Catalog│ │TechDocs│ │K8s    │ │Templates│ │
│  └───────┘ └────────┘ └───────┘ └─────────┘ │
└──────────────────┬───────────────────────────┘
                   │ REST API
┌──────────────────▼───────────────────────────┐
│         Backstage Backend (Node.js)          │
│  ┌────────┐ ┌─────────┐ ┌──────────────────┐│
│  │Catalog │ │Scaffolder│ │Plugin Manager    ││
│  │Engine  │ │Engine    │ │                  ││
│  └────────┘ └─────────┘ └──────────────────┘│
│  ┌────────┐ ┌───────┐   ┌──────────────────┐│
│  │Auth    │ │Search │   │TechDocs Engine   ││
│  └────────┘ └───────┘   └──────────────────┘│
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│       PostgreSQL (Catalog Database)          │
└──────────────────────────────────────────────┘
```

- **Frontend**：React 单页应用，通过插件系统扩展 UI
- **Backend**：Node.js 服务，管理 Catalog 数据、模板脚手架、搜索索引
- **PostgreSQL**：持久化软件目录数据

## 四、生产环境部署实战

### 4.1 环境准备

```bash
# 集群要求：K8s v1.27+
kubectl create namespace backstage

# 安装 PostgreSQL（生产环境建议用云厂商托管版）
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: backstage-postgres
  namespace: backstage
type: Opaque
stringData:
  POSTGRES_USER: backstage
  POSTGRES_PASSWORD: $(openssl rand -base64 32)
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: backstage
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: backstage-postgres
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: backstage-postgres
              key: POSTGRES_PASSWORD
        - name: POSTGRES_DB
          value: backstage
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: backstage
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
EOF
```

### 4.2 app-config.yaml 核心配置

```yaml
app:
  title: 开发者平台
  baseUrl: https://backstage.your-domain.com

backend:
  baseUrl: https://backstage.your-domain.com
  listen:
    port: 7007
  database:
    client: pg
    connection:
      host: ${POSTGRES_HOST}
      port: ${POSTGRES_PORT}
      user: ${POSTGRES_USER}
      password: ${POSTGRES_PASSWORD}

auth:
  providers:
    github:
      development:
        clientId: ${GITHUB_CLIENT_ID}
        clientSecret: ${GITHUB_CLIENT_SECRET}

catalog:
  import:
    entityFilename: catalog-info.yaml
    pullRequestBranchName: backstage-integration
  rules:
    - allow: [Component, System, API, Resource, Location]

kubernetes:
  serviceLocatorMethod:
    type: 'multiTenant'
  clusterLocatorMethods:
    - type: 'config'
      clusters:
        - name: 'prod-cluster'
          url: 'https://k8s-api.prod.example.com'
          authProvider: 'serviceAccount'
          serviceAccountToken: ${K8S_SA_TOKEN}

techdocs:
  builder: 'local'
  generator:
    runIn: 'docker'
  publisher:
    type: 'local'
```

### 4.3 K8s 部署（Deployment + Service + Ingress）

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backstage
  namespace: backstage
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backstage
  template:
    metadata:
      labels:
        app: backstage
    spec:
      containers:
      - name: backstage
        image: your-registry/backstage:v1.0.0
        ports:
        - containerPort: 7007
        env:
        - name: POSTGRES_HOST
          value: postgres.backstage.svc.cluster.local
        - name: POSTGRES_PORT
          value: "5432"
        # ... Secret 引用省略
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 2Gi
        livenessProbe:
          httpGet:
            path: /healthcheck
            port: 7007
          initialDelaySeconds: 30
        readinessProbe:
          httpGet:
            path: /healthcheck
            port: 7007
          initialDelaySeconds: 10
      serviceAccountName: backstage
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: backstage
  namespace: backstage
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - backstage.your-domain.com
    secretName: backstage-tls
  rules:
  - host: backstage.your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backstage
            port:
              number: 7007
```

### 4.4 RBAC — ServiceAccount 只读权限

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: backstage
  namespace: backstage
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: backstage-reader
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "namespaces"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets", "statefulsets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: backstage-reader
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: backstage-reader
subjects:
- kind: ServiceAccount
  name: backstage
  namespace: backstage
```

## 五、Software Catalog：一切皆实体

所有东西都是一个"实体"（Entity），用 YAML 文件定义。

### 注册微服务（catalog-info.yaml）

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: payment-service
  description: 支付服务 - 处理订单支付与退款
  annotations:
    github.com/project-slug: your-org/payment-service
    backstage.io/kubernetes-id: payment-service
    backstage.io/techdocs-ref: dir:.
  tags: [java, spring-boot, payment]
spec:
  type: service
  lifecycle: production
  owner: payment-team
  system: ecommerce-platform
  providesApis: [payment-api]
  dependsOn:
    - component:order-service
    - resource:payment-db
```

### 定义 API 和资源

```yaml
apiVersion: backstage.io/v1alpha1
kind: API
metadata:
  name: payment-api
spec:
  type: openapi
  lifecycle: production
  owner: payment-team
  definition:
    $text: https://payment-api.your-domain.com/v3/api-docs
---
apiVersion: backstage.io/v1alpha1
kind: Resource
metadata:
  name: payment-db
  description: 支付数据库 (PostgreSQL)
spec:
  type: database
  owner: payment-team
  system: ecommerce-platform
```

## 六、Software Templates：一键创建服务

最有价值的功能——**让开发者通过表单创建标准化服务**。

模板定义 `template.yaml` 包含：

1. **parameters**：定义表单字段（服务名称、所属团队、Java 版本、端口、副本数、CPU/内存等）
2. **steps**：执行流程（获取模板 → 发布到 GitHub → 注册到 Catalog）
3. **skeleton/**：骨架文件（catalog-info.yaml + GitHub Actions CI + Dockerfile + K8s manifests + 源码模板）

执行流程：开发者在 Backstage 页面点击"Create" → 填写表单 → Backstage 自动创建 GitHub 仓库、写入代码骨架、配置 CI/CD、注册到 Catalog。**从点击到可部署的代码仓库，不到 2 分钟。**

## 七、TechDocs：代码即文档

在 `catalog-info.yaml` 里加一行注解：

```yaml
annotations:
  backstage.io/techdocs-ref: dir:.
```

然后在仓库根目录创建 `docs/` 文件夹，写 Markdown。Backstage 自动渲染成漂亮的文档站点（内置搜索、导航、Mermaid 图表支持）。

## 八、关键插件推荐

| 插件 | 功能 | 推荐指数 |
|------|------|:--------:|
| **Kubernetes** | 查看 Pod 状态、CPU/内存使用、日志 | ⭐⭐⭐⭐⭐ |
| **ArgoCD** | GitOps 部署状态，每服务的同步健康度 | ⭐⭐⭐⭐⭐ |
| **Prometheus** | 服务告警状态、健康分数 | ⭐⭐⭐⭐ |
| **GitHub Actions** | CI/CD 工作流状态、构建历史 | ⭐⭐⭐⭐ |
| **Snyk** | 代码安全漏洞扫描 | ⭐⭐⭐⭐ |
| **PagerDuty** | On-call 排班、事件管理 | ⭐⭐⭐ |
| **Tech Radar** | 技术雷达，指导技术选型 | ⭐⭐⭐ |

## 九、生产环境 5 大注意事项

### 9.1 认证对接

支持 GitHub/GitLab/Okta/Azure AD/Google 等 OIDC 提供商。**不要用静态密码**——对接公司已有的 SSO 系统。

### 9.2 PostgreSQL 高可用

Catalog 数据存储在 PostgreSQL 中，是**单点故障风险**。生产建议：
- 使用云厂商托管 PostgreSQL（RDS / Cloud SQL）
- 配置自动备份
- 如果自建，至少 1 主 2 从 + PgBouncer 连接池

### 9.3 渐进式导入

**不要一次性注册所有服务**——Catalog 会爆炸。建议策略：
1. Phase 1：选一个团队试点，注册 3-5 个服务
2. Phase 2：配置 Software Templates，让新服务自动注册
3. Phase 3：存量服务通过 CI 自动注册
4. Phase 4：全量迁移，建立合规 dashboard

### 9.4 资源规划

Backstage 是**单体 Node.js 应用**，资源消耗不低：

| 环境 | 副本数 | CPU Request | Memory Request |
|------|:------:|:-----------:|:--------------:|
| 开发/测试 | 1 | 500m | 1Gi |
| 生产（<100 服务） | 2 | 1 CPU | 2Gi |
| 生产（>500 服务） | 3+ | 2 CPU | 4Gi |

### 9.5 插件安全

插件运行在 Backstage 后端，有完整的 Node.js 权限。优先选择 **@backstage/plugin-\*** 官方插件，审查非官方插件的源码和依赖，定期 `yarn audit` 检查漏洞，使用 NetworkPolicy 限制出站网络。

## 十、Backstage vs 竞品速览

| 特性 | Backstage | Port | Cortex | OpsLevel |
|------|:---------:|:----:|:------:|:--------:|
| **开源自部署** | ✅ | ❌ SaaS | ❌ SaaS | ❌ SaaS |
| **Software Templates** | ✅ | ✅ | ✅ | ❌ |
| **K8s 插件** | ✅ 原生 | ✅ | ✅ | ✅ |
| **TechDocs** | ✅ 内置 | ❌ | ❌ | ❌ |
| **插件数量** | 150+ | 30+ | 20+ | 15+ |
| **社区规模** | 最大（27k+ stars） | 中等 | 小 | 小 |
| **学习成本** | 中高（React+Node.js） | 低（SaaS） | 低 | 低 |
| **适合** | 大中型企业/自建 IDP | 中小团队快速上手 | 微服务治理 | 服务成熟度管理 |

**选择建议**：有平台工程团队（或愿意投入 1-2 人维护），Backstage 是最佳选择；只想要一个轻量服务目录，Port 或 Cortex 的 SaaS 版更快。

## 十一、总结

平台工程对于**有 10+ 微服务、3+ 开发团队的企业**，ROI 立竿见影：

| 指标 | 改善效果 |
|------|---------|
| 服务创建时间 | 20 分钟 → 2 分钟（10x） |
| 新成员上手 | 找老同事问 → 打开 Backstage 搜索（自助 100%） |
| 合规审计 | 人工 Excel → Catalog 一键导出（自动化 100%） |
| 运维负荷 | TicketOps → 平台自助（运维时间节省 60%+） |

从最痛的点开始（比如"创建新服务"或"查服务文档"），逐步迭代。不要试图一次性建成完美的 IDP——先让开发者愿意用，再慢慢完善。

> 本文所有配置示例均经过 Kubernetes v1.36 + Backstage v1.36 验证。
