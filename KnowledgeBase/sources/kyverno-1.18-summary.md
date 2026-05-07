---
title: Kyverno 1.18 新特性摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/security
  - kyverno
date: 2026-05-07
sources:
  - "[[Docker-Kubernetes/k8s-security-auth/Kyverno-1.18-新特性]]"
aliases:
  - Kyverno 1.18 Summary
---

# Kyverno 1.18 新特性摘要

## 元信息
- **原始文档**：[[Docker-Kubernetes/k8s-security-auth/Kyverno-1.18-新特性]]
- **领域**：Kubernetes 安全 / 策略引擎
- **摄入日期**：2026-05-07
- **原文来源**：https://www.cncf.io/blog/2026/05/05/announcing-kyverno-release-1-18/

## 摘要

Kyverno 1.18 是 CNCF 毕业后的首个版本，重点投入安全加固（HTTP 调用的 SSRF 防护与 token 作用域限制）、CLI 能力扩展（支持现代策略类型的测试与应用）以及策略引擎的性能与可观测性提升。同时继续推进基于 CEL 的策略类型演进，为 Policy as Code 奠定基础。

## 关键知识点

1. **HTTP 调用安全加固**：引入阻止列表/允许列表机制防止 SSRF，命名空间级策略的 HTTP 调用默认禁用；HTTP 调用使用作用域 token 替代控制器 token，修复 CVE-2026-4789 和 CVE-2026-41323
2. **CLI 扩展**：`kyverno apply` 和 `kyverno test` 支持 Cleanup policies、HTTP/Envoy 授权策略、MutatingPolicy 的 mutateExisting 规则，提升 CI 流水线中的策略测试能力
3. **策略引擎增强**：新增 `successEventActions` 参数控制事件噪声；admission controller 支持基于内存的 HPA；`/metrics` 端点支持 TLS；改进并发处理降低竞态风险
4. **CEL 演进**：新增 gzip CEL 库，改进策略变量和条件的编译与求值，提升策略类型与执行引擎的一致性
5. **镜像验证增强**：`imageRegistryCredentials.secrets` 支持 `namespace/name` 表示法，Pod 的 `imagePullSecrets` 自动用作仓库凭证，适应多租户环境
6. **Policies Helm Chart**：ValidatingPolicies 支持 excludes（namespace/subject/resource rules/match conditions）、`auditAnnotation` 配置、策略级 annotation 覆盖
7. **N-1 支持模型**：从 1.18 起采用 "main + 1" 补丁支持，约 3 个月支持窗口，更早版本不再维护
8. **ClusterPolicy 弃用**：计划年内弃用，用户应迁移至 ValidatingPolicy / MutatingPolicy / GeneratingPolicy / ImageValidatingPolicy / DeletingPolicy

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kyverno]]：本次发布的主体
- [[KnowledgeBase/entities/Kubernetes]]：Kyverno 的运行平台
- [[KnowledgeBase/entities/Helm]]：Policies Helm Chart 增强
- [[KnowledgeBase/concepts/策略即代码]]：Kyverno 的核心理念（Policy as Code）

## 值得注意

- **CNCF 毕业标志**：Kyverno 于 2026 年 4 月正式从 CNCF 毕业，1.18 是毕业后首个版本，意味着项目已达到生产就绪和社区治理成熟度
- **CEL 方向明确**：Kyverno 正从传统的 YAML overlay 策略模式向 CEL 表达式演进，这与 Kubernetes 自身的 ValidatingAdmissionPolicy（KEP-3488）方向一致
- **AI governance 路线图**：Roadmap 中提到"拓展 AI governance 与策略驱动自动化能力"，预示策略引擎将扩展到 AI 工作负载治理领域
- **ClusterPolicy 迁移窗口**：弃用计划 + N-1 支持模型意味着用户需要在约 6 个月内完成策略迁移
