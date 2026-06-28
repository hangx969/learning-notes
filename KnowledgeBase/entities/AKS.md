---
title: AKS
tags:
  - knowledgebase/entity
date: 2026-04-17
sources:
  - "[[KnowledgeBase/sources/azure-batch-summary|Azure 来源批量摘要]]"
aliases:
  - Azure Kubernetes Service
---

# AKS

## 简介
Azure Kubernetes Service（AKS）是 Microsoft Azure 提供的托管 Kubernetes 服务，简化了集群的部署、管理和扩展。本仓库重点记录 AKS 基础操作、Workload Identity 联邦身份认证以及通过 SecretProviderClass 集成 Azure Key Vault 的实践。

## 使用场景
- 企业级 K8s 托管：免运维控制面，专注业务负载
- 混合云架构：Azure Arc 纳管本地 K8s 集群
- DevOps 全链路：与 Azure DevOps Pipeline、ACR 深度集成

## 在本仓库中的覆盖
主要出现在 `Azure/` 目录中与 AKS 相关的文章，同时与 `Docker-Kubernetes/` 下的 Kubernetes 基础资源、网络、监控等内容紧密关联。


- [[Azure/2_AKS-basics|2_AKS-basics]]
- [[Azure/3_AKS-workload-identity|3_AKS-workload-identity]]
- [[Azure/4_AKS-SecretProviderClass-KeyVault|4_AKS-SecretProviderClass-KeyVault]]
- [[Azure/7_ACR-ACI|7_ACR-ACI]]
- [[Azure/6_Azure-Networking|6_Azure-Networking]]

## 相关概念与实体
- [[KnowledgeBase/entities/Azure|Azure]]
- [[KnowledgeBase/concepts/CICD|CICD]]
- [[KnowledgeBase/concepts/Observability|Observability]]
- [[KnowledgeBase/concepts/服务网格|服务网格]]
- [[KnowledgeBase/concepts/容器运行时|容器运行时]]
- [[KnowledgeBase/entities/Terraform|Terraform]]

## 知识空白
- AKS 集群升级与节点池管理策略
- AKS 与 Azure CNI / Kubenet 网络模型对比
- AKS GitOps 集成（Flux / ArgoCD）
- AKS 成本优化（Spot 节点、Karpenter）
- AKS 与 Azure Monitor / Managed Prometheus 集成
