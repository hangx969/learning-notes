---
title: AI 工作流专题地图
tags:
  - knowledgebase/map
  - knowledgebase/ai
aliases:
  - AI Workflow Map
date: 2026-04-16
---

# 🤖 AI 工作流专题地图

> [!info] 专题范围
> 覆盖 AI/ 目录下 ==20 篇文档==，聚焦 Claude Code、OpenClaw 两大 AI 工具平台及其在运维场景中的应用，并收录 AI 行业动态分析。

---

## 核心概念
- [[KnowledgeBase/entities/Claude-Code|Claude-Code]] — AI 编码与知识管理助手
- [[KnowledgeBase/entities/OpenClaw|OpenClaw]] — AI 多智能体运维平台
- [[KnowledgeBase/entities/MCP|MCP]] — Model Context Protocol
- [[KnowledgeBase/entities/Obsidian|Obsidian]] — 知识管理工具

---

## 📖 推荐阅读顺序

### Claude Code 路径
1. [[AI/ClaudeCode/ClaudeCode基础指南|ClaudeCode基础指南]] — 入门必读
2. [[AI/ClaudeCode/Claude Code 扩展体系|扩展体系]] — MCP + Skills + Slash Commands + Plugin 四层扩展机制
3. [[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams|多智能体协作]] — Subagents 与 Agent Teams
4. [[AI/ClaudeCode/Claude-Skill质检工具-SkillCraft|Skill Craft 质检工具]] — 7 类失效模式 + 三层评估 + 四模式质量工程
5. [[AI/ClaudeCode/Claude-Code-Harness实战-最小可用系统|Harness 实战]] — 四层约束架构 + Git 门禁，系统强制执行安全边界

### OpenClaw 路径
1. [[AI/OpenClaw/OpenClaw-基础-安装|OpenClaw-基础-安装]] — 入门安装
2. [[AI/OpenClaw/OpenClaw-Channels|OpenClaw-Channels]] — Channel 配置
3. [[AI/OpenClaw/OpenClaw-Skills-Plugins|OpenClaw-Skills-Plugins]] — Skills 插件开发
4. [[AI/OpenClaw/CoPaw|CoPaw]] — CoPaw 工具
5. [[AI/OpenClaw/Openclaw-AIOps|Openclaw-AIOps]] — AIOps 运维场景
6. [[AI/OpenClaw/Openclaw-多智能体|Openclaw-多智能体]] — 多智能体架构（2974 行，全库最大文档）
7. [[AI/OpenClaw/Ubuntu-2510-Setup-Guide|Ubuntu-2510-Setup-Guide]] — Ubuntu 环境搭建

### Hermes Agent 路径
1. [[AI/Hermes-agent/Hermes Agent 资源合集|资源合集]] — 中文/全球资源索引
2. [[AI/Hermes-agent/Ubuntu 25.10 安装与使用 Hermes Agent 指南|Ubuntu 安装指南]] — 部署与 OpenClaw 迁移
3. [[AI/Hermes-agent/Hermes与OpenClaw对比及飞书接入指南|架构解析与对比]] — 五层架构、记忆系统、飞书接入
4. [[AI/Hermes-agent/Hermes满配指南-五大配置模块|满配指南]] — 五大配置模块实操

### AI 行业动态
1. [[AI/行业动态/Claude-Code创始人红杉大会七个判断|Boris Cherny 红杉大会七个判断]] — 代码价值重估、MCP 定位、SaaS 护城河瓦解、创业机会窗口

### 补充
- [[AI/HarnessKit|HarnessKit]] — AI 编码智能体统一管理工具（Skills/MCP/Plugins/Hooks 跨 Agent 管理）
- [[AI/GithubCopilot/Copilot CLI|Copilot CLI]] — GitHub Copilot CLI
- [[AI/提示词|提示词]] — 提示词工程

---

## 📂 全部文档

### Claude Code（5 篇）

| 文章 | 主题 | 关键词 |
|------|------|--------|
| [[AI/ClaudeCode/ClaudeCode基础指南|ClaudeCode基础指南]] | 全面指南 | 安装、配置、使用场景 |
| [[AI/ClaudeCode/Claude Code 扩展体系|扩展体系]] | 四层扩展机制 | MCP、Skills、Slash Commands、Plugin |
| [[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams|多智能体协作]] | Subagents 与 Agent Teams | 并行任务、团队协作 |
| [[AI/ClaudeCode/Claude-Skill质检工具-SkillCraft|Skill Craft 质检工具]] | Skill 质量工程 | 7 类失效模式、三层评估、check/fix/create/audit |
| [[AI/ClaudeCode/Claude-Code-Harness实战-最小可用系统|Harness 实战]] | 安全约束系统 | 四层架构、Hooks 拦截器、规范先行、Git 门禁 |

