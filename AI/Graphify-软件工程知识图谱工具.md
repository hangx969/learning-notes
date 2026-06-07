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

## 简介

Graphify 将项目中的代码、文档、PDF、图片、视频等分散资料整理成一张**可查询的软件工程知识图谱**。核心价值是从"检索文件"走向"查询关系"——AI 不再每次从头翻文件，而是沿着已有关系继续查找和推理。

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
├── graph.html       # 浏览器可视化图谱（给人看）
├── GRAPH_REPORT.md  # 项目总结与关系分析（给人和 AI 一起看）
└── graph.json       # 完整结构化图谱（供查询/MCP/合并）
```

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

支持平台：Claude Code、Codex、Cursor、Gemini CLI、GitHub Copilot CLI、VS Code Copilot、Aider、Kimi Code、Kiro、Trae 等。

## 基本使用

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

# 增量更新（不全量重跑）
/graphify ./docs --update

# 只重新聚类
/graphify . --cluster-only

# 不生成 HTML
/graphify . --no-viz

# 生成 Markdown wiki
/graphify . --wiki

# 导出可读架构页面
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
