---
title: "Claude Code 并行开发完全指南：Subagents + Agent Teams + Git Worktree + 工作流编排实战"
source: "https://mp.weixin.qq.com/s/g8wc2ULicc0djeOkRN5WvA"
author:
  - "[[lkb83]]"
published:
created: 2026-04-22
description:
tags:
  - "clippings"
---
lkb83 *2026年4月18日 20:01*

## Claude Code 用久了会遇到一个问题：项目大了，单个实例处理不过来，上下文越来越长，响应越来越慢，多个模块只能排队等一个人做完。

有四条路可以解决这个问题： **Subagents** 、 **Agent Teams** 、 **Git Worktree** ，以及 **工作流编排** 。每条路都有它最合适的地方，用对了效率翻倍，用错了越绕越远。

一、痛点：你的 Claude Code 什么时候开始"喘"

单个 Claude 实例处理复杂任务时，有三个典型的崩溃节点：

**节点一：上下文爆了。** 项目超过几万行，CLAUDE.md + 对话历史 + 代码文件把上下文窗口填满，Claude 开始"失忆"——前面说过的事后来说不知道，同一个 Bug 修三遍还出现。原因是模型对超长上下文的检索质量会下降，注意力被稀释。

**节点二：任务只能串行。** 想同时让 AI 做两件事：一边写新功能，一边给老模块加测试。做不到。必须等一个做完，再开另一个。中间还有上下文切换的损耗——新会话没有旧会话的上下文，等于从头认识项目。

**节点三：多模块无法同时推进。** 假设你有一个前端 + 后端 + 数据库三层重构任务，单个 Claude 实例每次只能聚焦一个方向。切到前端，后端的决策就断了；切到数据库，前端刚建好的模型又得重新对齐。

这三条路的共同解法是： **让多个工作单元并行跑，彼此隔离但又可以通信** 。Claude Code 给了你四套机制。

二、三种并行方案 + 工作流编排：一张表说清楚

| 方案 | 核心作用 | 适用场景 | 上手难度 |
| --- | --- | --- | --- |
| **Subagents** | 同项目多角色分工 | 一个人管多个工种（写代码+review+测试） | ★ |
| **Agent Teams** | 多 Agent 同时并行 | 需要真正"多头脑"同时工作 | ★★★ |
| **Git Worktree** | 隔离分支并行 | 长时重构、多人协作场景 | ★★ |
| **工作流编排** | 串联 + 控制各单元 | 全局协调、任务调度 | ★★ |

三、Subagents：用 Markdown 定义你的"团队成员"

#### 3.1 什么是 Subagent

Subagent 就是一组 Markdown 文件，放在特定目录里，定义了一个"角色"的指令、工具和职责范围。

Claude Code 启动时自动加载 Subagents，之后在对话里直接呼叫名字，它就会以对应角色身份响应。

#### 3.2 目录结构：全局 vs 项目级

**全局级（跨项目复用）：**

```
~/.claude/agents/
├── code-reviewer.md      # 代码审查员
├── test-writer.md       # 测试工程师
└── security-auditor.md # 安全审计员
```

**项目级（团队共享，推荐）：**

```
your-project/.claude/agents/
├── frontend-dev.md       # 前端工种
├── backend-dev.md        # 后端工种
└── architect.md          # 架构评审
```

项目级的好处是：提交到 Git 之后，新成员 clone 仓库即可拥有同一套 AI 工种定义，团队协作效率一致。

#### 3.3 怎么写一个 Subagent 文件

```
# 角色：代码审查员（Code Reviewer）

## 职责
你是一个严格的代码审查员，专注于代码质量、安全性和可维护性。

## 工作原则
- 每次 review 必须包含：逻辑错误、安全漏洞、性能问题、代码风格
- 发现问题必须给出具体修复建议，不只说"有问题"
- 优先审查：权限相关、数据库操作、外部 API 调用

## 输出格式
每次 review 输出：
1. 问题列表（按严重程度排序）
2. 推荐修复方案
3. 本次 review 综合评分（1-10）

## 触发信号
当用户在会话中提到 @code-reviewer 或要求"审查代码"时激活。
```

关键组成部分：

\- **角色名称** （顶行 `# ` ）：Subagent 的身份标识

\- **职责** ：这个角色干什么

\- **工作原则** ：怎么干

\- **输出格式** ：交付什么

\- **触发信号** ：什么时候激活

