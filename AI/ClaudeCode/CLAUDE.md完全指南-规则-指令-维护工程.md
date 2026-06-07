---
title: "CLAUDE.md 完全指南：规则、指令与维护工程"
source:
  - "https://mp.weixin.qq.com/s/CHdj9kwpfxCHPmu-k_4u1Q"
  - "https://x.com/Mnilax/status/2053116311132155938"
  - "https://x.com/TheAIWorld22/status/2053023798170198453"
created: 2026-06-07
tags:
  - claude-code
  - CLAUDE-md
  - best-practices
  - engineering
aliases:
  - CLAUDE.md完全指南
---

# CLAUDE.md 完全指南：规则、指令与维护工程

> 三篇文章合并：Mnilax 12 条规则模板（写什么）+ Mayank Agarwal 21 条指令清单（怎么写）+ 四层加载与指令预算（怎么管）。

---

## 一、CLAUDE.md 是什么

CLAUDE.md 是 Claude Code 每次启动时自动读取的**持久化指令文件**——不是 README，不是注释，是给 Claude 写的"入职须知"。每次新会话，Claude Code 第一件事就是把 CLAUDE.md 塞进上下文窗口，整个会话过程中都能"看到"。

`/init` 只是起点——它扫描代码仓库（package.json、Makefile、README），自动生成包含构建命令、测试命令、项目结构的基础 CLAUDE.md。真正的维护从这之后开始。

---

## 二、四层加载体系

### 第一层：全局配置

路径：`~/.claude/CLAUDE.md`，所有项目都会加载。放个人编码偏好：

```markdown
- 使用 2 空格缩进
- commit message 用英文，遵循 Conventional Commits
- 不写注释，用有意义的变量名和函数名代替
```

### 第二层：项目配置

路径：项目根目录 `CLAUDE.md` 或 `.claude/CLAUDE.md`，提交到 git，团队共享。最常用的一层。

### 第三层：本地覆盖

路径：`CLAUDE.local.md` 或 `.claude/CLAUDE.local.md`，加到 `.gitignore`，只在本地生效。放个人环境变量、调试偏好、试验中的新规则。

### 第四层：子目录配置

子目录下的 CLAUDE.md，**按需加载**——只有 Claude 读取到那个目录下的文件时才加载。对 monorepo 友好：

```
my-monorepo/
├── CLAUDE.md              # 全局项目规则
├── frontend/
│   └── CLAUDE.md          # React 相关规则，按需加载
├── backend/
│   └── CLAUDE.md          # Java/Spring 相关规则，按需加载
└── infra/
    └── CLAUDE.md          # 部署相关规则，按需加载
```

### 加载顺序（源码级）

核心逻辑在 `src/utils/claudemd.ts` 的 `getMemoryFiles()` 函数：先从当前目录往上收集所有路径，然后 `dirs.reverse()` 反转，从根目录往工作目录走。**越靠近工作目录的文件越晚加载，优先级越高。** CLAUDE.local.md 在 CLAUDE.md 之后加载，天然能覆盖项目规则。

> 第一维护原则：**不要让不同层级的 CLAUDE.md 互相矛盾。**

---

## 三、指令预算：为什么要精简

### 学术依据

arXiv 论文《How Many Instructions Can LLMs Follow at Once?》（2507.11538）：

- 给模型一个写报告任务 + N 条约束，看模型能遵守多少条
- **即使最强前沿模型，500 条指令密度下准确率仅 68%**
- 指令越多遵循率越低，且模型系统性偏向序列前面的指令

瓶颈不是上下文窗口装不下，**而是模型的注意力分配不过来**。Claude Code 系统提示本身已带大量内置指令，CLAUDE.md 是叠加在这些之上的。

### 实测数据（Mnilax，30 个代码库 × 50 个任务 × 6 周）

| 配置 | 错误率 | 合规率 |
|------|--------|--------|
| 无 CLAUDE.md | ~41% | N/A |
| Karpathy 4 条 | ~11% | ~78% |
| 完整 12 条 | ~3% | ~76% |
| 超过 18 条 | — | 52%（崩了） |

关键发现：4→12 条**几乎未增加合规开销**（78%→76%），却将错误率再降 8 个百分点。但超过 18 条后合规率急剧下降。**200 行天花板是真的。**

### 判断一条指令该不该放

