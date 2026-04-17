---
title: Claude Code 扩展体系
tags:
  - AI
  - claude-code
  - MCP
  - skills
  - plugin
  - slash-command
aliases:
  - CC扩展体系
  - Claude Code Extensions
---

# Claude Code 扩展体系

Claude Code 的核心竞争力不只是对话和代码生成，更在于它的**四层扩展机制**。这四层机制各有定位，组合起来构成一个可编排、可沉淀、可分发的智能工作流系统。

| 层级 | 机制 | 本质 | 触发方式 | 注入方式 |
|------|------|------|---------|---------|
| 1 | **MCP** | 外部工具桥梁 | 自动（AI 判断需要时调用） | tool call |
| 2 | **Skills** | 自动触发的能力包 | 自动（匹配用户意图） | system prompt |
| 3 | **Slash Commands** | 手动触发的工作流 | 手动（`/命令名`） | user message |
| 4 | **Plugin** | 打包分发容器 | — | 包含以上所有 |

**一句话总结**：MCP 是"手"（操作外部世界），Skills 是"肌肉记忆"（自动响应），Slash Commands 是"快捷键"（手动触发），Plugin 是"安装包"（打包分发）。

单个 Skill 是能力，多个 Skill 编排是流程，Skill + MCP + SubAgent 是智能体。

---

# 一、MCP（Model Context Protocol）

MCP 是连接 AI 模型与外部工具、数据源的标准化桥梁协议。通过 MCP Server，Claude Code 可以调用文件系统、数据库、API、浏览器等外部资源。

- **协议模型**：Client（Claude Code）↔ Server（MCP 进程），通过 stdio 通信
- **安装方式**：`claude mcp add <name> -- <command>` 或在 JSON 配置文件中声明
- **配置位置**：用户全局 `~/.claude/settings.json` 或项目级 `.claude/settings.json`

---

## 常用 MCP 服务器

### context7

**场景**：查最新框架文档（Next.js 15、React 19）、API 参数和用法确认、库的最佳实践和陷阱、版本迁移指南。

