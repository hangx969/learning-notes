---
title: "Kyverno 1.18 发布：CNCF 毕业后的首个版本，继续强化 Kubernetes 原生策略能力"
source: "https://mp.weixin.qq.com/s/xYdB_VEVehtopOd08KqO_Q?scene=1&click_id=93"
author:
published:
created: 2026-05-07
description: "Kyverno 也在继续向基于 CEL 的策略类型演进，为未来的 Policy as Code 奠定基础。"
tags:
  - "clippings"
---
*2026年5月7日 09:45*

![图片](https://mmbiz.qpic.cn/mmbiz_png/Bia64aMibibM1cSg41Mbk4r75IFbyCMO706NxrYkkAUflYngfomEsMD11F1YVlv0uFKibuH8GOVgtqwTxJar2PlUTI2Io4gcibeerDjYXG2fs3lo/640?from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

Kyverno 1.18 现已发布，这是 Kyverno 在 CNCF 毕业后的首个版本。

本次发布进一步巩固了 Kyverno 作为 Kubernetes 原生策略引擎的定位，重点投入方向包括安全、CLI 能力以及策略引擎可靠性。同时，Kyverno 也在继续向基于 CEL 的策略类型演进，为未来的 Policy as Code 奠定基础。

TL;DR

Kyverno 1.18 带来了以下更新：

- 面向基于 HTTP 的策略执行，提供更强的安全控制，并缓解多个 CVE 问题
- 大幅增强 CLI 能力，用于测试和应用现代策略类型
- 提升策略引擎在性能、可观测性和可扩展性方面的表现
- 增强 policies Helm chart，支持更灵活的自定义配置

本次发布没有破坏性变更，但 ClusterPolicy 的弃用计划仍在推进，用户应开始迁移到新的策略类型。

安全改进

安全一直是 Kyverno 的核心支柱。1.18 版本为策略执行引入了多项重要防护能力。

更安全的 HTTP 执行

Kyverno 策略可以通过 HTTP CEL 库调用外部服务。在 1.18 中，这一能力得到了显著加固：

- 阻止列表 / 允许列表强制执行：默认情况下，loopback、元数据服务等不安全地址会被阻止。用户可以为集群级策略和命名空间级策略配置允许列表和阻止列表。此外，来自命名空间级策略的 HTTP 调用默认被禁用，需要通过配置标志显式开启。这些变更有助于防止 SSRF 类型的滥用。更多细节可参考 CVE-2026-4789。
- 作用域 token 授权：此前，Kyverno HTTP 调用中包含的 token 可能被用于冒充 Kyverno 控制器。现在，HTTP 调用会携带一个单独的、具备作用域限制的 token，确保服务端无法滥用该 token。更多细节可参考 CVE-2026-41323。

这些变化在保持高级策略场景灵活性的同时，降低了非预期外部访问的风险。

CLI 扩展与开发者体验

Kyverno CLI 正在持续演进，成为策略开发和测试中的关键工具。

扩展策略支持

kyverno apply 和 kyverno test 命令现在支持：

- Cleanup policies
- HTTP 和 Envoy 授权策略
- MutatingPolicy 中的 mutateExisting 规则
- \--exceptions-with-policies 标志，用于改进测试工作流

这显著提升了在本地环境和 CI 流水线中测试现代策略类型的能力。

可靠性与易用性改进

本次版本还修复了多个问题，涉及：

- 错误处理与错误报告
- 无集群连接场景下的 CRD 兼容性
- panic、文件句柄泄漏等稳定性问题

这些改进让用户在处理策略时获得更可预测、更友好的开发体验。

策略引擎改进

Kyverno 1.18 包含多项增强，用于改进策略在大规模环境中的执行和管理方式。

更细粒度的成功事件过滤

新的 successEventActions ConfigMap 参数允许用户控制：

- 哪些成功事件会被发出
- 策略报告的噪声程度

这对于大型环境尤其有价值，因为在这些环境中，事件数量往往需要进行调优。

性能与可扩展性

关键改进包括：

- admission controller 支持基于内存的 HPA 自动扩缩容
- /metrics 端点支持 TLS
- 改进并发处理，降低竞态条件风险

这些变化让 Kyverno 在大规模生产环境中更加可靠。

CEL 与策略执行增强

- 新增 gzip CEL 库，支持更高级的表达式
- 改进策略变量和条件的编译与求值
- 改善策略类型与执行引擎之间的一致性

镜像验证改进

本次版本还对镜像验证能力进行了多项针对性改进：

- 对于 ClusterPolicies，imageRegistryCredentials.secrets 现在支持 namespace/name 表示法；同时，Pod 级别的 imagePullSecrets 会自动被用作镜像仓库凭证。这对于多租户环境很有用，因为每个命名空间通常会管理自己的 pull secrets。
- ImageValidatingPolicy 可靠性修复，包括更好地处理签名时间戳和 TSA 证书链、Notary resolver 修复、正确的 matchImageReferences 过滤，以及改进命名空间级策略的 autogen 支持。

Policies Helm chart 增强

policies Helm chart 也在持续演进，提供更好的自定义能力和控制能力。

新增能力包括：

- 在 ValidatingPolicies 中支持 excludes，包括 namespace、subject、resource rules 和 match conditions
- auditAnnotation 配置
- 每个策略级别的 annotation 覆盖

这些改进让用户可以更容易地根据组织和运维需求定制策略。

支持策略更新

随着 Kyverno 的采用规模、贡献数量以及项目整体范围持续增长，社区也在调整发布支持方式。

从 1.18 版本开始，Kyverno 将采用 “main + 1” 补丁支持模型。

这意味着：

- 当前版本（main）和上一个版本会获得补丁支持。补丁范围仅限于严重和高危 CVE，以及其他关键修复。这大约提供 3 个月的社区补丁支持。
- 更早版本将不再获得常规更新或修复。

为什么做出这一调整

这一调整可以帮助维护者团队：

- 更高效地管理由 AI 驱动带来的安全问题和 PR 数量增长
- 在安全性和响应速度方面保持更高标准
- 将精力集中在当前版本和活跃使用版本上
- 在项目规模扩大时，保持项目可持续和可管理

这对用户意味着什么

我们建议用户：

- 保持使用较新的 Kyverno 版本
- 根据约 3 个月的支持窗口规划升级，或者使用能够提供更高 SLA 和长期支持的商业发行版
- 如需指导，可联系社区

这一变化将确保 Kyverno 能够继续为所有用户交付安全、稳定且持续向前演进的项目。

ClusterPolicy 弃用提醒

再次提醒，ClusterPolicy 资源计划在今年晚些时候弃用。

我们强烈建议用户开始迁移到新的策略类型：

- ValidatingPolicy
- MutatingPolicy
- GeneratingPolicy
- ImageValidatingPolicy
- DeletingPolicy

用户应该做什么

- 开始迁移现有策略
- 使用 CLI 进行充分测试
- 反馈功能差距或问题

社区反馈对于确保平滑迁移和实现完整功能对齐至关重要。我们希望用户积极报告问题，并帮助项目在未来几个月内实现完整的功能一致性。

加入社区

Kyverno 社区会议现在提供多个更适合全球社区参与的时间段：

- APAC / EU：每隔一周周三 9:00 CET / 印度 13:30 / 欧洲 09:00 / 新加坡 16:00 / 澳大利亚 18:00
- USA / LATAM：每隔一周周三 16:00 CET / 印度 20:30 / 欧洲 16:00 / 纽约 10:00 / 旧金山 7:00

用户可以在 CNCF Calendar 中使用 Kyverno 过滤器查看所有会议。

此外，社区正在创建一个空间，让社区成员能够在社区博客中发布案例研究和使用案例，希望它能够成为大家互相学习的场所。请持续关注该博客版块上线的相关公告。

如果你希望提交使用案例或案例研究，可以直接联系 ：

cortney.nickerson@nirmata.com。

接下来

展望未来，Kyverno roadmap 将重点关注：

- 持续投入基于 CEL 的策略类型
- 改进策略编写体验
- 在多集群环境中扩展策略能力
- 拓展 AI governance 与策略驱动自动化能力

结语

Kyverno 1.18 是项目在 CNCF 毕业后的重要一步。

通过更强的安全能力、扩展后的 CLI 能力，以及对策略引擎可靠性和 Kubernetes 原生策略的持续投入，Kyverno 正在帮助团队从策略执行走向大规模的策略驱动运维。

随着项目不断成长，Kyverno 也在调整自身运作方式，以确保长期可持续发展。转向 N-1 支持模型，体现了社区对高质量发布的承诺，也帮助项目跟上快速扩大的社区和生态需求。

升级到 Kyverno 1.18，保持使用受支持的版本，开始迁移到新的策略类型，并一起构建 Policy as Code 的未来。

作者：Cortney Nickerson，Kyverno Contributor

原文链接：

https://www.cncf.io/blog/2026/05/05/announcing-kyverno-release-1-18/

Kyverno CNCF 毕业公告：

https://www.cncf.io/announcements/2026/04/02/cloud-native-computing-foundation-announces-kyverno-graduation/

CVE-2026-4789：

https://github.com/kyverno/kyverno/security/advisories/GHSA-xxxx

CVE-2026-41323：

https://github.com/kyverno/kyverno/security/advisories/GHSA-xxxx

CNCF Calendar：

https://www.cncf.io/calendar/

Kyverno 安装页面：

https://kyverno.io/docs/installation/

Kyverno GitHub release notes：

https://github.com/kyverno/kyverno/releases

Kyverno roadmap：

https://github.com/kyverno/kyverno/milestones

## 2026 KubeCon + CloudNativeCon + OpenInfra Summit Asia + PyTorch Conference China 议题征集与注册现已盛大开启！

## 立即下载赞助商企划书（https://cncf.io/sponsor）了解赞助方案和市场推广机会。

CNCF概况（幻灯片）

扫描二维码联系我们！

---

***CNCF (Cloud Native Computing Foundation)成立于2015年12月，隶属于Linux Foundation，是非营利性组织。***

******CNCF****** ***（*** ******云原生计算基金会*** ）致力于培育和维护一个厂商中立的开源生态系统，来推广云原生技术。我们通过将最前沿的模式民主化，让这些创新为大众所用。请关注CNCF微信公众号。***

阅读原文

继续滑动看下一个

CNCF

向上滑动看下一个