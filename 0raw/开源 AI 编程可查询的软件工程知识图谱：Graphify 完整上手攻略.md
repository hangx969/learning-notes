---
title: "开源 AI 编程可查询的软件工程知识图谱：Graphify 完整上手攻略"
source: "https://mp.weixin.qq.com/s/yG2JXr3AWFIdRzNDG7a70w"
author:
  - "[[兔兔AGI]]"
published:
created: 2026-06-05
description: "传统软件开发里，我们会用 README、架构文档、接口文档、代码注释来帮助团队理解项目。Graphify 做的，就是把这些分散的信息整理成一张可查询的软件工程知识图谱。"
tags:
  - "clippings"
---
兔兔AGI *2026年5月24日 11:36*

传统软件开发里，我们会用 README、架构文档、接口文档、代码注释来帮助团队理解项目。到了 AI 编程时代，这些东西依然存在，只是使用方式变了。我们会把仓库、文档、截图，甚至视频一起交给 AI 助手，但它还是得反复扫描文件、拼接上下文。

项目一大，这种方式就开始吃力。

代码在 `src/` ，设计文档在 `docs/` ，历史讨论记录在 Markdown 里，论文、截图、视频可能散落在各个目录里。资料其实很多，真正缺的是它们之间的关联。

**Graphify 做的，就是把这些分散的信息整理成一张可查询的软件工程知识图谱。**

## 为什么 AI 编程需要知识图谱

很多人现在用 AI 编程助手，流程其实都差不多：

先把项目文件交给模型，再提一个问题，让它去读代码、找线索、拼上下文。下次换个问题，它又重新读一遍、重新找一遍。

小项目还好，一旦项目复杂起来，这种方式很快就会吃力。

因为 AI 每次理解项目，某种程度上都像「临时上岗」。它能看懂当前上下文，也能回答眼前的问题，但这些理解很难真正沉淀下来。下一轮对话，它可能还得重新扫描同样的文件。

> 文件都在，资料都在，但理解没有累积。

更实用的做法，是让 AI 不停留在「读到更多文件」这一步，还能顺着项目里的关系继续查下去。

比如：

- • 一个认证流程到底经过了哪些模块？
- • 某个配置类影响了哪些服务？
- • 当前代码为什么会这样设计？有没有对应的设计说明？
- • 哪些论文、文档、视频和这个模块有关？

这些问题关心的重点，已经从「某个关键词出现在哪个文件里」，转向了「概念、代码、文档之间到底怎么连起来」。

**Graphify 的价值，就是把这些关系整理出来，变成一层可以持续复用的项目知识。**

你也可以把它理解成一层「项目记忆」。Graphify 会先读取项目，把代码结构、文档、设计思路和外部资料组织起来。之后 AI 再回答问题时，就不用每次都从头翻文件，而是能沿着已有关系继续查找和推理。

变化的核心，是从「检索文件」走向「查询关系」。

## Graphify 是什么？

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/CBgB44gdva0icicNMgpTBKQ5KVesJRiaI3UXHVEFls6NUNSIw2g6ictk2eROeRHenx1y71CPiatRjiabSibhtB4WjNkfhOJbbiavWCSVx1FKpbPpyV0/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

Graphify 的入口其实很直接。

在支持的 AI 编程助手里，你可以输入：

```
/graphify .
```

如果是在普通终端里，也可以运行：

```
graphify .
```

它会把当前项目目录里的代码、文档、PDF、图片、视频等内容，映射成一张可以查询的软件工程知识图谱。

运行之后，默认会得到一个 `graphify-out/` 目录：

```
graphify-out/
├── graph.html       # 浏览器可视化图谱
├── GRAPH_REPORT.md  # 项目总结与关系分析
└── graph.json       # 完整结构化图谱
```

这几个文件分别解决不同问题。

`graph.html` 是给人看的。你可以在浏览器里打开它，查看项目中的节点和关系，适合快速建立整体印象。

