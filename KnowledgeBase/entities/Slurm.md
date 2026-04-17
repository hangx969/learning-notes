---
title: Slurm
tags:
  - knowledgebase/entity
date: 2026-04-17
sources:
  - "[[HPC/CentOS7-slurm23.02-二进制安装]]"
  - "[[HPC/Ubuntu-2204-slurm-22.05.11-binary-installation]]"
  - "[[HPC/Ubuntu2204-slurm-22.05.11-二进制安装]]"
  - "[[HPC/Ubuntu2204-slurm- 23.11-deb安装]]"
  - "[[HPC/Slurm-node-exporter]]"
  - "[[HPC/PBS]]"
  - "[[HPC/PBS-cases]]"
---

# Slurm

## 定义
Slurm（Simple Linux Utility for Resource Management）是高性能计算（HPC）领域最主流的作业调度与资源管理系统，用于管理计算集群中的节点、队列（分区）和用户作业。本仓库记录了 Slurm 在 CentOS 和 Ubuntu 上的多种安装方式以及与 [[KnowledgeBase/entities/PBS|PBS]] 调度系统的对比。

## 集群架构
Slurm 集群采用典型的三层节点架构：
- **Management 节点**：运行 slurmctld 控制守护进程和 [[KnowledgeBase/entities/SlurmDBD|SlurmDBD]] 数据库守护进程
- **Compute 节点**：运行 slurmd 守护进程，执行实际计算任务
- **Login 节点**：用户登录与作业提交入口

## 安装部署
本仓库覆盖多个操作系统版本和 Slurm 版本的部署实践：

### 二进制安装
- **[[HPC/CentOS7-slurm23.02-二进制安装|CentOS 7 + Slurm 23.02]]**：一个控制节点（m1）+ 两个计算节点（c1/c2），包含防火墙关闭、SELinux 禁用等 CentOS 特有步骤
- **[[HPC/Ubuntu-2204-slurm-22.05.11-binary-installation|Ubuntu 22.04 + Slurm 22.05.11（生产环境）]]**：面向 H800 GPU 集群的生产级部署，包含 Management/Login/Compute 多节点完整流程
- **[[HPC/Ubuntu2204-slurm-22.05.11-二进制安装|Ubuntu 22.04 + Slurm 22.05.11（测试环境）]]**：三节点（m1/c1/l1）测试架构

### deb 包安装
- **[[HPC/Ubuntu2204-slurm- 23.11-deb安装|Ubuntu 22.04 + Slurm 23.11]]**：实验环境下通过 deb 包安装，三节点（um1/uc1/ul1）

### 关键依赖
- **[[KnowledgeBase/entities/Munge|Munge]] 认证**：Slurm 集群必需的认证组件，需确保所有节点 UID/GID 一致，使用 rng-tools 生成熵池，全局分发密钥
- 时间同步：ntpdate 同步、crontab 定时校时，对集群正常运行至关重要

## 监控集成
通过 **prometheus-slurm-exporter**（基于 Go 编译）将 Slurm 集群指标采集到 [[KnowledgeBase/entities/Prometheus|Prometheus]]，监听 9092 端口，使用 systemd 服务管理。与 [[KnowledgeBase/entities/Grafana|Grafana]] 配合实现可视化监控。

## 与 PBS 的对比
[[KnowledgeBase/entities/PBS|PBS]]（Portable Batch System）是 NASA 开发的另一大 HPC 调度器，分为 OpenPBS、PBS Pro、Torque 三个分支。PBS 使用 qsub/qstat 命令体系，而 Slurm 使用 sbatch/squeue。本仓库还记录了 PBS 生产环境故障案例，包括 [[KnowledgeBase/entities/Lustre|Lustre]] 客户端 bug 导致 GPU 节点重启、[[KnowledgeBase/entities/Singularity|Singularity]] 容器中 cudaErrorUnknown 等问题的排查与解决。

## GPU 资源调度
HPC 集群常配备 GPU 计算节点（如 H800），需要 Slurm 通过 GRES 机制进行 GPU 资源调度。底层依赖 [[KnowledgeBase/entities/NVIDIA|NVIDIA]] 驱动与 [[KnowledgeBase/entities/CUDA|CUDA]] 环境，GPU Persistent Mode 是 GPU 节点运维的核心配置项。

## 在本仓库中的位置
主要集中在 `HPC/` 目录下，共 7 篇文章（含脚本），涵盖 Slurm 二进制安装（CentOS 7 / Ubuntu 22.04）、deb 包安装、Node Exporter 监控集成以及 PBS 调度系统对比。

## 相关文章
- [[HPC/CentOS7-slurm23.02-二进制安装|CentOS7-slurm23.02-二进制安装]]
- [[HPC/Ubuntu-2204-slurm-22.05.11-binary-installation|Ubuntu-2204-slurm-22.05.11-binary-installation]]
- [[HPC/Ubuntu2204-slurm-22.05.11-二进制安装|Ubuntu2204-slurm-22.05.11-二进制安装]]
- [[HPC/Ubuntu2204-slurm- 23.11-deb安装|Ubuntu2204-slurm- 23.11-deb安装]]
- [[HPC/Slurm-node-exporter|Slurm-node-exporter]]
- [[HPC/PBS|PBS]]
- [[HPC/PBS-cases|PBS-cases]]

## 关联概念
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]
- [[KnowledgeBase/concepts/Observability|Observability]]
- [[KnowledgeBase/concepts/Python运维开发|Python运维开发]]

## 可延展方向
- Slurm 高级调度策略（Fair-share、Preemption、QOS）
- Slurm 与 GPU 资源管理（GRES 配置）
- Slurm REST API 与自动化作业提交
- HPC 容器化方案（Singularity / Apptainer）
- Slurm 集群监控与 Prometheus 集成
