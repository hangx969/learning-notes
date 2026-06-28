---
title: "多集群 GitOps 实践：如何用 Argo CD 管理上百个 Kubernetes 集群"
source: "https://mp.weixin.qq.com/s/gflLt0lXE0zkJGs1hncBtg"
author:
  - "[[AI炼丹踩坑]]"
published:
created: 2026-06-28
description: "单集群 GitOps 玩得很顺，到了多集群规模，问题会突然变成平台工程问题。Argo CD 依然是主角，但重点不再是 Sync 按钮，而是 ApplicationSet、目录模型、权限隔离和发布半径控制。"
tags:
  - "clippings"
---
AI炼丹踩坑 AI炼丹踩坑 *2026年6月4日 16:04*

100 个 Kubernetes 集群摆在你面前，真正麻烦的不是“怎么把 YAML apply 过去”。

麻烦的是：谁能发？发到哪些集群？生产和测试差异怎么管？一个配置写错，会不会把 100 个集群一起打爆？

单集群 GitOps 玩得很顺，到了多集群规模，问题会突然变成平台工程问题。Argo CD 依然是主角，但重点不再是 Sync 按钮，而是 ApplicationSet、目录模型、权限隔离和发布半径控制。

下面按真实工程视角拆一遍。

---

## 先别急着写 ApplicationSet，目录结构会决定上限

很多团队一开始管理多集群，会直接这么干：

```
clusters/
  cluster-a/
    app1/values.yaml
  cluster-b/
    app1/values.yaml
  cluster-c/
    app1/values.yaml
```

这个结构很直观。

哪个集群有什么配置，一眼能看到。集群少的时候，甚至很舒服。

但当集群涨到几十个以后，问题会很快出现：

- values 文件大量重复
- 某个全局参数改一次，要改几十份
- 不知道哪些差异是有意的，哪些是历史遗留
- Review 变成找不同游戏

更可怕的是，业务会开始复制粘贴一个“看起来能跑”的配置。半年后，你会发现每个集群都长得不一样。

我更推荐把目录拆成三层： **应用模板、环境覆盖、集群元数据** 。

```
gitops/
  apps/
    ingress-nginx/base/
    payment-api/base/
  envs/
    prod/values.yaml
    staging/values.yaml
  regions/
    cn-east/values.yaml
  clusters/
    cluster-a/config.yaml
```

这里的关键点是：集群目录不要塞完整应用配置。

`clusters/cluster-a/config.yaml` 只放元数据，比如：

```
name: cluster-a
env: prod
region: cn-east
tenant: payment
tier: core
```

应用怎么部署，由 `apps` 定义。

生产和测试差异，由 `envs` 定义。

地域差异，由 `regions` 定义。

单集群例外，才进入 `clusters` 。

这种结构最大的好处是：差异是分层的，也是可审计的。你能清楚地知道，一个参数为什么在这个集群不一样。

---

## ApplicationSet 才是多集群分发的核心

Argo CD 的 Application 适合描述“一个应用部署到一个目标”。

但多集群场景下，你真正想表达的是：

> 把这个应用部署到所有 env=prod、region=cn-east、tenant=payment 的集群。

这就是 ApplicationSet 的价值。

它通过 Generator 生成 Application，再由 Template 控制每个 Application 长什么样。

一个简化版 ApplicationSet 可以这样写：

```
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

这里的 `clusters` Generator 会读取 Argo CD 里注册集群的 Secret。

这些 Secret 上有 label，比如：

```
env=prod
region=cn-east
tenant=payment
tier=core
```

ApplicationSet 根据 label 选出目标集群，然后给每个集群生成一个 Application。

这比手写 100 个 Application 靠谱太多。

---

## Generator 怎么选？别只会 Cluster Generator

ApplicationSet 的 Generator 很多，常用的有几个。

**Cluster Generator** 适合从 Argo CD 已注册集群里筛选目标。

平台团队负责注册集群，并给集群打 label。业务团队只关心“我要发到哪些标签的集群”。

这很适合内部平台场景。

```
generators:
- clusters:
    selector:
      matchLabels:
        region: cn-east
        env: prod
```

**List Generator** 适合少量固定集群。

比如某个系统只部署到 3 个专用集群，显式列出来反而更清楚。

```
generators:
- list:
    elements:
    - cluster: cluster-a
      url: https://1.1.1.1
    - cluster: cluster-b
      url: https://2.2.2.2