`GRAPH_REPORT.md` 是给人和 AI 一起看的。它会总结项目里的关键概念、高连接度节点、值得注意的关系，以及这张图谱适合回答的问题。

`graph.json` 则是更底层的结构化产物。后续查询、路径追踪、MCP 接入、图谱合并，都可以围绕它展开。

Graphify 的关键不只在输出文件，而在它处理不同资料的方式。

对于代码文件，它会使用本地 AST 解析，也就是通过 tree-sitter 之类的结构化方式提取代码关系。这一部分不需要调用模型 API，速度更快，也更稳定。

对于文档、PDF、图片、视频等非结构化内容，它会交给 AI 模型做语义抽取，把概念和关系补充进图谱里。

简单说，就是：

```
代码 → 本地结构化解析
文档 / 图片 / 视频 → 模型语义提取
最终 → 合并成一张知识图谱
```

这里有一个很重要的设计：Graphify 不会把 AI 抽取出来的关系都当成绝对事实。

它会给每条关系标记来源和置信度：

| 标签 | 含义 |
| --- | --- |
| `EXTRACTED` | 直接从文件中提取 |
| `INFERRED` | 基于上下文推断 |
| `AMBIGUOUS` | 存在歧义，需要人工确认 |

这个细节很关键。

工程场景里，答案是否成立，不能只看它说得是否顺，还要看它来自哪里、可靠到什么程度。Graphify 把「发现」和「推断」分开标注，方便后续复核，也能降低 AI 编程里的误判风险。

## 快速上手指南

Graphify 的安装不算复杂，但有几个细节需要注意。

首先是环境要求。

| 依赖 | 最低要求 | 检查方式 | 安装入口 |
| --- | --- | --- | --- |
| Python | 3.10+ | `python --version` | python.org <sup>[1]</sup> |
| uv | 任意版本 | `uv --version` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| pipx | 任意版本 | `pipx --version` | `pip install pipx` |

官方推荐使用 `uv` 安装，因为它会自动把 CLI 放到 PATH 里，后续调用更省心。

需要特别注意的是，PyPI 包名是 `graphifyy` ，有两个 `y` 。但安装完成后的命令仍然是 `graphify` 。

推荐安装方式：

```
uv tool install graphifyy
```

也可以使用：

```
pipx install graphifyy
```

或者：

```
pip install graphifyy
```

安装完成后，需要把 Graphify 注册到你的 AI 编程助手里：

```
graphify install
```

然后打开 AI 编程助手，在项目根目录里输入：

```
/graphify .
```

如果你使用的是 Windows PowerShell，要注意这里的写法。

PowerShell 会把开头的 `/` 当成路径分隔符，所以不要写 `/graphify .`，而是直接在终端里运行：

```
graphify .
```

Graphify 支持的平台比较多，包括 Claude Code、Codex、OpenCode、Cursor、Gemini CLI、GitHub Copilot CLI、VS Code Copilot Chat、Aider、Kimi Code、Kiro、Trae 等。

如果你使用 Claude Code，可以运行：

```
graphify install
```

如果你需要指定平台，也可以使用类似命令：

```
graphify install --platform windows
graphify install --platform codex
graphify cursor install
graphify vscode install
```

Codex 用户还有一个额外差异：它使用的是 `$graphify` ，而不是 `/graphify` 。需要在 `~/.codex/config.toml` 的 `[features]` 下开启：

```
multi_agent = true
```

第一次生成图谱时，最常用的命令就是：

```
/graphify .
```

生成完成后，可以先打开：

```
graphify-out/GRAPH_REPORT.md
```

这个文件相当于项目图谱的「导读」。它会告诉你项目里哪些概念最关键，哪些关系最意外，以及这张图谱适合继续追问什么。

如果你想看一页更适合阅读的架构和调用流页面，可以运行：

```
graphify export callflow-html
```

这会基于 `graphify-out/` 导出更可读的架构页面，适合在团队内部做项目讲解。

## 常用查询方式

生成图谱只是第一步。更常用的场景，是围绕这张图继续提问。

