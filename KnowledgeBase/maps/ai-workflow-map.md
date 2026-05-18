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
6. [[AI/ClaudeCode/CLAUDE.md最佳实践-21条指令清单|CLAUDE.md 21 条指令]] — 五维度通用指令清单（沟通/行为/上下文/记忆/安全）
7. [[AI/ClaudeCode/CLAUDE.md最佳实践-12条规则模板|CLAUDE.md 12 条规则]] — Karpathy 4 条 + 8 条新规则，实测错误率 41%→3%
8. [[AI/ClaudeCode/code-review-graph-本地代码知识图谱|code-review-graph 代码知识图谱]] — 本地 AST 图谱 + MCP 接入，blast-radius 影响范围分析
9. [[AI/ClaudeCode/planning-with-files-AI项目规划Skill|Planning with Files]] — 文件化规划 Skill，3 个 Markdown 文件实现外置记忆+结构化推进

### OpenClaw 路径
1. [[AI/OpenClaw/OpenClaw-基础-安装|OpenClaw-基础-安装]] — 入门安装
2. [[AI/OpenClaw/OpenClaw-Channels|OpenClaw-Channels]] — Channel 配置
3. [[AI/OpenClaw/OpenClaw-Skills-Plugins|OpenClaw-Skills-Plugins]] — Skills 插件开发
4. [[AI/OpenClaw/CoPaw|CoPaw]] — CoPaw 工具
5. [[AI/OpenClaw/Openclaw-AIOps|Openclaw-AIOps]] — AIOps 运维场景
6. [[AI/OpenClaw/Openclaw-多智能体|Openclaw-多智能体]] — 多智能体架构（2974 行，全库最大文档）
7. [[AI/OpenClaw/Ubuntu-2510-Setup-Guide|Ubuntu-2510-Setup-Guide]] — Ubuntu 环境搭建
8. [[AI/OpenClaw/OpenClaw-K8s智能运维实战|K8s 智能运维实战]] — 三阶段渐进（只读→诊断→变更）+ OPA 护栏 + 实战案例

### Hermes Agent 路径
1. [[AI/Hermes-agent/Hermes-Agent-满配指南与生态资源|满配指南与生态资源]] — 五大配置模块 + 高阶进化 + 资源合集（两篇合并）
2. [[AI/Hermes-agent/Ubuntu 25.10 安装与使用 Hermes Agent 指南|Ubuntu 安装指南]] — 部署与 OpenClaw 迁移
3. [[AI/Hermes-agent/Hermes与OpenClaw对比及飞书接入指南|架构解析与对比]] — 五层架构、记忆系统、飞书接入
4. [[AI/Hermes-agent/Hermes-Curator-Skill膨胀治理|Curator Skill 膨胀治理]] — Skill 生命周期管理、四步工作流、Agent 四种记忆

### AI 行业动态
1. [[AI/行业动态/Claude-Code创始人红杉大会七个判断|Boris Cherny 红杉大会七个判断]] — 代码价值重估、MCP 定位、SaaS 护城河瓦解、创业机会窗口
2. [[AI/行业动态/Anthropic工程师力推HTML取代Markdown-Karpathy附议|HTML 取代 Markdown]] — Anthropic 工程师 5 大论据 + Karpathy 进化路线 + 哥白尼式智能观
3. [[AI/行业动态/AI时代的Git版本管理最佳实践|AI 时代 Git 实践]] — 11 条最佳实践 + Jujutsu/GitButler 新工具 + 隔离/透明/自动化三原则

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
| [[AI/Obsidian/obsidian-claude-code-AI知识库完整指南|AI知识库完整指南]] | 完整指南 | Markdown 母语、三层架构、30 分钟上手、六大操作、改造计划（三文合并） |
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

### 行业动态（3 篇）

| 文章 | 主题 | 关键词 |
|------|------|--------|
| [[AI/行业动态/Claude-Code创始人红杉大会七个判断\|Boris Cherny 红杉大会七个判断]] | AI 行业趋势 | 代码民主化、MCP 定位、SaaS 瓦解、创业机会、Computer Use |
| [[AI/行业动态/Anthropic工程师力推HTML取代Markdown-Karpathy附议\|HTML 取代 Markdown]] | AI 输出格式 | HTML vs Markdown、信息密度、交互性、一次性编辑器、哥白尼式智能观 |
| [[AI/行业动态/AI时代的Git版本管理最佳实践\|AI 时代 Git 实践]] | Agent Git 工作流 | Atomic Commit、Checkpoint、Stacked PR、Jujutsu、GitButler、AGENT.md |

---

## 📑 来源摘要
- [[KnowledgeBase/sources/cloudops-agent-batch-summary|CloudOps-Agent 批量摘要]] — 57 篇，三语言智能 OnCall Agent
- [[KnowledgeBase/sources/rag-agent-batch-summary|RAG-Agent 批量摘要]] — 33 篇，企业 RAG 知识库系统
- [[KnowledgeBase/sources/hermes-agent-batch-summary|Hermes-agent 批量摘要]] — 4 篇，Hermes Agent 安装、资源合集、架构解析与 Curator Skill 治理
- [[KnowledgeBase/sources/k8s-report-skills-summary|K8s 巡检 Skills 摘要]] — K8s 集群巡检 Python/Shell 技能
- [[KnowledgeBase/sources/obsidian-claude-AI知识库完整指南-summary|AI知识库完整指南摘要]] — Obsidian+Claude Code 完整指南（理念+工具+操作+计划）

---

## 🔗 与其他领域的连接

- **K8s 自动化：** AI 辅助 K8s 资源管理 → [[Python/python-运维开发/python-kubernetes-module|python-kubernetes-module]]
- **监控告警：** AI 辅助告警分析 → [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus基础|Prometheus基础]]
- **知识管理：** Obsidian 知识库 → 本知识库（KnowledgeBase/）
- **日常运维：** AI 辅助 Linux 运维 → [[Python/python-运维开发/python-Linux-operation|python-Linux-operation]]

---

## 🛠️ 相关工具
[[KnowledgeBase/entities/Claude-Code|Claude-Code]]、[[KnowledgeBase/entities/OpenClaw|OpenClaw]]、[[KnowledgeBase/entities/Hermes-Agent|Hermes Agent]]、[[KnowledgeBase/entities/MCP|MCP]]、[[KnowledgeBase/entities/Obsidian|Obsidian]]、[[AI/HarnessKit|HarnessKit]]
