---
title: Kustomize
tags:
  - knowledgebase/entity
  - kubernetes/configuration
date: 2026-04-17
---

## 简介

Kustomize 是 Kubernetes 原生的配置管理工具（自 K8s 1.14 起内置于 kubectl），采用 Base + Overlay 分层模式，无需模板引擎即可实现多环境配置定制。常与 Helm 互补使用，也是 ArgoCD 支持的配置管理方式之一。

## 在本仓库中的位置

- `Docker-Kubernetes/k8s-CICD/` 中涉及 Kustomize 在 GitOps 流程中的应用
- 多篇笔记中与 Helm 进行对比分析

## 相关概念与实体

- [[KnowledgeBase/entities/Helm|Helm]]：对比工具——Helm 用模板引擎，Kustomize 用 Overlay 补丁
- [[KnowledgeBase/entities/ArgoCD|ArgoCD]]：GitOps 中支持 Kustomize 作为配置源
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：K8s 1.14+ 原生集成
- [[KnowledgeBase/concepts/CICD|CI/CD]]：配置管理是 CI/CD 流程的关键环节
