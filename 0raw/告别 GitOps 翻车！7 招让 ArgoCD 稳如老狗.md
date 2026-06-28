---
title: "告别 GitOps 翻车！7 招让 ArgoCD 稳如老狗"
source: "https://mp.weixin.qq.com/s/Ua-8o4-4Lb4PHWJIOX_8pQ?scene=1"
author:
  - "[[东风微鸣]]"
published:
created: 2026-06-28
description: "分享 ArgoCD 在生产级多租户 Kubernetes 平台中的实战经验，包括资源限制、工具选择、仓库分离、实例隔离、配置陷阱、AppProject\x0d\x0a  权限管理和按需调整 7 个要点，帮助 GitOps 落地更稳。"
tags:
  - "clippings"
---
东风微鸣 东风微鸣技术博客 *2026年6月9日 15:31*

> 字数 2154，阅读大约需 11 分钟

## 前言

最近在搞一个多租户的 Kubernetes 平台，ArgoCD 负责 GitOps 的落地。说实话，之前一直觉得自己对这玩意儿挺熟的，但真正到了生产级的多团队、多集群场景，各种坑就开始冒出来了。

最近正好在 油管 上看了很多 GitOps/ArgoCD 的技术分享，又翻到了 Red Hat/ArgoCD 官方博客上关于 GitOps 的推荐实践，手痒的不行，结合这段时间的经历，把几个关键点沉淀下来，希望能给正在或即将上 GitOps 的兄弟们一些参考。

## 七步法：让 ArgoCD 更稳、更隔离、更可控

之前的文章介绍了 ArgoCD 的基本用法，但生产环境，光会配还不够，还得配得好。这次我们不讲概念，直接上实战要点，看看怎么让 ArgoCD 这个“GitOps 内核”跑得更稳。

### 第一步：别让它“饿死”，也别让它“暴走”——资源限制要设好

ArgoCD 本身也是个 Pod，会消耗集群的 CPU 和内存。如果不设资源限制，它可能会吃掉一个节点的所有资源，影响集群上其他的业务 Pod。特别是在大规模集群或多集群模式下，ArgoCD 的 `application-controller` 和 `repo-server` 的负载会比较高(我的 application-controller 一个 pod 16G 内存)，资源限制和请求一定要配。

我自己的经验是：

```
# argocd-cm.yaml 或者 Operator 的 spec
server:
  resources:
    requests:
      cpu: "250m"
      memory: "512Mi"
    limits:
      cpu: "500m"
      memory: "1Gi"

controller:
  resources:
    requests:
      cpu: "500m"
      memory: "1Gi"
    limits:
      cpu: "1"
      memory: "2Gi"

repoServer:
  resources:
    requests:
      cpu: "250m"
      memory: "512Mi"
    limits:
      cpu: "500m"
      memory: "1Gi"
```

这个配置要根据你的集群规模和应用数量来调整，但记住一个原则： **请求给足，限制给够** 。

### 第二步：别跟原始 YAML 死磕——Helm 或 Kustomize 任选其一

ArgoCD 本身不强制你用 Helm 还是 Kustomize，但强烈建议不要直接管理原始的 YAML。

- • 直接维护原始 YAML 的缺点：
- • 重复代码多，特别是对于多环境（dev/staging/prod）的情况。
	- • 容易出错，一个环境改漏了，DR 的时候就抓瞎了。
	- • 更新维护困难，版本管理复杂。
- • 推荐策略：
- • 首选 Helm：如果你是标准的应用发布，有 Chart 仓库，团队熟悉 Helm，那就用 Helm。ArgoCD 对 Helm 的支持非常原生，可以自动渲染 Chart。
	- • 次选 Kustomize：如果你更习惯 Kubernetes 原生的方式，或者项目结构比较复杂（比如有大量 overlay），Kustomize 也是个好选择。

我个人更倾向于 Helm，因为它的模板化能力更强，而且生态更丰富（比如 ArtifactHub 上有一堆现成的 Chart）。但如果你做的是平台层面的配置（如 CRD、Operator），Kustomize 会更合适一些。

