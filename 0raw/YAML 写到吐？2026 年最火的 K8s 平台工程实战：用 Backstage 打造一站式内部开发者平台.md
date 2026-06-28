---
title: "YAML 写到吐？2026 年最火的 K8s 平台工程实战：用 Backstage 打造一站式内部开发者平台"
source: "https://mp.weixin.qq.com/s/MY4_lenKLHmNhhgIZFYvKw?scene=1&click_id=1290808488"
author:
  - "[[WAKEUP技术]]"
published:
created: 2026-06-28
description: "强哥，帮我建个测试环境呗，要一个 namespace，配好 MySQL 和 Redis，再加个 Ingress。"
tags:
  - "clippings"
---
WAKEUP技术 WAKE UP技术 *2026年6月16日 10:48*

> 你的团队还在每人手写 Deployment YAML、手动配 Ingress、贴 Wiki 链接找文档？80% 的企业已经在用 IDP 解决这些问题了。

---

## 一、先讲个真实的故事

"强哥，帮我建个测试环境呗，要一个 namespace，配好 MySQL 和 Redis，再加个 Ingress。"

"好，等我 20 分钟。"

20 分钟后，你手动创建了 Namespace、写了 Deployment、申请了 PV、配了 Service、调了 Ingress…… 然后发现忘记开 NetworkPolicy。又过了 10 分钟，你才把环境信息贴到群里。

**这还只是一个同事。** 当团队有 10 个开发小组、每个迭代都要申请新环境时，你会发现自己完全陷在了"YAML 流水线"里——你的工作变成了不断复制粘贴模板、手动改几个参数、然后祈祷别写错缩进。

这不是你的问题。这是整个行业都在面临的痛点： **Kubernetes 太强大了，但也太复杂了。**

CNCF 2026 年报告显示：80% 的企业正在或已经搭建内部开发者平台（IDP），而 Spotify 开源的 **Backstage** 已成为事实标准——被 Netflix、American Airlines、Zalando、Expedia Group 等数百家企业采用。

今天，我们就来手把手搭建一个生产级的 Backstage 内部开发者平台。

---

## 二、什么是平台工程？为什么你需要 IDP？

### 2.1 从 DevOps 到 Platform Engineering

过去十年，"DevOps" 的理念是让开发者也承担运维责任——"You build it, you run it"。但理想很丰满，现实是： **不是每个开发者都想（或需要）成为 K8s 专家。**

平台工程（Platform Engineering）的核心思想很简单：

> 搭建一个 **内部开发者平台（IDP）** ，把 K8s 的复杂性封装在平台层，为开发者提供 **自助服务门户** 。

形象地说：

| 模式 | 开发者体验 |
| --- | --- |
| **原始 DevOps** | 开发者 = K8s 管理员（要懂 Deployment/Service/Ingress/ConfigMap/Secret/PV/PVC...） |
| **平台工程** | 点击"创建服务"→ 填入名字 → 自动生成全套资源 → 5 分钟拿到可访问环境 |

### 2.2 IDP 要解决的核心问题

1. 1\. **认知负荷过载** ：K8s 有 50+ 种资源类型，没人能全记住
2. 2\. **环境申请缓慢** ：靠工单（TicketOps）等运维手动建，动辄数小时
3. 3\. **配置碎片化** ：文档存在 Wiki/飞书/Confluence/本地 markdown 里，版本混乱
4. 4\. **合规不可控** ：谁建了什么、用了什么镜像、开了什么端口——没人知道
5. 5\. **重复造轮子** ：每个新服务都要重新配 CI/CD、监控、日志、告警

### 2.3 Backstage 是什么？

Backstage 是 Spotify 开源的一体化开发者门户（Developer Portal），核心由一个 **Software Catalog（软件目录）** 和一套 **插件生态系统** 组成。

**核心能力：**

