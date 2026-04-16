---
title: Slurm
tags:
  - knowledgebase/concept
date: 2026-04-16
---

# Slurm

## 定义
Slurm（Simple Linux Utility for Resource Management）是高性能计算（HPC）领域最主流的作业调度与资源管理系统，用于管理计算集群中的节点、队列（分区）和用户作业。本仓库记录了 Slurm 在 CentOS 和 Ubuntu 上的多种安装方式以及与 PBS 调度系统的对比。

## 在本仓库中的位置
主要集中在 `HPC/` 目录下，共 7 篇文章（含脚本），涵盖 Slurm 二进制安装（CentOS 7 / Ubuntu 22.04）、deb 包安装、Node Exporter 监控集成以及 PBS 调度系统对比。

## 相关文章
- [[HPC/CentOS7-slurm23.02-二进制安装]]
- [[HPC/Ubuntu-2204-slurm-22.05.11-binary-installation]]
- [[HPC/Ubuntu2204-slurm-22.05.11-二进制安装]]
- [[HPC/Ubuntu2204-slurm- 23.11-deb安装]]
- [[HPC/Slurm-node-exporter]]
- [[HPC/PBS]]
- [[HPC/PBS-cases]]

## 关联概念
- [[KnowledgeBase/concepts/自动化运维]]
- [[KnowledgeBase/concepts/Observability]]
- [[KnowledgeBase/concepts/Python运维开发]]

## 可延展方向
- Slurm 高级调度策略（Fair-share、Preemption、QOS）
- Slurm 与 GPU 资源管理（GRES 配置）
- Slurm REST API 与自动化作业提交
- HPC 容器化方案（Singularity / Apptainer）
- Slurm 集群监控与 Prometheus 集成