### 第三步：源代码和清单分开——权责分明，安全第一

这是一个很容易被忽略的点。很多人直接把应用代码和 ArgoCD 的 `Application` 清单放在同一个 Git 仓库里。

这样做有什么问题？

- • 生命周期不同：应用代码每天都在变，但 ArgoCD 的清单可能几周才改一次。把它们混在一起，版本管理会很混乱。
- • 权限不清：开发同学有代码仓库的写权限，但他们不应该有修改 `Application` 资源的权限（这可能会导致他们跳过审批直接上线）。
- • 安全风险：如果开发同学的仓库被黑，攻击者可以借机修改 ArgoCD 的配置，比如指向一个恶意的镜像仓库。

最佳实践：

- • 源代码（Source Repo）：应用本身的代码仓库（如 Java、Go 项目），开发团队维护。
- • 清单库（Manifest Repo）：存放 ArgoCD 的 `Application` 、 `AppProject` 、以及 Helm Chart 或 Kustomize 的 overlay 文件。由平台/SRE 团队维护，严格控制写权限。

### 第四步：最大程度隔离——应用实例和平台实例分开

这是 Red Hat 官方推荐的一个实践，我认为是多租户场景下的核心要点。

想象一下：一个团队的应用 `Application` 资源被误删了，导致整个 ArgoCD 的 `application-controller` 需要重新同步，这个过程可能会影响到其他所有团队的应用部署。

解决方案：为不同的团队创建独立的 ArgoCD 实例。(当然, 也可以根据实际情况, 一个共享 ArgoCD 实例, 但是进行严格的 RBAC 权限限制.)

```
apiVersion: v1
kind: Namespace
metadata:
  name: team-a-gitops
---
apiVersion: argoproj.io/v1alpha1
kind: ArgoCD
metadata:
  name: team-a
  namespace: team-a-gitops
spec:
  # 为 team-a 配置独立的 repo server, controller, dex server 等
  server:
    route:
      enabled: true
      hostname: argocd-team-a.example.com
  repo:
    # 限制 team-a 只能访问哪些仓库
    ...
```

上面是 openshift 下基于 argocd operator 的yaml. 通常我们要创建多个实例, 直接使用 helm chart 来部署多个实例即可.

注意：这听起来有些重，但在企业级场景下非常值得。每个实例都是自治的，一个团队的“瞎搞”不会影响集群的配置或别人的应用。

### 第五步：警惕声明式配置的“隐形陷阱”

ArgoCD 靠声明式配置（ `Application` 、 `AppProject` CRD）来管理。但这里有个坑：期望状态 ≠ 实际状态。

比如，你配了一个 `Application` ，希望它创建三个 `Deployment` 。但如果你在 Git 仓库里删了一个 `Deployment` 的 YAML 段，ArgoCD 会把它删掉。但如果有人在集群里手动 `kubectl edit` 改了某个字段，ArgoCD 会把它拉回 Git 里的状态。

那问题在哪？

- • 配置漂移的源头不止一个：除了 Git 仓库，还有 ArgoCD 本身的 Web UI 和 CLI 可以直接修改。如果有人（比如我自己，有手误）用 UI 手动改了 `syncPolicy` ，而忘记提交 Git，那这个期望状态和 Git 仓库就不一致了。
- • `Application` 本身也会漂移：想象一下，你通过 Web UI 修改了 `Application` 的某个参数（比如 `targetRevision` 指向不同的分支），这个修改是不会自动同步回 Git 的。

我的建议：

- • All-in Git：所有对 ArgoCD 配置的修改，必须从 Git 仓库发起。Web UI 只用来查看状态和手动触发同步。
- • 用 `argocd app diff` 检查：在 CI/CD 流程中，可以加一步脚本来运行 `argocd app diff` ，跟 Git 仓库对比，确保没有意外的配置漂移。
- • 监控 ArgoCD 自身：用 Prometheus 监控 ArgoCD 的指标，比如 `argocd_app_info` ，如果某个 `Application` 的状态变成了 `OutOfSync` ，就触发告警。或者用 ArgoCD 的 notifications-controller 来发送告警通知。

