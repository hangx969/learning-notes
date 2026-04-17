---
title: NFS
tags:
  - knowledgebase/entity
  - storage
date: 2026-04-17
aliases:
  - Network File System
---

## 简介

NFS（Network File System）是经典的网络文件系统协议，在 Kubernetes 中常用作 PV/PVC 的后端存储。NFS 部署简单但缺乏高可用性，适合开发测试环境和非关键数据持久化（如 Jenkins 工作空间、GitLab 数据），不推荐用于生产数据库。

## 在本仓库中的位置

- `Docker-Kubernetes/k8s-scaling-storage/` 中涉及 NFS 作为 PV 后端存储
- `Docker-Kubernetes/k8s-CICD/` 中涉及 Jenkins、GitLab 使用 NFS 持久化
- `Docker-Kubernetes/k8s-monitoring-logging/` 中涉及 Elasticsearch 使用 NFS 存储
- `Docker-Kubernetes/k8s-db-middleware-UI/` 中涉及中间件存储方案

## 相关概念与实体

- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：NFS 作为 K8s PV/PVC 后端
- [[KnowledgeBase/entities/Jenkins|Jenkins]]：使用 NFS 持久化工作空间
- [[KnowledgeBase/entities/GitLab|GitLab]]：使用 NFS 持久化数据
- [[KnowledgeBase/concepts/StorageClass|StorageClass]]：NFS Provisioner 动态存储
