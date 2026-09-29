---
title: PBS
tags:
  - knowledgebase/entity
  - hpc
  - job-scheduler
date: 2026-04-17
sources:
  - "[[HPC/PBS]]"
  - "[[HPC/CentOS7-slurm23.02-二进制安装]]"
  - "[[HPC/Ubuntu2204-Slurm-安装指南]]"
aliases:
  - OpenPBS
  - PBS Pro
  - Torque
  - Portable Batch System
  - PBS Professional
---

## 简介

PBS（Portable Batch System）是 HPC 领域经典的作业调度系统，有三个主要分支：OpenPBS（开源社区版）、PBS Pro（Altair 商业版）和 Torque（Adaptive Computing 分支）。在本仓库中与 Slurm 形成对比，覆盖了 PBS 生产故障案例和调度实践。

## 核心功能

- **作业提交与脚本**：用 `qsub` 提交作业，在脚本中以 `#PBS` 指令声明作业名、资源需求（如 `select`、`ncpus`、`mem`）、放置策略、walltime 和输出路径
- **作业查询与控制**：用 `qstat` 查看状态、`qdel` 删除作业、`tracejob` 追踪进度；作业状态（Q/W/H/E）与退出码可用于定位问题
- **队列与节点管理**：用 `qmgr` 创建和配置队列，用 `pbsnodes` 查看节点
- **数组作业与依赖**：用 `-J` 一次提交多个相似作业，用 `-W depend=afterok` 声明作业依赖
- **组件架构**：PBS Pro 由 Server（管理作业与队列）、Scheduler（调度作业）和 MoM（在计算节点执行作业）组成

## 使用场景

- HPC 集群批处理作业调度：按资源需求和队列排队，分配节点后执行
- 参数扫描、蒙特卡洛模拟等需要大量相似作业的计算（数组作业）
- 在 GPU 计算节点上运行 CUDA 或 Singularity 容器作业
- 用 Docker 容器或虚拟机搭建 PBS Pro、Torque 多节点学习环境

## 相关概念与实体

- [[KnowledgeBase/entities/Slurm|Slurm]]：另一个主流 HPC 作业调度器，对比对象
- [[KnowledgeBase/entities/NVIDIA|NVIDIA]]：GPU 作业调度依赖 GPU 硬件
- [[KnowledgeBase/entities/CUDA|CUDA]]：GPU 作业报 `cudaErrorUnknown` 的故障案例
- [[KnowledgeBase/entities/NFS|NFS]]：部署 Torque 时通过 NFS 共享 `/software` 目录
- [[KnowledgeBase/entities/Docker|Docker]]：用 Docker 容器部署 PBS Pro 多节点环境

## 在本仓库中的覆盖

- `HPC/` 目录下有 PBS 相关笔记，包括生产故障排查案例
- 与 Slurm 的对比分析散布在多篇 HPC 文档中
- [[HPC/PBS|PBS]]：版本分支与工作流程，常用命令与作业脚本，PBS Pro 组件、作业参数与故障排查，Docker 部署 PBS Pro、CentOS 虚拟机部署 Torque，以及 GPU 节点故障、时区错误等案例
- [[HPC/CentOS7-slurm23.02-二进制安装|CentOS7-slurm23.02-二进制安装]]：附 PBS 与 Slurm 的对比图
- [[HPC/Ubuntu2204-Slurm-安装指南|Ubuntu2204-Slurm-安装指南]]：环境验收部分附 PBS 与 Slurm 对照资料

## 知识空白

- 仓库中尚无 PBS 调度策略（如 fairshare、抢占、作业优先级）的配置实践
- 仓库中尚无 PBS 中 GPU 资源申请与调度的配置，GPU 相关内容仅为故障案例
- 仓库中尚无 PBS 集群的监控接入，现有 exporter 实践针对 Slurm
- 仓库中尚无 PBS Server 高可用（failover）配置
