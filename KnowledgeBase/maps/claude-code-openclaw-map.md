---
title: Claude Code & OpenClaw 专题地图
tags:
  - knowledgebase/map
  - knowledgebase/ai
  - knowledgebase/claude-code
  - knowledgebase/openclaw
date: 2026-04-16
---

# 🧠 Claude Code & OpenClaw 专题地图

> [!info] 专题范围
> 深入对比两大 AI 工具平台的架构、能力和使用场景，帮助读者选择和组合使用。

---

## 平台对比

| 维度 | Claude Code | OpenClaw |
|------|-------------|----------|
| **定位** | AI 编码助手 + 知识管理 | AI 多智能体运维平台 |
| **核心能力** | 代码生成/修改、MCP 工具调用、知识库构建 | AIOps、多智能体协作、Channel 集成 |
| **扩展机制** | Skills + Plugin + MCP | Skills + Channels + CoPaw |
| **运维场景** | 代码审查、文档整理、脚本编写 | 智能告警、自动修复、运维编排 |
| **文档量** | 5 篇（MCP/Skills/SlashCmd/Plugin 已合并） | 7 篇 |

---

## Claude Code 知识体系

```
ClaudeCode基础指南
    ├── Claude Code 扩展体系 (MCP + Skills + Slash Commands + Plugin)
    ├── 多智能体协作 (Subagents + Agent Teams)
    └── obsidian-claude-搭建个人知识库 (实战)
```

**核心文章：**
- [[AI/ClaudeCode/ClaudeCode基础指南|ClaudeCode基础指南]] — 从零开始
- [[AI/ClaudeCode/Claude Code 扩展体系|扩展体系]] — ==MCP、Skills、Slash Commands、Plugin 四层扩展机制全解==
- [[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams|多智能体协作]] — Subagents + Agent Teams

---

## OpenClaw 知识体系

```
OpenClaw-基础-安装
    ├── OpenClaw-Channels (通信通道)
    ├── OpenClaw-Skills-插件 (能力扩展)
    ├── CoPaw (交互式工具)
    ├── Openclaw-AIOps (智能运维)
    ├── Openclaw-多智能体 (工作流编排) ← 核心
    └── Ubuntu-2510-Setup-Guide (环境)
```

**核心文章：**
- [[AI/OpenClaw/OpenClaw-基础-安装|OpenClaw-基础-安装]] — 从零开始
- [[AI/OpenClaw/Openclaw-多智能体|Openclaw-多智能体]] — ==多智能体是 OpenClaw 的核心架构==（2974 行）
- [[AI/OpenClaw/Openclaw-AIOps|Openclaw-AIOps]] — AIOps 运维落地

---

## 共同概念

| 概念 | Claude Code | OpenClaw |
|------|-------------|----------|
| **Skills** | [[AI/ClaudeCode/Claude Code 扩展体系|扩展体系（Skills 章节）]] | [[AI/OpenClaw/OpenClaw-Skills-插件|OpenClaw-Skills-插件]] |
| **Agent/多智能体** | [[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams|多智能体协作]] | [[AI/OpenClaw/Openclaw-多智能体|Openclaw-多智能体]] |
| **扩展接口** | [[AI/ClaudeCode/Claude Code 扩展体系|MCP + Skills + Slash Commands + Plugin]] | [[AI/OpenClaw/OpenClaw-Channels|OpenClaw-Channels]] |

---

## 组合使用场景

> [!tip] 推荐组合
> - **Claude Code + Obsidian**：知识库管理、文档编写、代码审查
> - **OpenClaw + K8s**：智能运维、自动化告警处理
> - **Claude Code + OpenClaw**：Claude Code 写代码，OpenClaw 编排部署

---

## 🔗 关联概念
- [[KnowledgeBase/entities/Claude-Code|Claude-Code]]
- [[KnowledgeBase/entities/OpenClaw|OpenClaw]]
- [[KnowledgeBase/entities/MCP|MCP]]
- [[KnowledgeBase/entities/Obsidian|Obsidian]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]
