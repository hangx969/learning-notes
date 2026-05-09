---
title: "Claude Code+Obsidian ：让 AI 当你的知识管家"
source: "https://mp.weixin.qq.com/s/pSMue0paT9sQXOWhP0t1lg"
author:
  - "[[强西]]"
published:
created: 2026-05-09
description: "你不需要成为笔记达人。你只需要把笔记存成 AI 能直读的格式，然后让 AI 接管剩下的事。"
tags:
  - "clippings"
---
强西 *2026年5月6日 21:03*

> 你不需要成为笔记达人。你只需要把笔记存成 AI 能直读的格式，然后让 AI 接管剩下的事。

---

## 你的笔记软件里躺着多少僵尸

回忆一下，你上次打开笔记软件是什么时候？不是打开来记东西，而是打开来 **找东西、复用东西** 。

大概率你找不到。

我自己以前的状态是这样的。

印象笔记里躺着 2018 年收藏的文章，已经忘了为什么收藏。备忘录里塞满随手记的想法，但这些想法之间没有任何关联。

微信收藏夹里那成百上千篇"以后再看"——从此以后真的再也没看。

我记下来的不是知识，是 **信息的坟场** 。

不是不努力。每条笔记记录的当下都是有价值的。但从"记下来"到"用起来"中间隔着一道鸿沟——整理、关联、检索、复用，这件事人脑天生不擅长。

直到我把笔记搬到 Obsidian，把 Claude Code 接进来，让 AI 当全职管理员之后，这道鸿沟才算迈过去。今天分享我搭这套体系的过程，给你一份能直接抄的路径。

## 先说结论

**Obsidian + Claude Code 是 2026 年个人知识管理的最优解** ——前提是你做的是个人知识管理，不是团队协作。

理由三句话：

第一，Markdown 是 LLM（大语言模型）的母语。你的笔记格式决定了 AI 能帮你到什么程度。  
第二，本地文件让 AI 零摩擦读写。Obsidian 的 Vault 就是一个 Markdown 文件夹，Claude Code 进去是有完整权限的管理员，不是隔着 API 传话的外人。  
第三，AI 时代"整理"这件事不再是人的责任。你只管记录和思考，整理交给 AI。

下面分两块讲：为什么是这两个，以及怎么把它们接起来。

## 为什么是这两个组合

### Markdown 是 LLM 的母语

大语言模型的训练数据里，Markdown 是最主要的格式之一。GitHub 上几十亿个 README.md、技术文档、博客文章、教程，AI 全读过。它对 `##` 标题、 `**加粗**` 、 `-` 列表的理解，像你对中文标点一样自然。

具体三个特性：

**Token 效率** 。

同样的信息，用 Markdown 表示比 JSON 或 XML 紧凑很多（花叔手册里给到 30-50% 的差值，自己跑过一次类似比例）。

意味着同样的上下文窗口能装下更多笔记。Claude 1M token 大窗口大概能放下中等规模的整个知识库——对绝大多数人来说，纯文本 + 长上下文这套已经够用，根本不用先去搞向量数据库。

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

**Manus** ，AI Agent 公司，2026 年 Meta 拟以 20 亿美元收购，后被中方监管叫停（这事本身就够写一篇）。Manus 的 Agent 在执行长任务时用什么存记忆？ `task_plan.md` 和 `notes.md` ——Markdown 文件。

**OpenClaw** ，开源 AI Agent 框架，GitHub 上 35 万 + 颗星。Agent 的知识存在哪？ `MEMORY.md` 。Agent 的人格定义存在哪？ `SOUL.md` ——还是 Markdown 文件。

**Claude Code** ，Anthropic 自家的 AI 编程工具。项目上下文存哪？ `CLAUDE.md` 。用户长期记忆存哪？ `memory/` 目录下的 Markdown 文件。

三个不同的团队，解决不同的问题，服务不同的用户。在没有互相参考的情况下，做出了同一个选择： **用 Markdown 文件作为 AI Agent 的记忆层** 。

