---
title: 领域地图
tags:
  - knowledgebase/map
  - knowledgebase/navigation
aliases:
  - Domain Map
date: 2026-04-16
---

# 领域地图

> [!info] 按技术领域导航全库 297 篇文档，每个领域标注覆盖范围、重点子目录、代表性文章和关联领域。

---

## ☸️ Docker-Kubernetes（145 篇）

**覆盖范围：** 从 Docker 容器基础到企业级 Kubernetes 全生命周期管理，包含安装部署、核心资源、监控日志、CI/CD、网络、安全、存储、扩缩容。

**重点子目录：**
- `k8s-basic-resources/`（20 篇）— Pod、Deployment、Service、Ingress、Storage 等核心资源
- `k8s-monitoring-logging/`（20 篇）— Prometheus、Grafana、EFK、Loki、Jaeger、Skywalking
- `k8s-CICD/`（19 篇）— Jenkins、ArgoCD、GitLab、Tekton、Kustomize、GitHub Actions
- `k8s-installation-management/`（16 篇）— K8s 1.20~1.35 多版本安装、生产优化、故障排查
- `docker/`（12 篇）— Docker 基础与各类服务部署
- `k8s-networking-service-mesh/`（7 篇）— Istio、Ingress-Nginx、NetworkPolicy

**代表性文章：**
- [k8s基础-架构-组件-资源](../../Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源.md) — K8s 架构总览
- [安装k8s-1.35-基于rockylinux10-最新步骤](../../Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤.md) — 最新版安装
- [helm部署prometheus-stack全家桶](../../Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶.md) — 可观测性全家桶
- [ArgoCD基础](../../Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础.md) — GitOps 核心
- [k8s精细化流量管理-istio](../../Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio.md) — 服务网格

**关联领域：** [云原生](../../CloudComputing/云原生.md)、[2_AKS-basics](../../Azure/2_AKS-basics.md)、[python-kubernetes-module](../../Python/python-运维开发/python-kubernetes-module.md)、[GPU-basics](../../GPU-DeepLearning/GPU-basics.md)

---

## 🐍 Python（27 篇）

**覆盖范围：** Python 语言基础、Web 框架、网络编程、运维自动化开发、数据分析。

**重点子目录：**
- `python-运维开发/`（10 篇）— ==核心亮点==，K8s API、MySQL/PG/ES 自动化、Fabric
- `python-基础/`（8 篇）— 数据类型、OOP、函数、异常处理
- `python-网络编程-前端/`（6 篇）— Django、Flask、Requests、Socket、爬虫
- `python-数据分析-AI大模型/`（2 篇）— Excel/Word 处理、机器学习

**代表性文章：**
- [python-Linux-operation](../../Python/python-运维开发/python-Linux-operation.md) — Linux 运维核心模块（1737 行）
- [python-kubernetes-module](../../Python/python-运维开发/python-kubernetes-module.md) — K8s API 自动化
- [python-Web框架Django](../../Python/python-网络编程-前端/python-Web框架Django.md) — Django 全栈

**关联领域：** [Python调用k8s-api实现资源管理](../../Docker-Kubernetes/k8s-basic-resources/Python调用k8s-api实现资源管理.md)、[MySQL入门](../../Database/MySQL入门.md)、[shell-scripts](../../Linux-Shell/shell-scripts.md)

---

## 🐧 Linux-Shell（24 篇）

**覆盖范围：** Linux 系统管理、Shell 脚本、SSH、网络配置、Ubuntu 运维、开发环境搭建。

**代表性文章：**
- [Linux-learning-notes](../../Linux-Shell/Linux-learning-notes.md) — Linux 全面学习笔记（2688 行）
- [shell-scripts](../../Linux-Shell/shell-scripts.md) — Shell 脚本实战
- [ansible安装-rockylinux8](../../Linux-Shell/ansible安装-rockylinux8.md) — Ansible 自动化
- [开源堡垒机jumpserver部署](../../Linux-Shell/开源堡垒机jumpserver部署.md) — 安全运维

**关联领域：** 所有技术领域的基础底盘，特别是 Docker-Kubernetes、HPC、Python

---

## ☁️ Azure（21 篇）

**覆盖范围：** Azure VM/VMSS、AKS、DevOps、存储、网络、安全策略、排障工具链。

**代表性文章：**
- [2_AKS-basics](../../Azure/2_AKS-basics.md) — AKS 基础
- [3_AKS-workload-identity](../../Azure/3_AKS-workload-identity.md) — Workload Identity
- [8_Azure-devops-basics](../../Azure/8_Azure-devops-basics.md) — Azure DevOps
- [Kusto Query](../../Azure/Kusto%20Query.md) — KQL 查询语言（2208 行）

**关联领域：** [ECS](../../Aliyun/计算/ECS.md)（对标 VM）、[k8s基础-架构-组件-资源](../../Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源.md)

---

## 🏔️ Aliyun（19 篇）

**覆盖范围：** 阿里云全产品线 — 计算(ECS/ESS/SMC)、网络(VPC/SLB/WAF/DDoS)、存储(OSS/CORS)、数据库(RDS/DTS)、资源管理。

