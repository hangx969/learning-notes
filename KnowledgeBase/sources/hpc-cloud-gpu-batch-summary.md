---
title: HPC / CloudComputing / GPU-DeepLearning 来源批量摘要
tags:
  - knowledgebase/source
  - hpc
  - cloud-computing
  - gpu
date: 2026-04-17
sources:
  - "[[HPC/PBS-cases]]"
  - "[[HPC/PBS]]"
  - "[[HPC/Slurm-node-exporter]]"
  - "[[HPC/Ubuntu-2204-slurm-22.05.11-binary-installation]]"
  - "[[HPC/Ubuntu2204-slurm- 23.11-deb安装]]"
  - "[[HPC/Ubuntu2204-slurm-22.05.11-二进制安装]]"
  - "[[HPC/CentOS7-slurm23.02-二进制安装]]"
  - "[[CloudComputing/深入剖析Kubernetes]]"
  - "[[CloudComputing/Openstack]]"
  - "[[CloudComputing/极客时间-深入浅出云计算]]"
  - "[[CloudComputing/云原生]]"
  - "[[CloudComputing/大话云计算]]"
  - "[[CloudComputing/图解云计算架构]]"
  - "[[CloudComputing/Auth]]"
  - "[[GPU-DeepLearning/NVIDIA-GPU-开启persistent mode]]"
  - "[[GPU-DeepLearning/Server-basics]]"
  - "[[GPU-DeepLearning/GPU-basics]]"
  - "[[GPU-DeepLearning/GPU-exporter-grafana]]"
---

## 元信息

| 属性       | 内容                                                                 |
| ---------- | -------------------------------------------------------------------- |
| 来源目录   | `HPC/`（7 篇）、`CloudComputing/`（7 篇）、`GPU-DeepLearning/`（4 篇） |
| 文档总数   | 18 篇                                                                |
| 摄入日期   | 2026-04-17                                                           |

---

## 整体概述

这三个目录构成了从底层硬件到上层平台的完整技术栈：

1. **HPC 目录**聚焦高性能计算集群的作业调度系统，主要涵盖 [[KnowledgeBase/entities/Slurm|Slurm]] 和 [[KnowledgeBase/entities/PBS|PBS]] 两大调度器的部署、运维与故障排除，包含多个操作系统版本（Ubuntu 22.04、CentOS 7）和多个 Slurm 版本（22.05、23.02、23.11）的安装实战，以及 Prometheus 监控集成。
2. **CloudComputing 目录**覆盖云计算的理论与实践，从云计算起源（虚拟化、IaaS/PaaS/SaaS）到云原生体系（CNCF、微服务、容器编排、Serverless），深入剖析 Kubernetes 容器技术（Namespace、Cgroup），并涉及 OpenStack、Web API 架构、认证协议（OAuth、OIDC、SAML、CAS SSO）等。
3. **GPU-DeepLearning 目录**关注 NVIDIA GPU 的硬件基础、驱动与 CUDA 环境配置、Persistent Mode 设置、以及基于 Prometheus + Grafana 的 GPU 监控方案，同时包含服务器硬件（SSD）入门知识。

三个方向相互关联：HPC 集群常配备 GPU 计算节点，需要 Slurm 进行 GPU 资源调度；云计算平台（如 Kubernetes）也需要管理 GPU 设备；监控体系（Prometheus/Grafana）贯穿 HPC 与 GPU 两个领域。

---

## 各文档摘要

### HPC

#### [[HPC/PBS-cases|PBS 实际案例]]
收录三个 PBS 生产环境故障案例：(1) Lustre 客户端 bug 导致 GPU 节点 Kdump 重启，解决方案为升级 Lustre 客户端至 2.14.0-ddn168；(2) Singularity 容器中出现 cudaErrorUnknown，原因是 `nvidia_uvm` 内核模块未自动加载，需手动 `modprobe` 并开启 GPU Persistent Mode；(3) PBS 任务时区报错 Asia/Beijing，需统一修改为 Asia/Shanghai。

