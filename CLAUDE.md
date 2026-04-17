---
title: Learning Notes LLM Wiki Schema
tags:
  - knowledgebase/schema
date: 2026-04-17
---

# Learning Notes LLM Wiki Schema

> 本文件是知识库的核心规约，定义三层架构、目录结构、页面模板和操作流程。
> 人类与 LLM 共同演进此文件。

---

## 三层架构

| 层级 | 说明 | 所有权 | 规则 |
|------|------|--------|------|
| **Raw Sources（原始来源）** | 顶层主题目录中的 markdown 文件（AI/、Azure/、Docker-Kubernetes/ 等） | 人类策划 | **只读不改**。LLM 永远不修改、不移动、不删除这些文件 |
| **Wiki（编译知识层）** | `KnowledgeBase/` 目录下的所有内容 | LLM 拥有 | LLM 创建、更新、维护所有页面和交叉引用 |
| **Schema（规约文件）** | 本文件 `CLAUDE.md` | 人类与 LLM 共同演进 | 定义结构约定和工作流程 |

---

## 目录结构

```
learning-notes/                    ← Obsidian vault, git 仓库
├── CLAUDE.md                      ← 本文件（Schema 层）
│
├── AI/                            ← Raw Source（只读）
├── Aliyun/                        ← Raw Source（只读）
├── Azure/                         ← Raw Source（只读）
├── C++/                           ← Raw Source（只读）
├── CloudComputing/                ← Raw Source（只读）
├── Database/                      ← Raw Source（只读）
├── Docker-Kubernetes/             ← Raw Source（只读）
├── Git/                           ← Raw Source（只读）
├── Go/                            ← Raw Source（只读）
├── GPU-DeepLearning/              ← Raw Source（只读）
├── HPC/                           ← Raw Source（只读）
├── IaC/                           ← Raw Source（只读）
├── Linux-Shell/                   ← Raw Source（只读）
├── Middlewares/                   ← Raw Source（只读）
├── Networking/                    ← Raw Source（只读）
├── OS/                            ← Raw Source（只读）
├── Python/                        ← Raw Source（只读）
├── SoftwareTesting/               ← Raw Source（只读）
│
└── KnowledgeBase/                 ← Wiki 编译层（LLM 维护）
    ├── index.md                   ← 全 wiki 内容目录（面向内容）
    ├── log.md                     ← 操作日志（面向时间线，仅追加）
    ├── sources/                   ← 原始来源摘要页
    ├── concepts/                  ← 概念页（抽象概念）
    ├── entities/                  ← 实体页（工具、平台、项目）
    ├── maps/                      ← 主题地图（MOC, Map of Content）
    ├── analysis/                  ← 分析与综述
    ├── inventory/                 ← 文档盘点
    └── maintenance/               ← 维护报告
```

---

## 页面规约

### Frontmatter 规范

所有 wiki 页面必须包含以下 YAML frontmatter：

```yaml
---
title: 页面标题
tags:
  - knowledgebase/<type>   # type: concept | entity | source | map | analysis
  - <domain>/<topic>       # 领域标签
date: YYYY-MM-DD           # 创建或最后重大更新日期
sources:                   # 引用的原始来源文档（来源摘要页可省略此字段）
  - "[[原始文档路径]]"
aliases:
  - 别名1
---
```

### 链接格式

- **必须使用 Obsidian wikilink 格式**：`[[KnowledgeBase/concepts/页面名]]` 或 `[[KnowledgeBase/entities/页面名|显示名]]`
- **引用原始来源**：`[[Docker-Kubernetes/docker/docker基础]]`
- **禁止使用**：相对路径 markdown 链接 `[text](../path.md)`

### 概念页模板（concepts/）

适用于抽象概念：可观测性、CI/CD、服务网格、容器运行时等。

```markdown
# 概念名

## 定义
一段精炼的定义（2-3 句话）

## 核心要点
- 要点 1（从原始来源提炼的关键知识）
- 要点 2
- 要点 3

## 与其他概念的关系
- [[KnowledgeBase/concepts/相关概念A]]：关系描述
- [[KnowledgeBase/entities/相关实体B]]：关系描述

## 在本仓库中的覆盖
- [[原始文档1]]：简述该文档覆盖了本概念的哪个方面
- [[原始文档2]]：简述

## 知识空白
- 尚未覆盖的方面 1
- 尚未覆盖的方面 2
```

### 实体页模板（entities/）

适用于具体工具/平台/项目：Docker、Kubernetes、ArgoCD、Prometheus 等。

```markdown
# 实体名

## 简介
一段精炼的简介（是什么、解决什么问题）

## 核心功能
- 功能 1：简述
- 功能 2：简述

## 使用场景
- 场景 1
- 场景 2

## 相关概念与实体
- [[KnowledgeBase/concepts/相关概念]]：关系描述
- [[KnowledgeBase/entities/相关实体]]：关系描述

## 在本仓库中的覆盖
- [[原始文档1]]：简述
- [[原始文档2]]：简述

## 知识空白
- 尚未覆盖的方面
```

### 来源摘要页模板（sources/）

每篇原始来源文档对应一个摘要页。

```markdown
# 来源标题

## 元信息
- **原始文档**：[[原始文档路径]]
- **领域**：领域名
- **摄入日期**：YYYY-MM-DD

## 摘要
2-5 句话概括文档的核心内容

## 关键知识点
1. 知识点 1（可直接复用的事实或结论）
2. 知识点 2
3. 知识点 3

## 涉及的概念与实体
- [[KnowledgeBase/concepts/概念A]]
- [[KnowledgeBase/entities/实体B]]

## 值得注意
- 特别有价值的内容、独特观点、或与其他来源的矛盾
```

---

## 操作流程

### Ingest（摄入）

当新的原始来源文档被添加到仓库时：

1. **阅读**原始来源文档，理解其内容
2. 在 `sources/` **写摘要页**（按来源摘要页模板）
3. **更新或创建**相关 `concepts/` 和 `entities/` 页面
   - 如果概念/实体页已存在：补充新知识点、更新"在本仓库中的覆盖"
   - 如果不存在且该概念/实体足够重要（≥3 篇文档提及）：创建新页面
4. **更新** `maps/` 中的相关地图
5. **更新** `index.md`
6. 在 `log.md` **追加条目**

### Query（查询）

对 wiki 提问时：

1. 读 `index.md` 定位相关页面
2. 读取相关 wiki 页面（concepts/、entities/、sources/）
3. 综合回答并附引用
4. 如果回答有分析价值，**归档为新页面**到 `analysis/`

### Lint（健康检查）

定期检查 wiki 健康度：

1. **断链检查**：所有 wikilink 是否指向存在的文件
2. **孤儿页检查**：无入链的页面
3. **概念覆盖检查**：被多个页面提及但没有独立页面的重要概念
4. **一致性检查**：页面间矛盾的信息
5. **时效性检查**：sources/ 摘要与原始文档是否一致
6. **交叉引用检查**：缺失的 wikilink
7. 在 `log.md` 记录 lint 结果

---

## index.md 规范

index.md 是全 wiki 的目录页，按类别组织所有页面，每页一行，格式：

```
- [[KnowledgeBase/类别/页面名|显示名]] — 一句话摘要
```

按以下分类组织：概念页、实体页、来源摘要、主题地图、分析报告、维护报告。

---

## log.md 规范

仅追加的操作日志，格式：

```markdown
## [YYYY-MM-DD] 操作类型 | 主题

- 描述具体做了什么
- 影响了哪些页面
```

操作类型：`ingest`、`query`、`lint`、`restructure`、`create`、`update`