```

**Git Generator** 适合从 Git 中读取集群清单或应用清单。

比如你把集群元数据放在 `clusters/*/config.yaml` ，ApplicationSet 可以直接从 Git 扫描这些文件。

**Matrix Generator** 更适合“应用 x 集群”的组合场景。

比如 5 个基础组件，需要部署到 80 个集群，Matrix 可以把应用列表和集群列表组合起来。

真实落地时，我见得最多的是：

> **Cluster Generator 管目标集群，Git Generator 管发布规则。**

平台团队维护集群注册和标签。

业务团队通过 Git 提交应用发布规则。

这样边界比较清楚：平台不关心业务发什么，业务也不能随便碰集群凭证。

一个典型流程大概是这样：

![图片](https://mmbiz.qpic.cn/mmbiz_png/rK4MSArUKefX6dX6Cnic3t446343ze46NibV9eY0nOM9DoCP2Y9qxiaHJ28aVFjz8NfvVJvwxYdTPlkrLoE29uibFHnsrso3ARd0HOETic6mZ6pI/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

节点不复杂，但这里面已经包含了多集群 GitOps 的核心闭环。

---

## Push 还是 Pull？先看你的网络和风险模型

Argo CD 默认的多集群模式，本质上更接近 Push。

中心 Argo CD 持有各个集群的访问凭证，通过 Kubernetes API Server 把资源同步过去。

这种模式优点很明显：

- 一个控制面看所有集群
- UI、审计、告警都集中
- 运维体验统一
- 适合内部网络可控的集群

但它也有硬伤。

中心 Argo CD 会变成一个高价值目标。一旦权限过大，风险非常集中。

网络上也要求中心控制面能访问所有目标集群 API Server。集群多了以后，还会遇到 controller 压力、API 限流、同步风暴等问题。

尤其是生产核心组件，如果一次性触发 100 个集群自动同步，故障半径会非常难看。

Pull 模式则反过来。

每个集群内部署轻量 Argo CD、Argo CD Agent，或者类似的 GitOps Agent。集群自己去 Git 拉配置，不需要中心控制面直连 API Server。

它适合这几类场景：

- 边缘集群
- 客户侧私有集群
- 网络不稳定的机房
- 不希望集中保存集群凭证的组织

Pull 的问题也很现实。

全局视图会弱一些，统一编排也更麻烦。每个集群里都有组件要升级，策略一致性和版本管理也会变成新成本。

所以很多平台最后会选折中方案： **区域级 Argo CD** 。

比如一个大区或一个业务域部署一套 Argo CD，每套管理 10 到 30 个集群。

这样既不会把所有权限集中到一个控制面，也不会让每个集群都变成独立小岛。

简单选型可以这么看：

| 场景 | 推荐模式 |
| --- | --- |
| 10 个以内内部集群 | 中心 Argo CD |
| 几十个集群，跨地域 | 区域级 Argo CD |
| 上百个集群，业务域清晰 | 多套 Argo CD 分片 |
| 客户侧/边缘集群 | Pull 优先 |
| 高安全隔离要求 | 避免集中持有 cluster-admin |

不要迷信某一种模式。

多集群 GitOps 的目标不是架构漂亮，而是风险可控。

---

## 权限隔离别靠约定，要靠 Project 卡住

多团队共用 Argo CD 时，最怕一句话：

> “大家自觉点，别改别人的应用。”

这类约定最后基本都会失效。

Argo CD 里真正该用的是 Project。

Project 可以限制：

- 允许访问哪些 Git 仓库
- 允许部署到哪些集群
- 允许部署到哪些 namespace
- 能不能创建集群级资源
- 哪些用户或组能操作应用

一个简化的 Project 示例：

```
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

这个 Project 的意思是：

payment 团队只能从自己的仓库取配置，只能发到指定 namespace，不允许创建集群级资源。

生产里还要继续配合 Argo CD RBAC。

比如只允许业务团队 sync 自己 Project 下的 Application，不能改 Project，不能注册集群，不能改别的租户资源。

多租户场景下，强烈不建议把 cluster-admin 同步权限直接交给业务团队。

更稳的做法是：

- 平台维护受控 Helm Chart
- 业务只提交 values
- 命名空间级 RBAC 最小化
- 集群级资源由平台 Project 管
- 用 Kyverno / Gatekeeper 做准入校验

Git 仓库也要分层。

平台仓放基础组件、集群基线、准入策略。

应用仓放业务发布声明。

环境仓放环境参数和发布窗口。

不要让业务在一个仓库里既能改 Deployment，又能改 ClusterRole，还能改 Ingress Controller 配置。

这不是敏捷，这是埋雷。

---

## 环境差异要分层，不要给每个集群复制 values

多集群 GitOps 最容易失控的地方，就是环境差异。

一个常见反模式是：

```
values-cluster-a.yaml
values-cluster-b.yaml
values-cluster-c.yaml
...
```

一开始只是改了副本数。

后来加了镜像仓库、域名、资源配额、开关参数、亲和性配置。

最后每个 values 都几百行，没人敢删，也没人知道哪些配置还生效。

更可控的方式是分层覆盖：

```
global values
  -> env values
    -> region values
      -> cluster values
```

举个例子：

- global：镜像仓库、通用标签、默认资源限制
- env：prod 开启高可用，staging 降低副本数
- region：不同地域的域名、存储类、镜像加速地址
- cluster：只保留极少数例外，比如节点池名称

ApplicationSet 模板里可以根据集群 label 拼 values 路径。

```
helm:
  valueFiles:
  - values/global.yaml
  - values/envs/{{metadata.labels.env}}.yaml
  - values/regions/{{metadata.labels.region}}.yaml
  - values/clusters/{{name}}.yaml
```

注意，这里不是鼓励你无限叠 values。

层级太深也会变成另一种复杂度。

我一般建议 cluster 级 values 控制在很小范围内。如果某个组件在不同集群差异巨大，应该反过来问：它是不是已经不适合用同一个发布模型了？

对于复杂场景，可以用 Helm values、Kustomize patches、Jsonnet，甚至 Argo CD CMP 插件。

但要记住一点： **工具复杂度不能掩盖模型混乱** 。

---

## 大规模同步时，最怕“全体起立”

单集群里开 auto-sync 很爽。

提交代码，Argo CD 自动同步，几分钟后环境更新。

但放到 100 个集群，这个动作就危险了。

尤其是基础组件，比如：

- CNI
- Ingress Controller
- CoreDNS
- 监控 Agent
- 安全 DaemonSet
- 准入控制策略

这些东西一旦同时变更，出问题就是全局事故。

大规模多集群发布必须控制节奏。

常见手段有几个：

1. 按 label 分批
2. 用 sync waves 控制资源顺序
3. 用 sync windows 限制生产发布时间
4. 对核心组件关闭全量 auto-sync
5. 配置 resource health check
6. 失败后停止后续批次

比如先发 `tier=canary` ，观察没问题，再发 `tier=standard` ，最后发 `tier=core` 。

这比“所有 prod 集群一起 sync”安全得多。

ApplicationSet 的 Progressive Sync 能进一步帮你做分批推进，但不要把它当万能保险。

真正可靠的发布，还是要配合监控、告警、回滚策略和变更审计。

GitOps 不是让你不做发布管理。

它只是把发布管理变成了可声明、可审计、可回放的流程。

---

## 一个 100 集群平台可以怎么落地

假设你在做一个 SaaS 平台，有 100 个 Kubernetes 集群。

这些集群按环境、地域、租户、容量等级打标签：

```
env=prod
region=cn-east
tenant=customer-a
tier=standard
```

平台上有几类应用：

- 基础组件：ingress、cert-manager、external-dns
- 安全基线：kyverno、falco、network-policy
- 监控组件：prometheus-agent、logging-agent
- 业务应用：按租户或业务域发布

一个比较稳的架构是：

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/rK4MSArUKedj6ePEssaPRghQ2jhlQesWRxSEQfyjHYPUwI20hiayRbvaTraN1hm154TM8PJbXNiabacPVNlFZJsJ6Ig4kdbHzVs7esJyBhdGc/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

平台团队负责：

- 注册集群
- 维护集群标签
- 管理 Project
- 管理基础组件
- 定义准入策略
- 控制发布窗口

业务团队负责：

- 提交应用配置
- 声明目标标签
- 维护业务 values
- 查看自己 Project 下的同步状态

如果集群分布在多个大区，每个大区一套 Argo CD。

如果有客户侧私有化集群，优先考虑 Pull 模式，避免中心控制面直接访问客户 API Server。

如果是核心生产组件，默认不要全自动铺满所有集群，必须灰度。

这个方案不追求“一套 Argo CD 管天下”。

它追求的是：单个控制面的故障半径有限，权限边界清楚，发布节奏可控。

---

## 写在最后

多集群 GitOps 的难点，从来不是把 YAML 同步到更多集群。

真正的难点是：目录结构能不能撑住规模，ApplicationSet 生成逻辑是否可控，权限边界有没有被 Project 卡死，环境差异是否能被审计，发布失败会不会扩散成全局事故。

如果你现在只有几个集群，可以先用中心 Argo CD。

如果已经到几十个集群，建议尽早考虑区域拆分、标签治理和分批发布。

如果目标是客户侧或边缘场景，Pull 模式可能比中心 Push 更符合安全和网络现实。

你们现在的多集群 GitOps，是一个 Argo CD 管到底，还是已经按区域/业务域拆分了？

---

> 觉得有帮助？点个「在看」让更多人看到。 有类似的经历？欢迎留言区交流。