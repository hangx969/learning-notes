---
title: OpenClaw Skills 与插件
tags:
  - AI
  - openclaw
  - skills
  - plugin
aliases:
  - OpenClaw插件
  - OpenClaw技能
---

# OpenClaw Skills

OpenClaw 可以添加很多 Skill 以提升自身的能力，skills 可以从如下地址下载：

- OpenClaw 官方 Hub：[https://clawhub.ai/](https://clawhub.ai/)
- OpenClaw 实用 Skills 集合：[awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills)

---

## Skills 管理工具 Clawhub

> [!info] 教程文档
> [Clawhub 文档](https://docs.openclaw.ai/zh-CN/tools/clawhub)

Clawhub 是由 OpenClaw 官方提供的 Skill 管理工具，可以用该工具搜索、安装、升级或卸载 skill。首先安装该工具：

```sh
npm i -g clawhub

# 登录
clawhub login --token <从clawhub注册登录拿到CLI token>

# 搜索
clawhub search "pdf"

# 安装
clawhub install pdf
```

> [!note]
> 用 clawhub 安装的 Skills 默认是装在当前 Agent 的工作目录中的 Skills 里，是局部的。想要装成全局 Skills，需要手动安装。

---

## 手动下载 Skills

- 在 [clawhub.ai](https://clawhub.ai/) 上找到想要的，下载到 OpenClaw 的工作目录下的 `skills` 目录下即可（没有就创建一个）
- 可以在 WebUI 的"技能"中查看到安装的 Skills

> [!note]
> 第一次运行某个新 skill 的时候可能速度会比较慢，因为会安装一些依赖包。

---

## 办公 Skills

下载了如下 skills：

- [powerpoint-pptx](https://clawhub.ai/ivangdavila/powerpoint-pptx)
- [pdf](https://clawhub.ai/awspace/pdf)
- [xlsx-cn](https://clawhub.ai/guohongbin-git/xlsx-cn)

解压拷贝到 `.openclaw/skills` 目录下。

### 总结 PDF 内容

总结 PDF 时，需要给予 OpenClaw 具体的 PDF 路径或者文件名，否则会全盘扫描。

### 生成 Excel 表

提供一些源数据，生成一个 Excel 文件：

- 请帮我根据这些信息生成一个 Excel 文件，需要包含图表，并存储在桌面的 `xxx.xlsx` 文件内

### 生成 PPT

帮我生成一个 PPT，这个 PPT 是关于 OpenClaw 介绍相关的，只需要生成三页 PPT 即可，注意你需要先列出来大纲，然后再生成 PPT。请注意你需要使用桌面的 `openclaw.pptx` 模版进行生成。

---

## 自我进化 Skills

> [!info] 地址
> [self-improving-agent](https://clawhub.ai/pskoett/self-improving-agent)

这个 skill 不是"多了一个命令"，而是给 agent 加了一套行为模式：

> **做事 → 复盘 → 记录纠正 → 沉淀经验 → 下次改进**
> **当 agent 出错、被纠正、完成重要任务、或发现更优方法时，让它主动复盘并把经验沉淀为长期规则。**

它的目标不是单次答对，而是**越用越会做**。

**用法**：

1. 用法 1：出现错误时直接触发
2. 用法 2：做完一个重要任务后让它复盘
3. 用法 3：把你的偏好沉淀进去

---

## 个人知识库 - second-brain

> [!info] 地址
> [second-brain](https://clawhub.ai/) | 来源：[Openclaw帮你管理个人知识库](https://mp.weixin.qq.com/s/kEomUUhk3Fw6XcdT7m5X_Q)

second-brain 是 ClawHub 上的知识管理插件，名字直译就是"第二大脑"。把各种输入（读书笔记、会议记录、灵感碎片、文章摘录）统一存进一个结构化的**本地知识库**，用 AI 帮你检索、整理、关联。

与普通笔记软件的核心区别：**不需要手动分类整理**，直接把内容扔给它，它自己理解语义、建立关联。下次用自然语言问它，它从知识库里把相关内容找出来，不依赖你记得存在哪个文件夹。

### 安装与配置

```sh
clawcli install second-brain

# 初始化知识库存储路径（默认存在本地，不上云）
clawcli config second-brain --storage-path ~/second-brain
clawcli config second-brain --init

# （可选）自动备份到同步盘
clawcli config second-brain --backup-path ~/Dropbox/second-brain-backup

openclaw restart
```

### 使用方式

直接用自然语言和 OpenClaw 对话即可，它识别意图并调用 second-brain：

| 操作 | 示例 |
|------|------|
| 存笔记 | `记下来：《思考，快与慢》里说的锚定效应——人在做判断时会过度依赖第一个接收到的信息` |
| 存会议记录 | `整理这段会议记录并存档：[会议内容]` |
| 查询 | `帮我找找知识库里和定价策略相关的内容` |
| 按时间回顾 | `帮我列出这周存进去的所有笔记` |
| 主题聚合 | `帮我整理一下知识库里所有和远程工作、效率管理相关的笔记，按主题归类` |
| 知识连线 | `我最近记录的这条关于专注力管理的笔记，和我之前记过的哪些内容有关联？` |

### 核心能力

- **语义检索**：用自然语言查询，不需要记得存在哪里
- **自动关联**：存入时自动记录来源、打标签、与已有知识建立关联
- **主题聚合**：把散落各处的笔记按主题整理汇总
- **知识发现**：发现不同笔记之间你没有意识到的关联

> [!note] 与记忆插件的区别
> second-brain 侧重**主动的知识管理**（存笔记、按主题检索、知识关联），下面的 memos-local 记忆插件侧重**对话上下文的持久化记忆**。两者互补。

---

## 记忆插件

> [!info] 文档
> [memos-local-openclaw-plugin](https://memos-claw.openmem.net/docs/index.html#quickstart)

OpenClaw 自己本身也有内建 memory 机制（`MEMORY.md` / `memory*.md` + `memory_search`）。而这个 `memos-local-openclaw-plugin` 是**memory 类插件**，**本地 SQLite 存储**。

部署完成后可以可视化查看存储起来的 memory（`127.0.0.1:18799`）。

---

## 安全审计 - skill-vetter

> [!info] 地址
> [skill-vetter](https://clawhub.ai/spclaudehome/skill-vetter)

这个 skill 是 spclaudehome 做的，下载量 30000+，LobeHub 评分 4.96/5。它本身是一个纯文档型 skill，没有任何可执行代码，说白了就是一套安全审查协议。装上之后，每次你要安装新的 skill，它会引导你走四步审查流程：先查来源（作者信誉、GitHub 活跃度、Star 数量），然后做代码审查（扫描数据外泄模式、credential 访问、`eval()` 调用、可疑网络请求），再分析权限范围，最后给出风险评级，分 LOW、MEDIUM、HIGH、EXTREME 四个等级。

---

## 浏览器搜索和互联网平台信息抓取

Agent-browser & Agent-Reach

> AI Agent 最大的痛点是什么？看不到外面的世界。这两个配合起来，基本上让你的 OpenClaw 长出了眼睛和手。

### Agent-browser

> [!info] 仓库
> [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser)

Agent-browser 是 Vercel Labs 用 Rust 写的无头浏览器自动化 CLI，GitHub 19600+ stars。Agent-browser 其实不算是 Skill，本质上是个无头浏览器工具。

跟传统的浏览器自动化工具比（Puppeteer、Playwright），它最大的不同在于用 accessibility-tree 快照生成稳定的元素引用，类似 `@e1`、`@e2` 这种标记。传统 CSS 选择器在页面变动时很容易失效，但这种基于 accessibility-tree 的引用要稳定得多，对 AI Agent 来说简直是刚需。

除了基本的页面导航和元素交互，它还支持截图、PDF 生成、网络请求拦截、视频录制，甚至能做像素级 diff 对比。

```sh
npm install -g agent-browser
agent-browser install  # 下载Chromium，linux下加上 --with-deps 安装依赖
npx skills add vercel-labs/agent-browser
```

Claude Code 和 OpenClaw 都能用。

**场景：Web 数据采集**

需要从某个网站收集一些公开信息？以前要么手动复制，要么让 AI 写爬虫脚本。现在可以让 AI 直接用 agent-browser 操作：打开页面、获取元素、提取文本，整个流程在对话中就能完成。

### Agent-Reach

这个 skill 解决的是另一个大问题：让 AI Agent 免费访问各大平台的内容。Twitter/X、Reddit、YouTube、GitHub、B 站、小红书，都能通过它来搜索和读取，关键是不需要任何 API key。

它背后用的是 xreach CLI 读 Twitter、yt-dlp 读视频、Jina Reader 读网页，这些都是成熟的开源工具。写文章做调研的时候就靠它，先跑一下 `agent-reach doctor` 检查哪些渠道可用，然后按需调用。

Claude Code 和 OpenClaw 都能用：

```
帮我安装 Agent Reach：
https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

---

## 百度搜索 Skill

### 背景

Browser Agent、Playwright：帮我登录公众号排版，帮我登录 12306 买票。但现实是，所有平台都非常介意这种事。严重一点直接封号。小红书已经封过一批了。公众号都只敢拿小号。所以 Browser Agent 之类 Skill 看起来很酷，但目前很多场景其实不敢用。

我反而认为最重要的一个 Skill，是搜索。为什么？因为如果不装搜索 Skill 的话，模型是没有最新知识的。

> [!question] 模型不是也有搜索能力吗？
> 是这样没错。但 OpenClaw 接模型的方式是通过 API，API 里是没有搜索的。搜索是 Chat 产品层额外做了一层插件。现在没有哪个模型有原生搜索的能力。
>
> 所以如果你在 OpenClaw 里不装搜索 Skill，模型就是个半瞎子。因为模型的知识是有截止日期的。很多最新的信息，比如新闻、公司动态、产品更新，模型基本上都不知道。所以有的时候它就会一本正经地胡说八道。

这也是为什么在 OpenClaw 生态里，搜索类的 Skill 下载量一直非常高。大家都意识到了，Agent 只要你想让它真正干活，它必须得有眼睛。就像我们自己，现在干活要是没有搜索引擎的话，基本上就没办法干了。

而搜索类 Skill，我强烈推荐国内用户还是用百度的 Skill。之前我也装过 Brave Search Skill，但真实的体感是中文领域的搜索效果，百度仍然最好。

### Skill 地址

[baidu-search](https://clawhub.ai/ide-rea/baidu-search)

装完之后，需要配一个 API Key，可以在下面的地址申请。目前每天有免费额度福利，也不需要绑定信用卡，还是很方便的。

[百度 API Key 申请](https://console.bce.baidu.com/qianfan/ais/console/apiKey)

---

## 可视化面板

> [!info] 仓库
> [ClawDeckX](https://github.com/ClawDeckX/ClawDeckX/tree/main)

这个比较好看：

```sh
systemctl --user status clawdeckx
systemctl --user stop clawdeckx
systemctl --user start clawdeckx
```
