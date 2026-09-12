---
title: Kustomize
tags:
  - knowledgebase/entity
  - kubernetes/configuration
date: 2026-09-12
sources:
  - "[[KnowledgeBase/sources/k8s-CICD-batch-summary]]"
  - "[[KnowledgeBase/sources/kustomize-base-overlay-summary]]"
aliases:
  - Kubernetes 原生配置定制工具
---

# Kustomize

## 简介

Kustomize 是 Kubernetes 的无模板配置定制工具，可读取普通 Kubernetes YAML，并依据 `kustomization.yaml` 组合资源、应用转换和补丁。它自 Kubernetes 1.14 起集成到 `kubectl`，适合用 Base 复用公共配置、用 Overlay 描述开发、测试和生产等环境差异。

## 核心功能

- **资源组合**：通过 `resources` 引入资源文件或其他 Kustomization 目录。
- **横切修改**：通过 `namespace`、`labels`、名称前后缀等字段统一修改一组资源。
- **专用变换**：通过 `images`、`replicas` 修改镜像和工作负载副本数。
- **结构化补丁**：通过统一的 `patches` 字段应用 Strategic Merge 或 JSON 6902 补丁。
- **生成配置资源**：通过 `configMapGenerator` 和 `secretGenerator` 从文件或字面量生成资源。
- **构建与部署**：`kubectl kustomize` 只渲染清单，`kubectl diff -k` 比较差异，`kubectl apply -k` 构建并提交资源。

## 使用场景

- 多环境共享同一套工作负载和 Service，只覆盖 Namespace、镜像、副本、资源配额与调度规则。
- 在 GitOps 仓库中维护可审查的声明式环境差异，并交由 ArgoCD 等工具持续同步。
- 不希望在 Kubernetes YAML 中引入模板占位符，但仍需要复用和定制配置。

## 相关概念与实体

- [[KnowledgeBase/entities/Helm|Helm]]：Helm 侧重模板、打包和 Release 生命周期；Kustomize 侧重对原生 YAML 做结构化定制。
- [[KnowledgeBase/entities/ArgoCD|ArgoCD]]：可将 Kustomize 目录作为 GitOps 配置源并渲染期望状态。
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：`kubectl` 内置 Kustomize 支持，并通过 `-k` 操作 Kustomization 目录。
- [[KnowledgeBase/concepts/CICD|CI/CD]]：多环境配置管理是持续交付链路的重要组成部分。

## 在本仓库中的覆盖

- [[Docker-Kubernetes/k8s-CICD/Kustomize/Kustomize入门-Base与Overlay多环境配置|Kustomize Base 与 Overlay 入门]]：当前推荐字段、能力边界、六个常用字段和部署前验证顺序。
- [[Docker-Kubernetes/k8s-CICD/Kustomize/k8s配置定制工具-kustomize|Kustomize 使用指南]]：基础用法、生成器和更多进阶特性；部分示例包含旧字段，需要结合版本辨别。

## 版本边界

- 独立 Kustomize 与 `kubectl` 内置版本可能不同，字段是否可用应以当前客户端版本为准。
- 当前 Kustomize 源码将 `bases`、`commonLabels`、`patchesStrategicMerge`、`patchesJson6902` 和 `vars` 标记为弃用；新项目优先使用 `resources`、`labels`、`patches` 和 `replacements`。

## 知识空白

- Components、Replacements、自定义 Transformer/OpenAPI 配置的完整实战尚未系统覆盖。
- 缺少一套可直接运行并由 CI 验证渲染结果的 Base/Overlay 示例仓库。
