---
title: Dragonfly
tags:
  - knowledgebase/entity
  - docker-kubernetes/image-distribution
date: 2026-09-13
sources:
  - "[[KnowledgeBase/sources/k8s-misc-batch-summary]]"
  - "[[KnowledgeBase/sources/dragonfly-harbor-p2p-distribution-summary]]"
aliases:
  - Dragonfly P2P
---

# Dragonfly

## 简介

Dragonfly 是面向云原生与 AI 基础设施的 P2P 文件分发系统，通过复用 Peer 的空闲带宽减少 Registry、对象存储和核心网络上的重复流量。它适用于大规模并发分发容器镜像、模型、Dataset、Checkpoint 和软件包。

## 核心功能

- **分块与 P2P 传输**：将大对象拆成数据块，由多个 Peer 并行交换。
- **调度**：Scheduler 根据任务和 Peer 状态选择父节点，并在需要时触发回源。
- **源站卸载**：Seed Peer 和已有缓存的 Peer 承担重复分发，减少 Harbor 或对象存储的出口流量。
- **多集群管理**：Manager 管理动态配置、P2P 集群关系、指标和控制台；部分部署模型可不使用 Manager。
- **生态集成**：可与 containerd、Harbor P2P Preheat 及 AI/ML 数据分发场景集成。

## 使用场景

- 大规模 Kubernetes 集群并发扩容和镜像拉取
- AI/GPU 集群分发大型运行时镜像
- LLM 模型、Dataset 与 Checkpoint 的批量分发
- 需要降低 Registry、对象存储或跨机架网络出口压力的环境

## 相关概念与实体

- [[KnowledgeBase/concepts/P2P分发]]：核心数据分发模式
- [[KnowledgeBase/entities/Harbor]]：容器镜像源站与预热策略入口
- [[KnowledgeBase/entities/Kubernetes]]：主要编排环境
- [[KnowledgeBase/entities/containerd]]：容器镜像拉取链路中的运行时
- [[KnowledgeBase/concepts/容器运行时]]：Dragonfly 的非侵入式集成对象

## 在本仓库中的覆盖

- [[Docker-Kubernetes/harbor/Dragonfly与Harbor-P2P镜像分发]]：Harbor 源站卸载、AI 大文件分发、新旧架构与适用边界
- [[Docker-Kubernetes/helm-operator/helm部署dragonfly]]：Dragonfly 的 Helm 部署与早期实践

## 版本边界

- Dragonfly v1 已归档，v2 与 v1 不兼容。
- v2 核心角色为 Manager、Scheduler、Seed Peer 和 Peer；Manager 是否必需取决于部署模型。
- Harbor 集成前应核对 Harbor 与 Dragonfly 的官方兼容矩阵。

## 知识空白

- Dragonfly v2 在生产 Kubernetes 中的完整部署、升级与回滚实战
- 拓扑感知调度、跨机架流量控制和容量压测方法
- 模型分发与 Nydus/OCI 加速的实测对比
