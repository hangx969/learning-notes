---
title: Kubernetes MCP Server + Dify 智能运维
tags:
  - knowledgebase/source
  - AI/AIOps
  - kubernetes
  - MCP
date: 2026-06-07
sources:
  - "[[Kubernetes-MCP-Server-Dify智能运维]]"
aliases:
  - K8s MCP Server摘要
---

# Kubernetes MCP Server + Dify 智能运维

## 元信息
- **原始文档**：[[Kubernetes-MCP-Server-Dify智能运维]]
- **领域**：AI / AIOps / Kubernetes
- **摄入日期**：2026-06-07

## 摘要
基于 Dify（AI 应用开发平台）+ Kubernetes MCP Server（MCP 协议标准工具集）构建 AI 驱动的 Kubernetes 智能运维方案。Dify 作为大脑理解自然语言并规划任务，MCP Server 作为桥梁将 K8s API 封装成安全工具，实现实时集群感知、自然语言运维、自动故障分析和企业知识库集成。文章包含完整的部署步骤（Dify docker-compose + MCP Server 二进制）、MCP 连接配置和 Agent 提示词模板。

## 关键知识点
1. **三层架构**：Dify（大脑，理解自然语言+任务规划）→ Kubernetes MCP Server（桥梁，封装 K8s API 为 MCP 工具）→ Kubernetes（执行层）
2. **四大核心能力**：实时读取 K8s 集群数据（Pod/Deployment/Node/Event/Service）、自然语言运维（无需 kubectl）、自动故障分析（CrashLoopBackOff/OOMKilled/镜像拉取失败/调度失败/PVC 异常）、企业知识库集成（Dify RAG 接入运维文档/SOP）
3. **四大使用场景**：Pod 故障排查、Deployment 异常分析、集群智能巡检（Pending Pod/异常 Event/高负载 Node/未设置 requests-limits）、Node 故障分析
4. **部署要点**：MCP Server 使用 `--read-only` 模式（生产环境必须）、通过 SSE 端点（`/sse`）与 Dify 连接、Agent 提示词强调安全优先原则（高危操作需二次确认）
5. **MCP Server 项目地址**：https://github.com/containers/kubernetes-mcp-server

## 涉及的概念与实体
- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/entities/MCP]]

## 值得注意
- 与知识库中已有的 [[AI/OpenClaw/Openclaw-AIOps]] 方案互补：OpenClaw AIOps 通过飞书 Channel + kubectl Skill 实现，本文通过 Dify + MCP Server 实现，两者都是 AI 驱动 K8s 运维的落地方案
- Agent 提示词模板可直接复用，强调了安全优先原则（只读默认、高危操作二次确认、默认使用 default 命名空间）
- MCP Server 的 `--read-only` 模式是生产环境的关键安全保障
