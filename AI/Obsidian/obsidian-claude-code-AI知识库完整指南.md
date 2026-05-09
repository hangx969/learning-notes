---
title: "Obsidian + Claude Code：AI 驱动的知识库完整指南"
tags:
  - AI
  - obsidian
  - claude-code
  - knowledge-management
  - knowledgebase/methodology
aliases:
  - AI知识库完整指南
  - Obsidian AI 知识库
  - Claude Code Obsidian 集成
  - Karpathy LLM Wiki 改造
date: 2026-05-09
merged_from:
  - karpathy-llm-wiki-改造计划
  - obsidian-claude-搭建karpathy-wiki知识库
  - obsidian-claude-code-AI知识管家
---

# Obsidian + Claude Code：AI 驱动的知识库完整指南

> 你不需要成为笔记达人。你只需要把笔记存成 AI 能直读的格式，然后让 AI 接管剩下的事。

---

## 一、你的笔记软件里躺着多少僵尸

回忆一下，你上次打开笔记软件是什么时候？不是打开来记东西，而是打开来 **找东西、复用东西** 。

大概率你找不到。

印象笔记里躺着 2018 年收藏的文章，已经忘了为什么收藏。备忘录里塞满随手记的想法，但这些想法之间没有任何关联。微信收藏夹里那成百上千篇"以后再看"——从此以后真的再也没看。

我记下来的不是知识，是 **信息的坟场** 。

不是不努力。每条笔记记录的当下都是有价值的。但从"记下来"到"用起来"中间隔着一道鸿沟——整理、关联、检索、复用，这件事人脑天生不擅长。

直到我把笔记搬到 Obsidian，把 Claude Code 接进来，让 AI 当全职管理员之后，这道鸿沟才算迈过去。今天分享我搭这套体系的过程，给你一份能直接抄的路径。

---

## 二、为什么是 Obsidian + Claude Code

### 先说结论

**Obsidian + Claude Code 是 2026 年个人知识管理的最优解** ——前提是你做的是个人知识管理，不是团队协作。

理由三句话：

第一，Markdown 是 LLM（大语言模型）的母语。你的笔记格式决定了 AI 能帮你到什么程度。
第二，本地文件让 AI 零摩擦读写。Obsidian 的 Vault 就是一个 Markdown 文件夹，Claude Code 进去是有完整权限的管理员，不是隔着 API 传话的外人。
第三，AI 时代"整理"这件事不再是人的责任。你只管记录和思考，整理交给 AI。

### 知识库类软件的现状

当前市面上的知识库软件大致可以分为三类，各有不足：

| 类型 | 代表产品 | 优势 | 不足 |
| --- | --- | --- | --- |
| 传统笔记 | 语雀、印象笔记 | 整理、记录、协作齐全 | ==没有 AI==，知识存进去就"死"了 |
| AI + 知识库 | 腾讯 IMA、秘塔 AI 搜索 | 能上传文档做问答 | 更像内容聚合社区，产出形式受限 |
| 纯 AI 工具 | 元宝、豆包、Kimi | AI 能力强，写作/总结/翻译 | ==没有本地知识库==，知识无法沉淀 |

> [!summary] 核心矛盾
> 要么没脑子，要么没记忆，要么有脑子有记忆但==不是你的==。

### Markdown 是 LLM 的母语

大语言模型的训练数据里，Markdown 是最主要的格式之一。GitHub 上几十亿个 README.md、技术文档、博客文章、教程，AI 全读过。它对 `##` 标题、 `**加粗**` 、 `-` 列表的理解，像你对中文标点一样自然。

具体三个特性：

**Token 效率** 。同样的信息，用 Markdown 表示比 JSON 或 XML 紧凑很多（花叔手册里给到 30-50% 的差值，自己跑过一次类似比例）。意味着同样的上下文窗口能装下更多笔记。Claude 1M token 大窗口大概能放下中等规模的整个知识库——对绝大多数人来说，纯文本 + 长上下文这套已经够用，根本不用先去搞向量数据库。