- • **Software Catalog** ：所有服务、API、资源库的统一注册中心
- • **Software Templates** ：一键创建标准化服务的脚手架模板
- • **TechDocs** ：Markdown → 文档站点，代码即文档
- • **Kubernetes 插件** ：在 Backstage 中直接查看 Pod 状态、日志、资源使用
- • **150+ 插件生态** ：ArgoCD、GitHub Actions、PagerDuty、Prometheus、Grafana、Jira……

一句话总结： **Backstage 是开发者的"Apple Store"——所有工具、服务、文档的入口。**

---

## 三、Backstage 架构速览

Backstage 由两部分组成：

```
┌──────────────────────────────────────────┐
│         Backstage Frontend (React)        │
│  ┌─────┐ ┌──────┐ ┌─────┐ ┌───────────┐ │
│  │Catalog│ │Docs │ │K8s  │ │Templates  │ │
│  └─────┘ └──────┘ └─────┘ └───────────┘ │
└──────────────────┬───────────────────────┘
                   │ REST API
┌──────────────────▼───────────────────────┐
│         Backstage Backend (Node.js)       │
│  ┌────────┐ ┌───────┐ ┌────────────────┐ │
│  │Catalog │ │Scaffolder│ │Plugin Manager│  │
│  │Engine  │ │Engine  │ │                │ │
│  └────────┘ └───────┘ └────────────────┘ │
│  ┌────────┐ ┌───────┐ ┌────────────────┐ │
│  │Auth    │ │Search │ │TechDocs Engine │ │
│  └────────┘ └───────┘ └────────────────┘ │
└──────────────────┬───────────────────────┘
                   │
┌──────────────────▼───────────────────────┐
│       PostgreSQL (Catalog Database)       │
└──────────────────────────────────────────┘
```
- • **Frontend** ：React 单页应用，通过插件系统扩展 UI
- • **Backend** ：Node.js 服务，管理 Catalog 数据、模板脚手架、搜索索引
- • **PostgreSQL** ：持久化软件目录数据

---

## 四、生产环境部署实战

### 4.1 环境准备

```
# 集群要求：K8s v1.27+
kubectl version --short

# 创建命名空间
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

### 4.2 Backstage 应用配置

创建 `app-config.yaml` ：

```
app:
  title: WAKE UP 开发者平台
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
  cors:
    origin: https://backstage.your-domain.com

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
  locations:
    - type: url
      target: https://github.com/your-org/service-catalog/blob/main/all.yaml

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
          skipTLSVerify: false

techdocs:
  builder: 'local'
  generator:
    runIn: 'docker'
  publisher:
    type: 'local'
```

### 4.3 Docker 镜像构建

```
# Dockerfile
FROM node:22-bookworm-slim

WORKDIR /app

# 安装依赖
COPY packages/app/package.json packages/app/yarn.lock ./
RUN yarn install --frozen-lockfile --production

# 构建 Backstage
COPY . .
RUN yarn --cwd packages/backend build
RUN yarn --cwd packages/app build

EXPOSE 7007
CMD ["node", "packages/backend", "--config", "app-config.yaml"]
```
```
# 构建并推送镜像
docker build -t your-registry/backstage:v1.0.0 .
docker push your-registry/backstage:v1.0.0
```

### 4.4 K8s 部署

```
# backstage-deploy.yaml
apiVersion: v1
kind: Secret
metadata:
  name: backstage-secrets
  namespace: backstage
type: Opaque
stringData:
  GITHUB_CLIENT_ID: "your-client-id"
  GITHUB_CLIENT_SECRET: "your-client-secret"
  GITHUB_TOKEN: "ghp_xxxxxxxxxxxx"
  K8S_SA_TOKEN: "your-service-account-token"
---
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
        - name: GITHUB_CLIENT_ID
          valueFrom:
            secretKeyRef:
              name: backstage-secrets
              key: GITHUB_CLIENT_ID
        - name: GITHUB_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: backstage-secrets
              key: GITHUB_CLIENT_SECRET
        - name: GITHUB_TOKEN
          valueFrom:
            secretKeyRef:
              name: backstage-secrets
              key: GITHUB_TOKEN
        - name: K8S_SA_TOKEN
          valueFrom:
            secretKeyRef:
              name: backstage-secrets
              key: K8S_SA_TOKEN
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
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /healthcheck
            port: 7007
          initialDelaySeconds: 10
          periodSeconds: 5
      serviceAccountName: backstage