#### 3.4 在会话中调用 Subagent

在 Claude Code 会话里直接呼叫：

```
@code-reviewer
帮我 review 一下 src/auth/login.ts 这个文件
```

Claude 会自动切换到 code-reviewer 角色，以该角色的指令集来响应。完成 review 后，可以切回主会话继续其他任务。

#### 3.5 实战：同时配"代码审查员"+"测试工程师"

**步骤一：创建文件**

```
mkdir -p ~/.claude/agents

# 创建测试工程师
cat > ~/.claude/agents/test-writer.md << 'EOF'
# 角色：测试工程师（Test Writer）

## 职责
为代码编写可执行的测试用例，确保覆盖核心路径。

## 工作原则
- 测试文件名格式：原文件名 + .test.ts
- 必须包含：正常路径、边界条件、错误处理
- 每个测试用例要有中文注释说明意图
- 使用 Jest + Testing Library

## 输出格式
输出完整的测试文件内容，并说明覆盖了哪些场景。
EOF

# 创建代码审查员
cat > ~/.claude/agents/code-reviewer.md << 'EOF'
# 角色：代码审查员（Code Reviewer）

## 职责
审查代码质量、安全性和可维护性。

## 工作原则
- 必须包含：逻辑错误、安全漏洞、性能问题、代码风格
- 发现问题给出具体修复建议
- 优先审查：权限、数据库、外部 API 调用

## 输出格式
问题列表 + 修复建议 + 综合评分（1-10）
EOF
```

**步骤二：在会话中并行调用**

```
@code-reviewer @test-writer
我需要对 src/services/user.ts 做全面审查，同时生成测试用例。
code-reviewer 负责审查，test-writer 负责写测试。
两个可以并行工作。
```

#### 3.6 Subagents 的局限

Subagents 本质上是同一个 Claude 实例在跑，只是用不同指令集来响应不同角色。 **不解决并行问题** ，只是让角色分工更清晰。要真正并行，得靠 Agent Teams。

四、Agent Teams：多窗口并行的正确打开方式

#### 4.1 什么时候需要 Agent Teams

当一个 Claude 实例处理不过来，需要 **真正同时运行多个 agent** 时，Agent Teams 才是正确答案。

典型场景：

\- 前端界面和后端 API 同时开发，互不依赖

\- 需要"架构师"和"开发者"同时讨论一个设计方案

\- 同一个模块两个 AI 各自探索不同实现路径，最后合并

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/ibqW0esWbuWScXK9kc96V16ckFuiaQlzlwwicXwlsJeibVRqbWHsCGvWjujBiaVq8NfaHYr5ibYdDIgAGJs9hh86nicicJwZI3GgVLJCzqXQj6xU1tc/640?wx_fmt=jpeg&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

4.2 启用 Agent Teams

**方法一：settings.json（推荐）**

```
mkdir -p ~/.claude
cat > ~/.claude/settings.json << 'EOF'
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "teammateMode": "tmux"
}
EOF
```

**方法二：环境变量**

```
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

\> 注意： `agentTeams.enabled` 是旧版写法，当前版本（v2.1+）正确写法是 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` 环境变量或 `teammateMode: "tmux"` 配置项。

#### 4.3 tmux 在 Agent Teams 中的角色

tmux 在 Agent Teams 里是 Claude Code 用来 **托管多个队友窗口的底层容器** 。

4.3.1 工作原理

Claude Code 会：

\- 为 **每个队友自动创建独立的 tmux 窗口**

\- 每个窗口有独立的终端会话，显示该队友的全部输出

\- 你不需要手动执行 `tmux split-window` ，Claude Code 自动搞定

4.3.2 在多个队友窗口间切换

操作方式：

| 操作 | 按键 |
| --- | --- |
| 切换到下一个队友窗口 | `Shift+↑` |
| 切换到上一个队友窗口 | `Shift+↓` |
| 直接接管某个队友的操作 | 先切到该窗口，直接输入即可 |

4.3.3 iTerm2 用户：真正的 Split Pane 显示

如果你用 macOS + iTerm2，可以开启 tmux 控制模式，获得原生分屏体验：

```
# 启动 tmux 控制模式（iTerm2 专用）
tmux -CC
```

iTerm2 会自动把每个队友渲染成并排的 split pane， **真正做到同时可见所有 agent** ，而不需要来回切换。

\#### 4.3.4 tmux 基础命令（仅供调试参考）

