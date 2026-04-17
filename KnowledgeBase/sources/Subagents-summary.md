---
title: Subagents
tags:
  - knowledgebase/source
  - ai/claude-code
date: 2026-04-17
sources:
  - "[[AI/ClaudeCode/Subagents]]"
---

# Subagents

## 元信息
- **原始文档**：[[AI/ClaudeCode/Subagents]]
- **领域**：AI / Claude Code
- **摄入日期**：2026-04-17

## 摘要
SubAgent 是 Claude Code 中完全独立的 Claude 副本，通过 Markdown 文件定义系统提示和工具配置。每个 SubAgent 拥有手动指定的角色、提供的上下文、明确的任务边界和输出格式。SubAgent 将结果返回给 Claude Code（而非直接返回用户），由 Claude Code 综合所有结果后呈现给用户。典型场景如 5 个并行 SubAgent 审查支付模块，可将 2.5 小时串行工作压缩至 30 分钟，虽消耗 5 倍 token 但节省 80% 时间。

## 关键知识点
1. 每个 SubAgent 是完全独立的 Claude 副本，包含：手动指定的角色、提供的上下文、明确的任务边界和输出
2. SubAgent = 用户定义的系统提示 + 工具配置组合，通过 Markdown（.md）文件定义
3. 5 个组成部分：名称、描述（何时调用）、工具（可设置多个）、模型、系统提示（角色、规则、输出风格、工作流）
4. 产品逻辑：SubAgent 将结果返回给 Claude Code（而非用户），Claude Code 综合所有 SubAgent 结果后呈现给用户
5. 存储位置：项目级（`.claude/agents/`，优先级更高）或全局级（`~/.claude/agents/`，优先级更低），名称冲突时项目级覆盖全局级
6. 放置在正确目录后由 Claude Code 自动检测
7. 典型场景：5 个并行 SubAgent 审查支付模块（架构、安全、性能、代码质量、数据库）——30 分钟 vs 2.5 小时串行，5 倍 token 但节省 80% 时间
8. 适用性评级：★★★★★ 多角度审查/规划/文档；★★★★ 批处理/API 测试；★★ 迭代调试（无状态限制）；★ 依赖任务/敏感数据/单一复杂任务
9. 资源：GitHub 上的 awesome-claude-code-subagents 包含 100+ 个 agent

## 涉及的概念与实体
- [[KnowledgeBase/entities/Claude-Code|Claude-Code]]

## 值得注意
- SubAgent 的无状态特性使其不适合迭代调试场景，这是一个重要的架构限制
- 产品逻辑中 SubAgent 结果先汇总到 Claude Code 再呈现给用户，实现了"多专家会诊"模式
- 项目级配置覆盖全局级配置的设计，便于团队在项目层面统一 agent 定义
