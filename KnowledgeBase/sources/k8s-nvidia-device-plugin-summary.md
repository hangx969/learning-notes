---
title: K8s NVIDIA Device Plugin 部署 — 来源摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/k8s-ai-gpu
  - kubernetes/gpu
date: 2026-09-05
sources:
  - "[[Docker-Kubernetes/k8s-ai-gpu/从零部署 NVIDIA Device Plugin：K8s 识别 GPU 的“第一块敲门砖”]]"
aliases:
  - NVIDIA Device Plugin 摘要
---

# K8s NVIDIA Device Plugin 部署 — 来源摘要

## 元信息

- **原始文档**：[[Docker-Kubernetes/k8s-ai-gpu/从零部署 NVIDIA Device Plugin：K8s 识别 GPU 的“第一块敲门砖”]]
- **原始来源**：[深栈运维：从零部署 NVIDIA Device Plugin](https://mp.weixin.qq.com/s/h49RmFUKpZXW1ybiltyqsg)
- **领域**：Docker-Kubernetes / NVIDIA GPU
- **摄入日期**：2026-09-05

## 摘要

本文解释 NVIDIA Device Plugin 在 K8s GPU 调度链路中的位置：它通过 NVML 发现节点 GPU，并向 Kubelet/Kubernetes 注册 `nvidia.com/gpu` 扩展资源，使调度器能够为 Pod 分配 GPU。文章以裸金属 GPU 节点为背景，覆盖 NVIDIA 驱动、NVIDIA Container Toolkit、containerd runtime 的前置检查，以及 Helm、静态 DaemonSet 和 GPU Operator 三种部署方式。最后给出节点资源、插件日志和 CUDA 测试 Pod 的验证方法，以及常见 GPU 发现和容器启动错误的排查顺序。

## 关键知识点

1. **Device Plugin 解决资源可见性，不负责调度策略**：它向 K8s 上报 GPU 数量和健康状态，具体 Pod 放置仍由 `kube-scheduler` 决定。
2. **前置依赖是 NVIDIA 驱动与容器运行时**：驱动通过 NVML 暴露 GPU 信息，NVIDIA Container Toolkit 和 containerd runtime 负责把 GPU 设备挂载进容器。
3. **三种部署路径**：Helm 适合版本化管理；静态 DaemonSet 可控性最高；GPU Operator 统一管理驱动、Device Plugin、Container Toolkit 和 DCGM 监控，更适合生产环境。
4. **GPU 是 Kubernetes 扩展资源**：节点应出现 `nvidia.com/gpu`，工作负载通过 `resources.limits.nvidia.com/gpu` 请求 GPU。
5. **验证应覆盖三层**：检查节点扩展资源、查看 Device Plugin 日志、运行带 `nvidia-smi` 的 CUDA 测试 Pod。
6. **排障顺序从底层到上层**：先查 `nvidia-smi` 和 `lspci`，再查插件 Pod/日志，最后检查 kubelet；这样可以区分硬件、驱动、插件和运行时问题。
7. **Device Plugin 是持续运行的 DaemonSet**：启动时扫描 GPU，运行中响应 Kubelet 的 Allocate 请求；设备发生变化时可能需要重启插件重新扫描。
8. **版本与设备访问是高频故障点**：`no GPU found` 通常指向驱动或 `/dev/nvidia*` 访问问题，`Unknown runtime specified nvidia` 指向 containerd runtime 配置问题。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/entities/NVIDIA]]
- [[KnowledgeBase/entities/containerd]]
- [[KnowledgeBase/entities/Helm]]
- [[KnowledgeBase/concepts/容器运行时]]

## 值得注意

- 文章中的“GPU Operator 推荐生产使用”是组件整合与版本管理角度的实践建议；具体选型仍需结合集群发行版、驱动兼容矩阵和已有 Operator 管理边界。
- Device Plugin 上报 GPU 不等于容器一定能使用 GPU；驱动、容器运行时挂载链路和测试 Pod 三者都必须验证。
