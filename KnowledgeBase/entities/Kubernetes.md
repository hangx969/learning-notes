---
title: Kubernetes
tags:
  - knowledgebase/entity
date: 2026-04-16
---

# Kubernetes

## 定义
Kubernetes（K8s）是容器编排平台，用于自动化容器化应用的部署、扩缩容与管理。本仓库以 145 篇文章覆盖了 K8s 全生命周期，包括基础资源、网络、存储、监控、CI/CD、安全、扩缩容、备份恢复等主题。

## 在本仓库中的位置
贯穿整个 `Docker-Kubernetes/` 目录树，涵盖以下子目录：
- `k8s-basic-resources/` — Pod、Deployment、Service、Ingress、ConfigMap 等基础资源
- `k8s-installation-management/` — 集群安装与管理
- `k8s-networking-service-mesh/` — 网络与服务网格
- `k8s-monitoring-logging/` — 监控与日志
- `k8s-CICD/` — CI/CD 工具链
- `k8s-security-auth/` — 安全与认证
- `k8s-scaling/` — 扩缩容
- `k8s-storage/` — 存储
- `k8s-backup-dr/` — 备份与灾恢
- `k8s-db-middleware/` — 数据库与中间件
- `k8s-ai-gpu/` — AI 与 GPU
- `CKA-CKS/` — 认证考试

## 相关文章
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源|k8s基础-架构-组件-资源]]
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-pod|k8s基础-pod]]
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-deployment|k8s基础-deployment]]
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-Service|k8s基础-Service]]
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-ingress|k8s基础-ingress]]
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-configMap-Secret|k8s基础-configMap-Secret]]
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-storage|k8s基础-storage]]
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-容器运行时-containerd|k8s基础-容器运行时-containerd]]
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-认证-授权-准入|k8s基础-认证-授权-准入]]

## 关联概念
- [[KnowledgeBase/entities/Docker|Docker]]
- [[KnowledgeBase/entities/Helm|Helm]]
- [[KnowledgeBase/entities/Ingress|Ingress]]
- [[KnowledgeBase/entities/Istio|Istio]]
- [[KnowledgeBase/entities/Prometheus|Prometheus]]
- [[KnowledgeBase/entities/Grafana|Grafana]]
- [[KnowledgeBase/entities/ArgoCD|ArgoCD]]
- [[KnowledgeBase/entities/Jenkins|Jenkins]]

## 可延展方向
- Kubernetes Gateway API 替代 Ingress
- K8s 多集群管理与联邦
- K8s FinOps 成本优化
