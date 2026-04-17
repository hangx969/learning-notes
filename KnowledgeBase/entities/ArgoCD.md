---
title: ArgoCD
tags:
  - knowledgebase/entity
date: 2026-04-17
sources:
  - "[[KnowledgeBase/sources/k8s-CICD-batch-summary|k8s-CICD 来源批量摘要]]"
---

# ArgoCD

## 定义
ArgoCD 是基于 GitOps 理念的 Kubernetes 持续交付（CD）工具，通过监听 Git 仓库变更自动同步应用到集群。本仓库记录了 ArgoCD 基础使用、Image Updater 自动更新镜像、Helm 应用部署及问题排查。

## 编译知识

### 核心架构与组件
- ArgoCD 是 **CNCF 旗下**的声明式 GitOps 持续交付工具，以 Git 仓库作为**唯一事实来源**，自动同步集群状态与期望状态
- 核心组件：**API Server**（Web UI + gRPC/REST API）、**Repository Server**（Git 仓库缓存与模板渲染）、**Application Controller**（状态对比与同步）
- CRD 资源：**AppProject**（逻辑分组与权限隔离）、**Application**（应用定义，关联 Git 来源与目标集群）
- 支持多集群管理、[[KnowledgeBase/entities/Helm|Helm]]/Kustomize/Jsonnet 配置来源、同步波次与钩子、RBAC 和 SSO 集成

### ArgoCD Image Updater
- 自动更新 ArgoCD 管理的容器镜像版本，通过 Annotation 配置跟踪镜像仓库变更
- 支持 **semver、latest、name、digest** 四种更新策略
- 仅支持 Helm 或 Kustomize 渲染的应用

### GitOps vs 传统 CI/CD
- ArgoCD 采用 **Pull 模式**（从集群拉取期望状态），与 [[KnowledgeBase/entities/Jenkins|Jenkins]] 的 **Push 模式**（推送变更到集群）形成两种部署哲学
- 云原生演进趋势：Jenkins（VM 时代） -> Tekton（K8s 原生） -> ArgoCD（GitOps）

### 常见问题
- DNS 解析失败：CoreDNS 上游转发配置不当 + Go 纯 DNS 解析器优先尝试 IPv6 可导致 Helm 应用部署失败
- 排查涉及 CoreDNS forward 插件、Calico CNI、kubeadm 集群环境

## 在本仓库中的位置
主要集中在 `Docker-Kubernetes/k8s-CICD/ArgoCD/` 目录，共 4 篇文章。

## 相关文章
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础|ArgoCD基础]]
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD Image Updater|ArgoCD Image Updater]]
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD部署Helm应用时域名解析失败问题排查与解决|ArgoCD部署Helm应用时域名解析失败问题排查与解决]]
- [[Docker-Kubernetes/k8s-CICD/ArgoCD/学习链接|学习链接]]

## 关联概念
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/entities/Helm|Helm]]
- [[KnowledgeBase/entities/Jenkins|Jenkins]]
- [[KnowledgeBase/entities/Docker|Docker]]

## 可延展方向
- ArgoCD ApplicationSet 多环境管理
- ArgoCD 与 Kustomize 的结合使用
- ArgoCD RBAC 与多租户配置
