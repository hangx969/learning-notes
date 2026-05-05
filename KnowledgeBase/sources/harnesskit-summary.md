---
title: HarnessKit 来源摘要
tags:
  - knowledgebase/source
  - AI/agent-management
date: 2026-05-05
sources:
  - "[[AI/HarnessKit]]"
aliases:
  - HarnessKit摘要
---

# HarnessKit 来源摘要

## 元信息
- **原始文档**：[[AI/HarnessKit]]
- **领域**：AI Agent 管理工具
- **摄入日期**：2026-05-05

## 摘要
HarnessKit 是一个免费开源的 AI 编码智能体统一管理工具（Rust + TypeScript），支持从桌面、CLI 或 Web 界面管理 7 种主流 AI Agent（Claude Code、Codex、Gemini CLI、Cursor、Copilot 等）的扩展、配置、记忆和规则。核心价值在于解决多 Agent 并存时扩展分散、格式各异、缺乏安全审计的问题。

## 关键知识点
1. **五类扩展统一管理**：Skills、MCP Servers、Plugins、Hooks、Agent-first CLIs，一键跨 Agent 部署，自动处理格式差异（JSON/TOML/hook/MCP schema）
2. **安全审计引擎**：18 条静态分析规则，Trust Score（0–100）三级评分，五维权限透视（文件系统/网络/Shell/数据库/环境变量）
3. **原地管理**：直接操作 Agent 原生目录，启用/禁用仅文件重命名，零拷贝零残留
4. **三种使用模式**：桌面应用（macOS DMG）、CLI（`hk` 命令，全平台）、Web 模式（`hk serve`，适合服务器/HPC 环境）
5. **市场集成**：skills.sh（Skills 注册表）、Smithery（MCP 服务器）、Agent-first CLI 发现

## 涉及的概念与实体
- [[KnowledgeBase/entities/Claude-Code|Claude-Code]]
- [[KnowledgeBase/entities/MCP|MCP]]
- [[KnowledgeBase/entities/OpenClaw|OpenClaw]]（路线图中计划支持）

## 值得注意
- HarnessKit 的定位是**元管理层**（meta-management layer），不替代任何 Agent，而是在所有 Agent 之上提供统一视角
- 与 OpenClaw 的 Clawhub（Skills 管理）有功能重叠，但 HarnessKit 覆盖更多 Agent 且侧重安全审计
- 路线图中计划支持 Hermes-agent 和 OpenClaw，有可能成为本仓库 AI 工具生态的统一管理入口
- 项目使用 Rust 编写核心逻辑，Tauri 框架实现桌面应用，Web 前端基于 Vite + TypeScript