用个人 GitHub 账号登录：[https://context7.com/](https://context7.com/)

**VSCode 扩展**：在扩展界面搜 `@mcp context7`，选择安装。配置文件 JSON 中添加 API Key：

```json
"servers": {
  "io.github.upstash/context7": {
    "type": "stdio",
    "command": "npx",
    "args": [
      "@upstash/context7-mcp@1.0.30"
    ],
    "env": {
      "CONTEXT7_API_KEY": ""
    },
    "gallery": "",
    "version": "1.0.30"
  }
}
```

**Claude Code**：

```sh
claude mcp add context7 -- npx -y @upstash/context7-mcp --api-key ""
```

---

### atlassian

用 Docker 方式安装。安装完成之后，在家目录配置文件中添加进去 Docker 命令和 token，启动 colima 就能自动连接 MCP。

```json
"mcpServers": {
  "atlassian": {
    "type": "stdio",
    "command": "docker",
    "args": [
      "run", "-i", "--rm",
      "-e", "JIRA_URL",
      "-e", "JIRA_USERNAME",
      "-e", "JIRA_PERSONAL_TOKEN",
      "-e", "CONFLUENCE_URL",
      "-e", "CONFLUENCE_USERNAME",
      "-e", "CONFLUENCE_PERSONAL_TOKEN",
      "ghcr.io/sooperset/mcp-atlassian:latest"
    ],
    "env": {
      "JIRA_URL": "",
      "JIRA_USERNAME": "",
      "JIRA_PERSONAL_TOKEN": "",
      "CONFLUENCE_URL": "",
      "CONFLUENCE_USERNAME": "",
      "CONFLUENCE_PERSONAL_TOKEN": ""
    }
  }
}
```

---

### bitbucket

```json
"bitbucket": {
  "type": "stdio",
  "command": "npx",
  "args": [
    "-y",
    "@zhanglc77/bitbucket-mcp-server"
  ],
  "env": {
    "BITBUCKET_BASE_URL": "",
    "BITBUCKET_USERNAME": "",
    "BITBUCKET_TOKEN": ""
  }
}
```

---

### sequential-thinking

深度思考引擎。

**安装**：

```sh
claude mcp add mcp-sequentialthinking-tools -- npx -y mcp-sequentialthinking-tools
```

**场景**：复杂技术选型（微服务 vs 单体、数据库选型）、架构设计决策（分层、模块边界、扩展性）、疑难 bug 根因分析（多因素交叉、隐蔽逻辑）、性能优化策略规划。

**实战案例**："分析为什么我们的订单服务在高峰期会超时,考虑数据库、缓存、网络、并发锁、GC 等所有可能因素"

**效果**：会给出完整的推理链：假设 → 验证 → 排除 → 聚焦 → 验证 → 结论，而不是直接猜一个答案。

---

### memory

长期记忆。

**安装**：

```sh
claude mcp add memory -- npx -y @modelcontextprotocol/server-memory
```

**场景**：记住项目约定（命名规范、错误码、配置路径）、记住团队踩过的坑（某个库的 bug、某个配置的坑）、记住重要决策（为什么选这个方案、权衡了什么）。

**实战案例**：

```
你:"记住:我们的错误码统一用E开头+4位数字,数据库表名用snake_case,Redis key用冒号分隔"
(一周后)你:"帮我设计一个用户登录失败的错误码"
Claude自动调用记忆:"根据你们的规范,应该是E1001这样的格式..."
```

对 Claude 说：

```markdown
"用memory(MCP)记住我们团队的规范:

代码规范:
- 用ESLint + Prettier
- 命名用驼峰(变量)和帕斯卡(组件)

Git规范:
- commit格式:feat/fix/docs: 描述
- PR必须关联issue

技术栈:
- 前端:React 18 + TypeScript + Vite
- 后端:Node.js + Express + PostgreSQL
"
```

验证：下次问问题时，看 Claude 是否会自动调用这些规范。

---

### playwright

浏览器自动化。

```sh
claude mcp add playwright -- npx -y @executeautomation/playwright-mcp-server
```

**场景**：竞品监控、批量截图、自动化测试、数据抓取

**案例**："打开这 5 个竞品官网,截图首页和定价页,保存到 `./analysis/`"

---

### filesystem

本地文件操作。

```sh
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path/to/project
```

**场景**：读写配置、批量处理文件、项目初始化脚本

> [!warning] 注意
> 指定允许访问的路径，避免权限过大。

---

### github

GitHub 操作（需要官网 key）。需要设置 `GITHUB_TOKEN` 环境变量。

```sh
export GITHUB_PERSONAL_ACCESS_TOKEN="your_token_here"
claude mcp add github -- npx -y @modelcontextprotocol/server-github
```

---

### exa

智能搜索（需要官网 key），依赖 axios 包。

- GitHub：[exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server)
- Exa API Key：[https://dashboard.exa.ai/home](https://dashboard.exa.ai/home)

```sh
claude mcp add exa -e EXA_API_KEY="" -- npx -y exa-mcp-server
```

**场景**：需要搜索最新信息、技术博客、开源项目时，比普通搜索引擎更精准。

**优势**：

- **语义理解更强（Neural Search）**：你可以用自然语言描述你想要的内容（例如："找一篇关于 Transformer 架构的通俗易懂的教程"），它能理解"通俗易懂"和"教程"的含义，而不是只搜这两个词
- **返回结构化数据（Clean Data）**：传统搜索引擎返回的是充满了广告、SEO 废话和复杂 HTML 的网页。Exa 会清洗内容，直接返回**干净的文本**或**结构化数据**，这大大减少了 AI 处理杂乱信息的负担，减少了"幻觉"
- **强大的过滤功能**：它允许你按**域名**（如只搜 github.com）、**日期**、**内容类型**（如 PDF、代码）进行精确过滤
- **不仅是搜索，还能"内容相似推荐"**：你可以给它一个链接，让它找出"与这个网页内容相似的其他网页"，这对于做调研非常有用

---

### deepwiki

深度文档聚合。

```sh
claude mcp add deepwiki -- npx -y mcp-deepwiki
```

**场景**：聚合某个库的完整文档站点，比 context7 更全面但速度慢一些。

---

### drawio

> [!info] 仓库
> [jgraph/drawio-mcp](https://github.com/jgraph/drawio-mcp)

Draw.io 的这个 MCP 工具（`drawio-mcp`），走了一条非常聪明的路子。它不是自己在后台"画"一张图，而是**把 AI 生成的逻辑（Mermaid、CSV、XML）瞬间转换成 Draw.io 的专用链接**。

简单来说，流程变成了这样：

1. 你告诉 AI："画个 OAuth2 流程图"
2. AI 生成结构化数据
3. MCP 工具把数据压缩、编码
4. 浏览器自动弹出一个 Draw.io 编辑页面，图已经画好了，每一个节点都能拖、能改、能换色

根据 GitHub 上的官方文档，这个 MCP Server 目前支持三种核心模式：

- **Mermaid 转图 (`open_drawio_mermaid`)**：这是最常用的。AI 写 Mermaid 逻辑最强，Draw.io 负责渲染和二次编辑，绝配
- **CSV 转图 (`open_drawio_csv`)**：适合画组织架构图、网络拓扑图。你扔给 AI 一堆人员名单和汇报关系，它能瞬间生成树状图
- **XML 原生格式 (`open_drawio_xml`)**：如果你有现成的 Draw.io XML 数据，或者让 AI 学习了 XML 结构，可以直接生成最复杂的图表

**安装**：

```json
"mcpServers": {
  "drawio-mcp": {
    "command": "npx",
    "args": ["-y", "@drawio/mcp"],
    "env": {},
    "type": "stdio"
  }
}
```

**使用**：使用 draw.io MCP 工具 `open_drawio_mermaid` 制作展示 OAuth2 流程的时序图

**导出**：export 成 xml 格式，在 Confluence page 上创建一个 draw.io diagram

---

### 更多 MCP

- 官方列表：[modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)
- 社区精选：[wong2/awesome-mcp-servers](https://github.com/wong2/awesome-mcp-servers)（500+ 服务器持续更新，包括 Notion、Slack、Jira、数据库等各种集成）

---

## 配置文件一键添加 MCP

```json
{
  "mcpServers": {
    "atlassian": {
      "type": "stdio",
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "JIRA_URL",
        "-e", "JIRA_USERNAME",
        "-e", "JIRA_PERSONAL_TOKEN",
        "-e", "CONFLUENCE_URL",
        "-e", "CONFLUENCE_USERNAME",
        "-e", "CONFLUENCE_PERSONAL_TOKEN",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "JIRA_URL": "",
        "JIRA_USERNAME": "",
        "JIRA_PERSONAL_TOKEN": "",
        "CONFLUENCE_URL": "",
        "CONFLUENCE_USERNAME": "",
        "CONFLUENCE_PERSONAL_TOKEN": ""
      }
    },
    "bitbucket": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@zhanglc77/bitbucket-mcp-server"],
      "env": {
        "BITBUCKET_BASE_URL": "",
        "BITBUCKET_USERNAME": "",
        "BITBUCKET_TOKEN": ""
      }
    },
    "exa": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": {
        "EXA_API_KEY": "xxx"
      }
    },
    "sequential-thinking": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "mcp-sequential-thinking"]
    },
    "context7": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp", "--api-key", "xxx"]
    },
    "memory": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": ""
      }
    }
  }
}
```

---

## MCP 常用应用组合

| 场景 | 推荐组合 |
| --- | --- |
| 日常开发 | filesystem + github + memory |
| 深度工作 | sequential-thinking + context7 + memory |
| 自动化任务 | playwright + filesystem |
| 学习新技术 | context7 + deepwiki + exa（或 brave-search） |

---

# 二、Skills（技能）

Skills（技能）是自动触发的能力包，2025 年 10 月发布。

> [!info] 官方文档
> [Claude Code Skills](https://code.claude.com/docs/zh-CN/skills)

**和 MCP 的区别**：Skills 的范围更大，Skills 可以调用 MCP。Skills 还可以包含 Python 脚本，功能更灵活丰富。

简单说，**Skills 就是给 Claude 安装的"专业技能包"**。

**技术上**，一个 Skill 就是一个文件夹，里面包含技能的描述、相关脚本、示例代码等等。

比如你搞了一个 `SKILL.md` 文件，里面放了 AI 生成 PPT 固定流程的指令。你给 Claude 说：帮我生成 PPT，这个 Skill 就能激活。你就不需要每次都把你的要求写出来。

---

## 解决痛点

### 痛点 1：重复劳动

- **之前**：每次都像教小孩一样解释规则（"用现在时""50 字以内""说 what 和 why"）
- **现在**：打包成 Skill，说一句话自动应用

### 痛点 2：团队协作混乱

- **场景**：10 个人用 10 种方式让 Claude 生成文档，格式五花八门
- **解决**：
  1. 把 Skill 提交到项目代码库：`.claude/skills/company-doc-generator/`
  2. 团队成员 `git pull` 后自动同步
  3. 全员统一规范

### 痛点 3：知识无法沉淀

- **之前**：老员工调试 API 的技巧藏在脑子里
- **现在**：写成 Skill，新人克隆代码立刻获得团队智慧

---

## 渐进式披露机制

这个设计是 Skills 高效的核心：

- **初始加载**：Claude 只需记住每个 Skill 的元数据，包括：名称 + 描述，大概占几十个 Token
- **按需触发**：当你的请求匹配某个 Skill 的描述时，Claude 才会加载完整的指令和脚本
- **分模块读取**：复杂 Skill 可拆分多个文件，Claude 只会读取当前任务所需的部分

按照这种设计让你可以安装或者设计上百个 Skills，却不会占用大量上下文或影响交互的性能。

---

## 组成结构

一个 Skill 文件夹通常包含这几部分：

- **SKILL.md**：核心文件。用 YAML 写元数据（名字、描述），用 Markdown 写详细的指令，告诉 Claude 在什么情况下、以及如何使用这个 Skill
- **scripts/**：存放可执行的 Python、Shell 脚本
- **references/**：存放参考文档（如 API 文档、数据库 Schema、公司政策等），作为给 Claude 看的知识库
- **assets/**：存放资源文件（如 PPT 模板、Logo、项目脚架等），供 Claude 在执行任务时直接使用

---

## 安装

**手动安装**：

- 个人 Skills：`~/.claude/skills/`
- 项目 Skills：`.claude/skills/`
- 创建一个子目录和 skill 同名即可，在子目录中创建 `SKILL.md`

**Marketplace 安装**：

```sh
/plugin marketplace add anthropics/skills
/plugin
```

1. Select **Browse and install plugins**
2. Select **anthropic-agent-skills**
3. Select **document-skills or example-skills**
4. Select **Install now**

**打包与分享**：

Claude 可以打包 skill 变成一个 `xxx.skill` 文件，可以分享给其他人安装。

```sh
# 打包
python3 /path/to/skill-creator/scripts/package_skill.py \
  /path/to/your-skill \
  /output/path

# 安装
# 在 Claude Code 中：Install skill from /path/to/your-skill.skill
```

---

## 各种 Skill 推荐

### 官方 Skills仓库：
[anthropics/skills](https://github.com/anthropics/skills.git)

### 开源 Skills 仓库：

- 该项目收集了各种实用 Skill，采用模块化设计。比如文档处理、开发、数据分析、营销、写作创意啥的都有：[ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)、[BehiSecc/awesome-claude-skills](https://github.com/BehiSecc/awesome-claude-skills)
- 传统的 Claude Code Skill 需要你手动记忆和调用，而这个项目通过创新的钩子机制，实现了 Skill 的智能自动触发。当你输入提示或操作文件时，系统会自动分析上下文，并建议最相关的技能：[claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase)
- 开发者 @obra 觉得现在的 AI 写代码太随意了，所以他写了一组 Skills，**强迫** Claude 按照**世界级高级工程师**的标准流程来工作：[obra/superpowers](https://github.com/obra/superpowers)。装了之后，Claude 的模式就是：**收到需求 → 先头脑风暴 → 制定详细计划 → 写测试用例（TDD）→ 写代码通过测试 → 检查质量**
### 用 Skill 创建 Skill

Anthropic 官方有一个帮助创建 Skill 的 Skill：[skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
告诉 Claude Code 基于当前的 Skill 草稿，调用 skill-creator 来创建一个完整的 skill，名称为 xxx。

### Obsidian Skill

> [!info] 仓库地址
> [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)

obsidian-skills 直接把 Obsidian 专家集成在 Claude Code 里，仓库包含三个核心技能 Skill：

- **obsidian-markdown**：Obsidian 风格的 Markdown 书写，各种专有格式都支持
- **obsidian-bases**：`.base` 类数据库视图，支持过滤、公式、汇总
- **json-canvas**：`.canvas` 无限画布文件格式，可以实现点、连线、分组

**安装**：

```sh
/plugin marketplace add kepano/obsidian-skills
/plugin install obsidian@obsidian-skills
```



---

## Skills 实战案例

### 第一层：工程化单点突破（把说明书变技能包）

把最烦人的重复劳动自动化。少写废话提示词，让 Claude 自动识别场景。

#### 简单测试：Pre-commit Review

在 `.claude/skills/` 目录下创建 `pre-commit-check/SKILL.md`：

```markdown
# 名称
pre-commit-check

# 描述
代码提交前的标准检查:格式化、Lint、测试

# 触发
当用户提到"提交""commit""推送"时自动触发

# 执行逻辑
1、运行代码格式化
2、运行Lint检查
3、运行相关测试
4、生成检查报告

# 输出
分级报告:阻断问题、警告问题、通过项
```

#### 案例 1：智能代码审查

`smart-code-review`：

> [!success] 效果
> 以前代码审查靠人工挑毛病，经常遗漏关键问题。现在说"review 这个 PR"，自动按文件类型做专项检查，该找的坑一个不漏。团队线上事故率下降 60%。

```markdown
# 名称
smart-code-review

# 触发
当用户提到"review""审查""检查代码"或准备提交PR时

# 执行逻辑
1、分析变更文件类型和影响范围
2、根据文件类型选择检查项:
- API文件 → 检查鉴权、参数校验、错误处理、API文档
- 数据库迁移 → 检查索引、向后兼容、回滚脚本、性能影响
- 前端组件 → 检查无障碍、性能、状态管理、错误边界
- 配置文件 → 检查敏感信息泄露、环境变量、默认值安全性
3、调用对应SubAgent进行专项审查:
- security-auditor → SQL注入、XSS、CSRF等
- performance-engineer → N+1查询、大对象、内存泄漏
- frontend-developer → 重渲染、bundle大小、懒加载
4、汇总问题并按严重程度分级:
- 阻断级(安全漏洞、数据丢失风险)
- 警告级(性能隐患、可维护性问题)
- 建议级(优化空间、最佳实践)

# 输出
分级报告 + 修复建议 + 参考文档链接
```

#### 案例 2：依赖升级风险评估

`dependency-upgrade-check`：

> [!success] 效果
> 以前升级依赖全靠运气，升了才知道炸不炸。现在每次升级前先跑一遍评估，该注意的点全列出来，升级有底气。

~~~markdown
# 触发
检测到package.json/requirements.txt/go.mod等变更时

# 执行逻辑
1、识别新增、升级、删除的依赖
2、对每个变更依赖:
- 用github MCP查该库的changelog和breaking changes
- 用context7查新版本的API变化
- 扫描项目代码,找出使用该依赖的位置
- 评估影响面(多少文件、是否核心路径)
3、检查依赖树冲突(peerDependencies、版本兼容性)
4、查询CVE数据库,检查已知漏洞
5、生成升级checklist

# 输出
## 升级风险评估
- 高风险依赖(breaking changes多、使用面广)
- 中风险依赖(小改动、局部影响)
- 低风险依赖(bugfix、无API变化)

## 需要人工验证的点
[列出可能出问题的代码位置]

## 建议升级顺序
[从低风险到高风险,逐步验证]

## 回滚预案
[如果升级出问题,怎么快速回退]
~~~

---

### 第二层：编排型工作流（参数化 + 链式调用）

一个技能适配多项目，多个技能串成流水线。

#### 案例：生产事故应急响应

`incident-response`：

> [!success] 效果
> 以前线上出问题，团队一片慌乱，排查靠经验靠猜。现在说"线上订单服务挂了"，5 分钟内给出完整分析 + 3 套止损方案。平均故障恢复时间从 45 分钟降到 12 分钟。

~~~markdown
# 触发
用户说"线上出问题了""紧急""事故"等关键词

# 执行流程(自动并行+串行)
## 阶段1:快速止血(并行执行)
- 调用devops-troubleshooter → 分析日志、定位异常
- 调用performance-engineer → 检查资源使用、是否过载
- 调用database-optimizer → 检查慢查询、锁等待

## 阶段2:根因分析(基于阶段1结果)
- 如果是代码问题 → 调用debugger SubAgent
- 如果是配置问题 → 检查最近的配置变更
- 如果是依赖问题 → 检查上游服务状态
- 如果是资源问题 → 检查流量异常、是否被攻击

## 阶段3:止损方案(基于根因)
- 自动生成3个止损方案:
  1、 最快方案(回滚、降级、限流)
  2、 最稳方案(修复根因,重新发布)
  3、 临时方案(绕过问题点,保持可用)
- 对比每个方案的:恢复时间、风险、副作用

## 阶段4:执行确认
- 输出完整的执行命令和回滚命令
- 标注每步的预期结果和验证方式
- 等待人工确认后才执行

# 输出
## 事故摘要
影响范围、严重程度、开始时间、核心指标变化(错误率、延迟、可用性)

## 根因分析
详细分析,附日志/监控截图链接

## 止损方案对比
3个方案的完整对比表

## 执行清单
一步步操作指令,可复制执行

## 事后改进
如何预防类似问题再次发生
~~~

---

### 第三层：团队智能体（知识沉淀 + 自进化）

#### 案例：技术债追踪助手

> [!success] 效果
> 不再是"想起来就还"，而是每周有明确的 3 个小目标。结合 SonarQube 等专业工具，Skill 负责排优先级和生成报告。

`tech-debt-tracker`：

```markdown
# 名称
tech-debt-tracker

# 描述
每周帮助团队识别和追踪最重要的技术债

# 触发
用户提到"技术债""代码坏味道""重构计划"时

# 执行逻辑
1、集成SonarQube API,获取现有扫描结果
2、按影响面排序(修改频率高 + bug数多 = 优先级高)
3、生成本周TOP 3待还技术债清单
4、每项包含:位置、问题描述、建议方案、预估工作量

# 输出
Markdown周报:
- TOP 3技术债(本周建议优先处理)
- 已还技术债(上周完成的3项)
- 决策记录(为什么选这些,存入memory)
```

---

### 高级：版本治理 + 回滚

**目标**：把 Skills 当团队资产，能升级、能回退、可审计。

**落地做法**：

1. 小范围灰度两版，对比"查出率、耗时、误报率"
2. 确定没问题再全量，有问题立即回滚
3. 预期效果：两周内误报率从 18% 压到 6%

```
team-skills/
  code-review/
    v1.0.0/Skill.md
    v1.1.0/Skill.md
    v2.0.0/Skill.md  # 当前版本
```

---

# 三、Slash Commands（斜杠命令）

这是一个简单但极其好用的工具，用于手动标准化。

斜杠命令是手动触发的工作流快捷方式，存在 `.claude/commands/` 目录。

- **本质**：纯 Markdown 定义的多步骤流程，输入 `/命令名` 手动触发
- **API 注入**：作为用户消息扩展，而非系统提示工具（这是与 Skills 的核心区别）

命令内部可以：

- 调用 Skills 自动化检查
- 编排 SubAgents 并行工作
- 执行 MCP 工具链
- 串联 Git 操作

---

## Skills vs Slash Commands

| 对比项 | Skills | Slash Commands |
|--------|--------|---------------|
| 触发方式 | 自动（匹配用户意图） | 手动（`/命令名`） |
| 注入方式 | 作为 system prompt | 作为 user message |
| 适用场景 | 通用能力（代码审查、文档生成） | 固定流程（发版、回滚、入职） |
| 存放位置 | `.claude/skills/` | `.claude/commands/` |

---

## 典型场景

1. `/release` — 完整发版流程（测试 → 构建 → 打 tag → 发布 → 通知）
2. `/security-check` — 安全扫描（依赖漏洞 + 代码审计 + 配置检查）
3. `/perf-audit` — 性能审计（包体积 + 加载时间 + 运行时分析）
4. `/refactor-plan` — 重构规划（架构分析 + 影响评估 + 迁移方案）
5. `/onboard` — 新人入职（克隆仓库 + 环境配置 + 文档导览）
6. `/rollback` — 紧急回滚

---

## 使用示例

### 示例 1：版本发布

**定义命令**：建文件 `.claude/commands/release.md`

```markdown
# 版本发布流程

1、拉最新代码确认版本号
2、触发Skills检查:代码审查、完整测试、资源检查
3、生成changelog
4、预发布测试
5、人工确认
6、正式发布
7、发通知
```

**使用**：直接输入 `/release`

**效果**：整个团队按统一流程走,不会漏步骤。版本发布出错率从 15% 降到 0。

### 示例 2：带确认步骤的发版

在 `.claude/commands/` 目录下创建 `release.md`：

```markdown
# 版本发布流程
你是发布助手,帮助用户安全发布版本。

## 执行步骤
1、确认当前Git分支是main
2、拉取最新代码(git pull)
3、触发Skills:
- pre-commit-check(代码质量)
- test-coverage-check(测试覆盖率>80%)
4、询问版本号(major.minor.patch)
5、生成changelog(基于Git commit)
...

## 每步都需要用户确认
不要自动执行,每步输出命令,等用户确认。
```

验证：输入 `/release`，看是否触发完整流程。

---

# 四、Plugin（插件）

Plugin（插件）是应用级打包容器，用来打包其他四个工具。

一个 Plugin 可以包含：

| 组成 | 数量上限 |
|------|---------|
| Skills | 5 |
| Slash Commands | 10 |
| MCP 服务器 | 3 |
| SubAgents | 2 |
| Hooks | 若干 |

## 适合场景

1. 团队标准化工具打包、快速分享工作流、一键安装完整套件
2. 临时用一次，快速试试某个功能

## 缺点

装太多会卡，而且大部分功能都重复。

> [!tip] 建议
> 个人用全局配置，团队用 Plugins 打包分发。别超过 3 个，够用就行。

---

## 开源 Plugin 推荐

### andrej-karpathy-skills（⭐ 46.5K）

> [!info] 仓库
> [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) — 仅 2.3K 的 CLAUDE.md 文件，GitHub 全球热榜，46.5K 星。

这个项目把 Andrej Karpathy 观察到的 LLM 编程三大祖传毛病，浓缩成 4 条行为准则，写进 CLAUDE.md 让 Claude Code "乖乖听话"。

**LLM 编码三大痛点**：

1. **默默做错误假设**：不确定的地方不问你，自己猜，猜完接着写，bug 就埋进去了
2. **把简单问题复杂化**：50 行能搞定的事，整出 200 行抽象 API
3. **乱改不相干的代码**：让它修一个函数，它顺便把隔壁的注释删了，格式也"优化"了

**四条核心原则**：

| 原则 | 要点 |
|------|------|
| **Think Before Coding** | 不确定就问，不要闷头猜。主动说"这里我假设了 X，你确认吗" |
| **Simplicity First** | 不加没人要求的功能，不为只用一次的代码建抽象，200 行能写成 50 行就重写 |
| **Surgical Changes** | 只动必须改的地方，不"顺便优化"相邻代码，不重构没坏的东西 |
| **Goal-Driven Execution** | 给目标而非命令。"添加验证" → "为无效输入写测试，然后让它们通过" |

**效果判断标准**：
- PR 的 diff 变干净了，没有莫名其妙的格式改动
- 代码第一次就足够简单，不用返工
- Claude 开始在动手之前先问问题
- PR 不再附带一堆"顺手重构"

**安装**：

```sh
# 方式一：Plugin 安装（全局生效）
/plugin marketplace add forrestchang/andrej-karpathy-skills
/plugin install andrej-karpathy-skills@karpathy-skills

# 方式二：单个项目生效（下载到项目根目录）
curl -o CLAUDE.md https://raw.githubusercontent.com/forrestchang/andrej-karpathy-skills/main/CLAUDE.md

# 方式三：追加到已有 CLAUDE.md
echo "" >> CLAUDE.md
curl https://raw.githubusercontent.com/forrestchang/andrej-karpathy-skills/main/CLAUDE.md >> CLAUDE.md
```

### wshobson/agents

最大的 Claude Code Plugin Marketplace，详见 [[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams#开源 Agents 推荐|多智能体协作 — 开源 Agents 推荐]]。

```sh
/plugin marketplace add wshobson/agents
/plugin install <plugin-name>@claude-code-workflows
```
