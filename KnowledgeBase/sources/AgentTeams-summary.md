---
title: Agent Teams 来源摘要
tags:
  - knowledgebase/source
  - ai/claude-code
date: 2026-04-17
sources:
  - "[[AI/ClaudeCode/Agent Teams]]"
---

## 元信息

- **原始文档**：[[AI/ClaudeCode/Agent Teams]]
- **领域**：AI / Claude Code
- **摄入日期**：2026-04-17

## 摘要

Claude Code Agent Teams 是多智能体协作功能，让多个 Claude Code 实例组成团队协同工作。一个 Team Lead 负责协调，多个 Teammates 各自独立工作，通过共享任务列表和 Mailbox 消息系统实现自主协调和直接通信。与 SubAgents 的核心区别在于队友间可以互相发消息、共享发现和互相挑战，而非只向主 Agent 汇报。

## 关键知识点

1. **启用方式**：设置环境变量 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`，需要 Claude Code v2.1.32+
2. **四大组件**：Team Lead（协调者）、Teammates（独立工作者）、Task List（共享任务列表，支持依赖关系和文件锁认领）、Mailbox（消息系统）
3. **两种显示模式**：In-process（默认，`Shift+Down` 切换队友）和 Split panes（tmux/iTerm2 分屏，每个队友独立窗格）
4. **与 SubAgents 的区别**：SubAgents 只能向调用者汇报，Agent Teams 队友之间可直接通信、共享任务列表、自主认领任务
5. **最佳使用场景**：并行代码评审、竞争假设调试、新模块开发、跨层协调
6. **不适合场景**：顺序依赖任务、编辑同一文件、依赖关系复杂的工作
7. **计划审批机制**：可要求队友在只读 plan 模式下先制定计划，Lead 审批通过后才能实施
8. **Hooks 质量门禁**：TeammateIdle / TaskCreated / TaskCompleted 三个 Hook 支持退出码 2 拦截
9. **团队规模建议**：起步 3-5 人，每人 5-6 个任务，3 个聚焦队友优于 5 个分散队友
10. **已知限制**：实验性功能，不支持会话恢复、嵌套团队、Lead 转让，每个会话只能一个团队

## 涉及的概念与实体

- [[KnowledgeBase/entities/Claude-Code|Claude Code]]：Agent Teams 的宿主平台
- [[KnowledgeBase/entities/MCP|MCP]]：队友从项目设置加载 MCP 服务器

## 值得注意

- Agent Teams 是 SubAgents 的**升级形态**，核心增量是队友间的直接通信和共享任务列表的自主协调
- **辩论结构**（competing hypotheses）是 Agent Teams 独有的高价值模式——利用多个独立调查者互相推翻理论来避免锚定效应
- Token 成本随队友数量**线性增长**，每个队友都是独立的 Claude 实例
- 可复用已有的 Subagent 定义来创建队友，实现角色复用（但 `skills` 和 `mcpServers` 字段不会应用到队友）
