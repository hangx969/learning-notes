---
title: K8s CGroup v2 深度解析 — 来源摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/installation-management
  - linux/cgroup
date: 2026-05-13
sources:
  - "[[Docker-Kubernetes/k8s-installation-management/k8s-cgroup-v2深度解析-迁移实战与避坑指南]]"
aliases:
  - cgroup v2 摘要
---

# K8s CGroup v2 深度解析 — 来源摘要

## 元信息
- **原始文档**：[[Docker-Kubernetes/k8s-installation-management/k8s-cgroup-v2深度解析-迁移实战与避坑指南]]
- **领域**：Docker-Kubernetes / Linux 内核
- **摄入日期**：2026-05-13

## 摘要

本文系统讲解 Linux cgroup v1 到 v2 的架构演进，覆盖内核原理（统一层次树、CPU Burst、memory.high 双层限制、I/O 控制统一）、K8s 实战配置（kubelet/containerd 驱动对齐、Pod QoS 与 cgroup 层次映射、MemoryQoS 特性）、5 个生产踩坑案例（OS 升级 Pod 创建失败、CPU throttle 指标失效、内存 OOM 行为变化、JVM 误杀、v1/v2 混合集群）以及 Prometheus 监控告警规则。

## 关键知识点

1. **cgroup v2 统一层次树**：所有控制器（CPU/内存/IO）作用于同一棵树，消除 v1 多层次树导致的跨子系统配置不一致和协调困难
2. **CPU Burst 特性（内核 5.14+）**：`cpu.max.burst` 允许空闲时段积累预算在突发时使用，P99 延迟可降低 30%-50%，解决 v1 固定 100ms 窗口 throttle 问题
3. **memory.high 双层限制**：超过软限制时内核主动回收内存并 throttle，不触发 OOM Kill；只有超过 `memory.max` 才 OOM Kill，对 Go 服务减少误杀效果显著
4. **K8s MemoryQoS（v1.27 Beta）**：`memory.min = requests.memory`、`memory.high = requests * memoryThrottlingFactor(0.9)`、`memory.max = limits.memory`
5. **kubelet + containerd 驱动对齐**：v2 环境必须两端都使用 `systemd` cgroupDriver，不一致会导致 `failed to create containerd task`
6. **Prometheus 指标变化**：v2 下 CPU throttle 指标需 cAdvisor ≥ 0.45，新增 `container_memory_high_bytes` 软限制指标
7. **v1/v2 节点共存**：通过 `node.kubernetes.io/cgroup-version=v2` 标签 + NodeAffinity 隔离，逐步迁移
8. **JVM 适配**：推荐 `-XX:MaxRAMPercentage=75.0` + `UseContainerSupport` + Java 17+ ZGC

## 涉及的概念与实体
- [[KnowledgeBase/entities/Kubernetes]]：cgroup v2 从 v1.25 GA 支持，v1.27 MemoryQoS Beta
- [[KnowledgeBase/entities/containerd]]：≥ 1.6 完整支持 cgroup v2，需配置 SystemdCgroup = true
- [[KnowledgeBase/entities/Prometheus]]：cAdvisor ≥ 0.45/0.47 才能正确读取 v2 格式指标
- [[KnowledgeBase/concepts/容器运行时]]：cgroup 是容器资源隔离的内核基础

## 值得注意
- **MemoryQoS 默认开启会改变 OOM 行为**：v2 下 `limits.memory: 2Gi` 的 Pod，实际在 ~1.8Gi 时就可能因 `memory.high` 触发 throttle 导致应用 crash，需调整 `memoryThrottlingFactor` 或提高 requests/limits 比例
- **cgroup v1 → v2 是不可逆趋势**：RHEL 10 和 Fedora 43 已完全移除 v1 支持，存量集群迟早需要迁移
- 文章提供了 3 条 Prometheus 告警规则（CPU throttle 率、内存接近软限制、OOM Kill），可直接用于生产环境
