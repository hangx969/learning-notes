---
title: "Markdown Viewer：让 AI 写文档时，顺手把图也画了"
source: "https://mp.weixin.qq.com/s/gdIO1bWwjWUAceWcaovx9A?scene=1&click_id=1661587049"
author:
  - "[[AI工具教程]]"
published:
created: 2026-06-28
description:
tags:
  - "clippings"
---
AI工具教程 AI工具教程 *2026年5月1日 09:52*

我是在写一段接口文档时想起这个问题的。

文字已经让 AI 编程助手补得差不多了，参数表也能自动整理。卡住的反而是那张图：一个请求从网关进来，经过鉴权、队列、worker，再落到数据库。

这东西不复杂。

但你真要画，还是得切出去。

打开画图工具，拖几个框，拉线，对齐，再把图片导回来。改一次流程，图也跟着重画一遍。文档写到一半，手感基本断了。

Markdown Viewer 的这个 skills 仓库，盯上的就是这一下。它不是再做一个在线画图网站，而是把画图能力塞回 AI 编程助手的工作流里。仓库介绍里写得很直接：让 AI coding agent 在 Markdown 里创建图表和可视化内容。

我点进去看了一圈，它把这些能力拆成了一组“技能”。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/VEYrTI9ybKpfN6AQfvBKxePQJRibomZNibTsSIjdFBn7vwubEQU5ScoCW3FLbRVLL9ZDfb7ZPGlxuDmgfPgmQy7cw1eGBAYmuuAzw5C7m14ck/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

比如 UML、云架构、网络拓扑、数据分析、信息卡片这些。UML 那部分走 PlantUML，云架构里带 AWS、Azure、GCP、Kubernetes 这类图标；数据分析技能会偏向 ETL、数据湖、实时流、数仓和 BI 场景。

这就比“让 AI 生成一段 Mermaid”更窄一点。

窄反而有用。

你不是对 AI 说“帮我画个架构图”，然后等它自由发挥。你是在某个文档上下文里，让它按云架构图、部署图、类图、状态图这些固定范式去出图。图还是代码块，留在 Markdown 里。文档改了，图也可以继续让 AI 改。

这个动作很小，但对技术文档挺要命。

很多团队的文档烂，不是因为没人会写字。是文字、图、表、流程，总在不同工具之间散着。最后 README 里有一张过期截图，Notion 里有一版流程图，draw.io 文件不知道谁本地还有。

Markdown Viewer 这套东西，至少把“生成”和“修改”放回同一个地方。

它支持的渲染也不是只押一个引擎。项目页里列了 PlantUML、Vega / Vega-Lite、drawio、Canvas、Graphviz、LaTeX 等内容，Markdown Viewer 本身也强调可以把这些图表转成高分辨率图片，继续导出到 Word。

我还挺在意那个 infocard 技能。

它不是流程图，而是直接在 Markdown 里生成带排版的 HTML 信息卡片。项目说明里要求直接嵌入 HTML，不要包在代码块里，还会按内容密度和版式去组织卡片。

![图片](https://mmbiz.qpic.cn/mmbiz_png/VEYrTI9ybKpz1QRcVmAniaoCvWVfmia4pD4bDhqeHQQ2Fx5fUrm6wZfTmvH4gVFl6XWDNFfjEGp6YWicFLiaViajKKprLsDA8dU3CciaTuIiaOcMVM/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

这类东西以前很容易变成“设计同学帮忙做一下”。

现在它更像一段可以提交、可以改、可以复用的文档片段。

当然，它不是替代专业画图工具。

复杂系统图真要精修，还是会回到专门工具里。AI 生成的图也需要人看，尤其是架构边界、调用方向、状态流转这些地方，错一根线就会误导别人。

但 Markdown Viewer skills 的位置不在最终视觉稿。

它更像是把技术文档里最烦的那一步提前消掉：先让图出现，和文字待在一起，再慢慢改。

对 Claude Code、Codex、Cursor 这类工具用户来说，这个思路会很顺。装一个 skill，继续在原来的编辑器里写文档，让 AI 在 Markdown 里补图，而不是写到一半跑去开另一个软件。

GitHub地址：markdown-viewer/skills

AI工具 · 目录