---
title: Kubernetes Volume Health Monitor 来源摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/storage
  - kubernetes/observability
date: 2026-09-06
sources:
  - "[[Docker-Kubernetes/k8s-storage/让存储故障现形：Kubernetes Volume Health Monitor 原理与生产接入]]"
  - "[[0raw/让存储故障现形：Kubernetes Volume Health Monitor 原理与生产接入]]"
aliases:
  - Volume Health Monitor 摘要
---

# Kubernetes Volume Health Monitor 来源摘要

## 元信息

- **原始文档**：[[Docker-Kubernetes/k8s-storage/让存储故障现形：Kubernetes Volume Health Monitor 原理与生产接入]]
- **原始剪藏**：[[0raw/让存储故障现形：Kubernetes Volume Health Monitor 原理与生产接入]]
- **领域**：Kubernetes 存储可观测性
- **摄入日期**：2026-09-06

## 摘要

本文介绍 Kubernetes Volume Health Monitor 如何把 CSI 驱动掌握的卷健康状态带入 Kubernetes API 对象，从而让原本只显示 `Bound` 的 PVC 获得可读取、可告警的健康信号。核心机制是控制器侧和节点侧各自调用 2 个 CSI RPC，并分别写入 PVC、Pod 和 CSINode 的状态。文章还给出 feature gate、状态读取、Prometheus 告警、故障切换联动和生产落地的风险边界。

## 关键知识点

1. 控制器侧 RPC 为 `ControllerListVolumeHealth` 和 `ControllerGetVolumeHealth`，结果写入 `PersistentVolumeClaim.status.healthStatus`。
2. 节点侧 RPC 为 `NodeGetVolumeHealth` 和 `NodeGetStorageHealth`，结果分别写入 `Pod.status.volumeHealth` 与 `CSINode.status.storageHealth`。
3. 健康状态至少区分 `Healthy`、`Degraded` 和 `Inaccessible`；`reason` 与 `message` 用于补充厂商或后端故障信息。
4. 文章以 Kubernetes 1.37 Alpha 为前提，要求 API Server、kube-controller-manager 和 kubelet 开启 `VolumeHealthMonitor=true`，且 CSI 驱动实现对应 RPC。
5. 接入前应在测试集群用 `kubectl get pvc -o yaml` 验证状态字段确实被填充；只开启 feature gate 而驱动不支持时不会产生健康数据。
6. 监控链路可通过 kube-controller-manager/kubelet 指标或自定义 exporter 转换为 Prometheus gauge，并按 `Degraded`/`Inaccessible` 分级告警。
7. 控制器侧、节点侧和 CSINode 侧视角互补：PVC 健康并不排除某个节点的挂载点或本地存储路径异常。
8. remediation 不应无脑删除 Pod 重调度；自动化应配备冷却时间、最大重试次数和人工确认，并把真正的 failover 交给存储层或人工流程。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/concepts/Observability|Observability]]
- [[KnowledgeBase/entities/Prometheus|Prometheus]]
- [[Docker-Kubernetes/k8s-storage/让存储故障现形：Kubernetes Volume Health Monitor 原理与生产接入|Volume Health Monitor 归档文档]]

## 值得注意

- 这是 Alpha 特性，字段和行为可能随 Kubernetes 后续版本变化，不应作为唯一故障判定依据。
- CSI 驱动支持是必要前提，云厂商或企业存储驱动的具体支持矩阵需要按实际版本单独确认。
- 文中的 PromQL 指标名和 exporter 方案是接入思路，不等同于所有 Kubernetes 版本或发行版都默认暴露同名指标。