正常使用时 Claude Code 会自动管理 tmux 会话，以下命令仅在需要手动清理时参考：

```
# 查看当前所有 tmux 会话
tmux list-sessions

# 断开会话（后台保持）
Ctrl+b 然后按 d

# 重新接入会话
tmux attach -t my-project

# 强制删除残留会话（出问题时用）
tmux kill-session -t my-project
```

#### 4.4 创建第一个 Agent Team

**步骤一：创建团队目录**

```
mkdir -p ~/.claude/teams/dev
```

**步骤二：配置团队成员**

```
cat > ~/.claude/teams/dev/config.json << 'EOF'
{
  "name": "dev",
  "members": [
    {
      "name": "frontend-dev",
      "role": "前端开发",
      "instructions": "你是一个专业的前端开发工程师，擅长 React、TypeScript 和 Tailwind CSS。"
    },
    {
      "name": "backend-dev",
      "role": "后端开发",
      "instructions": "你是一个专业的后端开发工程师，擅长 Node.js、Python FastAPI 和 PostgreSQL。"
    },
    {
      "name": "architect",
      "role": "架构评审",
      "instructions": "你是一个资深架构师，关注系统的可扩展性、稳定性和工程化最佳实践。"
    }
  ]
}
EOF
```

**步骤三：启动团队会话**

```
claude --team dev
```

启动后，Claude Code 会创建一个主会话，同时启动各个成员 Agent，它们可以独立工作也可以相互通信。

#### 4.5 Agent Teams 任务分配示例

在团队会话中，分配任务给不同成员：

```
architect：请分析一下 src/architecture 这个目录的结构，给出一个模块划分的优化建议。

frontend-dev：根据 architect 的建议，用 Next.js 重构 pages 目录。优先处理 /user 和 /dashboard 两个路径。

backend-dev：同步开始写 user 和 dashboard 对应的 RESTful API，要求：Node.js + Express + PostgreSQL，API 规范参考 OpenAPI 3.0。
```

三个 Agent 可以同时接收任务，各自并行工作。architect 的分析结果出来后，frontend-dev 可以直接引用，不需要重复传递上下文。

#### 4.6 Agent Teams 的通信机制

团队成员之间通过 **共享上下文** 来通信。主会话持有全局上下文，各成员可以读取和写入。架构师的结论自动对前端和后端可见，减少了手动传递信息的损耗。

#### 4.7 常见问题

**Q：Agent Teams 启动报错"tmux not found"**

A：先安装 tmux，命令见 4.3 节。macOS 用户用 `brew install tmux` ，Windows 用户需要用 WSL2。

**Q：团队成员不响应**

A：检查 `~/.claude/teams/{team}/config.json` 格式是否正确，JSON 必须严格合法。

**Q：队友窗口显示混乱，不知道在看哪个**

A：用 `Shift+↑` / `Shift+↓` 确认当前所在的窗口。也可以用 `tmux list-windows` 查看所有窗口状态。iTerm2 用户建议直接用 `tmux -CC` 模式，分屏更清晰。

**Q：Agent Teams 启动报错"tmux not found"**

A：先安装 tmux，macOS 用 `brew install tmux` ，Ubuntu/Debian 用 `sudo apt install tmux` 。Windows 用户需要用 WSL2。

**Q：团队成员不响应**

A：检查 `~/.claude/teams/{team}/config.json` 格式是否正确，JSON 必须严格合法。

五、Git Worktree：分支级别的硬隔离

#### 5.1 适用场景

当你需要在一个项目里同时处理多个不兼容的改动时，Git Worktree 比 Agent Teams 更底层、更稳定。

典型场景：

\- 同时做 Feature A 和 Refactor B，但两者改动重叠，不能在同一个分支上串行

\- 需要"保持当前工作目录干净"的同时并行处理一个紧急 Bugfix

\- 多人协作时，避免合并冲突

#### 5.2 工作原理

Git Worktree 允许你在同一个 Git 仓库里，同时创建多个工作目录，每个目录对应一个独立的分支。它们共享同一个 `.git` 对象库，但文件系统和提交历史完全隔离。

#### 5.3 基础命令

```
# 查看当前所有 Worktree
git worktree list

# 创建新的 Worktree（同时创建新分支）
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

#### 5.4 实战：结合 Claude Code 并行开发

```
# 场景：同时处理新功能 + 重构

