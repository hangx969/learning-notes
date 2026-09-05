---
title: Codex Host 多厂商 Harness 接入摘要
tags:
  - knowledgebase/source
  - ai/codex
  - ai/harness
date: 2026-09-05
sources:
  - "[[0raw/在 Codex 里随时切换不同厂家的 Harness]]"
aliases:
  - Codex Host Harness Summary
  - codex-host
---

# Codex Host：在 Codex 中切换多厂商 Harness

## 元信息

- **原始文档**：[[0raw/在 Codex 里随时切换不同厂家的 Harness]]
- **领域**：AI / Codex / 多智能体协作
- **摄入日期**：2026-09-05

## 摘要

本文介绍开源项目 `BytePioneer-AI/codex-host`：它被描述为可将 Claude Code、DeepSeek Harness、Pi、Grok Build 等不同厂商的 Harness 接入 Codex 界面，并在其中切换使用。文章称，切换后仍可沿用 Codex 的 Thread、Diff、工具状态、审批、Fork 与上下文压缩等交互。文中还提出按角色分工的协作方式：Codex 编码，Claude Code 审查，Pi 调查缺陷；各 Agent 使用独立 Thread 以隔离任务。

## 关键知识点

1. **统一入口**：`codex-host` 的目标是把多个 Agent Harness 汇集到 Codex 中，而非为每个 Harness 另行使用终端界面。
2. **交互继承**：来源声称切换 Harness 后可继续使用 Codex 原有的任务线程、差异查看、工具状态、审批、Fork 与上下文压缩能力；该兼容性尚未在本仓库验证。
3. **角色化协作**：可将编码、代码审查和 Bug 调查交给不同 Agent，借助独立 Thread 保持任务隔离，再在同一界面中协作。
4. **项目线索**：文中给出的开源项目为 `BytePioneer-AI/codex-host`；来源未提供安装步骤、支持矩阵、认证方式或稳定性信息。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Codex|Codex]]
- [[KnowledgeBase/entities/Claude-Code|Claude Code]]

## 值得注意

- 本文是简短项目介绍，关于支持的 Harness、功能兼容性和跨 Agent 协作的表述均来自原文，尚未通过项目文档或实际运行验证。
- 它与 [[KnowledgeBase/sources/harness-system-summary|Harness 实战摘要]] 的范围不同：后者讨论单项目内的安全约束系统；本文关注跨厂商 Harness 的统一入口与协作界面。
