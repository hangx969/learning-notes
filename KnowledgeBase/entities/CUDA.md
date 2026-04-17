---
title: CUDA
tags:
  - knowledgebase/entity
  - gpu
  - computing-platform
date: 2026-04-17
aliases:
  - CUDA Toolkit
---

## 简介

CUDA（Compute Unified Device Architecture）是 NVIDIA 推出的并行计算平台和编程模型，允许开发者利用 GPU 进行通用计算（GPGPU）。CUDA Toolkit 包含编译器、库和调试工具，是深度学习框架和 HPC 应用的基础依赖。

## 在本仓库中的位置

- `GPU-DeepLearning/` 目录下涉及 CUDA 环境搭建
- `HPC/` 目录下涉及 Slurm 集群的 CUDA 配置
- `Docker-Kubernetes/docker/` 中涉及 Docker 容器内的 CUDA 环境
- `Docker-Kubernetes/k8s-misc/` 中涉及 K8s GPU 节点的 CUDA 配置

## 相关概念与实体

- [[KnowledgeBase/entities/NVIDIA|NVIDIA]]：CUDA 的开发厂商
- [[KnowledgeBase/entities/Slurm|Slurm]]：HPC 集群中管理 CUDA 计算任务
- [[KnowledgeBase/entities/Docker|Docker]]：容器化 CUDA 工作负载