#### [[HPC/PBS|PBS 作业调度系统]]
介绍 PBS（Portable Batch System）的背景（NASA 开发）、三大分支（OpenPBS、PBS Pro、Torque）、工作流程（qsub 提交 -> 排队 -> 资源分配 -> 执行 -> 完成），以及核心命令（pbsnodes、qsub、qstat）和 PBS 脚本编写方法，包含 shell、Python、MPI 并行作业示例。

#### [[HPC/Slurm-node-exporter|Slurm Node Exporter]]
记录两代 Slurm Prometheus Exporter 的部署方式：旧版基于 Go 编译的 prometheus-slurm-exporter（含在线与离线部署步骤），提供 Slurm 集群指标到 Prometheus 的采集方案，通过 systemd 服务管理，监听 9092 端口。

#### [[HPC/Ubuntu-2204-slurm-22.05.11-binary-installation|Ubuntu 22.04 Slurm 22.05.11 生产环境二进制安装]]
面向 H800 GPU 集群的生产级 Slurm 部署文档，涵盖 Management/Login/Compute 多节点架构，详细步骤包括：Munge 认证安装（确保 UID/GID 一致）、熵池生成（rng-tools）、全局密钥分发，以及 Slurm 各组件的编译安装。

#### [[HPC/Ubuntu2204-slurm- 23.11-deb安装|Ubuntu 22.04 Slurm 23.11 deb 安装]]
实验环境下通过 deb 包安装 Slurm 23.11 的完整指南，包含 IP 规划（um1/uc1/ul1 三节点）、网络配置（netplan）、apt 源设置、主机名与 hosts 配置、资源限制调优等环境准备步骤。

#### [[HPC/Ubuntu2204-slurm-22.05.11-二进制安装|Ubuntu 22.04 Slurm 22.05.11 二进制安装]]
测试环境下的 Slurm 22.05.11 二进制安装文档，三节点架构（m1/c1/l1），涵盖时区配置（ntpdate 同步）、SSH 免密登录设置、crontab 定时同步等基础环境准备。

#### [[HPC/CentOS7-slurm23.02-二进制安装|CentOS7 Slurm 23.02 二进制安装]]
CentOS 7 环境下 Slurm 23.02 的部署指南，一个控制节点（m1）加两个计算节点（c1/c2），包含防火墙关闭、SELinux 禁用、资源限制配置等 CentOS 特有步骤，并提供丰富的参考文档链接（北大、上海交大 HPC 文档等）。

### CloudComputing

#### [[CloudComputing/深入剖析Kubernetes|深入剖析 Kubernetes]]
基于极客时间课程的深度笔记，从进程隔离原理讲起，详细解析 Docker 容器的本质：通过 Linux Namespace（PID、Mount、UTS、IPC、Network、User）实现进程视图隔离，通过 Cgroups 实现资源约束。对比容器与虚拟机的架构差异，阐述容器的性能优势（无 Guest OS 开销、无 Hypervisor 性能损耗）及 Namespace 的局限性。

#### [[CloudComputing/Openstack|OpenStack]]
OpenStack 教程的链接笔记，指向微信公众号的 OpenStack 教程文章。

#### [[CloudComputing/极客时间-深入浅出云计算|深入浅出云计算]]
涵盖云计算核心概念：虚拟机术语（NSG、vCPU、裸金属）、价格优化策略（竞价实例、性能突增型实例/Azure B 系列）、块存储与计算存储分离架构、网络虚拟化（虚拟网卡、多网卡绑定）、网关类型（NAT Gateway SNAT、VPN Gateway）、PaaS 概念、对象存储与块存储的本质差异（K-V 存储 vs 块设备）。

#### [[CloudComputing/云原生|云原生概念介绍]]
系统介绍云原生体系：CNCF 项目生态（Sandbox/Incubating/Graduated）、发展历程（2010-2020）、核心技术体系（微服务、容器、持续交付、DevOps、服务网格、声明式 API、容器编排、Serverless），以及云原生十二要素（基准代码、依赖声明、环境变量配置、无状态化等）。