1. **如果不写这条，Claude 会不会搞错？** 能从代码/配置推断出来的不用写
2. **这条指令是不是每次会话都需要？** 只在特定场景需要的，放 `rules/` 做路径限定

Anthropic 官方建议：**像维护代码一样维护 CLAUDE.md**——定期 review，没遵守的加强调，本来就会做对的果断删。

---

## 四、好规则 vs 坏规则

### 好规则三特征

1. **一句话能写完**（需要三行说明就太复杂了）
2. **Claude 靠自己推断不出来**
3. **有明确行动指导**（"PathGuard 限制在项目根目录" vs "注意安全"）

### ✅ 好规则示例（PaiCLI 项目）

```markdown
- 构建：mvn clean package -DskipTests
- search_code 是 RAG 辅助，优先用 glob → grep → read
- 改了命令入口 → Main.java + CliCommandParser + 测试 + 文档
- 禁止提交 .env、真实 API Key、target/ 产物
```

### ❌ 坏规则示例

```markdown
- 使用 Java 17 编写代码       # pom.xml 里有 <java.version>17
- 遵循分层架构                 # 看目录结构就知道
- 保持代码整洁                 # 等于没说
```

### 试过但放弃的

- **在 CLAUDE.md 里放例子**：三个例子消耗约 10 条规则的上下文，且 Claude 会过度拟合
- **"小心"/"多想"/"真正专注"**：纯噪音，合规率掉到约 30%——不可测试
- **让 Claude 做"高级工程师"**：没用，Claude 已经觉得自己是高级的。祈使句规则能闭合差距，身份提示不能

---

## 五、12 条行为规则模板（Mnilax）

> 来源：Mnilax 在 Karpathy 原版 4 条基础上新增 8 条，30 个代码库实测，错误率从 41% 降到 3%。

### 规则 1-4（Karpathy 原版——底线）

| 规则 | 要点 |
|------|------|
| **先思后码** | 明确假设，有疑先问，不盲目猜测 |
| **简单至上** | 最少代码解决问题，不加"以防万一"的冗余 |
| **外科手术式修改** | 仅改必要部分，不"顺手优化"相邻代码 |
| **目标驱动执行** | 定义成功标准，持续迭代直至验证通过 |

### 规则 5-12（Mnilax 补齐——覆盖剩余 60% 失败模式）

| 规则 | 要点 | 翻车场景 |
|------|------|----------|
| **模型只做判断** | 分类/起草/摘要用 Claude；路由/重试/确定性转换用代码 | 用 Claude 判断 503 该不该重试，策略变成随机的 |
| **Token 预算硬限** | 单任务 4K、单会话 30K，超了就摘要重置 | 90 分钟调试会话，模型开始建议 40 条消息前已否决的方案 |
| **暴露冲突不折中** | 两种模式矛盾时择一，不强行融合 | async/await + Error Boundary 叠加，异常被静默吞掉两次 |
| **先读后写** | 添加代码前通读导出接口、调用方、公共工具 | 在已有相同函数旁加了新函数，因导入顺序优先执行 |
| **测试验证意图** | 测试必须体现 WHY，不只是断言 WHAT | 12 个测试全通过，但生产认证彻底失效——只验证了"有返回值" |
| **长任务设检查点** | 每步总结已完成/已验证/剩余待办 | 6 步重构第 4 步出错，在错误状态上完成了第 5、6 步 |
| **约定胜于新奇** | 代码库内规范一致性 > 个人偏好 | class 组件代码库引入 hooks，搞坏了测试模式 |
| **显性失败** | 跳过步骤就不能说"已完成"，跳过测试不能说"通过" | 迁移"成功完成"但静默跳过 14% 记录，11 天后数据对不上 |

### 12 条规则英文版（可直接粘贴）