### Obsidian 知识库（4 篇）

| 文章 | 主题 | 关键词 |
|------|------|--------|
| [[AI/Obsidian/obsidian-claude-搭建个人知识库|obsidian-claude-搭建个人知识库]] | 知识库搭建 | Obsidian + Claude Code 集成 |
| [[AI/Obsidian/obsidian-claude-code-AI知识管家|Claude Code+Obsidian 知识管家]] | 为什么+上手 | Markdown 母语、30 分钟四步、自动 backlinks |
| [[AI/Obsidian/karpathy-llm-wiki-改造计划|karpathy-llm-wiki-改造计划]] | Wiki 改造 | Karpathy LLM Wiki 模式落地 |
| [[AI/Obsidian/Obsidian可视化Skills-Excalidraw-Mermaid-Canvas|Obsidian可视化Skills]] | AI 可视化 | Excalidraw、Mermaid、Canvas、Skills |

### OpenClaw（7 篇）

| 文章 | 主题 | 关键词 |
|------|------|--------|
| [[AI/OpenClaw/OpenClaw-基础-安装|OpenClaw-基础-安装]] | 基础安装 | 环境搭建、配置 |
| [[AI/OpenClaw/OpenClaw-Channels|OpenClaw-Channels]] | Channel | 通信通道、集成 |
| [[AI/OpenClaw/OpenClaw-Skills-Plugins|OpenClaw-Skills-Plugins]] | Skills 插件 | 自定义能力 |
| [[AI/OpenClaw/CoPaw|CoPaw]] | CoPaw | 交互式工具 |
| [[AI/OpenClaw/Openclaw-AIOps|Openclaw-AIOps]] | AIOps | 智能运维 |
| [[AI/OpenClaw/Openclaw-多智能体|Openclaw-多智能体]] | 多智能体 | Agent 协作、工作流编排 |
| [[AI/OpenClaw/Ubuntu-2510-Setup-Guide|Ubuntu-2510-Setup-Guide]] | Ubuntu 配置 | 开发环境 |

### 行业动态（1 篇）

| 文章 | 主题 | 关键词 |
|------|------|--------|
| [[AI/行业动态/Claude-Code创始人红杉大会七个判断\|Boris Cherny 红杉大会七个判断]] | AI 行业趋势 | 代码民主化、MCP 定位、SaaS 瓦解、创业机会、Computer Use |

---

## 📑 来源摘要
- [[KnowledgeBase/sources/cloudops-agent-batch-summary|CloudOps-Agent 批量摘要]] — 57 篇，三语言智能 OnCall Agent
- [[KnowledgeBase/sources/rag-agent-batch-summary|RAG-Agent 批量摘要]] — 33 篇，企业 RAG 知识库系统
- [[KnowledgeBase/sources/hermes-agent-batch-summary|Hermes-agent 批量摘要]] — 3 篇，Hermes Agent 安装、资源合集与架构解析
- [[KnowledgeBase/sources/k8s-report-skills-summary|K8s 巡检 Skills 摘要]] — K8s 集群巡检 Python/Shell 技能
- [[KnowledgeBase/sources/obsidian-claude-code-AI知识管家-summary|AI 知识管家摘要]] — Obsidian+Claude Code 最优解论证与上手路径

---

## 🔗 与其他领域的连接

- **K8s 自动化：** AI 辅助 K8s 资源管理 → [[Python/python-运维开发/python-kubernetes-module|python-kubernetes-module]]
- **监控告警：** AI 辅助告警分析 → [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus基础|Prometheus基础]]
- **知识管理：** Obsidian 知识库 → 本知识库（KnowledgeBase/）
- **日常运维：** AI 辅助 Linux 运维 → [[Python/python-运维开发/python-Linux-operation|python-Linux-operation]]

---

## 🛠️ 相关工具
[[KnowledgeBase/entities/Claude-Code|Claude-Code]]、[[KnowledgeBase/entities/OpenClaw|OpenClaw]]、[[KnowledgeBase/entities/Hermes-Agent|Hermes Agent]]、[[KnowledgeBase/entities/MCP|MCP]]、[[KnowledgeBase/entities/Obsidian|Obsidian]]、[[AI/HarnessKit|HarnessKit]]
