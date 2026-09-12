---
title: Kustomize Base 与 Overlay 多环境配置来源摘要
tags:
  - knowledgebase/source
  - kubernetes/configuration
date: 2026-09-12
sources:
  - "[[Docker-Kubernetes/k8s-CICD/Kustomize/Kustomize入门-Base与Overlay多环境配置]]"
aliases:
  - Kustomize 多环境配置摘要
---

# Kustomize Base 与 Overlay 多环境配置来源摘要

## 元信息

- **原始文档**：[[Docker-Kubernetes/k8s-CICD/Kustomize/Kustomize入门-Base与Overlay多环境配置]]
- **原始剪藏**：[[0raw/Kustomize 入门：用 Base 和 Overlay 管理 Kubernetes 多环境配置]]
- **领域**：Kubernetes 配置管理
- **摄入日期**：2026-09-12

## 摘要

本文从多环境 YAML 重复与配置漂移问题出发，介绍 Kustomize 的无模板定制模型，以及 Base 复用公共配置、Overlay 只描述环境差异的分层方式。文章进一步解释 `kustomization.yaml` 的作用，逐项覆盖 `resources`、`namespace`、`images`、`replicas`、`labels` 和 `patches`，并给出构建、差异检查与部署顺序。

## 关键知识点

1. Base 保存跨环境稳定的 Deployment、Service、探针、端口、Volume 与基础标签；Overlay 引用 Base，只声明 Namespace、镜像、副本、资源限制和调度规则等环境差异。
2. Base 与 Overlay 都不是 Kubernetes API 资源，而是包含 `kustomization.yaml` 的目录；Base 不需要知道有哪些 Overlay。
3. Overlay 应使用 `resources` 引用 Base；Kustomize 当前源码将 `bases` 标记为弃用并建议迁移到 `resources`。
4. `namespace` 只为命名空间作用域资源写入 Namespace，不会自动创建 Namespace 对象。
5. `images.name` 匹配镜像名而不是容器名；`replicas.name` 匹配工作负载的 `metadata.name`。
6. 环境标签可通过 `labels` 加入资源和 Pod Template；对可变环境标签应谨慎设置 `includeSelectors`，避免修改不可变或承担匹配关系的 Selector。
7. 常见差异优先用专用字段，复杂差异使用 `patches`；小补丁应保持单一职责，便于审查和复用。
8. `kubectl kustomize` 只生成清单，`kubectl diff -k` 比较期望状态，`kubectl apply -k` 才会构建并提交给 API Server。
9. `kustomization.yaml` 不能用 `kubectl apply -f` 当作普通 Kubernetes 对象提交。
10. 独立 Kustomize 与 `kubectl` 内置版本可能不同，字段兼容性必须以当前客户端版本为准。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kustomize]]
- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/entities/Helm]]
- [[KnowledgeBase/entities/ArgoCD]]
- [[KnowledgeBase/concepts/CICD]]

## 值得注意

- Kubernetes 官方任务文档仍展示部分旧字段的功能表；Kustomize 当前源码则明确将 `bases`、`commonLabels`、`patchesStrategicMerge`、`patchesJson6902` 和 `vars` 标记为弃用。实际使用应以所运行版本及其警告为准。
- 本文没有给出完整可运行项目，重点是建立 Base/Overlay 心智模型和字段边界；实操前应先渲染并审查最终 YAML。
