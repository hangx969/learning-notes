---
title: 基于 Karpathy LLM Wiki 模式改造知识库
tags:
  - ai/workflow
  - knowledgebase/methodology
date: 2026-04-16
---

# 基于 Karpathy LLM Wiki 模式改造知识库

## 一、Karpathy 的核心规则总结

> 来源：[karpathy/llm-wiki.md](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)

### 核心理念

传统 RAG 方式（上传文档 → 查询时检索 chunk → 生成回答）的问题：**每次查询都从零发现知识，没有积累**。

LLM Wiki 的做法完全不同：**LLM 增量构建并维护一个持久化的 wiki**——一组结构化、互相链接的 markdown 文件，位于你和原始资料之间。每当新资料进入，LLM 不是简单索引，而是阅读、提取关键信息、整合到现有 wiki 中——更新实体页、修订主题摘要、标注新旧数据的矛盾、强化或挑战已有综述。知识被**编译一次，持续更新**，而非每次查询重新推导。

**你永远（或几乎）不自己写 wiki——LLM 写并维护全部内容。你负责：策划来源、探索方向、提出好问题。LLM 负责：总结、交叉引用、归档和簿记。**

比喻：Obsidian 是 IDE；LLM 是程序员；wiki 是代码库。

### 三层架构

| 层级 | 说明 | 所有权 |
|------|------|--------|
| **Raw Sources（原始来源）** | 文章、论文、图片、数据文件。**不可变**，LLM 只读不改。这是你的事实来源。 | 人类策划 |
| **Wiki（编译知识层）** | LLM 生成的 markdown 文件目录：摘要、实体页、概念页、对比、综览、综述。LLM 完全拥有此层，创建页面、更新、维护交叉引用、保持一致性。 | LLM 拥有 |
| **Schema（规约文件）** | 一份文档（如 `CLAUDE.md`）告诉 LLM wiki 的结构约定、工作流程。这是核心配置文件——让 LLM 成为有纪律的 wiki 维护者而非通用聊天机器人。 | 人类与 LLM 共同演进 |

### 三大操作

#### 1. Ingest（摄入）

新来源放入原始资料集，指示 LLM 处理：
- 阅读来源，讨论关键要点
- 在 wiki 中写摘要页
- 更新索引
- 更新相关实体页和概念页（单个来源可能触及 10-15 个 wiki 页面）
- 在日志中追加条目

#### 2. Query（查询）

对 wiki 提问。LLM 搜索相关页面、阅读、综合回答并附引用。**好的回答应被归档回 wiki 作为新页面**——你的探索也在知识库中复利积累。

#### 3. Lint（健康检查）

定期要求 LLM 检查 wiki 健康度：
- 页面间矛盾
- 被新来源取代的过时声明
- 无入链的孤儿页面
- 被提及但缺少独立页面的重要概念
- 缺失的交叉引用
- 可通过搜索填补的数据空白

### 索引与日志

| 文件 | 用途 | 特点 |
|------|------|------|
| `index.md` | **面向内容**。wiki 中所有页面的目录——链接 + 一行摘要 + 元数据。按类别组织。 | LLM 每次摄入时更新。查询时先读索引定位相关页面。 |
| `log.md` | **面向时间线**。仅追加的操作记录——摄入、查询、lint。 | 条目格式如 `## [2026-04-16] ingest \| 文章标题`，便于 grep 解析。 |

---

## 二、现有知识库现状分析

### 现有结构

```
learning-notes/          ← Obsidian vault, git 仓库
├── AI/                  ← 16 篇（AI 工具、提示词、Claude Code）
├── Aliyun/              ← 19 篇（阿里云）
├── Azure/               ← 21 篇
├── C++/                 ← 1 篇
├── CloudComputing/      ← 7 篇
├── Database/            ← 3 篇
├── Docker-Kubernetes/   ← 145 篇（最大领域）
├── Git/                 ← 2 篇
├── Go/                  ← 9 篇
├── GPU-DeepLearning/    ← 4 篇
├── HPC/                 ← 7 篇
├── IaC/                 ← 2 篇
├── Linux-Shell/         ← 24 篇
├── Middlewares/         ← 3 篇
├── Networking/          ← 2 篇
├── OS/                  ← 3 篇
├── Python/              ← 27 篇
├── SoftwareTesting/     ← 少量
├── KnowledgeBase/       ← 已有初步编译层（index、maps、concepts、analysis）
└── .claude/             ← Claude Code skills
```