不是向量数据库，不是 SQL，不是 JSON。就是 `.md` 文件。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

## 怎么把它们接起来——30 分钟上手

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

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
\\`\\`\\`yaml
---
title: 笔记标题
tags: []
created: YYYY-MM-DD
type: fleeting | literature | permanent
summary: 一句话摘要
---
\\`\\`\\`

## 行为规则
- 可以：加标签、建 [[双向链接]]、生成摘要、整理分类
- 不可以：删除已有笔记内容、修改原始记录
- 创建新笔记必须遵循 Front Matter 模板
```

这份手册不需要一上来就完美。三五行起步，每次 Claude Code 犯错就加一条规则——半年下来它会自然长成一份很详尽的指南。

### 第三步：每个大目录补一份 index.md

Claude Code 进入一个文件夹，看到 50 个文件需要逐个扫描判断。但如果你在文件夹里放一份 3-5 行的 `index.md` ，它先读这一份，3 秒钟就知道这里是干嘛的、关键文件在哪。

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

这个习惯我做下来之后效率提升非常明显。原来 Claude Code 每次都要 ls 一遍才能定位，现在直接定向跳进对应文件夹拿上下文。

### 第四步：装 obsidian-skills

最后一步。Obsidian 的 Markdown 有些独有语法（ `[[wikilinks]]` 双向链接、callout 提示框、`.canvas` 空间笔记），Claude Code 默认不一定懂——它可能把 `[[]]` 当成普通 Markdown 链接处理，搞坏格式。

Obsidian CEO kepano 亲自做了 `obsidian-skills` 这套官方 Skill 集，教 Claude Code 正确处理这些非标准语法。安装就一行命令：

```
cd ~/Obsidian/我的vault
git clone https://github.com/kepano/obsidian-skills.git .claude/skills/obsidian-skills
```

下次 Claude Code 启动时会自动加载，从此处理 `[[]]` 、callout、`.canvas` 、`.base` 都不会出错。

到这里 30 分钟够了。

## 装完之后让 AI 帮你做的第一件事

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

MakeUseOf 有一位作者的案例值得参考——5 年笔记没标签、没链接、没结构、试过三次手动整理都放弃的烂账，他用 Claude Code + Obsidian 90 分钟整理完。我没那么多年的笔记可整，但跑了一遍我自己散落在备忘录里的几百条素材，5 分钟就跑出了第一版分类——比我预期的快得多。

## 想再玩深一点的三个方向

整理完之后大概率你会想要更多。这里给三个进阶方向，按性价比排序，不一定全做但都值得知道。

### 方向一：让 AI 把笔记编译成可复用的 wiki

这个思路来自 Andrej Karpathy 2026 年 4 月那条 1600 万浏览的推文。

他说的核心是一个观点转换： **AI 不是检索器，是编译器** 。

RAG（检索增强生成）的逻辑是每次提问都重头搜索原始材料、拼接、生成回答，回答用完即弃，下次再问还得从零开始。但 AI 也可以把读过的素材 **编译成结构化的 wiki 文章** ，文章被保留、被迭代、被交叉引用——下次提问基于已编译的 wiki 回答。

落到 Obsidian 里就是 raw → wiki → output 三层结构：

```
Vault/
├── raw/      # 你扔进来的原始素材，只增不改
├── wiki/     # AI 编译过的可复用知识
│   ├── concepts/   # 概念页（每个概念一篇）
│   ├── entities/   # 人物 / 产品页
│   └── topics/     # 主题分析页
└── output/   # 基于 wiki 生成的报告 / 分析
```

每次写完一篇文章，让 Claude Code 把里面"可独立成立的知识点"提炼到 wiki/。下次写相关主题时它先读 wiki，不重新调研。我自己改造素材库时把这个落进去了，三层加配套的 SCHEMA.md（写清楚命名规范、Front Matter 模板、 `[[]]` 规则），效果是知识从一次性消耗变成永久资产。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

这一步的重点不是装新工具，是 **改变心智** ：让 AI 在你这边累积，而不是每次重置。

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

### 方向三：把 Claude Code 嵌进 Obsidian，加语义搜索

如果你已经经常切窗口（Obsidian 看 → 终端跑 → Obsidian 看），三个插件能让体验提一档：

**Claudian** ：把 Claude Code 的对话界面嵌进 Obsidian 侧边栏。右侧给指令、主编辑区实时看到笔记变化，少了一次 Alt+Tab。

**Smart Connections** ：Obsidian 自带搜索是关键词匹配——搜"投资"找不到"资产配置"。Smart Connections 用 AI embedding（把笔记转成向量）给 Vault 建语义索引，相关概念都能搜到。打开任何笔记时侧边栏自动显示语义最近的其他笔记，经常会发现自己没意识到的关联。

**Copilot for Obsidian** ：Vault 级别的 RAG 问答。问"我之前关于定价策略写过什么"，它从你自己的笔记里答，每个观点带出处。和直接问 ChatGPT 的区别是——回答来自你自己的知识，不是互联网通用信息。

三个不必都装。我自己优先级是 Smart Connections > Claudian > Copilot——语义搜索是日常每次都用的，回报最稳；Claudian 是体验优化，看你切窗口频率；Copilot 是有了一定笔记规模（500 篇以上）才真值得装的，否则可问的东西不够。

## 我用了一周后的几个判断

我刚跑完一阶段 Obsidian + Claude Code 这套体系的搭建（包括术语统一、wiki 三层架构、Front Matter 升级等改造），分享几个非翻译稿层面的真实体感。

**一定做的三件事** ：装 obsidian-skills、补 index.md、Front Matter 加 type 和 summary 字段。这三件投入不超过 1 小时，但日常每次操作都受益。尤其 type 字段的三态（fleeting / literature / permanent），AI 扫 Vault 时按 type 决定处理策略，这件事一旦开始用就回不去了。

**不要照抄大博主们 Skills 的做法** 。一上来不要装一堆 Skill，那是他用了一年多积累出来的。先用几个月，等你明确知道自己缺什么能力的时候，再去找对应的 Skill——否则你只是在收集工具不在解决问题。

**多 Vault 不要太早搞** 。先用一个 Vault，500 篇以下别拆。等到出现两类内容 **完全不交叉** （比如工作机密 vs 个人日记，或者写公众号 vs 学术研究）、且你确实在频繁切换上下文时才拆——过早拆分会增加管理成本而不解决任何问题。

**先写后整理** 。我自己第一次搭体系时踩过的最大坑是"系统先行"——花一下午研究各种方法论、设计完美分类，一周后发现实际笔记根本不符合预设，整套推翻重来。后来想明白笔记系统得从笔记里长出来，不是从设计图纸里长出来。

**40 万字以内不需要向量数据库** 。Claude 的上下文窗口够大，纯文本 wiki + index.md 导航，AI 找到相关知识的速度和准确度都很高。超过百万字级别再考虑加语义搜索。

## 最后一句

这套体系的核心不是 Obsidian，也不是 Claude Code。是 **整理这件事不再是你的责任** 。

过去几十年所有的笔记工具，从 Word 到 Notion，都假设"整理是你的事"。AI 改变的是这个假设——你只管记录和思考，整理交给 AI。

工具会变。今天是 Obsidian，明天可能是别的。但你 Vault 里的那些 Markdown 文件，它们一直是你的。

我搬完一周，没打算搬回去。

要试的话路径很短：找一篇你最近想存的文章存成 `.md` ，扔进一个新建的文件夹， `cd` 进去 `claude` 起个对话——剩下 AI 会问你三个问题然后开始干活。

**微信扫一扫赞赏作者**

继续滑动看下一个

强西

向上滑动看下一个