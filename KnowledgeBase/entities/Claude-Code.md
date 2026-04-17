---
title: Claude Code
tags:
  - knowledgebase/entity
  - ai/claude-code
date: 2026-04-17
sources:
  - "[[AI/ClaudeCode/ClaudeCode基础指南]]"
  - "[[AI/ClaudeCode/Claude Code 扩展体系]]"
  - "[[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams]]"
  - "[[AI/ClaudeCode/obsidian-claude-搭建个人知识库]]"
  - "[[AI/skills/k8s-report-skills/SKILL.md]]"
---

# Claude Code

## 简介

Claude Code (CC) 是 Anthropic 推出的 CLI 形态 AI 编程助手。它以项目文件夹为作用域（单一项目原则），提供 3 种交互模式，并通过 MCP、Skills、SubAgents、Slash Commands、Plugin 五层扩展机制构成完整的智能工作流系统——不只是聊天机器人，而是可编排、可扩展、可沉淀知识的开发基础设施。

## 核心架构：7 层能力栈

### 1. 基础交互层

CC 提供 3 种操作模式：

- **Normal 模式**：每步操作需人工确认，适合探索和学习
- **Plan 模式**：先讨论方案再执行，适合复杂任务的前期规划
- **Auto-accept 模式**：自动执行所有操作，适合重复性任务

Extended Thinking 支持 4 级思考深度，通过自然语言触发：

| 触发词 | 思考深度 | 适用场景 |
|--------|---------|---------|
| `think` | 基础 | 简单逻辑推理 |
| `think hard` | 中等 | 多步骤问题 |
| `think harder` | 深度 | 复杂架构决策 |
| `ultrathink` | 最深 | 高难度系统设计 |

### 2. 记忆层 (Claude.md)

Claude.md 是 CC 的持久记忆机制，分两级：

- **用户级** (`~/.claude/CLAUDE.md`)：全局偏好，跨项目生效
- **项目级** (项目根目录 `CLAUDE.md`)：项目特定的规范、技术栈、约定

创建方式：`/init` 命令自动生成，或通过 `# memory` 手动追加。

**Spec 工作流**是记忆层的高级应用，解决长对话中上下文丢失问题，分 4 步：
1. 需求文档 → 2. 技术方案文档 → 3. TODO 拆解 → 4. spec.md 整合

每步产出物都持久化为文件，即使上下文窗口截断也不会丢失关键信息。

### 3. MCP 扩展层

MCP (Model Context Protocol) 为 CC 提供外部工具集成能力。

**必装三件套：**
- **memory**：跨会话持久化记忆
- **context7**：实时拉取最新库文档，避免训练数据过时
- **sequential-thinking**：结构化多步推理，提升复杂问题解决质量

**已记录的 10+ MCP 服务器：**

| 服务器 | 用途 |
|--------|------|
| atlassian | Jira/Confluence 集成 |
| bitbucket | 代码仓库操作 |
| playwright | 浏览器自动化测试 |
| filesystem | 文件系统操作 |
| github | GitHub API 集成 |
| exa | AI 搜索引擎 |
| deepwiki | GitHub 仓库文档生成 |
| drawio | 流程图/架构图生成 |
| mcp-obsidian | Obsidian 笔记库集成 |
| context7 | 实时文档查询 |

### 4. Skills 技能层

Skills（2025 年 10 月推出）是自动触发的能力包，采用渐进式加载设计：

- **元数据优先**：CC 启动时只加载 Skills 的描述信息（metadata）
- **按需加载**：匹配到用户意图后才注入完整 Skill 内容（作为 system prompt）

**3 层使用模式：**
1. **单点自动化**：单个 Skill 完成特定任务（如代码审查、文档生成）
2. **编排式工作流**：多个 Skills 按序协作完成复杂流程
3. **团队智能**：Skills 沉淀团队最佳实践，新成员即插即用

### 5. SubAgents 子智能体

SubAgent 是独立的 Claude 副本，可并行执行任务。每个 SubAgent 由 5 个组件定义：

| 组件 | 作用 |
|------|------|
| name | 标识符 |
| description | 能力描述 |
| tools | 可用工具集 |
| model | 使用的模型 |
| system | 系统提示词 |

数据流向：SubAgent 执行 → 结果返回 CC → CC 汇总后呈现给用户。SubAgent 之间不直接通信，由 CC 主进程协调。

### 5.5 Agent Teams 多智能体团队

Agent Teams 是 SubAgents 的升级形态——多个 Claude Code 实例组成团队协作：

| 对比项 | SubAgents | Agent Teams |
|--------|-----------|-------------|
| 通信 | 只能向主 Agent 汇报 | 队友之间直接互发消息 |
| 协调 | 主 Agent 管理 | 共享任务列表，自主认领 |
| 适用 | 聚焦型任务 | 复杂协作（评审、调试、跨层开发） |
| 成本 | 较低 | 较高（每个队友独立上下文窗口） |

