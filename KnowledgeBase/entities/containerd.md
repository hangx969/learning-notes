---
title: containerd
tags:
  - knowledgebase/entity
  - container-runtime
date: 2026-04-17
---

## 简介

containerd 是从 Docker 中剥离出的工业级容器运行时，自 Kubernetes 1.24 起成为默认容器运行时（取代 dockershim）。它实现了 CRI（Container Runtime Interface）标准，负责镜像管理、容器生命周期管理和底层存储/网络。

## 在本仓库中的位置

- `Docker-Kubernetes/k8s-installation/` 中涉及 containerd 作为 K8s 运行时的配置
- `Docker-Kubernetes/k8s-basic-resources/` 中涉及容器运行时选型
- Azure AKS 集群默认使用 containerd 运行时

## 相关概念与实体

- [[KnowledgeBase/concepts/容器运行时|容器运行时]]：containerd 所属的概念类别
- [[KnowledgeBase/entities/Docker|Docker]]：containerd 从 Docker 项目中剥离而来
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：K8s 1.24+ 默认运行时
- [[KnowledgeBase/entities/AKS|AKS]]：Azure AKS 默认使用 containerd