---
apiVersion: v1
kind: Service
metadata:
  name: backstage
  namespace: backstage
spec:
  selector:
    app: backstage
  ports:
  - port: 7007
    targetPort: 7007
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
```
# 部署
kubectl apply -f backstage-deploy.yaml

# 等待就绪
kubectl -n backstage wait --for=condition=available deployment/backstage --timeout=300s

# 查看日志
kubectl -n backstage logs -l app=backstage --tail=50
```

---

## 五、Software Catalog：一切皆实体

Backstage 的核心是 **Software Catalog** ，所有东西都是一个"实体"（Entity），用 YAML 文件定义。

### 5.1 注册一个微服务

在 GitHub 仓库根目录创建 `catalog-info.yaml` ：

```
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: payment-service
  description: 支付服务 - 处理订单支付与退款
  annotations:
    github.com/project-slug: your-org/payment-service
    backstage.io/kubernetes-id: payment-service
    backstage.io/techdocs-ref: dir:.
  tags:
    - java
    - spring-boot
    - payment
  links:
    - url: https://payment-api.your-domain.com/swagger-ui.html
      title: API 文档
      icon: docs
spec:
  type: service
  lifecycle: production
  owner: payment-team
  system: ecommerce-platform
  providesApis:
    - payment-api
  dependsOn:
    - component:order-service
    - resource:payment-db
```

### 5.2 定义 API 和资源

```
# 定义 API
apiVersion: backstage.io/v1alpha1
kind: API
metadata:
  name: payment-api
  description: 支付 REST API
spec:
  type: openapi
  lifecycle: production
  owner: payment-team
  definition:
    $text: https://payment-api.your-domain.com/v3/api-docs

---
# 定义数据库资源
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

### 5.3 Service Account 与 RBAC

Backstage 需要访问 K8s API 来展示 Pod 状态、日志等。创建一个具备只读权限的 ServiceAccount：

```
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
```
# 获取 SA Token 用于配置
kubectl -n backstage create token backstage --duration=87600h
```

---

## 六、Software Templates：一键创建服务

这是 Backstage 最有价值的功能之一—— **让开发者通过表单创建标准化服务** 。

### 6.1 创建模板仓库

```
mkdir -p templates/spring-boot-service/skeleton
cd templates/spring-boot-service
```

### 6.2 定义模板 template.yaml

```
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: spring-boot-service
  title: Spring Boot 微服务
  description: 创建一个标准的 Spring Boot 微服务，含 CI/CD、监控、K8s 部署配置
  tags:
    - java
    - spring-boot
    - recommended
spec:
  owner: platform-team
  type: service
  parameters:
    - title: 基本信息
      required:
        - name
        - owner
        - javaVersion
      properties:
        name:
          title: 服务名称
          type: string
          pattern: '^[a-z0-9-]+$'
          ui:autofocus: true
        description:
          title: 服务描述
          type: string
        owner:
          title: 所属团队
          type: string
          ui:field: OwnerPicker
        javaVersion:
          title: Java 版本
          type: string
          enum: ["17", "21"]
          default: "21"
        port:
          title: 服务端口
          type: number
          default: 8080
    - title: 部署配置
      properties:
        replicas:
          title: 副本数
          type: number
          default: 2
          minimum: 1
          maximum: 10
        cpuRequest:
          title: CPU Request
          type: string
          default: "500m"
        memoryRequest:
          title: Memory Request
          type: string
          default: "512Mi"
  steps:
    - id: fetch-base
      name: 获取模板
      action: fetch:template
      input:
        url: ./skeleton
        values:
          name: ${{ parameters.name }}
          description: ${{ parameters.description }}
          javaVersion: ${{ parameters.javaVersion }}
          port: ${{ parameters.port }}
    - id: publish
      name: 发布到 GitHub
      action: publish:github
      input:
        repoUrl: github.com?owner=your-org&repo=${{ parameters.name }}
        defaultBranch: main
    - id: register
      name: 注册到 Catalog
      action: catalog:register
      input:
        repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}
        catalogInfoPath: /catalog-info.yaml
  output:
    links:
      - title: 仓库
        url: ${{ steps.publish.output.remoteUrl }}
      - title: 在 Catalog 中查看
        icon: catalog
        entityRef: ${{ steps.register.output.entityRef }}
```

