---
title: Claude Code Agent Teams 使用指南
tags:
  - AI
  - claude
  - agent-teams
  - multi-agent
date: 2026-04-17
source: "https://code.claude.com/docs/en/agent-teams"
---

# Claude Code Agent Teams 使用指南

## 什么是 Agent Teams

Agent Teams 是 Claude Code 的多智能体协作功能——让多个 Claude Code 实例组成团队，协同完成复杂任务。

**核心模型：**
- 一个 **Team Lead**（主会话）负责协调、分配任务、综合结果
- 多个 **Teammates**（队友）各自独立工作，拥有各自的上下文窗口
- 队友之间可以**直接通信**，不需要经过 Lead 中转
- 你也可以**直接与任意队友对话**，给它额外指令

> [!warning] 实验性功能
> Agent Teams 当前为实验性功能，默认关闭。需要 Claude Code **v2.1.32+**。
> 使用 `claude --version` 检查版本。

---

## Agent Teams vs Subagents

两者都能并行工作，但机制完全不同：

| 对比项 | Subagents | Agent Teams |
|--------|-----------|-------------|
| **上下文** | 有自己的上下文窗口，结果返回给调用者 | 有自己的上下文窗口，完全独立 |
| **通信** | 只能向主 Agent 汇报结果 | 队友之间可以直接互发消息 |
| **协调** | 主 Agent 管理所有工作 | 共享任务列表，队友自主认领 |
| **适用场景** | 聚焦型任务，只关心结果 | 复杂工作，需要讨论和协作 |
| **Token 成本** | 较低：结果摘要返回主上下文 | 较高：每个队友都是独立的 Claude 实例 |

> [!tip] 选择原则
> - 队友之间**不需要互相沟通** → 用 Subagents
> - 队友之间**需要共享发现、互相挑战** → 用 Agent Teams

---

## 启用 Agent Teams

在 `settings.json` 中添加环境变量：

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

或者直接设置 shell 环境变量：

