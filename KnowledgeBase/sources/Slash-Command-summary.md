---
title: Slash Command
tags:
  - knowledgebase/source
  - ai/claude-code
date: 2026-04-17
sources:
  - "[[AI/ClaudeCode/Slash Command]]"
---

# Slash Command

## 元信息
- **原始文档**：[[AI/ClaudeCode/Slash Command]]
- **领域**：AI / Claude Code
- **摄入日期**：2026-04-17

## 摘要
Slash Commands 是 Claude Code 中由用户手动触发的工作流快捷方式，存储在 `.claude/commands/` 目录中，以纯 Markdown 定义多步骤流程。与 Skills 的关键技术区别在于，Slash Commands 以用户消息展开的方式注入，而非作为系统提示工具。它们可以在内部调用 Skills、SubAgents、MCP 工具和 Git 操作，适用于发布、安全检查、性能审计等场景，显著降低了版本发布错误率。

## 关键知识点
1. Slash Commands 是手动触发的工作流快捷方式，存储在 `.claude/commands/` 目录中
2. 以纯 Markdown 定义多步骤流程，通过输入 `/command-name` 触发
3. 技术区别：以用户消息展开（user message expansion）方式注入，而非作为系统提示工具（system prompt tools），这是与 Skills 的关键差异
4. 可在内部调用：Skills（自动化检查）、SubAgents（并行工作）、MCP 工具、Git 操作
5. 6 个典型用例：/release（完整发布流程）、/security-check、/perf-audit、/refactor-plan、/onboard（新人入职）、/rollback
6. /release 示例：定义了从代码拉取到通知的 7 个步骤，每一步都需要用户确认
7. 效果："版本发布错误率从 15% 降至 0"

## 涉及的概念与实体
- [[KnowledgeBase/entities/Claude-Code|Claude-Code]]

## 值得注意
- Slash Commands 与 Skills 的核心技术区别在于注入方式：用户消息展开 vs 系统提示工具
- /release 命令通过强制每步用户确认，将发布错误率从 15% 降至 0，体现了人机协作的最佳实践
- 纯 Markdown 定义使得命令易于版本控制、团队共享和迭代改进