- **总计约 350 篇 markdown 文档，17 个主题领域**
- 已有 `KnowledgeBase/` 目录做了初步编译（INDEX.md、domain-map、概念页等），但未按 LLM Wiki 模式设计
- 现有文档既是"原始来源"也是"知识页"，角色未分离

### 与 Karpathy 模式的差距

| 维度 | Karpathy 模式 | 当前状态 | 差距 |
|------|--------------|---------|------|
| 原始来源不可变性 | raw/ 目录只读 | 无 raw/，笔记随时可编辑 | 需明确原始来源层 |
| wiki 编译层 | LLM 生成的结构化 wiki 目录 | KnowledgeBase/ 有雏形但不完整 | 需扩充为完整 wiki 层 |
| Schema 文件 | CLAUDE.md 定义结构和工作流 | 无专门 schema | 需创建 |
| index.md | 全 wiki 目录，每页一行摘要 | KnowledgeBase/INDEX.md 有但粒度粗 | 需细化 |
| log.md | 仅追加操作日志 | 不存在 | 需创建 |
| Ingest 流程 | 标准化：读源→写摘要→更新索引→更新实体/概念页 | 无标准流程 | 需定义 |
| Query 归档 | 好答案归档回 wiki | 不存在 | 需定义 |
| Lint 流程 | 定期检查矛盾、孤儿页、缺失概念 | maintenance/ 有断链报告 | 需扩展 |
| 交叉引用 | 系统化的 `[[wikilink]]` 网络 | 部分存在但不系统 | 需加强 |

---

## 三、改造行动计划

### 原则

1. **不动现有文档**：现有 350 篇笔记视为 Raw Sources（原始来源层），保持不可变
2. **KnowledgeBase/ 作为 Wiki 层**：LLM 在此生成和维护所有编译内容
3. **渐进式改造**：不需要一步到位，先建立骨架，再逐步摄入
4. **LLM 做重活**：所有 wiki 页面由 LLM 编写和维护

### Phase 0：建立 Schema（Day 1）

**目标**：创建 `CLAUDE.md`，定义 wiki 的结构规约和操作流程。

Schema 应包含以下内容：

```markdown
# Learning Notes LLM Wiki Schema

## 目录结构
- 原始来源层：顶层各主题目录（AI/, Azure/, Docker-Kubernetes/ 等）
  - 只读，LLM 不修改这些文件
- Wiki 编译层：KnowledgeBase/
  - maps/        — 主题地图（MOC, Map of Content）
  - concepts/    — 概念页（技术概念的独立页面）
  - entities/    — 实体页（工具、平台、项目的独立页面）
  - sources/     — 原始来源摘要页（每篇原始文档对应一个摘要）
  - analysis/    — 分析与综述
  - maintenance/ — 维护报告
  - index.md     — 全 wiki 内容目录
  - log.md       — 操作日志

## 页面规约
- 每页必须有 YAML frontmatter：title, tags, date, sources（引用的原始文档）
- 使用 Obsidian wikilink 格式 [[path/file|显示名]]
- 概念页结构：定义 → 核心要点 → 与其他概念的关系 → 来源引用
- 实体页结构：简介 → 核心功能 → 使用场景 → 相关概念 → 来源引用

## 操作流程
### Ingest
1. 读取原始来源文档
2. 在 sources/ 写摘要页
3. 更新或创建相关 concepts/ 和 entities/ 页面
4. 更新 maps/ 中的相关地图
5. 更新 index.md
6. 在 log.md 追加条目

### Query
1. 读 index.md 定位相关页面
2. 读取相关 wiki 页面
3. 综合回答
4. 如果回答有价值，归档为新页面

### Lint
1. 检查断链和孤儿页
2. 检查概念间矛盾
3. 检查过时内容
4. 建议缺失的概念页或交叉引用
```

### Phase 1：调整 Wiki 目录结构（Day 1-2）

**目标**：在现有 `KnowledgeBase/` 基础上补齐目录。

- [ ] 创建 `KnowledgeBase/sources/` 目录（原始来源摘要页存放处）
- [ ] 创建 `KnowledgeBase/entities/` 目录（工具/平台实体页存放处）
- [ ] 创建 `KnowledgeBase/log.md`（操作日志）
- [ ] 重构 `KnowledgeBase/index.md`，按 sources / concepts / entities / maps / analysis 分类

### Phase 2：按领域优先级摄入原始来源（Day 3-14）

