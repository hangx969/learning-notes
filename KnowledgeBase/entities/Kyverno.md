---
title: Kyverno
tags:
  - knowledgebase/entity
  - docker-kubernetes/security
  - kyverno
date: 2026-05-07
sources:
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署kyverno和policy-reporter]]"
  - "[[Docker-Kubernetes/k8s-security-auth/helm部署kyverno和policy-reporter]]"
aliases:
  - Kyverno 策略引擎
---

# Kyverno

## 简介

Kyverno（希腊语"govern"之意）是 Kubernetes 原生策略引擎，于 2026 年 4 月从 CNCF 毕业。作为 Admission Controller 运行，通过 CRD 定义策略，无需学习额外的策略语言，直接使用 Kubernetes 原生资源和 YAML 定义验证、变更和生成规则。

## 核心功能

- **验证策略（Validate）**：拦截 API 请求，验证资源是否符合策略（如强制使用指定镜像仓库）
- **变更策略（Mutate）**：自动修改资源配置（如注入 sidecar、添加标签）
- **生成策略（Generate）**：根据事件自动创建资源（如创建 Namespace 时自动生成 NetworkPolicy）
- **镜像验证（Image Verify）**：验证容器镜像签名和来源
- **清理策略（Cleanup）**：自动清理过期或不再需要的资源
- **Policy Reporter**：内置 GUI 界面，展示策略执行结果的可视化报告

## 架构

Kyverno 作为 Kubernetes Admission Controller 运行，拦截 API Server 的请求并根据策略进行处理：

```
kubectl apply → API Server → Kyverno (Webhook) → 验证/变更/拒绝 → etcd
```

## 策略类型演进

Kyverno 正从传统的 ClusterPolicy 向新的策略类型迁移：

| 旧类型 | 新类型 | 说明 |
|--------|--------|------|
| ClusterPolicy (validate) | ValidatingPolicy | 基于 CEL 的验证策略 |
| ClusterPolicy (mutate) | MutatingPolicy | 基于 CEL 的变更策略 |
| ClusterPolicy (generate) | GeneratingPolicy | 资源生成策略 |
| ClusterPolicy (imageVerify) | ImageValidatingPolicy | 镜像验证策略 |
| CleanupPolicy | DeletingPolicy | 资源清理策略 |

## 使用场景

- 强制 Pod 使用指定镜像仓库（如 Harbor）
- 多租户环境下的资源隔离策略
- 安全基线合规（如禁止 privileged 容器）
- 自动为资源添加标签和注解
- CI 流水线中的策略测试（kyverno apply / kyverno test）

## 相关概念与实体

- [[KnowledgeBase/concepts/策略即代码]]：Kyverno 的核心理念（Policy as Code）
- [[KnowledgeBase/entities/Kubernetes]]：运行平台
- [[KnowledgeBase/entities/Helm]]：通过 Helm Chart 部署
- [[KnowledgeBase/concepts/RBAC]]：与 K8s RBAC 配合实现准入控制
- [[KnowledgeBase/concepts/镜像安全]]：镜像验证能力与 Trivy 互补

## 在本仓库中的覆盖

- [[Docker-Kubernetes/k8s-security-auth/helm部署kyverno和policy-reporter]]：Helm 部署 Kyverno 和 Policy Reporter 完整流程，包含 values 配置、策略语法、实战示例（强制使用 Harbor 镜像）
- [[Docker-Kubernetes/k8s-security-auth/helm部署kyverno和policy-reporter]]：1.18 版本新特性——安全加固、CLI 扩展、CEL 演进、N-1 支持模型、ClusterPolicy 弃用迁移路径
- [[KnowledgeBase/sources/kyverno-1.18-summary|Kyverno 1.18 摘要]]：版本摘要与关键知识点提炼
- [[KnowledgeBase/sources/k8s-security-auth-batch-summary|安全认证批量摘要]]：Kyverno 在 K8s 安全工具链中的定位

## 知识空白

- Kyverno vs OPA/Gatekeeper 对比分析
- 基于 CEL 的 ValidatingPolicy 编写实战
- Kyverno 在多集群环境中的策略分发
- AI governance 策略定义实践
