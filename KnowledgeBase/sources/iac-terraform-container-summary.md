---
title: Terraform 容器管理 来源摘要
tags:
  - knowledgebase/source
  - IaC/terraform
  - docker-kubernetes/container
date: 2026-05-04
sources:
  - "[[IaC/terraform-container-management]]"
aliases:
  - Terraform容器管理摘要
---

# Terraform 容器管理 来源摘要

## 元信息
- **原始文档**：`IaC/terraform-container-management.md`
- **领域**：IaC / 容器编排
- **摄入日期**：2026-05-04

## 摘要
介绍 Terraform 如何通过 Docker Provider、Kubernetes Provider 和 Helm Provider 统一管理容器基础设施，涵盖 Docker 镜像管理、EKS 集群部署/配置、YAML/HCL 资源定义、NetworkPolicy、Helm Chart（Redis/Prometheus/Grafana）及 Nomad 调度。

## 关键知识点
1. Docker Provider 支持本地/远程镜像，`keep_locally = true` 用于自研镜像管理
2. 区分集群部署（新建 EKS）与集群配置（添加 namespace），使用不同 Terraform 模块
3. `kubernetes_manifest` 资源支持直接加载 YAML，也可用纯 HCL 编写 K8s 资源
4. NetworkPolicy 通过 `pod_selector` + `policy_types` 精细控制 Pod 间流量
5. Helm Provider 将 Helm Release 纳入 Terraform 状态管理，支持 Prometheus + Grafana 一键部署
6. Nomad 适合混合调度场景（容器+非容器化应用）

## 涉及的概念与实体
- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/entities/Docker|Docker]]
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/entities/Helm|Helm]]
- [[KnowledgeBase/entities/Prometheus|Prometheus]]
- [[KnowledgeBase/entities/Grafana|Grafana]]
- [[KnowledgeBase/entities/AKS|AKS]]（EKS 类似）