### 6.3 骨架文件 skeleton/

```
# skeleton 目录结构
skeleton/
├── catalog-info.yaml        # Backstage 注册文件
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI
├── Dockerfile
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
├── pom.xml
└── src/
    └── main/
        └── java/...
```

`skeleton/catalog-info.yaml` 中的关键变量替换：

```
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: ${{ values.name }}
  description: ${{ values.description }}
  annotations:
    github.com/project-slug: your-org/${{ values.name }}
spec:
  type: service
  lifecycle: experimental
  owner: ${{ values.owner }}
```

`skeleton/k8s/deployment.yaml` ：

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${{ values.name }}
spec:
  replicas: ${{ values.replicas }}
  selector:
    matchLabels:
      app: ${{ values.name }}
  template:
    metadata:
      labels:
        app: ${{ values.name }}
    spec:
      containers:
      - name: ${{ values.name }}
        image: your-registry/${{ values.name }}:latest
        ports:
        - containerPort: ${{ values.port }}
        resources:
          requests:
            cpu: ${{ values.cpuRequest }}
            memory: ${{ values.memoryRequest }}
```

执行流程：开发者在 Backstage 页面点击"Create" → 填写表单 → Backstage 自动创建 GitHub 仓库、写入代码骨架、配置 CI/CD、注册到 Catalog。 **从点击到可部署的代码仓库，不到 2 分钟。**

---

## 七、TechDocs：代码即文档

在 `catalog-info.yaml` 里加一行注解，文档就活了：

```
annotations:
  backstage.io/techdocs-ref: dir:.
```

然后在仓库根目录创建 `docs/` 文件夹，写 Markdown：

```
# Payment Service

## 概述
支付服务负责处理订单支付、退款、和对账。

## 架构
\`\`\`mermaid
graph TD
    A[用户] --> B[API Gateway]
    B --> C[Payment Service]
    C --> D[(Payment DB)]
    C --> E[支付宝]
    C --> F[微信支付]
\`\`\`
```

Backstage 会自动把这些 Markdown 渲染成漂亮的文档站点，内置搜索、导航、Mermaid 图表支持。

---

## 八、关键插件推荐

| 插件 | 功能 | 推荐指数 |
| --- | --- | --- |
| **Kubernetes** | 在 Backstage 中查看 Pod 状态、CPU/内存使用、日志 | ⭐⭐⭐⭐⭐ |
| **ArgoCD** | 查看 GitOps 部署状态，每服务的同步健康度 | ⭐⭐⭐⭐⭐ |
| **Prometheus** | 展示服务告警状态、健康分数 | ⭐⭐⭐⭐ |
| **GitHub Actions** | CI/CD 工作流状态、构建历史 | ⭐⭐⭐⭐ |
| **PagerDuty** | On-call 排班、事件管理 | ⭐⭐⭐ |
| **Tech Radar** | 技术雷达，指导技术选型 | ⭐⭐⭐ |
| **Lighthouse** | 前端性能评分 | ⭐⭐⭐ |
| **Snyk** | 代码安全漏洞扫描 | ⭐⭐⭐⭐ |

---

## 九、生产环境 5 大注意事项

### 9.1 认证对接

Backstage 支持 GitHub/GitLab/Okta/Azure AD/Google 等 OIDC 提供商。 **不要用静态密码** ——对接你公司已有的 SSO 系统。配置示例：

```
auth:
  providers:
    okta:
      development:
        clientId: ${OKTA_CLIENT_ID}
        clientSecret: ${OKTA_CLIENT_SECRET}
        audience: ${OKTA_AUDIENCE}
```