**结构天然清晰** 。 `##` 是标题、 `>` 是引用、 ` ``` ` 是代码块。这些标记本身就是结构分隔符，不需要告诉 AI"这是标题"，Markdown 语法自己在说。

**AI 的默认输出格式** 。让 ChatGPT 或 Claude 回答问题，回复就是 Markdown。你的知识库用 Markdown，AI 进来就像回家。

反过来——如果你的笔记存在 Apple Notes 里，AI 摸不到。存在 Notion 里，AI 只能通过 API 间接访问，权限受限、速度受限、操作受限。存在印象笔记里，格式私有，导出困难。

笔记格式决定了 AI 能帮你到什么程度。

### 本地文件 = AI 直接读写

Obsidian 的 Vault 是什么？一个文件夹。

不是数据库、不是云端服务、不是私有格式。就是你电脑上的一个文件夹，里面全是 `.md` 文件。Obsidian 做的事情是给这个文件夹加了一层 UI——双向链接、图谱视图、搜索、插件。但底层文件从头到尾都是标准 Markdown。

Claude Code 的工作方式是直接操作本地文件系统。读文件、写文件、搜索文件、移动文件、重命名，所有操作都是对文件系统的直接访问，不需要 API、不需要认证、不需要网络请求。

把 Claude Code 指向一个 Obsidian Vault，立刻就能工作：

```
cd ~/Obsidian/我的vault
claude
```

这个差异不是"体验好一点"，是 **能做 vs 不能做** 的区别。在 Obsidian 里 Claude Code 是管家，在 Notion 里它是只能传话的外人。

### 三个独立的十亿级项目殊途同归

如果只是理论分析，你可能觉得"听起来有道理但也就那样"。但有一个论据让我没法忽视——

三个完全独立的、十亿美元级别的项目，没有互相参考，做出了同一个架构决策。

**Manus** ，AI Agent 公司，2026 年 Meta 拟以 20 亿美元收购，后被中方监管叫停。Manus 的 Agent 在执行长任务时用什么存记忆？ `task_plan.md` 和 `notes.md` ——Markdown 文件。

**OpenClaw** ，开源 AI Agent 框架，GitHub 上 35 万 + 颗星。Agent 的知识存在哪？ `MEMORY.md` 。Agent 的人格定义存在哪？ `SOUL.md` ——还是 Markdown 文件。

**Claude Code** ，Anthropic 自家的 AI 编程工具。项目上下文存哪？ `CLAUDE.md` 。用户长期记忆存哪？ `memory/` 目录下的 Markdown 文件。

三个不同的团队，解决不同的问题，服务不同的用户。在没有互相参考的情况下，做出了同一个选择： **用 Markdown 文件作为 AI Agent 的记忆层** 。

不是向量数据库，不是 SQL，不是 JSON。就是 `.md` 文件。

### 为什么选 Obsidian

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

## 三、核心理念：Karpathy LLM Wiki 模式

> [!abstract] 核心理念
> 基于 [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 模式：**你永远不自己写 wiki——LLM 写并维护全部内容。你负责：策划来源、探索方向、提出好问题。LLM 负责：总结、交叉引用、归档和簿记。**

这个思路来自 Andrej Karpathy 2026 年 4 月那条 1600 万浏览的推文。

他说的核心是一个观点转换： **AI 不是检索器，是编译器** 。

传统 RAG（检索增强生成）的逻辑是每次提问都重头搜索原始材料、拼接、生成回答，回答用完即弃，下次再问还得从零开始——**每次查询都从零发现知识，没有积累**。

LLM Wiki 的做法完全不同：**LLM 增量构建并维护一个持久化的 wiki**——一组结构化、互相链接的 markdown 文件，位于你和原始资料之间。每当新资料进入，LLM 不是简单索引，而是阅读、提取关键信息、整合到现有 wiki 中——更新实体页、修订主题摘要、标注新旧数据的矛盾、强化或挑战已有综述。知识被**编译一次，持续更新**，而非每次查询重新推导。

> [!tip] 比喻
> Obsidian 是 IDE；LLM 是程序员；Wiki 是代码库。

### 三层架构

| 层级 | 说明 | 所有权 |
|------|------|--------|
| **Raw Sources（原始来源）** | 你写的笔记、剪藏的文章、论文、图片、数据文件。**不可变**，LLM 只读不改。这是你的事实来源。 | 人类策划 |
| **Wiki（编译知识层）** | LLM 生成的 markdown 文件目录：摘要、实体页、概念页、对比、综览、综述。LLM 完全拥有此层，创建页面、更新、维护交叉引用、保持一致性。 | LLM 拥有 |
| **Schema（规约文件）** | 一份文档（如 `CLAUDE.md`）告诉 LLM wiki 的结构约定、工作流程。这是核心配置文件——让 LLM 成为有纪律的 wiki 维护者而非通用聊天机器人。 | 人类与 LLM 共同演进 |

落到 Obsidian 里就是 raw → wiki → output 三层结构：

```
Vault/
├── raw/      # 你扔进来的原始素材，只增不改
├── wiki/     # AI 编译过的可复用知识
│   ├── concepts/   # 概念页（每个概念一篇）
│   ├── entities/   # 人物 / 产品页
│   ├── sources/    # 原始来源摘要
│   └── topics/     # 主题分析页
└── output/   # 基于 wiki 生成的报告 / 分析
```

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

## 四、30 分钟上手搭建

### 第一步：cd 进 Vault，启动 Claude Code

如果你已经有一个装满 Markdown 文件的文件夹，直接拿它当 Vault。Obsidian 不会改你的任何文件，只是加一层 UI。

```
cd ~/Documents/我的vault
claude
```

完事。Claude Code 启动后自动获得整个 Vault 目录的读写权限——读笔记、新建文件、搜索内容、重命名、移动、删除全都可以，不需要任何配置。

第一次启动可以试一句"我的 Vault 里有什么？帮我概览一下"，作为冒烟测试。

### 第二步：写一份 CLAUDE.md 给 AI 看

光有读写权限还不够。Claude Code 第一次进入你的 Vault 像新员工第一天上班，指着满屋子文件柜说"你随便看"——他要么无从下手，要么乱翻一气。

需要一份 **员工手册** 。在 Vault 根目录创建 `CLAUDE.md` ，Claude Code 每次启动都会读它。最少四块内容：

```
# 我的知识库

