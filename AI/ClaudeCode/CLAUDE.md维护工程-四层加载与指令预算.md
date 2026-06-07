---
title: "CLAUDE.md 维护工程：四层加载与指令预算"
source: "https://mp.weixin.qq.com/s/CHdj9kwpfxCHPmu-k_4u1Q"
created: 2026-06-07
tags:
  - claude-code
  - CLAUDE-md
  - engineering
---

# CLAUDE.md 维护工程：四层加载与指令预算

## 一、CLAUDE.md 是什么

CLAUDE.md 不是 README，不是注释，是 Claude Code 每次启动时自动读取的**持久化指令文件**。每次新会话，Claude Code 第一件事就是把 CLAUDE.md 塞进上下文窗口，整个会话过程中都能"看到"。

`/init` 只是起点——它扫描代码仓库（package.json、Makefile、README），自动生成一份包含构建命令、测试命令、项目结构的基础 CLAUDE.md。真正的维护从这之后开始。

> 为兼容 Codex，可以让 CLAUDE.md 加载 AGENTS.md，省得一个项目维护两份规则。

## 二、四层加载体系

Claude Code 有完整的四层加载体系，搞懂才能用好 CLAUDE.md。

### 第一层：全局配置

路径：`~/.claude/CLAUDE.md`，所有项目都会加载。放个人编码偏好：

```markdown
- 使用 2 空格缩进
- commit message 用英文，遵循 Conventional Commits
- 不写注释，用有意义的变量名和函数名代替
```

### 第二层：项目配置

路径：项目根目录 `CLAUDE.md` 或 `.claude/CLAUDE.md`，提交到 git，团队共享。最常用的一层——构建命令、代码规范、架构约定。

### 第三层：本地覆盖

路径：`CLAUDE.local.md` 或 `.claude/CLAUDE.local.md`，加到 `.gitignore`，只在本地生效。放个人环境变量、调试偏好、试验中的新规则。

### 第四层：子目录配置

子目录下的 CLAUDE.md，**按需加载**——只有 Claude 读取到那个目录下的文件时才加载。对 monorepo 特别友好：

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

核心逻辑在 `src/utils/claudemd.ts` 的 `getMemoryFiles()` 函数：

```typescript
// 1. 加载系统级和用户级 CLAUDE.md
const managedClaudeMd = getMemoryPath('Managed')
const userClaudeMd = getMemoryPath('User')

// 2. 从当前目录往上收集所有路径
const dirs: string[] = []
let currentDir = getOriginalCwd()
while (currentDir !== parse(currentDir).root) {
  dirs.push(currentDir)
  currentDir = dirname(currentDir)
}

// 3. 反转！从根目录往下走，依次加载
for (const dir of dirs.reverse()) {
  // 加载 CLAUDE.md（Project 类型）
  // 加载 .claude/CLAUDE.md
  // 加载 .claude/rules/*.md
  // 加载 CLAUDE.local.md（Local 类型）
}
```

**越靠近工作目录的文件越晚加载，优先级越高。** CLAUDE.local.md 在 CLAUDE.md 之后加载，天然能覆盖项目规则。

> 第一维护原则：**不要让不同层级的 CLAUDE.md 互相矛盾。**

## 三、指令预算：LLM 注意力是稀缺资源

Anthropic 官方原话：

> "If your CLAUDE.md is too long, Claude ignores half of it because important rules get lost in the noise."

### 学术依据

arXiv 论文《How Many Instructions Can LLMs Follow at Once?》（Daniel Jaroslawicz 等，论文编号 2507.11538）测试了模型同时遵循多条指令的能力：

- 给模型一个写报告任务 + N 条约束（关键词、语态、段落限制等）
- **即使最强前沿模型，500 条指令密度下准确率仅 68%**
- 指令越多遵循率越低，且模型系统性偏向序列前面的指令

**瓶颈不是上下文窗口装不下，而是模型的注意力分配不过来。** Claude Code 系统提示本身已带大量内置指令（权限控制、工具规范、安全约束），CLAUDE.md 是叠加在这些之上的，留给 CLAUDE.md 的有效空间没有想象的多。

### 判断一条指令该不该放进 CLAUDE.md

问两个问题：

1. **如果不写这条，Claude 会不会搞错？** 能从代码/配置推断出来的不用写。
2. **这条指令是不是每次会话都需要？** 只在特定场景需要的，放 `rules/` 做路径限定。

