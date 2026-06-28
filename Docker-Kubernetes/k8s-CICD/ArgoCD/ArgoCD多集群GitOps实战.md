---
title: "多集群 GitOps 实战：用 Argo CD 管理上百个 Kubernetes 集群"
source:
  - "https://mp.weixin.qq.com/s/gflLt0lXE0zkJGs1hncBtg"
  - "https://mp.weixin.qq.com/s/Ua-8o4-4Lb4PHWJIOX_8pQ"
created: 2026-06-28
tags:
  - kubernetes
  - argocd
  - gitops
  - multi-cluster
  - applicationset
---

# ArgoCD 多集群 GitOps 实战

> 单集群 GitOps 玩得很顺，到了多集群规模，问题会突然变成平台工程问题。重点不再是 Sync 按钮，而是 ApplicationSet、目录模型、权限隔离和发布半径控制。

## 一、目录结构会决定上限

### 反模式：每集群一份完整配置

```
clusters/
  cluster-a/app1/values.yaml
  cluster-b/app1/values.yaml
  cluster-c/app1/values.yaml
```

集群少时很直观，但涨到几十个后：values 大量重复、全局参数改一次要改几十份、不知道哪些差异是有意的哪些是历史遗留、Review 变成找不同游戏。

### 推荐：三层目录模型

```
gitops/
  apps/                          # 应用模板
    ingress-nginx/base/
    payment-api/base/
  envs/                          # 环境覆盖
    prod/values.yaml
    staging/values.yaml
  regions/                       # 地域覆盖
    cn-east/values.yaml
  clusters/                      # 集群元数据（只放元数据，不放完整配置）
    cluster-a/config.yaml
```

`clusters/cluster-a/config.yaml` 只放元数据：

```yaml
name: cluster-a
env: prod
region: cn-east
tenant: payment
tier: core
```

- 应用怎么部署 → `apps` 定义
- 生产和测试差异 → `envs` 定义
- 地域差异 → `regions` 定义
- 单集群例外 → 才进入 `clusters`

**好处**：差异是分层的，也是可审计的。

## 二、ApplicationSet：多集群分发的核心

Argo CD 的 Application 适合描述"一个应用部署到一个目标"。多集群场景下需要的是：**把这个应用部署到所有 env=prod、region=cn-east、tenant=payment 的集群。**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: payment-api-prod
spec:
  generators:
  - clusters:
      selector:
        matchLabels:
          env: prod
          tenant: payment
  template:
    metadata:
      name: 'payment-api-{{name}}'
    spec:
      destination:
        server: '{{server}}'
        namespace: payment
