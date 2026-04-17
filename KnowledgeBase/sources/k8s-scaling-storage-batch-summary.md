---
title: k8s-scaling 与 k8s-storage 来源批量摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/scaling
  - docker-kubernetes/storage
date: 2026-04-17
sources:
  - "[[Docker-Kubernetes/k8s-scaling/helm部署goldilocks]]"
  - "[[Docker-Kubernetes/k8s-scaling/helm部署vpa]]"
  - "[[Docker-Kubernetes/k8s-scaling/k8s-基于KEDA的弹性能力]]"
  - "[[Docker-Kubernetes/k8s-scaling/k8s-HPA-VPA]]"
  - "[[Docker-Kubernetes/k8s-storage/k8s-分布式存储CubeFS]]"
  - "[[Docker-Kubernetes/k8s-storage/helm部署nfs-subdir-external-provisioner]]"
  - "[[Docker-Kubernetes/k8s-storage/k8s-ceph部署与集成]]"
---

## 元信息

- **原始目录**: `Docker-Kubernetes/k8s-scaling/` 与 `Docker-Kubernetes/k8s-storage/`
- **文档数量**: 7 篇（扩缩容 4 篇 + 存储 3 篇）
- **领域**: Kubernetes 自动扩缩容（HPA/VPA/KEDA）与分布式存储（NFS/Ceph/CubeFS）
- **摄入日期**: 2026-04-17

## 整体概述

本批次摘要覆盖了 Kubernetes 集群的两大基础能力：自动扩缩容和持久化存储。扩缩容部分系统性介绍了 HPA（水平扩缩）、VPA（垂直扩缩）、KEDA（事件驱动扩缩）三种方案及其部署工具（Goldilocks 资源推荐），从原生能力到高级事件驱动扩展形成完整体系。存储部分涵盖了从简单的 NFS 动态供应到企业级分布式存储（Ceph、CubeFS）的部署与 K8s 集成，为有状态应用提供可靠的数据持久化方案。

## 各文档摘要

### [[Docker-Kubernetes/k8s-scaling/helm部署goldilocks|Helm 部署 Goldilocks]]

**核心内容**: Goldilocks 是一个开源工具，通过分析 VPA 推荐值帮助确定工作负载的合理 resource request/limit 设置。

- 依赖 VPA Recommender 组件提供资源推荐数据
- 提供 Web Dashboard 可视化展示推荐值
- 支持 `--on-by-default` 为所有 Namespace 创建 VPA 对象
- 可通过 `--exclude-namespaces` 和 `--ignore-controller-kind` 排除特定资源
- 集成 OAuth2 Proxy 实现访问认证

### [[Docker-Kubernetes/k8s-scaling/helm部署vpa|Helm 部署 VPA]]

**核心内容**: VPA（垂直 Pod 自动扩缩容）自动为 Pod 设置合理的 resource request，通过 Fairwinds Helm Chart 部署。

- 三个组件：Updater（更新 Pod 资源）、Admission Controller（拦截创建请求）、Recommender（推荐资源值）
- 必须依赖 Metrics Server（Chart 可自带安装）
- kubeadm 集群中自带 Metrics Server 子 Chart 可能启动失败（需 `--kubelet-insecure-tls`）
- 可仅启用 Recommender 模式（不自动更新，只提供推荐）

### [[Docker-Kubernetes/k8s-scaling/k8s-基于KEDA的弹性能力|KEDA 事件驱动扩缩容]]

**核心内容**: KEDA 是下一代事件驱动自动扩缩器，支持基于事件、消息队列、流量、自定义指标和定时策略的扩缩容，甚至支持缩容到 0。

- 解决原生 HPA 仅基于 CPU/内存的局限性
- 核心 CRD：ScaledObject（控制 Deployment 副本数）、ScaledJob（触发一次性 Job）、TriggerAuthentication（外部事件源认证）
- 架构：Controller -> Scaler -> HPA 协同完成扩缩容
- 支持数十种外部事件源：Kafka、RabbitMQ、HTTP 请求数、Cron 定时等
- 独特优势：缩容到 0（Serverless 模式），适用于大数据处理等场景

### [[Docker-Kubernetes/k8s-scaling/k8s-HPA-VPA|HPA 与 VPA 自动扩缩容]]

**核心内容**: 系统性介绍 K8s 四种自动扩缩容方案（HPA、VPA、KPA、Cluster Autoscaler）的原理、工作机制和使用约束。

- HPA：基于 Metrics Server 的 CPU/内存水平扩缩，默认 30s 检测、5min 稳定期，算法相对保守
- VPA：垂直调整 Pod 的 request/limit，不能与 HPA 同时使用，优化节点资源利用率
- KPA（Knative Pod Autoscaler）：基于并发请求数扩缩，可与 HPA 混用
- Cluster Autoscaler：节点级别弹性伸缩，自动创建/删除节点
- HPA 要求 Pod 必须配置 requests，算法为 `sum(实际使用量) / 使用率限额 + 1`