Anthropic 官方建议：**像维护代码一样维护 CLAUDE.md**——定期 review，没遵守的加强调，本来就会做对的果断删。

## 四、好规则 vs 坏规则

以 PaiCLI 项目（纯 Java Agent CLI）为例：

**✅ 好规则**（不写就一定会搞错，信息密度高）：

```markdown
- 构建：mvn clean package -DskipTests
- search_code 是 RAG 辅助，不是主要代码定位方式，优先用 glob → grep → read
- 改了命令入口 → Main.java + CliCommandParser + 测试 + 文档
- 禁止提交 .env、真实 API Key、target/ 产物
```

**❌ 坏规则**（Claude 自己能推断，等于噪音）：

```markdown
- 使用 Java 17 编写代码       # pom.xml 里有 <java.version>17
- 遵循分层架构                 # 看目录结构就知道
- 保持代码整洁                 # 等于没说
```

**好规则三特征**：
1. 一句话能写完（需要三行说明就太复杂了，拆成三条或放文档里）
2. Claude 靠自己推断不出来
3. 有明确行动指导（"PathGuard 限制在项目根目录，禁止绝对路径逃逸" vs "注意安全"）

## 五、Anthropic 官方 CLAUDE.md 结构

Anthropic 的 `claude-code-action` 仓库（GitHub Actions 跑 Claude Code 的项目）的 CLAUDE.md 结构：

- **Commands**：构建、测试、lint 的具体命令
- **What This Is**：一句话说清楚项目是什么
- **How It Runs**：运行机制（改代码前必须知道的事）
- **Key Concepts**：3-5 个核心概念
- **Things That Will Bite You**：踩坑清单
- **Code Conventions**：只写和默认不一样的部分

## 六、rules/ 目录：精准投放

`.claude/rules/` 目录下每个 `.md` 文件是独立指令集。带 `paths` 前置字段的，只在操作匹配路径的文件时才加载：

```markdown
# .claude/rules/react-conventions.md
---
paths:
  - "src/components/**/*.tsx"
  - "src/hooks/**/*.ts"
---
- 组件用函数式写法，不用 class
- props 在函数签名中解构
- 自定义 hook 以 use 开头
- 状态管理用 zustand，不用 redux
```

推荐的目录结构：

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

**进阶：`@path` 语法导入外部文件**：

```markdown
# CLAUDE.md
@README.md
@docs/architecture.md
## 项目规则
- 所有 API 返回统一用 Result 包装
```

`@README.md` 启动时展开，把内容注入上下文。适合 README 写得好但不想重复的项目。

## 七、/init 与 /memory 的分工

**`/init` 负责冷启动**：扫描仓库生成基础 CLAUDE.md（构建命令、测试命令、项目描述）。

**`/memory` 负责热更新**：每个项目在 `~/.claude/projects/` 下有 `MEMORY.md`，Claude 自动把跨会话需记住的信息写入。下次启动时 MEMORY.md 前 200 行自动加载。

**分工原则**：
- **CLAUDE.md** 放团队共享的、长期稳定的规则（提交到 git）
- **memory** 放个人的、会变化的、日常积累的经验

**维护节奏**：
- 第一周：`/init` 生成基础版，日常使用中 Claude 自动往 memory 积累
- 第二周起：review memory 内容，通用经验提炼到 CLAUDE.md，过时条目清理掉

## 八、配置体系四角色分工

| 角色 | 职责 | 特征 |
|------|------|------|
| **CLAUDE.md** | 建议 | 团队共享的编码规范和架构约定 |
| **settings.json** | 强制 | 权限控制、环境变量、MCP 配置，硬性约束 |
| **hooks** | 自动化 | 必须每次执行的事（格式化/安全检查），由 harness 执行不依赖 Claude 记忆 |
| **rules/** | 精准投放 | 按路径限定加载，节省指令预算 |

```json
// settings.json 示例
{
  "permissions": {
    "allow": ["Bash(npm run *)", "Bash(git *)"],
    "deny": ["Bash(rm -rf *)", "Bash(git push --force)"]
  }
}
```

**一句话记住**：CLAUDE.md 管建议，settings.json 管强制，hooks 管自动化，rules/ 管精准投放。

## 九、实战模板

```markdown
# CLAUDE.md

## Commands
- 构建：mvn clean package -DskipTests
- 测试：mvn test
- 单个测试：mvn test -Dtest=XxxTest
- 代码检查：mvn spotbugs:check
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