```markdown
# CLAUDE.md — 12-rule template

These rules apply to every task in this project unless explicitly overridden.
Bias: caution over speed on non-trivial work. Use judgment on trivial tasks.

## Rule 1 — Think Before Coding
State assumptions explicitly. If uncertain, ask rather than guess.
Present multiple interpretations when ambiguity exists.
Push back when a simpler approach exists.
Stop when confused. Name what's unclear.

## Rule 2 — Simplicity First
Minimum code that solves the problem. Nothing speculative.
No features beyond what was asked. No abstractions for single-use code.
Test: would a senior engineer say this is overcomplicated? If yes, simplify.

## Rule 3 — Surgical Changes
Touch only what you must. Clean up only your own mess.
Don't "improve" adjacent code, comments, or formatting.
Don't refactor what isn't broken. Match existing style.

## Rule 4 — Goal-Driven Execution
Define success criteria. Loop until verified.
Don't follow steps. Define success and iterate.
Strong success criteria let you loop independently.

## Rule 5 — Use the model only for judgment calls
Use me for: classification, drafting, summarization, extraction.
Do NOT use me for: routing, retries, deterministic transforms.
If code can answer, code answers.

## Rule 6 — Token budgets are not advisory
Per-task: 4,000 tokens. Per-session: 30,000 tokens.
If approaching budget, summarize and start fresh.
Surface the breach. Do not silently overrun.

## Rule 7 — Surface conflicts, don't average them
If two patterns contradict, pick one (more recent / more tested).
Explain why. Flag the other for cleanup.
Don't blend conflicting patterns.

## Rule 8 — Read before you write
Before adding code, read exports, immediate callers, shared utilities.
"Looks orthogonal" is dangerous. If unsure why code is structured a way, ask.

## Rule 9 — Tests verify intent, not just behavior
Tests must encode WHY behavior matters, not just WHAT it does.
A test that can't fail when business logic changes is wrong.

## Rule 10 — Checkpoint after every significant step
Summarize what was done, what's verified, what's left.
Don't continue from a state you can't describe back.
If you lose track, stop and restate.

## Rule 11 — Match the codebase's conventions, even if you disagree
Conformance > taste inside the codebase.
If you genuinely think a convention is harmful, surface it. Don't fork silently.

## Rule 12 — Fail loud
"Completed" is wrong if anything was skipped silently.
"Tests pass" is wrong if any were skipped.
Default to surfacing uncertainty, not hiding it.
```

---

## 六、21 条指令清单（Mayank Agarwal）

> 来源：X 平台 290 万阅读的实操长帖，覆盖五个维度，每条可直接复制到 CLAUDE.md。

### 沟通方式（指令 1-4）

| # | 指令 |
|---|------|
| 1 | 禁掉废话开场白，直接给答案 |
| 2 | 重要任务前先给 2-3 种方案，等选择后再继续 |
| 3 | 不确定就说"不确定"，不用听起来合理的信息填补空白 |
| 4 | 回复长度匹配任务复杂度，不重复表述填充篇幅 |

### 行为准则（指令 5-8）

| # | 指令 |
|---|------|
| 5 | 大改之前先停住，描述准备改什么、为什么改，等确认 |
| 6 | 只改明确要求改的地方，发现改进点在末尾提出 |
| 7 | 做完附简短变更总结：改了什么、没动什么、需要关注什么 |
| 8 | 永远不要代替发送/发布/分享，必须当前消息明确确认 |

### 个人上下文（指令 9-11）

| # | 指令 |
|---|------|
| 9 | 告诉 Claude 你是谁（角色/背景/擅长/正在学的） |
| 10 | 告诉 Claude 你在做什么（项目/目标/受众/基调） |
| 11 | 锁定你的写作风格（语气/句式/惯用词/格式偏好） |

### 记忆连续性（指令 12-15）

| # | 指令 |
|---|------|
| 12 | 维护 MEMORY.md——每次重要决策后记录：决定了什么、为什么、否决了什么替代方案 |
| 13 | 会话结束时写总结到 MEMORY.md：做了什么、进行中、下次从哪继续 |
| 14 | 维护 ERRORS.md——尝试超两次才成功的方法记录下来，类似任务前先检查 |
| 15 | 给一份"永远成立"的事实清单，任务与之冲突时先标出 |

### 开发者安全网（指令 16-21）

| # | 指令 |
|---|------|
| 16 | 只修改当前任务相关的文件/函数/代码行 |
| 17 | 不可逆操作前停下，列影响范围，要求确认 |
| 18 | 部署/迁移/外部 API 调用/不可逆命令——无例外必须确认 |
| 19 | 锁定技术栈，不主动建议替代方案 |
| 20 | 改完代码附变更清单（改过的文件/未触碰的文件/跟进事项） |
| 21 | Karpathy 四条规则（同规则 1-4） |

---

## 七、rules/ 目录：精准投放

`.claude/rules/` 目录下每个 `.md` 文件是独立指令集。带 `paths` 前置字段的，只在操作匹配路径的文件时才加载：