它提供了一组常用命令，用来查询概念、追踪路径、解释节点。

比如你想知道认证模块和数据库之间有什么关系，可以问：

```
/graphify query "what connects auth to the database?"
```

如果你想看两个具体模块之间的路径，可以用：

```
/graphify path "UserService" "DatabasePool"
```

如果你想理解某个节点，可以用：

```
/graphify explain "RateLimiter"
```

这和普通 `grep` 的使用场景不太一样。

`grep` 擅长找「这个词出现在哪里」。Graphify 更适合追问「这些模块、概念、文档之间怎么连起来」。

在接手陌生项目时，一个比较自然的流程是：

```
# 第一步：生成图谱
/graphify .

# 第二步：先读报告
# 打开 graphify-out/GRAPH_REPORT.md

# 第三步：围绕关键模块追问
/graphify query "show the auth flow"
```

如果你已经有 `graph.json` ，也可以直接从终端查询：

```
graphify query "show the auth flow"
graphify query "what connects DigestAuth to Response?" --graph graphify-out/graph.json
```

当项目发生变化时，不一定每次都要全量重跑。可以只更新变化文件：

```
/graphify ./docs --update
```

如果只想重新做聚类，不重新抽取内容，可以运行：

```
/graphify . --cluster-only
```

如果项目太大，不想生成 HTML，只想保留报告和 JSON，可以运行：

```
/graphify . --no-viz
```

如果你想基于图谱生成一套 Markdown wiki，可以运行：

```
/graphify . --wiki
```

Graphify 还可以把外部资料纳入项目图谱。

比如把一篇论文加入图谱：

```
/graphify add https://arxiv.org/abs/1706.03762
```

或者把一个 YouTube 视频转录后加入：

```
/graphify add <youtube-url>
```

这件事的意义在于，项目知识不再局限于代码仓库本身。论文、会议视频、设计文档、产品说明，都可以变成图谱里的节点和关系。

对于一些特殊文件类型，Graphify 提供了可选 extras。你可以按需安装，不必一开始全部装上。

| Extra | 能力 | 安装方式 |
| --- | --- | --- |
| `pdf` | PDF 提取 | `pip install "graphifyy[pdf]"` |
| `office` | `.docx`  、`.xlsx` 支持 | `pip install "graphifyy[office]"` |
| `google` | Google Sheets 渲染 | `pip install "graphifyy[google]"` |
| `video` | 视频和音频转录 | `pip install "graphifyy[video]"` |
| `mcp` | MCP stdio server | `pip install "graphifyy[mcp]"` |
| `neo4j` | 推送到 Neo4j | `pip install "graphifyy[neo4j]"` |
| `svg` | SVG 图谱导出 | `pip install "graphifyy[svg]"` |
| `ollama` | 本地 Ollama 推理 | `pip install "graphifyy[ollama]"` |
| `openai` | OpenAI 或兼容 API | `pip install "graphifyy[openai]"` |
| `gemini` | Google Gemini API | `pip install "graphifyy[gemini]"` |
| `bedrock` | AWS Bedrock | `pip install "graphifyy[bedrock]"` |
| `sql` | SQL schema 抽取 | `pip install "graphifyy[sql]"` |

如果你的团队已经在使用 MCP，也可以把图谱作为 MCP server 暴露给 AI 助手：

```
python -m graphify.serve graphify-out/graph.json
```

它会提供类似 `query_graph` 、 `get_node` 、 `get_neighbors` 、 `shortest_path` 这样的结构化访问能力。

这样接入后，AI 助手查询项目时就有了明确路径：先看图谱里的节点和关系，再回到具体文件核对细节。

## 常用技巧与最佳实践

如果只把 Graphify 当作个人工具，它已经能提升项目理解效率。

放到团队里用时，它还可以变成一份共享的项目资料。

`graphify-out/` 可以提交到 git。团队成员拉取后，不一定每个人都要从零生成图谱。

一种推荐流程是：