#### [[CloudComputing/大话云计算|大话云计算]]
云计算入门读物笔记，梳理云计算的发展脉络：从专用机房、网格计算、超算到云计算；服务器演进阶段（普通服务器 -> 小型机 -> 资源池 -> 虚拟化）；虚拟化技术分类（服务器/网络/桌面虚拟化）；云计算对 IT 的影响（DevOps 产生、DBA 岗位变化）；IaaS/PaaS/SaaS 与传统服务器租赁的区别。

#### [[CloudComputing/图解云计算架构|图解云计算架构]]
云计算架构的图解笔记，涵盖服务器资源管理（SSH 密钥对、cloud-init）、对象存储结构（容器-对象模型）、Web API 设计（认证+操作+资源、RESTful URI、Endpoint）、DNS 相关概念（FQDN、DNS 轮询、递归/迭代查询、CDN 与负载均衡）。

#### [[CloudComputing/Auth|认证协议与 SSO]]
认证授权体系的详细笔记：Authentication vs Authorization 概念辨析、Permission/Privilege/Scopes 区分、CAS 协议原理（三方参与者）、SSO 统一认证中心的工作流程（首次登录的 302 重定向、ticket 验证、跨域 cookie 问题）、JWT 原理及其局限性。

### GPU-DeepLearning

#### [[GPU-DeepLearning/NVIDIA-GPU-开启persistent mode|NVIDIA GPU 开启 Persistent Mode]]
记录通过 NVIDIA 驱动自带脚本配置 GPU Persistent Mode 开机自启动的完整步骤：解压 nvidia-persistenced-init 工具包、运行 install.sh 创建 systemd 服务、验证 nvidia-smi 中 Persistence-M 状态为 On。

#### [[GPU-DeepLearning/Server-basics|服务器入门基础]]
包含服务器入门介绍链接和 SSD 硬盘知识：SSD 的产生背景（NAND Flash 技术）、与 HDD 的对比优势（速度快、低功耗、抗震）、SSD 类型分类（NVMe SSD 使用 PCIe 通道、SATA SSD 使用 SATA 接口及其性能差异）。

#### [[GPU-DeepLearning/GPU-basics|GPU 基础与环境配置]]
GPU 知识体系的系统笔记，收录多篇教程链接（GPU 入门、各型号介绍、CUDA 环境安装、nvidia-smi 使用），重点记录不同环境的 GPU 配置要求：裸机环境（GPU Driver + CUDA Toolkit）、Docker 环境（额外需 nvidia-container-toolkit）、Kubernetes 环境（额外需 device-plugin 或 gpu-operator），以及驱动安装步骤。

#### [[GPU-DeepLearning/GPU-exporter-grafana|GPU Exporter 与 Grafana 监控]]
基于 nvidia_gpu_exporter 的 GPU 监控部署方案：二进制部署 exporter（监听 9835 端口）、Prometheus 配置 job 抓取 GPU 指标、Grafana 仪表盘导入（Dashboard ID 14574），并提到内网 IP 变动问题可通过 Pushgateway 中转解决，以及时间同步对 Prometheus 数据准确性的重要性。

---

## 涉及的概念与实体

### 调度系统
- [[KnowledgeBase/entities/Slurm|Slurm]] - HPC 作业调度器，多篇文档覆盖不同版本与平台的安装
- [[KnowledgeBase/entities/PBS|PBS]] - Portable Batch System 作业调度器（OpenPBS / PBS Pro / Torque）
- [[KnowledgeBase/entities/Munge|Munge]] - HPC 集群认证服务，Slurm 依赖组件
- [[KnowledgeBase/entities/SlurmDBD|SlurmDBD]] - Slurm 数据库守护进程

### GPU 与深度学习
- [[KnowledgeBase/entities/NVIDIA|NVIDIA]] - GPU 硬件厂商
- [[KnowledgeBase/entities/CUDA|CUDA]] - NVIDIA GPU 计算平台与编程模型
- [[KnowledgeBase/entities/nvidia-smi|nvidia-smi]] - NVIDIA GPU 管理与监控命令行工具
- [[KnowledgeBase/entities/nvidia-container-toolkit|nvidia-container-toolkit]] - Docker 中使用 GPU 的运行时工具
- [[KnowledgeBase/entities/gpu-operator|gpu-operator]] - Kubernetes 中 GPU 资源管理方案

