---
title: Rancher
tags:
  - knowledgebase/entity
  - kubernetes/management
date: 2026-04-17
aliases:
  - SUSE Rancher
---

## 简介

Rancher 是 SUSE 旗下的企业级 Kubernetes 多集群管理平台，提供统一的 Web UI 管理多个 K8s 集群（本地、云端、边缘）。同时也是 K3S（轻量级 K8s 发行版）的母公司，在 IoT/边缘计算场景有广泛应用。

## 在本仓库中的位置

- `Docker-Kubernetes/k8s-db-middleware-UI/` 中涉及 Rancher 作为 K8s UI 管理工具
- `Docker-Kubernetes/k8s-misc/` 中涉及 K3S 和 Rancher 在边缘/IoT 场景的应用
- 与 Dashboard、Lens、k9s 等 K8s UI 工具形成生态对比

## 相关概念与实体

- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：Rancher 管理的目标平台
- [[KnowledgeBase/concepts/高可用架构|高可用架构]]：Rancher 自身的 HA 部署
- [[KnowledgeBase/entities/Helm|Helm]]：Rancher 通过 Helm 部署