## 关于我
- 你的身份和职业
- 关注领域 3-5 个
- 偏好（用中文、不要过度格式化等）

## Vault 结构
- daily/：每日记录
- notes/：永久笔记
- projects/：进行中的项目
- raw/：待整理的原始素材
- archive/：已完成或不再活跃的内容

## 笔记 Front Matter（必填）
新建笔记时使用：
---
title: 笔记标题
tags: []
created: YYYY-MM-DD
type: fleeting | literature | permanent
summary: 一句话摘要
---

## 行为规则
- 可以：加标签、建 [[双向链接]]、生成摘要、整理分类
- 不可以：删除已有笔记内容、修改原始记录
- 创建新笔记必须遵循 Front Matter 模板
```

这份手册不需要一上来就完美。三五行起步，每次 Claude Code 犯错就加一条规则——半年下来它会自然长成一份很详尽的指南。

### 第三步：每个大目录补一份 index.md

Claude Code 进入一个文件夹，看到 50 个文件需要逐个扫描判断。但如果你在文件夹里放一份 3-5 行的 `index.md` ，它先读这一份，3 秒钟就知道这里是干啥的、关键文件在哪。

```
# notes/ — 永久笔记

存放经过思考整理的、可被反复引用的判断。

## 命名规范
按"主题-标题.md"命名

## 关键文件
- [[卡尼曼-思考快与慢]] — 认知偏差经典
- [[芒格-穷查理宝典]] — 跨学科思维模型

