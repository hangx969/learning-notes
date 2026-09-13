---
title: Dragonfly 与 Harbor 的 P2P 镜像和大文件分发
tags:
  - knowledgebase/source
  - docker-kubernetes/harbor
  - docker-kubernetes/dragonfly
  - ai/infrastructure
date: 2026-09-13
sources:
  - "[[Docker-Kubernetes/harbor/Dragonfly与Harbor-P2P镜像分发]]"
aliases:
  - Dragonfly Harbor P2P 分发摘要
---

# Dragonfly 与 Harbor 的 P2P 镜像和大文件分发

## 元信息

- **原始文档**：[[Docker-Kubernetes/harbor/Dragonfly与Harbor-P2P镜像分发]]
- **领域**：Kubernetes 镜像分发、AI 基础设施
- **摄入日期**：2026-09-13
- **原始来源**：[微信公众号文章](https://mp.weixin.qq.com/s/NTEYZHwnhJkh9okx_2-2gQ)

## 摘要

文章解释了大规模 Kubernetes 和 AI/GPU 集群中，集中式 Registry 拉取如何把 Harbor 出口、后端存储和核心网络变成瓶颈。Dragonfly 通过文件分块、Peer 间交换、Seed Peer 回源和 Scheduler 调度，将 Harbor 从重复数据发送者收敛为源站。文章同时比较了 Dragonfly v1 的 Supernode 架构与 v2 的 Manager、Scheduler、Seed Peer、Peer 架构，并区分 Harbor P2P Preheat 策略和运行时镜像拉取链路。

## 关键知识点

1. 100 台节点并发拉取 100 GB 镜像会产生约 10 TB 的理论重复传输量，瓶颈可能同时出现在 Registry 出口、存储 IOPS 和核心交换网络。
2. Dragonfly 将文件切分为数据块，由 Peer 从其他 Peer、Seed Peer 或源站获取；Scheduler 负责选择父节点，不承载主要数据流。
3. Harbor 负责镜像存储、认证、项目、扫描和 Registry 服务，Dragonfly 负责 P2P 分发与缓存，二者不是替代关系。
4. P2P 的收益主要体现在大规模并发和源站卸载；单节点请求会增加调度、分块、缓存与校验开销，未必比直连 Harbor 更快。
5. Dragonfly 可分发镜像、模型、Dataset、Checkpoint 等大对象，但会增加东西向流量、组件数量和故障排查复杂度。
6. Dragonfly v1 已归档且与 v2 不兼容；旧版 Supernode、`df-daemon` 与 Docker `HTTP_PROXY` 示例不应直接用于现代生产部署。
7. Harbor 的 P2P Preheat 依赖外部 P2P 引擎和项目级策略。Harbor 2.14 文档给出的兼容关系是 Harbor `>= 2.12.0` 对应 Dragonfly `>= 2.1.59`。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Harbor]]
- [[KnowledgeBase/entities/Dragonfly]]
- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/entities/containerd]]
- [[KnowledgeBase/concepts/P2P分发]]
- [[KnowledgeBase/concepts/容器运行时]]

## 值得注意

- 原文中的性能数据来自早期 Dragonfly/Supernode 测试环境，适合说明源站流量下降机制，不应直接外推到 Dragonfly v2 或其他网络拓扑。
- Manager 在 Dragonfly v2 的部分部署模型中可以省略；Scheduler 属于控制面，Peer、Seed Peer 和源站才是主要数据路径。
- AI 集群是否值得引入 P2P，应以并发节点数、对象大小、重复率、机架拓扑、东西向带宽和运维成本共同评估。