```bash
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

---

## 最佳使用场景

Agent Teams 在以下场景中最有价值：

| 场景 | 为什么适合 Teams |
|------|-----------------|
| **研究与评审** | 多个队友同时调查问题的不同方面，然后共享和质疑彼此的发现 |
| **新模块/新功能开发** | 每个队友负责一个独立模块，互不干扰 |
| **竞争假设调试** | 多个队友并行测试不同假设，更快收敛到答案 |
| **跨层协调** | 前端、后端、测试分别由不同队友负责 |

> [!important] 不适合的场景
> - 顺序依赖的任务
> - 需要编辑同一个文件的工作
> - 依赖关系复杂的任务
>
> 这些场景用单会话或 Subagents 更高效。

---

## 快速开始

启用后，用自然语言告诉 Claude 创建团队：

```text
I'm designing a CLI tool that helps developers track TODO comments across
their codebase. Create an agent team to explore this from different angles: one
teammate on UX, one on technical architecture, one playing devil's advocate.
```

Claude 会自动：
1. 创建团队和共享任务列表
2. 为每个角色生成队友
3. 让队友并行探索问题
4. 综合所有发现
5. 工作完成后清理团队

---

## 团队控制

### 显示模式

Agent Teams 支持两种显示模式：

| 模式 | 说明 | 操作方式 |
|------|------|---------|
| **In-process**（默认） | 所有队友在主终端内运行 | `Shift+Down` 切换队友，直接打字发消息 |
| **Split panes** | 每个队友一个独立窗格 | 点击窗格即可交互，同时看到所有输出 |

**默认行为**（`"auto"`）：如果已经在 tmux 会话中则用分屏，否则用 in-process。

手动设置显示模式：

```json
// ~/.claude.json
{
  "teammateMode": "in-process"
}
```

或单次会话指定：

```bash
claude --teammate-mode in-process
```

> [!note] Split panes 依赖
> 需要安装 [tmux](https://github.com/tmux/tmux/wiki) 或 iTerm2 + [`it2` CLI](https://github.com/mkusaka/it2)。
> VS Code 集成终端、Windows Terminal、Ghostty **不支持**分屏模式。

### 指定队友数量和模型

```text
Create a team with 4 teammates to refactor these modules in parallel.
Use Sonnet for each teammate.
```

### 要求队友先制定计划

对于复杂或有风险的任务，可以要求队友在实施前先制定计划：

```text
Spawn an architect teammate to refactor the authentication module.
Require plan approval before they make any changes.
```

工作流程：
1. 队友在**只读 plan 模式**下工作
2. 完成计划后，向 Lead 发送审批请求
3. Lead 审核后**批准或驳回**
4. 驳回时队友修改计划重新提交
5. 批准后队友退出 plan 模式，开始实施

> [!tip] 影响审批标准
> 你可以在 prompt 中设定标准，如：
> - "only approve plans that include test coverage"
> - "reject plans that modify the database schema"

### 直接与队友对话

每个队友都是完整独立的 Claude Code 会话，你可以随时直接与任意队友交流：

- **In-process 模式**：`Shift+Down` 切换队友 → 直接打字发消息 → `Enter` 查看队友会话 → `Escape` 中断当前回合 → `Ctrl+T` 切换任务列表
- **Split-pane 模式**：点击队友的窗格即可直接交互

### 任务分配与认领

共享任务列表是团队协调的核心：

| 任务状态 | 说明 |
|---------|------|
| **Pending** | 待处理，可被认领 |
| **In Progress** | 正在处理中 |
| **Completed** | 已完成 |

任务可以有**依赖关系**——依赖未完成的任务不能被认领。任务认领使用**文件锁**防止竞态条件。

分配方式：
- **Lead 指派**：告诉 Lead 把哪个任务分给哪个队友
- **自主认领**：队友完成任务后自动认领下一个未分配、未阻塞的任务

### 关闭队友与清理团队

关闭单个队友：

```text
Ask the researcher teammate to shut down
```

Lead 发送关闭请求，队友可以批准（优雅退出）或拒绝（附解释）。

清理整个团队：

```text
Clean up the team
```

> [!warning] 清理注意事项
> - 清理前**先关闭所有队友**，否则清理会失败
> - **必须由 Lead 执行清理**，队友执行可能导致资源状态不一致

---

## 架构详解

### 核心组件

| 组件 | 作用 |
|------|------|
| **Team Lead** | 主会话，创建团队、分配任务、协调工作 |
| **Teammates** | 独立的 Claude Code 实例，各自处理分配的任务 |
| **Task List** | 共享任务列表，队友认领和完成任务 |
| **Mailbox** | 消息系统，队友间直接通信 |

### 存储位置

| 内容 | 路径 |
|------|------|
| 团队配置 | `~/.claude/teams/{team-name}/config.json` |
| 任务列表 | `~/.claude/tasks/{team-name}/` |

> [!caution]
> 团队配置文件由 Claude Code 自动管理（包含 session ID、tmux pane ID 等运行时状态），**不要手动编辑**，下次状态更新会覆盖你的修改。

### 团队创建方式

Agent Teams 有两种启动方式：

1. **你主动请求**：给 Claude 一个适合并行工作的任务，明确要求创建团队
2. **Claude 主动提议**：如果 Claude 判断任务适合并行，它会建议创建团队，你确认后再执行

两种方式下，**你始终保持控制权**——Claude 不会未经你同意就创建团队。

### 复用 Subagent 定义

你可以用已有的 Subagent 类型来创建队友，实现角色复用：

```text
Spawn a teammate using the security-reviewer agent type to audit the auth module.
```

队友会继承该定义的 `tools` 白名单和 `model`，定义内容**追加到**队友系统提示词（而非替换）。

注意事项：
- 团队协调工具（`SendMessage`、任务管理）**始终可用**，不受 `tools` 限制
- Subagent 定义中的 `skills` 和 `mcpServers` 字段**不会应用**到队友

### 上下文与通信

队友生成时加载与普通会话相同的项目上下文（`CLAUDE.md`、MCP 服务器、Skills），但**不继承 Lead 的对话历史**。

| 通信方式 | 说明 |
|---------|------|
| **message** | 向特定队友发消息 |
| **broadcast** | 向所有队友广播（慎用，成本随团队规模增长） |
| **自动空闲通知** | 队友完成/停止时自动通知 Lead |
| **依赖自动解锁** | 任务完成后，被依赖的任务自动解锁 |

Lead 在生成时为每个队友分配名称，任何队友都可以通过名称互相发消息。你可以在 spawn 指令中指定队友名称，以便后续引用。

### 权限与 Token

- **权限**：队友继承 Lead 的权限设置，生成后可单独修改
- **Token**：每个队友独立消耗 Token，成本随活跃队友数量线性增长

### Hooks 质量门禁

| Hook | 触发时机 | 用途 |
|------|---------|------|
| `TeammateIdle` | 队友即将空闲时 | 退出码 2 → 发送反馈让队友继续工作 |
| `TaskCreated` | 任务被创建时 | 退出码 2 → 阻止创建并反馈 |
| `TaskCompleted` | 任务被标记完成时 | 退出码 2 → 阻止完成并反馈 |

---

## 实战案例

### 案例 1：并行代码评审

单个评审者往往一次只关注一类问题。拆分到不同维度可以同时获得全面关注：

```text
Create an agent team to review PR #142. Spawn three reviewers:
- One focused on security implications
- One checking performance impact
- One validating test coverage
Have them each review and report findings.
```

每个评审者从相同 PR 出发，但应用不同的审查视角，Lead 最后综合所有发现。

### 案例 2：竞争假设调试

当根因不明时，单个 Agent 容易找到一个看似合理的解释就停下来。多个队友互相挑战可以避免**锚定效应**：

```text
Users report the app exits after one message instead of staying connected.
Spawn 5 agent teammates to investigate different hypotheses. Have them talk to
each other to try to disprove each other's theories, like a scientific
debate. Update the findings doc with whatever consensus emerges.
```

关键机制是**辩论结构**——多个独立调查者主动尝试推翻彼此的理论，存活下来的理论更可能是真正的根因。

---

## 最佳实践

### 1. 给队友足够的上下文

队友**不继承 Lead 的对话历史**，spawn 时务必在 prompt 中提供具体细节：

```text
Spawn a security reviewer teammate with the prompt: "Review the authentication
module at src/auth/ for security vulnerabilities. Focus on token handling,
session management, and input validation. The app uses JWT tokens stored in
httpOnly cookies. Report any issues with severity ratings."
```

### 2. 选择合适的团队规模

| 建议 | 说明 |
|------|------|
| **起步 3-5 人** | 平衡并行度和协调开销 |
| **每人 5-6 个任务** | 保持高效又不过度切换 |
| **15 个任务 → 3 个队友** | 合理起点 |
| **3 个聚焦 > 5 个分散** | 质量优先于数量 |

### 3. 合理划分任务粒度

| 粒度 | 问题 |
|------|------|
| 太小 | 协调开销超过收益 |
| 太大 | 队友工作太久没有检查点，浪费风险高 |
| 刚好 | 自包含的单元，产出明确（一个函数、一个测试文件、一份评审） |

### 4. 避免文件冲突

两个队友编辑同一个文件会导致覆写。拆分工作时确保每个队友**负责不同的文件集**。

### 5. 让 Lead 等待

有时 Lead 会自己开始做任务而不等队友。遇到这种情况直接说：

```text
Wait for your teammates to complete their tasks before proceeding
```

### 6. 从研究评审类任务入手

新手先从**不需要写代码**的任务开始（评审 PR、调研库、调查 Bug），感受并行探索的价值后再尝试并行开发。

### 7. 持续监控和引导

定期检查队友进展，重定向不工作的方法，及时综合发现。无人看管太久会增加浪费风险。

---

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| **队友不出现** | In-process 模式下按 `Shift+Down` 切换；检查任务是否足够复杂；检查 tmux 是否安装（`which tmux`） |
| **权限提示太多** | 在权限设置中预先批准常用操作 |
| **队友遇错停止** | 用 `Shift+Down` 查看输出，给额外指令或生成替代队友 |
| **Lead 提前结束** | 告诉 Lead 继续等待队友完成 |
| **孤儿 tmux 会话** | `tmux ls` 查看会话，`tmux kill-session -t <name>` 清理 |

---

## 已知限制

| 限制 | 说明 |
|------|------|
| 不支持恢复队友 | `/resume` 和 `/rewind` 不会恢复 in-process 队友，需重新生成 |
| 任务状态滞后 | 队友有时忘记标记完成，需手动更新或让 Lead 催促 |
| 关闭较慢 | 队友会完成当前请求后才关闭 |
| 一个会话一个团队 | 清理当前团队后才能创建新团队 |
| 不支持嵌套团队 | 队友不能创建自己的团队 |
| Lead 不可转让 | 创建团队的会话永久为 Lead |
| 权限继承 | 所有队友继承 Lead 权限，不能单独预设 |
| 分屏终端限制 | VS Code、Windows Terminal、Ghostty 不支持分屏 |

> [!info] CLAUDE.md 正常工作
> 队友会从工作目录读取 `CLAUDE.md` 文件，可以用它向所有队友提供项目级指导。

---

## 相关功能

| 方案 | 适用场景 |
|------|---------|
| [[AI/ClaudeCode/Subagents]] | 轻量级委派，不需要队友间通信 |
| Agent Teams（本文） | 复杂协作，需要讨论和自主协调 |
| Git Worktrees 并行会话 | 手动管理多个 Claude Code 会话，无自动协调 |
