---
title: "K8S工具推荐，Kargo：下一代 GitOps 持续交付工具"
source: "https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485786&idx=1&sn=2935d0620bb8aabfcf8b228541254345&scene=21&poc_token=HLI26mmj92ITLxeAzGeKK8EmhFZRzWcGtyn6bCSZ"
author:
  - "[[海笑]]"
published:
created: 2026-04-23
description: "K8S工具推荐，深入了解 Kargo：下一代 GitOps 持续交付工具"
tags:
  - "clippings"
---

文末会有 **重磅福利** 赠送

随着云原生技术的快速发展，Kubernetes 已成为现代应用部署的核心。而在 Kubernetes 生态中，GitOps 作为一种以代码为中心的运维模式，因其高效性和可靠性，逐渐成为 DevOps 的主流实践。然而，复杂的多阶段部署流程、频繁的手动操作以及对 CI/CD 工具的高度依赖，依然是团队在实现真正的 GitOps 自动化时面临的挑战。

为了解决这些痛点， **Kargo** 应运而生。作为一个由 Argo 项目团队开发和维护的开源工具，Kargo 为 Kubernetes 提供了一个灵活且直观的持续交付和多阶段应用发布编排层，旨在简化 GitOps 实践的复杂性。本文将带您全面了解 Kargo 的核心功能与优势。
## 什么是 Kargo？

Kargo 是一个专注于\*\*持续发布（Continuous Promotion）\*\*的工具，它通过补充 Argo CD 的功能，帮助团队在 Kubernetes 环境中实现从一个阶段到下一个阶段的自动化变更推广。Kargo 的核心理念是通过 GitOps 原则，消除对自定义脚本和 CI 管道的依赖，让多阶段部署变得更加高效、安全且可视化。

### 核心特性：

1. 1\. **多阶段变更自动化**  
	Kargo 使用一个阶段的“真实来源”（如 Git 仓库、容器镜像或 Helm Chart）作为下一阶段的基础，实现无缝的变更推广，完全摆脱手动干预。
2. 2\. **灵活的推广管道**  
	用户可以根据具体的工作流需求，自定义多阶段推广流程，确保每个阶段的部署都符合业务逻辑。
3. 3\. **统一变更可视化**  
	通过直观的界面，用户可以清晰地查看每个环境中的变更状态，确保透明度和可控性。
4. 4\. **用户友好的界面**  
	Kargo 抽象了 GitOps 的复杂性，提供了一个简单易用的操作体验，使团队中的每个成员都能轻松上手。
5. 5\. **安全可靠的部署**  
	内置的流程与防护措施，确保跨环境的变更推广平稳且安全。

---

## 为什么选择 Kargo？

#### 1\. GitOps 驱动的下一代工具

Kargo 遵循 GitOps 原则，将配置视为代码管理，变更推广的方式与容器镜像的推广一致。通过状态驱动的推广过程，Kargo 能够无缝跟踪 Git 工件、容器镜像、Helm Chart 等更新，完全融入现有的 Kubernetes 基础设施。

#### 2\. 原生支持渐进式部署

Kargo 内置强大的渐进式部署策略，彻底摆脱 CI 工具中的自定义脚本。它通过原生的持续交付解决方案管理所有内容，不再依赖 CI 生成的工件作为“真实来源”，实现更高效的部署。

#### 3\. 提升开发者体验

Kargo 为开发者提供了完善的保护机制与深度洞察，让开发者能够自信地管理自己的变更推广。通过无摩擦的推广与回滚功能，开发者可以轻松推广容器镜像、Kubernetes 清单和 Helm Chart。

#### 4\. 全生命周期自动化

Kargo 将 GitOps 原则贯穿于应用的整个生命周期，自动化处理从开发到生产的每个阶段，显著提升效率、降低风险，并提供更高的可见性。

---

## 如何使用 Kargo？

### 1\. 安装Kargo

执行以下命令安装Kargo及其依赖：

```
curl -L https://raw.githubusercontent.com/akuity/kargo/main/hack/quickstart/install.sh | sh
```

安装完成后，可以通过以下地址访问：

- • Argo CD控制台：https://localhost:31443
- • Kargo控制台：https://localhost:31444

### 2\. 准备GitOps仓库

1. 1\. 首先fork示例仓库：https://github.com/akuity/kargo-demo
2. 2\. 仓库结构说明：
- • `base/` ：包含通用配置
	- • `stages/<stage-name>/` ：包含各环境特定配置

### 3\. 创建发布流水线

Kargo中的核心概念构建包括：

1. 1\. **Project（项目）** ：
- • 作为最顶层的组织单位
	- • 包含完整的发布流水线配置
3. 2\. **Warehouse（仓库）** ：
- • 用于订阅容器镜像仓库
	- • 自动发现新版本镜像
5. 3\. **Stage（阶段）** ：
- • 代表部署流水线中的各个环境
	- • 可以配置晋升规则和健康检查
7. 4\. **Freight（货物）** ：
- • 表示待发布的制品集合
	- • 可以包含容器镜像、Kubernetes配置等

## 实践演示

### 1\. 配置发布流水线

创建一个包含test、uat、prod三个环境的发布流水线：

