---
title: Claude Code 多智能体协作：Subagents 与 Agent Teams
tags:
  - AI
  - claude-code
  - subagent
  - agent-teams
  - multi-agent
  - git-worktree
  - workflow
date: 2026-04-17
source:
  - "https://code.claude.com/docs/en/agent-teams"
  - "https://mp.weixin.qq.com/s/g8wc2ULicc0djeOkRN5WvA"
aliases:
  - 子智能体
  - Agent Teams
---

# Claude Code 多智能体协作：Subagents 与 Agent Teams

Claude Code 提供两种多智能体并行工作机制：**Subagents**（子智能体）和 **Agent Teams**（智能体团队）。两者都能让多个 Claude 实例并行执行任务，但在通信模型、协调方式和适用场景上有本质区别。

---

## 核心对比：怎么选？

| 对比项 | Subagents | Agent Teams |
|--------|-----------|-------------|
| **上下文** | 有自己的上下文窗口，结果返回给调用者 | 有自己的上下文窗口，完全独立 |
| **通信** | ==只能向主 Agent 汇报==结果 | 队友之间可以==直接互发消息== |
| **协调** | 主 Agent 管理所有工作 | 共享任务列表，队友自主认领 |
| **适用场景** | 聚焦型任务，只关心结果 | 复杂工作，需要讨论和协作 |
| **Token 成本** | 较低：结果摘要返回主上下文 | 较高：每个队友都是独立的 Claude 实例 |
| **状态** | 稳定功能 | 实验性功能（需 v2.1.32+） |

> [!tip] 一句话选择原则
> - 并行干活、各自汇报 → **Subagents**
> - 并行干活、互相讨论 → **Agent Teams**

---

# 第一部分：Subagents（子智能体）

## 什么是 Subagent

每个 SubAgent 是完全独立的 Claude 副本。你通过 Markdown 文件（`.md`）定义它的==系统提示 + 工具配置==组合，Claude Code 在需要时自动调用或由你手动触发。

**产品逻辑**：SubAgent 处理结果→返回给 Claude Code→Claude Code 汇总后输出给你。注意 SubAgent 的输出对象不是你，而是 Claude Code。

## 组成（5 个核心字段）

每个 SubAgent 是一个 `.md` 文件，由 frontmatter 定义：

| 字段 | 作用 |
|------|------|
| **name** | Agent 名字（标识符） |
| **description** | 能力描述——Claude 在什么情况下调用这个 Agent |
| **tools** | 可调用的工具列表 |
| **model** | 使用的模型（如 `sonnet`、`opus`、`haiku`） |
| **system** | 系统提示词——角色定位、规则限制、输出风格、工作流程 |

## 存储位置与优先级

| 类型 | 路径 | 可用范围 | 优先级 |
|------|------|---------|--------|
| 项目级 | `.claude/agents/` | 当前项目 | **高** |
| 全局级 | `~/.claude/agents/` | 所有项目 | 低 |

> [!note]
> 名称冲突时，项目级 SubAgent 会覆盖全局级。

## 新建 SubAgent

1. 在项目的 `.claude/agents/` 目录下创建 `.md` 文件
2. Claude Code 自动检测并加载
3. 在对话中自然调用，或让 Claude 自行判断何时使用

> [!info] 更多现成的 SubAgent
> GitHub 上有社区整理的 100+ SubAgent：[awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)，可按场景挑选直接使用。

## 典型场景

你："这个支付模块需要全面审查"

Claude Code 并行创建 5 个 Task：

1. 架构分析 SubAgent → 模块设计和接口审查
2. 安全审计 SubAgent → SQL 注入、XSS、CSRF 检查
3. 性能分析 SubAgent → 慢查询和瓶颈定位
4. 代码质量 SubAgent → 测试覆盖和规范检查
5. 数据库 SubAgent → 索引和查询优化建议

- 30 分钟返回 5 份报告（串行需 2.5 小时）
- 成本：5 倍 Token，节省 80% 时间
- 本质是==时间换成本==的策略：Token 线性累加，但时间节省 50-80%

## 适用场景评级

| 评级 | 场景 | 原因 |
|:----:|------|------|
| ★★★★★ | 多角度代码审查、项目规划、文档生成 | 任务完全独立 |
| ★★★★☆ | 文件批处理、API 集成测试 | 任务基本独立 |
| ★★☆☆☆ | 迭代式功能调试 | SubAgent 无状态特性不利于迭代 |
| ★☆☆☆☆ | 任务间有依赖、敏感数据、单一复杂任务 | 不需要或不适合并行 |