## AI 操作规则
- 创建新笔记必须带完整 Front Matter
- 修改前先 grep Vault 是否已有相关概念
```

这个习惯做下来之后效率提升非常明显。原来 Claude Code 每次都要 ls 一遍才能定位，现在直接定向跳进对应文件夹拿上下文。

### 第四步：装 obsidian-skills

最后一步。Obsidian 的 Markdown 有些独有语法（ `[[wikilinks]]` 双向链接、callout 提示框、`.canvas` 空间笔记），Claude Code 默认不一定懂——它可能把 `[[]]` 当成普通 Markdown 链接处理，搞坏格式。

Obsidian CEO kepano 亲自做了 `obsidian-skills` 这套官方 Skill 集，教 Claude Code 正确处理这些非标准语法。安装就一行命令：

```
cd ~/Obsidian/我的vault
git clone https://github.com/kepano/obsidian-skills.git .claude/skills/obsidian-skills
```

下次 Claude Code 启动时会自动加载，从此处理 `[[]]` 、callout、`.canvas` 、`.base` 都不会出错。

到这里 30 分钟够了。

---

## 五、三个关键工具：打通 Obsidian × AI

上面四步是基础版。如果想让 Obsidian 和 AI 的集成更深入，以下三个工具可按需使用。

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

## 六、日常操作谱系

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

### 4. Restructure（结构调整）— 知识重组

> [!quote] 当知识积累到一定程度，结构需要演进。

| 你说 | 场景 |
|------|------|
| "Prometheus 内容越来越多了，拆分出一个可观测性子地图" | 新建 map |
| "把 `容器运行时` 拆成 Docker Engine 和 containerd 两个实体页" | 概念拆分 |
| "这几个概念其实是一回事，合并一下" | 概念合并 |
| "帮 Python 领域建一个专题地图" | 新建 map |
| "CLAUDE.md 的 Ingest 流程要加一步 xxx" | Schema 演进 |

### 5. Review（回顾）— 知识复盘

> [!quote] 宏观审视知识库的全貌和成长。

| 你说 | LLM 做什么 |
|------|-----------| 
| "最近一周知识库有什么变化？" | 读 `log.md`，汇总最近操作 |
| "给我一个知识库现状报告" | 统计页面数、覆盖度、红链数 |
| "Docker-Kubernetes 领域的知识覆盖够完整吗？" | 读取实体页"知识空白"章节，分析覆盖度 |
| "帮我列出所有标记为 stub 的实体页" | 找出需要增强的薄弱页面 |

### 6. Export（导出）— 知识输出

> [!quote] 知识库的最终价值在于输出。

| 你说 | 输出场景 |
|------|---------| 
| "基于 wiki 里的 K8s 知识，准备一个 CKA 复习大纲" | 考试备考 |
| "帮我写一份监控方案的技术分享 PPT 大纲" | 团队分享 |
| "基于 Aliyun 和 Azure 的对比，生成多云选型报告" | 架构决策 |
| "把 Helm 实体页的内容整理成一篇博客" | 内容创作 |

### 推荐节奏

> [!example] 日常节奏
>
> | 频率 | 操作 |
> |------|------|
> | **每天** | Query（随时提问，有价值就归档） |
> | **每周** | Ingest（新笔记摄入）+ Lint（快速健康检查） |
> | **每月** | Review（覆盖度回顾）+ Restructure（按需调整结构） |
> | **按需** | Export（基于积累的知识产出价值） |

---

## 七、装完之后让 AI 帮你做的第一件事

四步搭完是底子，真正让你感受到价值的是接下来这件事—— **让 AI 整理一批散乱的笔记** 。

找一批以前在备忘录、微信收藏、印象笔记里的乱账，转成 Markdown（Claude Code 也能帮你转）扔进 Vault 的 `raw/` 目录。然后告诉它：

```
帮我整理 raw/ 下的散乱笔记。
读取所有文件，按主题分类，给每条笔记加 Front Matter，
建立 [[双向链接]]，最后给每个文件夹生成 index.md。
```

接下来你会看到 Claude Code 工作：

- 扫描分类，按主题把笔记移到对应文件夹
- 给每条加 Front Matter（标题、标签、摘要）
- 发现笔记间关联，自动插入 `[[双向链接]]`
- 给每个文件夹生成 index.md

五分钟，也许更快。

整理完打开 Obsidian 的图谱视图。原来散落的点开始形成网络，一条关于"注意力"的笔记连向了卡尼曼读书笔记，也连向社交媒体的思考——这些关联以前只在你脑子里模糊存在，现在变成可见可点击的链接。

MakeUseOf 有一位作者的案例值得参考—5 年笔记没标签、没链接、没结构、试过三次手动整理都放弃的烂账，他用 Claude Code + Obsidian 90 分钟整理完。我没那么多年的笔记可整，但跑了一遍我自己散落在备忘录里的几百条素材，5 分钟就跑出了第一版分类——比我预期的快得多。

---

## 八、现有知识库现状分析

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

| 维度        | Karpathy 模式              | 当前状态                         | 差距            |
| --------- | ------------------------ | ---------------------------- | ------------- |
| 原始来源不可变性  | raw/ 目录只读                | 无 raw/，笔记随时可编辑               | 需明确原始来源层      |
| wiki 编译层  | LLM 生成的结构化 wiki 目录       | KnowledgeBase/ 有雏形但不完整       | 需扩充为完整 wiki 层 |
| Schema 文件 | CLAUDE.md 定义结构和工作流       | 无专门 schema                   | 需创建           |
| index.md  | 全 wiki 目录，每页一行摘要         | KnowledgeBase/INDEX.md 有但粒度粗 | 需细化           |
| log.md    | 仅追加操作日志                  | 不存在                          | 需创建           |
| Ingest 流程 | 标准化：读源→写摘要→更新索引→更新实体/概念页 | 无标准流程                        | 需定义           |
| Query 归档  | 好答案归档回 wiki              | 不存在                          | 需定义           |
| Lint 流程   | 定期检查矛盾、孤儿页、缺失概念          | maintenance/ 有断链报告           | 需扩展           |
| 交叉引用      | 系统化的 `[[wikilink]]` 网络   | 部分存在但不系统                     | 需加强           |

---

## 九、改造行动计划

### 原则

1. **不动现有文档**：现有 350 篇笔记视为 Raw Sources（原始来源层），保持不可变
2. **KnowledgeBase/ 作为 Wiki 层**：LLM 在此生成和维护所有编译内容
3. **渐进式改造**：不需要一步到位，先建立骨架，再逐步摄入
4. **LLM 做重活**：所有 wiki 页面由 LLM 编写和维护

### Phase 0：建立 Schema（Day 1）

**目标**：创建 `CLAUDE.md`，定义 wiki 的结构规约和操作流程。

Schema 应包含：目录结构定义、页面规约（frontmatter、链接格式、模板）、操作流程（Ingest/Query/Lint）。

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

## 十、想再玩深一点的三个方向

整理完之后大概率你会想要更多。这里给三个进阶方向，按性价比排序，不一定全做但都值得知道。

### 方向一：让 AI 把笔记编译成可复用的 wiki

每次写完一篇文章，让 Claude Code 把里面"可独立成立的知识点"提炼到 wiki/。下次写相关主题时它先读 wiki，不重新调研。三层加配套的 SCHEMA.md（写清楚命名规范、Front Matter 模板、 `[[]]` 规则），效果是知识从一次性消耗变成永久资产。

这一步的重点不是装新工具，是 **改变心智** ：让 AI 在你这边积累，而不是每次重置。

### 方向二：自动 backlinks（Agentic Note-Taking）

`[[双向链接]]` 很好，但你得记得去建。写日记顺手提到"今天和老王吃饭、聊了塔勒布"，不主动输入 `[[老王]]` 、 `[[塔勒布]]` ，这条日记和你之前关于这两个人的笔记就没关系。

德国开发者 Stefan Imhoff 之前每天花 10-15 分钟手动给日记加 `[[]]` 。后来他用 Claude Code 写了一个工作流：

```
读取今天的日记。
找出所有人名、地名、书名、概念。
对每一个：搜索 Vault 是否已有对应笔记；
有就把纯文本替换成 [[wikilink]]，
没有就在 wiki/ 下建一个占位页（stub）再链接。
```

10 分钟的手工活变成几秒钟。更彻底的是它不会漏——你可能忘了 Vault 里有某个概念页，它不会忘。

把这个动作做成 CLAUDE.md 里的一条规则（"我说'处理今天的日记'时执行上面流程"），从此你写笔记时不需要管 `[[]]` ，写完一个命令织网。

### 方向三：把 Claude Code 嵌入 Obsidian，加语义搜索

如果你已经经常切窗口（Obsidian 看 → 终端跑 → Obsidian 看），三个插件能让体验提一档：

**Claudian** ：把 Claude Code 的对话界面嵌进 Obsidian 侧边栏。右侧给指令、主编辑区实时看到笔记变化，少了一次 Alt+Tab。

**Smart Connections** ：Obsidian 自带搜索是关键词匹配——搜"投资"找不到"资产配置"。Smart Connections 用 AI embedding（把笔记转成向量）给 Vault 建语义索引，相关概念都能搜到。打开任何笔记时侧边栏自动显示语义最近的其他笔记，经常会发现自己没意识到的关联。

**Copilot for Obsidian** ：Vault 级别的 RAG 问答。问"我之前关于定价策略写过什么"，它从你自己的笔记里答，每个观点带出处。和直接问 ChatGPT 的区别是——回答来自你自己的知识，不是互联网通用信息。

三个不必都装。优先级是 Smart Connections > Claudian > Copilot——语义搜索是日常每次都用的，回报最稳；Claudian 是体验优化，看你切窗口频率；Copilot 是有了一定笔记规模（500 篇以上）才真值得装的，否则可问的东西不够。

---

## 十一、实用工具建议

| 工具 | 用途 |
|------|------|
| **Obsidian Graph View** | 可视化 wiki 连接结构，发现孤儿页和 hub 页 |
| **Obsidian Web Clipper** | 浏览器扩展，将网页文章转为 markdown 存入 raw 层 |
| **Obsidian Dataview** | 查询 frontmatter，生成动态表格和列表 |
| **qmd** | 本地 markdown 搜索引擎（BM25 + 向量混合搜索），wiki 增长后替代 index.md |
| **git** | wiki 本身就是 git 仓库，天然有版本历史、分支和协作能力 |

---

## 十二、预期成果

改造完成后，知识库将具备：

1. **清晰的三层分离**：原始笔记（只读）→ wiki 编译层（LLM 维护）→ schema（共同演进）
2. **知识复利**：每次摄入新来源都会丰富已有的概念网络，而非孤立存放
3. **高效查询**：通过 index.md 和结构化的 wiki 页面，LLM 能快速定位和综合回答
4. **维护成本近零**：LLM 处理所有交叉引用更新、一致性维护、日志记录
5. **可视化知识图谱**：Obsidian Graph View 展示概念间关联

---

## 十三、我用了一周后的几个判断

**一定做的三件事** ：装 obsidian-skills、补 index.md、Front Matter 加 type 和 summary 字段。这三件投入不超过 1 小时，但日常每次操作都受益。尤其 type 字段的三态（fleeting / literature / permanent），AI 扫 Vault 时按 type 决定处理策略，这件事一旦开始用就回不去了。

**不要照抄大博主们 Skills 的做法** 。一上来不要装一堆 Skill，那是他用了一年多积累出来的。先用几个月，等你明确知道自己缺什么能力的时候，再去找对应的 Skill——否则你只是在收集工具不在解决问题。

**多 Vault 不要太早搞** 。先用一个 Vault，500 篇以下别拆。等到出现两类内容 **完全不交叉** （比如工作机密 vs 个人日记，或者写公众号 vs 学术研究）、且你确实在频繁切换上下文时才拆——过早拆分会增加管理成本而不解决任何问题。

**先写后整理** 。我自己第一次搭体系时踩过的最大坑是"系统先行"——花一下午研究各种方法论、设计完美分类，一周后发现实际笔记根本不符合预设，整套推翻重来。后来想明白笔记系统得从笔记里长出来，不是从设计图纸里长出来。

**40 万字以内不需要向量数据库** 。Claude 的上下文窗口够大，纯文本 wiki + index.md 导航，AI 找到相关知识的速度和准确度都很高。超过百万字级别再考虑加语义搜索。

---

## 最后一句

这套体系的核心不是 Obsidian，也不是 Claude Code。是 **整理这件事不再是你的责任** 。

过去几十年所有的笔记工具，从 Word 到 Notion，都假设"整理是你的事"。AI 改变的是这个假设——你只管记录和思考，整理交给 AI。

工具会变。今天是 Obsidian，明天可能是别的。但你 Vault 里的那些 Markdown 文件，它们一直是你的。

要试的话路径很短：找一篇你最近想存的文章存成 `.md` ，扔进一个新建的文件夹， `cd` 进去 `claude` 起个对话——剩下 AI 会问你三个问题然后开始干活。
