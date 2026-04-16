---
title: 知识库入口
tags:
  - knowledgebase/index
  - knowledgebase/navigation
aliases:
  - 知识库首页
  - KB Index
date: 2026-04-16
---

# 📚 Learning Notes 知识库

> [!info] 知识库说明
> 本知识库基于 `learning-notes` 仓库构建，覆盖 **297 篇文档、17 个主题领域**。
> 知识编译层（本目录）不改动原有文档，仅在原始知识源之上叠加导航、概念网络和分析层。
>
> - **扫描日期**：2026-04-16
> - **核心定位**：云原生运维工程师的全栈技术知识库

---

## 🗂️ 主要入口

### 盘点与分析
- [📋 全库文档盘点](inventory/repository-inventory.md) — 297 篇文档逐一列出
- [📊 领域内容特点分析](inventory/domain-summary.md) — 17 个领域的成熟度与编译优先级

### 地图与导航
- [🗺️ 领域地图](maps/domain-map.md) — 按技术领域导航全库
- [🔧 工具地图](maps/tool-map.md) — 按工具/平台聚合知识

### 专题地图
- [☸️ Kubernetes 专题](maps/kubernetes-map.md) — 145 篇 K8s 生态知识导航
- [🤖 AI 工作流专题](maps/ai-workflow-map.md) — Claude Code + OpenClaw + AI 辅助运维
- [🧠 Claude Code & OpenClaw 专题](maps/claude-code-openclaw-map.md)
- [☁️ 云平台专题](maps/cloud-platform-map.md) — Aliyun + Azure 对标
- [🐧 Linux 运维专题](maps/linux-ops-map.md)
- [🐍 Python 运维开发专题](maps/python-devops-map.md)

### 概念网络
- [概念页目录](concepts/) — 20+ 个高价值概念页

### 分析报告
- [📈 主题覆盖分析](analysis/topic-coverage-analysis.md)
- [🔍 高价值知识缺口](analysis/high-value-gaps.md)
- [✏️ 后续写作建议](analysis/next-writing-suggestions.md)

### 维护
- [🔗 断链报告](maintenance/broken-links-report.md)
- [📝 命名规范](maintenance/naming-normalization.md)
- [🔄 增量维护流程](maintenance/update-workflow.md)

---

## 🏗️ 按领域导航

| 领域 | 篇数 | 成熟度 | 入口 |
|------|------|:------:|------|
| Docker-Kubernetes | 145 | 🟢 | [kubernetes-map](maps/kubernetes-map.md) |
| Python | 27 | 🟢 | [python-devops-map](maps/python-devops-map.md) |
| Linux-Shell | 24 | 🟡 | [linux-ops-map](maps/linux-ops-map.md) |
| Azure | 21 | 🟢 | [cloud-platform-map](maps/cloud-platform-map.md) |
| Aliyun | 19 | 🟢 | [cloud-platform-map](maps/cloud-platform-map.md) |
| AI | 16 | 🟡 | [ai-workflow-map](maps/ai-workflow-map.md) |
| Go | 9 | 🟡 | [go-01-环境配置-基础](../Go/go-01-环境配置-基础.md) |
| CloudComputing | 7 | 🟡 | [云原生](../CloudComputing/云原生.md) |
| HPC | 7 | 🟡 | [CentOS7-slurm23.02-二进制安装](../HPC/CentOS7-slurm23.02-二进制安装.md) |
| GPU-DeepLearning | 4 | 🟠 | [GPU-basics](../GPU-DeepLearning/GPU-basics.md) |
| Database | 3 | 🟡 | [MySQL入门](../Database/MySQL入门.md) |
| Middlewares | 3 | 🔴 | [Kafka](../Middlewares/Kafka.md) |
| OS | 3 | 🟠 | [OS](../OS/OS.md) |
| Networking | 2 | 🟠 | [计算机网络基础](../Networking/计算机网络基础.md) |
| IaC | 2 | 🟠 | [terraform-basics](../IaC/terraform-basics.md) |

---

## ⭐ 推荐优先阅读

### 云原生核心路径
1. [云原生](../CloudComputing/云原生.md) → 理解云原生哲学
2. [Docker 基础](../Docker-Kubernetes/docker/docker基础.md) → 容器基础
3. [K8s 架构-组件-资源](../Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源.md) → K8s 架构
4. [安装 k8s-1.35](../Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤.md) → 最新版安装
5. [Prometheus Stack 全家桶](../Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶.md) → 可观测性

### AI 赋能运维
1. [Claude Code 基础指南](../AI/ClaudeCode/ClaudeCode基础指南.md) → Claude Code 入门
2. [MCP](../AI/ClaudeCode/MCP.md) → MCP 协议
3. [OpenClaw 基础安装](../AI/OpenClaw/OpenClaw-基础-安装.md) → OpenClaw 入门
4. [Obsidian + Claude 搭建个人知识库](../AI/ClaudeCode/obsidian-claude-搭建个人知识库.md) → 知识库搭建方法论

### 云平台实战
1. [Aliyun VPC](../Aliyun/网络/VPC.md) + [Azure Networking](../Azure/6_Azure-Networking.md) → 云网络对比
2. [负载均衡 SLB](../Aliyun/网络/负载均衡SLB.md) + [AKS Basics](../Azure/2_AKS-basics.md) → 负载均衡与 K8s 托管服务
3. [Python Linux 运维](../Python/python-运维开发/python-Linux-operation.md) → 自动化运维脚本
