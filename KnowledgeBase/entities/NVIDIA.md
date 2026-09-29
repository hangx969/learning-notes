---
title: NVIDIA
tags:
  - knowledgebase/entity
  - gpu
  - hardware
date: 2026-09-06
sources:
  - "[[KnowledgeBase/sources/k8s-nvidia-device-plugin-summary]]"
  - "[[AI/企业级私有化大模型/大模型精度与量化：FP64到NVFP4]]"
  - "[[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni]]"
---

## 简介

NVIDIA 是全球领先的 GPU 硬件厂商，其 GPU 产品广泛用于深度学习训练、HPC 高性能计算和容器化 GPU 工作负载。在本仓库中主要涉及 NVIDIA 驱动安装、nvidia-smi 监控工具、GPU 持久化模式配置等运维实践。

## 在本仓库中的覆盖

- [[GPU-DeepLearning/GPU-basics|GPU 基础与环境配置]]：裸机驱动与 CUDA Toolkit、Docker 的 NVIDIA Container Toolkit、K8s Device Plugin 与 GPU Operator（NFD/GFD、Driver Installer、DCGM Exporter）
- [[GPU-DeepLearning/NVIDIA-GPU-开启persistent mode|NVIDIA GPU 开启 Persistent Mode]]：安装驱动自带的 `nvidia-persistenced` systemd 服务，在没有活动客户端时维持驱动状态
- [[GPU-DeepLearning/GPU-exporter-grafana|GPU Exporter 与 Grafana 监控]]：以 systemd 部署 nvidia_gpu_exporter，由 Prometheus 抓取并在 Grafana 展示
- [[HPC/Ubuntu2204-Slurm-安装指南|Ubuntu 22.04 Slurm 安装指南]]：H800 GPU 生产集群通过 `GresTypes=gpu`、`Gres=gpu:H800:8` 与 gres.conf 定义 GPU 资源
- [[HPC/PBS|PBS]]：GPU 节点因 Lustre 客户端问题异常重启、Singularity 作业报 `cudaErrorUnknown` 的排查案例
- [[Docker-Kubernetes/docker/docker配置NVIDIA GPU|Docker 配置 NVIDIA GPU]]：安装驱动、CUDA 与 nvidia-docker2，用 `--gpus` 指定容器可见的 GPU
- [[Docker-Kubernetes/k8s-ai-gpu/k8s配置NVIDIA GPU|K8s 配置 NVIDIA GPU]]：Ubuntu 22.04 裸金属节点的驱动安装、NVIDIA Container Toolkit、containerd `nvidia` runtimeClass 与 GPU Operator
- [[Docker-Kubernetes/k8s-ai-gpu/从零部署 NVIDIA Device Plugin：K8s 识别 GPU 的“第一块敲门砖”|从零部署 NVIDIA Device Plugin]]：驱动与 Container Toolkit 前置条件、Helm/手动/GPU Operator 三种部署方式、验证与常见报错
- [[KnowledgeBase/sources/k8s-nvidia-device-plugin-summary|NVIDIA Device Plugin 摘要]]：Device Plugin 部署笔记的来源摘要
- [[AI/企业级私有化大模型/大模型精度与量化：FP64到NVFP4|大模型精度与量化]]：介绍 NVIDIA Tensor Core 上的 TF32/FP8，以及 Blackwell 相关的 NVFP4 4-bit 浮点路线。
- [[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni|大模型本地部署选型]]：覆盖 NVIDIA Container Toolkit、GPU 可见性、显存余量和多 Runtime 容器化。

## 核心功能

- **GPU 资源发现**：通过 NVIDIA 驱动提供的 NVML 接口读取 GPU 信息
- **K8s 集成**：借助 Device Plugin 向节点注册 `nvidia.com/gpu` 扩展资源
- **容器运行时支持**：通过 NVIDIA Container Toolkit 将 GPU 设备挂载到容器

## 使用场景

- **深度学习环境搭建**：裸机安装 NVIDIA 驱动并用 `nvidia-smi` 验证，按需安装 CUDA Toolkit，再用 PyTorch 确认 GPU 可用
- **容器化 GPU 工作负载**：宿主机安装 NVIDIA Container Toolkit 并配置 Docker 或 containerd 运行时，容器复用宿主机驱动，用 `--gpus` 指定 GPU
- **Kubernetes GPU 调度**：Device Plugin 上报 `nvidia.com/gpu`，Pod 通过 `resources.limits` 申请；GPU Operator 统一管理驱动、Container Toolkit、Device Plugin 与 DCGM Exporter
- **HPC GPU 集群**：Slurm 通过 GRES 调度 H800 GPU，GPU 节点开启 Persistent Mode 维持驱动状态
- **大模型推理与低精度计算**：推理 Runtime 按 Worker 容器分配 GPU；TF32、FP8 依赖 Tensor Core 加速，NVFP4 是 Blackwell 架构引入的 4-bit 浮点格式

## 相关概念与实体

- [[KnowledgeBase/entities/CUDA|CUDA]]：NVIDIA GPU 计算平台与编程模型
- [[KnowledgeBase/entities/Slurm|Slurm]]：HPC 集群中 NVIDIA GPU 资源调度
- [[KnowledgeBase/entities/Docker|Docker]]：Docker GPU 运行时（nvidia-docker）
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：K8s GPU 设备插件与调度

- [[KnowledgeBase/concepts/混合精度与模型量化]]：大模型数值格式、混合精度与低比特量化的抽象概念。

## 知识空白

- 仓库中尚无 MIG（多实例 GPU）切分的配置实践，仅在 K8s 1.37 DRA 与 vLLM 显存规划中顺带提及
- 仓库中尚无 NVIDIA Device Plugin 的 time-slicing 共享配置，现有 GPU 共享实践基于 HAMi
- 仓库中尚无 GPU XID 错误解读或 `dcgmi diag` 等硬件故障诊断记录，DCGM 目前只用于指标采集