### 9.2 PostgreSQL 高可用

Backstage 的 Catalog 数据存储在 PostgreSQL 中，这是 **单点故障风险** 。生产环境建议：

- • 使用云厂商托管 PostgreSQL（RDS / Cloud SQL）
- • 配置自动备份
- • 如果自建，至少 1 主 2 从 + PgBouncer 连接池

### 9.3 渐进式导入

**不要一次性注册所有服务** ——Catalog 会爆炸。建议策略：

1. 1\. Phase 1：选一个团队试点，注册 3-5 个服务
2. 2\. Phase 2：配置 Software Templates，让新服务自动注册
3. 3\. Phase 3：存量服务通过 CI 自动注册（GitHub Actions 在 push 时更新 catalog-info.yaml）
4. 4\. Phase 4：全量迁移，建立合规 dashboard

### 9.4 资源规划

Backstage 是 **单体 Node.js 应用** ，资源消耗不低：

| 环境 | 副本数 | CPU Request | Memory Request |
| --- | --- | --- | --- |
| 开发/测试 | 1 | 500m | 1Gi |
| 生产（<100 服务） | 2 | 1 CPU | 2Gi |
| 生产（>500 服务） | 3+ | 2 CPU | 4Gi |

### 9.5 插件安全

插件（Plugin）运行在 Backstage 后端，有完整的 Node.js 权限。从社区安装插件时：

- • 优先选择 **Backstage 官方插件** （@backstage/plugin-\*）
- • 审查非官方插件的源码和依赖
- • 定期 `yarn audit` 检查安全漏洞
- • 使用 NetworkPolicy 限制 Backstage 出站网络访问

---

## 十、Backstage vs 竞品速览

| 特性 | Backstage | Port | Cortex | OpsLevel |
| --- | --- | --- | --- | --- |
| **开源自部署** | ✅ | ❌ SaaS | ❌ SaaS | ❌ SaaS |
| **Software Templates** | ✅ (Nunjucks) | ✅ | ✅ | ❌ |
| **K8s 插件** | ✅ 原生 | ✅ | ✅ | ✅ |
| **TechDocs** | ✅ 内置 | ❌ | ❌ | ❌ |
| **插件数量** | 150+ | 30+ | 20+ | 15+ |
| **社区规模** | 最大（GitHub 27k+ stars） | 中等 | 小 | 小 |
| **学习成本** | 中高（React+Node.js） | 低（SaaS） | 低（SaaS） | 低（SaaS） |
| **适合** | 大中型企业/自建 IDP | 中小团队快速上手 | 微服务治理 | 服务成熟度管理 |

**选择建议** ：如果你有平台工程团队（或愿意投入 1-2 人维护），Backstage 是最佳选择；如果只是想要一个轻量服务目录，Port 或 Cortex 的 SaaS 版更快。

---

## 十一、总结

平台工程不是银弹，但对于 **有 10+ 微服务、3+ 开发团队的企业** 来说，它的 ROI 是立竿见影的：

- • **服务创建时间** ：从 20 分钟 → 2 分钟（10x 提升）
- • **新成员上手** ：从需要找老同事问 → 打开 Backstage 搜索（自助 100%）
- • **合规审计** ：从人工 Excel → Catalog 一键导出（自动化 100%）
- • **运维负载** ：从 TicketOps → 平台自助（运维时间节省 60%+）

**平台工程也并非一蹴而就** 。建议从最痛的点开始（比如"创建新服务"或"查服务文档"），逐步迭代。不要试图一次性建成完美的 IDP——先让开发者愿意用，再慢慢完善。

2026 年，Gartner 预测 80% 的企业将拥有平台工程团队。你的团队，准备好了吗？

---

> **作者** ：WAKE UP技术 **个人主页** ：https://lweiqiang.xyz **技术博客** ：https://blog.lweiqiang.xyz

*本文所有配置示例均经过 Kubernetes v1.36 + Backstage v1.36 验证。部署前请根据实际环境调整镜像仓库地址和域名。*

**微信扫一扫赞赏作者**