### 第六步：多人协作时，AppProject 是黄金搭档

权限管理，在多团队场景下是必选项。 `AppProject` 就是干这个的。

```
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: team-b-project
  namespace: argocd
spec:
  sourceRepos:
    - 'https://gitlab.example.com/team-b/*'  # 只能从 team-b 的仓库拉
  destinations:
    - namespace: 'team-b-*'  # 只能部署到 team-b 相关的命名空间
      server: 'https://kubernetes.default.svc'
  clusterResourceWhitelist:
    - group: '*'
      kind: '*'
  namespaceResourceWhitelist:
    - group: '*'
      kind: '*'
```

`AppProject` 可以严格控制：

- • 谁（ `sourceRepos` ）能拉什么代码？
- • 哪里（ `destinations` ）能部署？
- • 能创建什么资源（ `clusterResourceWhitelist` / `namespaceResourceWhitelist` ）？

说实话，这是 GitOps 多租户的基石，少了它，后面的隔离全是空谈。

### 第七步：不要迷信“最佳实践”

最后想吐槽一句。网上有很多现成的“ArgoCD 最佳实践”模板，但这玩意儿不能直接套用。

Red Hat 的专家也说了：要根据你的组织结构和 YAML 管理工具来调整。

- • 如果你们团队结构扁平，项目简单，一个 ArgoCD 实例 + Helm/Kustomize 就够用了。
- • 如果你们是平台团队，服务多个业务单元，那必须上多实例 + AppProject + 严格的权限控制。
- • 如果你们还在用原始 YAML，别急着上 Kustomize，先评估一下切换成本。

声明：本文所有实践建议，都来自我个人的生产实践和 Red Hat 官方推荐，不要无脑抄，要理解背后的原理。

## 总结

ArgoCD 是一个很牛的工具，但用好它不光是要会配，更是要对 GitOps 的设计原则有深入理解。

- • 资源限制：防止一台机器被吃掉。
- • 工具选择：Helm 或 Kustomize，别自己手写 YAML。
- • 仓库分离：源代码和清单库分开。
- • 实例隔离：应用和平台实例分开。
- • 警惕陷阱：All-in Git，不要手动改 UI。
- • AppProject：多租户的权限护栏。
- • 按需调整：不要盲目套用模板。

> 知行合一。知道怎么配置只是第一步，动手去实践、去踩坑、去复盘，才能真的把 GitOps 变成你团队的基础设施。

## 参考文档

- • Declarative...ish? Fixing Hidden Argo CD Pitfalls in Your GitOps Setup - Regina Voloshin <sup>[1]</sup>
- • OpenShift GitOps 推荐实践 | Red Hat 开发人员 <sup>[2]</sup>
- • Best Practices ArgoCD | K8s Deployment Strategy With ArgoCD <sup>[3]</sup>
- • GitOps with ArgoCD for Kubernetes <sup>[4]</sup>

#### 引用链接

`[1]` Declarative...ish? Fixing Hidden Argo CD Pitfalls in Your GitOps Setup - Regina Voloshin: *https://www.youtube.com/watch?v=VfVQj4Oa3z0*  
`[2]` OpenShift GitOps 推荐实践 | Red Hat 开发人员: *https://developers.redhat.com/blog/2025/03/05/openshift-gitops-recommended-practices#recommended\_practices*  
`[3]` Best Practices ArgoCD | K8s Deployment Strategy With ArgoCD: *https://medium.com/@dikshantmali.dev/best-practices-argocd-k8s-deployment-strategy-with-argocd-5b8226052718*  
`[4]` GitOps with ArgoCD for Kubernetes: *https://overcast.blog/gitops-with-argocd-for-kubernetes-tips-and-tricks-4b926ba75f88*

东风微鸣技术博客

邀请你前往腾讯公益一起捐

未来工程师计划

1人捐赠

GitOps · 目录