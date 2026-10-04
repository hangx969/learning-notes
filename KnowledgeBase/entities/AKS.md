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

## 核心功能
- **托管控制面**：apiserver、scheduler、etcd、controller 由 Azure 托管，工作节点（kubelet、kube-proxy、容器运行时）由用户管理；AKS 为集群管理预留节点资源，节点规格越大预留越多
- **节点池与资源组**：集群至少需要一个 system 节点池，节点池创建后 VM 规格不可修改；基于 VMAS 的集群只能使用一个节点池，且不能直接转为 VMSS；AKS 自动创建 `MC_` 节点资源组，存放节点 VM、虚拟网络和存储
- **弹性伸缩**：HPA 调整 Pod 副本数；Cluster Autoscaler 在 Pod 因资源不足无法调度时增加节点，空闲时缩减节点；突发负载可借助 ACI 虚拟节点，但集群仍需至少一个工作节点
- **版本升级与证书**：用 `az aks get-upgrades`、`az aks upgrade` 升级，不支持跳版本（当前版本已不受支持时除外），可配置自动升级通道；启用 TLS Bootstrapping 后，升级会自动轮换集群证书
- **Pod 身份与密钥**：Workload Identity 通过 OIDC Issuer 和 Federated Identity Credential，让 Kubernetes ServiceAccount 使用 Azure 托管标识；SecretProviderClass 通过 Secrets Store CSI Driver 将 Key Vault 内容挂载为卷，并可同步为 Kubernetes Secret

## 使用场景
- 企业级 K8s 托管：免运维控制面，专注业务负载
- 混合云架构：Azure Arc 纳管本地 K8s 集群
- DevOps 全链路：与 Azure DevOps Pipeline、ACR 深度集成

## 在本仓库中的覆盖
主要出现在 `Azure/` 目录中与 AKS 相关的文章，同时与 `Docker-Kubernetes/` 下的 Kubernetes 基础资源、网络、监控等内容紧密关联。


- [[Azure/2_AKS-basics|2_AKS-basics]]
- [[Azure/3_AKS-workload-identity|3_AKS-workload-identity]]
- [[Azure/4_AKS-SecretProviderClass-KeyVault|4_AKS-SecretProviderClass-KeyVault]]
- [[Azure/7_ACR-ACI|Azure ACR and ACI]]
- [[Azure/6_Azure-Networking|6_Azure-Networking]]

## 相关概念与实体
- [[KnowledgeBase/entities/Azure|Azure]]
- [[KnowledgeBase/concepts/CICD|CICD]]
- [[KnowledgeBase/concepts/Observability|Observability]]
- [[KnowledgeBase/concepts/服务网格|服务网格]]
- [[KnowledgeBase/concepts/容器运行时|容器运行时]]
- [[KnowledgeBase/entities/Terraform|Terraform]]

## 知识空白
- AKS 与 Azure CNI / Kubenet 网络模型对比
- AKS GitOps 集成（Flux / ArgoCD）
- AKS 成本优化（Spot 节点、Karpenter）
- AKS 与 Azure Monitor / Managed Prometheus 集成