1. 1\. 一个人在项目里运行 `/graphify .`。
2. 2\. 提交 `graphify-out/` 。
3. 3\. 其他人拉取代码后，AI 助手可以直接读取图谱。
4. 4\. 后续通过 `--update` 或 hook 机制增量更新。

为了避免把不稳定或本地化文件提交进去，可以在 `.gitignore` 里加入：

```
graphify-out/manifest.json
graphify-out/cost.json
# graphify-out/cache/ 可按团队需要决定是否提交
```

如果你不希望某些文件进入图谱，可以在项目根目录创建 `.graphifyignore` 。它的语法和 `.gitignore` 类似，也支持 `!` 取反。

例如：

```
# .graphifyignore
node_modules/
dist/
*.generated.py

# 只索引 src/，忽略其他内容
*
!src/
!src/**
```

团队协作里还有一个实用命令：

```
graphify hook install
```

它可以在 git commit 后自动重建图谱。对于代码 AST 部分，这个过程没有 API 成本。同时它还会设置 git merge driver，避免 `graph.json` 在多人并行提交时留下冲突标记。

如果有多个图谱需要合并，也可以使用：

```
graphify merge-graphs a.json b.json
```

也要提前说清楚，Graphify 解决的是「项目知识关系化」这类问题，工程判断仍然要靠人来做。

图谱质量首先取决于输入质量。代码命名混乱、文档过时、注释错误，都会被带进图谱里。

`INFERRED` 和 `AMBIGUOUS` 关系也不能直接当结论用。它们更像提示：这里可能有关联，但需要人工复核。

另外，隐私和成本也需要提前评估。

代码文件会通过 tree-sitter 在本地处理，不会离开你的机器。视频和音频也可以通过 faster-whisper 本地转录。

但文档、PDF、图片等非结构化内容，通常会发送给你的 AI 助手或配置的模型后端做语义抽取。如果是企业项目、客户资料、未公开论文或敏感设计文档，就需要先确认数据边界。

在 headless 或 CI 场景下，Graphify 也支持通过环境变量指定不同后端，例如：

| 环境变量 | 用途 |
| --- | --- |
| `ANTHROPIC_API_KEY` | Claude 后端 |
| `GEMINI_API_KEY`  或 `GOOGLE_API_KEY` | Gemini 后端 |
| `OPENAI_API_KEY` | OpenAI 或兼容 API |
| `MOONSHOT_API_KEY` | Kimi Code 后端 |
| `OLLAMA_BASE_URL` | Ollama 本地推理地址 |
| `AWS_*`  或 `~/.aws/credentials` | AWS Bedrock |

所以，使用 Graphify 前最好先划清边界。

哪些文件应该进入图谱？哪些文件应该忽略？哪些资料可以发给模型？哪些内容只能本地处理？

这些问题先定下来，后面生成出来的图谱才更可靠。

回到最开始的问题：AI 编程当然需要上下文，但更长的窗口并不总能解决项目理解的问题。很多时候，更缺的是一套稳定的上下文结构。

Graphify 的作用，就是把分散在代码、文档和外部资料里的线索整理出来，让 AI 在提问时能顺着关系查，少一些重复翻文件的工作。

对于复杂工程来说，这个变化不一定显眼，但很实用。

**GitHub 地址** ：https://github.com/safishamsi/graphify

#### 引用链接

`[1]` python.org: *https://www.python.org/downloads/*

**既然看到这里了，如果觉得有启发，随手点个赞、推荐、转发三连吧，你的支持是我持续分享干货的动力。**

推荐阅读： [LLM Wiki 架构解析：Karpathy 的 Markdown 知识库模式](https://mp.weixin.qq.com/s?__biz=MjM5NzA1NzMyOQ==&mid=2247487035&idx=1&sn=16227b052787487b3c93004bbe5ee198&scene=21#wechat_redirect)

**微信扫一扫赞赏作者**

AI编程 · 目录

继续滑动看下一个

技术极简主义

向上滑动看下一个