### [[Docker-Kubernetes/k8s-storage/k8s-分布式存储CubeFS|K8s 分布式存储 CubeFS]]

**核心内容**: 对比单节点存储 vs 分布式存储的优劣，详细比较 Ceph 与 CubeFS 两大平台，阐述在 K8s 上落地分布式存储的优势。

- 单节点存储问题：单点故障、性能瓶颈、扩容复杂、仅支持文件存储
- 分布式存储优势：无限扩容、数据冗余、多副本/纠删码、负载均衡、多存储类型
- Ceph vs CubeFS：Ceph 支持块/对象/文件三种存储但部署复杂；CubeFS 轻量级适合云原生但不支持块存储
- K8s 上部署优势：简化管理（Helm IaC）、自动化运维、一键扩展（DaemonSet）、故障自愈

### [[Docker-Kubernetes/k8s-storage/helm部署nfs-subdir-external-provisioner|Helm 部署 NFS Provisioner]]

**核心内容**: 部署 nfs-subdir-external-provisioner 实现 K8s PV 的动态供应，将现有 NFS 服务器对接 StorageClass。

- NFS 服务端部署：安装 nfs-utils、配置共享目录和 exports
- nfs-subdir-external-provisioner：替代已归档的 nfs-client-provisioner
- 支持通过 StorageClass 动态创建 PV，无需手动创建 PV 资源
- 注意 exports 配置需写宿主机网段（非 Pod 网段），因 PV 先挂载到宿主机再挂载到 Pod

### [[Docker-Kubernetes/k8s-storage/k8s-ceph部署与集成|K8s Ceph 部署与集成]]

**核心内容**: Ceph 分布式存储系统的完整介绍，包含三种存储类型（块/文件系统/对象）、核心组件和集群搭建。

- 三种存储类型：RBD（块存储，高性能单挂载）、CephFS（文件系统，共享挂载）、RADOS Gateway（对象存储，HTTP 协议）
- 核心组件：Monitor（集群状态映射）、Manager（运行时指标）、OSD（对象存储守护进程）、MDS（文件系统元数据）
- 最低要求：3 Monitor + 2 Manager + 3 OSD
- 生产环境强烈建议二进制安装在服务器上，不要装在 K8s 中（数据恢复困难）

## 涉及的概念与实体

- [[KnowledgeBase/concepts/HPA]]: 水平 Pod 自动扩缩容
- [[KnowledgeBase/concepts/VPA]]: 垂直 Pod 自动扩缩容
- [[KnowledgeBase/concepts/KEDA]]: 事件驱动自动扩缩容
- [[KnowledgeBase/concepts/Cluster-Autoscaler]]: 节点级别弹性伸缩
- [[KnowledgeBase/concepts/分布式存储]]: 多节点数据冗余存储架构
- [[KnowledgeBase/concepts/StorageClass]]: K8s 动态存储供应
- [[KnowledgeBase/concepts/PV-PVC]]: 持久卷与持久卷声明
- [[KnowledgeBase/entities/Goldilocks]]: 资源推荐可视化工具
- [[KnowledgeBase/entities/VPA]]: 垂直扩缩容组件
- [[KnowledgeBase/entities/KEDA]]: 事件驱动扩缩器
- [[KnowledgeBase/entities/Metrics-Server]]: K8s 资源指标服务
- [[KnowledgeBase/entities/CubeFS]]: 云原生分布式存储（OPPO 开源）
- [[KnowledgeBase/entities/Ceph]]: 企业级分布式存储系统
- [[KnowledgeBase/entities/NFS]]: 网络文件系统
- [[KnowledgeBase/entities/Knative]]: Serverless 框架（KPA 来源）

## 交叉主题发现

1. **扩缩容层次体系**: HPA（Pod 水平） -> VPA（Pod 垂直） -> KEDA（事件驱动） -> Cluster Autoscaler（节点级别），四层扩缩能力从应用层到基础设施层逐步递进。
2. **存储与 CI/CD 依赖**: Jenkins、GitLab 等 CI/CD 工具（k8s-CICD 目录）大量使用 NFS PV/PVC 做持久化存储，NFS Provisioner 的动态供应能力直接支撑了 DevOps 工具链的部署。
3. **Metrics Server 枢纽角色**: HPA 和 VPA 均依赖 Metrics Server 提供资源指标，是扩缩容体系的基础组件。
4. **资源优化闭环**: VPA Recommender 提供推荐值 -> Goldilocks 可视化展示 -> 运维人员调整 request/limit -> HPA 基于 request 计算扩缩比例，形成资源优化闭环。
5. **存储选型权衡**: NFS（简单但非高可用） -> CubeFS（云原生友好但无块存储） -> Ceph（功能全面但运维复杂），三种方案适用于不同规模和复杂度的场景。
6. **KEDA 与 Serverless**: KEDA 的缩容到 0 能力与 Knative/KPA 的 Serverless 模式理念一致，反映了事件驱动架构在 K8s 中的深入应用。
