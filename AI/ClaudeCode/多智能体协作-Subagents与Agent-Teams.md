---
title: Claude Code 多智能体协作：Subagents 与 Agent Teams
tags:
  - AI
  - claude-code
  - subagent
  - agent-teams
  - multi-agent
date: 2026-04-17
source: "https://code.claude.com/docs/en/agent-teams"
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
# 开源 Agents 推荐

## wshobson/agents

> [!info] 仓库
> [wshobson/agents](https://github.com/wshobson/agents) — Claude Code 的大型 Plugin Marketplace，包含 **72 个插件、112 个专业 Agent、146 个 Skills、16 个多智能体编排器**。

### 项目定位

这是目前最大的 Claude Code Agent 开源集合，目标是为软件开发提供**细粒度自动化和多智能体编排**。核心设计理念：

- **按需加载**：安装 marketplace 后不会加载任何 agent，安装具体插件才加载对应能力
- **23 个领域覆盖**：从架构设计到 SEO 优化，覆盖软件开发全生命周期
- **四级模型策略**：根据任务复杂度分配 Opus/Sonnet/Haiku，兼顾质量和成本

### 安装

```sh
# 第一步：添加 marketplace（使所有 72 个插件可用，不加载任何 agent）
/plugin marketplace add wshobson/agents

# 第二步：安装具体插件（按需）
/plugin install agent-teams@claude-code-workflows
/plugin install backend-development@claude-code-workflows
```

### 全部 Agent 分类

#### 架构与系统设计

| Agent | 模型 | 描述 |
|-------|------|------|
| `backend-architect` | opus | RESTful API 设计、微服务边界、数据库 schema |
| `frontend-developer` | sonnet | React 组件、响应式布局、客户端状态管理 |
| `graphql-architect` | opus | GraphQL schema、resolver、联邦架构 |
| `architect-reviewer` | opus | 架构一致性分析和模式验证 |
| `cloud-architect` | opus | AWS/Azure/GCP 基础设施设计和成本优化 |
| `hybrid-cloud-architect` | opus | 多云策略（云 + 本地混合） |
| `kubernetes-architect` | opus | 云原生基础设施、Kubernetes + GitOps |
| `service-mesh-expert` | opus | Istio/Linkerd 服务网格、mTLS、流量管理 |
| `event-sourcing-architect` | opus | 事件溯源、CQRS 模式、Saga 编排 |
| `monorepo-architect` | opus | Nx/Turborepo/Bazel 单体仓库工具链优化 |

#### UI/UX 与移动端

| Agent | 模型 | 描述 |
|-------|------|------|
| `ui-designer` | opus | 移动端和 Web UI/UX 设计 |
| `accessibility-expert` | opus | WCAG 合规、无障碍审计、包容性设计 |
| `design-system-architect` | opus | Design Token、组件库、主题系统 |
| `ui-ux-designer` | sonnet | 界面设计、线框图、设计系统 |
| `ui-visual-validator` | sonnet | 视觉回归测试和 UI 验证 |
| `mobile-developer` | sonnet | React Native / Flutter 开发 |
| `ios-developer` | sonnet | Swift/SwiftUI 原生 iOS 开发 |
| `flutter-expert` | sonnet | Flutter 高级开发与状态管理 |

#### 编程语言

**系统级：**

| Agent | 模型 | 描述 |
|-------|------|------|
| `c-pro` | sonnet | 系统编程、内存管理、OS 接口 |
| `cpp-pro` | sonnet | 现代 C++、RAII、智能指针、STL |
| `rust-pro` | sonnet | 内存安全系统编程、所有权模式 |
| `golang-pro` | sonnet | 并发编程、goroutine、channel |

**Web 与应用：**

| Agent | 模型 | 描述 |
|-------|------|------|
| `javascript-pro` | sonnet | 现代 JS（ES6+）、异步模式、Node.js |
| `typescript-pro` | sonnet | 高级 TypeScript、类型系统、泛型 |
| `python-pro` | sonnet | Python 高级特性与优化 |
| `temporal-python-pro` | sonnet | Temporal 工作流编排（Python SDK） |
| `ruby-pro` | sonnet | Ruby 元编程、Rails 模式 |
| `php-pro` | sonnet | 现代 PHP 框架与性能优化 |

**企业级 / JVM：**

| Agent | 模型 | 描述 |
|-------|------|------|
| `java-pro` | sonnet | 现代 Java、Stream、并发、JVM 优化 |
| `scala-pro` | sonnet | 企业级 Scala、函数式编程 |
| `csharp-pro` | sonnet | C# + .NET 框架与模式 |

**专业平台：**

| Agent | 模型 | 描述 |
|-------|------|------|
| `elixir-pro` | sonnet | Elixir + OTP + Phoenix |
| `django-pro` | sonnet | Django ORM + 异步视图 |
| `fastapi-pro` | sonnet | FastAPI 异步模式 + Pydantic |
| `haskell-pro` | sonnet | 强类型函数式编程 |
| `unity-developer` | sonnet | Unity 游戏开发与优化 |
| `minecraft-bukkit-pro` | sonnet | Minecraft 服务端插件开发 |
| `sql-pro` | sonnet | 复杂 SQL 查询与数据库优化 |

#### 基础设施与运维

| Agent | 模型 | 描述 |
|-------|------|------|
| `devops-troubleshooter` | sonnet | 生产环境调试、日志分析、部署排错 |
| `deployment-engineer` | sonnet | CI/CD 流水线、容器化、云部署 |
| `terraform-specialist` | sonnet | Terraform 模块与状态管理 |
| `dx-optimizer` | sonnet | 开发者体验优化与工具链改进 |
| `database-optimizer` | sonnet | 查询优化、索引设计、迁移策略 |
| `database-admin` | sonnet | 数据库运维、备份、复制、监控 |
| `database-architect` | opus | 数据库从零设计、选型、schema 建模 |
| `incident-responder` | opus | 生产事故管理与恢复 |
| `network-engineer` | sonnet | 网络调试、负载均衡、流量分析 |
| `conductor-validator` | opus | Conductor 项目产物完整性验证 |

#### 安全与质量保障

| Agent | 模型 | 描述 |
|-------|------|------|
| `code-reviewer` | opus | 安全聚焦的代码审查 |
| `security-auditor` | opus | 漏洞评估与 OWASP 合规 |
| `backend-security-coder` | opus | 后端安全编码、API 安全 |
| `frontend-security-coder` | opus | XSS 防护、CSP、客户端安全 |
| `mobile-security-coder` | opus | 移动安全模式、WebView 安全 |
| `threat-modeling-expert` | opus | STRIDE 威胁建模、攻击树 |
| `test-automator` | sonnet | 全面测试套件（单元/集成/E2E） |
| `tdd-orchestrator` | sonnet | TDD 方法论指导 |
| `debugger` | sonnet | 错误解决与测试失败分析 |
| `error-detective` | sonnet | 日志分析与错误模式识别 |
| `performance-engineer` | opus | 应用性能分析与优化 |
| `observability-engineer` | opus | 生产监控、分布式追踪、SLI/SLO |
| `search-specialist` | haiku | 高级 Web 搜索与信息综合 |

#### 数据与 AI

| Agent | 模型 | 描述 |
|-------|------|------|
| `data-scientist` | opus | 数据分析、SQL 查询、BigQuery |
| `data-engineer` | sonnet | ETL 流水线、数据仓库、流式架构 |
| `ai-engineer` | opus | LLM 应用、RAG 系统、Prompt 流水线 |
| `ml-engineer` | opus | ML 流水线、模型服务、特征工程 |
| `mlops-engineer` | opus | ML 基础设施、实验追踪、模型注册 |
| `prompt-engineer` | opus | LLM Prompt 优化与工程 |
| `vector-database-engineer` | opus | 向量数据库、Embedding、语义检索 |

#### 文档与技术写作

| Agent | 模型 | 描述 |
|-------|------|------|
| `docs-architect` | opus | 综合技术文档生成 |
| `api-documenter` | sonnet | OpenAPI/Swagger 规范与开发者文档 |
| `reference-builder` | haiku | 技术参考与 API 文档 |
| `tutorial-engineer` | sonnet | 分步教程与教学内容 |
| `mermaid-expert` | sonnet | 图表创建（流程图、时序图、ERD） |
| `c4-code` | haiku | C4 代码级文档 |
| `c4-component` | sonnet | C4 组件级架构文档 |
| `c4-container` | sonnet | C4 容器级架构文档 |
| `c4-context` | sonnet | C4 上下文级系统文档 |

#### 商业与运营

| Agent | 模型 | 描述 |
|-------|------|------|
| `business-analyst` | sonnet | 指标分析、报告、KPI 追踪 |
| `quant-analyst` | opus | 金融建模、交易策略、市场分析 |
| `risk-manager` | sonnet | 投资组合风险监控与管理 |
| `content-marketer` | sonnet | 博客、社交媒体、邮件营销 |
| `sales-automator` | haiku | 冷邮件、跟进、提案生成 |
| `customer-support` | sonnet | 工单、FAQ、客户沟通 |
| `hr-pro` | opus | HR 运营、政策、员工关系 |
| `legal-advisor` | opus | 隐私政策、服务条款、法律文档 |

#### SEO 优化（10 个）

| Agent | 模型 | 描述 |
|-------|------|------|
| `seo-content-auditor` | sonnet | 内容质量分析、E-E-A-T 信号评估 |
| `seo-meta-optimizer` | sonnet | 元标签优化 |
| `seo-keyword-strategist` | sonnet | 关键词策略 |
| `seo-structure-architect` | sonnet | SEO 结构优化 |
| `seo-snippet-hunter` | sonnet | 精选摘要优化 |
| `seo-content-refresher` | sonnet | 内容刷新与更新 |
| `seo-cannibalization-detector` | sonnet | 关键词蚕食检测 |
| `seo-authority-builder` | sonnet | 权威性建设 |
| `seo-content-writer` | sonnet | SEO 内容创作 |
| `seo-content-planner` | sonnet | SEO 内容规划 |

#### 专业领域

| Agent | 模型 | 描述 |
|-------|------|------|
| `gallery-researcher` | sonnet | 视觉素材搜索（MeiGen gallery） |
| `image-generator` | sonnet | AI 图片生成（MeiGen MCP） |
| `arm-cortex-expert` | sonnet | ARM Cortex-M 固件与外设驱动开发 |
| `blockchain-developer` | sonnet | Web3 应用、智能合约、DeFi 协议 |
| `payment-integration` | sonnet | 支付集成（Stripe/PayPal） |
| `legacy-modernizer` | sonnet | 遗留代码重构与现代化 |
| `context-manager` | haiku | 多智能体上下文管理 |

#### 多智能体团队

| Agent | 模型 | 描述 |
|-------|------|------|
| `team-lead` | opus | 团队编排、任务分解、生命周期管理、结果综合 |
| `team-reviewer` | opus | 多维度代码审查 |
| `team-debugger` | sonnet | 假设驱动的调查取证式调试 |
| `team-implementer` | sonnet | 在严格文件所有权边界内实现功能 |

### 模型分配策略

| 模型 | 定位 | 典型任务 |
|------|------|---------|
| **Opus** | 关键决策层 | 架构设计、安全审计、生产代码审查、事故响应 |
| **Sonnet** | 主力执行层 | 编码实现、测试编写、文档生成、DevOps 操作 |
| **Haiku** | 快速操作层 | 代码生成（有明确 spec）、参考文档构建、搜索 |