# 1. 主分支继续开发新功能
cd ~/projects/myapp
claude
# 在主会话里继续 feature-auth 的工作

# 2. 创建 Worktree 做重构（隔离）
git worktree add ../refactor-db -b refactor/db
cd ../refactor-db
claude
# 新会话里专门做数据库重构，不影响主分支

# 3. 两边并行做完，合并
git checkout main
git merge refactor/db
git worktree remove ../refactor-db
git branch -d refactor/db
```

#### 5.5 Git Worktree vs Agent Teams 怎么选

| 维度 | Git Worktree | Agent Teams |
| --- | --- | --- |
| 隔离级别 | 分支级别（文件系统） | 上下文级别（内存） |
| 适用场景 | 大范围重构、并行分支开发 | 快速探索、多角色协作 |
| Claude Code 集成 | 完全兼容 | 需要 tmux 支持 |
| 多人协作 | 支持 | 主要单人使用 |
| 上手难度 | ★★ | ★★★ |

**用 Git Worktree** ：改动会相互冲突、需要硬隔离、多人协作场景

**用 Agent Teams** ：需要快速并行探索、多个角色同时讨论方案

六、工作流编排：让并行单元有序运转

#### 6.1 什么是工作流编排

前面说的三条路解决的是"怎么并行"，但多个工作单元怎么有序配合、谁先做谁后做、怎么做完了怎么整合，这是另一层问题，叫工作流编排。

在 Claude Code 生态里，工作流编排有三个关键工具： **Plan 模式** 、 **Agent Teams** （即多 agent 协作编排）、 **CLAUDE.md 的任务分解** 。其中 Agent Teams 既是执行层，也是编排层的核心——通过它你可以协调多个 agent 按顺序或并行完成复杂任务。

#### 6.2 Plan 模式：动手之前的任务分解

Claude Code 内置 `/plan` 命令，它不是一个执行命令，而是一个 **任务规划工具** 。

```
# 在 Claude Code 会话里输入
/plan

# Claude 会分析当前项目结构和任务需求
# 输出一个分步骤的计划，等待你确认后才执行
```

输出格式示例：

```
📋 Plan Mode

正在分析代码库...
正在设计实现方案...

计划概要：
- 使用 d3-cloud 实现词云布局
- 后端添加 /api/news/wordcloud 端点
- 前端创建 WordCloud 组件
- 支持点击筛选、深色主题适配

预估工作量：2 天

详细步骤 [点击展开]...
[批准计划]  [修改建议]  [取消]
```

Plan 模式的实际价值： **把"想清楚做什么"和"动手做"分开** 。很多时候 AI 编程效率低，不是因为 AI 写代码慢，而是因为给的指令本身就有问题——需求没说清楚、边界没定义、优先级没说。Plan 模式强制你先拿到一个完整方案再动。

#### 6.3 在工作流中嵌入 Plan 模式

把 Plan 模式嵌入到多 Agent 工作流里，能显著减少返工：

```
architect（Agent Team 里）：用 /plan 分析 src/modules 里各模块的依赖关系，给出重构优先级建议。

architect 的 plan 确认后，再分配给 frontend-dev 和 backend-dev 各自执行。

backend-dev：
/plan
根据 architect 的分析结果，设计 database schema 迁移方案。

backend-dev plan 确认后，执行迁移。
```

这样每个 Agent 动手之前都有一次"想清楚"的环节，减少"做了半天发现方向错了"的损耗。

#### 6.4 Multi-Agent 协作工作流模板

一个典型的多 Agent 工作流：

```
阶段一：任务分解（Plan 模式）
├─ 主会话：定义项目范围和目标
├─ /plan：拆解为具体模块
└─ 输出：完整的任务分解清单

阶段二：角色分配（Agent Teams）
├─ architect：负责架构设计和方案评审
├─ frontend-dev：负责前端实现
└─ backend-dev：负责后端实现

阶段三：并行执行
├─ 各 Agent 独立工作
├─ 通过共享上下文通信
└─ architect 负责协调冲突

阶段四：整合与 Review（Subagents）
├─ code-reviewer：全面代码审查
├─ test-writer：生成测试用例
└─ architect：最终架构评审

