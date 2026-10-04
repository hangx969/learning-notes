# CloudOps Vault · 云原生与基础设施知识库

**📖 在线浏览：[hangx969.github.io/cloudops-vault](https://hangx969.github.io/cloudops-vault/)**（随 main 分支自动更新）

[![Deploy Pages](https://github.com/hangx969/cloudops-vault/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/hangx969/cloudops-vault/actions/workflows/deploy-pages.yml)

网站使用 [Quartz 4](https://github.com/jackyzha0/quartz/tree/v4) 构建。

涵盖云原生技术、基础设施自动化、编程语言、AI/ML 和现代 DevOps 实践的综合知识库。

> **~360 篇学习笔记 · 18 个技术领域 · 159 篇知识编译层文件**

## 🧭 知识库导航（KnowledgeBase）

本仓库在原始文档之上构建了一个 **知识编译层**（[Karpathy LLM Wiki 模式](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)），提供全局导航、概念网络和分析报告，无需逐篇翻找。

**→ [进入知识库首页](./KnowledgeBase/INDEX.md)**

| 类型 | 说明 | 入口 |
| --- | --- | --- |
| 📋 全库盘点 | 文档逐一索引 | [repository-inventory](./KnowledgeBase/inventory/repository-inventory.md) |
| 🗺️ 领域地图 | 按技术领域导航 | [domain-map](./KnowledgeBase/maps/domain-map.md) |
| 🔧 工具地图 | 按工具/平台聚合 | [tool-map](./KnowledgeBase/maps/tool-map.md) |
| ☸️ K8s 专题 | K8s 生态导航（Docker-Kubernetes 共 168 篇） | [kubernetes-map](./KnowledgeBase/maps/kubernetes-map.md) |
| 🤖 AI 专题 | Claude Code + Codex + OpenClaw + Hermes Agent + AI 视觉 | [ai-workflow-map](./KnowledgeBase/maps/ai-workflow-map.md) |
| ☁️ 云平台专题 | Aliyun vs Azure 对标 | [cloud-platform-map](./KnowledgeBase/maps/cloud-platform-map.md) |
| 🐧 Linux 运维 | 系统管理 + HPC + GPU | [linux-ops-map](./KnowledgeBase/maps/linux-ops-map.md) |
| 🐍 Python 运维 | 27 篇 Python 开发导航 | [python-devops-map](./KnowledgeBase/maps/python-devops-map.md) |
| 📈 覆盖分析 | 主题深度与缺口识别 | [topic-coverage-analysis](./KnowledgeBase/analysis/topic-coverage-analysis.md) |
| ✏️ 写作建议 | 推荐补写方向 | [next-writing-suggestions](./KnowledgeBase/analysis/next-writing-suggestions.md) |

## 🚀 推荐阅读路径

### 云原生入门
1. [云原生概念](./CloudComputing/云原生.md) → 理解云原生哲学
2. [Docker 基础](./Docker-Kubernetes/docker/docker基础.md) → 容器基础
3. [K8s 架构](./Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源.md) → K8s 架构总览
4. [K8s API Server：请求链路、认证授权与生产调优](./Docker-Kubernetes/k8s-basic-resources/k8s-APIServer深度剖析-请求链路-认证授权-生产调优.md) → 请求链路与认证授权
5. [Prometheus-Stack：生产部署与运维](./Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶.md) → 可观测性
6. [OpenTelemetry 统一可观测性实战](./Docker-Kubernetes/k8s-monitoring-logging/OpenTelemetry实战-统一Traces-Metrics-Logs.md) → 下一代可观测性
7. [K8s 集群成本优化](./Docker-Kubernetes/k8s-scaling/k8s成本优化方案-FinOps实战.md) → FinOps 实战

### AI 赋能运维
1. [Claude Code 指南](./AI/ClaudeCode/Claude%20Code%20基础指南.md) → 入门必读
2. [扩展体系（MCP/Skills/Plugin）](./AI/ClaudeCode/Claude%20Code%20扩展体系.md) → 四层扩展机制
3. [Mnilax 的 CLAUDE.md：12 条规则](./AI/ClaudeCode/CLAUDE.md最佳实践-12条规则模板.md) → 错误率 41%→3%
4. [Claude Code 为何用 grep 而非 RAG 检索代码？](./AI/ClaudeCode/Claude-Code为什么用grep不用RAG.md) → Agentic Search 架构
5. [OpenClaw 安装](./AI/OpenClaw/OpenClaw-基础-安装.md) → 开源 AI 工具平台
6. [OpenClaw K8s 运维：从只读巡检到低风险变更](./AI/OpenClaw/OpenClaw-K8s智能运维实战.md) → 三阶段渐进式 AIOps

### 云平台实战
1. [VPC](./Aliyun/网络/VPC.md) + [Azure 网络](./Azure/6_Azure-Networking.md) → 云网络对比
2. [AKS 基础](./Azure/2_AKS-basics.md) → 托管 K8s 服务
3. [FinOps 云成本优化](./Aliyun/资源管理/FinOps-云成本优化实战.md) → 降本增效

## 🏗️ 架构说明

本知识库采用 **三层架构**（基于 [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 模式）：

| 层级 | 说明 | 所有权 |
| --- | --- | --- |
| **Raw Sources** | 顶层主题目录中的 markdown 文件 | 人类策划，只读不改 |
| **Wiki** | `KnowledgeBase/` 目录下的所有内容 | LLM 创建和维护 |
| **Schema** | `AGENTS.md` 规约文件 | 人类与 LLM 共同演进 |

详见 [AGENTS.md](./AGENTS.md) 了解完整的页面模板、操作流程和命名约定。
