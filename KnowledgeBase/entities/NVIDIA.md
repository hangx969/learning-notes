---
title: NVIDIA
tags:
  - knowledgebase/entity
  - gpu
  - hardware
date: 2026-09-05
sources:
  - "[[KnowledgeBase/sources/k8s-nvidia-device-plugin-summary]]"
---

## 简介

NVIDIA 是全球领先的 GPU 硬件厂商，其 GPU 产品广泛用于深度学习训练、HPC 高性能计算和容器化 GPU 工作负载。在本仓库中主要涉及 NVIDIA 驱动安装、nvidia-smi 监控工具、GPU 持久化模式配置等运维实践。

## 在本仓库中的位置

- `GPU-DeepLearning/` 目录下有 GPU 环境搭建相关笔记
- `HPC/` 目录下涉及 Slurm + NVIDIA GPU 调度（GRES 配置）
- `Docker-Kubernetes/docker/` 中涉及 Docker GPU 运行时配置
- `Docker-Kubernetes/k8s-misc/` 中涉及 K8s GPU 节点配置
- `Docker-Kubernetes/k8s-ai-gpu/` 中涉及 NVIDIA Device Plugin、GPU Operator 和 containerd GPU runtime 配置

## 核心功能

- **GPU 资源发现**：通过 NVIDIA 驱动提供的 NVML 接口读取 GPU 信息
- **K8s 集成**：借助 Device Plugin 向节点注册 `nvidia.com/gpu` 扩展资源
- **容器运行时支持**：通过 NVIDIA Container Toolkit 将 GPU 设备挂载到容器

## 相关概念与实体

- [[KnowledgeBase/entities/CUDA|CUDA]]：NVIDIA GPU 计算平台与编程模型
- [[KnowledgeBase/entities/Slurm|Slurm]]：HPC 集群中 NVIDIA GPU 资源调度
- [[KnowledgeBase/entities/Docker|Docker]]：Docker GPU 运行时（nvidia-docker）
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：K8s GPU 设备插件与调度