阶段五：合并（Git Worktree）
├─ 合并各分支到 main
└─ 运行集成测试
```

#### 6.5 把工作流模板固化到 CLAUDE.md

上面 6.4 的工作流模板，每次新建项目都要重新配一遍，太累了。实际做法是： **把团队配置和工作流固化到项目的 `CLAUDE.md` 里** ，Claude Code 启动时自动加载。

在项目根目录创建或编辑 `CLAUDE.md` ，写入：

```
# 项目 AI 团队配置

## 默认团队
本项目使用以下 Agent 团队配置：

| 角色 | 职责 |
|------|------|
| architect | 架构设计和技术方案评审 |
| frontend-dev | 前端开发，React/TypeScript/Tailwind CSS |
| backend-dev | 后端开发，Node.js/Python + PostgreSQL |
| code-reviewer | 代码审查，安全和质量问题 |

## 工作流规范
1. **任务分解**：涉及多模块时，先用 /plan 拆解，确认后再执行
2. **方案优先**：architect 评审通过的技术方案，才能分配给前端/后端执行
3. **Review 前置**：所有代码合并前必须经过 code-reviewer 审查

## 启动团队
\\`\\`\\`bash
claude --team dev
\\`\\`\\`
启动后，architect 会自动分析项目结构并给出模块划分建议。
```

下次在这个项目里开 Claude Code，它自己就加载好了，不用再手动配。

#### 6.6 容易踩的坑

**坑一：Subagent 记忆不共享**

Subagent 之间不共享对话历史，各自是独立的上下文。跨 Subagent 传递信息需要在主会话里中转。

**坑二：Agent Teams 上下文窗口竞争**

多个 Agent 同时跑，共享同一个上下文窗口。如果每个都输出大量内容，上下文会被快速填满。解决：每个 Agent 的指令里明确限制输出长度。

**坑三：Git Worktree 合并冲突**

Worktree 之间共享 `.git` 对象库，但工作目录完全独立。合并前确保主分支没有未提交的改动，否则可能触发保护机制拒绝合并。

**坑四：Plan 模式太慢**

每次都用 /plan 会拖慢节奏。经验： **多模块重构、新技术引入、架构调整时用 Plan；常规 CRUD、小需求直接做。**

#### 6.7 Routines：让并行任务定时自动跑起来

2026 年 4 月 Claude Code 上线了一个新功能叫 Routines。前面几节讲的是怎么并行，Routines 解决的是另一个问题：什么时候让这些任务自动跑起来。

6.7.1 核心概念

你可以把"一次 prompt + 代码仓库 + 触发条件"打包成一个 Routines 配置，丢到 Anthropic 云端跑，不需要你的电脑保持开机。

三种触发方式：

| 触发方式 | 说明 | 典型场景 |
| --- | --- | --- |
| **定时触发** | cron 表达式，每小时/每天/自定义周期 | 每天早上自动跑代码审查 |
| **API 触发** | 调 REST 接口触发执行 | 外部系统触发 CI/CD 流水线 |
| **GitHub 事件** | PR opened、push、issue comment 等 | PR 创建时自动做 code review |

6.7.2 和 Agent Teams 的配合

这是最值得关注的组合：Routines 作为调度层，Agent Teams 作为执行层，形成真正的"无人值守流水线"：

```
Routines（定时 08:00）
  └─→ 触发 Agent Teams
        ├─ architect：代码审查
        ├─ backend-dev：Bug 修复
        └─ frontend-dev：依赖检查
  └─→ 审查结果自动发 PR comment 或邮件通知
```

整个流程不需要你在电脑前，醒来直接看结果。

6.7.3 配置示例

```
# 定时触发：每天早上 8 点自动做代码审查
# 在 Claude Code 里创建 Routine
/claude routine create   --name "morning-review"   --prompt "审查昨晚到现在的所有 commits，重点关注：安全漏洞、性能问题、测试覆盖率"   --trigger "0 8 * * *"   --repo ./my-project
```

6.7.4 当前限制

\- Routines 处于 **研究预览阶段** ，稳定性仍在迭代

\- 需要科学上网访问 Anthropic 云端

\- 部分触发器（尤其是 GitHub 事件）需要配置 webhook 回调地址

\> **使用建议** ：先用定时触发跑起来，体验完整流程，再逐步接入 GitHub 事件触发。

\> **订阅限制** ：Routines 运行在 Anthropic 云端，目前仅支持 Claude 官方模型，不支持 OpenRouter、硅基流动等第三方 API 路由。若你正在使用第三方模型 API，需等待后续支持或第三方开发者推出平替方案。