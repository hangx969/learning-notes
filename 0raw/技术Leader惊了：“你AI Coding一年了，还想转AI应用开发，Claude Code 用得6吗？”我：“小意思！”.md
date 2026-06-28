---
title: "技术Leader惊了：“你AI Coding一年了，还想转AI应用开发，Claude Code 用得6吗？”我：“小意思！”"
source: "https://mp.weixin.qq.com/s/td5iPyNd0Qcgq5gmdx179Q?scene=1&click_id=1014036589"
author:
  - "[[沉默王二]]"
published:
created: 2026-06-28
description:
tags:
  - "clippings"
---
沉默王二 沉默王二 *2026年6月22日 15:47*

大家好，我是二哥呀。

相信大多数小伙伴和我一样，日常的开发基本上都交给了 Claude Code 和 Codex。

短时间内，这两个 Agent 应该就是使用频率最高的应用。

所以，今天必须得给大家推荐两样东西，非常非常重要。

第一个是 `/powerup` 命令。

![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu1VfSUhk8NqaXoJWb5WdAib0jrAtQoO72ncibCh6zFXicPt2IM2FEDamVb69HDciaoWnDFWKFJIcnsxZIlxAicibg4XUo9ebXFLoogQA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

这是 Claude Code 官方提供的一个学习 Claude Code 命令的交互式引导课程。它会逐个功能引导你体验 Claude Code 的各种能力，从上下文管理到会话恢复，从代码审查到自主模式，每个功能都有一段互动式的演示。

第二个要推荐的这个在线网站：https://learn.shareai.run/zh/

![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu0yRvwpETM3EEgc0u1bc9VBLYV9hh0X6QI6XyK3w5D0A5Z447GriasialNEiasOmj0OsYx1BUf4xoHeL4ibacU91GNntPBKiaCA4DgA/640?wx_fmt=png&from=appmsg#imgIndex=1)

这个网站的定位不是用户手册，而是通过源码逆向工程拆解 Claude Code 的内部架构。全站 20 个章节，从最简单的 Agent 循环开始，每一章叠加一个机制，最终构建出一个完整的 AI Agent 系统。

它把 Claude Code 分成了五层架构：

![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu1hzYTRaHhtjIuRbMHly26urxz72s6k2Vf9NS9WiaWczgJfOZpFRYPMmuab40050iaynicl7It5ND4iaOCx3EcibV8HpCojIx2yBSoE/640?wx_fmt=png&from=appmsg#imgIndex=2)

- **L1 工具与执行** ：Agent 能做什么（工具注册、分发表模式）
- **L2 规划与控制** ：如何组织工作（TodoWrite、Subagent、Skill 加载）
- **L3 内存管理** ：在上下文限制内维持记忆（四层压缩管线、Memory 系统）
- **L4 并发与调度** ：后台执行和定时任务（Background Tasks、Cron Scheduler）
- **L5 多 Agent 平台** ：Agent 团队协作（消息总线、Worktree 隔离、MCP）

想理解 Claude Code 内部原理的小伙伴，这个网站必看。知道命令背后的机制，才能在遇到异常情况时快速判断问题出在哪一层。

哦，还要再推荐一个：https://claude.nagdy.me/learn/slash-commands/

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/rZm1sEcvdu1s9iaGu0TX5jYj0mHqdP7bPdnAMu2Uy2eudWE6MJTDxJBpu24zw68myYJVrjicaWBlhSaeRdJyZ2y48cs1LZdk7JJH2EicJ2nwmA/640?wx_fmt=png&from=appmsg#imgIndex=3)

这个网站更偏实用，是一本结构清晰的 Claude Code 速查手册。所有斜杠命令按功能分组（上下文管理、会话工具、配置、诊断、代码审查、高级功能），每个命令都有说明和参数列表。

除了斜杠命令，它还覆盖了 CLI 标志（ `-p` 非交互模式、 `--permission-mode` 权限模式、 `--sandbox` 沙箱隔离等）、权限模式详解（default / acceptEdits / plan / auto / dontAsk / bypassPermissions 六种模式的区别）、环境变量配置、配置文件路径层级。

两个网站一个讲原理、一个讲用法，搭配着看效果最好。

> 让我们开始吧，走起～

## 01、从 /powerup 开始

在 Claude Code 里直接输入 `/powerup` ，它会启动一个交互式的功能发现课程。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/rZm1sEcvdu0bvDic2C1dcpjojMoJ0MGoCObxYfib0NpxkymwXVrOJrbJDGmbHlo3BEbGAopnlokSVdFB3k2b0barYEXHVyVZOUNxuZb2NcSTA/640?wx_fmt=png&from=appmsg#imgIndex=4)

不是甩一堆文档自己看，而是逐个功能引导体验。

比如 Shift+Tab 可以切换权限模式、 `/goal` 可以设定条件让 Agent 自主干活、 `/branch` 可以创建并行对话分支。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/rZm1sEcvdu1iaB3emchibqTgcunctwPzBTY1J9pjNSWzbibaOgSJy2UHBYH5JYJa8O16SNlVsgGWDlntZ1gD4RKSS2cdCGuO0ic4hUaw1TFfUvc/640?wx_fmt=png&from=appmsg#imgIndex=5)

建议每个人都跑一遍。

![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu3bu3UrNZS9endP7GaELN6nDEkC6b2ib4qwOgOgRCBwD8TKuwG60Rzbak87EHIDD6HsarQmMGwFa0fq5F49tlxzzpjfI4EPbRAk/640?wx_fmt=png&from=appmsg#imgIndex=6)

## 02、上下文管理

Claude Code 最核心的资源是上下文窗口。

上下文管理做得好不好，直接决定了一次对话能完成多大的任务。

对话越长，上下文消耗越大，消耗完了 Agent 就开始“失忆”——前面讨论过的决策、确认过的方案，可能都会丢失。

相信大家都会遇到过，明明一开始很聪明，跑着跑着就感觉 Agent 变蠢了。

举个例子，我平常会用 Codex 生图，但如果上下文太长，我这个小人就会变成三毛，搞笑的很。

![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu13gaJsXAYLVUiarOic6qaw43jhYN2Ju59Ahibq5qOnwNvwvx93c1kUuUcJ6b7ZUgmy4B4JFcxTwvwGiceibkefG3JiaKibSpUGNticPzE/640?wx_fmt=png&from=appmsg#imgIndex=7)

### /context

输入 `/context` ，终端会显示一个彩色网格，用颜色表示上下文的使用状况：空白越多表示空间充足。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/rZm1sEcvdu1gpT4Jr0LGibiavprIFmDicBpUV8MWcYxD0El05NVLxctuhuWE8V4xic0uVNM1paAIkguxQhemabaHhrYdzoFgS7gDSGDkAialnjo4/640?wx_fmt=png&from=appmsg#imgIndex=8)

我的习惯是每做完一轮大的代码改动之后先看一眼 `/context` ，根据空间决定是继续干还是先压缩一轮。

免得压缩后丢掉重要的信息。

### /compact

`/compact` 会把对话历史压缩，释放上下文空间，同时保留关键信息。

一般情况下直接 `/compact` 就行，Claude 会自动判断什么重要什么不重要。但如果对话里有明确需要保留的内容，可以带上指令：

```
/compact 丢掉debug信息，但保留迁移方案的讨论
```
![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/rZm1sEcvdu3ibbpllQibUBJmickoOFY5DoPNuA5WlpybeNFxNPIaCZvLlH5OHFlpgxHMA6Ek9uic2lMxcHmIaTYibM1WxeKcLmgqZHY7wLOFmlZA/640?wx_fmt=png&from=appmsg#imgIndex=9)

这条命令的意思是保留迁移方案的讨论，丢掉调试过程中的大量试错信息。

对比无脑压缩，带指令的压缩精准得多。调试过程中的 500 行报错信息对后续工作毫无价值，但方案设计的结论必须留着。

### /clear

`/clear` 更彻底，直接清空整个对话重新开始。

![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu2oJ3Hpd4CcAA1bibpPrHsajhY2dlH4tDCoYkCAMyg2Let8gTcBzzUjVqJAgibXIe9Vgo3aNM4HfXiaYY8ILdbycrHzeP5jBjnprA/640?wx_fmt=png&from=appmsg#imgIndex=10)

和关掉终端重新打开不同的是， `/clear` 会保留 CLAUDE.md 里的项目配置，所以不用担心项目指令丢失。

我的使用策略：修 bug 或者小改动用 `/compact` 续命，完成一个完整模块或者对话方向需要大调整时用 `/clear` 重启人生。

哈哈。

## 03、会话管理

Claude Code 的对话默认是一次性的——关掉终端就没了。但会话管理命令可以让工作状态跨终端、跨时间保存下来。

### /resume 和 /rename

`/resume` 恢复之前保存的会话。直接输入 `/resume` 会列出最近的会话供选择，也可以 `/resume auth-refactor` 按名称直接恢复。

![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu0tAdIY00bx9Oc4ffOQ1Z3Kbp2dgn9ROrqthecjib6xExptL9Kw3qaPHB8FiaqfUM03kicTu4DwFOyYqroIhoF2uSZEibM4v0JAKoQ/640?wx_fmt=png&from=appmsg#imgIndex=11)

搭配 `/rename` 使用效果最好——每次开始一个新任务先 `/rename auth-refactor` 给会话起个名字。

![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu3VdTKnkL93Y7YgshicKtGemVpD2SlOc4ckHBgDibXZUgOBD522QCLRxeUS02HYDYR2RuLrl8xibU9ojyjibZ9eIewyEbcV1B8ySlg/640?wx_fmt=png&from=appmsg#imgIndex=12)

后面恢复的时候一目了然。

### /branch

`/branch` 从当前对话状态创建一个并行分支，两个分支互不干扰。

使用场景：和 Claude 讨论到一半，有两个方案都想试试。

![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu2yicooFElo69Nc5dYcQXiclicuyc5KI4K6mQGGjcPADqiawLd2qjjoiaqcgMe7GsBGibO6bWZSicIsJmVic5DOl4hibRMV6fUxUgPo1618/640?wx_fmt=png&from=appmsg#imgIndex=13)

以前只能选一个先做，不行再推倒重来。现在 `/branch` 创建分支，在分支里试方案 A，在原来的会话里试方案 B。哪个好用就留哪个，另一个直接丢掉。

这个命令把“试错成本”降到了几乎为零。

### /rewind

`/rewind` （别名 `/undo` ）回滚到对话中更早的某个点，可以选择同时回滚文件变更。

![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu3nINNmicnCXibiakhLPC6vyJswXO6XJpxLebNsgkfYl91I8MuNMd0h8ov8m28ESnxh5V9HF0nTNsWaxZkRx3A2go6jl8LE4VHReM/640?wx_fmt=png&from=appmsg#imgIndex=14)

Agent 改了不该改的文件，或者走了一条错误的路径， `/rewind` 一键回到出问题之前的状态。比手动 `git checkout` 恢复文件再重新对话高效得多。

### /recap

可以随时 `/recap` 手动触发一行会话摘要，提示之前在做什么。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/rZm1sEcvdu16mJmUCxnMTcjZgKnhibtnSEHRpIPzyKIJXYaLoeQUDJNA7Q5gnbwUq7ISWa2Sib3AFLGhHt8DtMv1SrkPhsGY3HhGY9JoibA7BQ/640?wx_fmt=png&from=appmsg#imgIndex=15)

## 04、模型和推理控制

接下来，这三个命令控制 Claude Code 的“大脑”——用什么模型、思考多深、跑多快。

### /model

`/model` 在 Sonnet、Opus、Haiku 之间切换。除了直接选模型名，还支持别名： `best` 会选当前最强的模型。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/rZm1sEcvdu0eHOHcS5vFeYqTnyqAEjNnibks3xiaGKu3KjGjb9vDjSAhABYBEXLMibibRd8Hcj1xNBNplzmMOsInTrmZOgfibKwdb2ImA9bphaia8/640?wx_fmt=png&from=appmsg#imgIndex=16)

实测下来，日常编码 Sonnet 足够用，遇到复杂架构设计或者大规模重构再切 Opus。Haiku 适合做简单的格式转换、批量改名这种不需要深度推理的活，速度快，费用低。

### /effort

`/effort` 设置推理深度，从 low 到 max 一共五个级别。

![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu3UQSnyW7SuOOgCR1PwIVHxRsLAJzQ8yiaAyTXdf1icATe2NvuVT9rq679dY1H7c9BLzeq0vOyQ4Ml78szfnqWLpRX7xibjkuFRvE/640?wx_fmt=png&from=appmsg#imgIndex=17)

- **low** ：快速响应，适合“这个函数的参数是什么”这类简单查询
- **high/max** ：深度推理，适合“这段代码为什么在并发场景下偶尔报错”这类需要仔细分析的问题

当前会话的 effort 设置只在本次会话生效。如果想全局默认设置，可以通过环境变量 `CLAUDE_CODE_EFFORT_LEVEL` 来配置。

### /fast

`/fast` 开启 Fast Mode，这是 Opus 模型专属的加速模式，最高提供 2.5 倍的速度提升。启用后提示栏会显示 ↯ 图标。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/rZm1sEcvdu1Wd9V7Qr49JLx3mtZfvn0ExXEibxFmLFOZiaynwWicm20wfibdy9v2HljuYCXaH3yvOtA5rDnJbicAggQdCmtS3ia4CjT5Jo1HnEEFE/640?wx_fmt=png&from=appmsg#imgIndex=18)

代价是 token 费用更高。到达速率限制时会自动降回标准速度，不需要手动关闭。赶进度的时候可以开一下。

## 05、代码审查

这组命令是提交代码之前的最后一道防线。

### /code-review

`/code-review` 审查当前 diff 的正确性问题，支持不同的审查力度：

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/rZm1sEcvdu2X2dD8LKSV6NmkMpmLOHsLibusaZeMOaz0JyVuYuRzCN4NCMiavnKfTiaRXCYclECzRHz7GIr2OVj6iacHbQ9dcXRwhRykuYnhIN4/640?wx_fmt=png&from=appmsg#imgIndex=19)

- `low` / `medium` ：只报高置信度的发现，适合日常提交前快速扫一眼
- `high` / `max` ：覆盖面更广，会报一些不完全确定但值得关注的问题
![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu3mWDL5jJEI1rE7r3YRv2u4DicwesAYmKuJeWOHRFBIHCXZIldIuWfWCddUh7PdInTpuLpn5YBN6GN6SiaN2DNg4ADkDR5ouuJzc/640?wx_fmt=png&from=appmsg#imgIndex=20)

两个实用参数值得记住： `--comment` 会把发现以内联评论的形式发布到 PR 上， `--fix` 会直接应用修复到代码里。

### /diff

`/diff` 打开交互式 diff 查看器，直观地展示未提交的变更。比终端里的 `git diff` 可读性强很多，尤其是涉及多文件改动的时候。

![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu3CZs5OPPIgSQlGge9e2D3iclGicyKkvysw4TNaMCcEhTDaoLkRdGjTzH5dqXR3ekF2q8AgYYnqcibZaJBiargnZkRD53cnug5wlK4/640?wx_fmt=png&from=appmsg#imgIndex=21)

### /simplify

`/simplify` 专注于代码清理——找复用机会、简化逻辑、优化效率。

![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu2fwYZy46zvJzFTiajXiaQjVYFfO3RqyZ5mSLmdGb0WcJDHFXOaAdyfAksUmPfticXL4ISI8X2X0rFATLWa4D7sIyQ91LGHgJRTM4/640?wx_fmt=png&from=appmsg#imgIndex=22)

它不查 bug，只管代码整洁度。和 `/code-review` 搭配使用效果最好：先 `/code-review` 排查正确性问题，再 `/simplify` 清理代码质量。

## 06、自主模式

这组命令代表了 Claude Code 不同程度的自主性——从“先规划再动手”到“设条件让我自己干”。

### /plan

`/plan` 进入计划模式。Claude 会先研究项目结构、分析需求，然后提出一个分步实施计划。在计划被明确批准之前，不会修改任何文件。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/rZm1sEcvdu1PWOcoZrOmlJwKINk5kEUdLBhUzNllmAnqnEHnLicF8RRqfoQ8QyadicjjpuQhIU5Y44u559eHhaHqU59jqF4hXZN068mwFPvibI/640?wx_fmt=png&from=appmsg#imgIndex=23)

适合两种场景：一是对任务怎么拆解没有把握，想先看看 Claude 的思路；二是团队协作时需要先对方案达成共识再动手。

### /goal

`/goal` 是 Claude Code 自主性最强的命令。设定一个完成条件，Claude 会自主工作直到条件满足，执行过程中实时显示已用时间、对话轮次和 token 消耗。

```
/goal 提交所有已修改的文件/我要实现一个Claude Code
```
![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu2cvzl83KftBibRdIFYLdshf7VDNj7YzXic6pgymBu9YWtIZw8BAficaGPwGXy63AB3lwEAPicBZFoDucZ2UQzy39adj9icouowwKicw/640?wx_fmt=png&from=appmsg#imgIndex=24)

这个命令把 Claude Code 从“对话式助手”升级成了“自主执行的 Agent”。省去了每一轮对话里手动确认和推进的时间。

### /batch

`/batch` 用于大规模多文件变更。它会使用隔离的 git worktree 来协调工作，避免一次性改动太多文件导致混乱。

比如给项目里 50 个文件统一加 license header，或者把所有 REST API 调用从 v1 迁移到 v2，这种需要批量改动又怕改出问题的场景， `/batch` 就是干这个的。

### /loop

`/loop` 按固定间隔重复运行任务。

```
/loop 2m 检查一下最新一条待回复issue，并自动回复。
```
![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu1rIZDUYaeVAVaWjvkUcuiaP1NQtaNJYVcMc8YF6D6GasVmxql0VgTGwibiaEsqno0b0thYicBRpzJbBvJ9xVMVRbo54ZRcMwulYibA/640?wx_fmt=png&from=appmsg#imgIndex=25)

比如说我们可以 2 分钟检查一下 GitHub 上的 issue，然后让 Claude Code 自主回复。

## 07、快捷键

Claude Code 的快捷键数量不多，但每一个都很实用。

- **Shift+Tab** ：在权限模式之间循环切换（default → acceptEdits → plan → auto）。不用每次都打 `/permissions` 或者回答“是否允许”的弹窗，按一下就切到自动批准模式
- **Option+T** （macOS）/ **Alt+T** ：一键切换扩展思考（Extended Thinking）开关。遇到复杂问题打开让模型多想一会儿，简单问题关掉省 token
- **Ctrl+B** ：把正在运行的 bash 命令或 Agent 放到后台。测试在跑、依赖在装的时候，不用干等，按 Ctrl+B 丢后台，继续和 Claude 聊别的事情
- **Ctrl+R** ：交互式反向搜索命令历史。输入关键词就能找到之前用过的命令，再按 Ctrl+S 可以在当前会话、当前项目、所有项目三个范围之间切换
![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/rZm1sEcvdu0tcDYJiaK1QrrbacHJ302EqR0mPuZrDxztVdibSbOhqA27Rat8n5YRMGHrQFu50AzwKTE99s8Mx06HHnIZzwvKIciayXauRJSDGw/640?wx_fmt=png&from=appmsg#imgIndex=26)

### 编辑和导航

- **Ctrl+U** ：清除整个输入缓冲区。打了一大段话想重写的时候，比一个个删字符快得多
- **Ctrl+Y** ：恢复刚才用 Ctrl+U 清除的内容。手滑误清除的时候救命
- **Ctrl+G** ：在外部编辑器中打开当前计划，方便做大段修改
- **Ctrl+L** ：强制全屏重绘并清除输入。终端显示乱了按一下就恢复

## 08、三个隐藏关键词

这三个不是斜杠命令，是在正常对话中嵌入的特殊关键词，Claude Code 识别到之后会激活对应的增强模式。

### ultrathink

在提示中包含 ultrathink，Claude 会进入深度推理模式，无视当前的 effort 设置。推理链更长，思考过程更充分，输出质量明显提升。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/rZm1sEcvdu19YvBgESiavvvlchqHRQzCvaIPMjcMS1fmPGdIgr8LicdFp5Gkq3kibOmVP7cPhoX5HUicMR1SiaR5yTIstU1CrLPx4UiaO9F1icGR3k/640?wx_fmt=png&from=appmsg#imgIndex=27)

适合遇到特别棘手的问题时使用——debug 了好几轮找不到根因、架构设计拿不准方向、并发问题的竞态条件分析。日常简单编码没必要开，token 消耗会增加。

### ultracode

包含 ultracode 会触发动态工作流（Workflow）运行。Claude Code 会启动多个子 Agent 并行工作，每个子 Agent 负责一部分任务，最后汇总结果。

比如“审查这个项目的所有 API 端点是否存在安全漏洞”这种需要大规模扫描的任务，ultracode 会比单 Agent 快很多，因为多个 Agent 同时在跑。

### ultraplan

在提示中包含 ultraplan，规划任务会交给云端的 Claude Code on the web 会话处理。本地终端保持空闲，可以继续做其他事情。规划完成后结果会同步回来。

这三个关键词的共同特点是：在正常提示里嵌入即可，不需要额外的语法或格式。

## ending

50 多个斜杠命令、20 多个快捷键、3 个隐藏关键词。

全部记住没必要，也不现实。

日常高频用的就五个： `/compact` 管上下文、 `/resume` 管会话、 `/code-review` 管代码质量、Shift+Tab 管权限、ultrathink 管推理深度。先把这五个用熟，剩下的需要时翻这篇文章查。

先跑一遍 `/powerup` ，再收藏我推荐的那两个网站。

![图片](https://mmbiz.qpic.cn/mmbiz_png/rZm1sEcvdu3zicHspGMkp8GS2V5TwLfwNEexMpx2t2b6nEzFwsBiaZykfgYnNJrfO4LrJMI9QKekchnaY7chYe1Sg5MRTHWWibSG1pEq5fTCYE/640?wx_fmt=png&from=appmsg#imgIndex=28)

【 **工具用得好不好，不看你装了多少插件，看你知不知道手边的东西还能怎么用** 。】

我们下期见。

AI编程进阶之路 · 目录

作者提示: 个人观点，仅供参考