核心组件：Team Lead（协调者）+ Teammates（独立工作者）+ Task List（共享任务）+ Mailbox（消息系统）。支持 in-process 和 split panes（tmux/iTerm2）两种显示模式。当前为实验性功能（需 v2.1.32+）。

### 6. Slash Commands 斜杠命令

斜杠命令是存放在 `.claude/commands/` 目录下的手动触发工作流快捷方式。

**与 Skills 的关键区别：**
- Skills：作为 **system prompt** 注入，自动触发
- Slash Commands：作为 **user message** 注入，手动触发

Slash Commands 可以编排 Skills + SubAgents + MCP，是构建自定义工作流的入口。

### 7. Plugin 插件

Plugin 是应用级打包容器，将多种扩展机制捆绑为一个可分发单元：

| 组成 | 数量上限 |
|------|---------|
| Skills | 5 |
| Slash Commands | 10 |
| MCP 服务器 | 3 |
| SubAgents | 2 |
| Hooks | (未详细展开) |

**建议：Plugin 不超过 3 个**，避免启动卡顿和功能重复。

## 关键工作流模式

### Spec 驱动开发
需求文档 → 技术方案文档 → TODO 拆解 → spec.md → 逐项实现。每步产出持久化文件，解决长任务中上下文丢失问题。

### 事故应急响应
1. 并行分流：3 个 SubAgent 同时采集日志、指标、变更记录
2. 根因分析：sequential-thinking MCP 结构化推理
3. 方案生成：输出 3 套缓解方案供选择
4. 执行修复

实测 MTTR 从 45 分钟降至 12 分钟。

### 遗留项目接手
1. Explore SubAgent 扫描项目结构
2. 并行分析：架构 + 数据库 + 安全性三路 SubAgent
3. 技术债评估与优先级排序
4. 知识沉淀：通过 memory MCP 持久化分析结果

### 代码审查
1. 自动检测文件类型
2. 分派专业 SubAgent（前端/后端/安全/性能）
3. 输出按严重级别分级的审查报告

实测生产事故率降低 60%。

## 最佳实践

1. **单一项目原则**：每个项目单独文件夹，避免上下文混乱
2. **Plan 模式优先**：先讨论方案再执行，减少返工
3. **三件套起步**：memory + context7 + sequential-thinking MCP
4. **文档驱动**：Spec 工作流解决上下文丢失问题
5. **知识沉淀**："好的工具链会自己长知识"——让 Claude.md 和 memory 持续积累
6. **Plugin 不超过 3 个**：避免启动卡顿和功能冲突

## 推荐 MCP 组合

| 场景 | 推荐组合 |
|------|---------|
| 日常开发 | filesystem + github + memory |
| 深度工作 | sequential-thinking + context7 + memory |
| 自动化任务 | playwright + filesystem |
| 学习新技术 | context7 + deepwiki + exa |

## 相关概念与实体

- [[KnowledgeBase/entities/MCP|MCP]]：Claude Code 的外部工具集成协议
- [[KnowledgeBase/entities/Obsidian|Obsidian]]：通过 Claudian 插件 + MCP 集成的知识管理平台
- [[KnowledgeBase/entities/OpenClaw|OpenClaw]]：开源 AI 工具平台
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]：CC 的核心应用场景之一

## 在本仓库中的覆盖

- [[AI/ClaudeCode/ClaudeCode基础指南]]：模式选择、思考模式、Claude.md、Spec 工作流、实战场景、最佳实践（最全面的综合指南）
- [[AI/ClaudeCode/Claude Code 扩展体系]]：四层扩展机制全解——MCP（10+ 服务器配置）、Skills（3 层使用模式）、Slash Commands（手动工作流）、Plugin（打包分发）
- [[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams]]：SubAgent（5 组件架构、适用场景评级）+ Agent Teams（Team Lead/Teammates/Task List/Mailbox、竞争假设调试）+ 开源 Agent 生态（wshobson/agents：112 个 Agent、72 个插件）
- [[AI/ClaudeCode/obsidian-claude-搭建个人知识库]]：Obsidian 集成方案（Claudian + Skills + MCP）
- [[AI/skills/k8s-report-skills/SKILL.md]]：自研 K8s 巡检 Skill（Python kubernetes 客户端 + Jinja2 HTML 报告），Agent 驱动的集群健康检查

## 知识空白

- Claude Code 的 **Hooks 机制**（文档中提及但未展开）
- Claude Code 的**计费模型和成本优化**策略
- Claude Code 与其他 AI 编程工具（Cursor、GitHub Copilot）的**横向对比**
- Claude Code **API 模式 vs CLI 模式**的差异
