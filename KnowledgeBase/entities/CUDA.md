---
title: CUDA
tags:
  - knowledgebase/entity
  - gpu
  - computing-platform
date: 2026-09-06
sources:
  - "[[AI/企业级私有化大模型/大模型精度与量化：FP64到NVFP4]]"
  - "[[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni]]"
aliases:
  - CUDA Toolkit
---

## 简介

CUDA（Compute Unified Device Architecture）是 NVIDIA 推出的并行计算平台和编程模型，允许开发者利用 GPU 进行通用计算（GPGPU）。CUDA Toolkit 包含编译器、库和调试工具，是深度学习框架和 HPC 应用的基础依赖。

## 核心功能

- **驱动与 Toolkit 分层**：GPU Driver 提供驱动及 CUDA Driver API；CUDA Toolkit 包含编译工具、库和运行时组件，安装后用 `nvcc -V` 验证。`nvidia-smi` 显示的 CUDA 版本是当前驱动最高支持的版本
- **按需安装 Toolkit**：需要在宿主机编译 CUDA 程序时才安装 Toolkit，并配置 `PATH`、`LD_LIBRARY_PATH`；只运行自带 CUDA 运行时的容器时，宿主机通常不需要 Toolkit
- **容器中的 CUDA**：NVIDIA Container Toolkit 把 GPU 设备和宿主机驱动挂载进容器，CUDA Runtime 等用户态库由镜像提供，例如 `nvidia/cuda` 系列镜像
- **框架与平台集成**：PyTorch 通过 `torch.cuda.is_available()`、`torch.version.cuda` 检测 CUDA 设备与版本；GPU Operator 的 GFD 把 CUDA Runtime 与驱动版本写入节点标签（如 `nvidia.com/cuda.runtime.major`）

## 使用场景

- **深度学习环境**：裸机安装驱动与 CUDA Toolkit 后，用 PyTorch 脚本检查 CUDA 设备、版本与显存
- **容器与 K8s GPU 验证**：Docker 用 `nvidia/cuda` 镜像执行 `nvidia-smi`，K8s 用 CUDA vectoradd 示例 Pod 验证 GPU 分配
- **大模型推理 Serving**：vLLM、SGLang 等 Runtime 可能依赖不同的 PyTorch 与 CUDA 用户态库，适合按容器隔离；测试环境可用 `CUDA_VISIBLE_DEVICES` 为每个进程指定 GPU
- **HPC 容器作业排障**：GPU 节点上 Singularity 作业报 `cudaErrorUnknown` 时，重点排查主机驱动栈初始化（`modprobe nvidia_uvm`、`nvidia-persistenced`）

## 在本仓库中的覆盖

- [[GPU-DeepLearning/GPU-basics|GPU 基础与环境配置]]：裸机安装驱动与 CUDA Toolkit、PyTorch 验证 CUDA，以及 Docker、K8s Device Plugin 与 GPU Operator 的 GPU 配置
- [[Docker-Kubernetes/docker/docker配置NVIDIA GPU|Docker 配置 NVIDIA GPU]]：安装驱动、CUDA 与 nvidia-docker2，用 `nvidia/cuda` 镜像验证容器内 GPU
- [[Docker-Kubernetes/k8s-ai-gpu/k8s配置NVIDIA GPU|K8s 配置 NVIDIA GPU]]：Pod 到 GPU 的完整路径；容器运行时只注入 GPU 设备，CUDA 等软件需由容器镜像提供
- [[HPC/PBS|PBS]]：GPU 节点 Singularity 作业报 `cudaErrorUnknown`（CUDA 12.0）的排查案例
- [[AI/企业级私有化大模型/大模型精度与量化：FP64到NVFP4|大模型精度与量化]]：从 TF32、FP8、NVFP4 的硬件支持角度说明精度选择不能脱离 CUDA/框架版本。
- [[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni|大模型本地部署选型]]：说明宿主机与容器中的驱动/CUDA Runtime 边界、依赖隔离和 GPU Serving 兼容性。

## 相关概念与实体

- [[KnowledgeBase/entities/NVIDIA|NVIDIA]]：CUDA 的开发厂商
- [[KnowledgeBase/entities/Slurm|Slurm]]：HPC 集群中管理 CUDA 计算任务
- [[KnowledgeBase/entities/Docker|Docker]]：容器化 CUDA 工作负载

- [[KnowledgeBase/concepts/混合精度与模型量化]]：CUDA 与 GPU 架构共同决定可用的数据类型、Tensor Core 加速和量化实现。

## 知识空白

- 仓库中尚无 CUDA C/C++ kernel 编写与编译示例：[[GPU-DeepLearning/GPU-basics|GPU 基础与环境配置]] 中的 Hello World 仅为外部链接，`nvcc` 只用于版本验证
- 仓库中尚无 cuDNN 的安装与版本配套记录
- 仓库中尚无 Nsight Systems、Nsight Compute 等 CUDA 性能分析工具的使用记录