**代表性文章：**
- [VPC](../../Aliyun/网络/VPC.md) — 专有网络架构
- [负载均衡SLB](../../Aliyun/网络/负载均衡SLB.md) — CLB/ALB/NLB 全家族
- [WAF](../../Aliyun/网络/WAF.md) + [DDoS高防](../../Aliyun/网络/DDoS高防.md) — 安全矩阵
- [ACP考试](../../Aliyun/ACP考试.md) — ACP 认证备考

**关联领域：** [6_Azure-Networking](../../Azure/6_Azure-Networking.md)、[计算机网络基础](../../Networking/计算机网络基础.md)

---

## 🤖 AI（16 篇）

**覆盖范围：** Claude Code（7 篇）、OpenClaw（7 篇）、GitHub Copilot（1 篇）、提示词工程（1 篇）。

**重点子目录：**
- `ClaudeCode/`（7 篇）— 基础指南、MCP、Plugin、Skills、Subagents、Obsidian 知识库
- `OpenClaw/`（7 篇）— 基础安装、Channels、Skills、AIOps、多智能体、CoPaw

**代表性文章：**
- [ClaudeCode基础指南](../../AI/ClaudeCode/ClaudeCode基础指南.md) — Claude Code 全面指南
- [OpenClaw-基础-安装](../../AI/OpenClaw/OpenClaw-基础-安装.md) — OpenClaw 入门
- [Openclaw-多智能体](../../AI/OpenClaw/Openclaw-多智能体.md) — 多智能体架构（2974 行，全库最大）

**关联领域：** 与所有领域潜在交叉（AI 辅助编码、运维、知识管理）

---

## 🔤 Go（9 篇）

**覆盖范围：** Go 语言完整学习路径 + 云原生开发基础。

**推荐顺序：** [go-01-环境配置-基础](../../Go/go-01-环境配置-基础.md) → [go-变量-数据类型-运算](../../Go/go-变量-数据类型-运算.md) → [go-分支-循环](../../Go/go-分支-循环.md) → [go-函数-包](../../Go/go-函数-包.md) → [go-数组-切片-map](../../Go/go-数组-切片-map.md) → [go-面向对象](../../Go/go-面向对象.md) → [go-错误处理](../../Go/go-错误处理.md) → [go-web开发](../../Go/go-web开发.md) → [云原生开发-基础](../../Go/云原生开发-基础.md)

**关联领域：** [云原生](../../CloudComputing/云原生.md)、[发布go-python-java代码到K8S环境](../../Docker-Kubernetes/k8s-CICD/发布go-python-java代码到K8S环境.md)

---

## ☁️ CloudComputing（7 篇）

**覆盖范围：** 云计算架构理论、云原生概念、OpenStack、K8s 深入剖析、认证协议（SSO/OAuth）。

**代表性文章：**
- [云原生](../../CloudComputing/云原生.md) — 云原生哲学
- [深入剖析Kubernetes](../../CloudComputing/深入剖析Kubernetes.md) — K8s 理论深入
- [Auth](../../CloudComputing/Auth.md) — 认证协议

**关联领域：** Docker-Kubernetes（实操对照）、Aliyun/Azure（云平台实践）

---

## 🖥️ HPC（7 篇）

**覆盖范围：** Slurm 和 PBS 作业调度系统，覆盖 CentOS 7 / Ubuntu 22.04 多版本部署。

**代表性文章：**
- [CentOS7-slurm23.02-二进制安装](../../HPC/CentOS7-slurm23.02-二进制安装.md) — 最全面的 Slurm 部署指南（1449 行）
- [PBS](../../HPC/PBS.md) — PBS 调度系统

**关联领域：** [GPU-basics](../../GPU-DeepLearning/GPU-basics.md)、[Linux-learning-notes](../../Linux-Shell/Linux-learning-notes.md)

---

## 其他领域

| 领域 | 篇数 | 核心文章 | 关联 |
|------|------|----------|------|
| GPU-DeepLearning | 4 | [GPU-basics](../../GPU-DeepLearning/GPU-basics.md) | HPC、Docker |
| Database | 3 | [MySQL入门](../../Database/MySQL入门.md)、[源码安装redis-6.2.6-centos7](../../Database/源码安装redis-6.2.6-centos7.md) | Python 运维 |
| Middlewares | 3 | [Kafka](../../Middlewares/Kafka.md)、[RabbitMQ](../../Middlewares/RabbitMQ.md) | K8s 中间件部署 |
| OS | 3 | [OS](../../OS/OS.md)、[计算机组成原理](../../OS/计算机组成原理.md) | 理论基础 |
| Networking | 2 | [计算机网络基础](../../Networking/计算机网络基础.md)、[HTTP基础](../../Networking/HTTP基础.md) | 云网络基础 |
| IaC | 2 | [terraform-basics](../../IaC/terraform-basics.md) | 自动化运维 |
| Git | 2 | [git-learning](../../Git/git-learning.md) | 开发工具 |
| SoftwareTesting | 2 | [软件工程基础](../../SoftwareTesting/软件工程基础.md) | 软件工程 |
| C++ | 1 | [C++LearningNotes](../../C++/C++LearningNotes.md) | 编程语言 |
