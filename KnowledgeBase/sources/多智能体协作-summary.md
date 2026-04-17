---
title: 多智能体协作来源摘要
tags:
  - knowledgebase/source
  - ai/claude-code
date: 2026-04-17
sources:
  - "[[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams]]"
---

## 元信息

- **原始文档**：[[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams]]
- **领域**：AI / Claude Code
- **摄入日期**：2026-04-17

## 摘要

Claude Code 提供两种多智能体并行工作机制。**Subagents** 是独立的 Claude 副本，通过 Markdown 文件定义角色和工具配置，执行结果返回给 Claude Code 汇总后呈现给用户，适合聚焦型独立任务。**Agent Teams** 是升级形态，多个 Claude Code 实例组成团队协作，通过共享任务列表和 Mailbox 消息系统实现队友间直接通信和自主协调，适合需要讨论、互相挑战的复杂协作场景。

## 关键知识点

### Subagents
1. 每个 SubAgent 是完全独立的 Claude 副本，由 5 个字段定义：name、description、tools、model、system
2. 产品逻辑：SubAgent → 结果返回 Claude Code → Claude Code 汇总后呈现给用户（"多专家会诊"模式）
3. 存储位置：项目级（`.claude/agents/`，优先级高）或全局级（`~/.claude/agents/`），名称冲突时项目级覆盖全局级
4. 典型场景：5 个并行 SubAgent 审查支付模块，30 分钟 vs 2.5 小时串行，5 倍 Token 但节省 80% 时间
5. 适用性：★★★★★ 多角度审查/规划/文档；★☆☆☆☆ 依赖任务/敏感数据/单一复杂任务

### Agent Teams
6. 启用方式：环境变量 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`，需要 v2.1.32+
7. 四大组件：Team Lead（协调者）、Teammates（独立工作者）、Task List（共享任务列表，支持依赖关系和文件锁）、Mailbox（消息系统）
8. 两种显示模式：In-process（默认，`Shift+Down` 切换）和 Split panes（tmux/iTerm2）
9. 最佳场景：并行代码评审、竞争假设调试（辩论结构避免锚定效应）、新模块开发、跨层协调
10. 计划审批机制：队友在只读 plan 模式下制定计划，Lead 审批通过后才能实施
11. Hooks 门禁：TeammateIdle / TaskCreated / TaskCompleted 支持退出码 2 拦截
12. 团队规模建议：起步 3-5 人，每人 5-6 个任务，3 个聚焦优于 5 个分散
13. 已知限制：实验性功能，不支持会话恢复、嵌套团队、Lead 转让，每个会话只能一个团队

### 核心区别
14. Subagents 只能向调用者汇报，Agent Teams 队友之间可直接通信
15. Subagents 由主 Agent 管理，Agent Teams 通过共享任务列表自主协调
16. Subagents Token 成本较低（结果摘要），Agent Teams 成本较高（每个队友独立上下文窗口）

## 涉及的概念与实体

- [[KnowledgeBase/entities/Claude-Code|Claude Code]]：Subagents 和 Agent Teams 的宿主平台
- [[KnowledgeBase/entities/MCP|MCP]]：队友从项目设置加载 MCP 服务器

## 值得注意

- Agent Teams 的**辩论结构**（competing hypotheses）是独有的高价值模式——利用多个独立调查者互相推翻理论避免锚定效应，SubAgents 无法实现（因不通信）
- SubAgent 的无状态特性使其不适合迭代调试，这是重要的架构限制
- 可复用已有 Subagent 定义来创建 Agent Teams 队友，实现角色复用
- GitHub 上的 [awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) 包含 100+ 个现成 Agent
