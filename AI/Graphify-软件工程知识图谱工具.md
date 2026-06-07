---
title: "Graphify：软件工程知识图谱工具"
source: "https://mp.weixin.qq.com/s/yG2JXr3AWFIdRzNDG7a70w"
created: 2026-06-07
tags:
  - AI/tools
  - knowledge-graph
  - code-understanding
---

# Graphify：软件工程知识图谱工具

## 为什么 AI 编程需要知识图谱

AI 编程助手的常见工作流程：把项目文件交给模型 → 提问 → 模型读代码、找线索、拼上下文。下次换个问题，又重新读一遍、重新找一遍。

小项目还好，项目复杂起来后这种方式很快吃力——代码在 `src/`、设计文档在 `docs/`、历史讨论在 Markdown、论文/截图/视频散落各处。资料很多，**真正缺的是它们之间的关联**。

更实用的做法是让 AI 不停留在"读到更多文件"这一步，还能顺着项目里的关系继续查下去：

- 一个认证流程到底经过了哪些模块？
- 某个配置类影响了哪些服务？
- 当前代码为什么会这样设计？有没有对应的设计说明？
- 哪些论文、文档、视频和这个模块有关？

变化的核心是从"检索文件"走向"查询关系"。

## 简介

Graphify 将项目中的代码、文档、PDF、图片、视频等分散资料整理成一张**可查询的软件工程知识图谱**。可以理解为一层"**项目记忆**"——Graphify 先读取项目，把代码结构、文档、设计思路和外部资料组织起来。之后 AI 再回答问题时，就不用每次从头翻文件，而是能沿着已有关系继续查找和推理。

GitHub：https://github.com/safishamsi/graphify

## 核心机制

### 处理方式

```
代码 → 本地 AST 解析（tree-sitter，无 API 成本）
文档 / PDF / 图片 / 视频 → AI 模型语义提取
最终 → 合并成一张知识图谱
```

### 输出文件

```
graphify-out/
├── graph.html       # 浏览器可视化图谱
├── GRAPH_REPORT.md  # 项目总结与关系分析
└── graph.json       # 完整结构化图谱
```

- **graph.html**：给人看的。浏览器打开，查看节点和关系，快速建立整体印象
- **GRAPH_REPORT.md**：给人和 AI 一起看的"导读"。总结关键概念、高连接度节点、值得注意的关系，以及这张图谱适合回答的问题
- **graph.json**：更底层的结构化产物。后续查询、路径追踪、MCP 接入、图谱合并都围绕它展开

### 置信度标记

每条关系标注来源和可靠程度：

| 标签 | 含义 |
|------|------|
| `EXTRACTED` | 直接从文件中提取 |
| `INFERRED` | 基于上下文推断 |
| `AMBIGUOUS` | 存在歧义，需人工确认 |

## 安装

环境要求：Python 3.10+

```bash
# 推荐安装方式（PyPI 包名是 graphifyy，两个 y）
uv tool install graphifyy
# 或
pipx install graphifyy

# 注册到 AI 编程助手
graphify install

# 指定平台
graphify install --platform codex
graphify cursor install
graphify vscode install
```

支持平台：Claude Code、Codex、OpenCode、Cursor、Gemini CLI、GitHub Copilot CLI、VS Code Copilot Chat、Aider、Kimi Code、Kiro、Trae 等。

**Codex 用户注意**：使用 `$graphify` 而非 `/graphify`，且需在 `~/.codex/config.toml` 的 `[features]` 下开启：

```toml
multi_agent = true
```

**Windows PowerShell 注意**：PowerShell 会把开头的 `/` 当路径分隔符，不要写 `/graphify .`，直接在终端运行 `graphify .`。

## 常用查询方式

生成图谱只是第一步。更常用的场景是围绕这张图继续提问。与 grep 的区别：grep 找"关键词在哪"，Graphify 追"模块/概念/文档之间怎么连起来"。

### 接手陌生项目的典型流程

```bash
# 第一步：生成图谱
/graphify .

# 第二步：先读报告（项目图谱的"导读"）
# 打开 graphify-out/GRAPH_REPORT.md

# 第三步：围绕关键模块追问
/graphify query "show the auth flow"
```

### 查询命令

```bash
# 生成图谱
/graphify .          # AI 助手内
graphify .           # 终端

# 查询关系
/graphify query "what connects auth to the database?"

# 追踪路径
/graphify path "UserService" "DatabasePool"

# 解释节点
/graphify explain "RateLimiter"
```

如果已有 `graph.json`，也可以从终端直接查询：

```bash
graphify query "what connects DigestAuth to Response?" --graph graphify-out/graph.json
```

### 更新与导出

```bash
# 增量更新（只更新变化文件，不全量重跑）
/graphify ./docs --update

# 只重新聚类，不重新抽取内容
/graphify . --cluster-only

# 不生成 HTML（大项目节省时间）
/graphify . --no-viz

# 生成 Markdown wiki
/graphify . --wiki

# 导出可读架构和调用流页面（适合团队内部项目讲解）
graphify export callflow-html
```

## 纳入外部资料

```bash
# 论文
/graphify add https://arxiv.org/abs/1706.03762

# YouTube 视频（转录后加入）
/graphify add <youtube-url>
```

## 可选扩展（Extras）

| Extra | 能力 | 安装 |
|-------|------|------|
| `pdf` | PDF 提取 | `pip install "graphifyy[pdf]"` |
| `office` | .docx/.xlsx | `pip install "graphifyy[office]"` |
| `video` | 视频/音频转录 | `pip install "graphifyy[video]"` |
| `mcp` | MCP stdio server | `pip install "graphifyy[mcp]"` |
| `neo4j` | 推送到 Neo4j | `pip install "graphifyy[neo4j]"` |
| `ollama` | 本地 Ollama 推理 | `pip install "graphifyy[ollama]"` |
| `openai` | OpenAI 或兼容 API | `pip install "graphifyy[openai]"` |
| `sql` | SQL schema 抽取 | `pip install "graphifyy[sql]"` |

## MCP Server 模式

```bash
python -m graphify.serve graphify-out/graph.json
```

提供结构化访问能力：`query_graph`、`get_node`、`get_neighbors`、`shortest_path`。

## 团队协作

```bash
# 提交图谱到 git（团队共享）
git add graphify-out/

# .gitignore 排除本地化文件
# graphify-out/manifest.json
# graphify-out/cost.json

# .graphifyignore 排除不需要的文件
# node_modules/
# dist/

# 安装 git hook，commit 后自动重建图谱
graphify hook install

# 合并多个图谱
graphify merge-graphs a.json b.json
```

## 隐私与成本

- **代码文件**：通过 tree-sitter 本地处理，不离开机器
- **视频/音频**：可通过 faster-whisper 本地转录
- **文档/PDF/图片**：通常需发送给 AI 模型做语义提取——企业项目需确认数据边界
- 环境变量配置后端：`ANTHROPIC_API_KEY`（Claude）、`OPENAI_API_KEY`、`OLLAMA_BASE_URL`（本地）等

## 使用注意

- 图谱质量取决于输入质量（代码命名混乱、文档过时会被带入图谱）
- `INFERRED` 和 `AMBIGUOUS` 关系不能直接当结论用，需人工复核
- 与 grep 的区别：grep 找"关键词在哪"，Graphify 追"模块/概念/文档之间怎么连起来"
