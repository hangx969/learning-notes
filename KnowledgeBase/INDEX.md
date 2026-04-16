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
- [[KnowledgeBase/inventory/repository-inventory|📋 全库文档盘点]] — 297 篇文档逐一列出
- [[KnowledgeBase/inventory/domain-summary|📊 领域内容特点分析]] — 17 个领域的成熟度与编译优先级

### 地图与导航
- [[KnowledgeBase/maps/domain-map|🗺️ 领域地图]] — 按技术领域导航全库
- [[KnowledgeBase/maps/tool-map|🔧 工具地图]] — 按工具/平台聚合知识

### 专题地图
- [[KnowledgeBase/maps/kubernetes-map|☸️ Kubernetes 专题]] — 145 篇 K8s 生态知识导航
- [[KnowledgeBase/maps/ai-workflow-map|🤖 AI 工作流专题]] — Claude Code + OpenClaw + AI 辅助运维
- [[KnowledgeBase/maps/claude-code-openclaw-map|🧠 Claude Code & OpenClaw 专题]]
- [[KnowledgeBase/maps/cloud-platform-map|☁️ 云平台专题]] — Aliyun + Azure 对标
- [[KnowledgeBase/maps/linux-ops-map|🐧 Linux 运维专题]]
- [[KnowledgeBase/maps/python-devops-map|🐍 Python 运维开发专题]]

### 概念网络
- [[KnowledgeBase/concepts/]] — 20+ 个高价值概念页

### 分析报告
- [[KnowledgeBase/analysis/topic-coverage-analysis|📈 主题覆盖分析]]
- [[KnowledgeBase/analysis/high-value-gaps|🔍 高价值知识缺口]]
- [[KnowledgeBase/analysis/next-writing-suggestions|✏️ 后续写作建议]]

### 维护
- [[KnowledgeBase/maintenance/broken-links-report|🔗 断链报告]]
- [[KnowledgeBase/maintenance/naming-normalization|📝 命名规范]]
- [[KnowledgeBase/maintenance/update-workflow|🔄 增量维护流程]]

---

## 🏗️ 按领域导航

| 领域 | 篇数 | 成熟度 | 入口 |
|------|------|:------:|------|
| Docker-Kubernetes | 145 | 🟢 | [[KnowledgeBase/maps/kubernetes-map]] |
| Python | 27 | 🟢 | [[KnowledgeBase/maps/python-devops-map]] |
| Linux-Shell | 24 | 🟡 | [[KnowledgeBase/maps/linux-ops-map]] |
| Azure | 21 | 🟢 | [[KnowledgeBase/maps/cloud-platform-map]] |
| Aliyun | 19 | 🟢 | [[KnowledgeBase/maps/cloud-platform-map]] |
| AI | 16 | 🟡 | [[KnowledgeBase/maps/ai-workflow-map]] |
| Go | 9 | 🟡 | [[Go/go-01-环境配置-基础]] |
| CloudComputing | 7 | 🟡 | [[CloudComputing/云原生]] |
| HPC | 7 | 🟡 | [[HPC/CentOS7-slurm23.02-二进制安装]] |
| GPU-DeepLearning | 4 | 🟠 | [[GPU-DeepLearning/GPU-basics]] |
| Database | 3 | 🟡 | [[Database/MySQL入门]] |
| Middlewares | 3 | 🔴 | [[Middlewares/Kafka]] |
| OS | 3 | 🟠 | [[OS/OS]] |
| Networking | 2 | 🟠 | [[Networking/计算机网络基础]] |
| IaC | 2 | 🟠 | [[IaC/terraform-basics]] |

---

## ⭐ 推荐优先阅读

### 云原生核心路径
1. [[CloudComputing/云原生]] → 理解云原生哲学
2. [[Docker-Kubernetes/docker/docker基础]] → 容器基础
3. [[Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源]] → K8s 架构
4. [[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤]] → 最新版安装
5. [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶]] → 可观测性

### AI 赋能运维
1. [[AI/ClaudeCode/ClaudeCode基础指南]] → Claude Code 入门
2. [[AI/ClaudeCode/MCP]] → MCP 协议
3. [[AI/OpenClaw/OpenClaw-基础-安装]] → OpenClaw 入门
4. [[AI/ClaudeCode/obsidian-claude-搭建个人知识库]] → 知识库搭建方法论

### 云平台实战
1. [[Aliyun/网络/VPC]] + [[Azure/6_Azure-Networking]] → 云网络对比
2. [[Aliyun/网络/负载均衡SLB]] + [[Azure/2_AKS-basics]] → 负载均衡与K8s托管服务
3. [[Python/python-运维开发/python-Linux-operation]] → 自动化运维脚本