```markdown
# .claude/rules/react-conventions.md
---
paths:
  - "src/components/**/*.tsx"
  - "src/hooks/**/*.ts"
---
- 组件用函数式写法，不用 class
- 自定义 hook 以 use 开头
- 状态管理用 zustand，不用 redux
```

推荐目录结构：

```
.claude/
├── CLAUDE.md              # 核心规则，控制在 80 行以内
└── rules/
    ├── code-style.md      # 通用代码风格，无路径限定
    ├── testing.md          # 测试约定
    ├── security.md         # 安全规则
    ├── frontend.md         # 前端规则，paths: ["src/**/*.tsx"]
    └── api.md              # API 规则，paths: ["src/api/**/*.ts"]
```

**进阶：`@path` 语法**——`@README.md` 启动时展开，把内容注入上下文，适合 README 写得好但不想重复的项目。

---

## 八、/init 与 /memory 的分工

| 命令 | 职责 | 内容去向 |
|------|------|----------|
| `/init` | 冷启动 | 生成基础 CLAUDE.md（构建/测试命令、项目描述） |
| `/memory` | 热更新 | `~/.claude/projects/` 下的 MEMORY.md，下次启动前 200 行自动加载 |

**分工原则**：
- **CLAUDE.md** 放团队共享的、长期稳定的规则（提交到 git）
- **memory** 放个人的、会变化的、日常积累的经验

**维护节奏**：第一周 `/init` 生成基础版，日常使用中 Claude 自动往 memory 积累。第二周起定期 review memory，通用经验提炼到 CLAUDE.md，过时条目清理掉。

---

## 九、配置体系四角色分工

| 角色 | 职责 | 特征 |
|------|------|------|
| **CLAUDE.md** | 建议 | 团队共享的编码规范和架构约定 |
| **settings.json** | 强制 | 权限控制、环境变量、MCP 配置，硬性约束 |
| **hooks** | 自动化 | 必须每次执行的事（格式化/安全检查），由 harness 执行 |
| **rules/** | 精准投放 | 按路径限定加载，节省指令预算 |

**一句话记住**：CLAUDE.md 管建议，settings.json 管强制，hooks 管自动化，rules/ 管精准投放。

---

## 十、Anthropic 官方 CLAUDE.md 结构

来自 `claude-code-action` 仓库（GitHub Actions 跑 Claude Code 的项目）：

- **Commands**：构建、测试、lint 的具体命令
- **What This Is**：一句话说清楚项目是什么
- **How It Runs**：运行机制（改代码前必须知道的事）
- **Key Concepts**：3-5 个核心概念
- **Things That Will Bite You**：踩坑清单
- **Code Conventions**：只写和默认不一样的部分

---

## 十一、实战模板

```markdown
# CLAUDE.md

## Commands
- 构建：mvn clean package -DskipTests
- 测试：mvn test
- 单个测试：mvn test -Dtest=XxxTest
- 格式化：mvn spotless:apply

## What This Is
一句话说清楚项目是什么。

## Architecture
- 入口：Main.java → CliCommandParser 分发命令
- 不要动 agent/core/ 下的接口定义，下游工具全部依赖它们

## Things That Will Bite You
- search_code 是 RAG 辅助，优先用 glob → grep → read
- 改了命令入口 → 必须同步 Main.java + CliCommandParser + 测试 + 文档
- 测试里的 API Key 全部用 mock，禁止提交真实 Key

## Code Conventions
- 日志用 SLF4J，不用 System.out
- 异常不要吞掉，至少 log.warn
- 新工具必须实现 Tool 接口并在 ToolRegistry 注册

## Don't
- 不要在业务代码里直接 new Thread
- 不要改 .env.example 的格式，CI 依赖它
```

整个文件不到 50 行，该覆盖的全覆盖了。

---

## 心智模型

1. **CLAUDE.md 不是许愿清单**——是闭合你观察到过的特定失效模式的行为合约。每条规则应能回答：这条规则预防的是什么错误？
2. **6 条针对你真踩过的坑的规则，比 12 条里有 6 条你永远用不上的更好**——Karpathy 4 条是地基，补齐的选你实际需要的。
3. **Skills 工程化是上层建筑，CLAUDE.md 是地基**——写 prompt 比的是"这次输出对"，写 CLAUDE.md 比的是"未来 100 次都稳定输出对且 token 还省"。
