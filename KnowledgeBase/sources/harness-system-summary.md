---
title: Harness 实战摘要
tags:
  - knowledgebase/source
  - ai/claude-code
  - ai/harness
date: 2026-05-05
sources:
  - "[[AI/ClaudeCode/Claude-Code-Harness实战-最小可用系统]]"
aliases:
  - Harness System Summary
---

# Harness 实战：从零搭建最小可用的 Harness 系统

## 元信息

- **原始文档**：[[AI/ClaudeCode/Claude-Code-Harness实战-最小可用系统]]
- **领域**：AI / Claude Code 安全约束
- **摄入日期**：2026-05-05

## 摘要

本文针对 Claude Code 在实际项目中暴露的三类安全问题（凭证泄露到代码注释、越界修改 migrations 目录、Bash 输出中间结果被写入代码），提出了一套基于系统强制执行（而非提示词软约束）的 Harness 四层架构，覆盖约束层、工具层、中间件层、编排层，加上 Git 门禁作为最后防线。

## 关键知识点

1. **核心原则**：提示词是软约束（AI 可以听也可以不听），真正有效的方式是系统层面强制执行边界——"不是靠 AI 自觉，是靠系统强制"
2. **四层架构**：约束层（CLAUDE.md + ARCHITECTURE.md 行为边界）→ 工具层（settings.local.json 最小权限）→ 中间件层（三层拦截器：pre-tool-guard.py 事前拦截 / post-output-guard.py 事后审查 / session-summary.sh 会话摘要）→ 编排层（/追问 → /固化 → /实现 → /验证 规范先行流程）
3. **Hooks 机制实战**：通过 Claude Code 的 PreToolUse / PostToolUse hooks 注册 Python 拦截脚本，实现对敏感文件访问的自动拦截和输出凭证扫描
4. **规范先行工作流**："规范是 AI 和人共同签署的合约"——追问挖掘隐含假设 → 固化形成书面规范 → 按规范实现 → 逐条验证；但简单需求应跳过此流程，避免过度流程化
5. **实际效果**：凭证泄露和越界修改基本消失、代码返工率下降、对话轮次从 3-4 轮降至 1-2 轮；10 小时一次性投入，新项目 5 分钟复用

## 涉及的概念与实体

- [[KnowledgeBase/entities/Claude-Code|Claude-Code]]

## 值得注意

- 文章提供了三个拦截器的**完整可运行代码**（pre-tool-guard.py / post-output-guard.py / session-summary.sh）和 settings.local.json 注册配置，可直接复用
- 踩坑经验：post-output-guard 检测 `password` 变量名导致误报率过高，解决方案是只检测真正的密钥格式（16位+字母数字组合前带 `=`/`:`）
- 编排层流程应按需启用——简单需求直接实现，复杂需求才走规范流程，"流程是为复杂度服务的，不是必须遵守的教条"
- 与 [[AI/HarnessKit|HarnessKit]]（Rust 跨 Agent 管理工具）是不同维度的工具：本文 Harness 聚焦单项目安全约束，HarnessKit 聚焦多 Agent 配置统一管理