```

`clusters` Generator 读取 Argo CD 里注册集群的 Secret（上面有 label），根据 label 选出目标集群，给每个集群生成一个 Application。

## 三、Generator 选型

| Generator | 适用场景 | 说明 |
|-----------|---------|------|
| **Cluster** | 从已注册集群筛选目标 | 平台团队注册集群 + 打 label，业务团队只关心"发到哪些标签" |
| **List** | 少量固定集群 | 某系统只部署到 3 个专用集群，显式列出更清楚 |
| **Git** | 从 Git 读取集群/应用清单 | 集群元数据放在 `clusters/*/config.yaml`，ApplicationSet 扫描 Git 文件 |
| **Matrix** | "应用 × 集群"组合场景 | 5 个基础组件 × 80 个集群 |

**真实落地最常见组合**：Cluster Generator 管目标集群，Git Generator 管发布规则。平台团队维护集群注册和标签，业务团队通过 Git 提交发布规则——边界清楚。

## 四、Push vs Pull：看网络和风险模型

### Push 模式（Argo CD 默认）

中心 Argo CD 持有各集群访问凭证，通过 API Server 同步。

**优点**：一个控制面看所有集群，UI/审计/告警集中，运维体验统一。

**硬伤**：中心控制面成高价值目标，权限过大风险集中；网络要求中心能访问所有集群 API Server；100 集群同时 auto-sync 触发同步风暴。

### Pull 模式

每个集群内部署轻量 Argo CD Agent，集群自己去 Git 拉配置，不需要中心控制面直连 API Server。

**适合**：边缘集群、客户侧私有集群、网络不稳定机房、不希望集中保存凭证的组织。

### 折中方案：区域级 Argo CD

一个大区或业务域部署一套 Argo CD，每套管理 10-30 个集群。

| 场景 | 推荐模式 |
|------|---------|
| 10 个以内内部集群 | 中心 Argo CD |
| 几十个集群，跨地域 | 区域级 Argo CD |
| 上百个集群，业务域清晰 | 多套 Argo CD 分片 |
| 客户侧/边缘集群 | Pull 优先 |
| 高安全隔离要求 | 避免集中持有 cluster-admin |

**多集群 GitOps 的目标不是架构漂亮，而是风险可控。**

## 五、权限隔离：靠 Project 卡住，别靠约定

Argo CD Project 可以限制：允许访问哪些 Git 仓库、部署到哪些集群/namespace、能否创建集群级资源、哪些用户能操作。

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: payment
spec:
  sourceRepos:
  - https://git.example.com/payment/*
  destinations:
  - namespace: payment-*
    server: https://kubernetes.default.svc
  clusterResourceWhitelist: []
```

**多租户最佳实践**：
- 平台维护受控 Helm Chart，业务只提交 values
- 命名空间级 RBAC 最小化，集群级资源由平台 Project 管
- 用 Kyverno / Gatekeeper 做准入校验
- Git 仓库分层：平台仓（基础组件/基线/策略）、应用仓（业务发布）、环境仓（参数/发布窗口）

> 不要让业务在一个仓库里既能改 Deployment，又能改 ClusterRole，还能改 Ingress Controller 配置。这不是敏捷，这是埋雷。

## 六、环境差异分层覆盖

### 反模式

```
values-cluster-a.yaml
values-cluster-b.yaml
values-cluster-c.yaml  # 每个都几百行，没人敢删
```

### 推荐：分层覆盖

```
global values → env values → region values → cluster values
```

- **global**：镜像仓库、通用标签、默认资源限制
- **env**：prod 开启高可用，staging 降低副本数
- **region**：不同地域的域名、存储类、镜像加速地址
- **cluster**：只保留极少数例外

ApplicationSet 模板里按集群 label 拼 values 路径：

```yaml
helm:
  valueFiles:
  - values/global.yaml
  - values/envs/{{metadata.labels.env}}.yaml
  - values/regions/{{metadata.labels.region}}.yaml
  - values/clusters/{{name}}.yaml
```

cluster 级 values 控制在很小范围内。如果某个组件在不同集群差异巨大，应该反过来问：它是不是已经不适合用同一个发布模型了？

## 七、大规模发布节奏控制

单集群 auto-sync 很爽，但 100 个集群同时变更基础组件（CNI/Ingress Controller/CoreDNS/监控/准入策略），出问题就是全局事故。

**控制手段**：

1. 按 label 分批：先发 `tier=canary` → 观察 → `tier=standard` → `tier=core`
2. sync waves 控制资源顺序
3. sync windows 限制生产发布时间
4. 对核心组件关闭全量 auto-sync
5. 配置 resource health check
6. 失败后停止后续批次

ApplicationSet 的 **Progressive Sync** 能做分批推进，但不要当万能保险。真正可靠的发布还要配合监控、告警、回滚策略和变更审计。

## 八、100 集群平台落地架构

SaaS 平台，100 个集群按 `env/region/tenant/tier` 打标签。

**平台团队职责**：注册集群、维护标签、管理 Project、管理基础组件、定义准入策略、控制发布窗口。

**业务团队职责**：提交应用配置、声明目标标签、维护业务 values、查看自己 Project 下的同步状态。

**架构原则**：
- 多大区 → 每个大区一套 Argo CD
- 客户侧私有化 → Pull 模式，避免直连客户 API Server
- 核心生产组件 → 不全自动铺满，必须灰度
- 不追求"一套 Argo CD 管天下"，追求**单个控制面故障半径有限、权限边界清楚、发布节奏可控**

## 九、总结

多集群 GitOps 的难点从来不是把 YAML 同步到更多集群。真正的难点是：

1. **目录结构能不能撑住规模** — 三层模型（应用模板/环境覆盖/集群元数据）
2. **ApplicationSet 生成逻辑是否可控** — Generator 选型 + 标签治理
3. **权限边界有没有被 Project 卡死** — 不靠约定靠机制
4. **环境差异是否能被审计** — 分层覆盖，cluster 级最小化
5. **发布失败会不会扩散成全局事故** — 分批发布 + Progressive Sync + 灰度


---

## 生产环境 7 步加固法

> 来源：多租户 K8s 平台 ArgoCD 实战经验 + Red Hat 官方推荐实践。

### 加固 1：资源限制——别让 ArgoCD 饿死，也别让它暴走

ArgoCD 本身也是 Pod，大规模集群下 `application-controller` 和 `repo-server` 负载会很高（实测 controller 单 Pod 16G 内存）。

```yaml
server:
  resources:
    requests: { cpu: "250m", memory: "512Mi" }
    limits:   { cpu: "500m", memory: "1Gi" }
controller:
  resources:
    requests: { cpu: "500m", memory: "1Gi" }
    limits:   { cpu: "1",    memory: "2Gi" }
repoServer:
  resources:
    requests: { cpu: "250m", memory: "512Mi" }
    limits:   { cpu: "500m", memory: "1Gi" }
```

原则：**请求给足，限制给够**。根据集群规模和应用数量调整。

### 加固 2：别跟原始 YAML 死磕——Helm 或 Kustomize 任选

直接维护原始 YAML 的缺点：重复代码多、一个环境改漏了 DR 时抓瞎、版本管理复杂。

- **首选 Helm**：模板化能力强，生态丰富（ArtifactHub 一堆现成 Chart），ArgoCD 原生支持
- **次选 Kustomize**：K8s 原生方式，大量 overlay 场景更合适，平台层 CRD/Operator 配置更适用

### 加固 3：源代码和清单库分开——权责分明，安全第一

很多人把应用代码和 ArgoCD `Application` 清单放在同一个 Git 仓库，这有严重问题：

- **生命周期不同**：应用代码每天变，ArgoCD 清单几周才改一次
- **权限不清**：开发有代码仓库写权限，但不应该有修改 `Application` 资源的权限（可能跳过审批直接上线）
- **安全风险**：代码仓库被黑，攻击者可以修改 ArgoCD 配置指向恶意镜像仓库

**最佳实践**：
- **源代码仓库**（Source Repo）：应用本身的代码，开发团队维护
- **清单库**（Manifest Repo）：ArgoCD 的 Application、AppProject、Helm Chart/Kustomize overlay，由平台/SRE 团队维护，严格控制写权限

### 加固 4：最大程度隔离——应用实例和平台实例分开

Red Hat 官方推荐。想象一个团队的 `Application` 资源被误删，导致整个 `application-controller` 需要重新同步，影响所有其他团队。

**解决方案**：为不同团队创建独立的 ArgoCD 实例（用 Helm Chart 或 ArgoCD Operator 部署多套）。每个实例自治，一个团队的"瞎搞"不会影响集群配置或别人的应用。

### 加固 5：警惕声明式配置的"隐形陷阱"

期望状态 ≠ 实际状态。有人用 Web UI 手动改了 `syncPolicy` 或 `targetRevision`，这个修改不会自动同步回 Git。

**防护措施**：
- **All-in Git**：所有对 ArgoCD 配置的修改必须从 Git 仓库发起，Web UI 只用来查看状态和手动触发同步
- **CI 中检查漂移**：在流水线中运行 `argocd app diff`，跟 Git 仓库对比，确保没有意外的配置漂移
- **监控 ArgoCD 自身**：用 Prometheus 监控 `argocd_app_info` 指标，`OutOfSync` 状态触发告警；或用 ArgoCD notifications-controller 发送通知

### 加固 6：多人协作时，AppProject 是黄金搭档

（与前文"权限隔离"互补，这里补充 `clusterResourceWhitelist` 和 `namespaceResourceWhitelist` 的细粒度控制）

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: team-b-project
  namespace: argocd
spec:
  sourceRepos:
    - 'https://gitlab.example.com/team-b/*'
  destinations:
    - namespace: 'team-b-*'
      server: 'https://kubernetes.default.svc'
  clusterResourceWhitelist: []        # 禁止创建任何集群级资源
  namespaceResourceWhitelist:
    - group: '*'
      kind: '*'
```

AppProject 是 GitOps 多租户的基石——少了它，后面的隔离全是空谈。

### 加固 7：不要迷信"最佳实践"——按需调整

- 团队结构扁平、项目简单 → 一个 ArgoCD 实例 + Helm/Kustomize 就够用
- 平台团队服务多个业务单元 → 必须上多实例 + AppProject + 严格权限控制
- 还在用原始 YAML → 别急着上 Kustomize，先评估切换成本

> 知行合一。知道怎么配置只是第一步，动手去实践、去踩坑、去复盘，才能真正把 GitOps 变成你团队的基础设施。