### 容器与云原生
- [[KnowledgeBase/entities/Docker|Docker]] - 容器运行时
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]] - 容器编排平台
- [[KnowledgeBase/entities/Namespace|Namespace]] - Linux 进程隔离机制
- [[KnowledgeBase/entities/Cgroups|Cgroups]] - Linux 资源限制机制
- [[KnowledgeBase/entities/CNCF|CNCF]] - 云原生计算基金会
- [[KnowledgeBase/entities/OpenStack|OpenStack]] - 开源云计算平台
- [[KnowledgeBase/entities/Singularity|Singularity]] - HPC 容器运行时

### 存储
- [[KnowledgeBase/entities/Lustre|Lustre]] - 高性能并行文件系统
- [[KnowledgeBase/entities/SSD|SSD]] - 固态硬盘（NVMe / SATA）

### 监控
- [[KnowledgeBase/entities/Prometheus|Prometheus]] - 开源监控与告警系统
- [[KnowledgeBase/entities/Grafana|Grafana]] - 数据可视化与仪表盘平台

### 认证与安全
- [[KnowledgeBase/entities/OAuth|OAuth]] - 开放授权协议
- [[KnowledgeBase/entities/OIDC|OIDC]] - OpenID Connect 认证协议
- [[KnowledgeBase/entities/SAML|SAML]] - 安全断言标记语言
- [[KnowledgeBase/entities/SSO|SSO]] - 单点登录

### 操作系统与平台
- [[KnowledgeBase/entities/Ubuntu|Ubuntu]] - Linux 发行版（22.04 LTS）
- [[KnowledgeBase/entities/CentOS|CentOS]] - Linux 发行版（CentOS 7）
- [[KnowledgeBase/entities/SUSE|SUSE]] - SUSE Linux Enterprise Server 12 SP5

---

## 交叉主题发现

1. **GPU 资源调度贯穿 HPC 与云计算**：HPC 端通过 Slurm 的 GRES 机制调度 GPU 节点（如 H800 集群），云端通过 Kubernetes device-plugin / gpu-operator 管理 GPU 资源。两种路径最终都需要底层的 NVIDIA 驱动与 CUDA 环境支持。

2. **Prometheus + Grafana 监控体系的复用**：Slurm 集群使用 prometheus-slurm-exporter（端口 9092）采集作业调度指标，GPU 节点使用 nvidia_gpu_exporter（端口 9835）采集 GPU 硬件指标，两者共享同一套 Prometheus + Grafana 监控基础设施。

3. **容器技术在 HPC 与云计算中的不同实现**：云计算领域以 Docker + Kubernetes 为主流，HPC 领域则使用 Singularity（因其无需 root 权限、与调度系统兼容性更好）。PBS 案例中 Singularity 的 `--nv` 参数与 Docker 的 nvidia-container-toolkit 解决的是同一个问题：容器内 GPU 访问。

4. **Persistent Mode 的多场景关联**：GPU Persistent Mode 在 PBS 故障案例（cudaErrorUnknown 修复）和 GPU-DeepLearning 目录（专门的配置文档）中均出现，说明这是 GPU 节点运维的核心配置项，无论是 HPC 还是独立 GPU 服务器都需要开启。

5. **认证体系的层次对应**：HPC 集群使用 Munge 进行节点间认证（对称密钥），云计算使用 OAuth/OIDC/SAML 进行用户认证与授权，Kubernetes 则有自己的 ServiceAccount/RBAC 体系。认证需求从集群内部扩展到跨系统 SSO。

6. **存储技术的互补**：HPC 使用 Lustre 并行文件系统满足高吞吐需求，云计算提供块存储（云硬盘）和对象存储（S3/OSS）满足不同场景，SSD（NVMe/SATA）作为底层介质支撑两种场景的 IO 性能。

7. **多操作系统部署经验**：Slurm 安装文档覆盖 Ubuntu 22.04 和 CentOS 7 两大主流平台，PBS 案例涉及 SUSE Linux，形成了跨发行版的 HPC 部署知识体系。各平台在防火墙管理、包管理器、SELinux/AppArmor 等方面的差异均有记录。
