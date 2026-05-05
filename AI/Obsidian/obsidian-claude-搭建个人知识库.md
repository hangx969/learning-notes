---
title: Obsidian + Claude Code 搭建 AI 知识库
tags:
  - AI
  - obsidian
  - claude
  - knowledge-management
aliases:
  - Obsidian AI 知识库
  - Claude Code Obsidian 集成
date: 2026-04-16
---

# Obsidian + Claude Code 搭建 AI 知识库

## 知识库类软件的现状

当前市面上的知识库软件大致可以分为三类，各有不足：

| 类型 | 代表产品 | 优势 | 不足 |
| --- | --- | --- | --- |
| 传统笔记 | 语雀、印象笔记 | 整理、记录、协作齐全 | ==没有 AI==，知识存进去就"死"了 |
| AI + 知识库 | 腾讯 IMA、秘塔 AI 搜索 | 能上传文档做问答 | 更像内容聚合社区，产出形式受限 |
| 纯 AI 工具 | 元宝、豆包、Kimi | AI 能力强，写作/总结/翻译 | ==没有本地知识库==，知识无法沉淀 |

> [!summary] 核心矛盾
> 要么没脑子，要么没记忆，要么有脑子有记忆但==不是你的==。

---

## 为什么选 Obsidian？

[Obsidian](https://obsidian.md) 在海外已有 ==150 万月活用户==，开发者、研究者、写作者用得特别多。

> [!info] 关于 Obsidian 公司
> - 完全没有接受风投，全靠用户付费
> - 年收入约 **2500 万美元**，续费率 **90%+**

**核心优势：**

- **本地存储** — 所有笔记就是电脑上的 `.md` 文本文件，不依赖任何云服务，数据从头到尾在自己手里
- **双向链接** — 笔记之间用 `[[wikilink]]` 互相关联，形成知识网络
- **Graph View** — 可视化所有笔记的关联关系，哪些知识孤立、哪些高频被引用，一目了然

> [!warning] 之前的门槛
> 要装插件、配同步、学 Markdown 语法、研究方法论（Zettelkasten、PARA、MOC），光折腾"怎么用"就能把人劝退。

==但现在不一样了。== Claude Code 的生态起来之后，Obsidian 的使用门槛大幅降低——你不需要懂那些方法论，Claude Code 替你搞定。

---

## 三个关键工具：打通 Obsidian × AI

### 1. Claudian 插件

> 直接把 Claude Code 嵌进 Obsidian 侧边栏，选中笔记就能让 AI 总结、扩写、找关联，整个过程不离开编辑器。

🔗 GitHub: [YishenTu/claudian](https://github.com/YishenTu/claudian)

> [!tip] 安装步骤
> 1. 在 [Release](https://github.com/YishenTu/claudian/releases) 中下载 `main.js`、`manifest.json`、`styles.css`
> 2. 放到 `.obsidian/plugins/claudian/` 目录
> 3. 重启 Obsidian → 插件页面启用 Claudian
> 4. 在设置中配置 Claude Code 相关环境变量
> 5. 侧边栏打开 Claudian 即可使用

### 2. Obsidian Skills

> 让 Claude Code 理解 Obsidian 的格式——双向链接、标签、属性、嵌入，全都认得。

🔗 GitHub: [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)

> [!tip] 安装步骤
> 1. 下载 Skills 文件
> 2. 放到 vault 的 `.claude/` 目录下即可

### 3. Obsidian Local API + Claude MCP

> 配好后 Claude Code 可以直接==搜索、读取、创建、修改==你的笔记，AI 直接操作知识库，无需手动复制粘贴。

**依赖项：**

- **Local REST API 插件**：[coddingtonbear/obsidian-local-rest-api](https://github.com/coddingtonbear/obsidian-local-rest-api)
  - 插件市场直接搜 `Local REST API`，下载并开启
  - 拿到 `API Key`、`Host`、`Port` 即可
- **MCP 服务端**：[MarkusPfundstein/mcp-obsidian](https://github.com/MarkusPfundstein/mcp-obsidian)

> [!example] MCP 配置
> 放到 vault 目录（`.claude/settings.json`）或 Claude 全局配置均可：
> ```json
> {
>   "mcpServers": {
>     "mcp-obsidian": {
>       "command": "uvx",
>       "args": ["mcp-obsidian"],
>       "env": {
>         "OBSIDIAN_API_KEY": "你的_API_KEY",
>         "OBSIDIAN_HOST": "127.0.0.1",
>         "OBSIDIAN_PORT": "27124",
>         "OBSIDIAN_PROTOCOL": "https"
>       }
>     }
>   }
> }
> ```

---

# LLM Wiki 模式：让 AI 维护你的知识库

> [!abstract] 核心理念
> 基于 [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 模式：**你永远不自己写 wiki——LLM 写并维护全部内容。你负责：策划来源、探索方向、提出好问题。LLM 负责：总结、交叉引用、归档和簿记。**

配合上面三个工具搭建好之后，Obsidian 变成了一个 **LLM 驱动的持久化知识库**，而非传统的笔记本。它有三层架构：

| 层级 | 说明 | 所有权 |
|------|------|--------|
| **Raw Sources（原始来源）** | 你写的笔记、剪藏的文章——==只读不改== | 你 |
| **Wiki（编译知识层）** | LLM 生成的摘要、概念页、实体页、地图、分析 | LLM |
| **Schema（规约）** | `CLAUDE.md`，告诉 LLM 知识库的结构和工作流程 | 共同演进 |

> [!tip] 比喻
> Obsidian 是 IDE；LLM 是程序员；Wiki 是代码库。

详细的改造计划和实施记录见 [[AI/ClaudeCode/karpathy-llm-wiki-改造计划]]。

---

## 日常操作谱系

搭建完成后，你和 LLM 的日常互动有六大类操作。

### 1. Ingest（摄入）— 知识进来

> [!quote] 新笔记写完后，一句话让 LLM 完成全部后续工作。

| 你说 | LLM 做什么 |
|------|-----------|
| "请摄入 `Docker-Kubernetes/xxx.md`" | 阅读 → 写摘要 → 更新概念/实体页 → 更新索引和日志 |
| "请摄入 `Python/python-运维开发/` 目录下的新文档" | 批量摄入整个目录 |
| "我新建了 `Rust/` 目录，里面有 5 篇文档，请摄入" | 新领域首次摄入 |
| "这篇文档更新了很多内容，请重新摄入" | 旧文档大幅修改后重新编译 |

> [!important] 核心原则
> 你只需要告诉 LLM ==文件路径或目录路径==，其余流程（写摘要、更新交叉引用、维护索引）全部自动完成。

---

### 2. Query（查询）— 向知识库提问

> [!quote] 这是**最高频**的日常操作。不需要自己翻文档，直接问。

| 你说 | LLM 做什么 |
|------|-----------|
| "K8s 的 HPA 和 KEDA 有什么区别？" | 搜索相关 wiki 页面，综合回答并附引用 |
| "我们仓库里关于 Prometheus 高可用有哪些方案？" | 汇总你笔记中记录的所有 HA 方案 |
| "Azure 和阿里云的网络产品怎么对标？" | 读取实体页 + 批量摘要，生成对比 |
| "帮我回顾一下 ArgoCD 的所有笔记要点" | 读取 entity 页 + source 摘要，结构化回顾 |

> [!success] 关键习惯
> 如果回答有分析价值，追一句 **"归档到 wiki"**。这样你的每次提问都在积累知识，而非一次性消耗——==知识复利==。

---

### 3. Lint（健康检查）— 维护质量

> [!quote] 定期检查知识库健康度，保持结构整洁。

| 你说 | 频率建议 |
|------|---------|
| "跑一次 lint" | 每周 / 批量操作后 |
| "检查一下断链" | 重命名或删除文件后 |
| "哪些概念被提到很多次但还没有独立页面？" | 每月 |
| "哪些实体页内容太薄需要增强？" | 每月 |

Lint 检查的内容：
- 断链（wikilink 指向不存在的文件）
- 孤儿页（没有任何入链的页面）
- 缺失概念（被多次提及但没有独立页面）
- 页面间矛盾
- 过时内容
- 缺失的交叉引用

---

### 4. Restructure（结构调整）— 知识重组

> [!quote] 当知识积累到一定程度，结构需要演进。

| 你说 | 场景 |
|------|------|
| "Prometheus 内容越来越多了，拆分出一个可观测性子地图" | 新建 map |
| "把 `容器运行时` 拆成 Docker Engine 和 containerd 两个实体页" | 概念拆分 |
| "这几个概念其实是一回事，合并一下" | 概念合并 |
| "帮 Python 领域建一个专题地图" | 新建 map |
| "CLAUDE.md 的 Ingest 流程要加一步 xxx" | Schema 演进 |

---

### 5. Review（回顾）— 知识复盘

> [!quote] 宏观审视知识库的全貌和成长。

| 你说 | LLM 做什么 |
|------|-----------|
| "最近一周知识库有什么变化？" | 读 `log.md`，汇总最近操作 |
| "给我一个知识库现状报告" | 统计页面数、覆盖度、红链数 |
| "Docker-Kubernetes 领域的知识覆盖够完整吗？" | 读取实体页"知识空白"章节，分析覆盖度 |
| "帮我列出所有标记为 stub 的实体页" | 找出需要增强的薄弱页面 |

---

### 6. Export（导出）— 知识输出

> [!quote] 知识库的最终价值在于输出。

| 你说 | 输出场景 |
|------|---------|
| "基于 wiki 里的 K8s 知识，准备一个 CKA 复习大纲" | 考试备考 |
| "帮我写一份监控方案的技术分享 PPT 大纲" | 团队分享 |
| "基于 Aliyun 和 Azure 的对比，生成多云选型报告" | 架构决策 |
| "把 Helm 实体页的内容整理成一篇博客" | 内容创作 |

---

### 推荐节奏

> [!example] 日常节奏
>
> | 频率 | 操作 |
> |------|------|
> | **每天** | Query（随时提问，有价值就归档） |
> | **每周** | Ingest（新笔记摄入）+ Lint（快速健康检查） |
> | **每月** | Review（覆盖度回顾）+ Restructure（按需调整结构） |
> | **按需** | Export（基于积累的知识产出价值） |