按成熟度和篇数排序，优先摄入核心领域：

| 批次 | 领域 | 篇数 | 优先级 | 说明 |
|------|------|------|--------|------|
| 1 | Docker-Kubernetes | 145 | 🔴 最高 | 核心专业领域，最大知识量 |
| 2 | Azure | 21 | 🔴 高 | 工作相关云平台 |
| 3 | Aliyun | 19 | 🔴 高 | 工作相关云平台 |
| 4 | Python | 27 | 🟡 中 | 运维开发语言 |
| 5 | Linux-Shell | 24 | 🟡 中 | 基础运维能力 |
| 6 | AI | 16 | 🟡 中 | AI 工具使用 |
| 7 | 其余领域 | ~50 | 🟢 低 | Go、HPC、IaC、DB 等 |

每个领域的摄入流程（以 Claude Code 会话执行）：

```
请摄入 Docker-Kubernetes/k8s-basic-resources/ 目录中的所有文档：
1. 逐篇阅读，在 KnowledgeBase/sources/ 写摘要页
2. 提取关键概念，创建或更新 KnowledgeBase/concepts/ 页面
3. 提取关键实体（工具/平台），创建或更新 KnowledgeBase/entities/ 页面
4. 更新 KnowledgeBase/maps/kubernetes-map.md
5. 更新 KnowledgeBase/index.md
6. 在 KnowledgeBase/log.md 追加记录
```

### Phase 3：建立 Lint 机制（Day 14+）

- [ ] 每周执行一次 lint 检查 prompt：

```
请对 KnowledgeBase/ 执行健康检查：
1. 检查所有 wikilink 是否有效（断链报告）
2. 找出无入链的孤儿页面
3. 找出在多个页面中被提到但没有独立页面的重要概念
4. 检查 sources/ 摘要与原始文档是否一致（是否有过时内容）
5. 建议缺失的交叉引用
6. 在 log.md 记录本次 lint
```

### Phase 4：Query 归档习惯（持续）

建立习惯：当在 Claude Code 会话中产生有价值的分析或对比时，将其归档到 wiki：

```
请将刚才的分析归档到 KnowledgeBase/analysis/[主题].md，
并更新 index.md 和相关概念页的交叉引用。
```

---

## 四、实用工具建议

| 工具 | 用途 |
|------|------|
| **Obsidian Graph View** | 可视化 wiki 连接结构，发现孤儿页和 hub 页 |
| **Obsidian Web Clipper** | 浏览器扩展，将网页文章转为 markdown 存入 raw 层 |
| **Obsidian Dataview** | 查询 frontmatter，生成动态表格和列表 |
| **qmd** | 本地 markdown 搜索引擎（BM25 + 向量混合搜索），wiki 增长后替代 index.md |
| **git** | wiki 本身就是 git 仓库，天然有版本历史、分支和协作能力 |

---

## 五、预期成果

改造完成后，知识库将具备：

1. **清晰的三层分离**：原始笔记（只读）→ wiki 编译层（LLM 维护）→ schema（共同演进）
2. **知识复利**：每次摄入新来源都会丰富已有的概念网络，而非孤立存放
3. **高效查询**：通过 index.md 和结构化的 wiki 页面，LLM 能快速定位和综合回答
4. **维护成本近零**：LLM 处理所有交叉引用更新、一致性维护、日志记录
5. **可视化知识图谱**：Obsidian Graph View 展示概念间关联

---

## 六、快速启动 Prompt

将以下内容复制到 `CLAUDE.md` 或作为 Claude Code 会话的起始指令：

```markdown
你是这个 Obsidian 知识库的 wiki 维护者。

## 规则
1. 顶层主题目录（AI/, Azure/, Docker-Kubernetes/ 等）是原始来源，只读不改
2. KnowledgeBase/ 是你的工作区，所有编译内容在此创建和维护
3. 每次操作后更新 KnowledgeBase/index.md 和 KnowledgeBase/log.md
4. 使用 Obsidian wikilink 格式 [[path|显示名]] 建立交叉引用
5. 每个 wiki 页面必须有 YAML frontmatter（title, tags, date, sources）
6. 标注与已有知识矛盾的新信息

## 可用操作
- `/ingest [路径]` — 摄入指定来源，写摘要，更新相关页面
- `/query [问题]` — 从 wiki 中回答问题，必要时创建新页面
- `/lint` — 全 wiki 健康检查
- `/status` — 报告 wiki 当前规模和最近操作
```