---

# 第二部分：Agent Teams（智能体团队）

## 什么是 Agent Teams

Agent Teams 让多个 Claude Code 实例组成团队协同工作：

- 一个 **Team Lead**（主会话）负责协调、分配任务、综合结果
- 多个 **Teammates**（队友）各自独立工作，拥有各自的上下文窗口
- 队友之间可以**直接通信**，不需要经过 Lead 中转
- 你也可以**直接与任意队友对话**，给它额外指令

> [!warning] 实验性功能
> Agent Teams 当前为实验性功能，默认关闭。需要 Claude Code **v2.1.32+**。

## 启用

在 `settings.json` 中添加：

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

或设置环境变量：`export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`

## 最佳使用场景

| 场景 | 为什么适合 Teams |
|------|-----------------|
| **研究与评审** | 多个队友同时调查不同方面，共享和质疑彼此发现 |
| **新模块/新功能开发** | 每个队友负责一个独立模块，互不干扰 |
| **竞争假设调试** | 多个队友并行测试不同假设，更快收敛答案 |
| **跨层协调** | 前端、后端、测试分别由不同队友负责 |

> [!important] 不适合的场景
> 顺序依赖任务、编辑同一文件、依赖关系复杂的工作——用单会话或 Subagents 更高效。

## 架构

| 组件 | 作用 |
|------|------|
| **Team Lead** | 主会话，创建团队、分配任务、协调工作 |
| **Teammates** | 独立的 Claude Code 实例，各自处理分配的任务 |
| **Task List** | 共享任务列表，队友认领和完成任务（支持依赖关系、文件锁防竞态） |
| **Mailbox** | 消息系统，队友间直接通信 |

存储位置：
- 团队配置：`~/.claude/teams/{team-name}/config.json`（自动管理，**不要手动编辑**）
- 任务列表：`~/.claude/tasks/{team-name}/`

## 快速开始

用自然语言告诉 Claude 创建团队即可：

```text
I'm designing a CLI tool that helps developers track TODO comments across
their codebase. Create an agent team to explore this from different angles: one
teammate on UX, one on technical architecture, one playing devil's advocate.
```

Claude 会自动创建团队→生成队友→并行探索→综合发现→清理团队。

## 显示模式

| 模式 | 说明 | 操作方式 |
|------|------|---------|
| **In-process**（默认） | 所有队友在主终端内运行 | `Shift+Down` 切换队友，直接打字发消息 |
| **Split panes** | 每个队友一个独立窗格 | 点击窗格即可交互，同时看到所有输出 |

默认 `"auto"`：已在 tmux 会话中→分屏，否则→in-process。

```json
// ~/.claude.json 手动设置
{ "teammateMode": "in-process" }
```

```bash
# 单次会话指定
claude --teammate-mode in-process
```

