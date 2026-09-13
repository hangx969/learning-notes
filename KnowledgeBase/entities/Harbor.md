---
title: Harbor
tags:
  - knowledgebase/entity
  - container-registry
date: 2026-09-13
sources:
  - "[[KnowledgeBase/sources/k8s-misc-batch-summary]]"
  - "[[KnowledgeBase/sources/dragonfly-harbor-p2p-distribution-summary]]"
aliases:
  - Harbor Registry
---

# Harbor

## 简介

Harbor 是 CNCF 开源的企业级 OCI 制品与容器镜像仓库，为容器化交付提供项目隔离、身份认证、权限控制、复制、安全扫描和 Registry 服务。它可以作为 Dragonfly 等 P2P 分发系统的源站，并通过 P2P Preheat 策略把镜像预热到外部分发网络。

## 核心功能

- **制品存储与 Registry**：管理容器镜像和 OCI 制品。
- **项目与权限**：通过项目、用户、机器人账号和 RBAC 控制访问。
- **安全与治理**：支持漏洞扫描、内容信任、标签保留和垃圾回收等能力。
- **复制与代理缓存**：在仓库之间复制制品，或缓存上游 Registry。
- **P2P Preheat**：对接 Dragonfly 等外部 P2P Provider，按项目策略预热镜像。

## 使用场景

- 企业内部私有镜像仓库
- Kubernetes 与 CI/CD 的镜像交付中心
- 多站点镜像复制和上游代理缓存
- 大规模集群中作为 Dragonfly P2P 分发的源站

## 相关概念与实体

- [[KnowledgeBase/entities/Docker]]：镜像构建、推送和拉取客户端
- [[KnowledgeBase/entities/Kubernetes]]：Harbor 镜像的主要消费环境
- [[KnowledgeBase/entities/Helm]]：Harbor 的 Kubernetes 部署方式
- [[KnowledgeBase/entities/Dragonfly]]：P2P 镜像与大文件分发层
- [[KnowledgeBase/concepts/P2P分发]]：大规模并发分发模式
- [[KnowledgeBase/entities/containerd]]：Kubernetes 节点常见容器运行时

## 在本仓库中的覆盖

- [[Docker-Kubernetes/harbor/harbor-basics]]：自签名证书、Docker Compose 安装和基本镜像操作
- [[Docker-Kubernetes/harbor/helm部署harbor]]：使用 Helm 在 Kubernetes 中部署 Harbor
- [[Docker-Kubernetes/harbor/Dragonfly与Harbor-P2P镜像分发]]：Harbor 源站瓶颈、Dragonfly P2P 卸载和 AI 大文件分发
- [[Docker-Kubernetes/kubeblocks/kubeblocks部署高可用harbor集群]]：使用外部 PostgreSQL 与 Redis 构建高可用后端

## 版本边界

- Harbor 的 P2P Preheat 依赖外部 P2P 引擎，不会由 Harbor 自身替代运行时的下载链路。
- Harbor 与 Dragonfly 的版本组合必须按照官方兼容矩阵确认。

## 知识空白

- Harbor 高可用部署的完整容量规划和故障演练
- 制品签名、SBOM、复制策略和垃圾回收的生产治理
- P2P Preheat 策略的端到端配置与观测