```
apiVersion: kargo.akuity.io/v1alpha1
kind:Project
metadata:
name:kargo-demo
---
apiVersion:v1
kind:Secret
type:Opaque
metadata:
name:kargo-demo-repo
namespace:kargo-demo
labels:
    kargo.akuity.io/cred-type:git
stringData:
repoURL:${GITOPS_REPO_URL}
username:${GITHUB_USERNAME}
password:${GITHUB_PAT}
---
apiVersion:kargo.akuity.io/v1alpha1
kind:Warehouse
metadata:
name:kargo-demo
namespace:kargo-demo
spec:
subscriptions:
-image:
      repoURL:public.ecr.aws/nginx/nginx
      semverConstraint:^1.26.0
      discoveryLimit:5
---
apiVersion:kargo.akuity.io/v1alpha1
kind:PromotionTask
metadata:
name:demo-promo-process
namespace:kargo-demo
spec:
vars:
-name:gitopsRepo
    value:${GITOPS_REPO_URL}
-name:imageRepo
    value:public.ecr.aws/nginx/nginx
steps:
-uses:git-clone
    config:
# 后续配置省略...
---
apiVersion:kargo.akuity.io/v1alpha1
kind:Stage
metadata:
name:test
namespace:kargo-demo
spec:
requestedFreight:
-origin:
      kind:Warehouse
      name:kargo-demo
    sources:
      direct:true
promotionTemplate:
    spec:
      steps:
      -task:
          name:demo-promo-process
        as:promo-process
---
apiVersion:kargo.akuity.io/v1alpha1
kind:Stage
metadata:
name:uat
namespace:kargo-demo
spec:
# 后续配置省略...
---
apiVersion:kargo.akuity.io/v1alpha1
kind:Stage
metadata:
name:prod
namespace:kargo-demo
spec:
# 后续配置省略...
```

### 2\. 执行发布流程

1. 1\. 访问Kargo控制台
2. 2\. 在Freight Timeline中选择要发布的版本
3. 3\. 点击目标环境的发布按钮
4. 4\. 确认发布操作

### 3\. 验证发布结果

- • 通过Kargo控制台监控发布状态
- • 查看各环境的应用健康状态
- • 验证应用是否正常运行

---

## 总结

Kargo 的出现，为 Kubernetes 环境中的多阶段部署带来了革命性的改变。通过消除对自定义脚本和 CI 管道的依赖，Kargo 让团队能够专注于核心业务逻辑，而不是复杂的运维操作。无论是提升效率、增强安全性，还是简化开发者体验，Kargo 都展现出了其强大的潜力。

如果您的团队正在寻求一种更高效、更安全的 GitOps 实践方式，Kargo 无疑是值得尝试的下一代工具。立即访问 Kargo 官方文档开始您的 GitOps 旅程吧！

[加](http://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485016&idx=1&sn=f97eb3faad3330fd169d687fd08be53c&chksm=c147b652f6303f44718c9b6fa402033e9f7400bc08e0df64cb3c486fa8881e7ba74f0a7a1241&scene=21#wechat_redirect) [入知识星球，共同探索云原](http://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485016&idx=1&sn=f97eb3faad3330fd169d687fd08be53c&chksm=c147b652f6303f44718c9b6fa402033e9f7400bc08e0df64cb3c486fa8881e7ba74f0a7a1241&scene=21#wechat_redirect) [生学习之旅！](http://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485016&idx=1&sn=f97eb3faad3330fd169d687fd08be53c&chksm=c147b652f6303f44718c9b6fa402033e9f7400bc08e0df64cb3c486fa8881e7ba74f0a7a1241&scene=21#wechat_redirect)

更多云架构、K8S学习资料以及CKA、Azure考试认证资料，星球内可免费领取哦！

云原生、K8S等相关实战教程系列持续更新中。。

##### 往期回顾

[K8S工具推荐： 使用 Kubemark 进行 Kubernetes 大规模集群模拟实践](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485727&idx=1&sn=65c3d50d36899a805c87c17ca650a010&scene=21#wechat_redirect)

[K8S工具推荐：使用Argo Rollouts实现GitOps自动化测试与回滚](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485755&idx=1&sn=50463bc31bb2610d18a843881b1515ac&scene=21#wechat_redirect)

[K8S工具推荐：资源编排新利器：三大云厂商联合推出 KRO](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485719&idx=1&sn=cc7fe428cb840c21576129d48986b70e&scene=21#wechat_redirect)

[K8S工具推荐：告别复杂认证！Kubernetes登录神器kubelogin指南](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485698&idx=1&sn=47443ce3322a407525cd6ccdffbffb29&scene=21#wechat_redirect)

[K8S工具推荐：Kubernetes资源优化神器KRR：一键诊断集群资源浪费](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485685&idx=1&sn=6ced5d257f3c3e93383a63ef6802edaf&scene=21#wechat_redirect)

[Kubernetes工具推荐：使用 k8s-pod-restart-info-collector简化故障排查](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485663&idx=1&sn=c0f05332e39e5b59793afd2a82326f55&scene=21#wechat_redirect)

[K8S工具推荐：动态无缝的Kubernetes多集群解决方案-Liqo](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485739&idx=1&sn=cd7e35bbf22ca3077fbec318bb714d00&scene=21#wechat_redirect)

[K8S学习路线2025](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485579&idx=1&sn=993a46217ed2d8190851715afb5134d0&scene=21#wechat_redirect)

[𝙺̲𝚞̲𝚋̲𝚎̲𝚛̲𝚗̲𝚎̲𝚝̲𝚎̲𝚜̲ 管理的最佳实践（2025）](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485744&idx=1&sn=43dc3d501156461591903118b264a998&scene=21#wechat_redirect)

K8S工具 · 目录

继续滑动看下一个

云原生SRE

向上滑动看下一个