> [!note] Split panes 依赖
> 需要 [tmux](https://github.com/tmux/tmux/wiki) 或 iTerm2 + [`it2` CLI](https://github.com/mkusaka/it2)。
> VS Code 集成终端、Windows Terminal、Ghostty **不支持**。

## 团队控制

### 指定队友和模型

```text
Create a team with 4 teammates to refactor these modules in parallel.
Use Sonnet for each teammate.
```

### 要求计划审批

```text
Spawn an architect teammate to refactor the authentication module.
Require plan approval before they make any changes.
```

流程：队友在只读 plan 模式工作→提交计划→Lead 批准或驳回→批准后开始实施。

> [!tip] 影响审批标准
> 在 prompt 中设定条件：`"only approve plans that include test coverage"`

### 直接与队友对话

- **In-process**：`Shift+Down` 切换 → 打字发消息 → `Enter` 查看会话 → `Escape` 中断 → `Ctrl+T` 任务列表
- **Split-pane**：点击窗格直接交互

### 任务分配

| 方式 | 说明 |
|------|------|
| **Lead 指派** | 告诉 Lead 把任务分给特定队友 |
| **自主认领** | 队友完成后自动认领下一个未分配、未阻塞的任务 |

任务有三种状态（Pending → In Progress → Completed），支持依赖关系和文件锁。

### 关闭与清理

```text
Ask the researcher teammate to shut down   # 关闭单个队友
Clean up the team                           # 清理整个团队
```

> [!warning] 清理注意
> 先关闭所有队友再清理；必须由 Lead 执行清理。

## 上下文与通信

队友加载项目上下文（`CLAUDE.md`、MCP、Skills），但**不继承 Lead 对话历史**。

| 通信方式 | 说明 |
|---------|------|
| **message** | 向特定队友发消息 |
| **broadcast** | 向所有队友广播（慎用，成本线性增长） |
| **自动通知** | 队友完成/停止时自动通知 Lead |
| **依赖解锁** | 任务完成后阻塞的任务自动解锁 |

### 复用 Subagent 定义

可以用已有的 Subagent 类型创建队友：

```text
Spawn a teammate using the security-reviewer agent type to audit the auth module.
```

队友继承该定义的 `tools` 和 `model`，但 `skills`/`mcpServers` 字段不应用。团队协调工具（`SendMessage`、任务管理）始终可用。

### 权限

队友继承 Lead 权限设置，生成后可单独修改，但不能在生成时预设。

### Hooks 质量门禁

| Hook | 触发时机 | 退出码 2 的效果 |
|------|---------|---------------|
| `TeammateIdle` | 队友即将空闲 | 发送反馈让队友继续工作 |
| `TaskCreated` | 任务被创建 | 阻止创建并反馈 |
| `TaskCompleted` | 任务被标记完成 | 阻止完成并反馈 |

## 已知限制

| 限制 | 说明 |
|------|------|
| 不支持恢复队友 | `/resume`、`/rewind` 不恢复 in-process 队友，需重新生成 |
| 任务状态滞后 | 队友有时忘记标记完成，需手动更新 |
| 关闭较慢 | 队友会完成当前请求后才关闭 |
| 一个会话一个团队 | 清理当前团队后才能创建新团队 |
| 不支持嵌套 | 队友不能再创建自己的团队 |
| Lead 不可转让 | 创建团队的会话永久为 Lead |
| 权限继承 | 所有队友继承 Lead 权限 |
| 分屏限制 | VS Code、Windows Terminal、Ghostty 不支持 |

> [!info] `CLAUDE.md` 正常工作
> 队友从工作目录读取 `CLAUDE.md`，可用它向所有队友提供项目级指导。

---

# 实战案例

## Subagents：并行代码审查

```text
"这个支付模块需要全面审查"
```

→ 并行 5 个 SubAgent（架构/安全/性能/质量/数据库），30 分钟返回 5 份报告。

## Agent Teams：竞争假设调试

```text
Users report the app exits after one message instead of staying connected.
Spawn 5 agent teammates to investigate different hypotheses. Have them talk to
each other to try to disprove each other's theories, like a scientific
debate. Update the findings doc with whatever consensus emerges.
```

关键机制是**辩论结构**——多个独立调查者主动推翻彼此理论，避免锚定效应。这是 Agent Teams 独有的高价值模式，SubAgents 无法实现（因为 SubAgent 之间不通信）。

## Agent Teams：分角度 PR 评审

```text
Create an agent team to review PR #142. Spawn three reviewers:
- One focused on security implications
- One checking performance impact
- One validating test coverage
Have them each review and report findings.
```

每个评审者应用不同视角，Lead 综合发现。

---

# 最佳实践总览

## 通用原则

1. **从研究评审类任务入手**——先感受并行价值，再尝试并行开发
2. **避免文件冲突**——确保每个并行工作者负责不同的文件集
3. **持续监控和引导**——无人看管太久会增加浪费风险

## Subagents 专属

4. **明确任务边界和产出**——SubAgent 无状态，一次性交付
5. **只用于独立任务**——有依赖关系的任务不要拆分到 SubAgent

## Agent Teams 专属

6. **给队友足够上下文**——队友不继承 Lead 对话历史，spawn 时提供具体细节
7. **起步 3-5 人**——平衡并行度和协调开销，3 个聚焦优于 5 个分散
8. **每人 5-6 个任务**——保持高效又不过度切换
9. **合理划分任务粒度**——太小协调开销大，太大浪费风险高
10. **让 Lead 等待队友**——如果 Lead 自己开始做任务，明确告诉它等待

## 故障排查（Agent Teams）

| 问题 | 解决方案 |
|------|---------|
| 队友不出现 | `Shift+Down` 切换；检查任务复杂度；检查 tmux（`which tmux`） |
| 权限提示太多 | 预先批准常用操作 |
| 队友遇错停止 | 查看输出，给额外指令或生成替代队友 |
| Lead 提前结束 | 告诉 Lead 继续等待 |
| 孤儿 tmux 会话 | `tmux ls` → `tmux kill-session -t <name>` |

---

# 第三部分：Git Worktree 并行开发

> 来源：[Claude Code 并行开发完全指南](https://mp.weixin.qq.com/s/g8wc2ULicc0djeOkRN5WvA)

当需要在同一个项目里**同时处理多个不兼容的改动**时，Git Worktree 比 Agent Teams 更底层、更稳定——它提供的是**分支级别的文件系统硬隔离**。

## 适用场景

- 同时做 Feature A 和 Refactor B，两者改动重叠，不能在同一分支串行
- 保持当前工作目录干净的同时并行处理紧急 Bugfix
- 多人协作避免合并冲突

## 基础命令

```bash
# 查看当前所有 Worktree
git worktree list

# 创建新 Worktree（同时创建新分支）
git worktree add ../feature-auth -b feature/auth
git worktree add ../bugfix-urgent -b bugfix/urgent

# 在新目录里启动 Claude Code
cd ../feature-auth
claude

# 工作完成后合并回主分支
git checkout main
git merge feature/auth
git worktree remove ../feature-auth
git branch -d feature/auth
```

## 实战：结合 Claude Code 并行开发

```bash
# 场景：同时处理新功能 + 重构

# 1. 主分支继续开发新功能
cd ~/projects/myapp
claude

# 2. 创建 Worktree 做重构（隔离）
git worktree add ../refactor-db -b refactor/db
cd ../refactor-db
claude
# 新会话里专门做数据库重构，不影响主分支

# 3. 两边并行做完，合并
git checkout main
git merge refactor/db
git worktree remove ../refactor-db
```

## Git Worktree vs Agent Teams 怎么选

| 维度 | Git Worktree | Agent Teams |
|------|-------------|-------------|
| 隔离级别 | 分支级别（文件系统） | 上下文级别（内存） |
| 适用场景 | 大范围重构、并行分支开发 | 快速探索、多角色协作 |
| 多人协作 | 支持 | 主要单人使用 |
| 上手难度 | ★★ | ★★★ |

- **用 Git Worktree**：改动会相互冲突、需要硬隔离、多人协作场景
- **用 Agent Teams**：需要快速并行探索、多个角色同时讨论方案

---

# 第四部分：工作流编排

前面三种方案解决的是"怎么并行"，工作流编排解决的是"多个工作单元怎么有序配合"。

## Plan 模式：动手前的任务分解

Claude Code 内置 `/plan` 命令，是一个**任务规划工具**——把"想清楚做什么"和"动手做"分开。

```text
/plan
# Claude 分析项目结构和任务需求
# 输出分步骤计划，等待确认后才执行
```

> [!tip] 什么时候用 Plan
> **多模块重构、新技术引入、架构调整**时用 Plan；常规 CRUD、小需求直接做。

## 在工作流中嵌入 Plan 模式

```text
architect（Agent Team）：用 /plan 分析 src/modules 的依赖关系，给出重构优先级。

architect 的 plan 确认后，分配给 frontend-dev 和 backend-dev 各自执行。

backend-dev：
/plan
根据 architect 的分析结果，设计 database schema 迁移方案。
```

每个 Agent 动手前都有一次"想清楚"的环节，减少返工。

## Multi-Agent 协作工作流模板

```
阶段一：任务分解（Plan 模式）
├─ 主会话：定义项目范围和目标
├─ /plan：拆解为具体模块
└─ 输出：完整的任务分解清单

阶段二：角色分配（Agent Teams）
├─ architect：架构设计和方案评审
├─ frontend-dev：前端实现
└─ backend-dev：后端实现

阶段三：并行执行
├─ 各 Agent 独立工作
├─ 通过共享上下文通信
└─ architect 协调冲突

阶段四：整合与 Review（Subagents）
├─ code-reviewer：全面代码审查
├─ test-writer：生成测试用例
└─ architect：最终架构评审

阶段五：合并（Git Worktree）
├─ 合并各分支到 main
└─ 运行集成测试
```

## 把工作流固化到 CLAUDE.md

将团队配置和工作流模板写入项目的 `CLAUDE.md`，Claude Code 启动时自动加载，新成员 clone 即可复用：

```markdown
# 项目 AI 团队配置

## 默认团队
| 角色 | 职责 |
|------|------|
| architect | 架构设计和技术方案评审 |
| frontend-dev | 前端开发，React/TypeScript/Tailwind CSS |
| backend-dev | 后端开发，Node.js/Python + PostgreSQL |
| code-reviewer | 代码审查，安全和质量问题 |

## 工作流规范
1. 涉及多模块时，先用 /plan 拆解，确认后再执行
2. architect 评审通过的技术方案，才能分配给前端/后端
3. 所有代码合并前必须经过 code-reviewer 审查
```

## Routines：定时自动执行

Routines 把"一次 prompt + 代码仓库 + 触发条件"打包成配置，在 Anthropic 云端运行，不需要电脑保持开机。

**三种触发方式**：

| 触发方式 | 说明 | 典型场景 |
|---------|------|---------|
| **定时触发** | cron 表达式 | 每天早上自动跑代码审查 |
| **API 触发** | REST 接口 | 外部系统触发 CI/CD 流水线 |
| **GitHub 事件** | PR opened、push 等 | PR 创建时自动 code review |

**配置示例**：

```bash
/claude routine create \
  --name "morning-review" \
  --prompt "审查昨晚到现在的所有 commits，重点关注：安全漏洞、性能问题、测试覆盖率" \
  --trigger "0 8 * * *" \
  --repo ./my-project
```

**与 Agent Teams 配合——无人值守流水线**：

```
Routines（定时 08:00）
  └─→ 触发 Agent Teams
        ├─ architect：代码审查
        ├─ backend-dev：Bug 修复
        └─ frontend-dev：依赖检查
  └─→ 审查结果自动发 PR comment 或邮件通知
```

> [!warning] 当前限制
> - Routines 处于**研究预览阶段**
> - 仅支持 Claude 官方模型，不支持第三方 API 路由
> - 部分触发器需要配置 webhook 回调地址

## 常见坑

| 坑 | 说明 |
|----|------|
| Subagent 记忆不共享 | 跨 Subagent 传递信息需要在主会话中转 |
| Agent Teams 上下文竞争 | 多 Agent 共享上下文窗口，每个 Agent 指令里限制输出长度 |
| Git Worktree 合并冲突 | 合并前确保主分支没有未提交的改动 |
| Plan 模式太慢 | 只在多模块重构/架构调整时使用，小需求直接做 |

---

# 全局选型决策表

| 场景 | 推荐方案 |
|------|---------|
| 同项目多工种分工（review + test） | Subagents |
| 真正多 Agent 同时工作 | Agent Teams |
| 长时重构、多分支并行 | Git Worktree |
| 复杂任务分解 + 协调 | 工作流编排（Plan + Teams） |
| 定时自动跑任务（无人值守） | Routines + Agent Teams |
| 快速小需求、单人单线程 | 单个 Claude 实例足够 |

> 这四条路不矛盾，一个项目里往往组合着用：Subagents 定义角色，Agent Teams 处理并行部分，Git Worktree 做分支硬隔离，工作流编排把全局串起来。

---

# 开源 Agents 推荐

## wshobson/agents

> [!info] 仓库
> [wshobson/agents](https://github.com/wshobson/agents) — Claude Code 的大型 Plugin Marketplace，包含 **72 个插件、112 个专业 Agent、146 个 Skills、16 个多智能体编排器**。

项目定位

这是目前最大的 Claude Code Agent 开源集合，目标是为软件开发提供**细粒度自动化和多智能体编排**。核心设计理念：

- **按需加载**：安装 marketplace 后不会加载任何 agent，安装具体插件才加载对应能力
- **23 个领域覆盖**：从架构设计到 SEO 优化，覆盖软件开发全生命周期
- **四级模型策略**：根据任务复杂度分配 Opus/Sonnet/Haiku，兼顾质量和成本
- 可以支持agent teams

安装：

```sh
# 第一步：添加 marketplace（使所有 72 个插件可用，不加载任何 agent）
/plugin marketplace add wshobson/agents

# 第二步：安装具体插件（按需）
/plugin install agent-teams@claude-code-workflows
/plugin install backend-development@claude-code-workflows
```

